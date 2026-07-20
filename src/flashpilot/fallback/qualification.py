"""Real-process qualification of fallback from a corrupt newest checkpoint."""

from __future__ import annotations

import os
import queue
import signal
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from flashpilot.checkpoints.integrity import directory_content_fingerprint
from flashpilot.checkpoints.loader import (
    CheckpointValidationError,
    discover_valid_checkpoints,
    latest_valid_checkpoint,
    validate_checkpoint,
)
from flashpilot.domain.recovery import CheckpointCommittedEvent, CrashMetadata
from flashpilot.fallback.models import (
    FallbackCheckpointSetEvent,
    FallbackSelectionCheck,
    PreviousValidFallbackResult,
)
from flashpilot.fallback.reporting import (
    render_fallback_job_summary,
    render_fallback_junit,
    render_fallback_markdown,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.orchestration.experiment import run_recovery_phase
from flashpilot.security.paths import PathSandbox
from flashpilot.verification.observations import snapshot_from_summary
from flashpilot.verification.recovery_gate import evaluate_recovery_gate
from flashpilot.workload.control import run_control

PRODUCER_TIMEOUT_SECONDS = 60.0
PREVIOUS_CHECKPOINT_PATH = "checkpoints/checkpoint-step-000002"
NEWEST_CHECKPOINT_PATH = "checkpoints/checkpoint-step-000004"
NEWEST_CORRUPTION_ERROR = "payload checksum mismatch: model.pt"


class FallbackQualificationError(RuntimeError):
    """Previous-valid fallback could not produce trustworthy evidence."""


def _worker_environment() -> dict[str, str]:
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
    existing = environment.get("PYTHONPATH")
    if existing:
        python_paths.append(existing)
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "PYTHONHASHSEED": "20260720",
            "PYTHONPATH": os.pathsep.join(python_paths),
            "PYTHONUNBUFFERED": "1",
        }
    )
    return environment


def _worker_command(run_root: Path) -> list[str]:
    executable = Path(sys.executable)
    if os.name == "nt":
        base_executable = Path(getattr(sys, "_base_executable", sys.executable))
        if base_executable.is_file():
            executable = base_executable
    return [
        str(executable),
        "-m",
        "flashpilot.fallback.worker",
        "--run-root",
        str(run_root),
    ]


def _read_lines(stream: TextIO, output: queue.Queue[str | None]) -> None:
    try:
        for line in stream:
            output.put(line)
    finally:
        output.put(None)


