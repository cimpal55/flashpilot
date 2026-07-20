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
CIKind = Literal[
    "static-audit",
    "native-qualification",
    "hf-qualification",
    "hf-preemption-certification",
    "lightning-qualification",
    "distributed-qualification",
    "deepspeed-qualification",
]
CIFramework = Literal[
    "native-pytorch",
    "huggingface-trainer",
    "pytorch-lightning",
    "pytorch-distributed",
    "deepspeed",
    "unknown",
]
CIAdapter = Literal[
    "native-pytorch",
    "huggingface-trainer",
    "pytorch-lightning",
    "pytorch-fsdp",
    "deepspeed-engine",
]
CIStrategy = Literal["fsdp", "zero"]
CIImplementation = Literal["fully_shard", "zero-stage-2"]
CIBackend = Literal["gloo"]


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
    kind: CIKind
    status: CIStatus
    qualification_profile: QualificationProfile
    framework: CIFramework
    adapter: CIAdapter | None = None
    strategy: CIStrategy | None = None
    implementation: CIImplementation | None = None
    backend: CIBackend | None = None
    world_size: int | None = Field(default=None, ge=1)
    zero_stage: Literal[2] | None = None
    checks: tuple[CICheck, ...] = Field(min_length=1)
    fault: CIFault | None = None
    fault_target_rank: Literal[0, 1] | None = None
    rpo_steps: int | None = Field(default=None, ge=0)
    rto_seconds: float | None = Field(default=None, gt=0.0)
    atol: float | None = Field(default=None, ge=0.0)
    rtol: float | None = Field(default=None, ge=0.0)

    @model_validator(mode="after")
    def validate_evidence(self) -> Self:
        identifiers = [check.check_id for check in self.checks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("CI check identifiers must be unique")
        if self.kind == "static-audit":
            runtime_values = (
                self.adapter,
                self.strategy,
                self.implementation,
                self.backend,
                self.world_size,
                self.zero_stage,
                self.fault,
                self.fault_target_rank,
                self.rpo_steps,
                self.rto_seconds,
                self.atol,
                self.rtol,
            )
            if any(value is not None for value in runtime_values):
                raise ValueError("static audit cannot claim runtime qualification metrics")
            if self.status is CIStatus.VERIFIED:
                raise ValueError("static audit can never become VERIFIED")
        elif any(
            value is None
            for value in (
                self.adapter,
                self.fault,
                self.rpo_steps,
                self.rto_seconds,
                self.atol,
                self.rtol,
            )
        ):
            raise ValueError(
                "qualification evidence requires identity, fault, RPO, RTO, and tolerances"
            )
        if self.kind == "distributed-qualification":
            if (
                self.framework != "pytorch-distributed"
                or self.adapter != "pytorch-fsdp"
                or self.strategy != "fsdp"
                or self.implementation != "fully_shard"
                or self.backend != "gloo"
                or self.world_size != 2
                or self.zero_stage is not None
            ):
                raise ValueError("distributed CI evidence has an unsupported topology identity")
        elif self.kind == "deepspeed-qualification":
            if (
                self.framework != "deepspeed"
                or self.adapter != "deepspeed-engine"
                or self.strategy != "zero"
                or self.implementation != "zero-stage-2"
                or self.backend != "gloo"
                or self.world_size != 2
                or self.zero_stage != 2
            ):
                raise ValueError("DeepSpeed CI evidence has an unsupported topology identity")
        elif any(
            value is not None
            for value in (
                self.strategy,
                self.implementation,
                self.backend,
                self.world_size,
                self.zero_stage,
            )
        ):
            raise ValueError("non-distributed CI evidence cannot claim a distributed topology")
        if self.fault == "rank_process_termination":
            if self.kind not in {"distributed-qualification", "deepspeed-qualification"}:
                raise ValueError("rank termination is valid only for distributed qualification")
            if self.fault_target_rank not in (0, 1):
                raise ValueError("rank termination requires exact target rank 0 or 1")
        elif self.fault_target_rank is not None:
            raise ValueError("only rank termination may identify a target rank")
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
