"""Optional local attestation registry and append-only history."""

from flashpilot.registry.models import (
    AttestationRegistryArtifactV1,
    AttestationRegistryCompletionV1,
    AttestationRegistryEntryV1,
    AttestationRegistryHeadV1,
    AttestationRegistryHistoryV1,
    AttestationRegistryMetadataV1,
)
from flashpilot.registry.service import (
    AttestationRegistryError,
    history_json,
    initialize_attestation_registry,
    register_recovery_attestation,
    verify_attestation_registry,
)

__all__ = [
    "AttestationRegistryArtifactV1",
    "AttestationRegistryCompletionV1",
    "AttestationRegistryEntryV1",
    "AttestationRegistryError",
    "AttestationRegistryHistoryV1",
    "AttestationRegistryHeadV1",
    "AttestationRegistryMetadataV1",
    "history_json",
    "initialize_attestation_registry",
    "register_recovery_attestation",
    "verify_attestation_registry",
]
