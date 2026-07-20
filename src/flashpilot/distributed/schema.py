"""Deterministic public JSON Schemas for distributed qualification evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.distributed.models import (
    DistributedCheckpointEvent,
    DistributedCheckpointManifest,
    DistributedQualificationResult,
    DistributedRankCheckpointState,
)


def distributed_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "distributed-checkpoint-event-v1.schema.json": (
            DistributedCheckpointEvent.model_json_schema(mode="serialization")
        ),
        "distributed-checkpoint-manifest-v1.schema.json": (
            DistributedCheckpointManifest.model_json_schema(mode="serialization")
        ),
        "distributed-qualification-v1.schema.json": (
            DistributedQualificationResult.model_json_schema(mode="serialization")
        ),
        "distributed-rank-state-v1.schema.json": (
            DistributedRankCheckpointState.model_json_schema(mode="serialization")
        ),
    }


def write_distributed_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(distributed_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
