from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.ci.models import (
    CICheck,
    CICheckStatus,
    CIRunEvidence,
    CIStatus,
)
from flashpilot.ci.sarif import (
    SARIF_SCHEMA_URI,
    FlashPilotSarifLog,
    build_sarif_log,
    render_sarif,
)
from flashpilot.ci.sarif_schema import sarif_schema_document
from flashpilot.contracts.models import QualificationProfile


def _failed_evidence() -> CIRunEvidence:
    return CIRunEvidence(
        kind="hf-qualification",
        status=CIStatus.FAILED,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="huggingface-trainer",
        adapter="huggingface-trainer",
        checks=(
            CICheck(
                check_id="checkpoint.optimizer",
                status=CICheckStatus.FAIL,
                summary="Optimizer state is missing.",
                expected="present",
                actual="missing",
            ),
            CICheck(
                check_id="checkpoint.model",
                status=CICheckStatus.PASS,
                summary="Model state is present.",
            ),
        ),
        fault="process_termination",
        rpo_steps=0,
        rto_seconds=4.0,
        atol=0.0,
        rtol=0.0,
    )


def test_sarif_preserves_exact_failed_check_without_creating_pass_alerts() -> None:
    evidence = _failed_evidence()
    document = json.loads(render_sarif(evidence))
    validated = FlashPilotSarifLog.model_validate(document)
    run = document["runs"][0]

    assert validated.version == "2.1.0"
    assert document["$schema"] == SARIF_SCHEMA_URI
    assert run["tool"]["driver"]["name"] == "FlashPilot"
    assert [rule["id"] for rule in run["tool"]["driver"]["rules"]] == [
        "checkpoint.optimizer",
        "checkpoint.model",
    ]
    assert len(run["results"]) == 1
    result = run["results"][0]
    assert result["ruleId"] == "checkpoint.optimizer"
    assert result["ruleIndex"] == 0
    assert result["level"] == "error"
    assert result["properties"] == {
        "actual": "missing",
        "evidenceKind": "hf-qualification",
        "expected": "present",
        "flashpilotStatus": "FAIL",
        "framework": "huggingface-trainer",
    }
    assert result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == ("result.json")
    assert len(result["partialFingerprints"]["primaryLocationLineHash"]) == 66
    assert "checkpoint.model" not in {item["ruleId"] for item in run["results"]}


def test_unknown_is_a_warning_at_relative_audit_evidence_location() -> None:
    evidence = CIRunEvidence(
        kind="static-audit",
        status=CIStatus.UNKNOWN,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="unknown",
        checks=(
            CICheck(
                check_id="detection.framework",
                status=CICheckStatus.UNKNOWN,
                summary="Layout is unknown and was not trusted.",
            ),
        ),
    )

    first = build_sarif_log(evidence)
    repeated = build_sarif_log(evidence)
    result = first.runs[0].results[0]

    assert first == repeated
    assert result.level == "warning"
    assert result.properties.flashpilot_status == "UNKNOWN"
    assert result.locations[0].physical_location.artifact_location.uri == "audit.json"
    assert "C:\\" not in render_sarif(evidence)


def test_verified_evidence_has_rules_and_no_dashboard_alerts() -> None:
    failed = _failed_evidence()
    evidence = failed.model_copy(
        update={
            "status": CIStatus.VERIFIED,
            "checks": tuple(
                check.model_copy(
                    update={
                        "status": (
                            CICheckStatus.PASS if index == 0 else CICheckStatus.NOT_APPLICABLE
                        )
                    }
                )
                for index, check in enumerate(failed.checks)
            ),
        }
    )

    run = build_sarif_log(evidence).runs[0]

    assert len(run.tool.driver.rules) == 2
    assert run.results == ()


def test_sarif_model_rejects_result_rule_substitution() -> None:
    payload = build_sarif_log(_failed_evidence()).model_dump(
        mode="json",
        by_alias=True,
        exclude_none=True,
    )
    payload["runs"][0]["results"][0]["ruleId"] = "checkpoint.model"

    with pytest.raises(ValidationError, match="exact rule"):
        FlashPilotSarifLog.model_validate(payload)


def test_checked_in_sarif_projection_schema_matches_generator() -> None:
    actual = json.loads(Path("schemas/flashpilot-sarif-v1.schema.json").read_text(encoding="utf-8"))

    assert actual == sarif_schema_document()
