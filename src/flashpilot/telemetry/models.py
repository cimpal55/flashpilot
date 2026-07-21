"""Strict schemas for optional storage telemetry captured as supporting evidence.

Storage telemetry is deliberately NOT part of the product core. It never
contributes to a Recovery Gate check, a qualification verdict, an attestation
field, or a policy decision. It exists only to record what the host reported
around a measured window, with its confounders stated in the artifact itself.

Two honesty rules are encoded structurally rather than left to documentation:

1. Host counters are device-wide. Any other process writing to the same device
   during the window is included in the delta, so a delta is never described as
   "bytes written by this run". The `attribution` field can only ever say
   `device-wide-not-attributable`.
2. FlashPilot never reports NAND wear, write amplification, or SSD lifetime.
   There is no field in which such a claim could be recorded.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

STORAGE_TELEMETRY_PATH = "storage-telemetry.json"

# NVMe Data Units Written is a ROUNDED device counter: the spec counts units of
# 1000 * 512 bytes, incremented per rounded-up unit. A difference of N units
# therefore does not establish N * 512000 bytes, nor even a strict lower bound,
# because each end of the window is itself rounded. This constant is published
# as the counter's granularity so a reader can interpret the unit delta — it is
# never used to synthesise a byte figure.
NVME_COUNTER_GRANULARITY_BYTES = 512_000

# Bounds for a real observation window. A window must be long enough to contain
# something and short enough to stay a bounded, interruptible operation.
MIN_OBSERVATION_SECONDS = 1
MAX_OBSERVATION_SECONDS = 3600


class StrictTelemetryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class StorageTelemetryAvailability(StrictTelemetryModel):
    """Why telemetry is or is not present. Absence is normal, not an error."""

    available: bool
    reason: Literal[
        "collected",
        "unsupported-platform",
        "tool-unavailable",
        "insufficient-privileges",
        "no-supported-device",
        "device-not-bound",
        "unreadable-counters",
        "output-limit-exceeded",
        "collection-disabled",
    ]
    detail: str = Field(max_length=500)


class StorageTelemetryCounters(StrictTelemetryModel):
    """One raw reading. Every field is optional because vendors differ."""

    data_units_written: int | None = Field(default=None, ge=0)
    host_write_commands: int | None = Field(default=None, ge=0)
    power_on_hours: int | None = Field(default=None, ge=0)
    unsafe_shutdowns: int | None = Field(default=None, ge=0)
    media_errors: int | None = Field(default=None, ge=0)

    def has_any(self) -> bool:
        return any(
            value is not None
            for value in (
                self.data_units_written,
                self.host_write_commands,
                self.power_on_hours,
                self.unsafe_shutdowns,
                self.media_errors,
            )
        )


class StorageTelemetrySample(StrictTelemetryModel):
    """A single point-in-time reading from one device."""

    schema_version: Literal["flashpilot-storage-telemetry-sample-v1"] = (
        "flashpilot-storage-telemetry-sample-v1"
    )
    captured_at: datetime
    device_id: str = Field(min_length=1, max_length=200)
    device_kind: Literal["nvme", "unknown"]
    source: Literal[
        "linux-nvme-cli",
        "windows-storage-reliability-counter",
        "unavailable",
    ]
    counters: StorageTelemetryCounters


class StorageTelemetryDelta(StrictTelemetryModel):
    """The change between two samples, with its confounders made explicit.

    There is deliberately no byte field. NVMe Data Units Written is rounded at
    both ends of the window, so no honest byte count — not even a lower bound —
    follows from a unit difference. The rounded unit delta is published with its
    granularity and left uninterpreted.
    """

    schema_version: Literal["flashpilot-storage-telemetry-delta-v1"] = (
        "flashpilot-storage-telemetry-delta-v1"
    )
    window_seconds: float = Field(ge=0.0)
    data_units_written_delta: int | None = Field(default=None, ge=0)
    counter_granularity_bytes: int | None = Field(default=None, gt=0)
    host_write_commands_delta: int | None = Field(default=None, ge=0)
    unsafe_shutdowns_delta: int | None = Field(default=None, ge=0)
    media_errors_delta: int | None = Field(default=None, ge=0)

    # Structurally fixed: a device-wide counter can never be attributed to one
    # process, so this field has exactly one permitted value.
    attribution: Literal["device-wide-not-attributable"] = "device-wide-not-attributable"
    counter_wrapped: bool = False

    @model_validator(mode="after")
    def _granularity_accompanies_units(self) -> Self:
        if self.data_units_written_delta is None:
            if self.counter_granularity_bytes is not None:
                raise ValueError("counter_granularity_bytes requires data_units_written_delta")
            return self
        if self.counter_granularity_bytes != NVME_COUNTER_GRANULARITY_BYTES:
            raise ValueError("counter_granularity_bytes must be the NVMe counter granularity")
        return self


class StorageTelemetryEvidenceV1(StrictTelemetryModel):
    """The complete supporting-evidence artifact.

    `influences_verdict` is a frozen literal. It exists so that any consumer —
    a reporter, a CI policy, the report UI — can assert mechanically that this
    artifact is not permitted to affect a verdict.
    """

    schema_version: Literal["flashpilot-storage-telemetry-v1"] = "flashpilot-storage-telemetry-v1"
    evidence_class: Literal["supporting-only"] = "supporting-only"
    influences_verdict: Literal[False] = False
    availability: StorageTelemetryAvailability
    before: StorageTelemetrySample | None = None
    after: StorageTelemetrySample | None = None
    delta: StorageTelemetryDelta | None = None
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _samples_match_availability(self) -> Self:
        if not self.availability.available:
            if self.before is not None or self.after is not None or self.delta is not None:
                raise ValueError("unavailable telemetry must not carry samples or a delta")
            return self
        if self.before is None or self.after is None:
            raise ValueError("available telemetry requires both a before and an after sample")
        if self.before.device_id != self.after.device_id:
            raise ValueError("before and after samples must describe the same device")
        if self.after.captured_at < self.before.captured_at:
            raise ValueError("after sample must not precede the before sample")
        return self


# Stated on every artifact, including unavailable ones. These are the claims
# FlashPilot explicitly does not make.
STORAGE_TELEMETRY_LIMITATIONS: tuple[str, ...] = (
    "Host counters are device-wide; concurrent writes by any other process are "
    "included and cannot be separated from this run.",
    "NVMe Data Units Written is a rounded counter. A unit difference does not "
    "establish a byte count or a byte lower bound, and none is reported.",
    "Reported values are what the device firmware exposes; FlashPilot does not "
    "verify their accuracy.",
    "No claim is made about NAND wear, write amplification, endurance, or drive "
    "lifetime, none of which are measured.",
    "This artifact is supporting evidence only. It does not contribute to any "
    "Recovery Gate check, qualification verdict, or attestation.",
)
