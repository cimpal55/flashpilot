"""Public deterministic JSON Schema for the closed CI policy."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.ci.models import CIPolicyV1


def ci_policy_schema_document() -> dict[str, object]:
    return CIPolicyV1.model_json_schema(mode="serialization")


def write_ci_policy_schema(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ci_policy_schema_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path
