"""Bounded parent harness for real two-rank FSDP checkpoint qualification."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from flashpilot.distributed.checkpoint import validate_distributed_checkpoint
from flashpilot.distributed.gate import evaluate_distributed_recovery_gate
from flashpilot.distributed.models import (
    DistributedCheckpointEvent,
    DistributedPhaseProcessEvidence,
    DistributedQualificationResult,
    DistributedRankProcessEvidence,
    DistributedRankSummary,
)
from flashpilot.distributed.reporting import render_distributed_html, render_distributed_markdown
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.workload.profiles import get_profile


class DistributedQualificationError(RuntimeError):
    """The distributed qualification could not produce trustworthy evidence."""


class DistributedUnsupportedConfigurationError(DistributedQualificationError):
    """The selected distributed configuration is outside the supported contract."""


def _environment(seed: int) -> dict[str, str]:
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
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "OMP_NUM_THREADS": "1",
            "PYTHONHASHSEED": str(seed),
            "PYTHONPATH": os.pathsep.join(python_paths),
            "PYTHONUNBUFFERED": "1",
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


def _load_rank_summary(run_root: Path, relative: str) -> DistributedRankSummary:
    try:
        path = PathSandbox.create(run_root).resolve_relative(relative, must_exist=True)
        return DistributedRankSummary.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise DistributedQualificationError(
            f"invalid distributed rank summary: {relative}"
        ) from error


def _launch_phase(
    *,
    phase: str,
    run_root: Path,
    workload_profile: str,
    checkpoint_step: int,
    timeout_seconds: float,
    temporary_checkpoint_relative: str | None = None,
    checkpoint_relative: str | None = None,
) -> tuple[DistributedPhaseProcessEvidence, tuple[DistributedRankSummary, ...]]:
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
            "flashpilot.distributed.worker",
            "--mode",
            phase,
            "--rank",
            str(rank),
            "--world-size",
            "2",
            "--backend",
            "gloo",
            "--init-method",
            init_method,
            "--run-root",
            str(run_root),
            "--workload-profile",
            workload_profile,
            "--checkpoint-step",
            str(checkpoint_step),
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
                env=_environment(get_profile(workload_profile).global_seed),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
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
        time.sleep(0.02)
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
        raise DistributedQualificationError(f"{phase} rank group timed out")
    if failures:
        raise DistributedQualificationError(
            f"{phase} rank group failed ({', '.join(failures)}); see logs"
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
            raise DistributedQualificationError(
                "rank summary identity differs from launched process"
            )
    return evidence, summaries


def _load_checkpoint_event(run_root: Path) -> DistributedCheckpointEvent:
    try:
        path = PathSandbox.create(run_root).resolve_relative(
            "checkpoint-event.json", must_exist=True
        )
        return DistributedCheckpointEvent.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise DistributedQualificationError("invalid distributed checkpoint event") from error


def run_distributed_qualification(
    *,
    run_root: Path,
    workload_profile: str = "ci",
    world_size: int = 2,
    strategy: str = "fsdp",
    backend: str = "gloo",
    timeout_seconds: float = 120.0,
) -> DistributedQualificationResult:
    """Prove exact two-rank FSDP checkpoint restart without injecting failure."""

    if world_size != 2 or strategy != "fsdp" or backend != "gloo":
        raise DistributedUnsupportedConfigurationError(
            "supported distributed contract is strategy=fsdp, backend=gloo, world_size=2"
        )
    profile = get_profile(workload_profile)
    checkpoint_step = profile.steps // 2
    if run_root.exists() and any(run_root.iterdir()):
        raise DistributedUnsupportedConfigurationError(
            "distributed qualification requires a new or empty run directory"
        )
    sandbox = PathSandbox.create(run_root)
    checkpoint_root = sandbox.resolve_relative("checkpoints")
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    checkpoint_id = f"checkpoint-step-{checkpoint_step:06d}"
    temporary_relative = f"checkpoints/.{checkpoint_id}.tmp-{uuid.uuid4().hex}"
    temporary_checkpoint = sandbox.resolve_relative(temporary_relative)
    temporary_checkpoint.mkdir()
    checkpoint_relative = f"checkpoints/{checkpoint_id}"

    control_processes, control = _launch_phase(
        phase="control",
        run_root=sandbox.root,
        workload_profile=workload_profile,
        checkpoint_step=checkpoint_step,
        timeout_seconds=timeout_seconds,
    )
    checkpoint_processes, checkpoint = _launch_phase(
        phase="checkpoint",
        run_root=sandbox.root,
        workload_profile=workload_profile,
        checkpoint_step=checkpoint_step,
        timeout_seconds=timeout_seconds,
        temporary_checkpoint_relative=temporary_relative,
    )
    checkpoint_event = _load_checkpoint_event(sandbox.root)
    checkpoint_path = sandbox.resolve_relative(checkpoint_relative, must_exist=True)
    validated = validate_distributed_checkpoint(
        run_root=sandbox.root,
        checkpoint_path=checkpoint_path,
    )
    recovery_processes, recovery = _launch_phase(
        phase="recovery",
        run_root=sandbox.root,
        workload_profile=workload_profile,
        checkpoint_step=checkpoint_step,
        timeout_seconds=timeout_seconds,
        checkpoint_relative=checkpoint_relative,
    )
    recovery_rto = (
        max(item.completed_at for item in recovery_processes.ranks)
        - min(item.started_at for item in recovery_processes.ranks)
    ).total_seconds()
    gate = evaluate_distributed_recovery_gate(
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
    result = DistributedQualificationResult(
        run_id=uuid.uuid4().hex,
        created_at=datetime.now(UTC),
        workload_profile=workload_profile,
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
            "Recovery uses the same world size; elastic resharding is not qualified here.",
            "Gloo file-store rendezvous is local and does not qualify network filesystems.",
            "This milestone performs a clean checkpoint restart, not a multi-rank failure.",
            "The attestation remains unsigned until the later signing milestone.",
        ),
    )
    write_json_artifact(run_root=sandbox.root, relative_path="result.json", value=result)
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.md",
        text=render_distributed_markdown(result),
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.html",
        text=render_distributed_html(result),
    )
    from flashpilot.ci.service import write_qualification_ci_outputs

    write_qualification_ci_outputs(run_root=sandbox.root, result=result)
    if result.final_verdict == "VERIFIED":
        from flashpilot.attestation.builder import emit_distributed_recovery_attestation

        emit_distributed_recovery_attestation(run_root=sandbox.root, result=result)
    return result
