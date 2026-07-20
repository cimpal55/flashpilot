"""Strict evidence models for managed SIGTERM preemption certification."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import ManagedRelativePath
from flashpilot.hf.models import (
    HFCheckpointLifecycleEvidence,
    HFProcessEvidence,
    HFQualificationCheck,
    HFRunSummary,
)

PREEMPTION_INCOMPLETE_MARKER = "preemption/INCOMPLETE"


class StrictPreemptionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class HFPreemptionReadyEvidence(StrictPreemptionModel):
    schema_version: Literal["flashpilot-hf-preemption-ready-v1"] = (
        "flashpilot-hf-preemption-ready-v1"
    )
    event: Literal["preemption_ready"] = "preemption_ready"
    worker_pid: int = Field(gt=0)
    completed_step: int = Field(gt=0)
    signal_name: Literal["SIGTERM"] = "SIGTERM"
    emitted_at: datetime

    @model_validator(mode="after")
    def validate_timestamp(self) -> Self:
        if self.emitted_at.tzinfo is None:
            raise ValueError("preemption-ready timestamp must be timezone-aware")
        return self


class HFPreemptionCommitEvidence(StrictPreemptionModel):
    schema_version: Literal["flashpilot-hf-preemption-commit-v1"] = (
        "flashpilot-hf-preemption-commit-v1"
    )
    event: Literal["preemption_checkpoint_committed"] = "preemption_checkpoint_committed"
    worker_pid: int = Field(gt=0)
    signal_name: Literal["SIGTERM"] = "SIGTERM"
    signal_received_at: datetime
    checkpoint_committed_at: datetime
    checkpoint: HFCheckpointLifecycleEvidence
    incomplete_marker_path: Literal["preemption/INCOMPLETE"] = PREEMPTION_INCOMPLETE_MARKER
    incomplete_marker_present: Literal[False] = False

    @model_validator(mode="after")
    def validate_commit(self) -> Self:
        if self.signal_received_at.tzinfo is None or self.checkpoint_committed_at.tzinfo is None:
            raise ValueError("preemption commit timestamps must be timezone-aware")
        if self.checkpoint_committed_at < self.signal_received_at:
            raise ValueError("preemption checkpoint cannot commit before signal receipt")
        if self.worker_pid != self.checkpoint.worker_pid:
            raise ValueError("preemption commit and checkpoint worker PIDs differ")
        if self.checkpoint.emitted_at > self.checkpoint_committed_at:
            raise ValueError("checkpoint lifecycle evidence cannot follow commit evidence")
        return self


class HFPreemptionGateV1(StrictPreemptionModel):
    schema_version: Literal["flashpilot-hf-preemption-gate-v1"] = "flashpilot-hf-preemption-gate-v1"
    passed: bool
    checks: tuple[HFQualificationCheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    achieved_rpo_steps: int = Field(ge=0)
    max_rpo_steps: Literal[0] = 0
    achieved_rpo_tokens: int = Field(ge=0)
    max_rpo_tokens: Literal[0] = 0

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        identifiers = tuple(check.check_id for check in self.checks)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("preemption Gate check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("preemption Gate verdict must derive from every check")
        return self


class HFPreemptionCertificationResult(StrictPreemptionModel):
    schema_version: Literal["flashpilot-hf-preemption-certification-v1"] = (
        "flashpilot-hf-preemption-certification-v1"
    )
    run_id: str = Field(min_length=1)
    created_at: datetime
    qualification_profile: Literal["preemption-safe-training"] = "preemption-safe-training"
    framework: Literal["transformers"] = "transformers"
    adapter: Literal["huggingface-trainer"] = "huggingface-trainer"
    fault_scenario: Literal["managed-preemption"] = "managed-preemption"
    signal_name: Literal["SIGTERM"] = "SIGTERM"
    signal_delivery: Literal["os.kill"] = "os.kill"
    grace_period_seconds: int = Field(ge=1, le=3_600)
    preemption_step: int = Field(gt=0)
    total_steps: int = Field(gt=0)
    tokens_per_step: int = Field(gt=0)
    script_path: ManagedRelativePath
    forwarded_arguments: tuple[str, ...]
    control_process: HFProcessEvidence
    control: HFRunSummary
    preemption_process: HFProcessEvidence
    ready_event: HFPreemptionReadyEvidence
    signal_sent_at: datetime
    commit_event: HFPreemptionCommitEvidence
    checkpoint_inventory: tuple[ManagedRelativePath, ...] = Field(min_length=1)
    checkpoint_commit_seconds: float = Field(ge=0.0)
    graceful_exit_seconds: float = Field(ge=0.0)
    recovery_process: HFProcessEvidence
    recovery: HFRunSummary
    recovery_rto_seconds: float = Field(gt=0.0)
    gate: HFPreemptionGateV1
    final_verdict: Literal["VERIFIED", "FAILED"]
    verified_persisted_bytes: int | None = Field(default=None, gt=0)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    sarif_path: Literal["results.sarif"] = "results.sarif"
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_certification(self) -> Self:
        timestamps = (
            self.created_at,
            self.signal_sent_at,
        )
        if any(value.tzinfo is None for value in timestamps):
            raise ValueError("preemption certification timestamps must be timezone-aware")
        if self.total_steps <= self.preemption_step:
            raise ValueError("preemption step must precede total steps")
        pids = {
            self.control_process.worker_pid,
            self.preemption_process.worker_pid,
            self.recovery_process.worker_pid,
        }
        if len(pids) != 3:
            raise ValueError("control, preemption, and recovery must use distinct processes")
        if self.control.worker_pid != self.control_process.worker_pid:
            raise ValueError("control summary and process PIDs differ")
        if self.ready_event.worker_pid != self.preemption_process.worker_pid:
            raise ValueError("preemption-ready and process PIDs differ")
        if self.commit_event.worker_pid != self.preemption_process.worker_pid:
            raise ValueError("preemption commit and process PIDs differ")
        if self.recovery.worker_pid != self.recovery_process.worker_pid:
            raise ValueError("recovery summary and process PIDs differ")
        if self.ready_event.completed_step != self.preemption_step:
            raise ValueError("preemption-ready event reports the wrong step")
        if self.commit_event.checkpoint.global_step != self.preemption_step:
            raise ValueError("preemption checkpoint reports the wrong step")
        if self.preemption_process.exit_code != 0 or not self.preemption_process.exit_verified:
            raise ValueError("preemption worker must exit cleanly within the grace period")
        if self.recovery_process.exit_code != 0 or not self.recovery_process.exit_verified:
            raise ValueError("preemption recovery worker must exit successfully")
        if not (
            self.ready_event.emitted_at
            <= self.signal_sent_at
            <= self.commit_event.signal_received_at
            <= self.commit_event.checkpoint_committed_at
            <= self.preemption_process.completed_at
        ):
            raise ValueError("preemption lifecycle timestamps are out of order")
        if self.graceful_exit_seconds > self.grace_period_seconds:
            raise ValueError("preemption worker exceeded its declared grace period")
        if (
            self.recovery_rto_seconds
            != (
                self.recovery_process.completed_at - self.recovery_process.started_at
            ).total_seconds()
        ):
            raise ValueError("preemption recovery RTO differs from process evidence")
        if self.final_verdict == "VERIFIED":
            if not self.gate.passed or self.gate.failed_check_ids:
                raise ValueError("verified preemption result requires every Gate check")
            if self.verified_persisted_bytes is None:
                raise ValueError("verified preemption result requires post-Gate bytes")
        elif self.gate.passed or self.verified_persisted_bytes is not None:
            raise ValueError("failed preemption result cannot claim verification or bytes")
        return self
