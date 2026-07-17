"""Control, direct-checkpoint, and real process recovery commands."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated, cast

import typer

from flashpilot.checkpoints.strategies import baseline_json, run_safe_full_baseline
from flashpilot.domain.recovery import CheckpointStrategy
from flashpilot.orchestration.experiment import run_crash_recovery_experiment
from flashpilot.verification.console import render_recovery_gate
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


@app.command("crash-demo")
def crash_demo(
    profile: Annotated[
        str,
        typer.Option(help="Controlled workload profile: ci or demo."),
    ] = "ci",
    strategy: Annotated[
        str,
        typer.Option(
            help=("Checkpoint strategy: safe_full, safe_adapter_aware, or missing_training_state.")
        ),
    ] = "safe_full",
    run_dir: Annotated[
        Path | None,
        typer.Option(help="Isolated run directory."),
    ] = None,
    checkpoint_step: Annotated[
        int | None,
        typer.Option(help="Completed step at which the worker commits."),
    ] = None,
    rollback_limit: Annotated[
        int,
        typer.Option(help="Hard maximum lost steps between crash and checkpoint."),
    ] = 0,
) -> None:
    """Kill a real worker after commit, recover in a new process, and run the gate."""

    supported = {"safe_full", "safe_adapter_aware", "missing_training_state"}
    if strategy not in supported:
        raise typer.BadParameter("unsupported checkpoint strategy", param_hint="--strategy")
    selected_strategy = cast(CheckpointStrategy, strategy)
    selected_run_dir = run_dir or Path("runs") / f"crash-{uuid.uuid4().hex[:12]}"
    try:
        result = run_crash_recovery_experiment(
            profile_name=profile,
            strategy=selected_strategy,
            run_root=selected_run_dir,
            checkpoint_step=checkpoint_step,
            hard_rollback_limit_steps=rollback_limit,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
    typer.echo(f"Original worker PID: {result.crash.worker_pid}")
    typer.echo(f"Checkpoint step: {result.crash.checkpoint_step}")
    typer.echo(f"Checkpoint path: {result.crash.checkpoint_path}")
    typer.echo(f"Termination method: {result.crash.termination_method}")
    typer.echo(f"Termination exit code: {result.crash.termination_exit_code}")
    typer.echo(f"Recovery worker PID: {result.recovery.worker_pid}")
    typer.echo()
    typer.echo(render_recovery_gate(result.gate), nl=False)
    typer.echo(f"Result: {(selected_run_dir / result.result_path).resolve()}")
    if result.failure_artifact_path is not None:
        typer.echo(
            f"Sanitized failure artifact: "
            f"{(selected_run_dir / result.failure_artifact_path).resolve()}"
        )


if __name__ == "__main__":
    app()
