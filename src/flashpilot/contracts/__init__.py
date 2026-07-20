"""VNext persistence contracts and deterministic qualification rules."""

from flashpilot.contracts.canonical import canonical_contract_json, persistence_contract_sha256
from flashpilot.contracts.deepspeed import deepspeed_zero2_persistence_contract
from flashpilot.contracts.distributed import distributed_fsdp_persistence_contract
from flashpilot.contracts.huggingface import huggingface_trainer_persistence_contract
from flashpilot.contracts.lightning import pytorch_lightning_persistence_contract
from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
)
from flashpilot.contracts.native import (
    migrate_native_checkpoint_contract,
    native_minimum_persistence_contract,
)
from flashpilot.contracts.validation import (
    PersistenceContractValidationError,
    merge_with_deterministic_minimum,
    validate_persistence_contract,
)

__all__ = [
    "PersistenceContract",
    "PersistenceContractValidationError",
    "PersistenceItem",
    "QualificationProfile",
    "RecoveryExactness",
    "RecoverySource",
    "RequirementClass",
    "canonical_contract_json",
    "deepspeed_zero2_persistence_contract",
    "distributed_fsdp_persistence_contract",
    "huggingface_trainer_persistence_contract",
    "merge_with_deterministic_minimum",
    "migrate_native_checkpoint_contract",
    "native_minimum_persistence_contract",
    "persistence_contract_sha256",
    "pytorch_lightning_persistence_contract",
    "validate_persistence_contract",
]
