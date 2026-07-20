"""Deterministic persistence minimum for the included HF Trainer contract."""

from __future__ import annotations

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


def huggingface_trainer_persistence_contract(
    profile: QualificationProfile = QualificationProfile.EXACT_TRAINING_RESUME,
) -> PersistenceContract:
    """Return the fixed exact-continuation contract qualified by the local example."""

    if profile not in {
        QualificationProfile.EXACT_TRAINING_RESUME,
        QualificationProfile.PREEMPTION_SAFE_TRAINING,
    }:
        raise ValueError("HF Trainer supports only exact-resume and preemption-safe contracts")

    items = (
        _checkpoint_item("batch_position", "trainer_state.json", "Resume the exact next batch."),
        _checkpoint_item("global_step", "trainer_state.json", "Preserve completed progress."),
        _checkpoint_item("model", "model.safetensors", "Restore all trained parameters."),
        _checkpoint_item("numpy_rng", "rng_state.pth", "Restore NumPy stochastic state."),
        _checkpoint_item("optimizer", "optimizer.pt", "Preserve optimizer trajectory state."),
        _checkpoint_item("python_rng", "rng_state.pth", "Restore Python stochastic state."),
        _checkpoint_item("scheduler", "scheduler.pt", "Preserve the learning-rate phase."),
        _checkpoint_item("torch_rng", "rng_state.pth", "Restore dropout stochastic state."),
        _checkpoint_item(
            "trainer_state", "trainer_state.json", "Restore Trainer progress and log history."
        ),
    )
    return validate_persistence_contract(
        PersistenceContract(
            qualification_profile=profile,
            framework="transformers",
            adapter="huggingface-trainer",
            max_rpo_steps=0,
            items=items,
            assumptions=(
                "CPU-only included local Trainer workload",
                "Sequential deterministic synthetic dataset",
                "Transformers and Accelerate versions recorded in environment evidence",
            ),
            warnings=(
                "Only the deterministic exact-trajectory gate can verify recovery.",
                "This contract does not claim compatibility with arbitrary Trainer scripts.",
            ),
        )
    )
