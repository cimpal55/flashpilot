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
    qualification_profile: Literal[
        QualificationProfile.EXACT_TRAINING_RESUME,
        QualificationProfile.PREEMPTION_SAFE_TRAINING,
    ] = QualificationProfile.EXACT_TRAINING_RESUME
    framework: Literal[
        "native-pytorch", "transformers", "lightning", "pytorch-distributed", "deepspeed"
    ] = "native-pytorch"
    framework_version: str = Field(min_length=1, max_length=200)
    adapter: Literal[
        "native-pytorch",
        "huggingface-trainer",
        "pytorch-lightning",
        "pytorch-fsdp",
        "deepspeed-engine",
    ] = "native-pytorch"
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
    fault_scenario: Literal[
        "process_termination",
        "process-kill",
        "managed_preemption",
        "checkpoint_restart",
    ] = "process_termination"
    preemption_signal: Literal["SIGTERM"] | None = None
    grace_period_seconds: int | None = Field(default=None, ge=1, le=3_600)
    checkpoint_commit_seconds: float | None = Field(default=None, ge=0.0)
    graceful_exit_seconds: float | None = Field(default=None, ge=0.0)
    rpo_tokens: int | None = Field(default=None, ge=0)
    distributed_strategy: Literal["fsdp", "zero"] | None = None
    distributed_implementation: Literal["fully_shard", "zero-stage-2"] | None = None
    distributed_backend: Literal["gloo"] | None = None
    distributed_world_size: Literal[2] | None = None
    distributed_zero_stage: Literal[2] | None = None
    original_worker_pids: tuple[int, ...] | None = Field(default=None, min_length=2, max_length=2)
    recovery_worker_pids: tuple[int, ...] | None = Field(default=None, min_length=2, max_length=2)
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
        preemption_fields = (
            self.preemption_signal,
            self.grace_period_seconds,
            self.checkpoint_commit_seconds,
            self.graceful_exit_seconds,
            self.rpo_tokens,
        )
        if self.qualification_profile is QualificationProfile.PREEMPTION_SAFE_TRAINING:
            if (
                self.framework != "transformers"
                or self.adapter != "huggingface-trainer"
                or self.fault_scenario != "managed_preemption"
                or any(value is None for value in preemption_fields)
            ):
                raise ValueError("preemption attestation fields and HF identity must agree")
            assert self.grace_period_seconds is not None
            assert self.graceful_exit_seconds is not None
            if self.graceful_exit_seconds > self.grace_period_seconds:
                raise ValueError("attested graceful exit exceeds the preemption grace period")
            return self
        if any(value is not None for value in preemption_fields):
            raise ValueError("exact-resume attestation cannot contain preemption metrics")
        distributed_fields = (
            self.distributed_strategy,
            self.distributed_implementation,
            self.distributed_backend,
            self.distributed_world_size,
            self.original_worker_pids,
            self.recovery_worker_pids,
        )
        if self.framework == "pytorch-distributed":
            if (
                self.adapter != "pytorch-fsdp"
                or self.fault_scenario != "checkpoint_restart"
                or any(value is None for value in distributed_fields)
                or self.distributed_strategy != "fsdp"
                or self.distributed_implementation != "fully_shard"
                or self.distributed_zero_stage is not None
            ):
                raise ValueError("distributed attestation fields and FSDP identity must agree")
            assert self.original_worker_pids is not None
            assert self.recovery_worker_pids is not None
            original = tuple(self.original_worker_pids)
            recovery = tuple(self.recovery_worker_pids)
            if (
                len(set(original)) != 2
                or len(set(recovery)) != 2
                or set(original) & set(recovery)
                or self.original_worker_pid != original[0]
                or self.recovery_worker_pid != recovery[0]
            ):
                raise ValueError("distributed attestation process groups are invalid")
            return self
        if self.framework == "deepspeed":
            if (
                self.adapter != "deepspeed-engine"
                or self.fault_scenario != "checkpoint_restart"
                or any(value is None for value in distributed_fields)
                or self.distributed_strategy != "zero"
                or self.distributed_implementation != "zero-stage-2"
                or self.distributed_zero_stage != 2
            ):
                raise ValueError("DeepSpeed attestation fields and ZeRO-2 identity must agree")
            assert self.original_worker_pids is not None
            assert self.recovery_worker_pids is not None
            original = tuple(self.original_worker_pids)
            recovery = tuple(self.recovery_worker_pids)
            if (
                len(set(original)) != 2
                or len(set(recovery)) != 2
                or set(original) & set(recovery)
                or self.original_worker_pid != original[0]
                or self.recovery_worker_pid != recovery[0]
            ):
                raise ValueError("DeepSpeed attestation process groups are invalid")
            return self
        if any(value is not None for value in distributed_fields) or self.distributed_zero_stage:
            raise ValueError("non-distributed attestation cannot contain topology fields")
        if self.framework == "native-pytorch" and (
            self.adapter != "native-pytorch" or self.fault_scenario != "process_termination"
        ):
            raise ValueError("native attestation framework, adapter, and fault must agree")
        if self.framework == "transformers" and (
            self.adapter != "huggingface-trainer" or self.fault_scenario != "process_termination"
        ):
            raise ValueError("HF attestation framework, adapter, and fault must agree")
        if self.framework == "lightning" and (
            self.adapter != "pytorch-lightning" or self.fault_scenario != "process_termination"
        ):
            raise ValueError("Lightning attestation framework, adapter, and fault must agree")
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
