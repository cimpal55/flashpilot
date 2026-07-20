from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.checkpoints.loader import CheckpointValidationError, validate_checkpoint
from flashpilot.ci.exits import EXIT_UNSUPPORTED
from flashpilot.fallback.models import PreviousValidFallbackResult


def test_previous_valid_fallback_cli_proves_exact_recovery(
    monkeypatch,
    tmp_path: Path,
) -> None:
    sentinel = "sk-test-fallback-secret-sentinel"
    monkeypatch.setenv("OPENAI_API_KEY", sentinel)
    run_root = tmp_path / "fallback"

    invocation = CliRunner().invoke(
        cli.app,
        [
            "qualify",
            "previous-valid-fallback",
            "--run-dir",
            str(run_root),
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "VERIFIED" in invocation.output
    assert "Selected step: 2 after rejecting step 4" in invocation.output
    assert "Recovery Gate: 24/24" in invocation.output
    assert "RPO: 2/2 steps" in invocation.output
    assert "Recovery verified: true" in invocation.output
    assert "Attestation emitted: false" in invocation.output
    assert "Storage savings reported: false" in invocation.output

    result = PreviousValidFallbackResult.model_validate_json(
        (run_root / "result.json").read_text(encoding="utf-8")
    )
    assert result.final_verdict == "VERIFIED"
    assert result.recovery_verified is True
    assert result.valid_candidate_steps == (2,)
    assert result.selected_checkpoint_step == 2
    assert result.producer_crash.checkpoint_step == 4
    assert result.producer_crash.termination_verified is True
    assert result.producer_crash.termination_exit_code != 0
    assert result.checkpoint_set_event.worker_pid != result.recovery.worker_pid
    assert result.recovery.worker_pid == result.recovery_process.worker_pid
    assert result.recovery.checkpoint_path == result.selected_checkpoint_path
    assert all(check.status == "pass" for check in result.selection_checks)
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert len(result.gate.checks) == 24
    assert result.gate.achieved_rollback_steps == 2
    assert result.gate.hard_rollback_limit_steps == 2
    assert result.gate.comparison_policy.atol == 0.0
    assert result.gate.comparison_policy.rtol == 0.0
    assert result.recovery.final == result.control
    assert result.previous_sha256_before == result.previous_sha256_after
    assert result.newest_sha256_before_corruption != result.newest_sha256_after_corruption
    assert result.newest_sha256_after_corruption == result.newest_sha256_after_recovery
    assert result.attestation_emitted is False
    assert result.storage_savings_reported is False
    assert not (run_root / "recovery.attestation.json").exists()
    assert (run_root / "report.md").is_file()
    assert (run_root / "junit.xml").is_file()
    assert (run_root / "job-summary.md").is_file()
    sarif = json.loads((run_root / "results.sarif").read_text(encoding="utf-8"))
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == (
        len(result.selection_checks) + len(result.gate.checks)
    )
    assert sarif["runs"][0]["results"] == []

    previous = validate_checkpoint(
        run_root=run_root,
        checkpoint_path=run_root / result.selected_checkpoint_path,
    )
    assert previous.manifest.global_step == 2
    with pytest.raises(CheckpointValidationError, match="checksum mismatch: model.pt"):
        validate_checkpoint(
            run_root=run_root,
            checkpoint_path=run_root / result.newest_checkpoint_path,
        )

    for relative in (
        "result.json",
        "report.md",
        "junit.xml",
        "job-summary.md",
        "results.sarif",
    ):
        text = (run_root / relative).read_text(encoding="utf-8")
        assert sentinel not in text
        assert "OPENAI_API_KEY" not in text
        assert str(run_root.resolve()) not in text


@pytest.mark.parametrize(
    ("option", "value"),
    [("--profile", "model-only-inference"), ("--scenario", "missing-newest")],
)
def test_previous_valid_fallback_cli_rejects_unsupported_modes(
    tmp_path: Path,
    option: str,
    value: str,
) -> None:
    run_root = tmp_path / f"unsupported-{value}"
    invocation = CliRunner().invoke(
        cli.app,
        [
            "qualify",
            "previous-valid-fallback",
            "--run-dir",
            str(run_root),
            option,
            value,
        ],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert "Unsupported previous-valid fallback" in invocation.output
    assert not run_root.exists()
