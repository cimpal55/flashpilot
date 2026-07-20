"""Strict models for the four V0.3 checkpoint-conversion cases."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.contracts.models import QualificationProfile
from flashpilot.domain.manifests import SHA256_PATTERN, ChecksumEntry


class ConversionKind(StrEnum):
    FULL_TO_PEFT = "full-to-peft"
    PEFT_TO_MERGED = "peft-to-merged"
    SHARDED_TO_CONSOLIDATED = "sharded-to-consolidated"
    VERSION_UPGRADE_RESUME = "version-upgrade-resume"


class ConversionRepresentation(StrEnum):
    FULL_MODEL = "full-model"
    PEFT = "peft"
    MERGED_MODEL = "merged-model"
    SHARDED = "sharded"
    CONSOLIDATED = "consolidated"
    LEGACY_V1 = "legacy-v1"
    UPGRADED_V2 = "upgraded-v2"


class StrictConversionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


_REPRESENTATIONS = {
    ConversionKind.FULL_TO_PEFT: (
        ConversionRepresentation.FULL_MODEL,
        ConversionRepresentation.PEFT,
    ),
    ConversionKind.PEFT_TO_MERGED: (
        ConversionRepresentation.PEFT,
        ConversionRepresentation.MERGED_MODEL,
    ),
    ConversionKind.SHARDED_TO_CONSOLIDATED: (
        ConversionRepresentation.SHARDED,
        ConversionRepresentation.CONSOLIDATED,
    ),
    ConversionKind.VERSION_UPGRADE_RESUME: (
        ConversionRepresentation.LEGACY_V1,
        ConversionRepresentation.UPGRADED_V2,
    ),
}

_PAYLOADS = {
    ConversionRepresentation.FULL_MODEL: ("full.pt",),
    ConversionRepresentation.PEFT: ("adapter.pt", "base.pt"),
    ConversionRepresentation.MERGED_MODEL: ("merged.pt",),
    ConversionRepresentation.SHARDED: ("index.json", "shard-000.pt", "shard-001.pt"),
    ConversionRepresentation.CONSOLIDATED: ("model.pt",),
    ConversionRepresentation.LEGACY_V1: ("checkpoint.pt",),
    ConversionRepresentation.UPGRADED_V2: (
        "model.pt",
        "optimizer.pt",
        "rng.pt",
        "scheduler.pt",
        "state.json",
    ),
}

_FORMAT_VERSIONS = {
    ConversionRepresentation.FULL_MODEL: "full-model-v1",
    ConversionRepresentation.PEFT: "peft-v1",
    ConversionRepresentation.MERGED_MODEL: "merged-model-v1",
    ConversionRepresentation.SHARDED: "sharded-v1",
    ConversionRepresentation.CONSOLIDATED: "consolidated-v1",
    ConversionRepresentation.LEGACY_V1: "training-checkpoint-v1",
    ConversionRepresentation.UPGRADED_V2: "training-checkpoint-v2",
}


class ConversionArtifactManifestV1(StrictConversionModel):
    schema_version: Literal["flashpilot-conversion-artifact-v1"] = (
        "flashpilot-conversion-artifact-v1"
    )
    artifact_id: Literal["source", "candidate"]
    role: Literal["source", "candidate"]
    conversion_kind: ConversionKind
    representation: ConversionRepresentation
    format_version: str = Field(pattern=r"^[a-z][a-z0-9.-]*$")
    profile: Literal["conversion", "ci"]
    global_step: int | None = Field(default=None, ge=0)
    source_artifact_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    payloads: tuple[ChecksumEntry, ...] = Field(min_length=1)

    @field_validator("payloads")
    @classmethod
    def canonicalize_payloads(
        cls, payloads: tuple[ChecksumEntry, ...]
    ) -> tuple[ChecksumEntry, ...]:
        return tuple(sorted(payloads, key=lambda payload: payload.path))

    @model_validator(mode="after")
    def validate_fixed_contract(self) -> Self:
        source_representation, candidate_representation = _REPRESENTATIONS[self.conversion_kind]
        expected_representation = (
            source_representation if self.role == "source" else candidate_representation
        )
        if self.artifact_id != self.role or self.representation is not expected_representation:
            raise ValueError("conversion artifact role and representation do not match")
        if self.format_version != _FORMAT_VERSIONS[self.representation]:
            raise ValueError("conversion artifact format version is unsupported")
        paths = tuple(payload.path for payload in self.payloads)
        if paths != _PAYLOADS[self.representation]:
            raise ValueError("conversion artifact payload set is not the fixed format")
        if self.role == "source" and self.source_artifact_sha256 is not None:
            raise ValueError("source artifact cannot claim source provenance")
        if self.role == "candidate" and self.source_artifact_sha256 is None:
            raise ValueError("candidate artifact must bind its source SHA-256")
        version_case = self.conversion_kind is ConversionKind.VERSION_UPGRADE_RESUME
        if version_case and (self.profile != "ci" or self.global_step is None):
            raise ValueError("version-upgrade artifacts require CI profile and global step")
        if not version_case and (self.profile != "conversion" or self.global_step is not None):
            raise ValueError("model-representation artifacts cannot claim training progress")
        return self


class ConversionCompletionV1(StrictConversionModel):
    schema_version: Literal["flashpilot-conversion-completion-v1"] = (
        "flashpilot-conversion-completion-v1"
    )
    artifact_id: Literal["source", "candidate"]
    manifest_sha256: str = Field(pattern=SHA256_PATTERN)


class UpgradedTrainingStateV2(StrictConversionModel):
    schema_version: Literal["flashpilot-training-checkpoint-v2"] = (
        "flashpilot-training-checkpoint-v2"
    )
    source_schema_version: Literal["flashpilot-training-checkpoint-v1"] = (
        "flashpilot-training-checkpoint-v1"
    )
    profile: Literal["ci"] = "ci"
    global_step: int = Field(gt=0)
    loss_history: tuple[float, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_progress(self) -> Self:
        if len(self.loss_history) != self.global_step:
            raise ValueError("upgraded loss history must contain one entry per completed step")
        return self


class ConversionComparisonPolicy(StrictConversionModel):
    mode: Literal["exact", "tolerance-bounded", "exact-training-resume"]
    atol: float = Field(ge=0.0)
    rtol: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_policy(self) -> Self:
        if self.mode in {"exact", "exact-training-resume"} and (
            self.atol != 0.0 or self.rtol != 0.0
        ):
            raise ValueError("exact conversion policies require zero tolerance")
        if self.mode == "tolerance-bounded" and self.atol == 0.0 and self.rtol == 0.0:
            raise ValueError("tolerance-bounded conversion requires an explicit tolerance")
        return self


class ConversionCheck(StrictConversionModel):
    check_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    status: Literal["pass", "fail"]
    summary: str = Field(min_length=1, max_length=500)
    expected: str = Field(min_length=1, max_length=500)
    actual: str = Field(min_length=1, max_length=500)


class VersionResumeEvidenceV1(StrictConversionModel):
    schema_version: Literal["flashpilot-version-resume-evidence-v1"] = (
        "flashpilot-version-resume-evidence-v1"
    )
    worker_pid: int = Field(gt=0)
    control_global_step: int = Field(gt=0)
    resumed_global_step: int = Field(gt=0)
    control_loss_history: tuple[float, ...] = Field(min_length=1)
    resumed_loss_history: tuple[float, ...] = Field(min_length=1)
    control_trainable_sha256: str = Field(pattern=SHA256_PATTERN)
    resumed_trainable_sha256: str = Field(pattern=SHA256_PATTERN)
    control_evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    resumed_evaluation_sha256: str = Field(pattern=SHA256_PATTERN)
    control_optimizer_sha256: str = Field(pattern=SHA256_PATTERN)
    resumed_optimizer_sha256: str = Field(pattern=SHA256_PATTERN)
    control_scheduler_sha256: str = Field(pattern=SHA256_PATTERN)
    resumed_scheduler_sha256: str = Field(pattern=SHA256_PATTERN)


class ConversionCaseResult(StrictConversionModel):
    schema_version: Literal["flashpilot-conversion-case-v1"] = "flashpilot-conversion-case-v1"
    conversion_kind: ConversionKind
    source_representation: ConversionRepresentation
    candidate_representation: ConversionRepresentation
    source_artifact_sha256: str = Field(pattern=SHA256_PATTERN)
    source_artifact_sha256_after: str = Field(pattern=SHA256_PATTERN)
    candidate_artifact_sha256: str = Field(pattern=SHA256_PATTERN)
    candidate_artifact_sha256_after: str = Field(pattern=SHA256_PATTERN)
    comparison_policy: ConversionComparisonPolicy
    checks: tuple[ConversionCheck, ...] = Field(min_length=1)
    failed_check_ids: tuple[str, ...]
    passed: bool
    maximum_absolute_difference: float = Field(ge=0.0)
    source_unmodified: bool
    candidate_unmodified: bool
    comparison_process_pid: int = Field(gt=0)
    resume_worker_pid: int | None = Field(default=None, gt=0)
    resume_in_distinct_process: bool
    recovery_verified: Literal[False] = False
    storage_savings_reported: Literal[False] = False
    sarif_path: Literal["results.sarif"] = "results.sarif"

    @model_validator(mode="after")
    def derive_result(self) -> Self:
        expected_representations = _REPRESENTATIONS[self.conversion_kind]
        if (self.source_representation, self.candidate_representation) != (
            expected_representations
        ):
            raise ValueError("conversion result representations do not match its kind")
        identifiers = [check.check_id for check in self.checks]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("conversion check IDs must be unique")
        failed = tuple(check.check_id for check in self.checks if check.status == "fail")
        if failed != self.failed_check_ids or self.passed != (not failed):
            raise ValueError("conversion verdict must derive from every check")
        if self.source_unmodified != (
            self.source_artifact_sha256 == self.source_artifact_sha256_after
        ):
            raise ValueError("source immutability must derive from artifact hashes")
        if self.candidate_unmodified != (
            self.candidate_artifact_sha256 == self.candidate_artifact_sha256_after
        ):
            raise ValueError("candidate immutability must derive from artifact hashes")
        expected_mode = {
            ConversionKind.FULL_TO_PEFT: "tolerance-bounded",
            ConversionKind.PEFT_TO_MERGED: "tolerance-bounded",
            ConversionKind.SHARDED_TO_CONSOLIDATED: "exact",
            ConversionKind.VERSION_UPGRADE_RESUME: "exact-training-resume",
        }[self.conversion_kind]
        if self.comparison_policy.mode != expected_mode:
            raise ValueError("conversion kind uses the wrong equivalence policy")
        if self.conversion_kind is ConversionKind.VERSION_UPGRADE_RESUME:
            if (
                self.resume_worker_pid is None
                or self.resume_worker_pid == self.comparison_process_pid
                or not self.resume_in_distinct_process
            ):
                raise ValueError("version-upgrade resume requires a distinct worker process")
        elif self.resume_worker_pid is not None or self.resume_in_distinct_process:
            raise ValueError("model-only conversions cannot claim a resume worker")
        return self


class ConversionQualificationResult(StrictConversionModel):
    schema_version: Literal["flashpilot-conversion-qualification-v1"] = (
        "flashpilot-conversion-qualification-v1"
    )
    qualification_profile: Literal[QualificationProfile.CHECKPOINT_CONVERSION_EQUIVALENCE] = (
        QualificationProfile.CHECKPOINT_CONVERSION_EQUIVALENCE
    )
    cases: tuple[ConversionCaseResult, ...] = Field(min_length=4, max_length=4)
    failed_cases: tuple[ConversionKind, ...]
    passed: bool
    verdict: Literal["PASS", "FAILED"]
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    junit_path: Literal["junit.xml"] = "junit.xml"
    job_summary_path: Literal["job-summary.md"] = "job-summary.md"
    sarif_path: Literal["results.sarif"] = "results.sarif"
    recovery_verified: Literal[False] = False
    attestation_emitted: Literal[False] = False
    storage_savings_reported: Literal[False] = False
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def derive_qualification(self) -> Self:
        expected_order = tuple(ConversionKind)
        actual_order = tuple(case.conversion_kind for case in self.cases)
        if actual_order != expected_order:
            raise ValueError("conversion qualification must contain all four cases in order")
        failed = tuple(case.conversion_kind for case in self.cases if not case.passed)
        if failed != self.failed_cases or self.passed != (not failed):
            raise ValueError("conversion qualification verdict must derive from every case")
        if self.verdict != ("PASS" if self.passed else "FAILED"):
            raise ValueError("conversion qualification text verdict is inconsistent")
        return self
