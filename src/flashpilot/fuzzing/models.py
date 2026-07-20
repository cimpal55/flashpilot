"""Strict evidence models for deterministic partial-write fuzzing."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.domain.manifests import SHA256_PATTERN, ManagedRelativePath


class FuzzScenario(StrEnum):
    TRUNCATED_PAYLOAD = "truncated-payload"
    MISSING_SHARD = "missing-shard"
    STALE_MANIFEST = "stale-manifest"
    CHECKSUM_MISMATCH = "checksum-mismatch"
    DUPLICATE_RANK = "duplicate-rank"
    REORDERED_WRITES = "reordered-writes"


class FuzzRejectionReason(StrEnum):
    MISSING_COMPLETION = "missing-completion"
    MISSING_METADATA = "missing-metadata"
    MANIFEST_INVALID = "manifest-invalid"
    COMPLETION_MISMATCH = "completion-mismatch"
    CHECKSUM_MANIFEST_MISMATCH = "checksum-manifest-mismatch"
    INVENTORY_MISMATCH = "inventory-mismatch"
    PAYLOAD_MISSING = "payload-missing"
    PAYLOAD_SIZE_MISMATCH = "payload-size-mismatch"
    PAYLOAD_CHECKSUM_MISMATCH = "payload-checksum-mismatch"
    PAYLOAD_INVALID = "payload-invalid"
    UNSAFE_PATH = "unsafe-path"


class StrictFuzzModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FuzzShardV1(StrictFuzzModel):
    rank: int = Field(ge=0)
    path: ManagedRelativePath
    sha256: str = Field(pattern=SHA256_PATTERN)
    size_bytes: int = Field(gt=0)


class FuzzCheckpointManifestV1(StrictFuzzModel):
    schema_version: Literal["flashpilot-fuzz-checkpoint-v1"] = "flashpilot-fuzz-checkpoint-v1"
    checkpoint_id: str = Field(pattern=r"^checkpoint-[0-9]{4}$")
    iteration: int = Field(gt=0, le=1000)
    global_step: int = Field(gt=0)
    world_size: Literal[2] = 2
    shards: tuple[FuzzShardV1, ...] = Field(min_length=2, max_length=2)

    @field_validator("shards")
    @classmethod
    def canonicalize_shards(cls, shards: tuple[FuzzShardV1, ...]) -> tuple[FuzzShardV1, ...]:
        return tuple(sorted(shards, key=lambda shard: (shard.rank, shard.path)))

    @model_validator(mode="after")
    def validate_fixed_shards(self) -> Self:
        if self.checkpoint_id != f"checkpoint-{self.iteration:04d}":
            raise ValueError("fuzz checkpoint ID must derive from its iteration")
        if tuple(shard.rank for shard in self.shards) != (0, 1):
            raise ValueError("fuzz checkpoint requires exactly one shard for ranks 0 and 1")
        if tuple(shard.path for shard in self.shards) != ("rank-000.pt", "rank-001.pt"):
            raise ValueError("fuzz checkpoint shard paths must derive from rank")
        return self


class FuzzCompletionV1(StrictFuzzModel):
    schema_version: Literal["flashpilot-fuzz-completion-v1"] = "flashpilot-fuzz-completion-v1"
    checkpoint_id: str = Field(pattern=r"^checkpoint-[0-9]{4}$")
    manifest_sha256: str = Field(pattern=SHA256_PATTERN)


class FuzzCaseResult(StrictFuzzModel):
    schema_version: Literal["flashpilot-fuzz-case-v1"] = "flashpilot-fuzz-case-v1"
    iteration: int = Field(gt=0, le=1000)
    scenario: FuzzScenario
    artifact_path: ManagedRelativePath
    expected_rejection_reason: FuzzRejectionReason | None
    observed_rejection_reasons: tuple[FuzzRejectionReason, ...]
    validation_attempts: int = Field(gt=0)
    premature_acceptances: int = Field(ge=0)
    final_valid: bool
    source_sha256_before: str = Field(pattern=SHA256_PATTERN)
    source_sha256_after: str = Field(pattern=SHA256_PATTERN)
    source_unmodified: bool
    candidate_sha256_before_validation: str = Field(pattern=SHA256_PATTERN)
    candidate_sha256_after_validation: str = Field(pattern=SHA256_PATTERN)
    candidate_unmodified_by_validation: bool
    passed: bool

    @model_validator(mode="after")
    def derive_case_verdict(self) -> Self:
        if self.source_unmodified != (self.source_sha256_before == self.source_sha256_after):
            raise ValueError("source immutability must derive from source hashes")
        if self.candidate_unmodified_by_validation != (
            self.candidate_sha256_before_validation == self.candidate_sha256_after_validation
        ):
            raise ValueError("candidate immutability must derive from candidate hashes")
        if self.scenario is FuzzScenario.REORDERED_WRITES:
            expected = (
                self.expected_rejection_reason is None
                and self.validation_attempts == len(self.observed_rejection_reasons) + 1
                and self.validation_attempts > 1
                and self.premature_acceptances == 0
                and self.final_valid
                and self.source_unmodified
                and self.candidate_unmodified_by_validation
            )
        else:
            expected = (
                self.expected_rejection_reason is not None
                and self.observed_rejection_reasons == (self.expected_rejection_reason,)
                and self.validation_attempts == 1
                and self.premature_acceptances == 0
                and not self.final_valid
                and self.source_unmodified
                and self.candidate_unmodified_by_validation
            )
        if self.passed != expected:
            raise ValueError("fuzz case verdict must derive from validation evidence")
        return self


class PartialWriteFuzzResult(StrictFuzzModel):
    schema_version: Literal["flashpilot-partial-write-fuzz-v1"] = "flashpilot-partial-write-fuzz-v1"
    scenario: Literal["partial-write"] = "partial-write"
    seed: Literal[20260720] = 20260720
    iterations: int = Field(gt=0, le=1000)
    cases: tuple[FuzzCaseResult, ...] = Field(min_length=6)
    total_cases: int = Field(gt=0)
    passed_cases: int = Field(ge=0)
    failed_cases: int = Field(ge=0)
    premature_acceptances: int = Field(ge=0)
    schedule_sha256: str = Field(pattern=SHA256_PATTERN)
    passed: bool
    verdict: Literal["PASS", "FAILED"]
    result_path: Literal["result.json"] = "result.json"
    report_path: Literal["report.md"] = "report.md"
    junit_path: Literal["junit.xml"] = "junit.xml"
    job_summary_path: Literal["job-summary.md"] = "job-summary.md"
    recovery_verified: Literal[False] = False
    attestation_emitted: Literal[False] = False
    storage_savings_reported: Literal[False] = False
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def derive_qualification_verdict(self) -> Self:
        expected_order = tuple(FuzzScenario)
        if len(self.cases) != self.iterations * len(expected_order):
            raise ValueError("fuzz result must contain the complete iteration matrix")
        for index in range(self.iterations):
            group = self.cases[index * len(expected_order) : (index + 1) * len(expected_order)]
            if tuple(case.scenario for case in group) != expected_order:
                raise ValueError("fuzz scenarios must use the fixed order")
            if any(case.iteration != index + 1 for case in group):
                raise ValueError("fuzz case iteration does not match its matrix position")
        passed_cases = sum(case.passed for case in self.cases)
        failed_cases = len(self.cases) - passed_cases
        premature = sum(case.premature_acceptances for case in self.cases)
        if (
            self.total_cases != len(self.cases)
            or self.passed_cases != passed_cases
            or self.failed_cases != failed_cases
            or self.premature_acceptances != premature
        ):
            raise ValueError("fuzz aggregate counts must derive from case evidence")
        expected_pass = failed_cases == 0 and premature == 0
        if self.passed != expected_pass or self.verdict != ("PASS" if expected_pass else "FAILED"):
            raise ValueError("fuzz verdict must derive from all cases")
        return self
