"""Strict evidence models for PyTorch Lightning qualification."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath

LightningScenario = Literal["complete", "weights-only"]
LightningWorkerMode = Literal["control", "train-crash", "recover"]


class StrictLightningModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class LightningAdapterCapabilities(StrictLightningModel):
    schema_version: Literal["lightning-adapter-capabilities-v1"] = (
        "lightning-adapter-capabilities-v1"
    )
    adapter_name: Literal["pytorch-lightning"] = "pytorch-lightning"
    framework: Literal["lightning"] = "lightning"
    cpu_only: Literal[True] = True
    supported_profiles: tuple[Literal["exact-training-resume"], ...] = ("exact-training-resume",)
    supported_faults: tuple[Literal["process-kill"], ...] = ("process-kill",)
    supported_scenarios: tuple[LightningScenario, ...] = ("complete", "weights-only")
    callback_can_declare_verdict: Literal[False] = False
    arbitrary_module_compatibility: Literal[False] = False
    repair_capability: Literal[False] = False


class LightningCheckpointLifecycleEvidence(StrictLightningModel):
    schema_version: Literal["flashpilot-lightning-checkpoint-event-v1"] = (
        "flashpilot-lightning-checkpoint-event-v1"
    )
    event: Literal["checkpoint_committed"] = "checkpoint_committed"
    worker_pid: int = Field(gt=0)
    global_step: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    scenario: LightningScenario
    model_present: bool
    loop_state_present: bool
    optimizer_present: bool
    scheduler_present: bool
    rng_state_present: bool
    loss_history_present: bool
    emitted_at: datetime

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        if self.emitted_at.tzinfo is None:
            raise ValueError("checkpoint lifecycle timestamp must be timezone-aware")
        state = (
            self.model_present,
            self.loop_state_present,
            self.optimizer_present,
            self.scheduler_present,
            self.rng_state_present,
            self.loss_history_present,
        )
        if self.scenario == "complete" and not all(state):
            raise ValueError("complete Lightning checkpoint is missing exact-resume state")
        if self.scenario == "weights-only" and (
            not self.model_present
            or any(
                (
                    self.optimizer_present,
                    self.scheduler_present,
                    self.rng_state_present,
                    self.loss_history_present,
                )
            )
        ):
            raise ValueError("weights-only Lightning checkpoint violates its state contract")
        return self


class LightningRunSummary(StrictLightningModel):
    schema_version: Literal["flashpilot-lightning-run-summary-v1"] = (
        "flashpilot-lightning-run-summary-v1"
    )
    mode: Literal["control", "recover"]
    scenario: LightningScenario
    worker_pid: int = Field(gt=0)
    trainer_global_step: int = Field(ge=0)
    semantic_global_step: int = Field(gt=0)
    checkpoint_step: int = Field(ge=0)
    model_loaded_from_checkpoint: bool
    loss_history: tuple[float, ...] = Field(min_length=1)
    trainable_state_sha256: str = Field(pattern=SHA256_PATTERN)
    evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    optimizer_sha256: str = Field(pattern=SHA256_PATTERN)
    scheduler_sha256: str = Field(pattern=SHA256_PATTERN)
    lightning_version: str = Field(min_length=1)
    torch_version: str = Field(min_length=1)
    cpu_only: Literal[True] = True

    @model_validator(mode="after")
    def validate_progress(self) -> Self:
        if (self.mode == "control" or self.scenario == "complete") and (
            len(self.loss_history) != self.semantic_global_step
        ):
            raise ValueError("complete Lightning history must contain one loss per semantic step")
        if (
            self.mode == "recover"
            and self.scenario == "weights-only"
            and (len(self.loss_history) > self.semantic_global_step)
        ):
            raise ValueError("weights-only recovery history cannot exceed semantic progress")
        if self.mode == "control" and (
            self.checkpoint_step != 0 or self.model_loaded_from_checkpoint
        ):
            raise ValueError("control summary cannot claim checkpoint loading")
        if self.mode == "recover" and (
            self.checkpoint_step <= 0 or not self.model_loaded_from_checkpoint
        ):
            raise ValueError("recovery summary must identify its loaded checkpoint")
        return self


class LightningProcessEvidence(StrictLightningModel):
    worker_pid: int = Field(gt=0)
    started_at: datetime
    completed_at: datetime
    exit_code: int
    exit_verified: bool

    @model_validator(mode="after")
    def validate_times(self) -> Self:
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("Lightning process timestamps must be timezone-aware")
        if self.completed_at < self.started_at:
            raise ValueError("Lightning process completion cannot precede start")
        return self


class LightningQualificationCheck(StrictLightningModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    category: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    status: Literal["pass", "fail"]
    expected: str = Field(min_length=1)
    actual: str = Field(min_length=1)


class LightningRecoveryGateV1(StrictLightningModel):
    schema_version: Literal["flashpilot-lightning-recovery-gate-v1"] = (
        "flashpilot-lightning-recovery-gate-v1"
    )
    passed: bool
    checks: tuple[LightningQualificationCheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    achieved_rpo_steps: int = Field(ge=0)
    max_rpo_steps: Literal[0] = 0

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        identifiers = [check.check_id for check in self.checks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Lightning Recovery Gate check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("Lightning Recovery Gate verdict must derive from every check")
        if self.achieved_rpo_steps > self.max_rpo_steps:
            raise ValueError("Lightning achieved RPO exceeds the exact profile")
        return self


class LightningQualificationResult(StrictLightningModel):
    schema_version: Literal["flashpilot-lightning-qualification-v1"] = (
        "flashpilot-lightning-qualification-v1"
    )
    run_id: str = Field(min_length=1)
    created_at: datetime
    qualification_profile: Literal["exact-training-resume"] = "exact-training-resume"
    framework: Literal["lightning"] = "lightning"
    adapter: Literal["pytorch-lightning"] = "pytorch-lightning"
    fault_scenario: Literal["process-kill"] = "process-kill"
    scenario: LightningScenario
    script_path: ManagedRelativePath
    forwarded_arguments: tuple[str, ...]
    control_process: LightningProcessEvidence
    control: LightningRunSummary
    crash_process: LightningProcessEvidence
    checkpoint_event: LightningCheckpointLifecycleEvidence
    checkpoint_inventory: tuple[str, ...] = Field(min_length=1)
    recovery_process: LightningProcessEvidence
    recovery: LightningRunSummary
    gate: LightningRecoveryGateV1
    model_checkpoint_load_succeeded: bool
    weights_only_diverged: bool
    final_verdict: Literal["VERIFIED", "FAILED"]
    verified_persisted_bytes: int | None = Field(default=None, gt=0)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_qualification(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("Lightning qualification timestamp must be timezone-aware")
        pids = {
            self.control_process.worker_pid,
            self.crash_process.worker_pid,
            self.recovery_process.worker_pid,
        }
        if len(pids) != 3:
            raise ValueError("control, crash, and recovery must use distinct processes")
        if self.control.worker_pid != self.control_process.worker_pid:
            raise ValueError("control summary PID differs from process evidence")
        if self.checkpoint_event.worker_pid != self.crash_process.worker_pid:
            raise ValueError("checkpoint event PID differs from crash process")
        if self.recovery.worker_pid != self.recovery_process.worker_pid:
            raise ValueError("recovery summary PID differs from process evidence")
        if self.crash_process.exit_code == 0 or not self.crash_process.exit_verified:
            raise ValueError("crash worker termination must be nonzero and verified")
        if self.recovery_process.exit_code != 0 or not self.recovery_process.exit_verified:
            raise ValueError("recovery worker must exit successfully")
        if not self.model_checkpoint_load_succeeded:
            raise ValueError("both Lightning scenarios require a loadable model checkpoint")
        if self.scenario == "complete":
            if not self.gate.passed or self.final_verdict != "VERIFIED":
                raise ValueError("complete Lightning scenario must pass the deterministic gate")
            if self.weights_only_diverged or self.verified_persisted_bytes is None:
                raise ValueError(
                    "complete Lightning result has invalid divergence/storage evidence"
                )
        elif (
            self.gate.passed
            or self.final_verdict != "FAILED"
            or not self.weights_only_diverged
            or self.verified_persisted_bytes is not None
        ):
            raise ValueError("weights-only scenario must fail exact qualification without bytes")
        return self
