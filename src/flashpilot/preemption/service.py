"""POSIX SIGTERM preemption certification for the narrow HF Trainer workload."""

from __future__ import annotations

import os
import queue
import signal
import subprocess
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from flashpilot.adapters.huggingface import HuggingFaceTrainerAdapter
from flashpilot.checkpoints.integrity import logical_directory_bytes
from flashpilot.hf.example import (
    HF_BATCH_SIZE,
    HF_CHECKPOINT_STEP,
    HF_SEED,
    HF_SEQUENCE_LENGTH,
    HF_TOTAL_STEPS,
)
from flashpilot.hf.models import HFProcessEvidence
from flashpilot.hf.qualification import (
    HFUnsupportedConfigurationError,
    _copy_script,
    _environment,
    _load_summary,
    _python_executable,
    _read_lines,
    _run_to_completion,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.preemption.gate import evaluate_preemption_gate
from flashpilot.preemption.models import (
    PREEMPTION_INCOMPLETE_MARKER,
    HFPreemptionCertificationResult,
    HFPreemptionCommitEvidence,
    HFPreemptionReadyEvidence,
)
from flashpilot.preemption.reporting import render_preemption_html, render_preemption_markdown
from flashpilot.security.paths import PathSandbox


class PreemptionCertificationError(RuntimeError):
    """Managed preemption could not produce trustworthy verified evidence."""


class PreemptionUnsupportedError(PreemptionCertificationError):
    """The requested signal/platform/framework combination is unsupported."""


def supports_posix_sigterm() -> bool:
    """Return whether an external POSIX SIGTERM can be delivered truthfully."""

    return os.name == "posix" and hasattr(signal, "SIGTERM")


def _parse_events(
    lines: list[str],
) -> tuple[HFPreemptionReadyEvidence | None, HFPreemptionCommitEvidence | None]:
    ready: HFPreemptionReadyEvidence | None = None
    commit: HFPreemptionCommitEvidence | None = None
    for line in lines:
        try:
            candidate_ready = HFPreemptionReadyEvidence.model_validate_json(line)
        except ValidationError:
            candidate_ready = None
        if candidate_ready is not None:
            if ready is not None and ready != candidate_ready:
                raise PreemptionCertificationError("worker emitted conflicting ready evidence")
            ready = candidate_ready
            continue
        try:
            candidate_commit = HFPreemptionCommitEvidence.model_validate_json(line)
        except ValidationError:
            continue
        if commit is not None and commit != candidate_commit:
            raise PreemptionCertificationError("worker emitted conflicting commit evidence")
        commit = candidate_commit
    return ready, commit


def _read_stderr(stream: TextIO, lines: list[str]) -> None:
    lines.extend(stream.readlines())


def _run_and_sigterm(
    *,
    command: tuple[str, ...],
    run_root: Path,
    startup_timeout_seconds: float,
    grace_period_seconds: int,
    seed: int,
) -> tuple[
    HFProcessEvidence,
    HFPreemptionReadyEvidence,
    datetime,
    HFPreemptionCommitEvidence,
    float,
    float,
]:
    started_at = datetime.now(UTC)
    process = subprocess.Popen(
        command,
        cwd=run_root,
        env=_environment(seed),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1,
        shell=False,
    )
    if process.stdout is None or process.stderr is None:
        raise PreemptionCertificationError("preemption worker output was not captured")
    output: queue.Queue[str | None] = queue.Queue()
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    stdout_reader = threading.Thread(target=_read_lines, args=(process.stdout, output), daemon=True)
    stderr_reader = threading.Thread(
        target=_read_stderr,
        args=(process.stderr, stderr_lines),
        daemon=True,
    )
    stdout_reader.start()
    stderr_reader.start()
    signal_sent_at: datetime | None = None
    signal_sent_monotonic: float | None = None
    graceful_exit_seconds: float | None = None
    completed_at: datetime | None = None
    try:
        startup_deadline = time.monotonic() + startup_timeout_seconds
        ready: HFPreemptionReadyEvidence | None = None
        while time.monotonic() < startup_deadline:
            try:
                line = output.get(timeout=min(0.1, max(0.01, startup_deadline - time.monotonic())))
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if line is None:
                break
            stdout_lines.append(line)
            ready, _ = _parse_events(stdout_lines)
            if ready is not None:
                break
        if ready is None:
            raise PreemptionCertificationError("worker did not become ready for SIGTERM")
        if ready.worker_pid != process.pid:
            raise PreemptionCertificationError("preemption-ready PID differs from worker PID")
        signal_sent_at = datetime.now(UTC)
        signal_sent_monotonic = time.monotonic()
        os.kill(process.pid, signal.SIGTERM)
        grace_deadline = signal_sent_monotonic + float(grace_period_seconds)
        while process.poll() is None and time.monotonic() < grace_deadline:
            try:
                line = output.get(timeout=min(0.05, max(0.01, grace_deadline - time.monotonic())))
            except queue.Empty:
                continue
            if line is not None:
                stdout_lines.append(line)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=startup_timeout_seconds)
            raise PreemptionCertificationError(
                "preemption worker exceeded the grace period and was force-killed"
            )
        exit_code = process.wait(timeout=startup_timeout_seconds)
        graceful_exit_seconds = time.monotonic() - signal_sent_monotonic
        completed_at = datetime.now(UTC)
        stdout_reader.join(timeout=5)
        stderr_reader.join(timeout=5)
        while True:
            try:
                line = output.get_nowait()
            except queue.Empty:
                break
            if line is not None:
                stdout_lines.append(line)
        parsed_ready, commit = _parse_events(stdout_lines)
        if parsed_ready != ready:
            raise PreemptionCertificationError("preemption-ready evidence changed after delivery")
        if commit is None:
            raise PreemptionCertificationError("worker exited without checkpoint commit evidence")
        if commit.worker_pid != process.pid:
            raise PreemptionCertificationError("preemption commit PID differs from worker PID")
        if exit_code != 0:
            raise PreemptionCertificationError(
                f"preemption worker failed with exit code {exit_code}; see logs/preemption.stderr.log"
            )
        checkpoint_commit_seconds = (
            commit.checkpoint_committed_at - signal_sent_at
        ).total_seconds()
        if checkpoint_commit_seconds < 0:
            raise PreemptionCertificationError("checkpoint commit predates parent signal delivery")
        return (
            HFProcessEvidence(
                worker_pid=process.pid,
                started_at=started_at,
                completed_at=completed_at,
                exit_code=exit_code,
                exit_verified=True,
            ),
            ready,
            signal_sent_at,
            commit,
            checkpoint_commit_seconds,
            graceful_exit_seconds,
        )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=startup_timeout_seconds)
        stdout_reader.join(timeout=5)
        stderr_reader.join(timeout=5)
        while True:
            try:
                line = output.get_nowait()
            except queue.Empty:
                break
            if line is not None:
                stdout_lines.append(line)
        write_text_artifact(
            run_root=run_root,
            relative_path="logs/preemption.stdout.log",
            text="".join(stdout_lines),
        )
        write_text_artifact(
            run_root=run_root,
            relative_path="logs/preemption.stderr.log",
            text="".join(stderr_lines),
        )


