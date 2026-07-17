"""Fail-closed checkpoint validation and latest-valid discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from flashpilot.checkpoints.integrity import logical_directory_bytes, sha256_file
from flashpilot.domain.manifests import (
    CheckpointManifest,
    ChecksumDocument,
    CompletionMarker,
)
from flashpilot.security.paths import PathContainmentError, PathSandbox


class CheckpointValidationError(RuntimeError):
    """Raised when a checkpoint is incomplete, malformed, corrupt, or unsafe."""


@dataclass(frozen=True, slots=True)
class ValidatedCheckpoint:
    path: Path
    manifest: CheckpointManifest
    checksums: ChecksumDocument
    logical_bytes: int


def _read_validated_json(path: Path, model_type: type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise CheckpointValidationError(f"invalid metadata file: {path.name}") from error


def _is_temporary_checkpoint(path: Path) -> bool:
    return path.name.startswith(".") and ".tmp-" in path.name


def validate_checkpoint(*, run_root: Path, checkpoint_path: Path) -> ValidatedCheckpoint:
    try:
        run_sandbox = PathSandbox.create(run_root)
        resolved_checkpoint = run_sandbox.require_contained(checkpoint_path, must_exist=True)
    except PathContainmentError as error:
        raise CheckpointValidationError("checkpoint path failed containment") from error
    if not resolved_checkpoint.is_dir() or _is_temporary_checkpoint(resolved_checkpoint):
        raise CheckpointValidationError("checkpoint must be a final directory")

    checkpoint_sandbox = PathSandbox.create(resolved_checkpoint)
    try:
        complete_path = checkpoint_sandbox.resolve_relative("COMPLETE", must_exist=True)
        manifest_path = checkpoint_sandbox.resolve_relative("manifest.json", must_exist=True)
        checksums_path = checkpoint_sandbox.resolve_relative("checksums.json", must_exist=True)
    except PathContainmentError as error:
        raise CheckpointValidationError("checkpoint metadata is missing or unsafe") from error

    marker = _read_validated_json(complete_path, CompletionMarker)
    manifest = _read_validated_json(manifest_path, CheckpointManifest)
    checksums = _read_validated_json(checksums_path, ChecksumDocument)
    if marker.checkpoint_id != manifest.checkpoint_id:
        raise CheckpointValidationError("completion marker does not match manifest")
    if manifest.checkpoint_id != resolved_checkpoint.name:
        raise CheckpointValidationError("manifest checkpoint_id does not match directory")

    checksum_mapping = {entry.path: entry for entry in checksums.files}
    manifest_mapping = {payload.path: payload for payload in manifest.payloads}
    if checksum_mapping.keys() != manifest_mapping.keys():
        raise CheckpointValidationError("manifest and checksum payload sets differ")

    for relative_path, checksum in checksum_mapping.items():
        try:
            payload_path = checkpoint_sandbox.resolve_relative(relative_path, must_exist=True)
        except PathContainmentError as error:
            raise CheckpointValidationError(
                f"payload path is missing or unsafe: {relative_path}"
            ) from error
        if not payload_path.is_file():
            raise CheckpointValidationError(f"payload is not a regular file: {relative_path}")
        actual_size = payload_path.stat().st_size
        actual_sha256 = sha256_file(payload_path)
        manifest_payload = manifest_mapping[relative_path]
        if actual_size != checksum.size_bytes or actual_size != manifest_payload.size_bytes:
            raise CheckpointValidationError(f"payload size mismatch: {relative_path}")
        if actual_sha256 != checksum.sha256 or actual_sha256 != manifest_payload.sha256:
            raise CheckpointValidationError(f"payload checksum mismatch: {relative_path}")

    return ValidatedCheckpoint(
        path=resolved_checkpoint,
        manifest=manifest,
        checksums=checksums,
        logical_bytes=logical_directory_bytes(resolved_checkpoint),
    )


def discover_valid_checkpoints(
    *,
    run_root: Path,
    checkpoint_root: Path,
) -> tuple[ValidatedCheckpoint, ...]:
    try:
        run_sandbox = PathSandbox.create(run_root)
        resolved_root = run_sandbox.require_contained(checkpoint_root, must_exist=True)
    except PathContainmentError as error:
        raise CheckpointValidationError("checkpoint root failed containment") from error
    if not resolved_root.is_dir():
        raise CheckpointValidationError("checkpoint root must be a directory")

    valid: list[ValidatedCheckpoint] = []
    for candidate in resolved_root.iterdir():
        if not candidate.is_dir() or _is_temporary_checkpoint(candidate):
            continue
        try:
            valid.append(validate_checkpoint(run_root=run_root, checkpoint_path=candidate))
        except CheckpointValidationError:
            continue
    return tuple(
        sorted(
            valid,
            key=lambda checkpoint: (
                checkpoint.manifest.global_step,
                checkpoint.manifest.checkpoint_id,
            ),
        )
    )


def latest_valid_checkpoint(
    *,
    run_root: Path,
    checkpoint_root: Path,
) -> ValidatedCheckpoint | None:
    valid = discover_valid_checkpoints(run_root=run_root, checkpoint_root=checkpoint_root)
    return valid[-1] if valid else None
