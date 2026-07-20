from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.conversion.models import ConversionKind
from flashpilot.conversion.service import (
    build_conversion_artifacts,
    run_conversion_qualification,
)


def test_all_four_conversion_classes_pass_with_declared_equivalence(tmp_path: Path) -> None:
    run_root = tmp_path / "qualification"
    result = run_conversion_qualification(run_root=run_root)

    assert result.verdict == "PASS"
    assert result.passed is True
    assert result.failed_cases == ()
    assert tuple(case.conversion_kind for case in result.cases) == tuple(ConversionKind)
    assert all(
        case.passed and case.source_unmodified and case.candidate_unmodified
        for case in result.cases
    )
    assert [case.comparison_policy.mode for case in result.cases] == [
        "tolerance-bounded",
        "tolerance-bounded",
        "exact",
        "exact-training-resume",
    ]
    assert 0.0 <= result.cases[0].maximum_absolute_difference <= 1e-12
    assert 0.0 < result.cases[1].maximum_absolute_difference <= 1e-12
    assert result.cases[2].maximum_absolute_difference == 0.0
    assert result.cases[3].maximum_absolute_difference == 0.0
    assert result.cases[3].resume_in_distinct_process is True
    assert result.cases[3].resume_worker_pid != result.cases[3].comparison_process_pid
    assert all(case.resume_worker_pid is None for case in result.cases[:3])
    assert result.recovery_verified is False
    assert result.attestation_emitted is False
    assert result.storage_savings_reported is False
    assert not (run_root / "recovery.attestation.json").exists()
    assert (run_root / "result.json").is_file()
    assert (run_root / "report.md").is_file()
    assert (run_root / "junit.xml").is_file()
    assert (run_root / "job-summary.md").is_file()
    sarif = json.loads((run_root / "results.sarif").read_text(encoding="utf-8"))
    sarif_run = sarif["runs"][0]
    assert len(sarif_run["tool"]["driver"]["rules"]) == sum(
        len(case.checks) for case in result.cases
    )
    assert sarif_run["results"] == []
    junit = (run_root / "junit.xml").read_text(encoding="utf-8")
    for kind in ConversionKind:
        assert kind.value in junit
    version_checks = {
        check.check_id
        for check in result.cases[-1].checks
        if check.check_id.startswith("continuation.")
    }
    assert version_checks == {
        "continuation.global-step",
        "continuation.loss-history",
        "continuation.trainable-state",
        "continuation.evaluation",
        "continuation.optimizer",
        "continuation.scheduler",
    }


def test_compare_checkpoints_cli_reuses_typed_comparison_core(tmp_path: Path) -> None:
    source, candidate = build_conversion_artifacts(
        run_root=tmp_path / "artifacts",
        kind=ConversionKind.SHARDED_TO_CONSOLIDATED,
    )
    output = tmp_path / "comparison"

    invocation = CliRunner().invoke(
        cli.app,
        [
            "compare-checkpoints",
            str(source),
            str(candidate),
            "--output-dir",
            str(output),
        ],
    )

    assert invocation.exit_code == 0
    assert "PASS" in invocation.output
    assert "sharded-to-consolidated" in invocation.output
    assert "Recovery verified: false" in invocation.output
    assert "Storage savings reported: false" in invocation.output
    persisted = json.loads((output / "comparison.json").read_text(encoding="utf-8"))
    assert persisted["passed"] is True
    assert persisted["recovery_verified"] is False
    sarif = json.loads((output / "results.sarif").read_text(encoding="utf-8"))
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == len(persisted["checks"])
    assert sarif["runs"][0]["results"] == []
