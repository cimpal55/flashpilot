from __future__ import annotations

from pathlib import Path

from flashpilot.adapters.lightning import PyTorchLightningAdapter
from flashpilot.attestation import verify_recovery_attestation
from flashpilot.ci.service import emit_ci_outputs
from flashpilot.lightning.example import LIGHTNING_CHECKPOINT_STEP, LIGHTNING_TOTAL_STEPS
from flashpilot.lightning.qualification import run_lightning_qualification


def _script() -> Path:
    return Path(__file__).resolve().parents[2] / "examples" / "lightning" / "train.py"


def test_complete_lightning_checkpoint_survives_real_kill_and_exact_resume(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "complete"
    result = run_lightning_qualification(
        script_path=_script(),
        run_root=run_root,
        scenario="complete",
    )

    assert result.final_verdict == "VERIFIED"
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert result.verified_persisted_bytes is not None
    assert result.checkpoint_event.global_step == LIGHTNING_CHECKPOINT_STEP
    assert result.recovery.semantic_global_step == LIGHTNING_TOTAL_STEPS
    assert result.control.loss_history == result.recovery.loss_history
    assert result.control.trainable_state_sha256 == result.recovery.trainable_state_sha256
    assert result.control.evaluation_sha256 == result.recovery.evaluation_sha256
    assert result.control.optimizer_sha256 == result.recovery.optimizer_sha256
    assert result.control.scheduler_sha256 == result.recovery.scheduler_sha256
    assert (
        len(
            {
                result.control_process.worker_pid,
                result.crash_process.worker_pid,
                result.recovery_process.worker_pid,
            }
        )
        == 3
    )
    assert result.crash_process.exit_code != 0
    assert result.crash_process.exit_verified is True
    assert (run_root / "junit.xml").is_file()
    assert (run_root / "job-summary.md").is_file()
    assert (run_root / "results.sarif").is_file()
    verification = verify_recovery_attestation(run_root / "recovery.attestation.json")
    assert verification.valid is True
    assert emit_ci_outputs(run_root=run_root).exit_code == 0


def test_weights_only_checkpoint_loads_but_fails_exact_resume(tmp_path: Path) -> None:
    run_root = tmp_path / "weights-only"
    result = run_lightning_qualification(
        script_path=_script(),
        run_root=run_root,
        scenario="weights-only",
    )

    assert result.final_verdict == "FAILED"
    assert result.gate.passed is False
    assert result.model_checkpoint_load_succeeded is True
    assert result.weights_only_diverged is True
    assert result.verified_persisted_bytes is None
    assert not (run_root / "recovery.attestation.json").exists()
    assert (run_root / "results.sarif").is_file()
    assert {
        "checkpoint.optimizer",
        "checkpoint.scheduler",
        "checkpoint.rng",
        "checkpoint.loss-history",
    } <= set(result.gate.failed_check_ids)
    checkpoint = run_root / result.checkpoint_event.checkpoint_path
    presence = PyTorchLightningAdapter().training_state_presence(checkpoint)
    assert presence["model"] is True
    assert presence["optimizer"] is False
    assert presence["scheduler"] is False
    assert presence["rng"] is False
    assert presence["loss_history"] is False
    assert result.control.trainable_state_sha256 != result.recovery.trainable_state_sha256
    assert emit_ci_outputs(run_root=run_root).exit_code == 3
