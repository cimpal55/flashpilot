"""Strict schemas for the optional local attestation history."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from flashpilot.contracts.models import QualificationProfile
from flashpilot.domain.manifests import SHA256_PATTERN

REGISTRY_METADATA_PATH = "registry.json"
REGISTRY_ENTRIES_PATH = "entries"
REGISTRY_HEAD_PATH = "HEAD"
REGISTRY_ENTRY_PATH = "entry.json"
REGISTRY_COMPLETION_PATH = "COMPLETE"
REGISTRY_ATTESTATION_PATH = "recovery.attestation.json"
REGISTRY_SIGNATURE_PATH = "recovery.attestation.signature.json"
REGISTRY_PUBLIC_KEY_PATH = "ed25519-public.pem"
REGISTRY_ARTIFACT_PATHS = (
    REGISTRY_ATTESTATION_PATH,
    REGISTRY_SIGNATURE_PATH,
    REGISTRY_PUBLIC_KEY_PATH,
)


class StrictRegistryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AttestationRegistryMetadataV1(StrictRegistryModel):
    schema_version: Literal["flashpilot-attestation-registry-v1"] = (
        "flashpilot-attestation-registry-v1"
    )
    storage: Literal["local-directory"] = "local-directory"
    history: Literal["append-only-hash-chain"] = "append-only-hash-chain"
    admission: Literal["verified-signed-recovery-attestation"] = (
        "verified-signed-recovery-attestation"
    )


class AttestationRegistryArtifactV1(StrictRegistryModel):
    path: Literal[
        "recovery.attestation.json",
        "recovery.attestation.signature.json",
        "ed25519-public.pem",
    ]
    size_bytes: int = Field(gt=0)
    sha256: str = Field(pattern=SHA256_PATTERN)


class AttestationRegistryEntryV1(StrictRegistryModel):
    schema_version: Literal["flashpilot-attestation-registry-entry-v1"] = (
        "flashpilot-attestation-registry-entry-v1"
    )
    sequence: int = Field(ge=1)
    previous_entry_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    attestation_sha256: str = Field(pattern=SHA256_PATTERN)
    signature_artifact_sha256: str = Field(pattern=SHA256_PATTERN)
    signing_key_sha256: str = Field(pattern=SHA256_PATTERN)
    qualification_profile: Literal[
        QualificationProfile.EXACT_TRAINING_RESUME,
        QualificationProfile.PREEMPTION_SAFE_TRAINING,
    ]
    framework: Literal[
        "native-pytorch", "transformers", "lightning", "pytorch-distributed", "deepspeed"
    ]
    adapter: Literal[
        "native-pytorch",
        "huggingface-trainer",
        "pytorch-lightning",
        "pytorch-fsdp",
        "deepspeed-engine",
    ]
    fault_scenario: Literal[
        "process_termination",
        "process-kill",
        "managed_preemption",
        "checkpoint_restart",
        "rank_process_termination",
    ]
    run_id: str = Field(min_length=1, max_length=500)
    issued_at: datetime
    verification_check_ids: tuple[str, ...] = Field(min_length=1)
    artifacts: tuple[AttestationRegistryArtifactV1, ...] = Field(min_length=3, max_length=3)

    @field_validator("verification_check_ids")
    @classmethod
    def validate_check_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if len(values) != len(set(values)):
            raise ValueError("registry verification check IDs must be unique")
        if any(
            not value
            or value != value.strip()
            or len(value) > 200
            or not value[0].islower()
            or any(
                character not in "abcdefghijklmnopqrstuvwxyz0123456789_.-" for character in value
            )
            for value in values
        ):
            raise ValueError("registry verification check IDs must be canonical identifiers")
        if "signature.ed25519" not in values:
            raise ValueError("registry admission requires detached Ed25519 verification")
        return values

    @field_validator("artifacts")
    @classmethod
    def canonicalize_artifacts(
        cls,
        artifacts: tuple[AttestationRegistryArtifactV1, ...],
    ) -> tuple[AttestationRegistryArtifactV1, ...]:
        ordered = tuple(sorted(artifacts, key=lambda artifact: artifact.path))
        if tuple(artifact.path for artifact in ordered) != tuple(sorted(REGISTRY_ARTIFACT_PATHS)):
            raise ValueError("registry entry must contain the exact fixed artifact inventory")
        return ordered

    @model_validator(mode="after")
    def validate_chain_position(self) -> Self:
        if (self.sequence == 1) != (self.previous_entry_sha256 is None):
            raise ValueError("only the first registry entry may omit its predecessor hash")
        if self.issued_at.tzinfo is None:
            raise ValueError("registered attestation issued_at must include a timezone")
        artifact_hashes = {artifact.path: artifact.sha256 for artifact in self.artifacts}
        if artifact_hashes[REGISTRY_ATTESTATION_PATH] != self.attestation_sha256:
            raise ValueError("registry attestation artifact hash must match the entry identity")
        if artifact_hashes[REGISTRY_SIGNATURE_PATH] != self.signature_artifact_sha256:
            raise ValueError("registry signature artifact hash must match the entry identity")
        return self


class AttestationRegistryCompletionV1(StrictRegistryModel):
    schema_version: Literal["flashpilot-attestation-registry-completion-v1"] = (
        "flashpilot-attestation-registry-completion-v1"
    )
    sequence: int = Field(ge=1)
    entry_sha256: str = Field(pattern=SHA256_PATTERN)


class AttestationRegistryHeadV1(StrictRegistryModel):
    schema_version: Literal["flashpilot-attestation-registry-head-v1"] = (
        "flashpilot-attestation-registry-head-v1"
    )
    entry_count: int = Field(ge=0, le=10_000)
    head_entry_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)

    @model_validator(mode="after")
    def validate_head(self) -> Self:
        if (self.entry_count == 0) != (self.head_entry_sha256 is None):
            raise ValueError("only an empty registry may omit its head entry SHA-256")
        return self


class AttestationRegistryHistoryV1(StrictRegistryModel):
    schema_version: Literal["flashpilot-attestation-registry-history-v1"] = (
        "flashpilot-attestation-registry-history-v1"
    )
    valid: Literal[True] = True
    entry_count: int = Field(ge=0)
    head_entry_sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    entries: tuple[AttestationRegistryEntryV1, ...]

    @model_validator(mode="after")
    def validate_history_summary(self) -> Self:
        if self.entry_count != len(self.entries):
            raise ValueError("registry history count must match its entries")
        if not self.entries and self.head_entry_sha256 is not None:
            raise ValueError("empty registry history cannot have a head")
        if self.entries and self.head_entry_sha256 is None:
            raise ValueError("nonempty registry history requires a head")
        if tuple(entry.sequence for entry in self.entries) != tuple(range(1, self.entry_count + 1)):
            raise ValueError("registry history entries must be contiguous and ordered")
        return self
