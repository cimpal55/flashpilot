"""Deterministic public JSON Schemas for conversion evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.conversion.models import (
    ConversionArtifactManifestV1,
    ConversionCaseResult,
    ConversionQualificationResult,
)


def conversion_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "conversion-artifact-v1.schema.json": ConversionArtifactManifestV1.model_json_schema(
            mode="serialization"
        ),
        "conversion-case-v1.schema.json": ConversionCaseResult.model_json_schema(
            mode="serialization"
        ),
        "conversion-qualification-v1.schema.json": (
            ConversionQualificationResult.model_json_schema(mode="serialization")
        ),
    }


def write_conversion_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(conversion_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
