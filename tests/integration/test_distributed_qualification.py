from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from flashpilot.attestation import verify_recovery_attestation
from flashpilot.ci.service import emit_ci_outputs
from flashpilot.distributed.checkpoint import (
    DistributedCheckpointError,
    validate_distributed_checkpoint,
)
from flashpilot.distributed.gate import evaluate_distributed_recovery_gate
from flashpilot.distributed.qualification import run_distributed_qualification


def test_two_rank_fsdp_checkpoint_exactly_restores_and_fails_closed_on_mutation(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "distributed"
    result = run_distributed_qualification(run_root=run_root)

    assert result.final_verdict == "VERIFIED"
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert len(result.gate.checks) == 24
    assert result.verified_persisted_bytes is not None
    assert result.world_size == 2
    assert result.strategy == "fsdp"
    assert result.implementation == "fully_shard"
    assert result.backend == "gloo"
    assert (
        len(
            {
                process.worker_pid
                for phase in (
                    result.control_processes,
                    result.checkpoint_processes,
                    result.recovery_processes,
                )
                for process in phase.ranks
            }
        )
        == 6
    )
    assert tuple(rank.loss_history for rank in result.recovery) == tuple(
        rank.loss_history for rank in result.control
    )
    assert tuple(rank.trainable_state_sha256 for rank in result.recovery) == tuple(
        rank.trainable_state_sha256 for rank in result.control
    )
    assert tuple(rank.evaluation_sha256 for rank in result.recovery) == tuple(
        rank.evaluation_sha256 for rank in result.control
    )
    assert tuple(rank.optimizer_sha256 for rank in result.recovery) == tuple(
        rank.optimizer_sha256 for rank in result.control
    )
    assert tuple(rank.scheduler_sha256 for rank in result.recovery) == tuple(
        rank.scheduler_sha256 for rank in result.control
    )
    checkpoint = run_root / result.checkpoint_event.checkpoint_path
    validated = validate_distributed_checkpoint(run_root=run_root, checkpoint_path=checkpoint)
    assert validated.logical_bytes == result.verified_persisted_bytes
    assert "dcp/.metadata" in validated.inventory
    assert "rank-state-000.json" in validated.inventory
    assert "rank-state-001.json" in validated.inventory
    assert verify_recovery_attestation(run_root / "recovery.attestation.json").valid is True
    assert emit_ci_outputs(run_root=run_root).exit_code == 0

    changed_losses = (*result.recovery[0].loss_history[:-1], 999.0)
    changed_rank_zero = result.recovery[0].model_copy(update={"loss_history": changed_losses})
    changed_gate = evaluate_distributed_recovery_gate(
        control_processes=result.control_processes,
        control=result.control,
        checkpoint_processes=result.checkpoint_processes,
        checkpoint=result.checkpoint,
        recovery_processes=result.recovery_processes,
        recovery=(changed_rank_zero, result.recovery[1]),
        checkpoint_event=result.checkpoint_event,
        validated_checkpoint=validated,
        checkpoint_step=result.checkpoint_manifest.global_step,
        total_steps=result.control[0].final_global_step,
    )
    assert changed_gate.passed is False
    assert changed_gate.failed_check_ids == ("trajectory.loss-history",)

    missing_marker = run_root / "mutations" / "missing-marker" / checkpoint.name
    shutil.copytree(checkpoint, missing_marker)
    (missing_marker / "COMPLETE").unlink()
    with pytest.raises(DistributedCheckpointError):
        validate_distributed_checkpoint(run_root=run_root, checkpoint_path=missing_marker)

    tampered = run_root / "mutations" / "tampered" / checkpoint.name
    shutil.copytree(checkpoint, tampered)
    shard = next((tampered / "dcp").glob("*.distcp"))
    with shard.open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(DistributedCheckpointError, match="size mismatch"):
        validate_distributed_checkpoint(run_root=run_root, checkpoint_path=tampered)

    extra = run_root / "mutations" / "extra" / checkpoint.name
    shutil.copytree(checkpoint, extra)
    (extra / "unexpected.bin").write_bytes(b"extra")
    with pytest.raises(DistributedCheckpointError, match="inventory is not closed"):
        validate_distributed_checkpoint(run_root=run_root, checkpoint_path=extra)
