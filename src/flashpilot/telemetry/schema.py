"""Deterministic public JSON Schema for storage telemetry evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.telemetry.models import StorageTelemetryEvidenceV1


def storage_telemetry_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "storage-telemetry-v1.schema.json": StorageTelemetryEvidenceV1.model_json_schema(
            mode="serialization"
        ),
    }


def write_storage_telemetry_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(storage_telemetry_schema_documents().items()):
        target = schema_root / filename
        target.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(target)
    return tuple(written)
