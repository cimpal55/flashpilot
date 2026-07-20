"""Control, recovery, and guarded live-validation commands."""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from rich.console import Console

from flashpilot.adapters.huggingface import (
    HuggingFaceDependencyError,
    require_huggingface_dependencies,
)
from flashpilot.adapters.lightning import (
    LightningDependencyError,
    require_lightning_dependencies,
)
from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.fixture_provider import FixtureFailureProvider
from flashpilot.agent.guardrails import validate_failure_analysis
from flashpilot.agent.openai_provider import OpenAIContractProvider, OpenAIFailureProvider
from flashpilot.agent.service import (
    analyze_recovery_failure,
    build_contract_request,
    infer_checkpoint_contract,
)
from flashpilot.attestation import (
    ATTESTATION_JUNIT_PATH,
    RECOVERY_ATTESTATION_PATH,
    AttestationVerificationError,
    RecoveryAttestationV1,
    verify_recovery_attestation,
)
from flashpilot.attestation.reporters import render_attestation_summary
from flashpilot.audit import (
    AUDIT_EXIT_CODES,
    FrameworkSelection,
    StaticAuditError,
    run_static_audit,
)
from flashpilot.checkpoints.strategies import baseline_json, run_safe_full_baseline
from flashpilot.ci.exits import (
    EXIT_INVALID_EVIDENCE,
    EXIT_QUALIFICATION_FAILED,
    EXIT_UNSUPPORTED,
)
from flashpilot.ci.policy import CIPolicyError, load_ci_policy
from flashpilot.ci.service import CIEvidenceError, emit_ci_outputs, write_qualification_ci_outputs
from flashpilot.contracts.models import QualificationProfile
from flashpilot.diagnostics import run_doctor
from flashpilot.domain.agent import AgentCallMetadata
from flashpilot.domain.recovery import CheckpointStrategy, SanitizedFailureArtifact
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.orchestration.experiment import run_crash_recovery_experiment
from flashpilot.orchestration.repair_loop import run_bounded_repair_loop
from flashpilot.presentation.console import (
    render_demo_result,
    render_demo_start,
    render_doctor_result,
)
from flashpilot.verification.console import render_recovery_gate
from flashpilot.workload.control import run_control

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
qualify_app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
app.add_typer(qualify_app, name="qualify")

_CAPTURED_FAILURE_REQUEST = Path("runs/manual-prompt3-incomplete/agent/request.redacted.json")
_LIVE_CONTRACT_OBJECTIVE = (
    "Lose no completed steps. Recovery correctness is more important than checkpoint size."
)


def _default_demo_run_dir() -> Path:
    return Path("runs") / f"repair-{uuid.uuid4().hex}"


def _default_audit_output_dir() -> Path:
    return Path("runs") / f"audit-{uuid.uuid4().hex}"


def _default_hf_script() -> Path:
    return Path(__file__).resolve().parent / "hf" / "worker.py"


def _default_lightning_script() -> Path:
    return Path(__file__).resolve().parent / "lightning" / "worker.py"


def _load_repair_loop_result(run_dir: Path) -> RepairLoopResult:
    path = run_dir / "result.json"
    if not path.is_file():
        raise typer.BadParameter("Prompt 5 result.json is unavailable", param_hint="--run-dir")
    return RepairLoopResult.model_validate_json(path.read_text(encoding="utf-8"))


def _load_recovery_attestation(path: Path) -> RecoveryAttestationV1:
    return RecoveryAttestationV1.model_validate_json(path.read_text(encoding="utf-8"))


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


