"""Strict evidence models for previous-valid checkpoint fallback."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath
from flashpilot.domain.recovery import (
    CheckpointCommittedEvent,
    CrashMetadata,
    RecoveryGateResult,
    RecoveryProcessMetadata,
    RecoveryWorkerResult,
    RngStateDigests,
    RuntimeSnapshot,
)

FallbackSelectionCheckId = Literal[
    "process.producer-terminated",
    "corruption.newest-changed",
    "corruption.newest-rejected",
    "discovery.only-previous-valid",
    "discovery.previous-selected",
    "immutability.previous-preserved",
    "immutability.corrupt-newest-preserved",
]


class StrictFallbackModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FallbackCheckpointRecord(StrictFallbackModel):
    checkpoint_path: ManagedRelativePath
    global_step: int = Field(gt=0)
    committed_at: datetime
    snapshot: RuntimeSnapshot
    rng_state: RngStateDigests

    @model_validator(mode="after")
    def validate_record(self) -> Self:
        if self.committed_at.tzinfo is None:
            raise ValueError("checkpoint commit timestamp must include a timezone")
        if self.snapshot.global_step != self.global_step:
            raise ValueError("checkpoint record step and snapshot disagree")
        if self.checkpoint_path != f"checkpoints/checkpoint-step-{self.global_step:06d}":
            raise ValueError("checkpoint record path must derive from its global step")
        return self


class FallbackCheckpointSetEvent(StrictFallbackModel):
    schema_version: Literal["flashpilot-fallback-checkpoint-set-v1"] = (
        "flashpilot-fallback-checkpoint-set-v1"
    )
    event: Literal["fallback_checkpoint_set_committed"] = "fallback_checkpoint_set_committed"
    worker_pid: int = Field(gt=0)
    checkpoints: tuple[FallbackCheckpointRecord, ...] = Field(min_length=2, max_length=2)
    last_completed_step: Literal[4] = 4

    @model_validator(mode="after")
    def validate_fixed_checkpoint_set(self) -> Self:
        if tuple(record.global_step for record in self.checkpoints) != (2, 4):
            raise ValueError("fallback producer must commit checkpoints at steps 2 and 4")
        return self


class FallbackSelectionCheck(StrictFallbackModel):
    check_id: FallbackSelectionCheckId
    status: Literal["pass", "fail"]
    summary: str = Field(min_length=1, max_length=500)
    expected: str = Field(min_length=1, max_length=500)
    actual: str = Field(min_length=1, max_length=500)


class PreviousValidFallbackResult(StrictFallbackModel):
    schema_version: Literal["flashpilot-previous-valid-fallback-v1"] = (
        "flashpilot-previous-valid-fallback-v1"
    )
    run_id: str = Field(min_length=1)
    created_at: datetime
    profile: Literal["ci"] = "ci"
    scenario: Literal["corrupt-newest"] = "corrupt-newest"
    control: RuntimeSnapshot
    checkpoint_set_event: FallbackCheckpointSetEvent
    selected_checkpoint_event: CheckpointCommittedEvent
    producer_crash: CrashMetadata
    newest_validation_error: Literal["payload checksum mismatch: model.pt"]
    valid_candidate_steps: tuple[Literal[2], ...]
    selected_checkpoint_step: Literal[2]
    selected_checkpoint_path: Literal["checkpoints/checkpoint-step-000002"]
    newest_checkpoint_path: Literal["checkpoints/checkpoint-step-000004"]
    previous_sha256_before: str = Field(pattern=SHA256_PATTERN)
    previous_sha256_after: str = Field(pattern=SHA256_PATTERN)
    newest_sha256_before_corruption: str = Field(pattern=SHA256_PATTERN)
    newest_sha256_after_corruption: str = Field(pattern=SHA256_PATTERN)
    newest_sha256_after_recovery: str = Field(pattern=SHA256_PATTERN)
    selection_checks: tuple[FallbackSelectionCheck, ...] = Field(min_length=7, max_length=7)
    recovery_process: RecoveryProcessMetadata
    recovery: RecoveryWorkerResult
    gate: RecoveryGateResult
    recovery_verified: bool
    final_verdict: Literal["VERIFIED", "FAILED"]
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    junit_path: Literal["junit.xml"] = "junit.xml"
    job_summary_path: Literal["job-summary.md"] = "job-summary.md"
    attestation_emitted: Literal[False] = False
    storage_savings_reported: Literal[False] = False
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def derive_qualification(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("fallback result timestamp must include a timezone")
        event = self.checkpoint_set_event
        if (
            self.producer_crash.worker_pid != event.worker_pid
            or self.producer_crash.checkpoint_step != 4
            or self.producer_crash.checkpoint_path != self.newest_checkpoint_path
            or not self.producer_crash.termination_verified
            or self.producer_crash.termination_exit_code == 0
        ):
            raise ValueError("producer crash evidence does not bind the newest checkpoint")
        selected = self.selected_checkpoint_event
        if (
            selected.worker_pid != event.worker_pid
            or selected.checkpoint_step != self.selected_checkpoint_step
            or selected.checkpoint_path != self.selected_checkpoint_path
            or selected.last_completed_step != event.last_completed_step
        ):
            raise ValueError("selected checkpoint event does not bind fallback selection")
        if self.valid_candidate_steps != (2,):
            raise ValueError("only the previous checkpoint may remain valid")
        if self.previous_sha256_before != self.previous_sha256_after:
            raise ValueError("previous checkpoint must remain unchanged")
        if self.newest_sha256_before_corruption == self.newest_sha256_after_corruption:
            raise ValueError("newest checkpoint corruption must change its fingerprint")
        if self.newest_sha256_after_corruption != self.newest_sha256_after_recovery:
            raise ValueError("corrupt newest checkpoint must remain preserved after detection")
        expected_check_ids: tuple[FallbackSelectionCheckId, ...] = (
            "process.producer-terminated",
            "corruption.newest-changed",
            "corruption.newest-rejected",
            "discovery.only-previous-valid",
            "discovery.previous-selected",
            "immutability.previous-preserved",
            "immutability.corrupt-newest-preserved",
        )
        if tuple(check.check_id for check in self.selection_checks) != expected_check_ids:
            raise ValueError("fallback selection checks must use the complete fixed order")
        selection_passed = all(check.status == "pass" for check in self.selection_checks)
        if (
            self.recovery.checkpoint_path != self.selected_checkpoint_path
            or self.recovery.worker_pid != self.recovery_process.worker_pid
            or self.recovery.worker_pid == event.worker_pid
        ):
            raise ValueError("recovery process does not bind the selected previous checkpoint")
        if self.gate.achieved_rollback_steps != 2 or self.gate.hard_rollback_limit_steps != 2:
            raise ValueError("fallback Recovery Gate must enforce the fixed two-step RPO")
        verified = selection_passed and self.gate.passed and not self.gate.failed_check_ids
        if self.recovery_verified != verified:
            raise ValueError("fallback recovery verdict must derive from selection and gate checks")
        if self.final_verdict != ("VERIFIED" if verified else "FAILED"):
            raise ValueError("fallback text verdict is inconsistent")
        return self
