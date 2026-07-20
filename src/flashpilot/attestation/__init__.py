"""Machine-verifiable recovery attestation support."""

from flashpilot.attestation.builder import (
    AttestationEmission,
    emit_deepspeed_recovery_attestation,
    emit_distributed_recovery_attestation,
    emit_hf_preemption_attestation,
    emit_hf_recovery_attestation,
    emit_recovery_attestation,
)
from flashpilot.attestation.models import (
    ATTESTATION_JUNIT_PATH,
    EVIDENCE_MANIFEST_PATH,
    RECOVERY_ATTESTATION_PATH,
    AttestationVerificationResult,
    EvidenceManifestV1,
    RecoveryAttestationV1,
)
from flashpilot.attestation.verifier import (
    AttestationVerificationError,
    verify_recovery_attestation,
)

__all__ = [
    "ATTESTATION_JUNIT_PATH",
    "EVIDENCE_MANIFEST_PATH",
    "RECOVERY_ATTESTATION_PATH",
    "AttestationEmission",
    "AttestationVerificationError",
    "AttestationVerificationResult",
    "EvidenceManifestV1",
    "RecoveryAttestationV1",
    "emit_recovery_attestation",
    "emit_deepspeed_recovery_attestation",
    "emit_distributed_recovery_attestation",
    "emit_hf_recovery_attestation",
    "emit_hf_preemption_attestation",
    "verify_recovery_attestation",
]
