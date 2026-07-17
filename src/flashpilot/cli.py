"""Prompt 1 command-line entry points."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated

import typer

from flashpilot.checkpoints.strategies import baseline_json, run_safe_full_baseline
from flashpilot.workload.control import run_control

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


@app.command()
def control(
    profile: Annotated[
        str,
        typer.Option(help="Controlled workload profile: ci or demo."),
    ] = "ci",
    output: Annotated[
        Path | None,
        typer.Option(help="Optional JSON summary path."),
    ] = None,
) -> None:
    """Run an uninterrupted deterministic control."""

    try:
        summary = run_control(profile, output_path=output)
    except ValueError as error:
        raise typer.BadParameter(str(error), param_hint="--profile") from error
    typer.echo(summary.to_json(), nl=False)


@app.command("safe-full")
def safe_full(
    profile: Annotated[
        str,
        typer.Option(help="Controlled workload profile: ci or demo."),
    ] = "ci",
    run_dir: Annotated[
        Path | None,
        typer.Option(help="Isolated run directory."),
    ] = None,
    checkpoint_step: Annotated[
        int | None,
        typer.Option(help="Completed step to checkpoint."),
    ] = None,
) -> None:
    """Measure a safe_full checkpoint and direct restore baseline."""

    selected_run_dir = run_dir or Path("runs") / f"safe-full-{uuid.uuid4().hex[:12]}"
    try:
        result = run_safe_full_baseline(
            profile_name=profile,
            run_root=selected_run_dir,
            checkpoint_step=checkpoint_step,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(baseline_json(result), nl=False)


if __name__ == "__main__":
    app()
