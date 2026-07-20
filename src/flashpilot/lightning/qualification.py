"""External process harness for PyTorch Lightning qualification."""

from __future__ import annotations

import os
import queue
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from flashpilot.adapters.lightning import PyTorchLightningAdapter
from flashpilot.checkpoints.integrity import logical_directory_bytes
from flashpilot.lightning.example import (
    LIGHTNING_CHECKPOINT_STEP,
    LIGHTNING_SEED,
    LIGHTNING_TOTAL_STEPS,
)
from flashpilot.lightning.gate import evaluate_lightning_recovery_gate
from flashpilot.lightning.models import (
    LightningCheckpointLifecycleEvidence,
    LightningProcessEvidence,
    LightningQualificationResult,
    LightningRunSummary,
    LightningScenario,
)
from flashpilot.lightning.reporting import render_lightning_html, render_lightning_markdown
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.security.paths import PathSandbox


class LightningQualificationError(RuntimeError):
    """Lightning qualification could not produce trustworthy evidence."""


class LightningUnsupportedConfigurationError(LightningQualificationError):
    """The selected configuration is outside the supported contract."""


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


def _termination_is_expected(exit_code: int) -> bool:
    return exit_code != 0 if os.name == "nt" else exit_code == -signal.SIGKILL


def _read_lines(stream: TextIO, output: queue.Queue[str | None]) -> None:
    try:
        for line in stream:
            output.put(line)
    finally:
        output.put(None)


def _load_summary(run_root: Path, relative_path: str) -> LightningRunSummary:
    path = PathSandbox.create(run_root).resolve_relative(relative_path, must_exist=True)
    try:
        return LightningRunSummary.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError) as error:
        raise LightningQualificationError(
            f"invalid Lightning worker result: {relative_path}"
        ) from error


def _run_to_completion(
    *,
    command: tuple[str, ...],
    run_root: Path,
    log_stem: str,
    timeout_seconds: float,
    seed: int,
) -> LightningProcessEvidence:
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
        shell=False,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as error:
        process.kill()
        process.wait(timeout=timeout_seconds)
        raise LightningQualificationError(f"{log_stem} worker timed out") from error
    completed_at = datetime.now(UTC)
    write_text_artifact(
        run_root=run_root,
        relative_path=f"logs/{log_stem}.stdout.log",
        text=stdout,
    )
    write_text_artifact(
        run_root=run_root,
        relative_path=f"logs/{log_stem}.stderr.log",
        text=stderr,
    )
    if process.returncode != 0:
        raise LightningQualificationError(
            f"{log_stem} worker failed with exit code {process.returncode}; "
            f"see logs/{log_stem}.stderr.log"
        )
    return LightningProcessEvidence(
        worker_pid=process.pid,
        started_at=started_at,
        completed_at=completed_at,
        exit_code=process.returncode,
        exit_verified=True,
    )


def _run_and_kill_at_checkpoint(
    *,
    command: tuple[str, ...],
    run_root: Path,
    timeout_seconds: float,
    seed: int,
) -> tuple[LightningProcessEvidence, LightningCheckpointLifecycleEvidence]:
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
        raise LightningQualificationError("crash worker output was not captured")
    output: queue.Queue[str | None] = queue.Queue()
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    stdout_reader = threading.Thread(target=_read_lines, args=(process.stdout, output), daemon=True)
    stderr_reader = threading.Thread(
        target=lambda: stderr_lines.extend(process.stderr.readlines()), daemon=True
    )
    stdout_reader.start()
    stderr_reader.start()
    deadline = time.monotonic() + timeout_seconds
    event: LightningCheckpointLifecycleEvidence | None = None
    try:
        while time.monotonic() < deadline:
            try:
                line = output.get(timeout=min(0.1, max(0.01, deadline - time.monotonic())))
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if line is None:
                break
            stdout_lines.append(line)
            try:
                candidate = LightningCheckpointLifecycleEvidence.model_validate_json(line)
            except ValidationError:
                continue
            if candidate.worker_pid != process.pid:
                raise LightningQualificationError("checkpoint event PID does not match worker")
            event = candidate
            break
        if event is None:
            raise LightningQualificationError("worker did not emit valid checkpoint evidence")
        checkpoint = PathSandbox.create(run_root).resolve_relative(
            event.checkpoint_path,
            must_exist=True,
        )
        PyTorchLightningAdapter().checkpoint_payload(checkpoint)
        process.kill()
        exit_code = process.wait(timeout=timeout_seconds)
        completed_at = datetime.now(UTC)
        if not _termination_is_expected(exit_code):
            raise LightningQualificationError(
                f"crash worker termination returned unexpected exit code {exit_code}"
            )
        return (
            LightningProcessEvidence(
                worker_pid=process.pid,
                started_at=started_at,
                completed_at=completed_at,
                exit_code=exit_code,
                exit_verified=True,
            ),
            event,
        )
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=timeout_seconds)
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
            relative_path="logs/crash.stdout.log",
            text="".join(stdout_lines),
        )
        write_text_artifact(
            run_root=run_root,
            relative_path="logs/crash.stderr.log",
            text="".join(stderr_lines),
        )


