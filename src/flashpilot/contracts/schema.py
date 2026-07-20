"""Deterministic JSON Schema export for the vNext contract boundary."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
)

SCHEMA_FILENAMES = (
    "persistence-contract-v1.schema.json",
    "persistence-item-v1.schema.json",
    "qualification-profile-v1.schema.json",
)


def schema_documents() -> dict[str, dict[str, object]]:
    """Return all public contract schemas with stable draft and identifier metadata."""

    documents: dict[str, dict[str, object]] = {
        SCHEMA_FILENAMES[0]: PersistenceContract.model_json_schema(),
        SCHEMA_FILENAMES[1]: PersistenceItem.model_json_schema(),
        SCHEMA_FILENAMES[2]: TypeAdapter(QualificationProfile).json_schema(),
    }
    for filename, document in documents.items():
        document["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        document["$id"] = f"https://schemas.flashpilot.dev/{filename}"
    return documents


def write_schema_files(output_directory: Path) -> tuple[Path, ...]:
    """Write public schemas using deterministic formatting."""

    output_directory.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in schema_documents().items():
        path = output_directory / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