def _read_event(
    process: subprocess.Popen[str],
    *,
    stderr_path: Path,
    timeout_seconds: float,
) -> FallbackCheckpointSetEvent:
    if process.stdout is None:
        raise FallbackQualificationError("fallback producer stdout was not captured")
    output: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(target=_read_lines, args=(process.stdout, output), daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            line = output.get(timeout=min(0.1, max(0.01, deadline - time.monotonic())))
        except queue.Empty:
            if process.poll() is not None:
                raise FallbackQualificationError(
                    f"fallback producer exited before its event with code {process.returncode}: "
                    f"{stderr_path.read_text(encoding='utf-8')}"
                ) from None
            continue
        if line is None:
            raise FallbackQualificationError("fallback producer closed stdout before its event")
        try:
            return FallbackCheckpointSetEvent.model_validate_json(line)
        except ValidationError as error:
            raise FallbackQualificationError(
                "fallback producer emitted an invalid event"
            ) from error
    raise FallbackQualificationError("timed out waiting for fallback checkpoint set")


def _termination_method() -> str:
    if os.name == "nt":
        return "TerminateProcess via subprocess.Popen.kill"
    return "SIGKILL via subprocess.Popen.kill"


def _termination_expected(exit_code: int) -> bool:
    return exit_code != 0 if os.name == "nt" else exit_code == -signal.SIGKILL


def _selection_check(
    check_id,
    passed: bool,
    summary: str,
    expected: str,
    actual: str,
) -> FallbackSelectionCheck:
    return FallbackSelectionCheck(
        check_id=check_id,
        status="pass" if passed else "fail",
        summary=summary,
        expected=expected,
        actual=actual,
    )


def _corrupt_newest(checkpoint_path: Path) -> None:
    model_path = checkpoint_path / "model.pt"
    with model_path.open("r+b") as stream:
        first = stream.read(1)
        if not first:
            raise FallbackQualificationError("newest model payload is unexpectedly empty")
        stream.seek(0)
        stream.write(bytes([first[0] ^ 0xFF]))
        stream.flush()
        os.fsync(stream.fileno())


def run_previous_valid_fallback(
    *,
    run_root: Path,
    timeout_seconds: float = PRODUCER_TIMEOUT_SECONDS,
) -> PreviousValidFallbackResult:
    """Reject a corrupt newest checkpoint and prove exact recovery from its predecessor."""

    if timeout_seconds <= 0:
        raise ValueError("fallback timeout must be positive")
    if run_root.exists() and (not run_root.is_dir() or any(run_root.iterdir())):
        raise FallbackQualificationError("fallback qualification requires a new or empty run root")
    run_root.mkdir(parents=True, exist_ok=True)
    root = PathSandbox.create(run_root.resolve()).root
    control = snapshot_from_summary(run_control("ci"))
    logs = PathSandbox.create(root).resolve_relative("logs")
    logs.mkdir()
    stderr_path = logs / "fallback-producer.stderr.log"
    event_received_at: datetime | None = None
    with stderr_path.open("x", encoding="utf-8", newline="\n") as stderr_stream:
        process = subprocess.Popen(
            _worker_command(root),
            cwd=root,
            env=_worker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=stderr_stream,
            text=True,
            encoding="utf-8",
            bufsize=1,
            shell=False,
        )
        try:
            event = _read_event(
                process,
                stderr_path=stderr_path,
                timeout_seconds=timeout_seconds,
            )
            if event.worker_pid != process.pid:
                raise FallbackQualificationError("fallback event PID differs from producer PID")
            event_received_at = datetime.now(UTC)
            records = {record.global_step: record for record in event.checkpoints}
            previous_path = PathSandbox.create(root).resolve_relative(
                records[2].checkpoint_path,
                must_exist=True,
            )
            newest_path = PathSandbox.create(root).resolve_relative(
                records[4].checkpoint_path,
                must_exist=True,
            )
            previous = validate_checkpoint(run_root=root, checkpoint_path=previous_path)
            newest = validate_checkpoint(run_root=root, checkpoint_path=newest_path)
            if previous.manifest.global_step != 2 or newest.manifest.global_step != 4:
                raise FallbackQualificationError("producer checkpoint steps are inconsistent")
            previous_before = directory_content_fingerprint(previous.path)
            newest_before = directory_content_fingerprint(newest.path)
            process.kill()
            exit_code = process.wait(timeout=timeout_seconds)
            terminated_at = datetime.now(UTC)
            if not _termination_expected(exit_code):
                raise FallbackQualificationError(
                    f"fallback producer termination returned unexpected code {exit_code}"
                )
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=timeout_seconds)
            if process.stdout is not None:
                process.stdout.close()
    if event_received_at is None:
        raise FallbackQualificationError("fallback producer event was not accepted")

    crash = CrashMetadata(
        worker_pid=event.worker_pid,
        checkpoint_step=4,
        last_completed_step=event.last_completed_step,
        checkpoint_path=NEWEST_CHECKPOINT_PATH,
        event_received_at=event_received_at,
        termination_method=_termination_method(),
        termination_exit_code=exit_code,
        termination_verified=True,
        terminated_at=terminated_at,
    )
    _corrupt_newest(newest.path)
    newest_after_corruption = directory_content_fingerprint(newest.path)
    validation_error = None
    try:
        validate_checkpoint(run_root=root, checkpoint_path=newest.path)
    except CheckpointValidationError as error:
        validation_error = str(error)
    valid = discover_valid_checkpoints(
        run_root=root,
        checkpoint_root=root / "checkpoints",
    )
    selected = latest_valid_checkpoint(
        run_root=root,
        checkpoint_root=root / "checkpoints",
    )
    valid_steps = tuple(checkpoint.manifest.global_step for checkpoint in valid)
    if selected is None:
        raise FallbackQualificationError("no valid checkpoint remained after corruption")
    selected_matches = selected.path == previous.path and selected.manifest.global_step == 2
    selected_record = records[2]
    selected_event = CheckpointCommittedEvent(
        worker_pid=event.worker_pid,
        checkpoint_step=selected_record.global_step,
        last_completed_step=event.last_completed_step,
        checkpoint_path=selected_record.checkpoint_path,
        committed_at=selected_record.committed_at,
        checkpoint_snapshot=selected_record.snapshot,
        rng_state=selected_record.rng_state,
    )
    recovery_phase = run_recovery_phase(
        profile_name="ci",
        strategy="safe_full",
        run_root=root,
        checkpoint_path=selected_record.checkpoint_path,
        timeout_seconds=timeout_seconds,
    )
    gate = evaluate_recovery_gate(
        run_root=root,
        checkpoint=selected,
        committed_event=selected_event,
        crash=crash,
        recovery_process=recovery_phase.process,
        recovery=recovery_phase.result,
        control=control,
        hard_rollback_limit_steps=2,
        managed_paths_contained=True,
    )
    previous_after = directory_content_fingerprint(previous.path)
    newest_after_recovery = directory_content_fingerprint(newest.path)
    checks = (
        _selection_check(
            "process.producer-terminated",
            crash.termination_verified and crash.termination_exit_code != 0,
            "Producer was terminated after both checkpoints committed.",
            "verified nonzero termination",
            f"exit={crash.termination_exit_code}, verified={crash.termination_verified}",
        ),
        _selection_check(
            "corruption.newest-changed",
            newest_before.sha256 != newest_after_corruption.sha256,
            "Injected corruption changed only the newest checkpoint fingerprint.",
            "newest SHA-256 changes",
            ("changed" if newest_before.sha256 != newest_after_corruption.sha256 else "unchanged"),
        ),
        _selection_check(
            "corruption.newest-rejected",
            validation_error == NEWEST_CORRUPTION_ERROR,
            "Newest checkpoint was rejected for its payload checksum.",
            NEWEST_CORRUPTION_ERROR,
            validation_error or "accepted",
        ),
        _selection_check(
            "discovery.only-previous-valid",
            valid_steps == (2,),
            "Discovery excluded the corrupt newest checkpoint.",
            "valid steps=(2,)",
            f"valid steps={valid_steps}",
        ),
        _selection_check(
            "discovery.previous-selected",
            selected_matches,
            "Latest-valid discovery selected the immediate predecessor.",
            PREVIOUS_CHECKPOINT_PATH,
            selected.path.relative_to(root).as_posix(),
        ),
        _selection_check(
            "immutability.previous-preserved",
            previous_before.sha256 == previous_after.sha256,
            "Fallback discovery and recovery preserved the previous checkpoint.",
            previous_before.sha256,
            previous_after.sha256,
        ),
        _selection_check(
            "immutability.corrupt-newest-preserved",
            newest_after_corruption.sha256 == newest_after_recovery.sha256,
            "Rejected newest evidence remained unchanged after recovery.",
            newest_after_corruption.sha256,
            newest_after_recovery.sha256,
        ),
    )
    selection_passed = all(check.status == "pass" for check in checks)
    verified = selection_passed and gate.passed and not gate.failed_check_ids
    if validation_error != NEWEST_CORRUPTION_ERROR or valid_steps != (2,) or not selected_matches:
        raise FallbackQualificationError("fallback selection failed closed")
    result = PreviousValidFallbackResult(
        run_id=root.name,
        created_at=datetime.now(UTC),
        control=control,
        checkpoint_set_event=event,
        selected_checkpoint_event=selected_event,
        producer_crash=crash,
        newest_validation_error=NEWEST_CORRUPTION_ERROR,
        valid_candidate_steps=valid_steps,
        selected_checkpoint_step=2,
        selected_checkpoint_path=PREVIOUS_CHECKPOINT_PATH,
        newest_checkpoint_path=NEWEST_CHECKPOINT_PATH,
        previous_sha256_before=previous_before.sha256,
        previous_sha256_after=previous_after.sha256,
        newest_sha256_before_corruption=newest_before.sha256,
        newest_sha256_after_corruption=newest_after_corruption.sha256,
        newest_sha256_after_recovery=newest_after_recovery.sha256,
        selection_checks=checks,
        recovery_process=recovery_phase.process,
        recovery=recovery_phase.result,
        gate=gate,
        recovery_verified=verified,
        final_verdict="VERIFIED" if verified else "FAILED",
        limitations=(
            "This qualification uses the fixed local native-PyTorch CI workload.",
            "It injects post-commit checksum corruption after producer termination.",
            "The rejected newest checkpoint is preserved; no automatic repair is attempted.",
            "No storage savings or physical device effects are measured.",
            "The verified result is not accompanied by a publisher-signed attestation.",
        ),
    )
    write_json_artifact(run_root=root, relative_path=result.result_path, value=result)
    write_text_artifact(
        run_root=root,
        relative_path=result.report_path,
        text=render_fallback_markdown(result),
    )
    write_text_artifact(
        run_root=root,
        relative_path=result.junit_path,
        text=render_fallback_junit(result),
    )
    write_text_artifact(
        run_root=root,
        relative_path=result.job_summary_path,
        text=render_fallback_job_summary(result),
    )
    from flashpilot.ci.sarif_adapters import render_fallback_sarif

    write_text_artifact(
        run_root=root,
        relative_path=result.sarif_path,
        text=render_fallback_sarif(result),
    )
    return result
