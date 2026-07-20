"""Typed state requirements for recovery qualification."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RequirementClass(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    EPHEMERAL = "ephemeral"
    UNKNOWN = "unknown"


class RecoverySource(StrEnum):
    CHECKPOINT = "checkpoint"
    IMMUTABLE_REFERENCE = "immutable_reference"
    EXTERNAL_DURABLE_SOURCE = "external_durable_source"
    DETERMINISTIC_RECOMPUTE = "deterministic_recompute"
    NONE = "none"


class RecoveryExactness(StrEnum):
    EXACT = "exact"
    TOLERANCE_BOUNDED = "tolerance_bounded"
    NON_EQUIVALENT = "non_equivalent"


class QualificationProfile(StrEnum):
    EXACT_TRAINING_RESUME = "exact-training-resume"
    MODEL_ONLY_INFERENCE = "model-only-inference"
    CHECKPOINT_CONVERSION_EQUIVALENCE = "checkpoint-conversion-equivalence"
    PREEMPTION_SAFE_TRAINING = "preemption-safe-training"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PersistenceItem(StrictContractModel):
    state_id: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_.-]*$")
    requirement: RequirementClass
    recovery_source: RecoverySource
    exactness: RecoveryExactness
    identity_controls: tuple[str, ...] = Field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = Field(default_factory=tuple)
    reason: str = Field(min_length=1, max_length=1_000)

    @field_validator("identity_controls", "evidence_ids")
    @classmethod
    def canonicalize_identifiers(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not value or value != value.strip() for value in values):
            raise ValueError("contract identifiers must be nonempty and already trimmed")
        if len(values) != len(set(values)):
            raise ValueError("contract identifiers must be unique")
        return tuple(sorted(values))


class PersistenceContract(StrictContractModel):
    schema_version: Literal["flashpilot-persistence-contract-v1"] = (
        "flashpilot-persistence-contract-v1"
    )
    qualification_profile: QualificationProfile
    framework: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_.-]*$")
    adapter: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_.-]*$")
    max_rpo_steps: int = Field(ge=0)
    items: tuple[PersistenceItem, ...] = Field(min_length=1)
    assumptions: tuple[str, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("items")
    @classmethod
    def canonicalize_items(cls, items: tuple[PersistenceItem, ...]) -> tuple[PersistenceItem, ...]:
        return tuple(sorted(items, key=lambda item: item.state_id))

    @field_validator("assumptions", "warnings")
    @classmethod
    def canonicalize_text(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not value or value != value.strip() for value in values):
            raise ValueError("contract text entries must be nonempty and already trimmed")
        if len(values) != len(set(values)):
            raise ValueError("contract text entries must be unique")
        return tuple(sorted(values))

    @model_validator(mode="after")
    def reject_duplicate_state_ids(self) -> Self:
        state_ids = [item.state_id for item in self.items]
        if len(state_ids) != len(set(state_ids)):
            raise ValueError("persistence contract contains duplicate state IDs")
        return self
