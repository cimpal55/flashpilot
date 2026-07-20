"""Checked-in schema generation for randomized fault-timing evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.fault_timing.models import (
    FaultTimingTrialResult,
    RandomizedFaultTimingResult,
)


def timing_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "fault-timing-trial-v1.schema.json": FaultTimingTrialResult.model_json_schema(
            mode="serialization"
        ),
        "randomized-fault-timing-v1.schema.json": RandomizedFaultTimingResult.model_json_schema(
            mode="serialization"
        ),
    }


def write_timing_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(timing_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
