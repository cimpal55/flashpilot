"""Deterministic persistence minimum for two-rank DeepSpeed ZeRO stage 2."""

from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
)
from flashpilot.contracts.validation import validate_persistence_contract


def _checkpoint_item(
    state_id: str,
    evidence_id: str,
    reason: str,
    *,
    identity_controls: tuple[str, ...] = (),
) -> PersistenceItem:
    return PersistenceItem(
        state_id=state_id,
        requirement=RequirementClass.REQUIRED,
        recovery_source=RecoverySource.CHECKPOINT,
        exactness=RecoveryExactness.EXACT,
        identity_controls=identity_controls,
        evidence_ids=(evidence_id,),
        reason=reason,
    )


def deepspeed_zero2_persistence_contract() -> PersistenceContract:
    """Return the exact same-world-size DeepSpeed ZeRO-2 restart contract."""

    items = (
        _checkpoint_item("global_step", "client-state.global_step", "Preserve progress."),
        _checkpoint_item("loss_history", "rank-state", "Preserve each rank trajectory."),
        _checkpoint_item("model", "deepspeed.model-state", "Restore model parameters."),
        _checkpoint_item("numpy_rng", "rank-state.numpy_rng", "Restore per-rank NumPy RNG."),
        _checkpoint_item(
            "optimizer", "deepspeed.zero-optimizer-shards", "Restore both ZeRO optimizer shards."
        ),
        _checkpoint_item("python_rng", "rank-state.python_rng", "Restore per-rank Python RNG."),
        _checkpoint_item("scheduler", "deepspeed.model-state", "Restore scheduler phase."),
        _checkpoint_item(
            "topology",
            "manifest.topology",
            "Bind the checkpoint to the qualified DeepSpeed topology.",
            identity_controls=("backend=gloo", "world_size=2", "zero_stage=2"),
        ),
        _checkpoint_item("torch_rng", "rank-state.torch_rng", "Restore per-rank dropout RNG."),
    )
    return validate_persistence_contract(
        PersistenceContract(
            qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
            framework="deepspeed",
            adapter="deepspeed-engine",
            max_rpo_steps=0,
            items=items,
            assumptions=(
                "CPU-only included deterministic workload",
                "Gloo backend with a run-owned file-store rendezvous",
                "DeepSpeed 0.19.x ZeRO stage 2 checkpoint APIs",
                "Same-world-size recovery at exactly two ranks",
            ),
            warnings=(
                "Only the deterministic DeepSpeed Recovery Gate can verify recovery.",
                "Multi-rank fault injection and elastic recovery are separate milestones.",
            ),
        )
    )
