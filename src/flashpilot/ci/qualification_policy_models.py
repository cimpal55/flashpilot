"""Closed typed models for repository qualification-suite policy enforcement."""

from __future__ import annotations

import json
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.ci.models import CICheck, CICheckStatus, CIRunEvidence
from flashpilot.contracts.models import QualificationProfile


class StrictQualificationPolicyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class StaticAuditPolicyRequirement(StrictQualificationPolicyModel):
    requirement_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    kind: Literal["static-audit"]
    framework: Literal["native-pytorch", "huggingface-trainer"]
    qualification_profile: QualificationProfile
    required_status: Literal["PASS"] = "PASS"
    require_attestation: Literal[False] = False


class RuntimePolicyRequirement(StrictQualificationPolicyModel):
    requirement_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    qualification_profile: QualificationProfile
    max_rpo_steps: int = Field(ge=0, le=1_000_000)
    max_rto_seconds: float = Field(gt=0.0, le=86_400.0)
    required_status: Literal["VERIFIED"] = "VERIFIED"
    require_exact_recovery: Literal[True] = True
    require_attestation: Literal[True] = True
    require_signed_attestation: bool = False


class NativePolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["native-qualification"]
    framework: Literal["native-pytorch"]
    adapter: Literal["native-pytorch"]
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME]
    fault: Literal["process_termination"]


class HFPolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["hf-qualification"]
    framework: Literal["huggingface-trainer"]
    adapter: Literal["huggingface-trainer"]
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME]
    fault: Literal["process_termination"]


class HFPreemptionPolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["hf-preemption-certification"]
    framework: Literal["huggingface-trainer"]
    adapter: Literal["huggingface-trainer"]
    qualification_profile: Literal[QualificationProfile.PREEMPTION_SAFE_TRAINING]
    fault: Literal["managed_preemption"]


class LightningPolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["lightning-qualification"]
    framework: Literal["pytorch-lightning"]
    adapter: Literal["pytorch-lightning"]
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME]
    fault: Literal["process_termination"]


class DistributedPolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["distributed-qualification"]
    framework: Literal["pytorch-distributed"]
    adapter: Literal["pytorch-fsdp"]
    strategy: Literal["fsdp"]
    implementation: Literal["fully_shard"]
    backend: Literal["gloo"]
    world_size: Literal[2]
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME]
    fault: Literal["checkpoint_restart", "rank_process_termination"]
    fault_target_rank: Literal[0, 1] | None = None

    @model_validator(mode="after")
    def validate_target_rank(self) -> Self:
        if self.fault == "rank_process_termination" and self.fault_target_rank is None:
            raise ValueError("rank-termination policy requires target rank 0 or 1")
        if self.fault == "checkpoint_restart" and self.fault_target_rank is not None:
            raise ValueError("clean distributed restart cannot select a target rank")
        return self


class DeepSpeedPolicyRequirement(RuntimePolicyRequirement):
    kind: Literal["deepspeed-qualification"]
    framework: Literal["deepspeed"]
    adapter: Literal["deepspeed-engine"]
    strategy: Literal["zero"]
    implementation: Literal["zero-stage-2"]
    zero_stage: Literal[2]
    backend: Literal["gloo"]
    world_size: Literal[2]
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME]
    fault: Literal["checkpoint_restart", "rank_process_termination"]
    fault_target_rank: Literal[0, 1] | None = None

    @model_validator(mode="after")
    def validate_target_rank(self) -> Self:
        if self.fault == "rank_process_termination" and self.fault_target_rank is None:
            raise ValueError("rank-termination policy requires target rank 0 or 1")
        if self.fault == "checkpoint_restart" and self.fault_target_rank is not None:
            raise ValueError("clean DeepSpeed restart cannot select a target rank")
        return self


QualificationPolicyRequirement = Annotated[
    StaticAuditPolicyRequirement
    | NativePolicyRequirement
    | HFPolicyRequirement
    | HFPreemptionPolicyRequirement
    | LightningPolicyRequirement
    | DistributedPolicyRequirement
    | DeepSpeedPolicyRequirement,
    Field(discriminator="kind"),
]

_SELECTOR_EXCLUDED_FIELDS = {
    "requirement_id",
    "max_rpo_steps",
    "max_rto_seconds",
    "required_status",
    "require_exact_recovery",
    "require_attestation",
    "require_signed_attestation",
}


def qualification_requirement_selector(
    requirement: QualificationPolicyRequirement,
) -> str:
    """Return the canonical closed selector shared by suite and organization policy."""

    selector = requirement.model_dump(
        mode="json",
        exclude=_SELECTOR_EXCLUDED_FIELDS,
    )
    return json.dumps(selector, sort_keys=True, separators=(",", ":"))


