"""Capture storage telemetry around a measured window, as supporting evidence.

The service always produces an artifact. When telemetry cannot be collected it
produces an explicitly unavailable artifact rather than omitting the file, so a
consumer can distinguish "not collected" from "collected and empty".

Nothing here can influence a verdict. The artifact is written beside a run's
other outputs and is excluded from the evidence manifest's verdict-bearing
inventory by the caller.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from flashpilot.checkpoints.atomic import fsync_directory
from flashpilot.security.paths import PathContainmentError, PathSandbox
from flashpilot.telemetry.collectors import collect_sample
from flashpilot.telemetry.models import (
    MAX_OBSERVATION_SECONDS,
    MIN_OBSERVATION_SECONDS,
    NVME_COUNTER_GRANULARITY_BYTES,
    STORAGE_TELEMETRY_LIMITATIONS,
    STORAGE_TELEMETRY_PATH,
    StorageTelemetryAvailability,
    StorageTelemetryDelta,
    StorageTelemetryEvidenceV1,
    StorageTelemetrySample,
)


class StorageTelemetryError(RuntimeError):
    """Raised only for caller misuse, never for an absent counter."""


@dataclass(frozen=True)
class StorageTelemetryCapture:
    """An open capture window. Call `finish_capture` to produce the artifact."""

    before: StorageTelemetrySample | None
    availability: StorageTelemetryAvailability
    device: str | None
    run_dir: Path | None = None


def _unavailable_evidence(availability: StorageTelemetryAvailability) -> StorageTelemetryEvidenceV1:
    return StorageTelemetryEvidenceV1(
        availability=availability,
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )


def start_capture(
    device: str | None = None,
    *,
    enabled: bool = True,
    run_dir: Path | None = None,
) -> StorageTelemetryCapture:
    """Take the opening reading. Never raises for an unavailable device."""
    if not enabled:
        return StorageTelemetryCapture(
            before=None,
            availability=StorageTelemetryAvailability(
                available=False,
                reason="collection-disabled",
                detail="storage telemetry collection was not requested",
            ),
            device=device,
            run_dir=run_dir,
        )
    result = collect_sample(device, run_dir)
    return StorageTelemetryCapture(
        before=result.sample,
        availability=result.availability,
        device=device,
        run_dir=run_dir,
    )


def _counter_delta(before: int | None, after: int | None) -> tuple[int | None, bool]:
    """Return the delta and whether the counter appears to have wrapped/reset.

    A counter that moves backwards means a wrap, a firmware reset, or a
    different device. None of those can be turned into a meaningful delta, so
    the value is dropped rather than clamped to zero, which would understate it
    while looking like a real measurement.
    """
    if before is None or after is None:
        return None, False
    if after < before:
        return None, True
    return after - before, False


def observe(capture: StorageTelemetryCapture, duration_seconds: int) -> StorageTelemetryEvidenceV1:
    """Hold the window open for a bounded interval, then close it.

    Reading both samples back to back measures nothing but the cost of reading
    them. A real window needs elapsed time, so the duration is explicit and
    bounded. No caller-supplied command is executed during the window.
    """
    if not MIN_OBSERVATION_SECONDS <= duration_seconds <= MAX_OBSERVATION_SECONDS:
        raise StorageTelemetryError(
            f"duration must be between {MIN_OBSERVATION_SECONDS} and "
            f"{MAX_OBSERVATION_SECONDS} seconds"
        )
    if capture.before is not None:
        time.sleep(duration_seconds)
    return finish_capture(capture)


def finish_capture(capture: StorageTelemetryCapture) -> StorageTelemetryEvidenceV1:
    """Take the closing reading and build the artifact."""
    if capture.before is None:
        return _unavailable_evidence(capture.availability)

    result = collect_sample(capture.device, capture.run_dir)
    after = result.sample
    if after is None:
        return _unavailable_evidence(
            StorageTelemetryAvailability(
                available=False,
                reason=result.availability.reason,
                detail=f"closing sample unavailable: {result.availability.detail}",
            )
        )
    if after.device_id != capture.before.device_id:
        return _unavailable_evidence(
            StorageTelemetryAvailability(
                available=False,
                reason="no-supported-device",
                detail="the device changed between the opening and closing samples",
            )
        )

    units, units_wrapped = _counter_delta(
        capture.before.counters.data_units_written, after.counters.data_units_written
    )
    commands, commands_wrapped = _counter_delta(
        capture.before.counters.host_write_commands, after.counters.host_write_commands
    )
    shutdowns, shutdowns_wrapped = _counter_delta(
        capture.before.counters.unsafe_shutdowns, after.counters.unsafe_shutdowns
    )
    errors, errors_wrapped = _counter_delta(
        capture.before.counters.media_errors, after.counters.media_errors
    )

    window = (after.captured_at - capture.before.captured_at).total_seconds()
    delta = StorageTelemetryDelta(
        window_seconds=max(0.0, window),
        data_units_written_delta=units,
        counter_granularity_bytes=None if units is None else NVME_COUNTER_GRANULARITY_BYTES,
        host_write_commands_delta=commands,
        unsafe_shutdowns_delta=shutdowns,
        media_errors_delta=errors,
        counter_wrapped=any((units_wrapped, commands_wrapped, shutdowns_wrapped, errors_wrapped)),
    )

    return StorageTelemetryEvidenceV1(
        availability=capture.availability,
        before=capture.before,
        after=after,
        delta=delta,
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )


def write_storage_telemetry(evidence: StorageTelemetryEvidenceV1, run_dir: Path) -> Path:
    """Write the artifact atomically, inside the run directory, never over a link.

    A plain write would follow a symlink planted at the target path and would
    leave a truncated file behind if it failed midway. This writes a temporary
    file, fsyncs it, then replaces the target in one step, so a reader sees
    either the previous artifact or the complete new one.
    """
    if not run_dir.is_dir():
        raise StorageTelemetryError(f"run directory does not exist: {run_dir}")
    try:
        sandbox = PathSandbox.create(run_dir)
        target = sandbox.resolve_relative(STORAGE_TELEMETRY_PATH, reject_symlinks=True)
    except PathContainmentError as error:
        raise StorageTelemetryError(f"unsafe telemetry target: {error}") from error

    payload = json.loads(evidence.model_dump_json())
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if target.exists():
        # Re-writing identical content is a no-op; different content would mean
        # two disagreeing artifacts for one run, which must not be resolved by
        # silently preferring the newer one.
        existing = target.read_text(encoding="utf-8")
        if existing == text:
            return target
        raise StorageTelemetryError(
            f"a different {STORAGE_TELEMETRY_PATH} already exists in this run directory"
        )

    temporary = target.with_name(f"{target.name}.tmp")
    if temporary.is_symlink():
        raise StorageTelemetryError("temporary telemetry path is a symbolic link")
    try:
        with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise StorageTelemetryError(f"could not write storage telemetry: {error}") from error

    # Best effort: on Windows a directory handle cannot always be fsynced, and
    # the helper reports that rather than failing the write.
    fsync_directory(target.parent)
    return target


def read_storage_telemetry(path: Path) -> StorageTelemetryEvidenceV1:
    """Read and validate an artifact, failing closed on anything malformed."""
    raw = path.read_text(encoding="utf-8")
    return StorageTelemetryEvidenceV1.model_validate_json(raw)
