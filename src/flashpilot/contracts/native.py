"""Native-PyTorch deterministic contracts and v0.1 contract migration."""

from __future__ import annotations

from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
)
from flashpilot.contracts.validation import (
    PersistenceContractValidationError,
    merge_with_deterministic_minimum,
    validate_persistence_contract,
)
from flashpilot.domain.agent import CheckpointContract

_EVIDENCE_BY_STATE: dict[str, tuple[str, ...]] = {
    "adapter": ("restore:model-state",),
    "base_model_identity": ("base:presence", "base:sha256"),
    "global_step": ("manifest:global-step",),
    "numpy_rng": ("restore:numpy-rng",),
    "optimizer": ("restore:optimizer-state",),
    "python_rng": ("restore:python-rng",),
    "scheduler": ("restore:scheduler-state",),
    "torch_rng": ("restore:torch-rng",),
}


def _required_checkpoint_item(state_id: str, reason: str) -> PersistenceItem:
    return PersistenceItem(
        state_id=state_id,
        requirement=RequirementClass.REQUIRED,
        recovery_source=RecoverySource.CHECKPOINT,
        exactness=RecoveryExactness.EXACT,
        identity_controls=("manifest-entry", "sha256-checksum"),
        evidence_ids=_EVIDENCE_BY_STATE[state_id],
        reason=reason,
    )


def _native_exact_items() -> tuple[PersistenceItem, ...]:
    return (
        _required_checkpoint_item(
            "adapter", "The trainable residual adapter must restore exactly."
        ),
        PersistenceItem(
            state_id="base_model_identity",
            requirement=RequirementClass.REQUIRED,
            recovery_source=RecoverySource.IMMUTABLE_REFERENCE,
            exactness=RecoveryExactness.EXACT,
            identity_controls=("base-artifact-identity", "base-artifact-sha256"),
            evidence_ids=_EVIDENCE_BY_STATE["base_model_identity"],
            reason="The adapter must bind to the exact immutable frozen base.",
        ),
        PersistenceItem(
            state_id="batch_position",
            requirement=RequirementClass.REQUIRED,
            recovery_source=RecoverySource.DETERMINISTIC_RECOMPUTE,
            exactness=RecoveryExactness.EXACT,
            identity_controls=("global-seed", "global-step"),
            evidence_ids=("process:next-step",),
            reason="The controlled workload derives the next batch from seed and global step.",
        ),
        _required_checkpoint_item("global_step", "The exact completed-step position must restore."),
        _required_checkpoint_item("numpy_rng", "NumPy RNG progression must restore exactly."),
        _required_checkpoint_item("optimizer", "AdamW continuation state must restore exactly."),
        _required_checkpoint_item("python_rng", "Python RNG progression must restore exactly."),
        _required_checkpoint_item("scheduler", "LinearLR continuation state must restore exactly."),
        _required_checkpoint_item(
            "torch_rng", "Torch RNG progression, including dropout, must restore exactly."
        ),
    )


def _native_model_only_items() -> tuple[PersistenceItem, ...]:
    required = [
        _required_checkpoint_item("adapter", "Inference requires the exact trained adapter."),
        PersistenceItem(
            state_id="base_model_identity",
            requirement=RequirementClass.REQUIRED,
            recovery_source=RecoverySource.IMMUTABLE_REFERENCE,
            exactness=RecoveryExactness.EXACT,
            identity_controls=("base-artifact-identity", "base-artifact-sha256"),
            evidence_ids=_EVIDENCE_BY_STATE["base_model_identity"],
            reason="Inference requires the exact immutable frozen base.",
        ),
    ]
    ephemeral = tuple(
        PersistenceItem(
            state_id=state_id,
            requirement=RequirementClass.EPHEMERAL,
            recovery_source=RecoverySource.NONE,
            exactness=RecoveryExactness.NON_EQUIVALENT,
            reason="Training-continuation state is not required for model-only inference.",
        )
        for state_id in (
            "batch_position",
            "global_step",
            "numpy_rng",
            "optimizer",
            "python_rng",
            "scheduler",
            "torch_rng",
        )
    )
    return (*required, *ephemeral)


def native_minimum_persistence_contract(
    profile: QualificationProfile,
    *,
    max_rpo_steps: int = 0,
) -> PersistenceContract:
    """Build the deterministic local minimum for the controlled native workload."""

    items = (
        _native_exact_items()
        if profile is QualificationProfile.EXACT_TRAINING_RESUME
        else _native_model_only_items()
    )
    contract = PersistenceContract(
        qualification_profile=profile,
        framework="native-pytorch",
        adapter="native-pytorch",
        max_rpo_steps=max_rpo_steps,
        items=items,
        assumptions=(
            "CPU-only controlled workload",
            "Only residual-adapter parameters are trainable",
        ),
        warnings=("Only the deterministic Recovery Gate can verify recovery.",),
    )
    return validate_persistence_contract(contract)


def migrate_native_checkpoint_contract(contract: CheckpointContract) -> PersistenceContract:
    """Convert the accepted v0.1 native training contract without changing v0.1 artifacts."""

    if contract.correctness_priority != "strict":
        raise PersistenceContractValidationError(
            "the v0.1 native contract must require strict correctness"
        )
    minimum = native_minimum_persistence_contract(
        QualificationProfile.EXACT_TRAINING_RESUME,
        max_rpo_steps=contract.rollback_limit_steps,
    )
    minimum_by_id = {item.state_id: item for item in minimum.items}
    migrated_items = []
    for requirement in contract.required_state:
        minimum_item = minimum_by_id.get(requirement.state)
        if minimum_item is None:
            raise PersistenceContractValidationError(
                f"v0.1 native contract contains unsupported state: {requirement.state}"
            )
        migrated_items.append(
            minimum_item.model_copy(
                update={
                    "requirement": (
                        RequirementClass.REQUIRED
                        if requirement.required
                        else RequirementClass.OPTIONAL
                    ),
                    "reason": requirement.reason,
                }
            )
        )
    proposed = PersistenceContract(
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="native-pytorch",
        adapter="native-pytorch",
        max_rpo_steps=contract.rollback_limit_steps,
        items=tuple(migrated_items),
        assumptions=contract.assumptions,
        warnings=contract.warnings,
    )
    return merge_with_deterministic_minimum(proposed, minimum)
