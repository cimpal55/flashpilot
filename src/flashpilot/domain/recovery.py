"""Structured process, recovery, gate, and sanitized-evidence records."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import ManagedRelativePath

CheckpointStrategy = Literal[
    "safe_full",
    "safe_adapter_aware",
    "missing_training_state",
]
GateCategory = Literal[
    "Integrity",
    "Required training state",
    "Process recovery",
    "Trajectory correctness",
    "Safety and rollback",
]
GateStatus = Literal["pass", "fail", "not_applicable"]


class StrictRecoveryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RuntimeSnapshot(StrictRecoveryModel):
    global_step: int = Field(ge=0)
    loss_history: tuple[float, ...]
    trainable_state_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evaluation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    optimizer_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    scheduler_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_progress(self) -> RuntimeSnapshot:
        if len(self.loss_history) != self.global_step:
            raise ValueError("snapshot loss history must match its global step")
        return self


class RngStateDigests(StrictRecoveryModel):
    python_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    numpy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    torch_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class CheckpointCommittedEvent(StrictRecoveryModel):
    schema_version: Literal["worker-event-v1"] = "worker-event-v1"
    event: Literal["checkpoint_committed"] = "checkpoint_committed"
    worker_pid: int = Field(gt=0)
    checkpoint_step: int = Field(gt=0)
    last_completed_step: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    committed_at: datetime
    checkpoint_snapshot: RuntimeSnapshot
    rng_state: RngStateDigests

    @model_validator(mode="after")
    def validate_event(self) -> CheckpointCommittedEvent:
        if self.committed_at.tzinfo is None:
            raise ValueError("committed_at must include a timezone")
        if self.checkpoint_snapshot.global_step != self.checkpoint_step:
            raise ValueError("checkpoint snapshot step does not match the event")
        if self.last_completed_step < self.checkpoint_step:
            raise ValueError("last completed step cannot precede the checkpoint")
        return self


class RecoveryCompletedEvent(StrictRecoveryModel):
    schema_version: Literal["worker-event-v1"] = "worker-event-v1"
    event: Literal["recovery_completed"] = "recovery_completed"
    worker_pid: int = Field(gt=0)
    output_path: ManagedRelativePath


class CrashMetadata(StrictRecoveryModel):
    worker_pid: int = Field(gt=0)
    checkpoint_step: int = Field(gt=0)
    last_completed_step: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    event_received_at: datetime
    termination_method: str = Field(min_length=1)
    termination_exit_code: int
    termination_verified: bool
    terminated_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> CrashMetadata:
        if self.event_received_at.tzinfo is None or self.terminated_at.tzinfo is None:
            raise ValueError("crash timestamps must include a timezone")
        if self.terminated_at < self.event_received_at:
            raise ValueError("termination cannot precede the committed event")
        return self


class RecoveryWorkerResult(StrictRecoveryModel):
    schema_version: Literal["recovery-worker-result-v1"] = "recovery-worker-result-v1"
    worker_pid: int = Field(gt=0)
    strategy: CheckpointStrategy
    checkpoint_path: ManagedRelativePath
    restored_global_step: int = Field(ge=0)
    first_resumed_batch_step: int = Field(ge=0)
    first_completed_step: int = Field(gt=0)
    after_restore: RuntimeSnapshot
    after_restore_rng: RngStateDigests
    final: RuntimeSnapshot
    started_at: datetime
    completed_at: datetime

    @model_validator(mode="after")
    def validate_recovery_progress(self) -> RecoveryWorkerResult:
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("recovery timestamps must include a timezone")
        if self.completed_at < self.started_at:
            raise ValueError("recovery completion cannot precede its start")
        if self.after_restore.global_step != self.restored_global_step:
            raise ValueError("after-restore snapshot step is inconsistent")
        if self.first_resumed_batch_step != self.restored_global_step:
            raise ValueError("the first resumed batch must use the restored step")
        if self.first_completed_step != self.restored_global_step + 1:
            raise ValueError("the first completed step must immediately follow restore")
        if self.final.global_step < self.first_completed_step:
            raise ValueError("final step must include resumed training")
        return self


class RecoveryProcessMetadata(StrictRecoveryModel):
    worker_pid: int = Field(gt=0)
    exit_code: int
    exit_verified: bool
    started_at: datetime
    completed_at: datetime

    @model_validator(mode="after")
    def validate_timestamps(self) -> RecoveryProcessMetadata:
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("process timestamps must include a timezone")
        if self.completed_at < self.started_at:
            raise ValueError("process completion cannot precede its start")
        return self


class ComparisonPolicy(StrictRecoveryModel):
    mode: Literal["exact"] = "exact"
    trainable_parameters: Literal["sha256_exact"] = "sha256_exact"
    evaluation_logits: Literal["sha256_exact"] = "sha256_exact"
    loss_history: Literal["sequence_exact"] = "sequence_exact"
    optimizer_state: Literal["sha256_exact"] = "sha256_exact"
    scheduler_state: Literal["sha256_exact"] = "sha256_exact"
    rng_state: Literal["sha256_exact"] = "sha256_exact"
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    evidence: str = Field(min_length=1)


class GateCheck(StrictRecoveryModel):
    check_id: str = Field(min_length=1)
    category: GateCategory
    label: str = Field(min_length=1)
    status: GateStatus
    evidence_ids: tuple[str, ...]
    expected: str | None = None
    actual: str | None = None
    details: str | None = None

    @model_validator(mode="after")
    def require_evidence(self) -> GateCheck:
        if not self.evidence_ids:
            raise ValueError("every Recovery Gate check requires evidence")
        return self


class RecoveryGateResult(StrictRecoveryModel):
    schema_version: Literal["recovery-gate-v1"] = "recovery-gate-v1"
    passed: bool
    checks: tuple[GateCheck, ...]
    failed_check_ids: tuple[str, ...]
    achieved_rollback_steps: int = Field(ge=0)
    hard_rollback_limit_steps: int = Field(ge=0)
    comparison_policy: ComparisonPolicy

    @model_validator(mode="after")
    def validate_verdict(self) -> RecoveryGateResult:
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids:
            raise ValueError("failed_check_ids must match the failed checks in order")
        if self.passed != (not failed):
            raise ValueError("gate verdict must be derived from every applicable check")
        return self


class CrashExperimentResult(StrictRecoveryModel):
    schema_version: Literal["crash-experiment-v1"] = "crash-experiment-v1"
    run_id: str = Field(min_length=1)
    created_at: datetime
    profile: Literal["ci", "demo"]
    strategy: CheckpointStrategy
    control: RuntimeSnapshot
    crash: CrashMetadata
    recovery_process: RecoveryProcessMetadata
    recovery: RecoveryWorkerResult
    gate: RecoveryGateResult
    failure_artifact_path: ManagedRelativePath | None = None
    result_path: ManagedRelativePath = "result.json"
    platform_support_note: str = Field(min_length=1)
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_created_at(self) -> CrashExperimentResult:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        if self.crash.worker_pid == self.recovery.worker_pid:
            raise ValueError("recovery must run in a different process")
        if self.recovery.worker_pid != self.recovery_process.worker_pid:
            raise ValueError("recovery process metadata does not match worker output")
        return self


class SanitizedFailureArtifact(StrictRecoveryModel):
    schema_version: Literal["sanitized-failure-v1"] = "sanitized-failure-v1"
    user_objective: dict[str, Any]
    workload_capabilities: dict[str, Any]
    checkpoint_contract: dict[str, Any]
    save_restore_summary: dict[str, Any]
    manifest_summary: dict[str, Any]
    restore_order: tuple[str, ...]
    gate_checks: tuple[dict[str, Any], ...]
    state_differences: dict[str, Any]
    trajectory_summary: dict[str, Any]
    integrity_summary: dict[str, Any]
    crash_metadata: dict[str, Any]
    evidence_catalog: dict[str, str]