class QualificationPolicyV1(StrictQualificationPolicyModel):
    schema_version: Literal["flashpilot-qualification-policy-v1"] = (
        "flashpilot-qualification-policy-v1"
    )
    policy_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    evidence_binding: Literal["explicit"] = "explicit"
    unknown_state: Literal["fail"] = "fail"
    missing_evidence: Literal["fail"] = "fail"
    duplicate_evidence: Literal["fail"] = "fail"
    unlisted_evidence: Literal["fail"] = "fail"
    all_requirements_must_pass: Literal[True] = True
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
            raise ValueError("qualification policy requirement IDs must be unique")
        selectors = [
            qualification_requirement_selector(requirement) for requirement in requirements
        ]
        if len(selectors) != len(set(selectors)):
            raise ValueError("qualification policy selectors must be unique")
        return requirements


class QualificationPolicyEvidence(StrictQualificationPolicyModel):
    schema_version: Literal["flashpilot-qualification-policy-evidence-v1"] = (
        "flashpilot-qualification-policy-evidence-v1"
    )
    source_artifact: Literal["result.json", "audit.json"]
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    attestation_status: Literal["verified", "missing", "not-applicable"]
    attestation_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    attestation_signature_status: Literal["verified", "unsigned", "missing", "not-applicable"]
    signing_key_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    signature_artifact_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    evidence: CIRunEvidence

    @model_validator(mode="after")
    def validate_evidence_binding(self) -> Self:
        expected_source = "audit.json" if self.evidence.kind == "static-audit" else "result.json"
        if self.source_artifact != expected_source:
            raise ValueError("policy evidence source differs from the normalized evidence kind")
        if self.attestation_status == "verified" and self.attestation_sha256 is None:
            raise ValueError("verified policy evidence requires an attestation SHA-256")
        if self.attestation_status != "verified" and self.attestation_sha256 is not None:
            raise ValueError("non-verified attestation status cannot carry an attestation hash")
        if self.evidence.kind == "static-audit" and self.attestation_status != "not-applicable":
            raise ValueError("static audit policy evidence cannot claim an attestation")
        signature_hashes = (self.signing_key_sha256, self.signature_artifact_sha256)
        if self.attestation_status == "not-applicable":
            if self.attestation_signature_status != "not-applicable":
                raise ValueError("static audit signature status must be not-applicable")
        elif self.attestation_status == "missing":
            if self.attestation_signature_status != "missing":
                raise ValueError("missing attestation cannot claim a signature status")
        elif self.attestation_signature_status not in {"verified", "unsigned"}:
            raise ValueError("verified attestation requires a closed signature status")
        if self.attestation_signature_status == "verified" and any(
            value is None for value in signature_hashes
        ):
            raise ValueError("verified signature status requires key and artifact hashes")
        if self.attestation_signature_status != "verified" and any(
            value is not None for value in signature_hashes
        ):
            raise ValueError("non-verified signature status cannot claim signature hashes")
        return self


class QualificationRequirementEvaluation(StrictQualificationPolicyModel):
    requirement_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    passed: bool
    evidence: QualificationPolicyEvidence | None = None
    checks: tuple[CICheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        failed = tuple(
            check.check_id for check in self.checks if check.status is CICheckStatus.FAIL
        )
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("requirement verdict must derive from every typed policy check")
        prefix = f"policy.{self.requirement_id}."
        if any(not check.check_id.startswith(prefix) for check in self.checks):
            raise ValueError("requirement checks must use their exact policy ID prefix")
        return self


class QualificationPolicyEvaluationV1(StrictQualificationPolicyModel):
    schema_version: Literal["flashpilot-qualification-policy-evaluation-v1"] = (
        "flashpilot-qualification-policy-evaluation-v1"
    )
    policy_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$", max_length=80)
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    passed: bool
    requirements: tuple[QualificationRequirementEvaluation, ...] = Field(min_length=1)
    failed_requirement_ids: tuple[str, ...]

    @model_validator(mode="after")
    def derive_verdict(self) -> Self:
        identifiers = tuple(item.requirement_id for item in self.requirements)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("policy evaluation requirement IDs must be unique")
        failed = tuple(item.requirement_id for item in self.requirements if not item.passed)
        if failed != self.failed_requirement_ids or self.passed != (not failed):
            raise ValueError("policy verdict must derive from every requirement verdict")
        return self

    @property
    def checks(self) -> tuple[CICheck, ...]:
        return tuple(check for requirement in self.requirements for check in requirement.checks)
