from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from flashpilot.audit.models import (
    AuditCheck,
    AuditFramework,
    AuditStatus,
    StaticAuditResult,
)
from flashpilot.ci.exits import (
    EXIT_INVALID_EVIDENCE,
    EXIT_QUALIFICATION_FAILED,
    EXIT_REVIEW,
    EXIT_UNSUPPORTED,
    EXIT_VERIFIED,
)
from flashpilot.ci.models import (
    CICheck,
    CICheckStatus,
    CIPolicyV1,
    CIRunEvidence,
    CIStatus,
)
from flashpilot.ci.policy import CIPolicyError, evaluate_ci_policy, load_ci_policy
from flashpilot.ci.reporters import render_job_summary, render_qualification_junit
from flashpilot.ci.schema import ci_policy_schema_document
from flashpilot.ci.service import emit_ci_outputs, normalize_run_evidence
from flashpilot.cli import app
from flashpilot.contracts.models import QualificationProfile


def _policy(**updates: object) -> CIPolicyV1:
    values: dict[str, object] = {
        "required_faults": ("process_termination",),
        "max_rpo_steps": 0,
        "max_rto_seconds": 60.0,
        "require_attestation": False,
    }
    values.update(updates)
    return CIPolicyV1(**values)


def _unknown_audit() -> StaticAuditResult:
    return StaticAuditResult(
        status=AuditStatus.UNKNOWN,
        framework=AuditFramework.UNKNOWN,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        checkpoint_name="unknown-checkpoint",
        checks=(
            AuditCheck(
                check_id="detection.framework",
                status=AuditStatus.UNKNOWN,
                summary="Layout is unknown and was not trusted.",
            ),
        ),
    )


def _failed_qualification() -> CIRunEvidence:
    return CIRunEvidence(
        kind="hf-qualification",
        status=CIStatus.FAILED,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="huggingface-trainer",
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
    )


def test_checked_in_policy_loads_through_safe_closed_schema() -> None:
    policy = load_ci_policy(Path("examples/ci/policy.yml"))

    assert policy.unknown_state == "fail"
    assert policy.required_faults == ("process_termination",)
    assert policy.max_rpo_steps == 0
    assert policy.max_rto_seconds == 60.0
    assert policy.require_attestation is True


@pytest.mark.parametrize(
    "update",
    [
        {"unknown_state": "pass"},
        {"required_faults": ["shell-command"]},
        {"max_rpo_steps": -1},
        {"arbitrary_expression": "result or true"},
    ],
)
def test_policy_rejects_weak_or_arbitrary_configuration(update: dict[str, object]) -> None:
    values = _policy().model_dump(mode="python")
    values.update(update)
    with pytest.raises(ValidationError):
        CIPolicyV1.model_validate(values)


def test_policy_loader_rejects_yaml_object_construction(tmp_path: Path) -> None:
    policy = tmp_path / "unsafe.yml"
    policy.write_text("!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8")

    with pytest.raises(CIPolicyError):
        load_ci_policy(policy)


def test_unknown_audit_never_becomes_pass_under_policy(tmp_path: Path) -> None:
    evidence = normalize_run_evidence(_unknown_audit())
    evaluation = evaluate_ci_policy(run_root=tmp_path, evidence=evidence, policy=_policy())

    assert evidence.status is CIStatus.UNKNOWN
    assert evaluation.passed is False
    assert "policy.unknown-state" in evaluation.failed_check_ids


def test_policy_enforces_rpo_and_rto_with_exact_check_ids(tmp_path: Path) -> None:
    evidence = _failed_qualification().model_copy(update={"rpo_steps": 2, "rto_seconds": 61.0})
    evaluation = evaluate_ci_policy(run_root=tmp_path, evidence=evidence, policy=_policy())

    assert evaluation.passed is False
    assert evaluation.failed_check_ids == (
        "policy.qualification-verdict",
        "policy.max-rpo",
        "policy.max-rto",
    )


def test_junit_and_markdown_name_exact_failed_requirement() -> None:
    evidence = _failed_qualification()
    junit = render_qualification_junit(evidence)
    summary = render_job_summary(evidence)
    suite = ElementTree.fromstring(junit)

    assert suite.attrib["tests"] == "2"
    assert suite.attrib["failures"] == "1"
    failure_case = suite.find("./testcase[@name='checkpoint.optimizer']/failure")
    assert failure_case is not None
    assert "Expected=present; actual=missing" in (failure_case.text or "")
    assert "`checkpoint.optimizer`" in summary


def test_emit_ci_outputs_preserves_unknown_review_exit_without_policy(tmp_path: Path) -> None:
    result = _unknown_audit()
    (tmp_path / "audit.json").write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    emitted = emit_ci_outputs(run_root=tmp_path)

    assert emitted.exit_code == EXIT_REVIEW
    assert emitted.junit_path.is_file()
    assert emitted.job_summary_path.is_file()
    assert "detection.framework" in emitted.junit_path.read_text(encoding="utf-8")


def test_emit_junit_cli_turns_unknown_into_policy_failure(tmp_path: Path) -> None:
    result = _unknown_audit()
    (tmp_path / "audit.json").write_text(result.model_dump_json() + "\n", encoding="utf-8")

    invocation = CliRunner().invoke(
        app,
        [
            "emit-junit",
            "--run-dir",
            str(tmp_path),
            "--policy",
            "examples/ci/policy.yml",
        ],
    )

    assert invocation.exit_code == EXIT_QUALIFICATION_FAILED
    assert "FAILED REQUIREMENT policy.unknown-state" in invocation.output


def test_stable_exit_code_contract() -> None:
    assert (EXIT_VERIFIED, EXIT_REVIEW, EXIT_QUALIFICATION_FAILED) == (0, 2, 3)
    assert (EXIT_INVALID_EVIDENCE, EXIT_UNSUPPORTED) == (4, 5)


def test_checked_in_policy_schema_matches_generator() -> None:
    actual = json.loads(Path("schemas/ci-policy-v1.schema.json").read_text(encoding="utf-8"))
    assert actual == ci_policy_schema_document()


def test_github_actions_example_is_noninstalled_and_uploads_attestation_only_on_success() -> None:
    path = Path("examples/github-actions/flashpilot-qualification.yml")
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["qualify-checkpoint"]["steps"]
    attestation_upload = next(
        step for step in steps if step.get("name") == "Upload verified recovery attestation"
    )

    assert not Path(".github/workflows/flashpilot-qualification.yml").exists()
    assert attestation_upload["if"] == "success()"
    assert attestation_upload["with"]["path"] == "runs/**/recovery.attestation.json"
    serialized = path.read_text(encoding="utf-8")
    assert "flashpilot audit-checkpoint" in serialized
    assert "flashpilot qualify hf-trainer" in serialized
    assert "flashpilot emit-junit" in serialized
