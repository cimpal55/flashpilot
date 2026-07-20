"""Machine-verifiable recovery attestation support."""

from flashpilot.attestation.builder import (
    AttestationEmission,
    emit_deepspeed_recovery_attestation,
    emit_distributed_recovery_attestation,
    emit_hf_preemption_attestation,
    emit_hf_recovery_attestation,
    emit_recovery_attestation,
)
from flashpilot.attestation.crypto import (
    AttestationSigningError,
    GeneratedSigningKey,
    generate_ed25519_signing_key,
)
from flashpilot.attestation.models import (
    ATTESTATION_JUNIT_PATH,
    ATTESTATION_SIGNATURE_PATH,
    EVIDENCE_MANIFEST_PATH,
    RECOVERY_ATTESTATION_PATH,
    AttestationSignatureV1,
    AttestationVerificationResult,
    EvidenceManifestV1,
    RecoveryAttestationV1,
)
from flashpilot.attestation.signing import (
    AttestationSignatureEmission,
    AttestationSignatureEmissionError,
    sign_recovery_attestation,
)
from flashpilot.attestation.verifier import (
    AttestationVerificationError,
    verify_recovery_attestation,
)

__all__ = [
    "ATTESTATION_JUNIT_PATH",
    "ATTESTATION_SIGNATURE_PATH",
    "EVIDENCE_MANIFEST_PATH",
    "RECOVERY_ATTESTATION_PATH",
    "AttestationEmission",
    "AttestationSignatureEmission",
    "AttestationSignatureEmissionError",
    "AttestationSignatureV1",
    "AttestationSigningError",
    "AttestationVerificationError",
    "AttestationVerificationResult",
    "EvidenceManifestV1",
    "GeneratedSigningKey",
    "RecoveryAttestationV1",
    "emit_recovery_attestation",
    "emit_deepspeed_recovery_attestation",
    "emit_distributed_recovery_attestation",
    "emit_hf_recovery_attestation",
    "emit_hf_preemption_attestation",
    "generate_ed25519_signing_key",
    "sign_recovery_attestation",
    "verify_recovery_attestation",
]
