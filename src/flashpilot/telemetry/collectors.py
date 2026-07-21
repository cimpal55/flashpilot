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
import time
from datetime import UTC, datetime
from pathlib import Path

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


class _OutputLimitExceeded(RuntimeError):
    """Raised when a collector produced more output than the cap allows."""


def _run_readonly(argv: list[str]) -> tuple[int, str] | None:
    """Run a read-only command as an argument array. Never uses a shell.

    Reads stdout incrementally and kills the child as soon as the cap is
    exceeded. `subprocess.run(capture_output=True)` would buffer the whole
    stream in memory first and only then allow slicing, which caps the value
    we keep but not the memory a hostile or broken tool can make us allocate.
    """
    try:
        process = subprocess.Popen(  # noqa: S603 - fixed argv, no shell, no user input
            argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except (OSError, ValueError):
        return None

    chunks: list[bytes] = []
    total = 0
    deadline = time.monotonic() + COLLECTION_TIMEOUT_SECONDS
    try:
        assert process.stdout is not None
        while True:
            if time.monotonic() > deadline:
                raise TimeoutError("collector exceeded its timeout")
            chunk = process.stdout.read(8192)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_COLLECTOR_OUTPUT_BYTES:
                raise _OutputLimitExceeded(f"collector exceeded {MAX_COLLECTOR_OUTPUT_BYTES} bytes")
            chunks.append(chunk)
        returncode = process.wait(timeout=max(0.0, deadline - time.monotonic()))
    except _OutputLimitExceeded:
        _terminate(process)
        raise
    except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired):
        _terminate(process)
        return None
    finally:
        if process.stdout is not None:
            process.stdout.close()

    return returncode, b"".join(chunks).decode("utf-8", errors="replace")


def _terminate(process: subprocess.Popen[bytes]) -> None:
    """Guarantee the child is gone, escalating from terminate to kill."""
    if process.poll() is not None:
        return
    try:
        process.terminate()
        process.wait(timeout=2.0)
    except (OSError, subprocess.TimeoutExpired):
        try:
            process.kill()
            process.wait(timeout=2.0)
        except (OSError, subprocess.TimeoutExpired):
            pass


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

    try:
        result = _run_readonly(["nvme", "smart-log", device, "--output-format=json"])
    except _OutputLimitExceeded as error:
        return _unavailable("output-limit-exceeded", str(error))
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


# Resolves the physical disk that actually backs the given drive letter:
# volume -> partition -> disk. Selecting the first disk on the system would be
# a proxy, not a measurement, so an unprovable link must fail closed instead.
_WINDOWS_COUNTER_SCRIPT = (
    "$ErrorActionPreference='Stop';"
    "$p=Get-Partition -DriveLetter {drive};"
    "$d=$p | Get-Disk | Get-PhysicalDisk;"
    "if(@($d).Count -ne 1){{throw 'ambiguous physical disk'}};"
    "$c=$d | Get-StorageReliabilityCounter;"
    "[pscustomobject]@{{"
    "DeviceId=$d.FriendlyName;"
    "SerialNumber=$d.SerialNumber;"
    "PowerOnHours=$c.PowerOnHours"
    "}} | ConvertTo-Json -Compress"
)


def _windows_drive_letter(run_dir: Path) -> str | None:
    """The drive letter backing run_dir, or None if it cannot be determined.

    The directory must already exist. Resolving a non-existent path would fall
    back to the current working drive, silently binding the measurement to a
    device that has nothing to do with the run.
    """
    try:
        resolved = run_dir.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not resolved.is_dir():
        return None
    # "C:" for a local path; a UNC path yields "\\\\server\\share", which is
    # not a drive letter and is therefore not bindable.
    drive = resolved.drive
    if len(drive) == 2 and drive[1] == ":" and drive[0].isalpha():
        return drive[0].upper()
    return None


def _collect_windows_reliability(run_dir: Path | None) -> _CollectorResult:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        return _unavailable("tool-unavailable", "PowerShell is not available on PATH")

    if run_dir is None:
        return _unavailable(
            "device-not-bound",
            "no run directory was supplied, so no device could be bound to the measurement",
        )
    drive_letter = _windows_drive_letter(run_dir)
    if drive_letter is None:
        return _unavailable(
            "device-not-bound",
            f"could not resolve a drive letter for {run_dir}; network and mapped paths are not bound",
        )

    try:
        result = _run_readonly(
            [
                powershell,
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                _WINDOWS_COUNTER_SCRIPT.format(drive=drive_letter),
            ]
        )
    except _OutputLimitExceeded as error:
        return _unavailable("output-limit-exceeded", str(error))
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

    # The device identity must be stable across both samples, so it is built
    # from what the disk reports rather than from an index that could shift.
    device_id = payload.get("SerialNumber") or payload.get("DeviceId")
    if not device_id:
        return _unavailable(
            "device-not-bound", "the bound physical disk reported no stable identity"
        )
    return _CollectorResult(
        sample=StorageTelemetrySample(
            captured_at=datetime.now(UTC),
            device_id=f"{drive_letter}: {str(device_id).strip()}"[:200],
            device_kind="unknown",
            source="windows-storage-reliability-counter",
            counters=counters,
        ),
        availability=StorageTelemetryAvailability(
            available=True,
            reason="collected",
            detail=(
                f"Windows storage reliability counters for the disk backing {drive_letter}: "
                "(no host-write byte counter is exposed)"
            ),
        ),
    )


def collect_sample(device: str | None = None, run_dir: Path | None = None) -> _CollectorResult:
    """Collect one reading, or explain why none is available."""
    if sys.platform.startswith("linux"):
        return _collect_linux_nvme(device or "/dev/nvme0")
    if sys.platform == "win32":
        if device is not None:
            return _unavailable(
                "no-supported-device",
                "explicit device selection is not supported on Windows",
            )
        return _collect_windows_reliability(run_dir)
    return _unavailable(
        "unsupported-platform", f"storage telemetry is not implemented for {sys.platform}"
    )
