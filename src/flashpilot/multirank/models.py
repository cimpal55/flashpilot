"""Strict evidence models for targeted multi-rank process termination."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.domain.manifests import ManagedRelativePath

MultiRankFramework = Literal["pytorch-distributed", "deepspeed"]
MultiRankAdapter = Literal["pytorch-fsdp", "deepspeed-engine"]
MultiRankStrategy = Literal["fsdp", "zero"]
MultiRankImplementation = Literal["fully_shard", "zero-stage-2"]


class StrictMultiRankModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _validate_identity(
    *,
    framework: MultiRankFramework,
    adapter: MultiRankAdapter,
    strategy: MultiRankStrategy,
    implementation: MultiRankImplementation,
    zero_stage: Literal[2] | None,
) -> None:
    if framework == "pytorch-distributed":
        if (
            adapter != "pytorch-fsdp"
            or strategy != "fsdp"
            or implementation != "fully_shard"
            or zero_stage is not None
        ):
            raise ValueError("multi-rank FSDP identity fields disagree")
    elif (
        adapter != "deepspeed-engine"
        or strategy != "zero"
        or implementation != "zero-stage-2"
        or zero_stage != 2
    ):
        raise ValueError("multi-rank DeepSpeed identity fields disagree")


class MultiRankFaultReadyEvidence(StrictMultiRankModel):
    schema_version: Literal["flashpilot-multi-rank-fault-ready-v1"] = (
        "flashpilot-multi-rank-fault-ready-v1"
    )
    event: Literal["rank_ready_for_termination"] = "rank_ready_for_termination"
    framework: MultiRankFramework
    adapter: MultiRankAdapter
    strategy: MultiRankStrategy
    implementation: MultiRankImplementation
    zero_stage: Literal[2] | None = None
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    rank: Literal[0, 1]
    worker_pid: int = Field(gt=0)
    checkpoint_path: ManagedRelativePath
    checkpoint_id: str = Field(pattern=r"^checkpoint-step-[0-9]{6}$")
    checkpoint_tag: str | None = Field(default=None, pattern=r"^global_step[0-9]{6}$")
    checkpoint_step: int = Field(gt=0)
    checkpoint_loaded: Literal[True] = True
    ready_at: datetime

    @model_validator(mode="after")
    def validate_ready(self) -> Self:
        _validate_identity(
            framework=self.framework,
            adapter=self.adapter,
            strategy=self.strategy,
            implementation=self.implementation,
            zero_stage=self.zero_stage,
        )
        if self.ready_at.tzinfo is None:
            raise ValueError("multi-rank ready timestamp must be timezone-aware")
        if self.checkpoint_id != f"checkpoint-step-{self.checkpoint_step:06d}":
            raise ValueError("multi-rank ready checkpoint ID must derive from the step")
        if self.framework == "deepspeed":
            if self.checkpoint_tag != f"global_step{self.checkpoint_step:06d}":
                raise ValueError("DeepSpeed ready checkpoint tag must derive from the step")
        elif self.checkpoint_tag is not None:
            raise ValueError("FSDP ready evidence cannot contain a DeepSpeed checkpoint tag")
        return self


class MultiRankPeerFailureEvidence(StrictMultiRankModel):
    schema_version: Literal["flashpilot-multi-rank-peer-failure-v1"] = (
        "flashpilot-multi-rank-peer-failure-v1"
    )
    event: Literal["peer_collective_failure_observed"] = "peer_collective_failure_observed"
    framework: MultiRankFramework
    target_rank: Literal[0, 1]
    observer_rank: Literal[0, 1]
    observer_pid: int = Field(gt=0)
    checkpoint_step: int = Field(gt=0)
    failure_kind: Literal["gloo_collective_error"] = "gloo_collective_error"
    observed_at: datetime

    @model_validator(mode="after")
    def validate_observation(self) -> Self:
        if self.target_rank == self.observer_rank:
            raise ValueError("terminated and observing ranks must differ")
        if self.observed_at.tzinfo is None:
            raise ValueError("peer-failure timestamp must be timezone-aware")
        return self


class MultiRankFaultProcessEvidence(StrictMultiRankModel):
    rank: Literal[0, 1]
    worker_pid: int = Field(gt=0)
    started_at: datetime
    ready_at: datetime
    completed_at: datetime
    exit_code: int
    externally_terminated: bool
    collective_failure_observed: bool
    cleanup_forced: bool

    @model_validator(mode="after")
    def validate_process(self) -> Self:
        if any(
            timestamp.tzinfo is None
            for timestamp in (self.started_at, self.ready_at, self.completed_at)
        ):
            raise ValueError("fault-process timestamps must be timezone-aware")
        if not self.started_at <= self.ready_at <= self.completed_at:
            raise ValueError("fault-process timestamps are out of order")
        if self.exit_code == 0:
            raise ValueError("a failed rank group cannot contain a clean rank exit")
        return self


class MultiRankFailureEvent(StrictMultiRankModel):
    schema_version: Literal["flashpilot-multi-rank-failure-event-v1"] = (
        "flashpilot-multi-rank-failure-event-v1"
    )
    event: Literal["multi_rank_process_terminated"] = "multi_rank_process_terminated"
    fault_scenario: Literal["rank_process_termination"] = "rank_process_termination"
    fault_method: Literal["subprocess_kill"] = "subprocess_kill"
    framework: MultiRankFramework
    adapter: MultiRankAdapter
    strategy: MultiRankStrategy
    implementation: MultiRankImplementation
    zero_stage: Literal[2] | None = None
    backend: Literal["gloo"] = "gloo"
    world_size: Literal[2] = 2
    target_rank: Literal[0, 1]
    checkpoint_path: ManagedRelativePath
    checkpoint_id: str = Field(pattern=r"^checkpoint-step-[0-9]{6}$")
    checkpoint_tag: str | None = Field(default=None, pattern=r"^global_step[0-9]{6}$")
    checkpoint_step: int = Field(gt=0)
    failure_rpo_steps: Literal[0] = 0
    ready_evidence: tuple[MultiRankFaultReadyEvidence, ...] = Field(min_length=2, max_length=2)
    peer_failure: MultiRankPeerFailureEvidence
    rank_processes: tuple[MultiRankFaultProcessEvidence, ...] = Field(min_length=2, max_length=2)
    delivered_at: datetime
    emitted_at: datetime
    peer_failure_propagated: Literal[True] = True
    group_cleanup_complete: Literal[True] = True

    @field_validator("ready_evidence")
    @classmethod
    def canonicalize_ready(
        cls, values: tuple[MultiRankFaultReadyEvidence, ...]
    ) -> tuple[MultiRankFaultReadyEvidence, ...]:
        return tuple(sorted(values, key=lambda item: item.rank))

    @field_validator("rank_processes")
    @classmethod
    def canonicalize_processes(
        cls, values: tuple[MultiRankFaultProcessEvidence, ...]
    ) -> tuple[MultiRankFaultProcessEvidence, ...]:
        return tuple(sorted(values, key=lambda item: item.rank))

    @model_validator(mode="after")
    def validate_event(self) -> Self:
        _validate_identity(
            framework=self.framework,
            adapter=self.adapter,
            strategy=self.strategy,
            implementation=self.implementation,
            zero_stage=self.zero_stage,
        )
        if self.delivered_at.tzinfo is None or self.emitted_at.tzinfo is None:
            raise ValueError("multi-rank failure timestamps must be timezone-aware")
        if self.checkpoint_id != f"checkpoint-step-{self.checkpoint_step:06d}":
            raise ValueError("multi-rank failure checkpoint ID must derive from the step")
        if self.framework == "deepspeed":
            if self.checkpoint_tag != f"global_step{self.checkpoint_step:06d}":
                raise ValueError("DeepSpeed failure checkpoint tag must derive from the step")
        elif self.checkpoint_tag is not None:
            raise ValueError("FSDP failure evidence cannot contain a DeepSpeed checkpoint tag")
        if tuple(item.rank for item in self.ready_evidence) != (0, 1):
            raise ValueError("multi-rank failure requires ready evidence from ranks 0 and 1")
        if tuple(item.rank for item in self.rank_processes) != (0, 1):
            raise ValueError("multi-rank failure requires process evidence for ranks 0 and 1")
        ready_pids = tuple(item.worker_pid for item in self.ready_evidence)
        process_pids = tuple(item.worker_pid for item in self.rank_processes)
        if ready_pids != process_pids or len(set(process_pids)) != 2:
            raise ValueError("multi-rank failure ready and process PIDs must agree")
        if tuple(item.ready_at for item in self.ready_evidence) != tuple(
            item.ready_at for item in self.rank_processes
        ):
            raise ValueError("multi-rank ready and process timestamps must agree")
        for ready in self.ready_evidence:
            if (
                ready.framework != self.framework
                or ready.adapter != self.adapter
                or ready.strategy != self.strategy
                or ready.implementation != self.implementation
                or ready.zero_stage != self.zero_stage
                or ready.checkpoint_path != self.checkpoint_path
                or ready.checkpoint_id != self.checkpoint_id
                or ready.checkpoint_tag != self.checkpoint_tag
                or ready.checkpoint_step != self.checkpoint_step
            ):
                raise ValueError("multi-rank ready evidence differs from the failure event")
        target = self.rank_processes[self.target_rank]
        peer = self.rank_processes[1 - self.target_rank]
        if (
            not target.externally_terminated
            or target.collective_failure_observed
            or peer.externally_terminated
            or not peer.collective_failure_observed
        ):
            raise ValueError("target termination and peer-failure roles are invalid")
        if (
            self.peer_failure.framework != self.framework
            or self.peer_failure.target_rank != self.target_rank
            or self.peer_failure.observer_rank != peer.rank
            or self.peer_failure.observer_pid != peer.worker_pid
            or self.peer_failure.checkpoint_step != self.checkpoint_step
        ):
            raise ValueError("peer-failure evidence differs from the failed rank group")
        if any(item.ready_at > self.delivered_at for item in self.rank_processes):
            raise ValueError("rank termination cannot precede readiness")
        if self.peer_failure.observed_at < self.delivered_at:
            raise ValueError("peer failure cannot precede target termination")
        if self.peer_failure.observed_at > peer.completed_at:
            raise ValueError("peer failure cannot follow peer process completion")
        if any(item.completed_at < self.delivered_at for item in self.rank_processes):
            raise ValueError("failed rank completion cannot precede termination")
        if self.emitted_at < max(item.completed_at for item in self.rank_processes):
            raise ValueError("failure event cannot predate rank-group cleanup")
        return self
