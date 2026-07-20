"""Deterministic public JSON Schemas for attestation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.attestation.models import EvidenceManifestV1, RecoveryAttestationV1


def attestation_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "evidence-manifest-v1.schema.json": EvidenceManifestV1.model_json_schema(
            mode="serialization"
        ),
        "recovery-attestation-v1.schema.json": RecoveryAttestationV1.model_json_schema(
            mode="serialization"
        ),
    }


def write_attestation_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, document in sorted(attestation_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        written.append(path)
    return tuple(written)
