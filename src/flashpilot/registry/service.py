"""Bounded, local, append-only storage for verified signed attestations."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import uuid
from pathlib import Path

from pydantic import BaseModel, ValidationError

from flashpilot.attestation.crypto import (
    MAX_ATTESTATION_BYTES,
    MAX_KEY_BYTES,
    AttestationSigningError,
    verify_attestation_signature,
)
from flashpilot.attestation.models import (
    MAX_ATTESTATION_SIGNATURE_BYTES,
    AttestationSignatureV1,
    RecoveryAttestationV1,
)
from flashpilot.attestation.verifier import (
    AttestationVerificationError,
    verify_recovery_attestation,
)
from flashpilot.checkpoints.atomic import fsync_directory
from flashpilot.registry.models import (
    REGISTRY_ARTIFACT_PATHS,
    REGISTRY_ATTESTATION_PATH,
    REGISTRY_COMPLETION_PATH,
    REGISTRY_ENTRIES_PATH,
    REGISTRY_ENTRY_PATH,
    REGISTRY_HEAD_PATH,
    REGISTRY_METADATA_PATH,
    REGISTRY_PUBLIC_KEY_PATH,
    REGISTRY_SIGNATURE_PATH,
    AttestationRegistryArtifactV1,
    AttestationRegistryCompletionV1,
    AttestationRegistryEntryV1,
    AttestationRegistryHeadV1,
    AttestationRegistryHistoryV1,
    AttestationRegistryMetadataV1,
)

MAX_REGISTRY_ENTRIES = 10_000
MAX_REGISTRY_METADATA_BYTES = 16 * 1024
MAX_REGISTRY_ENTRY_BYTES = 128 * 1024
MAX_REGISTRY_COMPLETION_BYTES = 16 * 1024
REGISTRY_LOCK_PATH = ".flashpilot-registry.lock"
_ENTRY_DIRECTORY_PATTERN = re.compile(r"^(?P<sequence>[0-9]{8})-(?P<sha256>[0-9a-f]{64})$")
_ENTRY_INVENTORY = {
    REGISTRY_ENTRY_PATH,
    REGISTRY_COMPLETION_PATH,
    *REGISTRY_ARTIFACT_PATHS,
}


class AttestationRegistryError(ValueError):
    """The local registry is unsafe, malformed, locked, or failed admission."""


def _serialize_model(model: BaseModel) -> bytes:
    return (model.model_dump_json(indent=2) + "\n").encode("utf-8")


def _write_bytes_durable(path: Path, value: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def _replace_bytes_durable(path: Path, value: bytes) -> None:
    temporary_path = path.parent / f".{path.name}.tmp-{uuid.uuid4().hex}"
    try:
        _write_bytes_durable(temporary_path, value)
        os.replace(temporary_path, path)
        directory_sync = fsync_directory(path.parent)
        if directory_sync.supported and not directory_sync.succeeded:
            raise OSError(directory_sync.detail)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _read_regular_bytes(path: Path, *, maximum_bytes: int, description: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise AttestationRegistryError(f"{description} must be a regular non-symlink file")
    try:
        size = path.stat().st_size
        if size <= 0 or size > maximum_bytes:
            raise AttestationRegistryError(f"{description} has an unsupported size")
        value = path.read_bytes()
    except OSError as error:
        raise AttestationRegistryError(f"{description} is unreadable") from error
    if len(value) != size:
        raise AttestationRegistryError(f"{description} changed while it was read")
    return value


def _read_model(path: Path, model_type: type[BaseModel], *, maximum_bytes: int) -> BaseModel:
    value = _read_regular_bytes(
        path,
        maximum_bytes=maximum_bytes,
        description=path.name,
    )
    try:
        return model_type.model_validate_json(value)
    except (ValidationError, ValueError) as error:
        raise AttestationRegistryError(f"{path.name} is malformed or unsupported") from error


def _require_registry_root(registry_root: Path) -> Path:
    if registry_root.is_symlink() or not registry_root.is_dir():
        raise AttestationRegistryError("registry root must be a regular non-symlink directory")
    try:
        return registry_root.resolve(strict=True)
    except OSError as error:
        raise AttestationRegistryError("registry root is missing or unreadable") from error


def _require_exact_directory_inventory(directory: Path, expected: set[str]) -> None:
    try:
        children: list[Path] = []
        for child in directory.iterdir():
            children.append(child)
            if len(children) > len(expected):
                raise AttestationRegistryError(
                    "registry directory has an unexpected or incomplete inventory"
                )
    except OSError as error:
        raise AttestationRegistryError("registry directory inventory is unreadable") from error
    if any(child.is_symlink() for child in children):
        raise AttestationRegistryError("registry inventories refuse symbolic links")
    actual = {child.name for child in children}
    if actual != expected:
        raise AttestationRegistryError(
            "registry directory has an unexpected or incomplete inventory"
        )


def initialize_attestation_registry(registry_root: Path) -> AttestationRegistryMetadataV1:
    """Create one new local registry without overwriting an existing path."""

    if registry_root.exists() or registry_root.is_symlink():
        raise AttestationRegistryError("registry root must not already exist")
    absolute = registry_root.absolute()
    if not absolute.name:
        raise AttestationRegistryError("registry root must name a new child directory")
    lexical_parent = absolute.parent
    if lexical_parent.is_symlink():
        raise AttestationRegistryError("registry parent must not be a symbolic link")
    try:
        parent = lexical_parent.resolve(strict=True)
    except OSError as error:
        raise AttestationRegistryError("registry parent is missing or unsafe") from error
    if not parent.is_dir():
        raise AttestationRegistryError("registry parent must be a directory")
    root = parent / absolute.name
    metadata = AttestationRegistryMetadataV1()
    created_root = False
    try:
        os.mkdir(root)
        created_root = True
        os.mkdir(root / REGISTRY_ENTRIES_PATH)
        _write_bytes_durable(root / REGISTRY_METADATA_PATH, _serialize_model(metadata))
        _write_bytes_durable(
            root / REGISTRY_HEAD_PATH,
            _serialize_model(AttestationRegistryHeadV1(entry_count=0)),
        )
        root_sync = fsync_directory(root)
        if root_sync.supported and not root_sync.succeeded:
            raise OSError(root_sync.detail)
        parent_sync = fsync_directory(parent)
        if parent_sync.supported and not parent_sync.succeeded:
            raise OSError(parent_sync.detail)
    except OSError as error:
        if created_root:
            shutil.rmtree(root, ignore_errors=True)
        raise AttestationRegistryError("registry could not be initialized durably") from error
    return metadata


def _verify_entry_directory(
    entry_directory: Path,
    *,
    expected_sequence: int,
    expected_previous_sha256: str | None,
    expected_directory_sha256: str | None,
) -> tuple[AttestationRegistryEntryV1, str]:
    if entry_directory.is_symlink() or not entry_directory.is_dir():
        raise AttestationRegistryError("registry entry must be a regular non-symlink directory")
    _require_exact_directory_inventory(entry_directory, _ENTRY_INVENTORY)
    entry_path = entry_directory / REGISTRY_ENTRY_PATH
    entry_bytes = _read_regular_bytes(
        entry_path,
        maximum_bytes=MAX_REGISTRY_ENTRY_BYTES,
        description="registry entry",
    )
    entry_sha256 = hashlib.sha256(entry_bytes).hexdigest()
    if expected_directory_sha256 is not None and entry_sha256 != expected_directory_sha256:
        raise AttestationRegistryError("registry entry directory does not match entry.json SHA-256")
    try:
        entry = AttestationRegistryEntryV1.model_validate_json(entry_bytes)
    except (ValidationError, ValueError) as error:
        raise AttestationRegistryError("registry entry is malformed or unsupported") from error
    if entry.sequence != expected_sequence:
        raise AttestationRegistryError("registry entry sequence is not contiguous")
    if entry.previous_entry_sha256 != expected_previous_sha256:
        raise AttestationRegistryError("registry entry predecessor hash is invalid")

    completion = _read_model(
        entry_directory / REGISTRY_COMPLETION_PATH,
        AttestationRegistryCompletionV1,
        maximum_bytes=MAX_REGISTRY_COMPLETION_BYTES,
    )
    assert isinstance(completion, AttestationRegistryCompletionV1)
    if completion.sequence != entry.sequence or completion.entry_sha256 != entry_sha256:
        raise AttestationRegistryError("registry completion marker does not close this entry")

    artifact_limits = {
        REGISTRY_ATTESTATION_PATH: MAX_ATTESTATION_BYTES,
        REGISTRY_SIGNATURE_PATH: MAX_ATTESTATION_SIGNATURE_BYTES,
        REGISTRY_PUBLIC_KEY_PATH: MAX_KEY_BYTES,
    }
    for artifact in entry.artifacts:
        path = entry_directory / artifact.path
        value = _read_regular_bytes(
            path,
            maximum_bytes=artifact_limits[artifact.path],
            description=f"registry artifact {artifact.path}",
        )
        if (
            len(value) != artifact.size_bytes
            or hashlib.sha256(value).hexdigest() != artifact.sha256
        ):
            raise AttestationRegistryError("registry artifact size or SHA-256 is invalid")

    try:
        attestation = RecoveryAttestationV1.model_validate_json(
            (entry_directory / REGISTRY_ATTESTATION_PATH).read_bytes()
        )
        signature = AttestationSignatureV1.model_validate_json(
            (entry_directory / REGISTRY_SIGNATURE_PATH).read_bytes()
        )
        key_sha256 = verify_attestation_signature(
            attestation_path=entry_directory / REGISTRY_ATTESTATION_PATH,
            signature=signature,
            public_key_path=entry_directory / REGISTRY_PUBLIC_KEY_PATH,
        )
    except (AttestationSigningError, OSError, ValidationError, ValueError) as error:
        raise AttestationRegistryError(
            "registry attestation signature is invalid or tampered"
        ) from error
    expected_summary = (
        attestation.qualification_profile,
        attestation.framework,
        attestation.adapter,
        attestation.fault_scenario,
        attestation.run_id,
        attestation.issued_at,
    )
    actual_summary = (
        entry.qualification_profile,
        entry.framework,
        entry.adapter,
        entry.fault_scenario,
        entry.run_id,
        entry.issued_at,
    )
    if actual_summary != expected_summary:
        raise AttestationRegistryError("registry entry summary differs from its attestation")
    if signature.signed_artifact_sha256 != entry.attestation_sha256:
        raise AttestationRegistryError("registry signature is bound to a different attestation")
    if key_sha256 != entry.signing_key_sha256:
        raise AttestationRegistryError("registry trusted-key fingerprint is invalid")
    return entry, entry_sha256


def _verify_attestation_registry(
    registry_root: Path,
    *,
    allow_lock: bool,
) -> AttestationRegistryHistoryV1:
    root = _require_registry_root(registry_root)
    allowed_root_inventory = {
        REGISTRY_METADATA_PATH,
        REGISTRY_ENTRIES_PATH,
        REGISTRY_HEAD_PATH,
    }
    lock_path = root / REGISTRY_LOCK_PATH
    if lock_path.exists() or lock_path.is_symlink():
        if not allow_lock:
            raise AttestationRegistryError("registry is locked or has an interrupted writer")
        allowed_root_inventory.add(REGISTRY_LOCK_PATH)
    _require_exact_directory_inventory(root, allowed_root_inventory)
    metadata = _read_model(
        root / REGISTRY_METADATA_PATH,
        AttestationRegistryMetadataV1,
        maximum_bytes=MAX_REGISTRY_METADATA_BYTES,
    )
    assert isinstance(metadata, AttestationRegistryMetadataV1)
    recorded_head = _read_model(
        root / REGISTRY_HEAD_PATH,
        AttestationRegistryHeadV1,
        maximum_bytes=MAX_REGISTRY_METADATA_BYTES,
    )
    assert isinstance(recorded_head, AttestationRegistryHeadV1)
    entries_root = root / REGISTRY_ENTRIES_PATH
    if entries_root.is_symlink() or not entries_root.is_dir():
        raise AttestationRegistryError("registry entries root is missing or unsafe")
    try:
        entry_directories: list[Path] = []
        for directory in entries_root.iterdir():
            entry_directories.append(directory)
            if len(entry_directories) > MAX_REGISTRY_ENTRIES:
                raise AttestationRegistryError("registry exceeds the bounded entry limit")
        entry_directories.sort(key=lambda item: item.name)
    except OSError as error:
        raise AttestationRegistryError("registry entries are unreadable") from error
    entries: list[AttestationRegistryEntryV1] = []
    previous_sha256: str | None = None
    for expected_sequence, directory in enumerate(entry_directories, start=1):
        if directory.is_symlink() or not directory.is_dir():
            raise AttestationRegistryError("registry entries must be non-symlink directories")
        match = _ENTRY_DIRECTORY_PATTERN.fullmatch(directory.name)
        if match is None:
            raise AttestationRegistryError("registry contains an incomplete or unknown entry")
        named_sequence = int(match.group("sequence"))
        if named_sequence != expected_sequence:
            raise AttestationRegistryError("registry entry sequence is not contiguous")
        entry, entry_sha256 = _verify_entry_directory(
            directory,
            expected_sequence=expected_sequence,
            expected_previous_sha256=previous_sha256,
            expected_directory_sha256=match.group("sha256"),
        )
        entries.append(entry)
        previous_sha256 = entry_sha256
    if (
        recorded_head.entry_count != len(entries)
        or recorded_head.head_entry_sha256 != previous_sha256
    ):
        raise AttestationRegistryError("registry HEAD does not match its append-only history")
    return AttestationRegistryHistoryV1(
        entry_count=len(entries),
        head_entry_sha256=previous_sha256,
        entries=tuple(entries),
    )


def verify_attestation_registry(registry_root: Path) -> AttestationRegistryHistoryV1:
    """Validate the complete local registry, every signature, and its hash chain."""

    return _verify_attestation_registry(registry_root, allow_lock=False)


def _acquire_registry_lock(root: Path) -> Path:
    lock_path = root / REGISTRY_LOCK_PATH
    try:
        descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(b"flashpilot-attestation-registry-writer-v1\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise AttestationRegistryError("registry is locked or has an interrupted writer") from error
    except OSError as error:
        raise AttestationRegistryError("registry writer lock could not be created") from error
    return lock_path


def _release_registry_lock(root: Path, lock_path: Path) -> None:
    try:
        lock_path.unlink()
        fsync_directory(root)
    except OSError:
        # A retained lock fails all later reads and writes closed. It is safer than
        # reporting an unlocked registry when durable deletion is unavailable.
        pass


def _source_artifacts(attestation_path: Path, public_key_path: Path) -> dict[str, bytes]:
    try:
        signature_path = attestation_path.resolve(strict=True).parent / REGISTRY_SIGNATURE_PATH
    except OSError as error:
        raise AttestationRegistryError("source attestation path is missing or unsafe") from error
    return {
        REGISTRY_ATTESTATION_PATH: _read_regular_bytes(
            attestation_path,
            maximum_bytes=MAX_ATTESTATION_BYTES,
            description="source recovery attestation",
        ),
        REGISTRY_SIGNATURE_PATH: _read_regular_bytes(
            signature_path,
            maximum_bytes=MAX_ATTESTATION_SIGNATURE_BYTES,
            description="source detached signature",
        ),
        REGISTRY_PUBLIC_KEY_PATH: _read_regular_bytes(
            public_key_path,
            maximum_bytes=MAX_KEY_BYTES,
            description="trusted Ed25519 public key",
        ),
    }


def register_recovery_attestation(
    *,
    registry_root: Path,
    attestation_path: Path,
    public_key_path: Path,
) -> AttestationRegistryEntryV1:
    """Admit one fully verified signed attestation to an initialized local registry."""

    try:
        source_verification = verify_recovery_attestation(
            attestation_path,
            public_key_path=public_key_path,
            require_signed=True,
        )
    except (AttestationVerificationError, OSError, UnicodeError, ValueError) as error:
        raise AttestationRegistryError(
            "registry admission requires a valid signed recovery-attestation bundle"
        ) from error
    if (
        source_verification.signature_status != "verified"
        or source_verification.signing_key_sha256 is None
        or source_verification.signature_artifact_sha256 is None
    ):
        raise AttestationRegistryError("registry admission requires verified signature evidence")
    artifacts = _source_artifacts(attestation_path, public_key_path)
    try:
        attestation = RecoveryAttestationV1.model_validate_json(
            artifacts[REGISTRY_ATTESTATION_PATH]
        )
        AttestationSignatureV1.model_validate_json(artifacts[REGISTRY_SIGNATURE_PATH])
    except (ValidationError, ValueError) as error:
        raise AttestationRegistryError("registry source artifacts are malformed") from error
    if hashlib.sha256(artifacts[REGISTRY_ATTESTATION_PATH]).hexdigest() != (
        source_verification.attestation_sha256
    ):
        raise AttestationRegistryError("source attestation changed after verification")
    if hashlib.sha256(artifacts[REGISTRY_SIGNATURE_PATH]).hexdigest() != (
        source_verification.signature_artifact_sha256
    ):
        raise AttestationRegistryError("source signature changed after verification")

    root = _require_registry_root(registry_root)
    lock_path = _acquire_registry_lock(root)
    temporary_path: Path | None = None
    try:
        history = _verify_attestation_registry(root, allow_lock=True)
        if history.entry_count >= MAX_REGISTRY_ENTRIES:
            raise AttestationRegistryError("registry has reached the bounded entry limit")
        if any(
            entry.attestation_sha256 == source_verification.attestation_sha256
            for entry in history.entries
        ):
            raise AttestationRegistryError("attestation is already registered")
        sequence = history.entry_count + 1
        registry_artifacts = tuple(
            AttestationRegistryArtifactV1(
                path=path,
                size_bytes=len(value),
                sha256=hashlib.sha256(value).hexdigest(),
            )
            for path, value in sorted(artifacts.items())
        )
        entry = AttestationRegistryEntryV1(
            sequence=sequence,
            previous_entry_sha256=history.head_entry_sha256,
            attestation_sha256=source_verification.attestation_sha256,
            signature_artifact_sha256=source_verification.signature_artifact_sha256,
            signing_key_sha256=source_verification.signing_key_sha256,
            qualification_profile=attestation.qualification_profile,
            framework=attestation.framework,
            adapter=attestation.adapter,
            fault_scenario=attestation.fault_scenario,
            run_id=attestation.run_id,
            issued_at=attestation.issued_at,
            verification_check_ids=tuple(check.check_id for check in source_verification.checks),
            artifacts=registry_artifacts,
        )
        entry_bytes = _serialize_model(entry)
        entry_sha256 = hashlib.sha256(entry_bytes).hexdigest()
        entries_root = root / REGISTRY_ENTRIES_PATH
        temporary_path = entries_root / f".tmp-{uuid.uuid4().hex}"
        os.mkdir(temporary_path)
        for path, value in artifacts.items():
            _write_bytes_durable(temporary_path / path, value)
        _write_bytes_durable(temporary_path / REGISTRY_ENTRY_PATH, entry_bytes)
        completion = AttestationRegistryCompletionV1(
            sequence=sequence,
            entry_sha256=entry_sha256,
        )
        _write_bytes_durable(
            temporary_path / REGISTRY_COMPLETION_PATH,
            _serialize_model(completion),
        )
        temp_sync = fsync_directory(temporary_path)
        if temp_sync.supported and not temp_sync.succeeded:
            raise OSError(temp_sync.detail)
        _verify_entry_directory(
            temporary_path,
            expected_sequence=sequence,
            expected_previous_sha256=history.head_entry_sha256,
            expected_directory_sha256=entry_sha256,
        )
        repeated_verification = verify_recovery_attestation(
            attestation_path,
            public_key_path=public_key_path,
            require_signed=True,
        )
        if repeated_verification != source_verification or (
            _source_artifacts(attestation_path, public_key_path) != artifacts
        ):
            raise AttestationRegistryError("source bundle changed during registry admission")
        final_path = entries_root / f"{sequence:08d}-{entry_sha256}"
        os.rename(temporary_path, final_path)
        temporary_path = None
        parent_sync = fsync_directory(entries_root)
        if parent_sync.supported and not parent_sync.succeeded:
            raise OSError(parent_sync.detail)
        _replace_bytes_durable(
            root / REGISTRY_HEAD_PATH,
            _serialize_model(
                AttestationRegistryHeadV1(
                    entry_count=sequence,
                    head_entry_sha256=entry_sha256,
                )
            ),
        )
        updated = _verify_attestation_registry(root, allow_lock=True)
        if updated.head_entry_sha256 != entry_sha256 or updated.entries[-1] != entry:
            raise AttestationRegistryError("committed registry entry failed closed validation")
        return entry
    except AttestationRegistryError:
        raise
    except (AttestationVerificationError, AttestationSigningError, OSError, ValueError) as error:
        raise AttestationRegistryError("registry entry could not be committed safely") from error
    finally:
        if temporary_path is not None and temporary_path.exists():
            shutil.rmtree(temporary_path, ignore_errors=True)
        _release_registry_lock(root, lock_path)


def history_json(history: AttestationRegistryHistoryV1) -> str:
    """Render one deterministic machine-readable history document."""

    return json.dumps(history.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
