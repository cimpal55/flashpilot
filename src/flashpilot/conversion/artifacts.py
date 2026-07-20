"""Atomic, checksummed artifact protocol for fixed conversion fixtures."""

from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

import torch
from pydantic import ValidationError

from flashpilot.checkpoints.atomic import (
    DirectorySyncStatus,
    fsync_directory,
    fsync_file,
    write_model_durable,
)
from flashpilot.checkpoints.integrity import (
    DirectoryContentFingerprint,
    directory_content_fingerprint,
    logical_directory_bytes,
    sha256_file,
)
from flashpilot.conversion.models import (
    ConversionArtifactManifestV1,
    ConversionCompletionV1,
    ConversionKind,
    ConversionRepresentation,
)
from flashpilot.domain.manifests import (
    ChecksumDocument,
    ChecksumEntry,
    validate_managed_relative_path,
)
from flashpilot.security.paths import PathContainmentError, PathSandbox

ConversionPayloadWriter = Callable[[Path], None]
MAX_CONVERSION_PAYLOAD_BYTES = 64 * 1024 * 1024
_METADATA_FILES = frozenset({"checksums.json", "manifest.json", "COMPLETE"})


class ConversionArtifactError(RuntimeError):
    """A conversion artifact is missing, unsafe, malformed, or inconsistent."""


@dataclass(frozen=True, slots=True)
class ConversionArtifactCommit:
    path: Path
    fingerprint: DirectoryContentFingerprint
    duration_seconds: float
    payload_files_fsynced: bool
    metadata_files_fsynced: bool
    atomic_rename_succeeded: bool
    temp_directory_sync: DirectorySyncStatus
    parent_directory_sync: DirectorySyncStatus


@dataclass(frozen=True, slots=True)
class ValidatedConversionArtifact:
    path: Path
    manifest: ConversionArtifactManifestV1
    checksums: ChecksumDocument
    fingerprint: DirectoryContentFingerprint


def torch_payload_writer(value: object) -> ConversionPayloadWriter:
    def write(path: Path) -> None:
        torch.save(value, path)

    return write


def json_payload_writer(value: object) -> ConversionPayloadWriter:
    def write(path: Path) -> None:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")

    return write


def text_payload_writer(value: str) -> ConversionPayloadWriter:
    def write(path: Path) -> None:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(value)

    return write


def _require_existing_directory(path: Path) -> Path:
    lexical = path.absolute()
    if not lexical.exists() or not lexical.is_dir() or lexical.is_symlink():
        raise ConversionArtifactError("conversion artifact must be an existing directory")
    try:
        resolved = lexical.resolve(strict=True)
    except OSError as error:
        raise ConversionArtifactError("conversion artifact cannot be resolved") from error
    for candidate in resolved.rglob("*"):
        if candidate.is_symlink():
            raise ConversionArtifactError("conversion artifact cannot contain symbolic links")
    return resolved


