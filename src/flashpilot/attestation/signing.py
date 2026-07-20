"""Create detached signatures only for fully verified recovery-attestation bundles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from flashpilot.attestation.crypto import create_attestation_signature
from flashpilot.attestation.models import (
    ATTESTATION_SIGNATURE_PATH,
    MAX_ATTESTATION_SIGNATURE_BYTES,
    AttestationSignatureV1,
    AttestationVerificationResult,
)
from flashpilot.attestation.verifier import _verify_recovery_attestation_bundle
from flashpilot.checkpoints.integrity import sha256_file
from flashpilot.orchestration.artifacts import write_json_artifact


class AttestationSignatureEmissionError(ValueError):
    """A verified attestation cannot be safely signed with the supplied key."""


@dataclass(frozen=True, slots=True)
class AttestationSignatureEmission:
    signature: AttestationSignatureV1
    signature_path: Path
    signature_sha256: str
    bundle_verification: AttestationVerificationResult


def _read_existing_signature(path: Path) -> AttestationSignatureV1:
    if path.is_symlink() or not path.is_file():
        raise AttestationSignatureEmissionError(
            "existing attestation signature must be a regular non-symlink file"
        )
    try:
        size = path.stat().st_size
        if size <= 0 or size > MAX_ATTESTATION_SIGNATURE_BYTES:
            raise AttestationSignatureEmissionError(
                "existing attestation signature has an unsupported size"
            )
        return AttestationSignatureV1.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise AttestationSignatureEmissionError(
            "existing attestation signature is malformed or unsupported"
        ) from error


def sign_recovery_attestation(
    *,
    attestation_path: Path,
    private_key_path: Path,
) -> AttestationSignatureEmission:
    """Verify the local bundle first, then sign its exact attestation bytes."""

    bundle_verification = _verify_recovery_attestation_bundle(attestation_path)
    signature = create_attestation_signature(
        attestation_path=attestation_path,
        private_key_path=private_key_path,
    )
    if (
        signature.signed_artifact_sha256 != bundle_verification.attestation_sha256
        or sha256_file(attestation_path.resolve(strict=True)) != signature.signed_artifact_sha256
    ):
        raise AttestationSignatureEmissionError(
            "recovery attestation changed after bundle verification"
        )
    root = attestation_path.resolve(strict=True).parent
    signature_path = root / ATTESTATION_SIGNATURE_PATH
    if signature_path.exists():
        existing = _read_existing_signature(signature_path)
        if existing != signature:
            raise AttestationSignatureEmissionError(
                "existing attestation signature differs from the requested key and payload"
            )
    else:
        write_json_artifact(
            run_root=root,
            relative_path=ATTESTATION_SIGNATURE_PATH,
            value=signature,
        )
    if _read_existing_signature(signature_path) != signature:
        raise AttestationSignatureEmissionError(
            "persisted attestation signature differs from the verified emission"
        )
    return AttestationSignatureEmission(
        signature=signature,
        signature_path=signature_path,
        signature_sha256=sha256_file(signature_path),
        bundle_verification=bundle_verification,
    )
