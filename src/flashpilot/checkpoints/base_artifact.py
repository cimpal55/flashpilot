"""Atomic, immutable storage for the native workload's frozen base state."""

from __future__ import annotations

import os
import shutil
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import torch
from pydantic import ValidationError

from flashpilot.adapters.base import TrainerAdapter
from flashpilot.checkpoints.atomic import (
    DirectorySyncStatus,
    fsync_directory,
    fsync_file,
    write_model_durable,
)
from flashpilot.checkpoints.integrity import logical_directory_bytes, sha256_file
from flashpilot.domain.manifests import BaseArtifactMetadata, BaseArtifactReference
from flashpilot.security.paths import PathContainmentError, PathSandbox
from flashpilot.workload.trainer import TrainingRuntime

BASE_DIRECTORY_RELATIVE = "artifacts/frozen-base"
BASE_PAYLOAD_RELATIVE = f"{BASE_DIRECTORY_RELATIVE}/base.pt"


class BaseArtifactValidationError(RuntimeError):
    """Raised when the frozen base is missing, corrupt, or unsafe."""


@dataclass(frozen=True, slots=True)
class BaseArtifactResult:
    reference: BaseArtifactReference
    artifact_path: Path
    logical_bytes: int
    duration_seconds: float
    created: bool
    payload_file_synced: bool
    metadata_file_synced: bool
    temp_directory_sync: DirectorySyncStatus | None
    parent_directory_sync: DirectorySyncStatus | None


def _read_metadata(path: Path) -> BaseArtifactMetadata:
    try:
        return BaseArtifactMetadata.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise BaseArtifactValidationError("frozen base metadata is invalid") from error


def validate_base_artifact(
    *, run_root: Path, reference: BaseArtifactReference
) -> BaseArtifactResult:
    """Validate the fixed artifact location, metadata, size, and SHA-256."""

    started_at = time.perf_counter()
    if reference.path != BASE_PAYLOAD_RELATIVE:
        raise BaseArtifactValidationError("frozen base path is not the managed P0 location")
    try:
        sandbox = PathSandbox.create(run_root)
        artifact_path = sandbox.resolve_relative(BASE_DIRECTORY_RELATIVE, must_exist=True)
        payload_path = sandbox.resolve_relative(reference.path, must_exist=True)
        metadata_path = sandbox.resolve_relative(
            f"{BASE_DIRECTORY_RELATIVE}/base.json", must_exist=True
        )
        complete_path = sandbox.resolve_relative(
            f"{BASE_DIRECTORY_RELATIVE}/COMPLETE", must_exist=True
        )
    except PathContainmentError as error:
        raise BaseArtifactValidationError("frozen base is missing or unsafe") from error
    if not artifact_path.is_dir() or not payload_path.is_file():
        raise BaseArtifactValidationError("frozen base payload is not a regular file")
    metadata = _read_metadata(metadata_path)
    if metadata.artifact != reference:
        raise BaseArtifactValidationError("frozen base metadata does not match its reference")
    try:
        completion_identity = complete_path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        raise BaseArtifactValidationError("frozen base completion marker is invalid") from error
    if completion_identity != reference.identity:
        raise BaseArtifactValidationError("frozen base completion marker does not match")
    if payload_path.stat().st_size != reference.size_bytes:
        raise BaseArtifactValidationError("frozen base size does not match its reference")
    if sha256_file(payload_path) != reference.sha256:
        raise BaseArtifactValidationError("frozen base SHA-256 does not match its reference")
    return BaseArtifactResult(
        reference=reference,
        artifact_path=artifact_path,
        logical_bytes=logical_directory_bytes(artifact_path),
        duration_seconds=time.perf_counter() - started_at,
        created=False,
        payload_file_synced=True,
        metadata_file_synced=True,
        temp_directory_sync=None,
        parent_directory_sync=None,
    )


def ensure_base_artifact(
    runtime: TrainingRuntime,
    *,
    run_root: Path,
    trainer_adapter: TrainerAdapter,
) -> BaseArtifactResult:
    """Create the frozen base once, or validate and reuse the immutable artifact."""

    started_at = time.perf_counter()
    sandbox = PathSandbox.create(run_root)
    artifact_parent = sandbox.resolve_relative("artifacts")
    artifact_parent.mkdir(parents=True, exist_ok=True)
    artifact_sandbox = PathSandbox.create(artifact_parent)
    final_path = artifact_sandbox.resolve_relative("frozen-base")
    if final_path.exists():
        metadata = _read_metadata(final_path / "base.json")
        if metadata.profile != runtime.profile.name:
            raise BaseArtifactValidationError("frozen base profile does not match this run")
        validated = validate_base_artifact(run_root=run_root, reference=metadata.artifact)
        existing_state = load_frozen_base_state(
            run_root=run_root,
            reference=metadata.artifact,
        )
        current_state = trainer_adapter.frozen_base_state(runtime.model)
        if not isinstance(existing_state, Mapping) or set(existing_state) != set(current_state):
            raise BaseArtifactValidationError("frozen base differs from the immutable run artifact")
        if any(
            not isinstance(existing_state[name], torch.Tensor)
            or not torch.equal(existing_state[name], expected)
            for name, expected in current_state.items()
        ):
            raise BaseArtifactValidationError("frozen base differs from the immutable run artifact")
        return validated

    temporary_path = artifact_sandbox.resolve_relative(f".frozen-base.tmp-{uuid.uuid4().hex}")
    temporary_path.mkdir()
    try:
        payload_path = temporary_path / "base.pt"
        torch.save(trainer_adapter.frozen_base_state(runtime.model), payload_path)
        fsync_file(payload_path)
        payload_sha256 = sha256_file(payload_path)
        reference = BaseArtifactReference(
            identity=f"native-pytorch:{runtime.profile.name}:{payload_sha256}",
            path=BASE_PAYLOAD_RELATIVE,
            sha256=payload_sha256,
            size_bytes=payload_path.stat().st_size,
        )
        write_model_durable(
            temporary_path / "base.json",
            BaseArtifactMetadata(profile=runtime.profile.name, artifact=reference),
        )
        with (temporary_path / "COMPLETE").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(reference.identity + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temp_directory_sync = fsync_directory(temporary_path)
        if temp_directory_sync.supported and not temp_directory_sync.succeeded:
            raise BaseArtifactValidationError(temp_directory_sync.detail)
        os.rename(temporary_path, final_path)
        parent_directory_sync = fsync_directory(artifact_parent)
        if parent_directory_sync.supported and not parent_directory_sync.succeeded:
            raise BaseArtifactValidationError(parent_directory_sync.detail)
        validated = validate_base_artifact(run_root=run_root, reference=reference)
        return BaseArtifactResult(
            reference=reference,
            artifact_path=validated.artifact_path,
            logical_bytes=validated.logical_bytes,
            duration_seconds=time.perf_counter() - started_at,
            created=True,
            payload_file_synced=True,
            metadata_file_synced=True,
            temp_directory_sync=temp_directory_sync,
            parent_directory_sync=parent_directory_sync,
        )
    except Exception:
        if temporary_path.exists():
            shutil.rmtree(temporary_path, ignore_errors=True)
        raise


def load_frozen_base_state(*, run_root: Path, reference: BaseArtifactReference) -> object:
    """Validate the base before deserializing its tensor-only state."""

    validated = validate_base_artifact(run_root=run_root, reference=reference)
    payload_path = validated.artifact_path / "base.pt"
    try:
        return torch.load(payload_path, map_location="cpu", weights_only=True)
    except Exception as error:
        raise BaseArtifactValidationError("frozen base payload could not be loaded") from error
