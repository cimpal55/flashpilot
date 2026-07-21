"""Closed organization qualification-policy models.

The organization layer constrains one explicitly supplied repository suite
policy. It is deliberately not an expression language, authorization engine,
or remote policy-distribution mechanism.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.ci.models import CICheck, CICheckStatus
from flashpilot.ci.qualification_policy_models import (
    QualificationPolicyEvaluationV1,
    QualificationPolicyRequirement,
    StaticAuditPolicyRequirement,
    qualification_requirement_selector,
)
from flashpilot.domain.manifests import SHA256_PATTERN


class StrictOrganizationPolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class OrganizationQualificationPolicyV1(StrictOrganizationPolicyModel):
    schema_version: Literal["flashpilot-organization-qualification-policy-v1"] = (
        "flashpilot-organization-qualification-policy-v1"
    )
    organization_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    policy_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    scope_binding: Literal["explicit"] = "explicit"
    repository_policy_binding: Literal["explicit-local-source"] = "explicit-local-source"
    requirement_inventory: Literal["exact"] = "exact"
    unknown_state: Literal["fail"] = "fail"
    missing_evidence: Literal["fail"] = "fail"
    unlisted_evidence: Literal["fail"] = "fail"
    all_requirements_must_pass: Literal[True] = True
    require_signed_runtime_attestations: Literal[True] = True
    requirements: tuple[QualificationPolicyRequirement, ...] = Field(
        min_length=1,
        max_length=64,
    )

    @field_validator("requirements")
    @classmethod
    def validate_requirements(
        cls,
        requirements: tuple[QualificationPolicyRequirement, ...],
    ) -> tuple[QualificationPolicyRequirement, ...]:
        identifiers = tuple(requirement.requirement_id for requirement in requirements)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("organization policy requirement IDs must be unique")
        selectors = tuple(qualification_requirement_selector(item) for item in requirements)
        if len(selectors) != len(set(selectors)):
            raise ValueError("organization policy selectors must be unique")
        unsigned = tuple(
            item.requirement_id
            for item in requirements
            if not isinstance(item, StaticAuditPolicyRequirement)
            and not item.require_signed_attestation
        )
        if unsigned:
            raise ValueError("organization runtime requirements must require signed attestations")
        return requirements


class OrganizationRequirementEvaluation(StrictOrganizationPolicyModel):
    requirement_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    repository_requirement_id: str | None = Field(
        default=None,
        pattern=r"^[a-z][a-z0-9-]*$",
        max_length=80,
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
            raise ValueError("organization requirement verdict must derive from every check")
        prefix = f"organization.{self.requirement_id}."
        if any(not check.check_id.startswith(prefix) for check in self.checks):
            raise ValueError("organization requirement checks must use their exact ID prefix")
        return self


class OrganizationPolicyEvaluationV1(StrictOrganizationPolicyModel):
    schema_version: Literal["flashpilot-organization-policy-evaluation-v1"] = (
        "flashpilot-organization-policy-evaluation-v1"
    )
    organization_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    policy_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    scope_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    organization_policy_sha256: str = Field(pattern=SHA256_PATTERN)
    repository_policy_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    repository_policy_sha256: str = Field(pattern=SHA256_PATTERN)
    repository_policy_evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    repository_policy_evaluation: QualificationPolicyEvaluationV1
    passed: bool
    checks: tuple[CICheck, ...] = Field(min_length=1)
    requirements: tuple[OrganizationRequirementEvaluation, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]

    @model_validator(mode="after")
    def derive_verdict_and_bind_repository_evaluation(self) -> Self:
        requirement_ids = tuple(item.requirement_id for item in self.requirements)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("organization evaluation requirement IDs must be unique")
        checks = self.all_checks
        check_ids = tuple(check.check_id for check in checks)
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("organization evaluation check IDs must be unique")
        if any(not check.check_id.startswith("organization.") for check in self.checks):
            raise ValueError("organization policy checks must use the organization prefix")
        failed = tuple(check.check_id for check in checks if check.status is CICheckStatus.FAIL)
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("organization policy verdict must derive from every check")
        serialized_repository_evaluation = (
            json.dumps(
                self.repository_policy_evaluation.model_dump(mode="json"),
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
        if (
            hashlib.sha256(serialized_repository_evaluation).hexdigest()
            != self.repository_policy_evaluation_sha256
        ):
            raise ValueError("repository policy evaluation hash is inconsistent")
        if (
            self.repository_policy_id != self.repository_policy_evaluation.policy_id
            or self.repository_policy_sha256 != self.repository_policy_evaluation.policy_sha256
        ):
            raise ValueError("repository policy identity differs from its evaluation")
        return self

    @property
    def all_checks(self) -> tuple[CICheck, ...]:
        return self.checks + tuple(
            check for requirement in self.requirements for check in requirement.checks
        )
