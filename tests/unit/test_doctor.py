from __future__ import annotations

from pathlib import Path

from rich.console import Console
from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.diagnostics import run_doctor
from flashpilot.presentation.console import render_doctor_result


def test_doctor_reports_offline_cpu_judge_requirements_without_key(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = run_doctor(output_dir=tmp_path / "runs")
    console = Console(record=True, width=180, color_system=None)
    render_doctor_result(console=console, result=result)
    rendered = console.export_text()

    assert result.passed is True
    assert "Python version" in rendered
    assert "OS / platform" in rendered
    assert "CPU execution" in rendered
    assert "Required dependencies" in rendered
    assert "Captured-response fixtures" in rendered
    assert "Writable output location" in rendered
    assert "OPENAI_API_KEY" in rendered
    assert "Not present (not required by fixture demo)" in rendered
    assert "Directory fsync" in rendered
    assert "Doctor verdict" in rendered


def test_doctor_never_prints_api_key_value(tmp_path: Path, monkeypatch) -> None:
    secret = "test-only-do-not-print-this-key"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    doctor_result = run_doctor(output_dir=tmp_path / "direct-runs")
    api_check = next(check for check in doctor_result.checks if check.name == "OPENAI_API_KEY")

    invocation = CliRunner().invoke(
        cli.app,
        ["doctor", "--output-dir", str(tmp_path / "runs")],
    )

    assert invocation.exit_code == 0, invocation.output
    assert api_check.detail == "Present (value hidden; not used by fixture demo)"
    assert "OPENAI_API_KEY" in invocation.output
    assert secret not in invocation.output


def test_default_demo_run_directories_are_unique_and_bounded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    first = cli._default_demo_run_dir()
    second = cli._default_demo_run_dir()

    assert first != second
    assert first.parent == Path("runs")
    assert second.parent == Path("runs")
    assert len(first.name.removeprefix("repair-")) == 32
    assert len(second.name.removeprefix("repair-")) == 32
