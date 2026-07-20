from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from flashpilot.attestation import verify_recovery_attestation
from flashpilot.ci.service import emit_ci_outputs
from flashpilot.deepspeed.checkpoint import (
    DeepSpeedCheckpointError,
    validate_deepspeed_checkpoint,
)
from flashpilot.deepspeed.gate import evaluate_deepspeed_recovery_gate
from flashpilot.deepspeed.qualification import run_deepspeed_qualification

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux") or importlib.util.find_spec("deepspeed") is None,
    reason="real DeepSpeed ZeRO-2 qualification requires the Linux optional dependency",
)


def test_two_rank_deepspeed_zero2_exactly_restores_and_fails_closed_on_mutation(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "deepspeed"
    result = run_deepspeed_qualification(run_root=run_root)

    assert result.final_verdict == "VERIFIED"
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert len(result.gate.checks) == 30
    assert result.verified_persisted_bytes is not None
    assert result.world_size == 2
    assert result.strategy == "zero"
    assert result.implementation == "zero-stage-2"
    assert result.zero_stage == 2
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
    validated = validate_deepspeed_checkpoint(run_root=run_root, checkpoint_path=checkpoint)
    assert validated.logical_bytes == result.verified_persisted_bytes
    assert f"{result.checkpoint_manifest.checkpoint_tag}/mp_rank_00_model_states.pt" in (
        validated.inventory
    )
    assert sum("optim_states.pt" in path for path in validated.inventory) == 2
    assert verify_recovery_attestation(run_root / "recovery.attestation.json").valid is True
    assert emit_ci_outputs(run_root=run_root).exit_code == 0

    changed_losses = (*result.recovery[0].loss_history[:-1], 999.0)
    changed_rank_zero = result.recovery[0].model_copy(update={"loss_history": changed_losses})
    changed_gate = evaluate_deepspeed_recovery_gate(
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
    with pytest.raises(DeepSpeedCheckpointError):
        validate_deepspeed_checkpoint(run_root=run_root, checkpoint_path=missing_marker)

    tampered = run_root / "mutations" / "tampered" / checkpoint.name
    shutil.copytree(checkpoint, tampered)
    shard = next(tampered.rglob("*optim_states.pt"))
    with shard.open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(DeepSpeedCheckpointError, match="size mismatch"):
        validate_deepspeed_checkpoint(run_root=run_root, checkpoint_path=tampered)

    extra = run_root / "mutations" / "extra" / checkpoint.name
    shutil.copytree(checkpoint, extra)
    (extra / "unexpected.bin").write_bytes(b"extra")
    with pytest.raises(DeepSpeedCheckpointError, match="inventory is not closed"):
        validate_deepspeed_checkpoint(run_root=run_root, checkpoint_path=extra)