def _copy_script(*, source: Path, run_root: Path) -> tuple[Path, str]:
    source = source.absolute()
    if not source.is_file() or source.is_symlink() or source.suffix.lower() != ".py":
        raise LightningUnsupportedConfigurationError(
            "qualification script must be a regular non-symlink .py file"
        )
    relative = "inputs/train.py"
    destination = PathSandbox.create(run_root).resolve_relative(relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise LightningUnsupportedConfigurationError("run-owned script already exists")
    shutil.copyfile(source, destination)
    return destination, relative


def run_lightning_qualification(
    *,
    script_path: Path,
    run_root: Path,
    scenario: LightningScenario,
    forwarded_arguments: tuple[str, ...] = (),
    checkpoint_step: int = LIGHTNING_CHECKPOINT_STEP,
    total_steps: int = LIGHTNING_TOTAL_STEPS,
    seed: int = LIGHTNING_SEED,
    timeout_seconds: float = 120.0,
) -> LightningQualificationResult:
    """Run control, real termination, and new-process resume."""

    if checkpoint_step <= 0 or total_steps <= checkpoint_step:
        raise ValueError("checkpoint step must be positive and precede total steps")
    if run_root.exists() and any(run_root.iterdir()):
        raise LightningUnsupportedConfigurationError(
            "Lightning qualification requires a new or empty run directory"
        )
    sandbox = PathSandbox.create(run_root)
    adapter = PyTorchLightningAdapter()
    adapter.dependency_version()
    forwarded = adapter.validate_forwarded_arguments(forwarded_arguments)
    owned_script, script_relative = _copy_script(source=script_path, run_root=sandbox.root)

    def command(mode: str, result_path: str, checkpoint_path: str | None = None):
        return adapter.worker_command(
            python_executable=_python_executable(),
            script_path=owned_script,
            mode=mode,
            run_root=sandbox.root,
            scenario=scenario,
            checkpoint_step=checkpoint_step,
            total_steps=total_steps,
            seed=seed,
            result_path=result_path,
            checkpoint_path=checkpoint_path,
            forwarded_arguments=forwarded,
        )

    control_relative = "control/result.json"
    control_process = _run_to_completion(
        command=command("control", control_relative),
        run_root=sandbox.root,
        log_stem="control",
        timeout_seconds=timeout_seconds,
        seed=seed,
    )
    control = _load_summary(sandbox.root, control_relative)
    crash_process, checkpoint_event = _run_and_kill_at_checkpoint(
        command=command("train-crash", "crash/result.json"),
        run_root=sandbox.root,
        timeout_seconds=timeout_seconds,
        seed=seed,
    )
    checkpoint = sandbox.resolve_relative(checkpoint_event.checkpoint_path, must_exist=True)
    inventory = adapter.checkpoint_inventory(checkpoint)
    recovery_relative = "recovery/result.json"
    recovery_process = _run_to_completion(
        command=command("recover", recovery_relative, checkpoint_event.checkpoint_path),
        run_root=sandbox.root,
        log_stem="recovery",
        timeout_seconds=timeout_seconds,
        seed=seed,
    )
    recovery = _load_summary(sandbox.root, recovery_relative)
    gate = evaluate_lightning_recovery_gate(
        control=control,
        recovery=recovery,
        checkpoint=checkpoint_event,
        crash_process=crash_process,
        recovery_process=recovery_process,
        total_steps=total_steps,
    )
    diverged = any(
        (
            recovery.loss_history != control.loss_history,
            recovery.trainable_state_sha256 != control.trainable_state_sha256,
            recovery.evaluation_sha256 != control.evaluation_sha256,
            recovery.optimizer_sha256 != control.optimizer_sha256,
            recovery.scheduler_sha256 != control.scheduler_sha256,
        )
    )
    result = LightningQualificationResult(
        run_id=uuid.uuid4().hex,
        created_at=datetime.now(UTC),
        scenario=scenario,
        script_path=script_relative,
        forwarded_arguments=forwarded,
        control_process=control_process,
        control=control,
        crash_process=crash_process,
        checkpoint_event=checkpoint_event,
        checkpoint_inventory=inventory,
        recovery_process=recovery_process,
        recovery=recovery,
        gate=gate,
        model_checkpoint_load_succeeded=True,
        weights_only_diverged=diverged if scenario == "weights-only" else False,
        final_verdict="VERIFIED" if gate.passed else "FAILED",
        verified_persisted_bytes=logical_directory_bytes(checkpoint) if gate.passed else None,
        limitations=(
            "Qualification covers the included CPU LightningModule, not arbitrary modules.",
            "The RNG bridge is explicit module checkpoint state required by this contract.",
            "The attestation is unsigned and provides integrity, not publisher authentication.",
        ),
    )
    write_json_artifact(run_root=sandbox.root, relative_path="result.json", value=result)
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.md",
        text=render_lightning_markdown(result),
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path="report.html",
        text=render_lightning_html(result),
    )
    from flashpilot.ci.service import write_qualification_ci_outputs

    write_qualification_ci_outputs(run_root=sandbox.root, result=result)
    if result.final_verdict == "VERIFIED":
        from flashpilot.attestation.builder import emit_lightning_recovery_attestation

        emit_lightning_recovery_attestation(run_root=sandbox.root, result=result)
    return result
