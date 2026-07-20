"""Deterministic schemas for multi-rank failure evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.multirank.models import (
    MultiRankFailureEvent,
    MultiRankFaultReadyEvidence,
    MultiRankPeerFailureEvidence,
)


def multi_rank_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "multi-rank-failure-event-v1.schema.json": MultiRankFailureEvent.model_json_schema(
            mode="serialization"
        ),
        "multi-rank-fault-ready-v1.schema.json": MultiRankFaultReadyEvidence.model_json_schema(
            mode="serialization"
        ),
        "multi-rank-peer-failure-v1.schema.json": MultiRankPeerFailureEvidence.model_json_schema(
            mode="serialization"
        ),
    }


def write_multi_rank_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(multi_rank_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
