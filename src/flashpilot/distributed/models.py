"""Strict evidence models for distributed PyTorch FSDP qualification."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath

DistributedPhase = Literal["control", "checkpoint", "recovery"]
DistributedPayloadRole = Literal["dcp-metadata", "dcp-shard", "rank-state"]

DISTRIBUTED_SERIALIZED_STATE = (
    "model",
    "optimizer",
    "scheduler",
    "global_step",
    "loss_history",
    "python_rng",
    "numpy_rng",
    "torch_rng",
)


class StrictDistributedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PythonRngState(StrictDistributedModel):
    version: int = Field(ge=1)
    internal_state: tuple[int, ...] = Field(min_length=1)
    gaussian_cache: float | None = None


class NumPyRngState(StrictDistributedModel):
    algorithm: Literal["MT19937"] = "MT19937"
    keys: tuple[int, ...] = Field(min_length=1)
    position: int = Field(ge=0)
    has_gaussian: Literal[0, 1]
    cached_gaussian: float


class TorchRngState(StrictDistributedModel):
    bytes: tuple[int, ...] = Field(min_length=1)

    @field_validator("bytes")
    @classmethod
    def validate_bytes(cls, values: tuple[int, ...]) -> tuple[int, ...]:
        if any(value < 0 or value > 255 for value in values):
            raise ValueError("Torch RNG bytes must be in the range 0..255")
        return values


class LinearSchedulerState(StrictDistributedModel):
    start_factor: float = Field(gt=0.0, le=1.0)
    end_factor: float = Field(gt=0.0, le=1.0)
    total_iters: int = Field(gt=0)
    base_lrs: tuple[float, ...] = Field(min_length=1)
    last_epoch: int = Field(ge=0)
    step_count: int = Field(ge=1)
    is_initial: bool
    get_lr_called_within_step: bool
    last_lrs: tuple[float, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_groups(self) -> Self:
        if len(self.base_lrs) != len(self.last_lrs):
            raise ValueError("scheduler base and current learning-rate groups must agree")
        return self


class DistributedRankCheckpointState(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-rank-state-v1"] = (
        "flashpilot-distributed-rank-state-v1"
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


class DistributedCheckpointPayload(StrictDistributedModel):
    role: DistributedPayloadRole
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
        elif self.rank is not None:
            raise ValueError("DCP payloads do not carry inferred rank ownership")
        if self.role == "dcp-metadata" and self.path != "dcp/.metadata":
            raise ValueError("DCP metadata path is fixed")
        if self.role == "dcp-shard" and (
            not self.path.startswith("dcp/") or not self.path.endswith(".distcp")
        ):
            raise ValueError("DCP shard path must be a managed .distcp file")
        return self


class DistributedCheckpointManifest(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-checkpoint-manifest-v1"] = (
        "flashpilot-distributed-checkpoint-manifest-v1"
    )
    checkpoint_id: str = Field(pattern=r"^checkpoint-step-[0-9]{6}$")
    framework: Literal["pytorch"] = "pytorch"
    strategy: Literal["fsdp"] = "fsdp"
    implementation: Literal["fully_shard"] = "fully_shard"
    state_dict_api: Literal["torch.distributed.checkpoint"] = "torch.distributed.checkpoint"
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    global_step: int = Field(gt=0)
    created_at: datetime
    serialized_state: tuple[str, ...] = DISTRIBUTED_SERIALIZED_STATE
    payloads: tuple[DistributedCheckpointPayload, ...] = Field(min_length=4)

    @field_validator("payloads")
    @classmethod
    def canonicalize_payloads(
        cls, payloads: tuple[DistributedCheckpointPayload, ...]
    ) -> tuple[DistributedCheckpointPayload, ...]:
        return tuple(sorted(payloads, key=lambda payload: payload.path))

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("distributed checkpoint timestamp must be timezone-aware")
        if tuple(self.serialized_state) != DISTRIBUTED_SERIALIZED_STATE:
            raise ValueError("distributed checkpoint serialized state is incomplete")
        paths = [payload.path for payload in self.payloads]
        if len(paths) != len(set(paths)):
            raise ValueError("distributed checkpoint payload paths must be unique")
        rank_payloads = tuple(
            (payload.rank, payload.path)
            for payload in self.payloads
            if payload.role == "rank-state"
        )
        if rank_payloads != (
            (0, "rank-state-000.json"),
            (1, "rank-state-001.json"),
        ):
            raise ValueError("distributed checkpoint requires exact rank 0 and 1 state")
        if sum(payload.role == "dcp-metadata" for payload in self.payloads) != 1:
            raise ValueError("distributed checkpoint requires one DCP metadata payload")
        if not any(payload.role == "dcp-shard" for payload in self.payloads):
            raise ValueError("distributed checkpoint requires DCP shard data")
        return self


class DistributedCheckpointEvent(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-checkpoint-event-v1"] = (
        "flashpilot-distributed-checkpoint-event-v1"
    )
    event: Literal["checkpoint_committed"] = "checkpoint_committed"
    writer_rank: Literal[0] = 0
    writer_pid: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    global_step: int = Field(gt=0)
    world_size: Literal[2] = 2
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
            raise ValueError("distributed checkpoint event timestamp must be timezone-aware")
        if self.directory_fsync_supported and not self.directory_fsync_succeeded:
            raise ValueError("supported directory fsync must succeed")
        if not self.directory_fsync_supported and self.directory_fsync_succeeded:
            raise ValueError("unsupported directory fsync cannot be reported successful")
        return self


class DistributedRankSummary(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-rank-summary-v1"] = (
        "flashpilot-distributed-rank-summary-v1"
    )
    phase: DistributedPhase
    rank: int = Field(ge=0)
    world_size: Literal[2] = 2
    worker_pid: int = Field(gt=0)
    backend: Literal["gloo"] = "gloo"
    strategy: Literal["fsdp"] = "fsdp"
    implementation: Literal["fully_shard"] = "fully_shard"
    device: Literal["cpu"] = "cpu"
    final_global_step: int = Field(gt=0)
    checkpoint_step: int = Field(ge=0)
    checkpoint_loaded: bool
    loss_history: tuple[float, ...] = Field(min_length=1)
    trainable_state_sha256: str = Field(pattern=SHA256_PATTERN)
    evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    optimizer_sha256: str = Field(pattern=SHA256_PATTERN)
    scheduler_sha256: str = Field(pattern=SHA256_PATTERN)
    collective_probe_sha256: str = Field(pattern=SHA256_PATTERN)
    torch_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_summary(self) -> Self:
        if self.rank >= self.world_size:
            raise ValueError("rank must be smaller than world size")
        if len(self.loss_history) != self.final_global_step:
            raise ValueError("rank summary loss history must match completed progress")
        if self.phase == "control" and (self.checkpoint_step != 0 or self.checkpoint_loaded):
            raise ValueError("control rank cannot claim checkpoint restore")
        if self.phase == "checkpoint" and (
            self.checkpoint_step != self.final_global_step or self.checkpoint_loaded
        ):
            raise ValueError("checkpoint rank must stop exactly at the saved step")
        if self.phase == "recovery" and (
            self.checkpoint_step <= 0
            or self.checkpoint_step >= self.final_global_step
            or not self.checkpoint_loaded
        ):
            raise ValueError("recovery rank must load and advance a prior checkpoint")
        return self


class DistributedRankProcessEvidence(StrictDistributedModel):
    rank: int = Field(ge=0)
    worker_pid: int = Field(gt=0)
    started_at: datetime
    completed_at: datetime
    exit_code: Literal[0] = 0
    exit_verified: Literal[True] = True

    @model_validator(mode="after")
    def validate_process(self) -> Self:
        if self.rank >= 2:
            raise ValueError("process rank must be 0 or 1")
        if self.started_at.tzinfo is None or self.completed_at.tzinfo is None:
            raise ValueError("distributed process timestamps must be timezone-aware")
        if self.completed_at < self.started_at:
            raise ValueError("distributed process completion cannot precede start")
        return self


class DistributedPhaseProcessEvidence(StrictDistributedModel):
    phase: DistributedPhase
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    ranks: tuple[DistributedRankProcessEvidence, ...] = Field(min_length=2, max_length=2)

    @field_validator("ranks")
    @classmethod
    def canonicalize_ranks(
        cls, ranks: tuple[DistributedRankProcessEvidence, ...]
    ) -> tuple[DistributedRankProcessEvidence, ...]:
        return tuple(sorted(ranks, key=lambda item: item.rank))

    @model_validator(mode="after")
    def validate_group(self) -> Self:
        if tuple(item.rank for item in self.ranks) != (0, 1):
            raise ValueError("distributed phase requires exact ranks 0 and 1")
        if len({item.worker_pid for item in self.ranks}) != self.world_size:
            raise ValueError("distributed phase worker PIDs must be unique")
        return self


class DistributedQualificationCheck(StrictDistributedModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    category: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=200)
    status: Literal["pass", "fail"]
    expected: str = Field(min_length=1)
    actual: str = Field(min_length=1)


class DistributedRecoveryGateV1(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-recovery-gate-v1"] = (
        "flashpilot-distributed-recovery-gate-v1"
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
            raise ValueError("distributed Recovery Gate check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("distributed Recovery Gate verdict must derive from every check")
        return self


class DistributedQualificationResult(StrictDistributedModel):
    schema_version: Literal["flashpilot-distributed-qualification-v1"] = (
        "flashpilot-distributed-qualification-v1"
    )
    run_id: str = Field(min_length=1)
    created_at: datetime
    qualification_profile: Literal["exact-training-resume"] = "exact-training-resume"
    framework: Literal["pytorch-distributed"] = "pytorch-distributed"
    adapter: Literal["pytorch-fsdp"] = "pytorch-fsdp"
    strategy: Literal["fsdp"] = "fsdp"
    implementation: Literal["fully_shard"] = "fully_shard"
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    workload_profile: Literal["ci", "demo"]
    control_processes: DistributedPhaseProcessEvidence
    control: tuple[DistributedRankSummary, ...] = Field(min_length=2, max_length=2)
    checkpoint_processes: DistributedPhaseProcessEvidence
    checkpoint: tuple[DistributedRankSummary, ...] = Field(min_length=2, max_length=2)
    checkpoint_event: DistributedCheckpointEvent
    checkpoint_manifest: DistributedCheckpointManifest
    checkpoint_inventory: tuple[ManagedRelativePath, ...] = Field(min_length=1)
    recovery_processes: DistributedPhaseProcessEvidence
    recovery: tuple[DistributedRankSummary, ...] = Field(min_length=2, max_length=2)
    recovery_rto_seconds: float = Field(gt=0.0)
    gate: DistributedRecoveryGateV1
    final_verdict: Literal["VERIFIED", "FAILED"]
    verified_persisted_bytes: int | None = Field(default=None, gt=0)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    limitations: tuple[str, ...] = Field(min_length=1)

    @field_validator("control", "checkpoint", "recovery")
    @classmethod
    def canonicalize_summaries(
        cls, summaries: tuple[DistributedRankSummary, ...]
    ) -> tuple[DistributedRankSummary, ...]:
        return tuple(sorted(summaries, key=lambda item: item.rank))

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("distributed qualification timestamp must be timezone-aware")
        phase_pairs = (
            (self.control_processes, self.control, "control"),
            (self.checkpoint_processes, self.checkpoint, "checkpoint"),
            (self.recovery_processes, self.recovery, "recovery"),
        )
        all_pids: list[int] = []
        for processes, summaries, phase in phase_pairs:
            if processes.phase != phase:
                raise ValueError("distributed process phase identity mismatch")
            if tuple(summary.phase for summary in summaries) != (phase, phase):
                raise ValueError("distributed summary phase identity mismatch")
            if tuple(summary.rank for summary in summaries) != (0, 1):
                raise ValueError("distributed summaries require exact ranks 0 and 1")
            process_pids = tuple(item.worker_pid for item in processes.ranks)
            if process_pids != tuple(item.worker_pid for item in summaries):
                raise ValueError("distributed summary PIDs differ from process evidence")
            all_pids.extend(process_pids)
        if len(all_pids) != len(set(all_pids)):
            raise ValueError("control, checkpoint, and recovery ranks require distinct processes")
        if self.checkpoint_event.writer_pid != self.checkpoint_processes.ranks[0].worker_pid:
            raise ValueError("checkpoint writer PID must identify checkpoint rank 0")
        if self.checkpoint_event.global_step != self.checkpoint_manifest.global_step:
            raise ValueError("checkpoint event and manifest step must agree")
        if (
            self.checkpoint_event.logical_bytes != self.verified_persisted_bytes
            and self.gate.passed
        ):
            raise ValueError("verified distributed bytes must match checkpoint event")
        if self.gate.passed:
            if self.final_verdict != "VERIFIED" or self.verified_persisted_bytes is None:
                raise ValueError("passing distributed Gate requires verified result and bytes")
        elif self.final_verdict != "FAILED" or self.verified_persisted_bytes is not None:
            raise ValueError("failed distributed Gate cannot report verified bytes")
        return self
