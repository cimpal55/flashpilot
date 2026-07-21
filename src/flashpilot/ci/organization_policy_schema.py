"""Public JSON Schemas for closed organization qualification policy."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.ci.organization_policy_models import (
    OrganizationPolicyEvaluationV1,
    OrganizationQualificationPolicyV1,
)


def organization_policy_schema_documents() -> dict[str, dict[str, object]]:
    return {
        "organization-qualification-policy-v1.schema.json": (
            OrganizationQualificationPolicyV1.model_json_schema(mode="serialization")
        ),
        "organization-policy-evaluation-v1.schema.json": (
            OrganizationPolicyEvaluationV1.model_json_schema(mode="serialization")
        ),
    }


def write_organization_policy_schema_files(schema_root: Path) -> tuple[Path, ...]:
    schema_root.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, document in sorted(organization_policy_schema_documents().items()):
        path = schema_root / filename
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        paths.append(path)
    return tuple(paths)
