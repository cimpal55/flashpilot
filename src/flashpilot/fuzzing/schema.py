"""Checked-in JSON Schema generation for partial-write fuzz evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.fuzzing.models import (
    FuzzCaseResult,
    FuzzCheckpointManifestV1,
    PartialWriteFuzzResult,
)


def fuzz_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "fuzz-checkpoint-artifact-v1.schema.json": (
            FuzzCheckpointManifestV1.model_json_schema(mode="serialization")
        ),
        "fuzz-case-v1.schema.json": FuzzCaseResult.model_json_schema(mode="serialization"),
        "partial-write-fuzz-v1.schema.json": PartialWriteFuzzResult.model_json_schema(
            mode="serialization"
        ),
    }


def write_fuzz_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(fuzz_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
