"""Strict aggregate evidence for repeated randomized fault timing."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath


class StrictTimingModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FaultTimingScheduleEntry(StrictTimingModel):
    iteration: int = Field(gt=0, le=32)
    checkpoint_step: int = Field(ge=1, le=7)
    post_commit_steps: int = Field(ge=0, le=3)
    fault_after_step: int = Field(ge=1, le=7)

    @model_validator(mode="after")
    def derive_fault_boundary(self) -> Self:
        if self.fault_after_step != self.checkpoint_step + self.post_commit_steps:
            raise ValueError("fault boundary must derive from checkpoint and post-commit steps")
        return self


class FaultTimingTrialResult(StrictTimingModel):
    schema_version: Literal["flashpilot-fault-timing-trial-v1"] = "flashpilot-fault-timing-trial-v1"
    schedule: FaultTimingScheduleEntry
    trial_path: ManagedRelativePath
    trial_result_path: ManagedRelativePath
    trial_result_sha256: str = Field(pattern=SHA256_PATTERN)
    trial_directory_sha256: str = Field(pattern=SHA256_PATTERN)
    trial_file_count: int = Field(gt=0)
    producer_pid: int = Field(gt=0)
    producer_exit_code: int
    producer_termination_verified: bool
    recovery_pid: int = Field(gt=0)
    recovery_exit_code: int
    recovery_exit_verified: bool
    gate_checks_passed: int = Field(ge=0)
    gate_checks_total: Literal[24] = 24
    failed_gate_check_ids: tuple[str, ...]
    achieved_rpo_steps: int = Field(ge=0, le=3)
    max_rpo_steps: Literal[3] = 3
    rto_seconds: float = Field(gt=0.0)
    exact_control_match: bool
    passed: bool

    @model_validator(mode="after")
    def derive_trial_verdict(self) -> Self:
        expected_trial_path = f"trials/trial-{self.schedule.iteration:04d}"
        if self.trial_path != expected_trial_path:
            raise ValueError("trial path must derive from its schedule iteration")
        if self.trial_result_path != f"{expected_trial_path}/result.json":
            raise ValueError("trial result path must be inside its trial directory")
        if self.achieved_rpo_steps != self.schedule.post_commit_steps:
            raise ValueError("achieved RPO must equal completed post-commit work")
        expected = (
            self.producer_pid != self.recovery_pid
            and self.producer_exit_code != 0
            and self.producer_termination_verified
            and self.recovery_exit_code == 0
            and self.recovery_exit_verified
            and self.gate_checks_passed == self.gate_checks_total
            and not self.failed_gate_check_ids
            and self.achieved_rpo_steps <= self.max_rpo_steps
            and self.exact_control_match
        )
        if self.passed != expected:
            raise ValueError(
                "fault-timing trial verdict must derive from process and gate evidence"
            )
        return self


class RandomizedFaultTimingResult(StrictTimingModel):
    schema_version: Literal["flashpilot-randomized-fault-timing-v1"] = (
        "flashpilot-randomized-fault-timing-v1"
    )
    profile: Literal["ci"] = "ci"
    strategy: Literal["safe_full"] = "safe_full"
    seed: int = Field(ge=0, le=9_223_372_036_854_775_807)
    iterations: int = Field(ge=4, le=32)
    max_rpo_steps: Literal[3] = 3
    schedule_sha256: str = Field(pattern=SHA256_PATTERN)
    trials: tuple[FaultTimingTrialResult, ...] = Field(min_length=4, max_length=32)
    observed_rpo_steps: tuple[int, ...]
    unique_timing_pairs: int = Field(gt=0)
    passed_trials: int = Field(ge=0)
    failed_trials: int = Field(ge=0)
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
        if len(self.trials) != self.iterations:
            raise ValueError("randomized timing result requires one trial per iteration")
        if tuple(trial.schedule.iteration for trial in self.trials) != tuple(
            range(1, self.iterations + 1)
        ):
            raise ValueError("fault-timing trial order must be contiguous")
        observed_rpo = tuple(sorted({trial.achieved_rpo_steps for trial in self.trials}))
        unique_pairs = len(
            {
                (trial.schedule.checkpoint_step, trial.schedule.post_commit_steps)
                for trial in self.trials
            }
        )
        passed = sum(trial.passed for trial in self.trials)
        failed = self.iterations - passed
        if observed_rpo != (0, 1, 2, 3) or self.observed_rpo_steps != observed_rpo:
            raise ValueError("randomized timing must cover every allowed RPO value")
        if (
            self.unique_timing_pairs != unique_pairs
            or self.passed_trials != passed
            or self.failed_trials != failed
        ):
            raise ValueError("randomized timing aggregates must derive from trial evidence")
        verified = failed == 0
        if self.recovery_verified != verified:
            raise ValueError("randomized timing recovery verdict must derive from every trial")
        if self.final_verdict != ("VERIFIED" if verified else "FAILED"):
            raise ValueError("randomized timing text verdict is inconsistent")
        return self
