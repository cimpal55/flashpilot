"""Checkpoint manifest, checksum, completion, and state schemas."""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

SHA256_PATTERN = r"^[0-9a-f]{64}$"
CHECKPOINT_ID_PATTERN = r"^checkpoint-step-[0-9]{6}$"


def validate_managed_relative_path(value: str) -> str:
    """Validate and normalize a platform-independent managed relative path."""

    if not value or "\x00" in value:
        raise ValueError("managed path must not be empty or contain NUL")
    portable_value = value.replace("\\", "/")
    path = PurePosixPath(portable_value)
    if path.is_absolute() or portable_value.startswith("/"):
        raise ValueError("managed path must be relative")
    if not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("managed path must not contain traversal segments")
    if ":" in path.parts[0]:
        raise ValueError("managed path must not contain a drive or URI scheme")
    normalized = path.as_posix()
    if normalized != portable_value:
        raise ValueError("managed path must use normalized relative segments")
    return normalized


ManagedRelativePath = Annotated[str, AfterValidator(validate_managed_relative_path)]
PayloadRole = Literal["model", "optimizer", "scheduler", "rng", "state"]
SerializedStateName = Literal[
    "model",
    "optimizer",
    "scheduler",
    "global_step",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "config",
]

SAFE_FULL_PAYLOADS: dict[PayloadRole, str] = {
    "model": "model.pt",
    "optimizer": "optimizer.pt",
    "scheduler": "scheduler.pt",
    "rng": "rng.pt",
    "state": "state.json",
}
SAFE_FULL_SERIALIZED_STATE: tuple[SerializedStateName, ...] = (
    "model",
    "optimizer",
    "scheduler",
    "global_step",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "config",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ChecksumEntry(StrictModel):
    path: ManagedRelativePath
    sha256: str = Field(pattern=SHA256_PATTERN)
    size_bytes: int = Field(ge=0)


class ChecksumDocument(StrictModel):
    schema_version: Literal["checksums-v1"] = "checksums-v1"
    files: tuple[ChecksumEntry, ...]

    @model_validator(mode="after")
    def require_unique_paths(self) -> ChecksumDocument:
        paths = [entry.path for entry in self.files]
        if len(paths) != len(set(paths)):
            raise ValueError("checksum paths must be unique")
        if not paths:
            raise ValueError("at least one checksum entry is required")
        return self


class ManifestPayload(StrictModel):
    role: PayloadRole
    path: ManagedRelativePath
    sha256: str = Field(pattern=SHA256_PATTERN)
    size_bytes: int = Field(ge=0)


class CheckpointManifest(StrictModel):
    schema_version: Literal["checkpoint-manifest-v1"] = "checkpoint-manifest-v1"
    checkpoint_id: str = Field(pattern=CHECKPOINT_ID_PATTERN)
    strategy: Literal["safe_full"] = "safe_full"
    profile: Literal["ci", "demo"]
    global_step: int = Field(ge=0)
    created_at: datetime
    serialized_state: tuple[SerializedStateName, ...]
    payloads: tuple[ManifestPayload, ...]

    @model_validator(mode="after")
    def validate_safe_full_contract(self) -> CheckpointManifest:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        if tuple(self.serialized_state) != SAFE_FULL_SERIALIZED_STATE:
            raise ValueError("safe_full must declare the complete serialized state")
        payload_mapping = {payload.role: payload.path for payload in self.payloads}
        if len(payload_mapping) != len(self.payloads):
            raise ValueError("manifest payload roles must be unique")
        if payload_mapping != SAFE_FULL_PAYLOADS:
            raise ValueError("safe_full manifest payload set is incomplete")
        return self


class CompletionMarker(StrictModel):
    schema_version: Literal["completion-marker-v1"] = "completion-marker-v1"
    checkpoint_id: str = Field(pattern=CHECKPOINT_ID_PATTERN)


class WorkloadProfileSnapshot(StrictModel):
    name: Literal["ci", "demo"]
    global_seed: int = Field(ge=0)
    steps: int = Field(gt=0)
    batch_size: int = Field(gt=0)
    sequence_length: int = Field(gt=0)
    vocabulary_size: int = Field(ge=2)
    model_width: int = Field(gt=0)
    attention_heads: int = Field(gt=0)
    transformer_layers: int = Field(gt=0)
    adapter_width: int = Field(gt=0)
    dropout: float = Field(gt=0.0, lt=1.0)
    learning_rate: float = Field(gt=0.0)


class SafeFullState(StrictModel):
    schema_version: Literal["safe-full-state-v1"] = "safe-full-state-v1"
    checkpoint_id: str = Field(pattern=CHECKPOINT_ID_PATTERN)
    global_step: int = Field(ge=0)
    profile: WorkloadProfileSnapshot
    loss_history: tuple[float, ...]

    @model_validator(mode="after")
    def validate_progress(self) -> SafeFullState:
        if self.global_step > self.profile.steps:
            raise ValueError("global_step exceeds the profile's final step")
        if len(self.loss_history) != self.global_step:
            raise ValueError("loss history must contain one entry per completed step")
        return self