@qualify_app.command(
    "hf-trainer",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def qualify_hf_trainer(
    context: typer.Context,
    run_dir: Annotated[
        Path,
        typer.Option(help="New or empty isolated qualification directory."),
    ],
    script: Annotated[
        Path | None,
        typer.Option(
            help=(
                "Trainer script implementing the documented FlashPilot callback contract; "
                "defaults to the installed offline example."
            )
        ),
    ] = None,
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile; only exact-training-resume is supported."),
    ] = "exact-training-resume",
    fault: Annotated[
        str,
        typer.Option(help="Fault mechanism; only process-kill is supported."),
    ] = "process-kill",
    scenario: Annotated[
        str,
        typer.Option(help="Checkpoint scenario: complete or model-only."),
    ] = "complete",
) -> None:
    """Qualify the included offline CPU Hugging Face Trainer contract."""

    if profile != "exact-training-resume" or fault != "process-kill":
        typer.echo("Unsupported Hugging Face qualification profile or fault.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    if scenario not in {"complete", "model-only"}:
        typer.echo("Unsupported Hugging Face qualification scenario.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    try:
        require_huggingface_dependencies()
    except HuggingFaceDependencyError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    try:
        from flashpilot.hf.qualification import (
            HFQualificationError,
            HFUnsupportedConfigurationError,
            run_hf_qualification,
        )

        result = run_hf_qualification(
            script_path=script or _default_hf_script(),
            run_root=run_dir,
            scenario=cast("Any", scenario),
            forwarded_arguments=tuple(context.args),
        )
    except (
        HFUnsupportedConfigurationError,
        ValueError,
    ) as error:
        typer.echo(f"Hugging Face qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    except HFQualificationError as error:
        typer.echo(f"Hugging Face qualification failed: {error}", err=True)
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED) from error
    typer.echo(result.final_verdict)
    typer.echo(
        f"Processes: control={result.control_process.worker_pid}, "
        f"terminated={result.crash_process.worker_pid}, "
        f"recovery={result.recovery_process.worker_pid}"
    )
    typer.echo(f"Result: {(run_dir / result.result_path).resolve()}")
    typer.echo(f"Markdown report: {(run_dir / result.report_path).resolve()}")
    typer.echo(f"HTML report: {(run_dir / result.html_report_path).resolve()}")
    typer.echo(f"JUnit XML: {(run_dir / 'junit.xml').resolve()}")
    typer.echo(f"Job summary: {(run_dir / 'job-summary.md').resolve()}")
    typer.echo(f"SARIF: {(run_dir / 'results.sarif').resolve()}")
    if result.final_verdict == "VERIFIED":
        typer.echo(f"Recovery attestation: {(run_dir / RECOVERY_ATTESTATION_PATH).resolve()}")
    else:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@qualify_app.command("native-pytorch")
def qualify_native_pytorch(
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile; only exact-training-resume is supported."),
    ] = "exact-training-resume",
    fault: Annotated[
        str,
        typer.Option(help="Fault mechanism; only process-kill is supported."),
    ] = "process-kill",
    workload: Annotated[
        str,
        typer.Option(help="Controlled native workload size: ci or demo."),
    ] = "ci",
    run_dir: Annotated[
        Path | None,
        typer.Option(help="New isolated native qualification directory."),
    ] = None,
) -> None:
    """Run the preserved native red-to-green qualification through the generic CLI."""

    if profile != "exact-training-resume" or fault != "process-kill":
        typer.echo("Unsupported native qualification profile or fault.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    if workload not in {"ci", "demo"}:
        typer.echo("Unsupported native workload profile.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    selected_run_dir = run_dir or Path("runs") / f"native-qualify-{uuid.uuid4().hex}"
    try:
        result = run_bounded_repair_loop(
            profile_name=workload,
            run_root=selected_run_dir,
        )
    except ValueError as error:
        typer.echo(f"Native qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    except (OSError, RuntimeError) as error:
        typer.echo(f"Native qualification failed: {error}", err=True)
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED) from error
    typer.echo(result.final_verdict)
    typer.echo(
        f"Processes: terminated={result.repaired_run.crash.worker_pid}, "
        f"recovery={result.repaired_run.recovery.worker_pid}"
    )
    typer.echo(f"Result: {(selected_run_dir / result.result_path).resolve()}")
    typer.echo(f"JUnit XML: {(selected_run_dir / 'junit.xml').resolve()}")
    typer.echo(f"Job summary: {(selected_run_dir / 'job-summary.md').resolve()}")
    typer.echo(f"SARIF: {(selected_run_dir / 'results.sarif').resolve()}")
    if result.final_verdict == "VERIFIED":
        typer.echo(
            f"Recovery attestation: {(selected_run_dir / RECOVERY_ATTESTATION_PATH).resolve()}"
        )
    else:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@qualify_app.command(
    "lightning",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def qualify_lightning(
    context: typer.Context,
    run_dir: Annotated[
        Path,
        typer.Option(help="New or empty isolated Lightning qualification directory."),
    ],
    script: Annotated[
        Path | None,
        typer.Option(
            help=(
                "Lightning script implementing the documented FlashPilot contract; "
                "defaults to the installed offline example."
            )
        ),
    ] = None,
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile; only exact-training-resume is supported."),
    ] = "exact-training-resume",
    fault: Annotated[
        str,
        typer.Option(help="Fault mechanism; only process-kill is supported."),
    ] = "process-kill",
    scenario: Annotated[
        str,
        typer.Option(help="Checkpoint scenario: complete or weights-only."),
    ] = "complete",
) -> None:
    """Qualify the included CPU PyTorch Lightning contract."""

    if profile != "exact-training-resume" or fault != "process-kill":
        typer.echo("Unsupported Lightning qualification profile or fault.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    if scenario not in {"complete", "weights-only"}:
        typer.echo("Unsupported Lightning qualification scenario.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    try:
        require_lightning_dependencies()
    except LightningDependencyError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    try:
        from flashpilot.lightning.qualification import (
            LightningQualificationError,
            LightningUnsupportedConfigurationError,
            run_lightning_qualification,
        )

        result = run_lightning_qualification(
            script_path=script or _default_lightning_script(),
            run_root=run_dir,
            scenario=cast("Any", scenario),
            forwarded_arguments=tuple(context.args),
        )
    except (LightningUnsupportedConfigurationError, ValueError) as error:
        typer.echo(f"Lightning qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    except LightningQualificationError as error:
        typer.echo(f"Lightning qualification failed: {error}", err=True)
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED) from error
    typer.echo(result.final_verdict)
    typer.echo(
        f"Processes: control={result.control_process.worker_pid}, "
        f"terminated={result.crash_process.worker_pid}, "
        f"recovery={result.recovery_process.worker_pid}"
    )
    typer.echo(f"Result: {(run_dir / result.result_path).resolve()}")
    typer.echo(f"Markdown report: {(run_dir / result.report_path).resolve()}")
    typer.echo(f"HTML report: {(run_dir / result.html_report_path).resolve()}")
    typer.echo(f"JUnit XML: {(run_dir / 'junit.xml').resolve()}")
    typer.echo(f"Job summary: {(run_dir / 'job-summary.md').resolve()}")
    typer.echo(f"SARIF: {(run_dir / 'results.sarif').resolve()}")
    if result.final_verdict == "VERIFIED":
        typer.echo(f"Recovery attestation: {(run_dir / RECOVERY_ATTESTATION_PATH).resolve()}")
    else:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@qualify_app.command("conversions")
def qualify_conversions(
    run_dir: Annotated[
        Path,
        typer.Option(help="New or empty directory for all four conversion-equivalence cases."),
    ],
) -> None:
    """Qualify every plan-defined V0.3 checkpoint conversion."""

    try:
        from flashpilot.conversion.service import (
            ConversionQualificationError,
            run_conversion_qualification,
        )

        result = run_conversion_qualification(run_root=run_dir)
    except (ConversionQualificationError, OSError, ValueError) as error:
        typer.echo(f"Conversion qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.verdict)
    for case in result.cases:
        typer.echo(
            f"{case.conversion_kind.value}: "
            f"{'PASS' if case.passed else 'FAILED'} "
            f"({case.comparison_policy.mode})"
        )
    typer.echo("Recovery verified: false")
    typer.echo("Storage savings reported: false")
    typer.echo(f"Result: {(run_dir / result.result_path).resolve()}")
    typer.echo(f"JUnit XML: {(run_dir / result.junit_path).resolve()}")
    typer.echo(f"Job summary: {(run_dir / result.job_summary_path).resolve()}")
    typer.echo(f"SARIF: {(run_dir / result.sarif_path).resolve()}")
    if not result.passed:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@qualify_app.command("previous-valid-fallback")
def qualify_previous_valid_fallback(
    run_dir: Annotated[
        Path,
        typer.Option(help="New or empty previous-valid fallback evidence directory."),
    ],
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile; only exact-training-resume is supported."),
    ] = "exact-training-resume",
    scenario: Annotated[
        str,
        typer.Option(help="Fallback scenario; only corrupt-newest is supported."),
    ] = "corrupt-newest",
) -> None:
    """Prove exact recovery from the previous valid native checkpoint."""

    if profile != "exact-training-resume" or scenario != "corrupt-newest":
        typer.echo("Unsupported previous-valid fallback profile or scenario.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    try:
        from flashpilot.fallback.qualification import (
            FallbackQualificationError,
            run_previous_valid_fallback,
        )

        result = run_previous_valid_fallback(run_root=run_dir)
    except (FallbackQualificationError, OSError, RuntimeError, ValueError) as error:
        typer.echo(f"Previous-valid fallback qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.final_verdict)
    typer.echo(
        f"Selected step: {result.selected_checkpoint_step} "
        f"after rejecting step {result.producer_crash.checkpoint_step}"
    )
    typer.echo(
        f"Recovery Gate: {len(result.gate.checks) - len(result.gate.failed_check_ids)}/"
        f"{len(result.gate.checks)}"
    )
    typer.echo(
        f"RPO: {result.gate.achieved_rollback_steps}/{result.gate.hard_rollback_limit_steps} steps"
    )
    typer.echo(
        f"Processes: producer={result.checkpoint_set_event.worker_pid}, "
        f"recovery={result.recovery.worker_pid}"
    )
    typer.echo(f"Recovery verified: {str(result.recovery_verified).lower()}")
    typer.echo("Attestation emitted: false")
    typer.echo("Storage savings reported: false")
    typer.echo(f"Result: {(run_dir / result.result_path).resolve()}")
    typer.echo(f"JUnit XML: {(run_dir / result.junit_path).resolve()}")
    typer.echo(f"Job summary: {(run_dir / result.job_summary_path).resolve()}")
    typer.echo(f"SARIF: {(run_dir / result.sarif_path).resolve()}")
    if not result.recovery_verified:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@qualify_app.command("randomized-fault-timing")
def qualify_randomized_fault_timing(
    run_dir: Annotated[
        Path,
        typer.Option(help="New or empty repeated fault-timing evidence directory."),
    ],
    iterations: Annotated[
        int,
        typer.Option(help="Seeded process-kill trials, from 4 through 32."),
    ] = 8,
    seed: Annotated[
        int,
        typer.Option(help="Recorded nonnegative 63-bit schedule seed."),
    ] = 20_260_720,
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile; only exact-training-resume is supported."),
    ] = "exact-training-resume",
    fault: Annotated[
        str,
        typer.Option(help="Fault mechanism; only process-kill is supported."),
    ] = "process-kill",
) -> None:
    """Run seeded RPO-stratified native process-kill recovery trials."""

    if profile != "exact-training-resume" or fault != "process-kill":
        typer.echo("Unsupported randomized fault-timing profile or fault.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    if not 4 <= iterations <= 32 or not 0 <= seed <= 9_223_372_036_854_775_807:
        typer.echo("Unsupported randomized fault-timing iteration count or seed.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    try:
        from flashpilot.fault_timing.service import (
            RandomizedFaultTimingError,
            run_randomized_fault_timing,
        )

        result = run_randomized_fault_timing(
            run_root=run_dir,
            iterations=iterations,
            seed=seed,
        )
    except (RandomizedFaultTimingError, OSError, RuntimeError, ValueError) as error:
        typer.echo(f"Randomized fault-timing qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.final_verdict)
    typer.echo(f"Trials: {result.passed_trials}/{result.iterations}")
    typer.echo(f"Seed: {result.seed}")
    typer.echo(f"Schedule SHA-256: {result.schedule_sha256}")
    typer.echo(f"Observed RPO steps: {result.observed_rpo_steps}")
    typer.echo("Recovery Gate: 24/24 required per trial")
    typer.echo(f"Recovery verified: {str(result.recovery_verified).lower()}")
    typer.echo("Attestation emitted: false")
    typer.echo("Storage savings reported: false")
    typer.echo(f"Result: {(run_dir / result.result_path).resolve()}")
    typer.echo(f"JUnit XML: {(run_dir / result.junit_path).resolve()}")
    typer.echo(f"Job summary: {(run_dir / result.job_summary_path).resolve()}")
    typer.echo(f"SARIF: {(run_dir / result.sarif_path).resolve()}")
    if not result.recovery_verified:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@app.command("compare-checkpoints")
def compare_checkpoints(
    baseline: Annotated[Path, typer.Argument(help="Source conversion artifact directory.")],
    candidate: Annotated[
        Path,
        typer.Argument(help="Converted candidate artifact directory."),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(help="New or empty comparison evidence directory."),
    ],
) -> None:
    """Compare one typed source/candidate conversion pair deterministically."""

    try:
        from flashpilot.conversion.artifacts import ConversionArtifactError
        from flashpilot.conversion.service import (
            ConversionQualificationError,
            compare_conversion_artifacts,
        )

        result = compare_conversion_artifacts(
            source_path=baseline,
            candidate_path=candidate,
            output_dir=output_dir,
        )
    except (ConversionArtifactError, ConversionQualificationError, OSError, ValueError) as error:
        typer.echo(f"Checkpoint comparison rejected invalid evidence: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo("PASS" if result.passed else "FAILED")
    typer.echo(f"Conversion: {result.conversion_kind.value}")
    typer.echo(f"Equivalence policy: {result.comparison_policy.mode}")
    typer.echo(f"Source unmodified: {str(result.source_unmodified).lower()}")
    typer.echo("Recovery verified: false")
    typer.echo("Storage savings reported: false")
    typer.echo(f"Comparison JSON: {(output_dir / 'comparison.json').resolve()}")
    typer.echo(f"SARIF: {(output_dir / result.sarif_path).resolve()}")
    if not result.passed:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@app.command("fuzz-checkpoint")
def fuzz_checkpoint(
    scenario: Annotated[
        str,
        typer.Option(help="Fuzz scenario; only partial-write is supported."),
    ] = "partial-write",
    iterations: Annotated[
        int,
        typer.Option(help="Deterministic matrix iterations, from 1 through 1000."),
    ] = 100,
    run_dir: Annotated[
        Path | None,
        typer.Option(help="New or empty fuzz-evidence directory."),
    ] = None,
) -> None:
    """Qualify fail-closed handling of partial and incomplete checkpoint commits."""

    if scenario != "partial-write" or not 1 <= iterations <= 1000:
        typer.echo("Unsupported checkpoint fuzz scenario or iteration count.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
    selected_run_dir = run_dir or Path("runs") / f"fuzz-{uuid.uuid4().hex}"
    try:
        from flashpilot.fuzzing.service import (
            PartialWriteFuzzError,
            run_partial_write_fuzz,
        )

        result = run_partial_write_fuzz(
            run_root=selected_run_dir,
            iterations=iterations,
        )
    except (PartialWriteFuzzError, OSError, ValueError) as error:
        typer.echo(f"Checkpoint fuzz qualification could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.verdict)
    typer.echo(f"Cases: {result.passed_cases}/{result.total_cases} passed")
    typer.echo(f"Premature acceptances: {result.premature_acceptances}")
    typer.echo(f"Schedule SHA-256: {result.schedule_sha256}")
    typer.echo("Recovery verified: false")
    typer.echo("Storage savings reported: false")
    typer.echo(f"Result: {(selected_run_dir / result.result_path).resolve()}")
    typer.echo(f"JUnit XML: {(selected_run_dir / result.junit_path).resolve()}")
    typer.echo(f"Job summary: {(selected_run_dir / result.job_summary_path).resolve()}")
    typer.echo(f"SARIF: {(selected_run_dir / result.sarif_path).resolve()}")
    if not result.passed:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


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


@app.command("audit-checkpoint")
def audit_checkpoint(
    path: Annotated[
        Path,
        typer.Argument(help="Checkpoint directory to inspect without running training."),
    ],
    framework: Annotated[
        str,
        typer.Option(help="Framework selection: auto, native-pytorch, or huggingface-trainer."),
    ] = "auto",
    profile: Annotated[
        str,
        typer.Option(help="Qualification profile: exact-training-resume or model-only-inference."),
    ] = "exact-training-resume",
    output_dir: Annotated[
        Path | None,
        typer.Option(
            help=("New or empty directory for audit.json, report.md, junit.xml, and results.sarif.")
        ),
    ] = None,
) -> None:
    """Inspect checkpoint evidence without executing a training workload."""

    try:
        selected_framework = FrameworkSelection(framework)
        selected_profile = QualificationProfile(profile)
    except ValueError as error:
        typer.echo(f"Unsupported audit configuration: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    try:
        run = run_static_audit(
            checkpoint_path=path,
            framework_selection=selected_framework,
            profile=selected_profile,
            output_dir=output_dir or _default_audit_output_dir(),
        )
    except StaticAuditError as error:
        typer.echo(f"Static audit could not run: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    typer.echo(run.result.status.value)
    typer.echo("Static audit only; recovery_verified=false.")
    typer.echo(f"Framework: {run.result.framework.value}")
    typer.echo(f"Audit JSON: {run.audit_json}")
    typer.echo(f"Markdown report: {run.report_markdown}")
    typer.echo(f"JUnit XML: {run.junit_xml}")
    typer.echo(f"Job summary: {run.job_summary}")
    typer.echo(f"SARIF: {run.sarif_json}")
    exit_code = AUDIT_EXIT_CODES[run.result.status]
    if exit_code:
        raise typer.Exit(code=exit_code)


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
        typer.echo("Unsupported checkpoint strategy.", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED)
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
        typer.echo(f"Unsupported crash qualification configuration: {error}", err=True)
        raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    typer.echo(f"Original worker PID: {result.crash.worker_pid}")
    typer.echo(f"Checkpoint step: {result.crash.checkpoint_step}")
    typer.echo(f"Checkpoint path: {result.crash.checkpoint_path}")
    typer.echo(f"Termination method: {result.crash.termination_method}")
    typer.echo(f"Termination exit code: {result.crash.termination_exit_code}")
    typer.echo(f"Recovery worker PID: {result.recovery.worker_pid}")
    typer.echo()
    typer.echo(render_recovery_gate(result.gate), nl=False)
    typer.echo(f"Result: {(selected_run_dir / result.result_path).resolve()}")
    junit_path, summary_path, sarif_path = write_qualification_ci_outputs(
        run_root=selected_run_dir,
        result=result,
    )
    typer.echo(f"JUnit XML: {junit_path.resolve()}")
    typer.echo(f"Job summary: {summary_path.resolve()}")
    typer.echo(f"SARIF: {sarif_path.resolve()}")
    if result.failure_artifact_path is not None:
        typer.echo(
            f"Sanitized failure artifact: "
            f"{(selected_run_dir / result.failure_artifact_path).resolve()}"
        )
    if not result.gate.passed:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)


@app.command()
def demo(
    provider: Annotated[
        str,
        typer.Option(help="Prompt 5 diagnosis provider; only fixture replay is supported."),
    ] = "fixture",
    profile: Annotated[
        str,
        typer.Option(help="Controlled workload profile: ci or demo."),
    ] = "demo",
    run_dir: Annotated[
        Path | None,
        typer.Option(help="New isolated Prompt 5 run directory."),
    ] = None,
    checkpoint_step: Annotated[
        int | None,
        typer.Option(help="Completed step used by both real crash experiments."),
    ] = None,
) -> None:
    """Run one captured-response repair replay and deterministic verification."""

    if provider != "fixture":
        raise typer.BadParameter(
            "Prompt 5 permits only the accepted captured-response fixture replay",
            param_hint="--provider",
        )
    selected_run_dir = run_dir or _default_demo_run_dir()
    console = Console()
    render_demo_start(console=console, run_dir=selected_run_dir)
    started_at = time.perf_counter()
    with console.status(
        "Running deterministic control, two real process terminations, and exact recovery gates...",
        spinner="dots",
    ):
        result = run_bounded_repair_loop(
            profile_name=profile,
            run_root=selected_run_dir,
            checkpoint_step=checkpoint_step,
        )
    runtime_seconds = time.perf_counter() - started_at
    render_demo_result(
        console=console,
        result=result,
        run_dir=selected_run_dir,
        runtime_seconds=runtime_seconds,
    )
    if not result.repaired_run.gate.passed:
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)
    attestation_path = selected_run_dir / RECOVERY_ATTESTATION_PATH
    attestation = _load_recovery_attestation(attestation_path)
    verification = verify_recovery_attestation(attestation_path)
    render_attestation_summary(
        console=console,
        attestation=attestation,
        verification=verification,
    )
    typer.echo(f"Recovery attestation: {attestation_path.resolve()}")
    typer.echo(f"Attestation JUnit: {(selected_run_dir / ATTESTATION_JUNIT_PATH).resolve()}")
    typer.echo(f"Qualification JUnit: {(selected_run_dir / 'junit.xml').resolve()}")
    typer.echo(f"Job summary: {(selected_run_dir / 'job-summary.md').resolve()}")
    typer.echo(f"SARIF: {(selected_run_dir / 'results.sarif').resolve()}")


@app.command()
def doctor(
    output_dir: Annotated[
        Path | None,
        typer.Option(help="Output location to verify; defaults to ./runs."),
    ] = None,
) -> None:
    """Check the installed offline CPU judge path without exposing secrets."""

    selected_output = output_dir or Path("runs")
    result = run_doctor(output_dir=selected_output)
    render_doctor_result(console=Console(), result=result)
    if not result.passed:
        raise typer.Exit(code=1)


@app.command()
def audit(
    run_dir: Annotated[Path, typer.Option(help="Completed Prompt 5 run directory.")],
) -> None:
    """Read and summarize the immutable Prompt 5 evidence record."""

    result = _load_repair_loop_result(run_dir)
    typer.echo(f"Fixture replay source: {result.replay_call_metadata.source}")
    typer.echo(f"Captured response ID: {result.captured_live_failure_metadata.response_id}")
    typer.echo(f"Repair attempts: {result.repair_attempt_count}")
    typer.echo(f"Original checkpoint unmodified: {result.original_checkpoint_unmodified}")
    typer.echo(f"Final Recovery Gate: {result.final_verdict}")


@app.command()
def verify(
    run_dir: Annotated[Path, typer.Option(help="Completed Prompt 5 run directory.")],
) -> None:
    """Revalidate the persisted deterministic verdict without rerunning a process."""

    result = _load_repair_loop_result(run_dir)
    policy = result.repaired_run.gate.comparison_policy
    if (
        not result.repaired_run.gate.passed
        or result.final_verdict != "VERIFIED"
        or policy.atol != 0.0
        or policy.rtol != 0.0
        or not result.original_checkpoint_unmodified
        or result.repair_attempt_count != 1
    ):
        typer.echo("Persisted Prompt 5 evidence is not verified.", err=True)
        raise typer.Exit(code=EXIT_QUALIFICATION_FAILED)
    typer.echo("VERIFIED by the persisted deterministic Recovery Gate (atol=0.0, rtol=0.0).")


@app.command("verify-attestation")
def verify_attestation(
    file: Annotated[
        Path,
        typer.Argument(help="Path to recovery.attestation.json."),
    ],
) -> None:
    """Verify an unsigned attestation and its closed local evidence bundle."""

    try:
        verification = verify_recovery_attestation(file)
        attestation = _load_recovery_attestation(file)
    except (AttestationVerificationError, OSError, UnicodeError, ValueError) as error:
        typer.echo(f"INVALID OR TAMPERED: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    render_attestation_summary(
        console=Console(),
        attestation=attestation,
        verification=verification,
    )
    typer.echo(f"Attestation SHA-256: {verification.attestation_sha256}")
    typer.echo("Unsigned integrity verification passed; no publisher signature was checked.")


@app.command("emit-junit")
def emit_junit(
    run_dir: Annotated[
        Path,
        typer.Option(help="Completed audit or qualification run directory."),
    ],
    policy: Annotated[
        Path | None,
        typer.Option(help="Optional typed FlashPilot CI policy YAML."),
    ] = None,
) -> None:
    """Emit or verify deterministic JUnit, Markdown, and SARIF CI artifacts."""

    selected_policy = None
    if policy is not None:
        try:
            selected_policy = load_ci_policy(policy)
        except CIPolicyError as error:
            typer.echo(f"Unsupported CI policy: {error}", err=True)
            raise typer.Exit(code=EXIT_UNSUPPORTED) from error
    try:
        result = emit_ci_outputs(run_root=run_dir, policy=selected_policy)
    except (CIEvidenceError, CIPolicyError, OSError, UnicodeError, ValueError) as error:
        typer.echo(f"INVALID OR TAMPERED CI EVIDENCE: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.evidence.status.value)
    typer.echo(f"JUnit XML: {result.junit_path.resolve()}")
    typer.echo(f"Job summary: {result.job_summary_path.resolve()}")
    typer.echo(f"SARIF: {result.sarif_path.resolve()}")
    if result.policy_evaluation is not None:
        typer.echo("Policy: " + ("PASS" if result.policy_evaluation.passed else "FAIL"))
        for check in result.policy_evaluation.checks:
            if check.status.value == "FAIL":
                typer.echo(f"FAILED REQUIREMENT {check.check_id}: {check.summary}", err=True)
    if result.exit_code:
        raise typer.Exit(code=result.exit_code)


@app.command("emit-sarif")
def emit_sarif(
    run_dir: Annotated[
        Path,
        typer.Option(help="Completed audit or qualification run directory."),
    ],
) -> None:
    """Emit or verify deterministic SARIF alongside the existing CI artifacts."""

    try:
        result = emit_ci_outputs(run_root=run_dir)
    except (CIEvidenceError, OSError, UnicodeError, ValueError) as error:
        typer.echo(f"INVALID OR TAMPERED CI EVIDENCE: {error}", err=True)
        raise typer.Exit(code=EXIT_INVALID_EVIDENCE) from error
    typer.echo(result.evidence.status.value)
    typer.echo(f"SARIF: {result.sarif_path.resolve()}")
    typer.echo(f"JUnit XML: {result.junit_path.resolve()}")
    typer.echo(f"Job summary: {result.job_summary_path.resolve()}")
    if result.exit_code:
        raise typer.Exit(code=result.exit_code)


@app.command()
def replay(
    run_dir: Annotated[Path, typer.Option(help="Completed Prompt 5 run directory.")],
) -> None:
    """Replay and revalidate the captured structured response without an API call."""

    result = _load_repair_loop_result(run_dir)
    request = SanitizedFailureArtifact.model_validate_json(
        (run_dir / "agent" / "request.redacted.json").read_text(encoding="utf-8")
    )
    replayed = FixtureFailureProvider().analyze_failure(request).output
    validation = validate_failure_analysis(request, replayed)
    if replayed != result.proposed_analysis or validation != result.plan_validation:
        typer.echo("Fixture replay differs from the persisted accepted plan.", err=True)
        raise typer.Exit(code=1)
    typer.echo("Captured GPT-5.6 structured response replay matched; no API call was made.")


if __name__ == "__main__":
    app()
