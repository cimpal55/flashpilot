"""Deterministic persistence minimum for two-rank PyTorch FSDP."""

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


def distributed_fsdp_persistence_contract() -> PersistenceContract:
    """Return the exact same-world-size FSDP restart contract."""

    items = (
        _checkpoint_item("global_step", "rank-state", "Preserve completed global progress."),
        _checkpoint_item("loss_history", "rank-state", "Preserve each rank trajectory."),
        _checkpoint_item("model", "dcp.model", "Restore every FSDP model shard."),
        _checkpoint_item("numpy_rng", "rank-state.numpy_rng", "Restore per-rank NumPy RNG."),
        _checkpoint_item("optimizer", "dcp.optimizer", "Restore sharded optimizer state."),
        _checkpoint_item("python_rng", "rank-state.python_rng", "Restore per-rank Python RNG."),
        _checkpoint_item("scheduler", "rank-state.scheduler", "Restore scheduler phase."),
        _checkpoint_item(
            "topology",
            "manifest.topology",
            "Bind the checkpoint to the qualified process-group topology.",
            identity_controls=("backend=gloo", "implementation=fully_shard", "world_size=2"),
        ),
        _checkpoint_item("torch_rng", "rank-state.torch_rng", "Restore per-rank dropout RNG."),
    )
    return validate_persistence_contract(
        PersistenceContract(
            qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
            framework="pytorch-distributed",
            adapter="pytorch-fsdp",
            max_rpo_steps=0,
            items=items,
            assumptions=(
                "CPU-only included deterministic workload",
                "Gloo backend with a run-owned file-store rendezvous",
                "PyTorch fully_shard and Distributed Checkpoint APIs",
                "Same-world-size recovery at exactly two ranks",
            ),
            warnings=(
                "Only the deterministic 24-check Gate can verify recovery.",
                "Multi-rank fault injection and elastic resharding are separate milestones.",
            ),
        )
    )
