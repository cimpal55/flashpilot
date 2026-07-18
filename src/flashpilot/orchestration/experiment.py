"""Parent-owned real process crash, recovery, gate, and artifact workflow."""

from __future__ import annotations

import os
import queue
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from flashpilot.checkpoints.loader import ValidatedCheckpoint, validate_checkpoint
from flashpilot.domain.recovery import (
    CheckpointCommittedEvent,
    CheckpointStrategy,
    CrashExperimentResult,
    CrashMetadata,
    RecoveryCompletedEvent,
    RecoveryProcessMetadata,
    RecoveryWorkerResult,
)
from flashpilot.domain.repair import CheckpointStrategyConfig
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.verification.failure_artifact import build_sanitized_failure_artifact
from flashpilot.verification.observations import snapshot_from_summary
from flashpilot.verification.recovery_gate import evaluate_recovery_gate
from flashpilot.workload.control import run_control
from flashpilot.workload.profiles import get_profile

_RECOVERY_OUTPUT = "workers/recovery-result.json"
_FAILURE_ARTIFACT = "agent/request.redacted.json"


class OrchestrationError(RuntimeError):
    """Raised when a worker violates the trusted process protocol."""


class WorkerProcessError(OrchestrationError):
    """A worker exited unsuccessfully before producing its required result."""

    def __init__(self, message: str, *, pid: int, exit_code: int | None, stderr: str) -> None:
        super().__init__(message)
        self.pid = pid
        self.exit_code = exit_code
        self.stderr = stderr


@dataclass(frozen=True, slots=True)
class CheckpointCrashPhase:
    event: CheckpointCommittedEvent
    checkpoint: ValidatedCheckpoint
    crash: CrashMetadata
    stderr_path: Path


@dataclass(frozen=True, slots=True)
class RecoveryPhase:
    process: RecoveryProcessMetadata
    result: RecoveryWorkerResult
    stderr_path: Path


def _worker_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in tuple(environment):
        normalized = key.upper()
        if normalized == "OPENAI_API_KEY" or normalized.endswith("_API_KEY"):
            environment.pop(key)
    source_root = Path(__file__).resolve().parents[2]
    python_paths = [str(source_root)]
    if os.name == "nt":
        venv_site_packages = Path(sys.prefix) / "Lib" / "site-packages"
        if venv_site_packages.is_dir():
            python_paths.append(str(venv_site_packages))
    existing_pythonpath = environment.get("PYTHONPATH")
    if existing_pythonpath:
        python_paths.append(existing_pythonpath)
    environment["PYTHONPATH"] = os.pathsep.join(python_paths)
    environment["PYTHONUNBUFFERED"] = "1"
    return environment


def _worker_command(*arguments: str) -> list[str]:
    executable = Path(sys.executable)
    if os.name == "nt":
        base_executable = Path(getattr(sys, "_base_executable", sys.executable))
        if base_executable.is_file():
            executable = base_executable
    return [str(executable), "-m", "flashpilot.orchestration.worker", *arguments]


