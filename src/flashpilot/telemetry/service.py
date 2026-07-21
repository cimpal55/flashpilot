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
from dataclasses import dataclass
from pathlib import Path

from flashpilot.telemetry.collectors import collect_sample
from flashpilot.telemetry.models import (
    NVME_DATA_UNIT_BYTES,
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
    """An open capture window. Call `finish` to produce the artifact."""

    before: StorageTelemetrySample | None
    availability: StorageTelemetryAvailability
    device: str | None


def _unavailable_evidence(availability: StorageTelemetryAvailability) -> StorageTelemetryEvidenceV1:
    return StorageTelemetryEvidenceV1(
        availability=availability,
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )


def start_capture(device: str | None = None, *, enabled: bool = True) -> StorageTelemetryCapture:
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
        )
    result = collect_sample(device)
    return StorageTelemetryCapture(
        before=result.sample, availability=result.availability, device=device
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


def finish_capture(capture: StorageTelemetryCapture) -> StorageTelemetryEvidenceV1:
    """Take the closing reading and build the artifact."""
    if capture.before is None:
        return _unavailable_evidence(capture.availability)

    result = collect_sample(capture.device)
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
        host_write_bytes_lower_bound=None if units is None else units * NVME_DATA_UNIT_BYTES,
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
    """Write the artifact deterministically beside the run's other outputs."""
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise StorageTelemetryError(f"run directory does not exist: {run_dir}")
    target = run_dir / STORAGE_TELEMETRY_PATH
    payload = json.loads(evidence.model_dump_json())
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return target


def read_storage_telemetry(path: Path) -> StorageTelemetryEvidenceV1:
    """Read and validate an artifact, failing closed on anything malformed."""
    raw = path.read_text(encoding="utf-8")
    return StorageTelemetryEvidenceV1.model_validate_json(raw)
