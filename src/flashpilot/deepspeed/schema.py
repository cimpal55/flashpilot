"""Deterministic public JSON Schemas for DeepSpeed qualification evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.deepspeed.models import (
    DeepSpeedCheckpointEvent,
    DeepSpeedCheckpointManifest,
    DeepSpeedQualificationResult,
    DeepSpeedRankCheckpointState,
)


def deepspeed_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "deepspeed-checkpoint-event-v1.schema.json": (
            DeepSpeedCheckpointEvent.model_json_schema(mode="serialization")
        ),
        "deepspeed-checkpoint-manifest-v1.schema.json": (
            DeepSpeedCheckpointManifest.model_json_schema(mode="serialization")
        ),
        "deepspeed-qualification-v1.schema.json": (
            DeepSpeedQualificationResult.model_json_schema(mode="serialization")
        ),
        "deepspeed-rank-state-v1.schema.json": (
            DeepSpeedRankCheckpointState.model_json_schema(mode="serialization")
        ),
    }


def write_deepspeed_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(deepspeed_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
