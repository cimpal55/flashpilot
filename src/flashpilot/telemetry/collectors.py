"""Read-only collectors for optional storage telemetry.

Every collector is strictly read-only, is invoked as an argument array rather
than a shell string, is bounded by a timeout and an output cap, and never
escalates privileges. Any failure — missing tool, unsupported platform,
insufficient rights, unparsable output — resolves to "unavailable" rather than
to a partial or guessed reading.

FlashPilot does not install, require, or prompt for these tools. Telemetry is
supporting evidence; its absence is a normal outcome and must never block or
degrade a qualification run.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime

from flashpilot.telemetry.models import (
    StorageTelemetryAvailability,
    StorageTelemetryCounters,
    StorageTelemetrySample,
)

COLLECTION_TIMEOUT_SECONDS = 10.0
MAX_COLLECTOR_OUTPUT_BYTES = 256 * 1024


class _CollectorResult:
    """Internal carrier so a collector can report why it produced nothing."""

    __slots__ = ("sample", "availability")

    def __init__(
        self,
        sample: StorageTelemetrySample | None,
        availability: StorageTelemetryAvailability,
    ) -> None:
        self.sample = sample
        self.availability = availability


def _unavailable(reason: str, detail: str) -> _CollectorResult:
    return _CollectorResult(
        sample=None,
        availability=StorageTelemetryAvailability(
            available=False,
            reason=reason,  # type: ignore[arg-type]
            detail=detail[:500],
        ),
    )


def _run_readonly(argv: list[str]) -> tuple[int, str] | None:
    """Run a read-only command as an argument array. Never uses a shell."""
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, no user input
            argv,
            capture_output=True,
            timeout=COLLECTION_TIMEOUT_SECONDS,
            check=False,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    stdout = completed.stdout[:MAX_COLLECTOR_OUTPUT_BYTES]
    try:
        return completed.returncode, stdout.decode("utf-8", errors="replace")
    except UnicodeError:
        return None


def _coerce_counter(value: object) -> int | None:
    """Accept only clean non-negative integers. Never coerce a guess."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float) and value.is_integer() and value >= 0:
        return int(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text.isdigit():
            return int(text)
    return None


def _collect_linux_nvme(device: str) -> _CollectorResult:
    if shutil.which("nvme") is None:
        return _unavailable("tool-unavailable", "nvme-cli is not installed or not on PATH")

    result = _run_readonly(["nvme", "smart-log", device, "--output-format=json"])
    if result is None:
        return _unavailable(
            "unreadable-counters", f"nvme smart-log could not be executed for {device}"
        )
    returncode, stdout = result
    if returncode != 0:
        # Non-zero here is most often EACCES: SMART logs usually need root.
        return _unavailable(
            "insufficient-privileges",
            f"nvme smart-log exited {returncode} for {device}; SMART logs typically require root",
        )
    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return _unavailable("unreadable-counters", "nvme smart-log output was not valid JSON")
    if not isinstance(payload, dict):
        return _unavailable("unreadable-counters", "nvme smart-log output was not a JSON object")

    counters = StorageTelemetryCounters(
        data_units_written=_coerce_counter(payload.get("data_units_written")),
        host_write_commands=_coerce_counter(payload.get("host_write_commands")),
        power_on_hours=_coerce_counter(payload.get("power_on_hours")),
        unsafe_shutdowns=_coerce_counter(payload.get("unsafe_shutdowns")),
        media_errors=_coerce_counter(payload.get("media_errors")),
    )
    if not counters.has_any():
        return _unavailable(
            "unreadable-counters", "no recognised counters in nvme smart-log output"
        )

    return _CollectorResult(
        sample=StorageTelemetrySample(
            captured_at=datetime.now(UTC),
            device_id=device,
            device_kind="nvme",
            source="linux-nvme-cli",
            counters=counters,
        ),
        availability=StorageTelemetryAvailability(
            available=True, reason="collected", detail=f"nvme-cli smart-log for {device}"
        ),
    )


_WINDOWS_COUNTER_SCRIPT = (
    "$ErrorActionPreference='Stop';"
    "$d=Get-PhysicalDisk | Select-Object -First 1;"
    "$c=$d | Get-StorageReliabilityCounter;"
    "[pscustomobject]@{"
    "DeviceId=$d.FriendlyName;"
    "PowerOnHours=$c.PowerOnHours;"
    "Wear=$c.Wear;"
    "ReadErrorsTotal=$c.ReadErrorsTotal"
    "} | ConvertTo-Json -Compress"
)


def _collect_windows_reliability() -> _CollectorResult:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        return _unavailable("tool-unavailable", "PowerShell is not available on PATH")

    result = _run_readonly(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            _WINDOWS_COUNTER_SCRIPT,
        ]
    )
    if result is None:
        return _unavailable(
            "unreadable-counters", "Get-StorageReliabilityCounter could not be executed"
        )
    returncode, stdout = result
    if returncode != 0 or not stdout.strip():
        return _unavailable(
            "insufficient-privileges",
            "Get-StorageReliabilityCounter returned no data; it normally requires an elevated session",
        )
    try:
        payload = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return _unavailable("unreadable-counters", "storage reliability output was not valid JSON")
    if not isinstance(payload, dict):
        return _unavailable(
            "unreadable-counters", "storage reliability output was not a JSON object"
        )

    # Windows exposes no host-write byte counter comparable to NVMe data units,
    # so no write volume is recorded here rather than substituting a proxy.
    counters = StorageTelemetryCounters(
        power_on_hours=_coerce_counter(payload.get("PowerOnHours")),
    )
    if not counters.has_any():
        return _unavailable(
            "unreadable-counters",
            "no usable counters were returned by Get-StorageReliabilityCounter",
        )

    device_id = payload.get("DeviceId")
    return _CollectorResult(
        sample=StorageTelemetrySample(
            captured_at=datetime.now(UTC),
            device_id=str(device_id)[:200] if device_id else "physical-disk-0",
            device_kind="unknown",
            source="windows-storage-reliability-counter",
            counters=counters,
        ),
        availability=StorageTelemetryAvailability(
            available=True,
            reason="collected",
            detail="Windows storage reliability counters (no host-write byte counter is exposed)",
        ),
    )


def collect_sample(device: str | None = None) -> _CollectorResult:
    """Collect one reading, or explain why none is available."""
    if sys.platform.startswith("linux"):
        return _collect_linux_nvme(device or "/dev/nvme0")
    if sys.platform == "win32":
        if device is not None:
            return _unavailable(
                "no-supported-device",
                "explicit device selection is not supported on Windows",
            )
        return _collect_windows_reliability()
    return _unavailable(
        "unsupported-platform", f"storage telemetry is not implemented for {sys.platform}"
    )
