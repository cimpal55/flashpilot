"""Deterministic public JSON Schemas for local attestation registries."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.registry.models import (
    AttestationRegistryCompletionV1,
    AttestationRegistryEntryV1,
    AttestationRegistryHeadV1,
    AttestationRegistryHistoryV1,
    AttestationRegistryMetadataV1,
)


def registry_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "attestation-registry-completion-v1.schema.json": (
            AttestationRegistryCompletionV1.model_json_schema(mode="serialization")
        ),
        "attestation-registry-entry-v1.schema.json": AttestationRegistryEntryV1.model_json_schema(
            mode="serialization"
        ),
        "attestation-registry-history-v1.schema.json": (
            AttestationRegistryHistoryV1.model_json_schema(mode="serialization")
        ),
        "attestation-registry-head-v1.schema.json": AttestationRegistryHeadV1.model_json_schema(
            mode="serialization"
        ),
        "attestation-registry-v1.schema.json": AttestationRegistryMetadataV1.model_json_schema(
            mode="serialization"
        ),
    }


def write_registry_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(registry_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
