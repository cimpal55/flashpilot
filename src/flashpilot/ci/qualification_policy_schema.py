"""Public JSON Schemas for typed qualification policy and evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.ci.qualification_policy_models import (
    QualificationPolicyEvaluationV1,
    QualificationPolicyV1,
)


def qualification_policy_schema_document() -> dict[str, object]:
    return QualificationPolicyV1.model_json_schema(mode="serialization")


def qualification_policy_evaluation_schema_document() -> dict[str, object]:
    return QualificationPolicyEvaluationV1.model_json_schema(mode="serialization")


def write_qualification_policy_schemas(*, policy_path: Path, evaluation_path: Path) -> None:
    policy_path.write_text(
        json.dumps(qualification_policy_schema_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    evaluation_path.write_text(
        json.dumps(qualification_policy_evaluation_schema_document(), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
