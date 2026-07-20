"""Typed CI policy and normalized run-evidence models."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.contracts.models import QualificationProfile

CIFault = Literal[
    "process_termination",
    "managed_preemption",
    "checkpoint_restart",
    "rank_process_termination",
]


class StrictCIModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CIStatus(StrEnum):
    VERIFIED = "VERIFIED"
    PASS = "PASS"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"


class CICheckStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class CIPolicyV1(StrictCIModel):
    schema_version: Literal["flashpilot-ci-policy-v1"] = "flashpilot-ci-policy-v1"
    qualification_profile: Literal[
        QualificationProfile.EXACT_TRAINING_RESUME,
        QualificationProfile.PREEMPTION_SAFE_TRAINING,
    ] = QualificationProfile.EXACT_TRAINING_RESUME
    unknown_state: Literal["fail"] = "fail"
    required_faults: tuple[CIFault, ...] = Field(min_length=1)
    max_rpo_steps: int = Field(ge=0)
    max_rto_seconds: float = Field(gt=0.0)
    require_attestation: bool

    @field_validator("required_faults")
    @classmethod
    def unique_faults(
        cls,
        values: tuple[CIFault, ...],
    ) -> tuple[CIFault, ...]:
        if len(values) != len(set(values)):
            raise ValueError("required fault identifiers must be unique")
        return tuple(sorted(values))


class CICheck(StrictCIModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    status: CICheckStatus
    summary: str = Field(min_length=1, max_length=1_000)
    expected: str | None = None
    actual: str | None = None


class CIRunEvidence(StrictCIModel):
    schema_version: Literal["flashpilot-ci-run-evidence-v1"] = "flashpilot-ci-run-evidence-v1"
    kind: Literal[
        "static-audit",
        "native-qualification",
        "hf-qualification",
        "hf-preemption-certification",
        "lightning-qualification",
        "distributed-qualification",
        "deepspeed-qualification",
    ]
    status: CIStatus
    qualification_profile: QualificationProfile
    framework: Literal[
        "native-pytorch",
        "huggingface-trainer",
        "pytorch-lightning",
        "pytorch-distributed",
        "deepspeed",
        "unknown",
    ]
    checks: tuple[CICheck, ...] = Field(min_length=1)
    fault: CIFault | None = None
    rpo_steps: int | None = Field(default=None, ge=0)
    rto_seconds: float | None = Field(default=None, gt=0.0)

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        identifiers = [check.check_id for check in self.checks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("CI check identifiers must be unique")
        if self.kind == "static-audit":
            if self.fault is not None or self.rpo_steps is not None or self.rto_seconds is not None:
                raise ValueError("static audit cannot claim runtime qualification metrics")
            if self.status is CIStatus.VERIFIED:
                raise ValueError("static audit can never become VERIFIED")
        elif self.fault is None or self.rpo_steps is None or self.rto_seconds is None:
            raise ValueError("qualification evidence requires fault, RPO, and RTO")
        passing_statuses = {CICheckStatus.PASS, CICheckStatus.NOT_APPLICABLE}
        if self.status in {CIStatus.VERIFIED, CIStatus.PASS} and any(
            check.status not in passing_statuses for check in self.checks
        ):
            raise ValueError("passing CI evidence cannot contain non-passing checks")
        return self


class CIPolicyEvaluation(StrictCIModel):
    schema_version: Literal["flashpilot-ci-policy-evaluation-v1"] = (
        "flashpilot-ci-policy-evaluation-v1"
    )
    passed: bool
    checks: tuple[CICheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        failed = tuple(
            check.check_id for check in self.checks if check.status is CICheckStatus.FAIL
        )
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("CI policy verdict must derive from every policy check")
        return self
