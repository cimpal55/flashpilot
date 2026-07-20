"""Typed results for metadata-only checkpoint audits."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.ci.exits import (
    EXIT_QUALIFICATION_FAILED,
    EXIT_REVIEW,
    EXIT_VERIFIED,
)
from flashpilot.contracts.models import QualificationProfile


class AuditStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class AuditFramework(StrEnum):
    NATIVE_PYTORCH = "native-pytorch"
    HUGGINGFACE_TRAINER = "huggingface-trainer"
    UNKNOWN = "unknown"


class FrameworkSelection(StrEnum):
    AUTO = "auto"
    NATIVE_PYTORCH = "native-pytorch"
    HUGGINGFACE_TRAINER = "huggingface-trainer"


class StrictAuditModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AuditCheck(StrictAuditModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    status: AuditStatus
    requirement_state_id: str | None = Field(
        default=None,
        pattern=r"^[a-z][a-z0-9_.-]*$",
    )
    summary: str = Field(min_length=1, max_length=500)
    evidence_paths: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("evidence_paths")
    @classmethod
    def canonicalize_evidence_paths(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not value or value != value.strip() for value in values):
            raise ValueError("evidence paths must be nonempty and already trimmed")
        if len(values) != len(set(values)):
            raise ValueError("evidence paths must be unique")
        return tuple(sorted(values))


class StaticAuditResult(StrictAuditModel):
    schema_version: Literal["flashpilot-static-audit-v1"] = "flashpilot-static-audit-v1"
    status: AuditStatus
    framework: AuditFramework
    qualification_profile: QualificationProfile
    checkpoint_name: str = Field(min_length=1, max_length=255)
    static_only: Literal[True] = True
    recovery_verified: Literal[False] = False
    checks: tuple[AuditCheck, ...] = Field(min_length=1)

    @field_validator("checks")
    @classmethod
    def canonicalize_checks(cls, checks: tuple[AuditCheck, ...]) -> tuple[AuditCheck, ...]:
        return tuple(sorted(checks, key=lambda check: check.check_id))

    @model_validator(mode="after")
    def validate_aggregate_status(self) -> Self:
        check_ids = [check.check_id for check in self.checks]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("audit check IDs must be unique")
        expected = aggregate_status(self.checks)
        if self.status is not expected:
            raise ValueError(f"audit status must aggregate to {expected.value}")
        return self


def aggregate_status(checks: tuple[AuditCheck, ...]) -> AuditStatus:
    statuses = {check.status for check in checks}
    if AuditStatus.FAIL in statuses:
        return AuditStatus.FAIL
    if AuditStatus.UNKNOWN in statuses:
        return AuditStatus.UNKNOWN
    if AuditStatus.WARN in statuses:
        return AuditStatus.WARN
    return AuditStatus.PASS


AUDIT_EXIT_CODES: dict[AuditStatus, int] = {
    AuditStatus.PASS: EXIT_VERIFIED,
    AuditStatus.WARN: EXIT_REVIEW,
    AuditStatus.UNKNOWN: EXIT_REVIEW,
    AuditStatus.FAIL: EXIT_QUALIFICATION_FAILED,
}