def run_hf_preemption_certification(
    *,
    script_path: Path,
    run_root: Path,
    signal_name: str = "SIGTERM",
    grace_period_seconds: int = 300,
    forwarded_arguments: tuple[str, ...] = (),
    preemption_step: int = HF_CHECKPOINT_STEP,
    total_steps: int = HF_TOTAL_STEPS,
    seed: int = HF_SEED,
    startup_timeout_seconds: float = 120.0,
) -> HFPreemptionCertificationResult:
    """Certify one real POSIX SIGTERM, checkpoint commit, and exact resume."""

    if signal_name != "SIGTERM":
        raise PreemptionUnsupportedError("only the exact SIGTERM signal is supported")
    if not supports_posix_sigterm():
        raise PreemptionUnsupportedError(
            "SIGTERM preemption certification requires a POSIX host; Windows "
            "TerminateProcess is not equivalent"
        )
    if not 1 <= grace_period_seconds <= 3_600:
        raise ValueError("grace period must be between 1 and 3600 seconds")
    if preemption_step <= 0 or total_steps <= preemption_step:
        raise ValueError("preemption step must be positive and precede total steps")
    if run_root.exists() and (not run_root.is_dir() or any(run_root.iterdir())):
        raise HFUnsupportedConfigurationError(
            "preemption certification requires a new or empty run directory"
        )
    sandbox = PathSandbox.create(run_root)
    adapter = HuggingFaceTrainerAdapter()
    adapter.dependency_versions()
    forwarded = adapter.validate_forwarded_arguments(forwarded_arguments)
    owned_script, owned_script_relative = _copy_script(source=script_path, run_root=sandbox.root)

    control_result = "control/result.json"
    control_command = adapter.worker_command(
        python_executable=_python_executable(),
        script_path=owned_script,
        mode="control",
        run_root=sandbox.root,
        scenario="complete",
        checkpoint_step=preemption_step,
        total_steps=total_steps,
        seed=seed,
        result_path=control_result,
        forwarded_arguments=forwarded,
    )
    control_process = _run_to_completion(
        command=control_command,
        run_root=sandbox.root,
        log_stem="control",
        timeout_seconds=startup_timeout_seconds,
        seed=seed,
    )
    control = _load_summary(sandbox.root, control_result)

    preemption_command = adapter.worker_command(
        python_executable=_python_executable(),
        script_path=owned_script,
        mode="preempt",
        run_root=sandbox.root,
        scenario="complete",
        checkpoint_step=preemption_step,
        total_steps=total_steps,
        seed=seed,
        result_path="preemption/unused-result.json",
        grace_period_seconds=grace_period_seconds,
        forwarded_arguments=forwarded,
    )
    (
        preemption_process,
        ready_event,
        signal_sent_at,
        commit_event,
        checkpoint_commit_seconds,
        graceful_exit_seconds,
    ) = _run_and_sigterm(
        command=preemption_command,
        run_root=sandbox.root,
        startup_timeout_seconds=startup_timeout_seconds,
        grace_period_seconds=grace_period_seconds,
        seed=seed,
    )
    persisted_commit_path = sandbox.resolve_relative("preemption/commit.json", must_exist=True)
    try:
        persisted_commit = HFPreemptionCommitEvidence.model_validate_json(
            persisted_commit_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValidationError) as error:
        raise PreemptionCertificationError("persisted preemption commit is invalid") from error
    if persisted_commit != commit_event:
        raise PreemptionCertificationError("persisted and streamed commit evidence differ")
    incomplete_marker_absent = not sandbox.resolve_relative(PREEMPTION_INCOMPLETE_MARKER).exists()
    checkpoint = sandbox.resolve_relative(
        commit_event.checkpoint.checkpoint_path,
        must_exist=True,
    )
    inventory = adapter.checkpoint_inventory(checkpoint)

    recovery_result = "recovery/result.json"
    recovery_command = adapter.worker_command(
        python_executable=_python_executable(),
        script_path=owned_script,
        mode="recover",
        run_root=sandbox.root,
        scenario="complete",
        checkpoint_step=preemption_step,
        total_steps=total_steps,
        seed=seed,
        result_path=recovery_result,
        checkpoint_path=commit_event.checkpoint.checkpoint_path,
        forwarded_arguments=forwarded,
    )
    recovery_process = _run_to_completion(
        command=recovery_command,
        run_root=sandbox.root,
        log_stem="recovery",
        timeout_seconds=startup_timeout_seconds,
        seed=seed,
    )
    recovery = _load_summary(sandbox.root, recovery_result)
    tokens_per_step = HF_BATCH_SIZE * HF_SEQUENCE_LENGTH
    gate = evaluate_preemption_gate(
        control=control,
        recovery=recovery,
        preemption_process=preemption_process,
        recovery_process=recovery_process,
        ready=ready_event,
        signal_sent_at=signal_sent_at,
        commit=commit_event,
        incomplete_marker_absent=incomplete_marker_absent,
        checkpoint_commit_seconds=checkpoint_commit_seconds,
        graceful_exit_seconds=graceful_exit_seconds,
        grace_period_seconds=grace_period_seconds,
        total_steps=total_steps,
        tokens_per_step=tokens_per_step,
    )
    verified_bytes = logical_directory_bytes(checkpoint) if gate.passed else None
    result = HFPreemptionCertificationResult(
        run_id=uuid.uuid4().hex,
        created_at=datetime.now(UTC),
        grace_period_seconds=grace_period_seconds,
        preemption_step=preemption_step,
        total_steps=total_steps,
        tokens_per_step=tokens_per_step,
        script_path=owned_script_relative,
        forwarded_arguments=forwarded,
        control_process=control_process,
        control=control,
        preemption_process=preemption_process,
        ready_event=ready_event,
        signal_sent_at=signal_sent_at,
        commit_event=commit_event,
        checkpoint_inventory=inventory,
        checkpoint_commit_seconds=checkpoint_commit_seconds,
        graceful_exit_seconds=graceful_exit_seconds,
        recovery_process=recovery_process,
        recovery=recovery,
        recovery_rto_seconds=(
            recovery_process.completed_at - recovery_process.started_at
        ).total_seconds(),
        gate=gate,
        final_verdict="VERIFIED" if gate.passed else "FAILED",
        verified_persisted_bytes=verified_bytes,
        limitations=(
            "Certification covers one local POSIX SIGTERM and the included CPU Trainer workload.",
            "Kubernetes, Slurm, and cloud-provider control planes are not invoked by this local run.",
            "The attestation is unsigned and provides integrity, not publisher authentication.",
        ),
    )
    write_json_artifact(run_root=sandbox.root, relative_path=result.result_path, value=result)
    write_text_artifact(
        run_root=sandbox.root,
        relative_path=result.report_path,
        text=render_preemption_markdown(result),
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path=result.html_report_path,
        text=render_preemption_html(result),
    )
    from flashpilot.ci.service import write_qualification_ci_outputs

    write_qualification_ci_outputs(run_root=sandbox.root, result=result)
    if result.final_verdict == "VERIFIED":
        from flashpilot.attestation.builder import emit_hf_preemption_attestation

        emit_hf_preemption_attestation(run_root=sandbox.root, result=result)
    return result
