"""Strict evidence models for the bounded DeepSpeed ZeRO-2 qualification."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.distributed.models import (
    DistributedPhaseProcessEvidence,
    DistributedQualificationCheck,
    LinearSchedulerState,
    NumPyRngState,
    PythonRngState,
    TorchRngState,
)
from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath

DeepSpeedPhase = Literal["control", "checkpoint", "recovery"]
DeepSpeedPayloadRole = Literal[
    "deepspeed-latest",
    "deepspeed-model-state",
    "deepspeed-optimizer-shard",
    "deepspeed-conversion-helper",
    "rank-state",
]

DEEPSPEED_SERIALIZED_STATE = (
    "model",
    "optimizer",
    "scheduler",
    "global_step",
    "loss_history",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "topology",
    "deepspeed_client_state",
)


class StrictDeepSpeedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DeepSpeedRankCheckpointState(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-rank-state-v1"] = (
        "flashpilot-deepspeed-rank-state-v1"
    )
    rank: int = Field(ge=0)
    world_size: Literal[2] = 2
    global_step: int = Field(gt=0)
    loss_history: tuple[float, ...] = Field(min_length=1)
    scheduler: LinearSchedulerState
    python_rng: PythonRngState
    numpy_rng: NumPyRngState
    torch_rng: TorchRngState

    @model_validator(mode="after")
    def validate_progress(self) -> Self:
        if self.rank >= self.world_size:
            raise ValueError("rank must be smaller than world size")
        if len(self.loss_history) != self.global_step:
            raise ValueError("rank loss history must contain one value per completed step")
        return self


class DeepSpeedCheckpointPayload(StrictDeepSpeedModel):
    role: DeepSpeedPayloadRole
    path: ManagedRelativePath
    sha256: str = Field(pattern=SHA256_PATTERN)
    size_bytes: int = Field(gt=0)
    rank: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_role(self) -> Self:
        if self.role == "rank-state":
            if self.rank is None or self.rank >= 2:
                raise ValueError("rank-state payloads require rank 0 or 1")
            if self.path != f"rank-state-{self.rank:03d}.json":
                raise ValueError("rank-state payload path must derive from rank")
        elif self.role == "deepspeed-optimizer-shard":
            if self.rank is None or self.rank >= 2:
                raise ValueError("ZeRO optimizer shards require rank 0 or 1")
        elif self.rank is not None:
            raise ValueError("only rank state and optimizer shards carry rank ownership")
        return self


class DeepSpeedCheckpointManifest(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-checkpoint-manifest-v1"] = (
        "flashpilot-deepspeed-checkpoint-manifest-v1"
    )
    checkpoint_id: str = Field(pattern=r"^checkpoint-step-[0-9]{6}$")
    framework: Literal["deepspeed"] = "deepspeed"
    adapter: Literal["deepspeed-engine"] = "deepspeed-engine"
    strategy: Literal["zero"] = "zero"
    implementation: Literal["zero-stage-2"] = "zero-stage-2"
    zero_stage: Literal[2] = 2
    checkpoint_api: Literal["DeepSpeedEngine.save_checkpoint"] = "DeepSpeedEngine.save_checkpoint"
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    global_step: int = Field(gt=0)
    checkpoint_tag: str = Field(pattern=r"^global_step[0-9]{6}$")
    created_at: datetime
    serialized_state: tuple[str, ...] = DEEPSPEED_SERIALIZED_STATE
    payloads: tuple[DeepSpeedCheckpointPayload, ...] = Field(min_length=7)

    @field_validator("payloads")
    @classmethod
    def canonicalize_payloads(
        cls, payloads: tuple[DeepSpeedCheckpointPayload, ...]
    ) -> tuple[DeepSpeedCheckpointPayload, ...]:
        return tuple(sorted(payloads, key=lambda payload: payload.path))

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("DeepSpeed checkpoint timestamp must be timezone-aware")
        if self.checkpoint_tag != f"global_step{self.global_step:06d}":
            raise ValueError("DeepSpeed checkpoint tag must derive from global step")
        if tuple(self.serialized_state) != DEEPSPEED_SERIALIZED_STATE:
            raise ValueError("DeepSpeed checkpoint serialized state is incomplete")
        paths = [payload.path for payload in self.payloads]
        if len(paths) != len(set(paths)):
            raise ValueError("DeepSpeed checkpoint payload paths must be unique")
        expected_roles = {
            "deepspeed-latest": 1,
            "deepspeed-model-state": 1,
            "deepspeed-optimizer-shard": 2,
            "deepspeed-conversion-helper": 1,
            "rank-state": 2,
        }
        for role, expected in expected_roles.items():
            actual = sum(payload.role == role for payload in self.payloads)
            if actual != expected:
                raise ValueError(f"DeepSpeed checkpoint requires {expected} {role} payload(s)")
        expected_paths = {
            "latest",
            "zero_to_fp32.py",
            "rank-state-000.json",
            "rank-state-001.json",
            f"{self.checkpoint_tag}/mp_rank_00_model_states.pt",
            f"{self.checkpoint_tag}/zero_pp_rank_0_mp_rank_00_optim_states.pt",
            f"{self.checkpoint_tag}/zero_pp_rank_1_mp_rank_00_optim_states.pt",
        }
        if set(paths) != expected_paths:
            raise ValueError("DeepSpeed checkpoint payload inventory is not the supported layout")
        optimizer_ranks = tuple(
            payload.rank for payload in self.payloads if payload.role == "deepspeed-optimizer-shard"
        )
        if optimizer_ranks != (0, 1):
            raise ValueError("DeepSpeed checkpoint requires exact optimizer ranks 0 and 1")
        return self


class DeepSpeedCheckpointEvent(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-checkpoint-event-v1"] = (
        "flashpilot-deepspeed-checkpoint-event-v1"
    )
    event: Literal["checkpoint_committed"] = "checkpoint_committed"
    writer_rank: Literal[0] = 0
    writer_pid: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    checkpoint_tag: str = Field(pattern=r"^global_step[0-9]{6}$")
    global_step: int = Field(gt=0)
    world_size: Literal[2] = 2
    zero_stage: Literal[2] = 2
    commit_duration_seconds: float = Field(ge=0.0)
    logical_bytes: int = Field(gt=0)
    payload_files_synced: Literal[True] = True
    metadata_files_synced: Literal[True] = True
    atomic_rename_succeeded: Literal[True] = True
    directory_fsync_supported: bool
    directory_fsync_succeeded: bool
    emitted_at: datetime

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        if self.emitted_at.tzinfo is None:
            raise ValueError("DeepSpeed checkpoint event timestamp must be timezone-aware")
        if self.checkpoint_tag != f"global_step{self.global_step:06d}":
            raise ValueError("DeepSpeed checkpoint event tag must derive from global step")
        if self.directory_fsync_supported and not self.directory_fsync_succeeded:
            raise ValueError("supported directory fsync must succeed")
        if not self.directory_fsync_supported and self.directory_fsync_succeeded:
            raise ValueError("unsupported directory fsync cannot be reported successful")
        return self


class DeepSpeedRankSummary(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-rank-summary-v1"] = (
        "flashpilot-deepspeed-rank-summary-v1"
    )
    phase: DeepSpeedPhase
    rank: int = Field(ge=0)
    world_size: Literal[2] = 2
    worker_pid: int = Field(gt=0)
    backend: Literal["gloo"] = "gloo"
    strategy: Literal["zero"] = "zero"
    implementation: Literal["zero-stage-2"] = "zero-stage-2"
    zero_stage: Literal[2] = 2
    device: Literal["cpu"] = "cpu"
    final_global_step: int = Field(gt=0)
    checkpoint_step: int = Field(ge=0)
    checkpoint_tag: str | None = Field(default=None, pattern=r"^global_step[0-9]{6}$")
    checkpoint_saved: bool
    checkpoint_loaded: bool
    loaded_checkpoint_path: ManagedRelativePath | None = None
    client_state_valid: bool
    loss_history: tuple[float, ...] = Field(min_length=1)
    trainable_state_sha256: str = Field(pattern=SHA256_PATTERN)
    evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    optimizer_sha256: str = Field(pattern=SHA256_PATTERN)
    scheduler_sha256: str = Field(pattern=SHA256_PATTERN)
    collective_probe_sha256: str = Field(pattern=SHA256_PATTERN)
    torch_version: str = Field(min_length=1)
    deepspeed_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_summary(self) -> Self:
        if self.rank >= self.world_size:
            raise ValueError("rank must be smaller than world size")
        if len(self.loss_history) != self.final_global_step:
            raise ValueError("rank summary loss history must match completed progress")
        if self.phase == "control":
            if any(
                (
                    self.checkpoint_step != 0,
                    self.checkpoint_tag is not None,
                    self.checkpoint_saved,
                    self.checkpoint_loaded,
                    self.loaded_checkpoint_path is not None,
                    self.client_state_valid,
                )
            ):
                raise ValueError("control rank cannot claim checkpoint activity")
        elif self.phase == "checkpoint":
            if (
                self.checkpoint_step != self.final_global_step
                or self.checkpoint_tag is None
                or not self.checkpoint_saved
                or self.checkpoint_loaded
                or self.loaded_checkpoint_path is not None
                or not self.client_state_valid
            ):
                raise ValueError("checkpoint rank must collectively save exact state")
        elif (
            self.checkpoint_step <= 0
            or self.checkpoint_step >= self.final_global_step
            or self.checkpoint_tag is None
            or self.checkpoint_saved
            or not self.checkpoint_loaded
            or self.loaded_checkpoint_path is None
            or not self.client_state_valid
        ):
            raise ValueError("recovery rank must load and advance the prior checkpoint")
        return self


class DeepSpeedRecoveryGateV1(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-recovery-gate-v1"] = (
        "flashpilot-deepspeed-recovery-gate-v1"
    )
    passed: bool
    checks: tuple[DistributedQualificationCheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    achieved_rpo_steps: Literal[0] = 0
    max_rpo_steps: Literal[0] = 0

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        identifiers = tuple(check.check_id for check in self.checks)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("DeepSpeed Recovery Gate check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("DeepSpeed Recovery Gate verdict must derive from every check")
        return self


class DeepSpeedQualificationResult(StrictDeepSpeedModel):
    schema_version: Literal["flashpilot-deepspeed-qualification-v1"] = (
        "flashpilot-deepspeed-qualification-v1"
    )
    run_id: str = Field(min_length=1)
    created_at: datetime
    qualification_profile: Literal["exact-training-resume"] = "exact-training-resume"
    framework: Literal["deepspeed"] = "deepspeed"
    adapter: Literal["deepspeed-engine"] = "deepspeed-engine"
    strategy: Literal["zero"] = "zero"
    implementation: Literal["zero-stage-2"] = "zero-stage-2"
    zero_stage: Literal[2] = 2
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    workload_profile: Literal["ci", "demo"]
    control_processes: DistributedPhaseProcessEvidence
    control: tuple[DeepSpeedRankSummary, ...] = Field(min_length=2, max_length=2)
    checkpoint_processes: DistributedPhaseProcessEvidence
    checkpoint: tuple[DeepSpeedRankSummary, ...] = Field(min_length=2, max_length=2)
    checkpoint_event: DeepSpeedCheckpointEvent
    checkpoint_manifest: DeepSpeedCheckpointManifest
    checkpoint_inventory: tuple[ManagedRelativePath, ...] = Field(min_length=1)
    recovery_processes: DistributedPhaseProcessEvidence
    recovery: tuple[DeepSpeedRankSummary, ...] = Field(min_length=2, max_length=2)
    recovery_rto_seconds: float = Field(gt=0.0)
    gate: DeepSpeedRecoveryGateV1
    final_verdict: Literal["VERIFIED", "FAILED"]
    verified_persisted_bytes: int | None = Field(default=None, gt=0)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    limitations: tuple[str, ...] = Field(min_length=1)

    @field_validator("control", "checkpoint", "recovery")
    @classmethod
    def canonicalize_summaries(
        cls, summaries: tuple[DeepSpeedRankSummary, ...]
    ) -> tuple[DeepSpeedRankSummary, ...]:
        return tuple(sorted(summaries, key=lambda item: item.rank))

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("DeepSpeed qualification timestamp must be timezone-aware")
        phase_pairs = (
            (self.control_processes, self.control, "control"),
            (self.checkpoint_processes, self.checkpoint, "checkpoint"),
            (self.recovery_processes, self.recovery, "recovery"),
        )
        all_pids: list[int] = []
        for processes, summaries, phase in phase_pairs:
            if processes.phase != phase:
                raise ValueError("DeepSpeed process phase identity mismatch")
            if tuple(summary.phase for summary in summaries) != (phase, phase):
                raise ValueError("DeepSpeed summary phase identity mismatch")
            if tuple(summary.rank for summary in summaries) != (0, 1):
                raise ValueError("DeepSpeed summaries require exact ranks 0 and 1")
            process_pids = tuple(item.worker_pid for item in processes.ranks)
            if process_pids != tuple(item.worker_pid for item in summaries):
                raise ValueError("DeepSpeed summary PIDs differ from process evidence")
            all_pids.extend(process_pids)
        if len(all_pids) != len(set(all_pids)):
            raise ValueError("DeepSpeed phases require distinct rank processes")
        if self.checkpoint_event.writer_pid != self.checkpoint_processes.ranks[0].worker_pid:
            raise ValueError("DeepSpeed checkpoint writer must identify checkpoint rank 0")
        if self.checkpoint_event.global_step != self.checkpoint_manifest.global_step:
            raise ValueError("DeepSpeed checkpoint event and manifest step must agree")
        if self.checkpoint_event.checkpoint_tag != self.checkpoint_manifest.checkpoint_tag:
            raise ValueError("DeepSpeed checkpoint event and manifest tag must agree")
        if self.gate.passed:
            if (
                self.final_verdict != "VERIFIED"
                or self.verified_persisted_bytes is None
                or self.checkpoint_event.logical_bytes != self.verified_persisted_bytes
            ):
                raise ValueError("passing DeepSpeed Gate requires verified bytes")
        elif self.final_verdict != "FAILED" or self.verified_persisted_bytes is not None:
            raise ValueError("failed DeepSpeed Gate cannot report verified bytes")
        return self