def _stderr_path(run_root: Path, relative_path: str) -> Path:
    sandbox = PathSandbox.create(run_root)
    path = sandbox.resolve_relative(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_lines(stream: TextIO, output: queue.Queue[str | None]) -> None:
    try:
        for line in stream:
            output.put(line)
    finally:
        output.put(None)


def _read_stderr(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _wait_for_checkpoint_event(
    process: subprocess.Popen[str],
    *,
    stderr_path: Path,
    timeout_seconds: float,
) -> CheckpointCommittedEvent:
    if process.stdout is None:
        raise OrchestrationError("checkpoint worker stdout was not captured")
    output: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(target=_read_lines, args=(process.stdout, output), daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            line = output.get(timeout=min(0.1, max(0.01, deadline - time.monotonic())))
        except queue.Empty:
            if process.poll() is not None:
                raise WorkerProcessError(
                    f"checkpoint worker exited before commit event with code {process.returncode}",
                    pid=process.pid,
                    exit_code=process.returncode,
                    stderr=_read_stderr(stderr_path),
                ) from None
            continue
        if line is None:
            exit_code = process.poll()
            if exit_code is None:
                exit_code = process.wait(timeout=min(5.0, timeout_seconds))
            raise WorkerProcessError(
                f"checkpoint worker closed stdout before commit event with code {exit_code}",
                pid=process.pid,
                exit_code=exit_code,
                stderr=_read_stderr(stderr_path),
            )
        try:
            return CheckpointCommittedEvent.model_validate_json(line)
        except ValidationError as error:
            raise OrchestrationError("checkpoint worker emitted an invalid event") from error
    raise WorkerProcessError(
        "timed out waiting for checkpoint commit event",
        pid=process.pid,
        exit_code=process.poll(),
        stderr=_read_stderr(stderr_path),
    )


def _termination_method() -> str:
    if os.name == "nt":
        return "TerminateProcess via subprocess.Popen.kill"
    return "SIGKILL via subprocess.Popen.kill"


def _termination_is_expected(exit_code: int) -> bool:
    if os.name == "nt":
        return exit_code != 0
    return exit_code == -signal.SIGKILL


def run_checkpoint_crash_phase(
    *,
    profile_name: str,
    strategy: CheckpointStrategy,
    run_root: Path,
    checkpoint_step: int,
    post_commit_steps: int = 0,
    strategy_config_path: str | None = None,
    timeout_seconds: float = 60.0,
) -> CheckpointCrashPhase:
    """Start a worker, validate its committed path, then kill that exact process."""

    run_root = run_root.resolve()
    sandbox = PathSandbox.create(run_root)
    if strategy_config_path is not None:
        if strategy != "safe_adapter_aware":
            raise ValueError("a repaired strategy config requires safe_adapter_aware storage")
        config_path = sandbox.resolve_relative(strategy_config_path, must_exist=True)
        config = CheckpointStrategyConfig.model_validate_json(
            config_path.read_text(encoding="utf-8")
        )
        config.require_complete_training_state()
    stderr_path = _stderr_path(run_root, "logs/checkpoint-worker.stderr.log")
    command = _worker_command(
        "checkpoint",
        "--run-root",
        str(run_root),
        "--profile",
        profile_name,
        "--strategy",
        strategy,
        "--checkpoint-step",
        str(checkpoint_step),
        "--post-commit-steps",
        str(post_commit_steps),
    )
    if strategy_config_path is not None:
        command.extend(("--strategy-config", strategy_config_path))
    with stderr_path.open("x", encoding="utf-8", newline="\n") as stderr_stream:
        process = subprocess.Popen(
            command,
            cwd=run_root,
            env=_worker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=stderr_stream,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )
        event_validated = False
        try:
            event = _wait_for_checkpoint_event(
                process,
                stderr_path=stderr_path,
                timeout_seconds=timeout_seconds,
            )
            if event.worker_pid != process.pid:
                raise OrchestrationError("checkpoint event PID does not match the child process")
            checkpoint_path = sandbox.resolve_relative(
                event.checkpoint_path,
                must_exist=True,
            )
            checkpoint = validate_checkpoint(
                run_root=run_root,
                checkpoint_path=checkpoint_path,
            )
            if checkpoint.manifest.global_step != event.checkpoint_step:
                raise OrchestrationError("checkpoint event step does not match the manifest")
            if checkpoint.manifest.strategy != strategy:
                raise OrchestrationError("checkpoint event strategy does not match the manifest")
            event_received_at = datetime.now(UTC)
            event_validated = True
            process.kill()
            exit_code = process.wait(timeout=timeout_seconds)
            terminated_at = datetime.now(UTC)
            termination_verified = _termination_is_expected(exit_code)
            if not termination_verified:
                raise WorkerProcessError(
                    f"checkpoint worker termination returned unexpected code {exit_code}",
                    pid=process.pid,
                    exit_code=exit_code,
                    stderr=_read_stderr(stderr_path),
                )
            crash = CrashMetadata(
                worker_pid=process.pid,
                checkpoint_step=event.checkpoint_step,
                last_completed_step=event.last_completed_step,
                checkpoint_path=event.checkpoint_path,
                event_received_at=event_received_at,
                termination_method=_termination_method(),
                termination_exit_code=exit_code,
                termination_verified=True,
                terminated_at=terminated_at,
            )
            return CheckpointCrashPhase(
                event=event,
                checkpoint=checkpoint,
                crash=crash,
                stderr_path=stderr_path,
            )
        finally:
            if process.poll() is None:
                # Invalid events are never accepted as crash triggers; this is process cleanup.
                process.kill()
                process.wait(timeout=timeout_seconds)
            if process.stdout is not None:
                process.stdout.close()
            if not event_validated and process.returncode is None:
                raise OrchestrationError("checkpoint worker cleanup did not terminate the process")


def run_recovery_phase(
    *,
    profile_name: str,
    strategy: CheckpointStrategy,
    run_root: Path,
    checkpoint_path: str,
    strategy_config_path: str | None = None,
    timeout_seconds: float = 60.0,
) -> RecoveryPhase:
    """Launch a new worker process and require a successful contained result."""

    run_root = run_root.resolve()
    sandbox = PathSandbox.create(run_root)
    sandbox.resolve_relative(checkpoint_path, must_exist=True)
    if strategy_config_path is not None:
        if strategy != "safe_adapter_aware":
            raise ValueError("a repaired strategy config requires safe_adapter_aware storage")
        config_path = sandbox.resolve_relative(strategy_config_path, must_exist=True)
        config = CheckpointStrategyConfig.model_validate_json(
            config_path.read_text(encoding="utf-8")
        )
        config.require_complete_training_state()
    output_path = sandbox.resolve_relative(_RECOVERY_OUTPUT)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path = _stderr_path(run_root, "logs/recovery-worker.stderr.log")
    command = _worker_command(
        "recover",
        "--run-root",
        str(run_root),
        "--profile",
        profile_name,
        "--strategy",
        strategy,
        "--checkpoint-path",
        checkpoint_path,
        "--output-path",
        _RECOVERY_OUTPUT,
    )
    if strategy_config_path is not None:
        command.extend(("--strategy-config", strategy_config_path))
    started_at = datetime.now(UTC)
    with stderr_path.open("x", encoding="utf-8", newline="\n") as stderr_stream:
        process = subprocess.Popen(
            command,
            cwd=run_root,
            env=_worker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=stderr_stream,
            text=True,
            encoding="utf-8",
        )
        try:
            stdout, _ = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as error:
            process.kill()
            process.wait(timeout=timeout_seconds)
            raise WorkerProcessError(
                "recovery worker timed out",
                pid=process.pid,
                exit_code=process.returncode,
                stderr=_read_stderr(stderr_path),
            ) from error
    completed_at = datetime.now(UTC)
    exit_code = process.returncode
    if exit_code != 0:
        raise WorkerProcessError(
            f"recovery worker failed with code {exit_code}",
            pid=process.pid,
            exit_code=exit_code,
            stderr=_read_stderr(stderr_path),
        )
    try:
        completed_event = RecoveryCompletedEvent.model_validate_json(stdout.strip())
    except ValidationError as error:
        raise OrchestrationError("recovery worker emitted an invalid completion event") from error
    if completed_event.worker_pid != process.pid or completed_event.output_path != _RECOVERY_OUTPUT:
        raise OrchestrationError("recovery completion event does not match the child process")
    try:
        result = RecoveryWorkerResult.model_validate_json(
            sandbox.resolve_relative(_RECOVERY_OUTPUT, must_exist=True).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValidationError) as error:
        raise OrchestrationError("recovery worker result is missing or invalid") from error
    if result.worker_pid != process.pid or result.checkpoint_path != checkpoint_path:
        raise OrchestrationError("recovery result does not match the child process or checkpoint")
    metadata = RecoveryProcessMetadata(
        worker_pid=process.pid,
        exit_code=exit_code,
        exit_verified=True,
        started_at=started_at,
        completed_at=completed_at,
    )
    return RecoveryPhase(process=metadata, result=result, stderr_path=stderr_path)


def run_crash_recovery_experiment(
    *,
    profile_name: str,
    strategy: CheckpointStrategy,
    run_root: Path,
    checkpoint_step: int | None = None,
    hard_rollback_limit_steps: int = 0,
    post_commit_steps: int = 0,
    strategy_config_path: str | None = None,
    timeout_seconds: float = 60.0,
) -> CrashExperimentResult:
    """Run control, real crash, new-process recovery, gate, and structured artifacts."""

    profile = get_profile(profile_name)
    selected_step = checkpoint_step if checkpoint_step is not None else profile.steps // 2
    if hard_rollback_limit_steps < 0:
        raise ValueError("hard rollback limit cannot be negative")
    run_root = run_root.resolve()
    sandbox = PathSandbox.create(run_root)
    if sandbox.resolve_relative("result.json").exists():
        raise FileExistsError("experiment result already exists in this run")

    control = snapshot_from_summary(run_control(profile.name))
    crash_phase = run_checkpoint_crash_phase(
        profile_name=profile.name,
        strategy=strategy,
        run_root=run_root,
        checkpoint_step=selected_step,
        post_commit_steps=post_commit_steps,
        strategy_config_path=strategy_config_path,
        timeout_seconds=timeout_seconds,
    )
    recovery_phase = run_recovery_phase(
        profile_name=profile.name,
        strategy=strategy,
        run_root=run_root,
        checkpoint_path=crash_phase.event.checkpoint_path,
        strategy_config_path=strategy_config_path,
        timeout_seconds=timeout_seconds,
    )
    if crash_phase.crash.worker_pid == recovery_phase.result.worker_pid:
        raise OrchestrationError("operating system reused the original PID for recovery")

    # Every path used above, plus both pending structured artifacts, resolves in this sandbox.
    sandbox.resolve_relative("result.json")
    sandbox.resolve_relative(_FAILURE_ARTIFACT)
    gate = evaluate_recovery_gate(
        run_root=run_root,
        checkpoint=crash_phase.checkpoint,
        committed_event=crash_phase.event,
        crash=crash_phase.crash,
        recovery_process=recovery_phase.process,
        recovery=recovery_phase.result,
        control=control,
        hard_rollback_limit_steps=hard_rollback_limit_steps,
        managed_paths_contained=True,
    )
    failure_artifact_path: str | None = None
    if not gate.passed:
        failure_artifact = build_sanitized_failure_artifact(
            checkpoint=crash_phase.checkpoint,
            event=crash_phase.event,
            crash=crash_phase.crash,
            recovery=recovery_phase.result,
            gate=gate,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path=_FAILURE_ARTIFACT,
            value=failure_artifact,
        )
        failure_artifact_path = _FAILURE_ARTIFACT

    if os.name == "nt":
        platform_note = (
            "Windows: payload and metadata files are fsynced and directory rename is atomic; "
            "directory fsync is unavailable through Python and remains best-effort."
        )
    else:
        platform_note = "POSIX: payload, metadata, and supported directory fsync are required."
    result = CrashExperimentResult(
        run_id=run_root.name,
        created_at=datetime.now(UTC),
        profile=profile.name,
        strategy=strategy,
        control=control,
        crash=crash_phase.crash,
        recovery_process=recovery_phase.process,
        recovery=recovery_phase.result,
        gate=gate,
        failure_artifact_path=failure_artifact_path,
        platform_support_note=platform_note,
        limitations=(
            "Physical NAND writes, write amplification, and SSD lifetime were not measured.",
            "No GPT provider, diagnosis, repair execution, HTML, or packaging is part of Prompt 3.",
        ),
    )
    write_json_artifact(run_root=run_root, relative_path="result.json", value=result)
    return result
