from __future__ import annotations

import pytest
from typer.testing import CliRunner

from flashpilot.agent.guardrails import RepairAttemptLimitError
from flashpilot.cli import app
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.orchestration.repair_loop import run_bounded_repair_loop
from flashpilot.repair.executor import execute_bounded_repair


@pytest.fixture(scope="module")
def completed_repair_loop(tmp_path_factory: pytest.TempPathFactory):
    run_root = tmp_path_factory.mktemp("repair-loop") / "run"
    result = run_bounded_repair_loop(
        profile_name="ci",
        run_root=run_root,
        checkpoint_step=4,
    )
    return run_root, result


def test_initial_failure_and_captured_plan_are_preserved(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.initial_failure.gate.passed is False
    assert set(result.initial_failure.gate.failed_check_ids) == {
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
    assert result.replay_call_metadata.source == "captured_live_response_replay"
    assert result.captured_live_failure_metadata.source == "captured_live_response"
    assert result.captured_live_failure_metadata.response_id
    assert tuple(action.action for action in result.proposed_analysis.repair_plan.actions) == (
        "change_supported_checkpoint_strategy",
        *NATIVE_PYTORCH_REPAIR_ACTIONS,
    )


def test_exactly_six_supported_actions_are_applied(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.repair_execution.applied_actions == NATIVE_PYTORCH_REPAIR_ACTIONS
    assert result.plan_validation.unsupported_actions == ("change_supported_checkpoint_strategy",)
    assert result.plan_validation.rejected_actions == ()
    assert "change_supported_checkpoint_strategy" not in result.repair_execution.applied_actions
    assert result.repair_attempt_count == 1
    assert result.repair_execution.repaired_config.complete_training_state_enabled is True


def test_original_checkpoint_is_unchanged_and_attempt_two_is_refused(
    completed_repair_loop,
) -> None:
    run_root, result = completed_repair_loop

    assert result.original_checkpoint_unmodified is True
    assert result.original_checkpoint_before == result.original_checkpoint_after
    with pytest.raises(RepairAttemptLimitError, match="one repair attempt"):
        execute_bounded_repair(validation=result.plan_validation, run_root=run_root)


def test_second_real_process_and_exact_final_gate_pass(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.repaired_run.crash.termination_verified is True
    assert result.repaired_run.crash.worker_pid != result.repaired_run.recovery.worker_pid
    assert result.repaired_run.recovery_process.exit_verified is True
    assert result.repaired_run.recovery.final == result.repaired_run.control
    assert result.repaired_run.gate.passed is True
    assert result.repaired_run.gate.failed_check_ids == ()
    assert all(
        check.status in {"pass", "not_applicable"} for check in result.repaired_run.gate.checks
    )
    assert result.repaired_run.gate.comparison_policy.atol == 0.0
    assert result.repaired_run.gate.comparison_policy.rtol == 0.0
    assert result.final_verdict == "VERIFIED"
    assert result.storage_comparison is not None


def test_prompt5_artifacts_and_read_only_cli_commands(completed_repair_loop) -> None:
    run_root, result = completed_repair_loop

    assert (
        RepairLoopResult.model_validate_json((run_root / "result.json").read_text(encoding="utf-8"))
        == result
    )
    assert (run_root / "report.md").is_file()
    assert (run_root / "agent/request.redacted.json").is_file()
    assert (run_root / "agent/failure/captured-live-metadata.json").is_file()
    assert (run_root / "agent/repair/repaired-strategy.json").is_file()
    runner = CliRunner()
    for command in ("audit", "verify", "replay"):
        invocation = runner.invoke(app, [command, "--run-dir", str(run_root)])
        assert invocation.exit_code == 0, invocation.output
