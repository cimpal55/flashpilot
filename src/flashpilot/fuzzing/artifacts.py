"""Fixed two-rank artifact protocol used by partial-write fuzz qualification."""

from __future__ import annotations

import io
import os
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

import torch
from pydantic import BaseModel, ValidationError

from flashpilot.checkpoints.atomic import DirectorySyncStatus, fsync_directory
from flashpilot.checkpoints.integrity import (
    DirectoryContentFingerprint,
    directory_content_fingerprint,
    sha256_file,
)
from flashpilot.domain.manifests import ChecksumDocument, ChecksumEntry
from flashpilot.fuzzing.models import (
    FuzzCheckpointManifestV1,
    FuzzCompletionV1,
    FuzzRejectionReason,
    FuzzShardV1,
)
from flashpilot.security.paths import PathContainmentError, PathSandbox

MAX_FUZZ_PAYLOAD_BYTES = 1024 * 1024
FUZZ_PAYLOAD_PATHS = ("rank-000.pt", "rank-001.pt")
FUZZ_METADATA_PATHS = frozenset({"COMPLETE", "checksums.json", "manifest.json"})


class FuzzArtifactError(RuntimeError):
    """A fuzz artifact was rejected for one stable typed reason."""

    def __init__(self, reason: FuzzRejectionReason, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class ValidatedFuzzArtifact:
    path: Path
    manifest: FuzzCheckpointManifestV1
    checksums: ChecksumDocument
    fingerprint: DirectoryContentFingerprint


@dataclass(frozen=True, slots=True)
class FuzzArtifactCommit:
    path: Path
    fingerprint: DirectoryContentFingerprint
    atomic_rename_succeeded: bool
    payload_files_fsynced: bool
    metadata_files_fsynced: bool
    temp_directory_sync: DirectorySyncStatus
    parent_directory_sync: DirectorySyncStatus


def serialize_model(model: BaseModel) -> bytes:
    return (model.model_dump_json(indent=2) + "\n").encode("utf-8")


def write_bytes_durable(path: Path, value: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def build_fuzz_documents(
    *,
    iteration: int,
    payloads: dict[str, bytes],
) -> tuple[ChecksumDocument, FuzzCheckpointManifestV1, FuzzCompletionV1]:
    checkpoint_id = f"checkpoint-{iteration:04d}"
    entries = tuple(
        ChecksumEntry(
            path=path,
            sha256=_sha256_bytes(payloads[path]),
            size_bytes=len(payloads[path]),
        )
        for path in FUZZ_PAYLOAD_PATHS
    )
    checksums = ChecksumDocument(files=entries)
    manifest = FuzzCheckpointManifestV1(
        checkpoint_id=checkpoint_id,
        iteration=iteration,
        global_step=iteration,
        shards=tuple(
            FuzzShardV1(
                rank=rank,
                path=entry.path,
                sha256=entry.sha256,
                size_bytes=entry.size_bytes,
            )
            for rank, entry in enumerate(entries)
        ),
    )
    completion = FuzzCompletionV1(
        checkpoint_id=checkpoint_id,
        manifest_sha256=_sha256_bytes(serialize_model(manifest)),
    )
    return checksums, manifest, completion


def _sha256_bytes(value: bytes) -> str:
    import hashlib

    return hashlib.sha256(value).hexdigest()


def _validate_loaded_payload(value: object, relative: str) -> None:
    rank = int(relative.removeprefix("rank-").removesuffix(".pt"))
    if (
        not isinstance(value, dict)
        or set(value) != {"rank", "tensor"}
        or value["rank"] != rank
        or not isinstance(value["tensor"], torch.Tensor)
        or value["tensor"].device.type != "cpu"
    ):
        raise FuzzArtifactError(
            FuzzRejectionReason.PAYLOAD_INVALID,
            f"shard content does not match its declared rank: {relative}",
        )


def _validate_payload_bytes(value: bytes, relative: str) -> None:
    if len(value) > MAX_FUZZ_PAYLOAD_BYTES:
        raise FuzzArtifactError(
            FuzzRejectionReason.PAYLOAD_SIZE_MISMATCH,
            f"shard exceeds the size limit: {relative}",
        )
    try:
        loaded = torch.load(io.BytesIO(value), map_location="cpu", weights_only=True)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise FuzzArtifactError(
            FuzzRejectionReason.PAYLOAD_INVALID,
            f"shard is not safely loadable: {relative}",
        ) from error
    _validate_loaded_payload(loaded, relative)


def _read_model(path: Path, model_type: type[BaseModel], reason: FuzzRejectionReason):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise FuzzArtifactError(reason, f"invalid fuzz metadata: {path.name}") from error


def _resolve_artifact(path: Path) -> Path:
    lexical = path.absolute()
    if (
        not lexical.exists()
        or not lexical.is_dir()
        or lexical.is_symlink()
        or (lexical.name.startswith(".") and ".tmp-" in lexical.name)
    ):
        raise FuzzArtifactError(
            FuzzRejectionReason.UNSAFE_PATH,
            "fuzz checkpoint must be an existing non-symlink directory",
        )
    try:
        resolved = lexical.resolve(strict=True)
    except OSError as error:
        raise FuzzArtifactError(
            FuzzRejectionReason.UNSAFE_PATH,
            "fuzz checkpoint cannot be resolved",
        ) from error
    for candidate in resolved.rglob("*"):
        if candidate.is_symlink():
            raise FuzzArtifactError(
                FuzzRejectionReason.UNSAFE_PATH,
                "fuzz checkpoint cannot contain symbolic links",
            )
    return resolved


def validate_fuzz_artifact(path: Path) -> ValidatedFuzzArtifact:
    """Validate completion, typed metadata, closed inventory, and every shard hash."""

    root = _resolve_artifact(path)
    sandbox = PathSandbox.create(root)
    try:
        complete_path = sandbox.resolve_relative("COMPLETE", must_exist=True)
    except PathContainmentError as error:
        raise FuzzArtifactError(
            FuzzRejectionReason.MISSING_COMPLETION,
            "fuzz checkpoint has no completion marker",
        ) from error
    try:
        manifest_path = sandbox.resolve_relative("manifest.json", must_exist=True)
        checksums_path = sandbox.resolve_relative("checksums.json", must_exist=True)
    except PathContainmentError as error:
        raise FuzzArtifactError(
            FuzzRejectionReason.MISSING_METADATA,
            "fuzz checkpoint metadata is incomplete",
        ) from error

    completion = _read_model(
        complete_path,
        FuzzCompletionV1,
        FuzzRejectionReason.COMPLETION_MISMATCH,
    )
    manifest = _read_model(
        manifest_path,
        FuzzCheckpointManifestV1,
        FuzzRejectionReason.MANIFEST_INVALID,
    )
    checksums = _read_model(
        checksums_path,
        ChecksumDocument,
        FuzzRejectionReason.CHECKSUM_MANIFEST_MISMATCH,
    )
    if (
        completion.checkpoint_id != manifest.checkpoint_id
        or completion.manifest_sha256 != sha256_file(manifest_path)
    ):
        raise FuzzArtifactError(
            FuzzRejectionReason.COMPLETION_MISMATCH,
            "completion marker does not bind the current manifest",
        )
    checksum_by_path = {entry.path: entry for entry in checksums.files}
    manifest_by_path = {shard.path: shard for shard in manifest.shards}
    if set(checksum_by_path) != set(manifest_by_path) or any(
        checksum_by_path[path].sha256 != manifest_by_path[path].sha256
        or checksum_by_path[path].size_bytes != manifest_by_path[path].size_bytes
        for path in checksum_by_path
    ):
        raise FuzzArtifactError(
            FuzzRejectionReason.CHECKSUM_MANIFEST_MISMATCH,
            "checksum document and manifest shard metadata differ",
        )
    for relative in FUZZ_PAYLOAD_PATHS:
        try:
            payload = sandbox.resolve_relative(relative, must_exist=True)
        except PathContainmentError as error:
            raise FuzzArtifactError(
                FuzzRejectionReason.PAYLOAD_MISSING,
                f"required shard is missing: {relative}",
            ) from error
        if not payload.is_file() or payload.is_symlink():
            raise FuzzArtifactError(
                FuzzRejectionReason.UNSAFE_PATH,
                f"shard is not a regular file: {relative}",
            )
        entry = checksum_by_path[relative]
        actual_size = payload.stat().st_size
        if actual_size > MAX_FUZZ_PAYLOAD_BYTES or actual_size != entry.size_bytes:
            raise FuzzArtifactError(
                FuzzRejectionReason.PAYLOAD_SIZE_MISMATCH,
                f"shard size differs from committed metadata: {relative}",
            )
        if sha256_file(payload) != entry.sha256:
            raise FuzzArtifactError(
                FuzzRejectionReason.PAYLOAD_CHECKSUM_MISMATCH,
                f"shard checksum differs from committed metadata: {relative}",
            )
        try:
            value = torch.load(payload, map_location="cpu", weights_only=True)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise FuzzArtifactError(
                FuzzRejectionReason.PAYLOAD_INVALID,
                f"shard is not safely loadable: {relative}",
            ) from error
        _validate_loaded_payload(value, relative)
    expected_files = FUZZ_METADATA_PATHS | set(FUZZ_PAYLOAD_PATHS)
    actual_files = {
        candidate.relative_to(root).as_posix()
        for candidate in root.rglob("*")
        if candidate.is_file()
    }
    if actual_files != expected_files:
        raise FuzzArtifactError(
            FuzzRejectionReason.INVENTORY_MISMATCH,
            "fuzz checkpoint inventory is not closed",
        )
    try:
        fingerprint = directory_content_fingerprint(root)
    except (OSError, ValueError) as error:
        raise FuzzArtifactError(
            FuzzRejectionReason.UNSAFE_PATH,
            "fuzz checkpoint cannot be fingerprinted",
        ) from error
    return ValidatedFuzzArtifact(
        path=root,
        manifest=manifest,
        checksums=checksums,
        fingerprint=fingerprint,
    )


def commit_fuzz_artifact(
    *,
    run_root: Path,
    iteration: int,
    payloads: dict[str, bytes],
) -> FuzzArtifactCommit:
    """Commit a valid source using the same-filesystem temporary-directory protocol."""

    if set(payloads) != set(FUZZ_PAYLOAD_PATHS):
        raise ValueError("fuzz source requires exactly two ranked payloads")
    for relative in FUZZ_PAYLOAD_PATHS:
        _validate_payload_bytes(payloads[relative], relative)
    checksums, manifest, completion = build_fuzz_documents(
        iteration=iteration,
        payloads=payloads,
    )
    sandbox = PathSandbox.create(run_root)
    sources = sandbox.resolve_relative("sources")
    sources.mkdir(parents=True, exist_ok=True)
    source_sandbox = PathSandbox.create(sources)
    checkpoint_id = manifest.checkpoint_id
    final_path = source_sandbox.resolve_relative(checkpoint_id)
    if final_path.exists():
        raise FileExistsError(f"fuzz source already exists: {final_path}")
    temporary = source_sandbox.resolve_relative(f".{checkpoint_id}.tmp-{uuid.uuid4().hex}")
    temporary.mkdir()
    try:
        for relative in FUZZ_PAYLOAD_PATHS:
            write_bytes_durable(temporary / relative, payloads[relative])
        write_bytes_durable(temporary / "checksums.json", serialize_model(checksums))
        write_bytes_durable(temporary / "manifest.json", serialize_model(manifest))
        write_bytes_durable(temporary / "COMPLETE", serialize_model(completion))
        temp_sync = fsync_directory(temporary)
        if temp_sync.supported and not temp_sync.succeeded:
            raise FuzzArtifactError(FuzzRejectionReason.UNSAFE_PATH, temp_sync.detail)
        os.rename(temporary, final_path)
        parent_sync = fsync_directory(sources)
        if parent_sync.supported and not parent_sync.succeeded:
            raise FuzzArtifactError(FuzzRejectionReason.UNSAFE_PATH, parent_sync.detail)
        validated = validate_fuzz_artifact(final_path)
        return FuzzArtifactCommit(
            path=validated.path,
            fingerprint=validated.fingerprint,
            atomic_rename_succeeded=True,
            payload_files_fsynced=True,
            metadata_files_fsynced=True,
            temp_directory_sync=temp_sync,
            parent_directory_sync=parent_sync,
        )
    except Exception:
        if temporary.exists() and temporary.is_relative_to(sources):
            shutil.rmtree(temporary, ignore_errors=True)
        raise
