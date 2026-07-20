"""Bounded Ed25519 primitives for detached recovery-attestation signatures."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from flashpilot.attestation.models import AttestationSignatureV1
from flashpilot.checkpoints.atomic import fsync_directory

SIGNATURE_DOMAIN = b"flashpilot:recovery-attestation:v1\x00"
MAX_KEY_BYTES = 16 * 1024
MAX_ATTESTATION_BYTES = 1024 * 1024
PRIVATE_KEY_FILENAME = "ed25519-private.pem"
PUBLIC_KEY_FILENAME = "ed25519-public.pem"


class AttestationSigningError(ValueError):
    """Key material or a detached signature cannot be used safely."""


@dataclass(frozen=True, slots=True)
class GeneratedSigningKey:
    private_key_path: Path
    public_key_path: Path
    public_key_sha256: str
    private_key_permissions: str


def _read_regular_file(path: Path, *, maximum_bytes: int, description: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise AttestationSigningError(f"{description} must be a regular non-symlink file")
    try:
        resolved = path.resolve(strict=True)
        size = resolved.stat().st_size
        if size <= 0 or size > maximum_bytes:
            raise AttestationSigningError(f"{description} has an unsupported size")
        value = resolved.read_bytes()
    except OSError as error:
        raise AttestationSigningError(f"{description} is unreadable") from error
    if len(value) != size:
        raise AttestationSigningError(f"{description} changed while it was read")
    return value


def _load_private_key(path: Path) -> Ed25519PrivateKey:
    encoded = _read_regular_file(
        path,
        maximum_bytes=MAX_KEY_BYTES,
        description="Ed25519 private key",
    )
    try:
        key = serialization.load_pem_private_key(encoded, password=None)
    except (TypeError, ValueError, UnsupportedAlgorithm) as error:
        raise AttestationSigningError(
            "private key must be an unencrypted PKCS8 PEM Ed25519 key"
        ) from error
    if not isinstance(key, Ed25519PrivateKey):
        raise AttestationSigningError("private key algorithm must be Ed25519")
    return key


def _load_public_key(path: Path) -> Ed25519PublicKey:
    encoded = _read_regular_file(
        path,
        maximum_bytes=MAX_KEY_BYTES,
        description="trusted Ed25519 public key",
    )
    try:
        key = serialization.load_pem_public_key(encoded)
    except (ValueError, UnsupportedAlgorithm) as error:
        raise AttestationSigningError(
            "public key must be a SubjectPublicKeyInfo PEM Ed25519 key"
        ) from error
    if not isinstance(key, Ed25519PublicKey):
        raise AttestationSigningError("trusted public key algorithm must be Ed25519")
    return key


def _public_key_sha256(key: Ed25519PublicKey) -> str:
    raw = key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return hashlib.sha256(raw).hexdigest()


def _message(attestation_bytes: bytes) -> bytes:
    return SIGNATURE_DOMAIN + attestation_bytes


def _read_attestation_bytes(path: Path) -> bytes:
    return _read_regular_file(
        path,
        maximum_bytes=MAX_ATTESTATION_BYTES,
        description="recovery attestation",
    )


def create_attestation_signature(
    *,
    attestation_path: Path,
    private_key_path: Path,
) -> AttestationSignatureV1:
    """Sign the domain-separated exact bytes of one verified attestation."""

    attestation_bytes = _read_attestation_bytes(attestation_path)
    private_key = _load_private_key(private_key_path)
    public_key = private_key.public_key()
    signature = private_key.sign(_message(attestation_bytes))
    return AttestationSignatureV1(
        signed_artifact_sha256=hashlib.sha256(attestation_bytes).hexdigest(),
        public_key_sha256=_public_key_sha256(public_key),
        signature=base64.b64encode(signature).decode("ascii"),
    )


def verify_attestation_signature(
    *,
    attestation_path: Path,
    signature: AttestationSignatureV1,
    public_key_path: Path,
) -> str:
    """Verify exact bytes with an explicitly supplied trusted Ed25519 public key."""

    attestation_bytes = _read_attestation_bytes(attestation_path)
    actual_attestation_sha256 = hashlib.sha256(attestation_bytes).hexdigest()
    if not hmac.compare_digest(actual_attestation_sha256, signature.signed_artifact_sha256):
        raise AttestationSigningError("signed attestation SHA-256 mismatch")
    public_key = _load_public_key(public_key_path)
    actual_key_sha256 = _public_key_sha256(public_key)
    if not hmac.compare_digest(actual_key_sha256, signature.public_key_sha256):
        raise AttestationSigningError("trusted public key SHA-256 mismatch")
    try:
        decoded = base64.b64decode(signature.signature, validate=True)
    except (binascii.Error, ValueError) as error:
        raise AttestationSigningError("Ed25519 signature encoding is invalid") from error
    if len(decoded) != 64:
        raise AttestationSigningError("Ed25519 signature length is invalid")
    try:
        public_key.verify(decoded, _message(attestation_bytes))
    except InvalidSignature as error:
        raise AttestationSigningError("Ed25519 signature verification failed") from error
    return actual_key_sha256


def _write_new_file(path: Path, value: bytes, mode: int) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        os.close(descriptor)


def generate_ed25519_signing_key(output_dir: Path) -> GeneratedSigningKey:
    """Create one new unencrypted PKCS8/SPKI key pair without overwriting paths."""

    if output_dir.exists() or output_dir.is_symlink():
        raise AttestationSigningError("signing-key output directory must not already exist")
    lexical_parent = output_dir.absolute().parent
    if lexical_parent.is_symlink():
        raise AttestationSigningError("signing-key output parent must not be a symlink")
    try:
        parent = lexical_parent.resolve(strict=True)
    except OSError as error:
        raise AttestationSigningError("signing-key output parent is missing or unsafe") from error
    if not parent.is_dir():
        raise AttestationSigningError("signing-key output parent must be a directory")
    directory = parent / output_dir.name
    private_path = directory / PRIVATE_KEY_FILENAME
    public_path = directory / PUBLIC_KEY_FILENAME
    created_directory = False
    try:
        os.mkdir(directory, 0o700)
        created_directory = True
        private_key = Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        _write_new_file(private_path, private_bytes, 0o600)
        _write_new_file(public_path, public_bytes, 0o644)
        directory_sync = fsync_directory(directory)
        if directory_sync.supported and not directory_sync.succeeded:
            raise OSError(directory_sync.detail)
    except (OSError, UnsupportedAlgorithm) as error:
        if created_directory:
            private_path.unlink(missing_ok=True)
            public_path.unlink(missing_ok=True)
            try:
                directory.rmdir()
            except OSError:
                pass
        raise AttestationSigningError(
            "Ed25519 signing key could not be generated durably"
        ) from error
    permissions = "windows-best-effort" if os.name == "nt" else "posix-0600"
    return GeneratedSigningKey(
        private_key_path=private_path,
        public_key_path=public_path,
        public_key_sha256=_public_key_sha256(public_key),
        private_key_permissions=permissions,
    )
