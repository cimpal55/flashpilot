"""Checked-in schema generation for previous-valid fallback evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.fallback.models import (
    FallbackCheckpointSetEvent,
    PreviousValidFallbackResult,
)


def fallback_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "fallback-checkpoint-set-v1.schema.json": FallbackCheckpointSetEvent.model_json_schema(
            mode="serialization"
        ),
        "previous-valid-fallback-v1.schema.json": PreviousValidFallbackResult.model_json_schema(
            mode="serialization"
        ),
    }


def write_fallback_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(fallback_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
