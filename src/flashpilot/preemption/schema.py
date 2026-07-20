"""Deterministic JSON Schemas for managed-preemption evidence."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.preemption.models import (
    HFPreemptionCertificationResult,
    HFPreemptionCommitEvidence,
    HFPreemptionReadyEvidence,
)


def preemption_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "hf-preemption-certification-v1.schema.json": (
            HFPreemptionCertificationResult.model_json_schema(mode="serialization")
        ),
        "hf-preemption-commit-v1.schema.json": HFPreemptionCommitEvidence.model_json_schema(
            mode="serialization"
        ),
        "hf-preemption-ready-v1.schema.json": HFPreemptionReadyEvidence.model_json_schema(
            mode="serialization"
        ),
    }


def write_preemption_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(preemption_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
