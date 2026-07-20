"""Checked-in schema generation for the supported FlashPilot SARIF subset."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.ci.sarif import FlashPilotSarifLog


def sarif_schema_document() -> dict[str, object]:
    return FlashPilotSarifLog.model_json_schema(
        mode="serialization",
        by_alias=True,
    )


def write_sarif_schema_file(schema_root: Path) -> Path:
    schema_root.mkdir(parents=True, exist_ok=True)
    path = schema_root / "flashpilot-sarif-v1.schema.json"
    path.write_text(
        json.dumps(sarif_schema_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path
