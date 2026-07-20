"""Strict recovery-attestation and evidence-manifest schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.contracts.models import QualificationProfile
from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath

EVIDENCE_MANIFEST_PATH = "evidence-manifest.json"
RECOVERY_ATTESTATION_PATH = "recovery.attestation.json"
ATTESTATION_JUNIT_PATH = "attestation.junit.xml"
PERSISTENCE_CONTRACT_PATH = "persistence-contract.json"
ENVIRONMENT_PATH = "environment.json"
STATEMENT_ARTIFACT_PATHS = (
    ATTESTATION_JUNIT_PATH,
    EVIDENCE_MANIFEST_PATH,
    RECOVERY_ATTESTATION_PATH,
)


class StrictAttestationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EvidenceEntry(StrictAttestationModel):
    path: ManagedRelativePath
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern=SHA256_PATTERN)


class EvidenceManifestV1(StrictAttestationModel):
    schema_version: Literal["flashpilot-evidence-manifest-v1"] = "flashpilot-evidence-manifest-v1"
    root_scope: Literal["attestation-directory"] = "attestation-directory"
    entries: tuple[EvidenceEntry, ...] = Field(min_length=1)
    excluded_statement_artifacts: tuple[ManagedRelativePath, ...] = STATEMENT_ARTIFACT_PATHS

    @field_validator("entries")
    @classmethod
    def canonicalize_entries(cls, entries: tuple[EvidenceEntry, ...]) -> tuple[EvidenceEntry, ...]:
        return tuple(sorted(entries, key=lambda entry: entry.path))

    @model_validator(mode="after")
    def validate_closed_inventory(self) -> Self:
        paths = [entry.path for entry in self.entries]
        if len(paths) != len(set(paths)):
            raise ValueError("evidence manifest paths must be unique")
        if tuple(self.excluded_statement_artifacts) != STATEMENT_ARTIFACT_PATHS:
            raise ValueError("evidence manifest statement exclusions are fixed")
        overlap = sorted(set(paths) & set(STATEMENT_ARTIFACT_PATHS))
        if overlap:
            raise ValueError(
                f"statement artifacts cannot be evidence entries: {', '.join(overlap)}"
            )
        return self


class DependencyVersion(StrictAttestationModel):
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]*$")
    version: str = Field(min_length=1, max_length=200)


class DependencyEnvironmentV1(StrictAttestationModel):
    schema_version: Literal["flashpilot-dependency-environment-v1"] = (
        "flashpilot-dependency-environment-v1"
    )
    python_version: str = Field(min_length=1)
    platform: str = Field(min_length=1)
    code_commit: str = Field(pattern=r"^(?:[0-9a-f]{40}|unavailable)$")
    source_tree_state: Literal["clean", "dirty", "unavailable"]
    cpu_only: Literal[True] = True
    torch_threads: int = Field(gt=0)
    deterministic_algorithms: bool
    dependencies: tuple[DependencyVersion, ...] = Field(min_length=1)

    @field_validator("dependencies")
    @classmethod
    def canonicalize_dependencies(
        cls,
        dependencies: tuple[DependencyVersion, ...],
    ) -> tuple[DependencyVersion, ...]:
        ordered = tuple(sorted(dependencies, key=lambda item: item.name))
        if len({item.name for item in ordered}) != len(ordered):
            raise ValueError("dependency names must be unique")
        return ordered


class RecoveryAttestationV1(StrictAttestationModel):
    schema_version: Literal["flashpilot-attestation-v1"] = "flashpilot-attestation-v1"
    verdict: Literal["verified"] = "verified"
    qualification_profile: Literal[QualificationProfile.EXACT_TRAINING_RESUME] = (
        QualificationProfile.EXACT_TRAINING_RESUME
    )
    framework: Literal["native-pytorch", "transformers"] = "native-pytorch"
    framework_version: str = Field(min_length=1, max_length=200)
    adapter: Literal["native-pytorch", "huggingface-trainer"] = "native-pytorch"
    run_id: str = Field(min_length=1)
    issued_at: datetime
    code_commit: str = Field(pattern=r"^(?:[0-9a-f]{40}|unavailable)$")
    source_tree_state: Literal["clean", "dirty", "unavailable"]
    dependency_environment_path: Literal["environment.json"] = ENVIRONMENT_PATH
    dependency_environment_sha256: str = Field(pattern=SHA256_PATTERN)
    checkpoint_path: ManagedRelativePath
    checkpoint_sha256: str = Field(pattern=SHA256_PATTERN)
    checkpoint_file_count: int = Field(gt=0)
    checkpoint_logical_bytes: int = Field(gt=0)
    persistence_contract_path: Literal["persistence-contract.json"] = PERSISTENCE_CONTRACT_PATH
    persistence_contract_sha256: str = Field(pattern=SHA256_PATTERN)
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    html_report_path: Literal["report.html"] = "report.html"
    evidence_manifest_path: Literal["evidence-manifest.json"] = EVIDENCE_MANIFEST_PATH
    evidence_manifest_sha256: str = Field(pattern=SHA256_PATTERN)
    fault_scenario: Literal["process_termination", "process-kill"] = "process_termination"
    original_worker_pid: int = Field(gt=0)
    recovery_worker_pid: int = Field(gt=0)
    control_digest: str = Field(pattern=SHA256_PATTERN)
    resumed_digest: str = Field(pattern=SHA256_PATTERN)
    control_evaluation_digest: str = Field(pattern=SHA256_PATTERN)
    resumed_evaluation_digest: str = Field(pattern=SHA256_PATTERN)
    checks_passed: int = Field(gt=0)
    checks_total: int = Field(gt=0)
    atol: Literal[0.0] = 0.0
    rtol: Literal[0.0] = 0.0
    rpo_steps: int = Field(ge=0)
    max_rpo_steps: int = Field(ge=0)
    rto_seconds: float = Field(gt=0.0)
    verified_persisted_bytes: int = Field(gt=0)
    signature_status: Literal["unsigned"] = "unsigned"
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_verified_claim(self) -> Self:
        if self.issued_at.tzinfo is None:
            raise ValueError("attestation issued_at must include a timezone")
        if self.original_worker_pid == self.recovery_worker_pid:
            raise ValueError("attestation must record a distinct recovery process")
        if self.control_digest != self.resumed_digest:
            raise ValueError("verified trainable-state digests must match")
        if self.control_evaluation_digest != self.resumed_evaluation_digest:
            raise ValueError("verified evaluation digests must match")
        if self.checks_passed != self.checks_total:
            raise ValueError("verified attestation requires every Recovery Gate check")
        if self.rpo_steps > self.max_rpo_steps:
            raise ValueError("attested RPO exceeds the declared maximum")
        if self.framework == "native-pytorch" and (
            self.adapter != "native-pytorch" or self.fault_scenario != "process_termination"
        ):
            raise ValueError("native attestation framework, adapter, and fault must agree")
        if self.framework == "transformers" and (
            self.adapter != "huggingface-trainer" or self.fault_scenario != "process_termination"
        ):
            raise ValueError("HF attestation framework, adapter, and fault must agree")
        return self


class AttestationVerificationCheck(StrictAttestationModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    passed: Literal[True] = True
    detail: str = Field(min_length=1, max_length=1_000)


class AttestationVerificationResult(StrictAttestationModel):
    schema_version: Literal["flashpilot-attestation-verification-v1"] = (
        "flashpilot-attestation-verification-v1"
    )
    valid: Literal[True] = True
    verdict: Literal["VERIFIED"] = "VERIFIED"
    attestation_sha256: str = Field(pattern=SHA256_PATTERN)
    checks: tuple[AttestationVerificationCheck, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_checks(self) -> Self:
        check_ids = [check.check_id for check in self.checks]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("attestation verification check IDs must be unique")
        return self