def _read_model(path: Path, model_type: type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise ConversionArtifactError(f"invalid conversion metadata: {path.name}") from error


def validate_conversion_artifact(path: Path) -> ValidatedConversionArtifact:
    """Validate containment, closed inventory, checksums, completion, and schema."""

    root = _require_existing_directory(path)
    sandbox = PathSandbox.create(root)
    try:
        manifest_path = sandbox.resolve_relative("manifest.json", must_exist=True)
        checksums_path = sandbox.resolve_relative("checksums.json", must_exist=True)
        complete_path = sandbox.resolve_relative("COMPLETE", must_exist=True)
    except PathContainmentError as error:
        raise ConversionArtifactError("conversion metadata is missing or unsafe") from error
    manifest = _read_model(manifest_path, ConversionArtifactManifestV1)
    checksums = _read_model(checksums_path, ChecksumDocument)
    completion = _read_model(complete_path, ConversionCompletionV1)
    if completion.artifact_id != manifest.artifact_id:
        raise ConversionArtifactError("conversion completion artifact ID mismatch")
    if completion.manifest_sha256 != sha256_file(manifest_path):
        raise ConversionArtifactError("conversion completion manifest hash mismatch")
    if manifest.payloads != tuple(sorted(checksums.files, key=lambda item: item.path)):
        raise ConversionArtifactError("conversion manifest/checksum inventory mismatch")
    expected_files = _METADATA_FILES | {entry.path for entry in checksums.files}
    actual_files = {
        candidate.relative_to(root).as_posix()
        for candidate in root.rglob("*")
        if candidate.is_file()
    }
    if actual_files != expected_files:
        raise ConversionArtifactError("conversion artifact inventory is not closed")
    for entry in checksums.files:
        try:
            payload = sandbox.resolve_relative(entry.path, must_exist=True)
        except PathContainmentError as error:
            raise ConversionArtifactError("conversion payload is missing or unsafe") from error
        if not payload.is_file() or payload.stat().st_size != entry.size_bytes:
            raise ConversionArtifactError("conversion payload size mismatch")
        if sha256_file(payload) != entry.sha256:
            raise ConversionArtifactError("conversion payload SHA-256 mismatch")
    try:
        fingerprint = directory_content_fingerprint(root)
    except (OSError, ValueError) as error:
        raise ConversionArtifactError("conversion artifact fingerprint failed") from error
    return ValidatedConversionArtifact(
        path=root,
        manifest=manifest,
        checksums=checksums,
        fingerprint=fingerprint,
    )


def commit_conversion_artifact(
    *,
    run_root: Path,
    parent_relative: str,
    role: str,
    conversion_kind: ConversionKind,
    representation: ConversionRepresentation,
    format_version: str,
    profile: str,
    global_step: int | None,
    source_artifact_sha256: str | None,
    payload_writers: Mapping[str, ConversionPayloadWriter],
) -> ConversionArtifactCommit:
    """Commit one immutable conversion artifact through same-filesystem rename."""

    started_at = time.perf_counter()
    sandbox = PathSandbox.create(run_root)
    parent = sandbox.resolve_relative(parent_relative)
    parent.mkdir(parents=True, exist_ok=True)
    parent_sandbox = PathSandbox.create(parent)
    artifact_id = validate_managed_relative_path(role)
    if artifact_id not in {"source", "candidate"}:
        raise ConversionArtifactError("conversion artifact role is unsupported")
    final_path = parent_sandbox.resolve_relative(artifact_id)
    if final_path.exists():
        raise FileExistsError(f"conversion artifact already exists: {final_path}")
    temporary = parent_sandbox.resolve_relative(f".{artifact_id}.tmp-{uuid.uuid4().hex}")
    temporary.mkdir()
    temporary_sandbox = PathSandbox.create(temporary)
    try:
        entries = []
        for relative, writer in sorted(payload_writers.items()):
            normalized = validate_managed_relative_path(relative)
            payload = temporary_sandbox.resolve_relative(normalized)
            payload.parent.mkdir(parents=True, exist_ok=True)
            writer(payload)
            if not payload.is_file() or payload.is_symlink():
                raise ConversionArtifactError("conversion writer did not create a regular file")
            if payload.stat().st_size > MAX_CONVERSION_PAYLOAD_BYTES:
                raise ConversionArtifactError("conversion payload exceeds the size limit")
            fsync_file(payload)
            entries.append(
                ChecksumEntry(
                    path=normalized,
                    sha256=sha256_file(payload),
                    size_bytes=payload.stat().st_size,
                )
            )
        checksums = ChecksumDocument(files=tuple(entries))
        write_model_durable(temporary / "checksums.json", checksums)
        manifest = ConversionArtifactManifestV1(
            artifact_id=artifact_id,
            role=role,
            conversion_kind=conversion_kind,
            representation=representation,
            format_version=format_version,
            profile=profile,
            global_step=global_step,
            source_artifact_sha256=source_artifact_sha256,
            payloads=checksums.files,
        )
        write_model_durable(temporary / "manifest.json", manifest)
        write_model_durable(
            temporary / "COMPLETE",
            ConversionCompletionV1(
                artifact_id=artifact_id,
                manifest_sha256=sha256_file(temporary / "manifest.json"),
            ),
        )
        temp_sync = fsync_directory(temporary)
        if temp_sync.supported and not temp_sync.succeeded:
            raise ConversionArtifactError(temp_sync.detail)
        os.rename(temporary, final_path)
        parent_sync = fsync_directory(parent)
        if parent_sync.supported and not parent_sync.succeeded:
            raise ConversionArtifactError(parent_sync.detail)
        validated = validate_conversion_artifact(final_path)
        return ConversionArtifactCommit(
            path=validated.path,
            fingerprint=validated.fingerprint,
            duration_seconds=time.perf_counter() - started_at,
            payload_files_fsynced=True,
            metadata_files_fsynced=True,
            atomic_rename_succeeded=True,
            temp_directory_sync=temp_sync,
            parent_directory_sync=parent_sync,
        )
    except Exception:
        if temporary.exists() and temporary.is_relative_to(parent):
            shutil.rmtree(temporary, ignore_errors=True)
        raise


def safe_load_torch_payload(artifact: ValidatedConversionArtifact, relative: str) -> object:
    """Load an explicitly checksummed bounded tensor payload with the safe unpickler."""

    try:
        payload = PathSandbox.create(artifact.path).resolve_relative(relative, must_exist=True)
    except PathContainmentError as error:
        raise ConversionArtifactError("conversion tensor payload is missing or unsafe") from error
    if payload.stat().st_size > MAX_CONVERSION_PAYLOAD_BYTES:
        raise ConversionArtifactError("conversion tensor payload exceeds the size limit")
    try:
        return torch.load(payload, map_location="cpu", weights_only=True)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise ConversionArtifactError("conversion tensor payload is not safely loadable") from error


def artifact_logical_bytes(path: Path) -> int:
    """Return artifact bytes for integrity diagnostics, never as a savings claim."""

    return logical_directory_bytes(_require_existing_directory(path))
