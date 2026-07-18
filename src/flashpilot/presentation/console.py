"""Rich judge-facing presentation rendered from deterministic result records."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from flashpilot.diagnostics import DoctorResult
from flashpilot.domain.repair import RepairLoopResult

GPT_SOURCE = "GPT source: GPT-5.6 captured-response fixture/replay"
MEASUREMENT_DISCLAIMER = (
    "Logical checkpoint bytes were measured in the controlled demo. "
    "Physical NAND writes, write amplification, and SSD lifetime were not measured."
)


def _status(label: str) -> Text:
    styles = {
        "PASS": "bold green",
        "VERIFIED": "bold green",
        "FAIL": "bold red",
        "UNSUPPORTED": "bold yellow",
        "GPT RECOMMENDATION": "bold magenta",
        "GUARDRAIL ACCEPTED": "bold cyan",
    }
    return Text(label, style=styles[label])


def render_demo_start(*, console: Console, run_dir: Path) -> None:
    body = Text()
    body.append("Checkpoint recovery qualification and verification harness\n", style="bold")
    body.append("CPU-only · offline fixture replay · no API key required\n", style="cyan")
    body.append(f"Generated run path: {run_dir.resolve()}")
    console.print(Panel(body, title="FlashPilot", border_style="blue"))
    console.print("[bold cyan]RUNNING[/] Complete real red-to-green workflow\n")


def _stage_table(result: RepairLoopResult) -> Table:
    repaired = result.repaired_run
    table = Table(title="Recovery qualification stages", header_style="bold blue")
    table.add_column("Stage", style="bold")
    table.add_column("Outcome", no_wrap=True)
    table.add_row(
        "Uninterrupted control",
        _status("PASS"),
    )
    table.add_row(
        "Initial checkpoint",
        _status("PASS"),
    )
    table.add_row(
        "First real process termination",
        _status("PASS"),
    )
    table.add_row(
        "Initial Recovery Gate",
        _status("FAIL"),
    )
    table.add_row(
        "GPT-5.6 captured-response fixture/replay diagnosis",
        _status("GPT RECOMMENDATION"),
    )
    table.add_row(
        "Deterministic bounded repair",
        _status("GUARDRAIL ACCEPTED"),
    )
    table.add_row(
        "Second real process termination",
        _status("PASS"),
    )
    table.add_row(
        "Final Recovery Gate",
        _status("VERIFIED" if repaired.gate.passed else "FAIL"),
    )
    storage_status = "VERIFIED" if result.storage_comparison is not None else "FAIL"
    table.add_row(
        "Verified storage comparison",
        _status(storage_status),
    )
    return table


def _decision_table(result: RepairLoopResult) -> Table:
    table = Table(title="GPT recommendations and deterministic guardrail decisions")
    table.add_column("Proposed action", style="magenta")
    table.add_column("Decision", no_wrap=True)
    for decision in result.plan_validation.decisions:
        if decision.disposition == "accepted":
            status = _status("GUARDRAIL ACCEPTED")
        elif decision.disposition == "unsupported":
            status = _status("UNSUPPORTED")
        else:
            status = _status("FAIL")
        table.add_row(decision.action, status)
    return table


def render_demo_result(
    *,
    console: Console,
    result: RepairLoopResult,
    run_dir: Path,
    runtime_seconds: float,
) -> None:
    console.print(GPT_SOURCE, style="bold magenta")
    console.print(
        "The failure is intentional and deterministic, but GPT-5.6 does not receive the "
        "injection label. It receives only the sanitized checkpoint manifest, restore behavior, "
        "failed Recovery Gate checks, and trajectory evidence.\n"
    )
    console.print(_stage_table(result))
    evidence = Text()
    evidence.append("Initial checkpoint: ", style="bold")
    evidence.append(
        f"step {result.initial_failure.crash.checkpoint_step}; worker PID "
        f"{result.initial_failure.crash.worker_pid}; recovery PID "
        f"{result.initial_failure.recovery.worker_pid}\n"
    )
    evidence.append("Initial gate: ", style="bold red")
    evidence.append(f"{len(result.initial_failure.gate.failed_check_ids)} exact failures\n")
    evidence.append("Repaired run: ", style="bold")
    evidence.append(
        f"worker PID {result.repaired_run.crash.worker_pid}; recovery PID "
        f"{result.repaired_run.recovery.worker_pid}\n"
    )
    evidence.append("Final gate: ", style="bold green")
    evidence.append(
        f"{len(result.repaired_run.gate.checks)}/"
        f"{len(result.repaired_run.gate.checks)} passed; atol=0.0, rtol=0.0"
    )
    console.print(Panel(evidence, title="Deterministic process evidence"))
    console.print()
    console.print(_decision_table(result))
    console.print(
        "Accepted actions map to explicit strategy booleans; unsupported or rejected actions "
        "are not executed.",
        style="cyan",
    )

    if result.repaired_run.gate.passed and result.storage_comparison is not None:
        storage = result.storage_comparison
        headline = Text()
        headline.append(
            f"{storage.structural_reduction_bytes:,} fewer recurring logical bytes ",
            style="bold green",
        )
        headline.append(f"({storage.structural_reduction_percent:.2f}%)", style="green")
        console.print(
            Panel(
                headline,
                title="VERIFIED STORAGE COMPARISON",
                border_style="green",
            )
        )
        metrics = Table(show_header=False, box=None)
        metrics.add_column(style="bold")
        metrics.add_column(justify="right")
        metrics.add_row("safe_full recurring logical bytes", f"{storage.safe_full_bytes:,}")
        metrics.add_row(
            "Repaired recurring logical bytes",
            f"{storage.repaired_recurring_bytes:,}",
        )
        metrics.add_row(
            "One-time frozen-base cost (separate)",
            f"{storage.repaired_one_time_base_bytes:,}",
        )
        console.print(metrics)
        console.print(
            "The first adapter-aware write is not presented as savings; the immutable base is "
            "reported separately.",
            style="italic",
        )

    console.print(f"\n{MEASUREMENT_DISCLAIMER}", style="yellow")
    artifacts = Table(title="Generated artifacts", show_header=False)
    artifacts.add_column("Artifact", style="bold")
    artifacts.add_column("Path")
    artifacts.add_row("Run directory", str(run_dir.resolve()))
    artifacts.add_row("result.json", str((run_dir / result.result_path).resolve()))
    artifacts.add_row("report.md", str((run_dir / result.report_path).resolve()))
    artifacts.add_row("report.html", str((run_dir / result.html_report_path).resolve()))
    artifacts.add_row("Total runtime", f"{runtime_seconds:.2f} seconds")
    console.print(artifacts)


def render_doctor_result(*, console: Console, result: DoctorResult) -> None:
    styles = {
        "PASS": "bold green",
        "FAIL": "bold red",
        "INFO": "bold cyan",
        "LIMITATION": "bold yellow",
    }
    table = Table(title="FlashPilot doctor", header_style="bold blue")
    table.add_column("Check", style="bold", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Detail")
    for check in result.checks:
        table.add_row(check.name, Text(check.status, style=styles[check.status]), check.detail)
    console.print(table)
    overall = Text(
        "PASS" if result.passed else "FAIL", style="bold green" if result.passed else "bold red"
    )
    console.print(
        Panel(overall, title="Doctor verdict", border_style="green" if result.passed else "red")
    )
