import json
from pathlib import Path

import pytest

from flashpilot.orchestration.experiment import (
    WorkerProcessError,
    run_checkpoint_crash_phase,
    run_crash_recovery_experiment,
    run_recovery_phase,
)
from flashpilot.verification.console import render_recovery_gate
from flashpilot.verification.failure_artifact import (
    FORBIDDEN_FAILURE_PAYLOAD_TERMS,
    assert_sanitized_failure_payload,
)


@pytest.fixture(scope="module")
def safe_full_process_result(tmp_path_factory: pytest.TempPathFactory):
    run_root = tmp_path_factory.mktemp("process-safe-full")
    incomplete = run_root / "checkpoints" / ".checkpoint-step-000003.tmp-incomplete"
    incomplete.mkdir(parents=True)
    (incomplete / "model.pt").write_bytes(b"incomplete")
    result = run_crash_recovery_experiment(
        profile_name="ci",
        strategy="safe_full",
        run_root=run_root,
        checkpoint_step=4,
        hard_rollback_limit_steps=0,
    )
    assert incomplete.is_dir()
    return result


def test_safe_full_real_kill_and_new_process_restore_passes(
    safe_full_process_result,
) -> None:
    result = safe_full_process_result

    assert result.gate.passed is True
    assert result.crash.termination_verified is True
    assert result.crash.termination_exit_code != 0
    assert "Popen.kill" in result.crash.termination_method
    assert result.recovery.worker_pid != result.crash.worker_pid
    assert result.recovery_process.exit_code == 0
    assert result.recovery.final == result.control
    assert result.gate.achieved_rollback_steps == 0
    assert result.gate.comparison_policy.mode == "exact"
    assert result.gate.comparison_policy.atol == 0.0
    assert result.gate.comparison_policy.rtol == 0.0


def test_safe_adapter_aware_real_kill_and_new_process_restore_passes(
    tmp_path: Path,
) -> None:
    result = run_crash_recovery_experiment(
        profile_name="ci",
        strategy="safe_adapter_aware",
        run_root=tmp_path / "process-adapter",
        checkpoint_step=4,
        hard_rollback_limit_steps=0,
    )

    assert result.gate.passed is True
    assert result.crash.worker_pid != result.recovery.worker_pid
    assert result.recovery.final == result.control
    statuses = {check.check_id: check.status for check in result.gate.checks}
    assert statuses["integrity.base_present"] == "pass"
    assert statuses["integrity.base_hash"] == "pass"


def test_missing_training_state_real_recovery_fails_gate_and_is_sanitized(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "process-incomplete"
    result = run_crash_recovery_experiment(
        profile_name="ci",
        strategy="missing_training_state",
        run_root=run_root,
        checkpoint_step=4,
        hard_rollback_limit_steps=0,
    )

    assert result.gate.passed is False
    assert set(result.gate.failed_check_ids) == {
        "state.optimizer",
        "state.scheduler",
        "state.python_rng",
        "state.numpy_rng",
        "state.torch_rng",
        "trajectory.final_trainable",
        "trajectory.final_evaluation",
        "trajectory.loss_history",
        "contract.no_mandatory_omission",
    }
    assert result.recovery.restored_global_step == 4
    assert result.recovery.first_resumed_batch_step == 4
    assert result.recovery.first_completed_step == 5
    assert result.recovery.final.global_step == result.control.global_step
    assert result.failure_artifact_path == "agent/request.redacted.json"
    serialized = (run_root / result.failure_artifact_path).read_text(encoding="utf-8")
    assert_sanitized_failure_payload(serialized)
    lowered = serialized.lower()
    assert all(term not in lowered for term in FORBIDDEN_FAILURE_PAYLOAD_TERMS)
    assert str(Path.home()).lower() not in lowered
    payload = json.loads(serialized)
    assert "strategy" not in payload["manifest_summary"]
    assert "checkpoint_id" in payload["crash_metadata"]
    assert "checkpoint_path" not in payload["crash_metadata"]

    rendered = render_recovery_gate(result.gate)
    category_positions = [
        rendered.index(category)
        for category in (
            "Integrity",
            "Required training state",
            "Process recovery",
            "Trajectory correctness",
            "Safety and rollback",
        )
    ]
    assert category_positions == sorted(category_positions)


def test_corrupted_optimizer_fails_closed_before_recovery(tmp_path: Path) -> None:
    run_root = tmp_path / "corrupted-optimizer"
    crash = run_checkpoint_crash_phase(
        profile_name="ci",
        strategy="safe_full",
        run_root=run_root,
        checkpoint_step=4,
    )
    optimizer_path = crash.checkpoint.path / "optimizer.pt"
    with optimizer_path.open("r+b") as stream:
        first_byte = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first_byte[0] ^ 0xFF]))

    with pytest.raises(WorkerProcessError) as captured:
        run_recovery_phase(
            profile_name="ci",
            strategy="safe_full",
            run_root=run_root,
            checkpoint_path=crash.event.checkpoint_path,
        )

    assert captured.value.exit_code == 2
    assert "payload checksum mismatch: optimizer.pt" in captured.value.stderr
    assert not (run_root / "agent" / "request.redacted.json").exists()


def test_missing_base_fails_closed_before_recovery(tmp_path: Path) -> None:
    run_root = tmp_path / "missing-base-process"
    crash = run_checkpoint_crash_phase(
        profile_name="ci",
        strategy="safe_adapter_aware",
        run_root=run_root,
        checkpoint_step=4,
    )
    reference = crash.checkpoint.manifest.base_artifact
    assert reference is not None
    (run_root / reference.path).unlink()

    with pytest.raises(WorkerProcessError) as captured:
        run_recovery_phase(
            profile_name="ci",
            strategy="safe_adapter_aware",
            run_root=run_root,
            checkpoint_path=crash.event.checkpoint_path,
        )

    assert captured.value.exit_code == 2
    assert "frozen base validation failed" in captured.value.stderr


def test_real_post_commit_rollback_violation_is_rejected(tmp_path: Path) -> None:
    result = run_crash_recovery_experiment(
        profile_name="ci",
        strategy="safe_full",
        run_root=tmp_path / "rollback-violation",
        checkpoint_step=2,
        post_commit_steps=2,
        hard_rollback_limit_steps=1,
    )

    assert result.crash.last_completed_step == 4
    assert result.gate.achieved_rollback_steps == 2
    assert result.gate.passed is False
    assert result.gate.failed_check_ids == ("rollback.hard_limit",)
    assert result.recovery.final == result.control


def test_unexpected_checkpoint_worker_exit_code_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(WorkerProcessError) as captured:
        run_checkpoint_crash_phase(
            profile_name="ci",
            strategy="safe_full",
            run_root=tmp_path / "unexpected-exit",
            checkpoint_step=4,
            post_commit_steps=100,
        )

    assert captured.value.exit_code == 2
    assert "target_step cannot exceed" in captured.value.stderr
