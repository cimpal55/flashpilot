from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.ci.exits import EXIT_UNSUPPORTED
from flashpilot.fault_timing.models import RandomizedFaultTimingResult
from flashpilot.fault_timing.service import (
    RandomizedFaultTimingError,
    verify_randomized_fault_timing,
)


def test_randomized_fault_timing_cli_runs_real_stratified_process_kills(
    monkeypatch,
    tmp_path: Path,
) -> None:
    sentinel = "sk-test-randomized-timing-secret-sentinel"
    monkeypatch.setenv("OPENAI_API_KEY", sentinel)
    run_root = tmp_path / "randomized-timing"

    invocation = CliRunner().invoke(
        cli.app,
        [
            "qualify",
            "randomized-fault-timing",
            "--run-dir",
            str(run_root),
            "--iterations",
            "4",
            "--seed",
            "20260720",
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "VERIFIED" in invocation.output
    assert "Trials: 4/4" in invocation.output
    assert "Recovery Gate: 24/24 required per trial" in invocation.output
    assert "Recovery verified: true" in invocation.output
    assert "Attestation emitted: false" in invocation.output
    assert "Storage savings reported: false" in invocation.output

    result = RandomizedFaultTimingResult.model_validate_json(
        (run_root / "result.json").read_text(encoding="utf-8")
    )
    assert verify_randomized_fault_timing(run_root) == result
    assert result.final_verdict == "VERIFIED"
    assert result.passed_trials == result.iterations == 4
    assert result.observed_rpo_steps == (0, 1, 2, 3)
    assert result.unique_timing_pairs == 4
    assert result.attestation_emitted is False
    assert result.storage_savings_reported is False
    assert not (run_root / "recovery.attestation.json").exists()
    assert all(trial.passed for trial in result.trials)
    assert all(trial.gate_checks_passed == trial.gate_checks_total == 24 for trial in result.trials)
    assert all(trial.failed_gate_check_ids == () for trial in result.trials)
    assert all(trial.exact_control_match for trial in result.trials)
    assert all(trial.producer_pid != trial.recovery_pid for trial in result.trials)
    assert all(trial.producer_exit_code != 0 for trial in result.trials)
    assert all(trial.producer_termination_verified for trial in result.trials)
    assert all(trial.recovery_exit_code == 0 for trial in result.trials)
    assert all(trial.recovery_exit_verified for trial in result.trials)

    for relative in ("result.json", "report.md", "junit.xml", "job-summary.md"):
        text = (run_root / relative).read_text(encoding="utf-8")
        assert sentinel not in text
        assert "OPENAI_API_KEY" not in text
        assert str(run_root.resolve()) not in text

    first_trial = run_root / result.trials[0].trial_result_path
    first_trial.write_text(first_trial.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(RandomizedFaultTimingError, match="fingerprint mismatch"):
        verify_randomized_fault_timing(run_root)


@pytest.mark.parametrize(
    ("arguments", "label"),
    [
        (("--profile", "model-only-inference"), "profile"),
        (("--fault", "power-loss"), "fault"),
        (("--iterations", "3"), "iterations"),
        (("--seed", "-1"), "seed"),
    ],
)
def test_randomized_fault_timing_cli_rejects_unsupported_inputs(
    tmp_path: Path,
    arguments: tuple[str, str],
    label: str,
) -> None:
    run_root = tmp_path / f"unsupported-{label}"
    invocation = CliRunner().invoke(
        cli.app,
        [
            "qualify",
            "randomized-fault-timing",
            "--run-dir",
            str(run_root),
            *arguments,
        ],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert "Unsupported randomized fault-timing" in invocation.output
    assert not run_root.exists()
