"""Bounded parent harness for real two-rank DeepSpeed ZeRO-2 qualification."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from flashpilot.deepspeed.checkpoint import validate_deepspeed_checkpoint
from flashpilot.deepspeed.gate import evaluate_deepspeed_recovery_gate
from flashpilot.deepspeed.models import (
    DeepSpeedCheckpointEvent,
    DeepSpeedQualificationResult,
    DeepSpeedRankSummary,
    DeepSpeedRecoveryGateV1,
)
from flashpilot.deepspeed.reporting import render_deepspeed_html, render_deepspeed_markdown
from flashpilot.distributed.models import (
    DistributedPhaseProcessEvidence,
    DistributedRankProcessEvidence,
)
from flashpilot.multirank.gate import evaluate_multi_rank_failure_checks
from flashpilot.multirank.models import MultiRankFailureEvent
from flashpilot.multirank.orchestration import (
    MultiRankFailureError,
    run_targeted_rank_termination,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.workload.profiles import get_profile


class DeepSpeedQualificationError(RuntimeError):
    """The DeepSpeed qualification could not produce trustworthy evidence."""


class DeepSpeedUnsupportedConfigurationError(DeepSpeedQualificationError):
    """The selected DeepSpeed configuration is outside the supported contract."""


def _require_deepspeed() -> str:
    if not sys.platform.startswith("linux"):
        raise DeepSpeedUnsupportedConfigurationError(
            "DeepSpeed qualification requires a Linux host; Windows is rejected before launch"
        )
    if importlib.util.find_spec("deepspeed") is None:
        raise DeepSpeedUnsupportedConfigurationError(
            "DeepSpeed is not installed; install the flashpilot[deepspeed] extra on Linux"
        )
    try:
        version = importlib.metadata.version("deepspeed")
        major, minor = (int(part) for part in version.split(".", maxsplit=2)[:2])
    except (importlib.metadata.PackageNotFoundError, TypeError, ValueError) as error:
        raise DeepSpeedUnsupportedConfigurationError(
            "DeepSpeed version cannot be established"
        ) from error
    if (major, minor) != (0, 19):
        raise DeepSpeedUnsupportedConfigurationError(
            f"unsupported DeepSpeed version {version}; expected >=0.19,<0.20"
        )
    return version


def _environment(*, seed: int, torch_extensions_dir: Path) -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        normalized = key.upper()
        if normalized == "OPENAI_API_KEY" or normalized.endswith("_API_KEY"):
            environment.pop(key)
    source_root = Path(__file__).resolve().parents[2]
    python_paths = [str(source_root)]
    if os.name == "nt":
        site_packages = Path(sys.prefix) / "Lib" / "site-packages"
        if site_packages.is_dir():
            python_paths.append(str(site_packages))
    if existing := environment.get("PYTHONPATH"):
        python_paths.append(existing)
    executable_dir = Path(sys.executable).resolve().parent
    existing_path = environment.get("PATH", "")
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "OMP_NUM_THREADS": "1",
            "PATH": os.pathsep.join((str(executable_dir), existing_path)),
            "PYTHONHASHSEED": str(seed),
            "PYTHONPATH": os.pathsep.join(python_paths),
            "PYTHONUNBUFFERED": "1",
            "TORCH_EXTENSIONS_DIR": str(torch_extensions_dir),
        }
    )
    return environment


def _python_executable() -> str:
    executable = Path(sys.executable)
    if os.name == "nt":
        base = Path(getattr(sys, "_base_executable", sys.executable))
        if base.is_file():
            executable = base
    return str(executable)


def _load_rank_summary(run_root: Path, relative: str) -> DeepSpeedRankSummary:
    try:
        path = PathSandbox.create(run_root).resolve_relative(relative, must_exist=True)
        return DeepSpeedRankSummary.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise DeepSpeedQualificationError(f"invalid DeepSpeed rank summary: {relative}") from error


def _launch_phase(
    *,
    phase: str,
    run_root: Path,
    workload_profile: str,
    checkpoint_step: int,
    checkpoint_tag: str,
    timeout_seconds: float,
    torch_extensions_dir: Path,
    temporary_checkpoint_relative: str | None = None,
    checkpoint_relative: str | None = None,
) -> tuple[DistributedPhaseProcessEvidence, tuple[DeepSpeedRankSummary, ...]]:
    rendezvous = run_root / "rendezvous" / f"{phase}-{uuid.uuid4().hex}.store"
    rendezvous.parent.mkdir(parents=True, exist_ok=True)
    init_method = rendezvous.resolve().as_uri()
    processes: list[subprocess.Popen[str]] = []
    starts: list[datetime] = []
    outputs: list[str] = []
    for rank in range(2):
        output = f"phases/{phase}/rank-{rank:03d}.json"
        command = (
            _python_executable(),
            "-m",
            "flashpilot.deepspeed.worker",
            "--mode",
            phase,
            "--rank",
            str(rank),
            "--world-size",
            "2",
            "--backend",
            "gloo",
            "--zero-stage",
            "2",
            "--init-method",
            init_method,
            "--run-root",
            str(run_root),
            "--workload-profile",
            workload_profile,
            "--checkpoint-step",
            str(checkpoint_step),
            "--checkpoint-tag",
            checkpoint_tag,
            "--output",
            output,
        )
        if temporary_checkpoint_relative is not None:
            command += ("--temporary-checkpoint", temporary_checkpoint_relative)
        if checkpoint_relative is not None:
            command += ("--checkpoint", checkpoint_relative)
        starts.append(datetime.now(UTC))
        processes.append(
            subprocess.Popen(
                command,
                cwd=run_root,
                env=_environment(
                    seed=get_profile(workload_profile).global_seed,
                    torch_extensions_dir=torch_extensions_dir,
                ),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
            )
        )
        outputs.append(output)

    deadline = time.monotonic() + timeout_seconds
    timed_out = False
    while any(process.poll() is None for process in processes):
        if time.monotonic() >= deadline:
            timed_out = True
            for process in processes:
                if process.poll() is None:
                    process.kill()
            break
        time.sleep(0.05)
    completed_at = datetime.now(UTC)
    process_evidence: list[DistributedRankProcessEvidence] = []
    failures: list[str] = []
    for rank, process in enumerate(processes):
        stdout, stderr = process.communicate(timeout=10)
        write_text_artifact(
            run_root=run_root,
            relative_path=f"logs/{phase}.rank-{rank:03d}.stdout.log",
            text=stdout,
        )
        write_text_artifact(
            run_root=run_root,
            relative_path=f"logs/{phase}.rank-{rank:03d}.stderr.log",
            text=stderr,
        )
        if process.returncode != 0:
            failures.append(f"rank {rank} exit {process.returncode}")
        else:
            process_evidence.append(
                DistributedRankProcessEvidence(
                    rank=rank,
                    worker_pid=process.pid,
                    started_at=starts[rank],
                    completed_at=completed_at,
                )
            )
    if rendezvous.exists():
        rendezvous.unlink()
    if timed_out:
        raise DeepSpeedQualificationError(f"{phase} DeepSpeed rank group timed out")
    if failures:
        raise DeepSpeedQualificationError(
            f"{phase} DeepSpeed rank group failed ({', '.join(failures)}); see logs"
        )
    evidence = DistributedPhaseProcessEvidence(
        phase=phase,
        ranks=tuple(process_evidence),
    )
    summaries = tuple(_load_rank_summary(run_root, relative) for relative in outputs)
    for rank, summary in enumerate(summaries):
        if (
            summary.rank != rank
            or summary.phase != phase
            or summary.worker_pid != processes[rank].pid
        ):
            raise DeepSpeedQualificationError(
                "DeepSpeed rank summary identity differs from launched process"
            )
    return evidence, summaries


def _load_checkpoint_event(run_root: Path) -> DeepSpeedCheckpointEvent:
    try:
        path = PathSandbox.create(run_root).resolve_relative(
            "checkpoint-event.json", must_exist=True
        )
        return DeepSpeedCheckpointEvent.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise DeepSpeedQualificationError("invalid DeepSpeed checkpoint event") from error


def _launch_fault_phase(
    *,
    run_root: Path,
    workload_profile: str,
    checkpoint_step: int,
    checkpoint_tag: str,
    checkpoint_relative: str,
    target_rank: int,
    timeout_seconds: float,
    torch_extensions_dir: Path,
) -> MultiRankFailureEvent:
    rendezvous = run_root / "rendezvous" / f"fault-{uuid.uuid4().hex}.store"
    rendezvous.parent.mkdir(parents=True, exist_ok=True)
    init_method = rendezvous.resolve().as_uri()
    ready_paths = tuple(f"phases/fault/rank-{rank:03d}.ready.json" for rank in range(2))
    peer_paths = tuple(f"phases/fault/rank-{rank:03d}.peer-failure.json" for rank in range(2))
    commands = []
    environments = []
    for rank in range(2):
        commands.append(
            (
                _python_executable(),
                "-m",
                "flashpilot.deepspeed.worker",
                "--mode",
                "fault",
                "--rank",
                str(rank),
                "--world-size",
                "2",
                "--backend",
                "gloo",
                "--zero-stage",
                "2",
                "--init-method",
                init_method,
                "--run-root",
                str(run_root),
                "--workload-profile",
                workload_profile,
                "--checkpoint-step",
                str(checkpoint_step),
                "--checkpoint-tag",
                checkpoint_tag,
                "--checkpoint",
                checkpoint_relative,
                "--fault-target-rank",
                str(target_rank),
                "--output",
                ready_paths[rank],
                "--peer-failure-output",
                peer_paths[rank],
            )
        )
        environments.append(
            _environment(
                seed=get_profile(workload_profile).global_seed,
                torch_extensions_dir=torch_extensions_dir,
            )
        )
    try:
        return run_targeted_rank_termination(
            run_root=run_root,
            commands=(commands[0], commands[1]),
            environments=(environments[0], environments[1]),
            ready_paths=(ready_paths[0], ready_paths[1]),
            peer_failure_paths=(peer_paths[0], peer_paths[1]),
            log_stem="fault",
            framework="deepspeed",
            adapter="deepspeed-engine",
            strategy="zero",
            implementation="zero-stage-2",
            zero_stage=2,
            checkpoint_path=checkpoint_relative,
            checkpoint_id=f"checkpoint-step-{checkpoint_step:06d}",
            checkpoint_tag=checkpoint_tag,
            checkpoint_step=checkpoint_step,
            target_rank=target_rank,
            timeout_seconds=timeout_seconds,
        )
    except MultiRankFailureError as error:
        raise DeepSpeedQualificationError(str(error)) from error
    finally:
        if rendezvous.exists():
            rendezvous.unlink()


def run_deepspeed_qualification(
    *,
    run_root: Path,
    workload_profile: str = "ci",
    world_size: int = 2,
    zero_stage: int = 2,
    backend: str = "gloo",
    fault: str = "checkpoint-restart",
    target_rank: int | None = None,
    timeout_seconds: float = 300.0,
) -> DeepSpeedQualificationResult:
    """Prove exact ZeRO-2 restart, optionally after a targeted rank failure."""

    if world_size != 2 or zero_stage != 2 or backend != "gloo":
        raise DeepSpeedUnsupportedConfigurationError(
            "supported DeepSpeed contract is zero_stage=2, backend=gloo, world_size=2"
        )
    if fault not in {"checkpoint-restart", "rank-termination"}:
        raise DeepSpeedUnsupportedConfigurationError(
            "supported DeepSpeed faults are checkpoint-restart and rank-termination"
        )
    if (fault == "rank-termination") != (target_rank in (0, 1)):
        raise DeepSpeedUnsupportedConfigurationError(
            "rank-termination requires target_rank=0 or target_rank=1; clean restart forbids it"
        )
    _require_deepspeed()
    profile = get_profile(workload_profile)
    checkpoint_step = profile.steps // 2
    if run_root.exists() and any(run_root.iterdir()):
        raise DeepSpeedUnsupportedConfigurationError(
            "DeepSpeed qualification requires a new or empty run directory"
        )
    sandbox = PathSandbox.create(run_root)
    checkpoint_root = sandbox.resolve_relative("checkpoints")
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    checkpoint_id = f"checkpoint-step-{checkpoint_step:06d}"
    checkpoint_tag = f"global_step{checkpoint_step:06d}"
    temporary_relative = f"checkpoints/.{checkpoint_id}.tmp-{uuid.uuid4().hex}"
    temporary_checkpoint = sandbox.resolve_relative(temporary_relative)
    temporary_checkpoint.mkdir()
    checkpoint_relative = f"checkpoints/{checkpoint_id}"

    with tempfile.TemporaryDirectory(prefix="flashpilot-deepspeed-") as extension_root:
        torch_extensions_dir = Path(extension_root)
        control_processes, control = _launch_phase(
            phase="control",
            run_root=sandbox.root,
            workload_profile=workload_profile,
            checkpoint_step=checkpoint_step,
            checkpoint_tag=checkpoint_tag,
            timeout_seconds=timeout_seconds,
            torch_extensions_dir=torch_extensions_dir,
        )
        checkpoint_processes, checkpoint = _launch_phase(
            phase="checkpoint",
            run_root=sandbox.root,
            workload_profile=workload_profile,
            checkpoint_step=checkpoint_step,
            checkpoint_tag=checkpoint_tag,
            timeout_seconds=timeout_seconds,
            torch_extensions_dir=torch_extensions_dir,
            temporary_checkpoint_relative=temporary_relative,
        )
        checkpoint_event = _load_checkpoint_event(sandbox.root)
        checkpoint_path = sandbox.resolve_relative(checkpoint_relative, must_exist=True)
        validated = validate_deepspeed_checkpoint(
            run_root=sandbox.root,
            checkpoint_path=checkpoint_path,
        )
        failure_event = None
        if fault == "rank-termination":
            assert target_rank is not None
            failure_event = _launch_fault_phase(
                run_root=sandbox.root,
                workload_profile=workload_profile,
                checkpoint_step=checkpoint_step,
                checkpoint_tag=checkpoint_tag,
                checkpoint_relative=checkpoint_relative,
                target_rank=target_rank,
                timeout_seconds=timeout_seconds,
                torch_extensions_dir=torch_extensions_dir,
            )
        recovery_processes, recovery = _launch_phase(
            phase="recovery",
            run_root=sandbox.root,
            workload_profile=workload_profile,
            checkpoint_step=checkpoint_step,
            checkpoint_tag=checkpoint_tag,
            timeout_seconds=timeout_seconds,
            torch_extensions_dir=torch_extensions_dir,
            checkpoint_relative=checkpoint_relative,
        )
    recovery_rto = (
        max(item.completed_at for item in recovery_processes.ranks)
        - min(item.started_at for item in recovery_processes.ranks)
    ).total_seconds()
    base_gate = evaluate_deepspeed_recovery_gate(
        control_processes=control_processes,
        control=control,
        checkpoint_processes=checkpoint_processes,
        checkpoint=checkpoint,
        recovery_processes=recovery_processes,
        recovery=recovery,
        checkpoint_event=checkpoint_event,
        validated_checkpoint=validated,
        checkpoint_step=checkpoint_step,
        total_steps=profile.steps,
    )
    gate = base_gate
    if failure_event is not None:
        existing_phase_pids = tuple(
            item.worker_pid
            for phase in (control_processes, checkpoint_processes, recovery_processes)
            for item in phase.ranks
        )
        fault_checks = evaluate_multi_rank_failure_checks(
            event=failure_event,
            expected_framework="deepspeed",
            expected_target_rank=target_rank,
            expected_checkpoint_path=checkpoint_relative,
            expected_checkpoint_step=checkpoint_step,
            existing_phase_pids=existing_phase_pids,
            recovery_started_at=min(item.started_at for item in recovery_processes.ranks),
        )
        checks = base_gate.checks + fault_checks
        failed = tuple(check.check_id for check in checks if check.status == "fail")
        gate = DeepSpeedRecoveryGateV1(
            passed=not failed,
            checks=checks,
            failed_check_ids=failed,
        )
    result = DeepSpeedQualificationResult(
        run_id=uuid.uuid4().hex,
        created_at=datetime.now(UTC),
        workload_profile=workload_profile,
        fault_scenario=(
            "rank_process_termination" if failure_event is not None else "checkpoint_restart"
        ),
        fault_target_rank=target_rank,
        failure_event=failure_event,
        control_processes=control_processes,
        control=control,
        checkpoint_processes=checkpoint_processes,
        checkpoint=checkpoint,
        checkpoint_event=checkpoint_event,
        checkpoint_manifest=validated.manifest,
        checkpoint_inventory=validated.inventory,
        recovery_processes=recovery_processes,
        recovery=recovery,
        recovery_rto_seconds=recovery_rto,
        gate=gate,
        final_verdict="VERIFIED" if gate.passed else "FAILED",
        verified_persisted_bytes=validated.logical_bytes if gate.passed else None,
        limitations=(
            "Qualification covers the included deterministic CPU workload at world size 2.",
            "Recovery uses the same world size; universal or elastic checkpoints are not qualified.",
            "Gloo file-store rendezvous is local and does not qualify network filesystems.",
            (
                "Qualification performs one parent-owned rank termination at a committed "
                "zero-RPO boundary."
                if failure_event is not None
                else "Qualification performs a clean checkpoint restart without fault injection."
            ),
            "Elastic or universal recovery, world-size changes, and job-manager retries are not qualified.",
            "DeepSpeed qualification is Linux-only; Windows fails closed before worker launch.",
            "The attestation remains unsigned until the later signing milestone.",
        ),
    )
    write_json_artifact(run_root=sandbox.root, relative_path="result.json", value=result)
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.md",
        text=render_deepspeed_markdown(result),
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.html",
        text=render_deepspeed_html(result),
    )
    from flashpilot.ci.service import write_qualification_ci_outputs

    write_qualification_ci_outputs(run_root=sandbox.root, result=result)
    if result.final_verdict == "VERIFIED":
        from flashpilot.attestation.builder import emit_deepspeed_recovery_attestation

        emit_deepspeed_recovery_attestation(run_root=sandbox.root, result=result)
    return result
