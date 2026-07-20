from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.ci.exits import EXIT_UNSUPPORTED
from flashpilot.fuzzing.models import FuzzRejectionReason, FuzzScenario
from flashpilot.fuzzing.service import run_partial_write_fuzz


def test_complete_two_iteration_matrix_fails_closed_and_is_reproducible(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = run_partial_write_fuzz(run_root=first_root, iterations=2)
    second = run_partial_write_fuzz(run_root=second_root, iterations=2)

    assert first.verdict == "PASS"
    assert first.passed is True
    assert first.total_cases == first.passed_cases == 12
    assert first.failed_cases == 0
    assert first.premature_acceptances == 0
    assert first.schedule_sha256 == second.schedule_sha256
    assert (first_root / "result.json").read_bytes() == (second_root / "result.json").read_bytes()
    assert all(
        case.source_unmodified and case.candidate_unmodified_by_validation for case in first.cases
    )
    assert first.recovery_verified is False
    assert first.attestation_emitted is False
    assert first.storage_savings_reported is False
    assert not (first_root / "recovery.attestation.json").exists()
    assert (first_root / "report.md").is_file()
    assert (first_root / "junit.xml").is_file()
    assert (first_root / "job-summary.md").is_file()
    sarif = json.loads((first_root / "results.sarif").read_text(encoding="utf-8"))
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == len(FuzzScenario)
    assert sarif["runs"][0]["results"] == []

    expected = {
        FuzzScenario.TRUNCATED_PAYLOAD: FuzzRejectionReason.PAYLOAD_SIZE_MISMATCH,
        FuzzScenario.MISSING_SHARD: FuzzRejectionReason.PAYLOAD_MISSING,
        FuzzScenario.STALE_MANIFEST: FuzzRejectionReason.COMPLETION_MISMATCH,
        FuzzScenario.CHECKSUM_MISMATCH: FuzzRejectionReason.CHECKSUM_MANIFEST_MISMATCH,
        FuzzScenario.DUPLICATE_RANK: FuzzRejectionReason.MANIFEST_INVALID,
    }
    for case in first.cases:
        if case.scenario is FuzzScenario.REORDERED_WRITES:
            assert case.expected_rejection_reason is None
            assert case.validation_attempts == 5
            assert len(case.observed_rejection_reasons) == 4
            assert case.final_valid is True
        else:
            assert case.observed_rejection_reasons == (expected[case.scenario],)
            assert case.final_valid is False


def test_fuzz_evidence_contains_no_absolute_paths_or_secret_values(
    monkeypatch,
    tmp_path: Path,
) -> None:
    sentinel = "sk-test-fuzz-secret-sentinel"
    monkeypatch.setenv("OPENAI_API_KEY", sentinel)
    run_root = tmp_path / "evidence"
    run_partial_write_fuzz(run_root=run_root, iterations=1)
    result_text = (run_root / "result.json").read_text(encoding="utf-8")

    assert sentinel not in result_text
    assert str(run_root.resolve()) not in result_text
    assert "OPENAI_API_KEY" not in result_text
    for case in json.loads(result_text)["cases"]:
        assert not Path(case["artifact_path"]).is_absolute()


def test_fuzz_checkpoint_cli_runs_the_typed_matrix(tmp_path: Path) -> None:
    run_root = tmp_path / "cli"
    invocation = CliRunner().invoke(
        cli.app,
        [
            "fuzz-checkpoint",
            "--scenario",
            "partial-write",
            "--iterations",
            "2",
            "--run-dir",
            str(run_root),
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "PASS" in invocation.output
    assert "Cases: 12/12 passed" in invocation.output
    assert "Premature acceptances: 0" in invocation.output
    assert "Recovery verified: false" in invocation.output
    assert "Storage savings reported: false" in invocation.output


def test_candidate_fuzz_command_uses_an_isolated_default_run(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    invocation = CliRunner().invoke(
        cli.app,
        [
            "fuzz-checkpoint",
            "--scenario",
            "partial-write",
            "--iterations",
            "1",
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    runs = tuple((tmp_path / "runs").glob("fuzz-*"))
    assert len(runs) == 1
    assert (runs[0] / "result.json").is_file()


def test_fuzz_checkpoint_cli_rejects_unknown_scenario(tmp_path: Path) -> None:
    invocation = CliRunner().invoke(
        cli.app,
        [
            "fuzz-checkpoint",
            "--scenario",
            "random-timing",
            "--run-dir",
            str(tmp_path / "unsupported"),
        ],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert "Unsupported checkpoint fuzz scenario" in invocation.output
    assert not (tmp_path / "unsupported").exists()
