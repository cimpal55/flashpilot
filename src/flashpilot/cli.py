"""Control, recovery, and guarded live-validation commands."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Annotated, cast

import typer

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.openai_provider import OpenAIContractProvider, OpenAIFailureProvider
from flashpilot.agent.service import (
    analyze_recovery_failure,
    build_contract_request,
    infer_checkpoint_contract,
)
from flashpilot.checkpoints.strategies import baseline_json, run_safe_full_baseline
from flashpilot.domain.agent import AgentCallMetadata
from flashpilot.domain.recovery import CheckpointStrategy, SanitizedFailureArtifact
from flashpilot.orchestration.experiment import run_crash_recovery_experiment
from flashpilot.verification.console import render_recovery_gate
from flashpilot.workload.control import run_control

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)

_CAPTURED_FAILURE_REQUEST = Path("runs/manual-prompt3-incomplete/agent/request.redacted.json")
_LIVE_CONTRACT_OBJECTIVE = (
    "Lose no completed steps. Recovery correctness is more important than checkpoint size."
)


def _require_live_preconditions(*, run_dir: Path, role: str) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise typer.BadParameter("OpenAI API key is not set")
    artifact_root = run_dir / "agent" / role
    if artifact_root.exists():
        raise typer.BadParameter(
            "live capture directory already exists; choose a new run directory",
            param_hint="--run-dir",
        )


def _load_live_metadata(*, run_dir: Path, role: str) -> AgentCallMetadata:
    metadata_path = run_dir / "agent" / role / "metadata.json"
    metadata = AgentCallMetadata.model_validate_json(metadata_path.read_text(encoding="utf-8"))
    if metadata.provider != "openai" or metadata.source != "captured_live_response":
        raise RuntimeError("persisted metadata is not a captured live OpenAI response")
    return metadata


def _render_live_capture(*, run_dir: Path, role: str) -> None:
    metadata = _load_live_metadata(run_dir=run_dir, role=role)
    artifact_root = run_dir / "agent" / role
    typer.echo(f"Live {role} response captured and accepted by all guardrails.")
    typer.echo(f"Response ID: {metadata.response_id}")
    typer.echo(f"Request: {artifact_root / 'request.redacted.json'}")
    typer.echo(f"Parsed response: {artifact_root / 'response.parsed.json'}")
    typer.echo(f"Validation: {artifact_root / 'validation.json'}")
    typer.echo(f"Metadata: {artifact_root / 'metadata.json'}")


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


@app.command("live-contract")
def live_contract(
    run_dir: Annotated[
        Path,
        typer.Option(help="New isolated directory for one live contract capture."),
    ],
) -> None:
    """Make one guarded live checkpoint-contract inference call."""

    _require_live_preconditions(run_dir=run_dir, role="contract")
    request = build_contract_request(
        adapter=NativePyTorchAdapter(),
        user_objective=_LIVE_CONTRACT_OBJECTIVE,
        hard_rollback_limit_steps=0,
    )
    infer_checkpoint_contract(
        provider=OpenAIContractProvider(),
        request=request,
        run_root=run_dir,
    )
    _render_live_capture(run_dir=run_dir, role="contract")


@app.command("live-failure")
def live_failure(
    run_dir: Annotated[
        Path,
        typer.Option(help="New isolated directory for one live failure-analysis capture."),
    ],
) -> None:
    """Make one guarded live analysis call from the fixed Prompt 3 capture."""

    _require_live_preconditions(run_dir=run_dir, role="failure")
    if not _CAPTURED_FAILURE_REQUEST.is_file():
        raise typer.BadParameter("the captured Prompt 3 redacted failure request is unavailable")
    request = SanitizedFailureArtifact.model_validate_json(
        _CAPTURED_FAILURE_REQUEST.read_text(encoding="utf-8")
    )
    analyze_recovery_failure(
        provider=OpenAIFailureProvider(),
        request=request,
        run_root=run_dir,
    )
    _render_live_capture(run_dir=run_dir, role="failure")


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
