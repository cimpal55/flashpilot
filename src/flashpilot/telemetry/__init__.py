"""Optional storage telemetry, captured strictly as supporting evidence.

This package is not part of the product core. Nothing it produces may
contribute to a Recovery Gate check, a qualification verdict, an attestation
field, or a CI policy decision.
"""

from flashpilot.telemetry.models import (
    MAX_OBSERVATION_SECONDS,
    MIN_OBSERVATION_SECONDS,
    NVME_COUNTER_GRANULARITY_BYTES,
    STORAGE_TELEMETRY_LIMITATIONS,
    STORAGE_TELEMETRY_PATH,
    StorageTelemetryAvailability,
    StorageTelemetryCounters,
    StorageTelemetryDelta,
    StorageTelemetryEvidenceV1,
    StorageTelemetrySample,
)
from flashpilot.telemetry.schema import (
    storage_telemetry_schema_documents,
    write_storage_telemetry_schema_files,
)
from flashpilot.telemetry.service import (
    StorageTelemetryCapture,
    StorageTelemetryError,
    finish_capture,
    observe,
    read_storage_telemetry,
    start_capture,
    write_storage_telemetry,
)

__all__ = [
    "MAX_OBSERVATION_SECONDS",
    "MIN_OBSERVATION_SECONDS",
    "NVME_COUNTER_GRANULARITY_BYTES",
    "STORAGE_TELEMETRY_LIMITATIONS",
    "STORAGE_TELEMETRY_PATH",
    "StorageTelemetryAvailability",
    "StorageTelemetryCapture",
    "StorageTelemetryCounters",
    "StorageTelemetryDelta",
    "StorageTelemetryError",
    "StorageTelemetryEvidenceV1",
    "StorageTelemetrySample",
    "finish_capture",
    "observe",
    "read_storage_telemetry",
    "start_capture",
    "storage_telemetry_schema_documents",
    "write_storage_telemetry_schema_files",
    "write_storage_telemetry",
]
