"""Typed records for the bounded Prompt 5 repair loop."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.agent import (
    AgentCallMetadata,
    FailureAnalysis,
    RepairActionType,
    RepairPlanValidationResult,
)
from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath
from flashpilot.domain.recovery import CrashExperimentResult

StrategyField = Literal[
    "include_optimizer",
    "include_scheduler",
    "include_python_rng",
    "include_numpy_rng",
    "include_torch_rng",
    "restore_before_next_batch",
]

REPAIR_ACTION_TO_FIELD: dict[RepairActionType, StrategyField] = {
    "persist_optimizer_state": "include_optimizer",
    "persist_scheduler_state": "include_scheduler",
    "persist_python_rng_state": "include_python_rng",
    "persist_numpy_rng_state": "include_numpy_rng",
    "persist_torch_rng_state": "include_torch_rng",
    "restore_state_before_next_batch": "restore_before_next_batch",
}


class StrictRepairModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CheckpointStrategyConfig(StrictRepairModel):
    """The complete and only executable P0 repair configuration surface."""

    schema_version: Literal["checkpoint-strategy-config-v1"] = "checkpoint-strategy-config-v1"
    strategy_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,63}$")
    include_optimizer: bool
    include_scheduler: bool
    include_python_rng: bool
    include_numpy_rng: bool
    include_torch_rng: bool
    restore_before_next_batch: bool

    @property
    def complete_training_state_enabled(self) -> bool:
        return all(
            (
                self.include_optimizer,
                self.include_scheduler,
                self.include_python_rng,
                self.include_numpy_rng,
                self.include_torch_rng,
                self.restore_before_next_batch,
            )
        )

    def require_complete_training_state(self) -> None:
        if not self.complete_training_state_enabled:
            raise ValueError(
                "repaired strategy does not enable every mandatory training-state field"
            )


class DirectoryFingerprint(StrictRepairModel):
    sha256: str = Field(pattern=SHA256_PATTERN)
    file_count: int = Field(gt=0)
    logical_bytes: int = Field(gt=0)


class RepairExecutionResult(StrictRepairModel):
    schema_version: Literal["repair-execution-v1"] = "repair-execution-v1"
    attempt_number: Literal[1] = 1
    admitted_at: datetime
    original_config: CheckpointStrategyConfig
    repaired_config: CheckpointStrategyConfig
    applied_actions: tuple[RepairActionType, ...]
    unsupported_actions: tuple[RepairActionType, ...]
    rejected_actions: tuple[RepairActionType, ...]
    execution_performed: Literal[True] = True

    @model_validator(mode="after")
    def validate_explicit_changes(self) -> RepairExecutionResult:
        if self.admitted_at.tzinfo is None:
            raise ValueError("repair admission time must include a timezone")
        if self.original_config.strategy_id == self.repaired_config.strategy_id:
            raise ValueError("repair must assign a new strategy ID")
        if len(self.applied_actions) != len(set(self.applied_actions)):
            raise ValueError("repair actions must be unique")
        for action in self.applied_actions:
            field = REPAIR_ACTION_TO_FIELD.get(action)
            if field is None:
                raise ValueError(f"action is not executable in P0: {action}")
            if getattr(self.original_config, field) or not getattr(self.repaired_config, field):
                raise ValueError(
                    f"action does not map to one explicit false-to-true field: {action}"
                )
        changed_fields = {
            field
            for field in REPAIR_ACTION_TO_FIELD.values()
            if getattr(self.original_config, field) != getattr(self.repaired_config, field)
        }
        mapped_fields = {REPAIR_ACTION_TO_FIELD[action] for action in self.applied_actions}
        if changed_fields != mapped_fields:
            raise ValueError("repaired strategy contains changes not authorized by typed actions")
        self.repaired_config.require_complete_training_state()
        return self


class StorageComparison(StrictRepairModel):
    schema_version: Literal["storage-comparison-v1"] = "storage-comparison-v1"
    measurement_scope: Literal["logical_checkpoint_directory_bytes"] = (
        "logical_checkpoint_directory_bytes"
    )
    profile: Literal["ci", "demo"]
    checkpoint_step: int = Field(gt=0)
    safe_full_bytes: int = Field(gt=0)
    repaired_recurring_bytes: int = Field(gt=0)
    repaired_one_time_base_bytes: int = Field(gt=0)
    structural_reduction_bytes: int = Field(gt=0)
    structural_reduction_percent: float = Field(gt=0.0, lt=100.0)
    reported_after_recovery_passed: Literal[True] = True
    safe_full_measurement_source: Literal["unchanged_safe_full_direct_restore_baseline"] = (
        "unchanged_safe_full_direct_restore_baseline"
    )
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_reduction(self) -> StorageComparison:
        expected = self.safe_full_bytes - self.repaired_recurring_bytes
        if self.structural_reduction_bytes != expected:
            raise ValueError("storage reduction must be derived from measured logical bytes")
        return self


class RepairLoopResult(StrictRepairModel):
    schema_version: Literal["repair-loop-result-v1"] = "repair-loop-result-v1"
    run_id: str = Field(min_length=1)
    created_at: datetime
    profile: Literal["ci", "demo"]
    initial_failure: CrashExperimentResult
    captured_live_failure_metadata: AgentCallMetadata
    replay_call_metadata: AgentCallMetadata
    proposed_analysis: FailureAnalysis
    plan_validation: RepairPlanValidationResult
    repair_execution: RepairExecutionResult
    repaired_run: CrashExperimentResult
    original_checkpoint_before: DirectoryFingerprint
    original_checkpoint_after: DirectoryFingerprint
    original_checkpoint_unmodified: bool
    repair_attempt_count: Literal[1] = 1
    final_verdict: Literal["VERIFIED", "FAILED"]
    fallback_status: Literal["not_required", "documented_not_invoked_after_failure"]
    storage_comparison: StorageComparison | None
    result_path: ManagedRelativePath = "result.json"
    report_path: ManagedRelativePath = "report.md"
    html_report_path: ManagedRelativePath = "report.html"
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_loop(self) -> RepairLoopResult:
        if self.created_at.tzinfo is None:
            raise ValueError("repair-loop timestamp must include a timezone")
        if self.initial_failure.gate.passed:
            raise ValueError("the initial incomplete-checkpoint gate must fail")
        if self.initial_failure.strategy != "missing_training_state":
            raise ValueError("the initial experiment must use the incomplete strategy")
        if self.repaired_run.strategy != "safe_adapter_aware":
            raise ValueError("the repaired experiment must use adapter-aware storage")
        if self.initial_failure.control != self.repaired_run.control:
            raise ValueError("both experiments must use the same uninterrupted control")
        if self.plan_validation.accepted_actions != self.repair_execution.applied_actions:
            raise ValueError("every accepted action and only accepted actions must be applied")
        if self.plan_validation.unsupported_actions != self.repair_execution.unsupported_actions:
            raise ValueError("unsupported action records must be preserved")
        if self.plan_validation.rejected_actions != self.repair_execution.rejected_actions:
            raise ValueError("rejected action records must be preserved")
        if self.original_checkpoint_unmodified != (
            self.original_checkpoint_before == self.original_checkpoint_after
        ):
            raise ValueError("original checkpoint mutation verdict does not match fingerprints")
        if not self.original_checkpoint_unmodified:
            raise ValueError("the original failed checkpoint was modified")
        passed = self.repaired_run.gate.passed
        if self.final_verdict != ("VERIFIED" if passed else "FAILED"):
            raise ValueError("only the final deterministic Recovery Gate may set the verdict")
        if passed and self.storage_comparison is None:
            raise ValueError(
                "passing recovery must include the post-verification storage comparison"
            )
        if not passed and self.storage_comparison is not None:
            raise ValueError("storage reduction cannot be reported before recovery passes")
        if passed != (self.fallback_status == "not_required"):
            raise ValueError("fallback status does not match the final gate")
        return self
