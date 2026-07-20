"""Deterministic persistence minimum for the included Lightning contract."""

from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
)
from flashpilot.contracts.validation import validate_persistence_contract


def _checkpoint_item(state_id: str, evidence_id: str, reason: str) -> PersistenceItem:
    return PersistenceItem(
        state_id=state_id,
        requirement=RequirementClass.REQUIRED,
        recovery_source=RecoverySource.CHECKPOINT,
        exactness=RecoveryExactness.EXACT,
        evidence_ids=(evidence_id,),
        reason=reason,
    )


def pytorch_lightning_persistence_contract() -> PersistenceContract:
    """Return the exact-resume contract qualified by the local Lightning workload."""

    items = (
        _checkpoint_item("batch_position", "loops", "Resume the exact next train batch."),
        _checkpoint_item("global_step", "global_step", "Preserve completed progress."),
        _checkpoint_item(
            "loss_history", "flashpilot_exact_resume", "Preserve trajectory evidence."
        ),
        _checkpoint_item("model", "state_dict", "Restore every trained parameter."),
        _checkpoint_item("numpy_rng", "flashpilot_exact_resume.rng", "Restore NumPy RNG state."),
        _checkpoint_item("optimizer", "optimizer_states", "Preserve optimizer trajectory state."),
        _checkpoint_item("python_rng", "flashpilot_exact_resume.rng", "Restore Python RNG state."),
        _checkpoint_item("scheduler", "lr_schedulers", "Preserve learning-rate phase."),
        _checkpoint_item("torch_rng", "flashpilot_exact_resume.rng", "Restore dropout RNG state."),
    )
    return validate_persistence_contract(
        PersistenceContract(
            qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
            framework="lightning",
            adapter="pytorch-lightning",
            max_rpo_steps=0,
            items=items,
            assumptions=(
                "CPU-only included local LightningModule",
                "Deterministic synthetic step-indexed data",
                "Lightning version recorded in environment evidence",
            ),
            warnings=(
                "Only the deterministic exact-trajectory gate can verify recovery.",
                "This contract does not claim compatibility with arbitrary LightningModules.",
            ),
        )
    )
