"""Same-filesystem atomic directory commit for checkpoint artifacts."""

from __future__ import annotations

import os
import shutil
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from flashpilot.checkpoints.integrity import logical_directory_bytes, sha256_file
from flashpilot.domain.manifests import (
    CheckpointManifest,
    ChecksumDocument,
    ChecksumEntry,
    CompletionMarker,
    validate_managed_relative_path,
)
from flashpilot.security.paths import PathSandbox

PayloadWriter = Callable[[Path], None]
ManifestFactory = Callable[[ChecksumDocument], CheckpointManifest]
CommittedCallback = Callable[[Path], None]


class AtomicCommitError(RuntimeError):
    """Raised when a checkpoint cannot be committed as one final directory."""


@dataclass(frozen=True, slots=True)
class DirectorySyncStatus:
    supported: bool
    succeeded: bool
    detail: str


@dataclass(frozen=True, slots=True)
class AtomicCommitResult:
    checkpoint_path: Path
    logical_bytes_written: int
    duration_seconds: float
    payload_files_synced: bool
    metadata_files_synced: bool
    temp_directory_sync: DirectorySyncStatus
    parent_directory_sync: DirectorySyncStatus
    atomic_rename_succeeded: bool


def _write_model_durable(path: Path, model: BaseModel) -> None:
    serialized = model.model_dump_json(indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(serialized)
        stream.flush()
        os.fsync(stream.fileno())


def _fsync_file(path: Path) -> None:
    # Windows' _commit requires a descriptor opened with write access even when
    # no bytes are changed. The payload writer has already closed the file.
    with path.open("r+b") as stream:
        os.fsync(stream.fileno())


def _fsync_directory(path: Path) -> DirectorySyncStatus:
    if os.name == "nt":
        return DirectorySyncStatus(
            supported=False,
            succeeded=False,
            detail="Directory fsync is unavailable through Python on Windows; commit is best-effort.",
        )

    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_RDONLY)
        os.fsync(descriptor)
    except OSError as error:
        return DirectorySyncStatus(
            supported=True,
            succeeded=False,
            detail=f"Directory fsync failed: {type(error).__name__}: {error}",
        )
    finally:
        if descriptor is not None:
            os.close(descriptor)
    return DirectorySyncStatus(
        supported=True,
        succeeded=True,
        detail="Directory metadata fsync completed.",
    )


def commit_checkpoint(
    *,
    run_root: Path,
    checkpoint_root_relative: str,
    checkpoint_id: str,
    payload_writers: Mapping[str, PayloadWriter],
    manifest_factory: ManifestFactory,
    on_committed: CommittedCallback | None = None,
) -> AtomicCommitResult:
    """Write, validate metadata, rename, then optionally emit a commit callback."""

    started_at = time.perf_counter()
    run_sandbox = PathSandbox.create(run_root)
    checkpoint_root = run_sandbox.resolve_relative(checkpoint_root_relative)
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    checkpoint_sandbox = PathSandbox.create(checkpoint_root)

    normalized_id = validate_managed_relative_path(checkpoint_id)
    if "/" in normalized_id:
        raise AtomicCommitError("checkpoint_id must be one directory name")
    final_path = checkpoint_sandbox.resolve_relative(normalized_id)
    if final_path.exists():
        raise FileExistsError(f"checkpoint destination already exists: {final_path}")

    temporary_name = f".{normalized_id}.tmp-{uuid.uuid4().hex}"
    temporary_path = checkpoint_sandbox.resolve_relative(temporary_name)
    temporary_path.mkdir()
    temporary_sandbox = PathSandbox.create(temporary_path)

    try:
        checksum_entries: list[ChecksumEntry] = []
        for relative_path, writer in sorted(payload_writers.items()):
            normalized_path = validate_managed_relative_path(relative_path)
            payload_path = temporary_sandbox.resolve_relative(normalized_path)
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            writer(payload_path)
            if not payload_path.is_file() or payload_path.is_symlink():
                raise AtomicCommitError(
                    f"payload writer did not create a regular file: {relative_path}"
                )
            _fsync_file(payload_path)
            checksum_entries.append(
                ChecksumEntry(
                    path=normalized_path,
                    sha256=sha256_file(payload_path),
                    size_bytes=payload_path.stat().st_size,
                )
            )

        checksums = ChecksumDocument(files=tuple(checksum_entries))
        _write_model_durable(
            temporary_sandbox.resolve_relative("checksums.json"),
            checksums,
        )
        manifest = manifest_factory(checksums)
        if manifest.checkpoint_id != normalized_id:
            raise AtomicCommitError("manifest checkpoint_id does not match destination")
        manifest_entries = {
            payload.path: (payload.sha256, payload.size_bytes) for payload in manifest.payloads
        }
        checksum_mapping = {
            entry.path: (entry.sha256, entry.size_bytes) for entry in checksums.files
        }
        if manifest_entries != checksum_mapping:
            raise AtomicCommitError("manifest payload metadata does not match checksums")
        _write_model_durable(
            temporary_sandbox.resolve_relative("manifest.json"),
            manifest,
        )
        _write_model_durable(
            temporary_sandbox.resolve_relative("COMPLETE"),
            CompletionMarker(checkpoint_id=normalized_id),
        )

        temp_directory_sync = _fsync_directory(temporary_path)
        if temp_directory_sync.supported and not temp_directory_sync.succeeded:
            raise AtomicCommitError(temp_directory_sync.detail)
        os.rename(temporary_path, final_path)
        parent_directory_sync = _fsync_directory(checkpoint_root)
        if parent_directory_sync.supported and not parent_directory_sync.succeeded:
            raise AtomicCommitError(parent_directory_sync.detail)
        result = AtomicCommitResult(
            checkpoint_path=final_path,
            logical_bytes_written=logical_directory_bytes(final_path),
            duration_seconds=time.perf_counter() - started_at,
            payload_files_synced=True,
            metadata_files_synced=True,
            temp_directory_sync=temp_directory_sync,
            parent_directory_sync=parent_directory_sync,
            atomic_rename_succeeded=True,
        )
        if on_committed is not None:
            on_committed(final_path)
        return result
    except Exception:
        if temporary_path.exists():
            shutil.rmtree(temporary_path, ignore_errors=True)
        raise
