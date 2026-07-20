"""Strict evidence models for the narrow Hugging Face qualification path."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath

HFScenario = Literal["complete", "model-only"]
HFWorkerMode = Literal["control", "train-crash", "preempt", "recover"]


class StrictHFModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class HFAdapterCapabilities(StrictHFModel):
    schema_version: Literal["hf-adapter-capabilities-v1"] = "hf-adapter-capabilities-v1"
    adapter_name: Literal["huggingface-trainer"] = "huggingface-trainer"
    framework: Literal["transformers"] = "transformers"
    cpu_only: Literal[True] = True
    supported_profiles: tuple[Literal["exact-training-resume", "preemption-safe-training"], ...] = (
        "exact-training-resume",
        "preemption-safe-training",
    )
    supported_faults: tuple[Literal["process-kill", "SIGTERM"], ...] = (
        "process-kill",
        "SIGTERM",
    )
    supported_preemption_signals: tuple[Literal["SIGTERM"], ...] = ("SIGTERM",)
    supported_scenarios: tuple[HFScenario, ...] = ("complete", "model-only")
    callback_can_declare_verdict: Literal[False] = False
    arbitrary_script_compatibility: Literal[False] = False


class HFCheckpointLifecycleEvidence(StrictHFModel):
    schema_version: Literal["flashpilot-hf-checkpoint-event-v1"] = (
        "flashpilot-hf-checkpoint-event-v1"
    )
    event: Literal["checkpoint_committed"] = "checkpoint_committed"
    worker_pid: int = Field(gt=0)
    global_step: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    scenario: HFScenario
    model_present: bool
    trainer_state_present: bool
    optimizer_present: bool
    scheduler_present: bool
    rng_state_present: bool
    emitted_at: datetime

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        if self.emitted_at.tzinfo is None:
            raise ValueError("checkpoint lifecycle timestamp must be timezone-aware")
        if self.scenario == "complete" and not all(
            (
                self.model_present,
                self.trainer_state_present,
                self.optimizer_present,
                self.scheduler_present,
                self.rng_state_present,
            )
        ):
            raise ValueError("complete HF checkpoint event is missing training state")
        if self.scenario == "model-only" and (
            not self.model_present
            or not self.trainer_state_present
            or self.optimizer_present
            or self.scheduler_present
            or self.rng_state_present
        ):
            raise ValueError("model-only HF checkpoint event does not match its file contract")
        return self


class HFRngMetadata(StrictHFModel):
    schema_version: Literal["flashpilot-hf-rng-metadata-v1"] = "flashpilot-hf-rng-metadata-v1"
    producer: Literal["flashpilot-trainer-callback"] = "flashpilot-trainer-callback"
    payload_path: Literal["rng_state.pth"] = "rng_state.pth"
    payload_sha256: str = Field(pattern=SHA256_PATTERN)
    python_rng_present: Literal[True] = True
    numpy_rng_present: Literal[True] = True
    torch_rng_present: Literal[True] = True


class HFRunSummary(StrictHFModel):
    schema_version: Literal["flashpilot-hf-run-summary-v1"] = "flashpilot-hf-run-summary-v1"
    mode: Literal["control", "recover"]
    scenario: HFScenario
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
    transformers_version: str = Field(min_length=1)
    torch_version: str = Field(min_length=1)
    offline_environment: Literal[True] = True

    @model_validator(mode="after")
    def validate_progress(self) -> Self:
        if len(self.loss_history) != self.semantic_global_step:
            raise ValueError("HF loss history must contain one loss per semantic step")
        if self.mode == "control" and (
            self.checkpoint_step != 0 or self.model_loaded_from_checkpoint
        ):
            raise ValueError("control summary cannot claim checkpoint loading")
        if self.mode == "recover" and (
            self.checkpoint_step <= 0 or not self.model_loaded_from_checkpoint
        ):
            raise ValueError("recovery summary must identify its loaded checkpoint")
        return self


class HFProcessEvidence(StrictHFModel):
    worker_pid: int = Field(gt=0)
    started_at: datetime
    completed_at: datetime
    exit_code: int
    exit_verified: bool

    @model_validator(mode="after")
    def validate_times(self) -> Self:
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("HF process timestamps must be timezone-aware")
        if self.completed_at < self.started_at:
            raise ValueError("HF process completion cannot precede start")
        return self


class HFQualificationCheck(StrictHFModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    category: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    status: Literal["pass", "fail"]
    expected: str = Field(min_length=1)
    actual: str = Field(min_length=1)


class HFRecoveryGateV1(StrictHFModel):
    schema_version: Literal["flashpilot-hf-recovery-gate-v1"] = "flashpilot-hf-recovery-gate-v1"
    passed: bool
    checks: tuple[HFQualificationCheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    achieved_rpo_steps: int = Field(ge=0)
    max_rpo_steps: Literal[0] = 0

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        check_ids = [check.check_id for check in self.checks]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("HF Recovery Gate check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids:
            raise ValueError("HF failed-check IDs must match gate checks in order")
        if self.passed != (not failed):
            raise ValueError("HF Recovery Gate verdict must derive from all checks")
        if self.achieved_rpo_steps > self.max_rpo_steps:
            raise ValueError("HF achieved RPO exceeds the exact profile")
        return self


class HFQualificationResult(StrictHFModel):
    schema_version: Literal["flashpilot-hf-qualification-v1"] = "flashpilot-hf-qualification-v1"
    run_id: str = Field(min_length=1)
    created_at: datetime
    qualification_profile: Literal["exact-training-resume"] = "exact-training-resume"
    framework: Literal["transformers"] = "transformers"
    adapter: Literal["huggingface-trainer"] = "huggingface-trainer"
    fault_scenario: Literal["process-kill"] = "process-kill"
    scenario: HFScenario
    script_path: ManagedRelativePath
    forwarded_arguments: tuple[str, ...]
    control_process: HFProcessEvidence
    control: HFRunSummary
    crash_process: HFProcessEvidence
    checkpoint_event: HFCheckpointLifecycleEvidence
    checkpoint_inventory: tuple[ManagedRelativePath, ...] = Field(min_length=1)
    recovery_process: HFProcessEvidence
    recovery: HFRunSummary
    gate: HFRecoveryGateV1
    model_checkpoint_load_succeeded: bool
    model_only_diverged: bool
    final_verdict: Literal["VERIFIED", "FAILED"]
    verified_persisted_bytes: int | None = Field(default=None, gt=0)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_qualification(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("HF qualification timestamp must be timezone-aware")
        pids = {
            self.control_process.worker_pid,
            self.crash_process.worker_pid,
            self.recovery_process.worker_pid,
        }
        if len(pids) != 3:
            raise ValueError("control, crash, and recovery must use distinct processes")
        if self.control.worker_pid != self.control_process.worker_pid:
            raise ValueError("control result PID differs from process evidence")
        if self.checkpoint_event.worker_pid != self.crash_process.worker_pid:
            raise ValueError("checkpoint event PID differs from crash process")
        if self.recovery.worker_pid != self.recovery_process.worker_pid:
            raise ValueError("recovery result PID differs from process evidence")
        if self.crash_process.exit_code == 0 or not self.crash_process.exit_verified:
            raise ValueError("crash worker termination must be nonzero and verified")
        if self.recovery_process.exit_code != 0 or not self.recovery_process.exit_verified:
            raise ValueError("recovery worker must exit successfully")
        if not self.model_checkpoint_load_succeeded:
            raise ValueError("both HF scenarios require a loadable model checkpoint")
        if self.scenario == "complete":
            if not self.gate.passed or self.final_verdict != "VERIFIED":
                raise ValueError("complete HF scenario must pass the deterministic gate")
            if self.model_only_diverged or self.verified_persisted_bytes is None:
                raise ValueError("complete HF result has invalid divergence/storage evidence")
        else:
            if self.gate.passed or self.final_verdict != "FAILED":
                raise ValueError("model-only HF scenario must fail exact qualification")
            if not self.model_only_diverged or self.verified_persisted_bytes is not None:
                raise ValueError("model-only HF failure must preserve divergence without savings")
        return self
