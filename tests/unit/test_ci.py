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


def test_checked_in_policy_loads_through_safe_closed_schema() -> None:
    policy = load_ci_policy(Path("examples/ci/policy.yml"))

    assert policy.unknown_state == "fail"
    assert policy.required_faults == ("process_termination",)
    assert policy.max_rpo_steps == 0
    assert policy.max_rto_seconds == 60.0
    assert policy.require_attestation is True


def test_policy_accepts_the_exact_multi_rank_fault_identifier() -> None:
    policy = _policy(required_faults=("rank_process_termination",))

    assert policy.required_faults == ("rank_process_termination",)


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
    assert emitted.sarif_path.is_file()
    assert "detection.framework" in emitted.junit_path.read_text(encoding="utf-8")
    sarif = json.loads(emitted.sarif_path.read_text(encoding="utf-8"))
    assert sarif["runs"][0]["results"][0]["ruleId"] == "detection.framework"


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


def test_emit_sarif_cli_preserves_unknown_review_exit(tmp_path: Path) -> None:
    result = _unknown_audit()
    (tmp_path / "audit.json").write_text(result.model_dump_json() + "\n", encoding="utf-8")

    invocation = CliRunner().invoke(
        app,
        ["emit-sarif", "--run-dir", str(tmp_path)],
    )

    assert invocation.exit_code == EXIT_REVIEW
    assert "UNKNOWN" in invocation.output
    assert "results.sarif" in invocation.output
    assert (tmp_path / "results.sarif").is_file()


def test_stable_exit_code_contract() -> None:
    assert (EXIT_VERIFIED, EXIT_REVIEW, EXIT_QUALIFICATION_FAILED) == (0, 2, 3)
    assert (EXIT_INVALID_EVIDENCE, EXIT_UNSUPPORTED) == (4, 5)


def test_checked_in_policy_schema_matches_generator() -> None:
    actual = json.loads(Path("schemas/ci-policy-v1.schema.json").read_text(encoding="utf-8"))
    assert actual == ci_policy_schema_document()


def test_active_github_actions_workflow_preserves_qualification_and_quality_guards() -> None:
    example_path = Path("examples/github-actions/flashpilot-qualification.yml")
    active_path = Path(".github/workflows/flashpilot-qualification.yml")
    example = yaml.load(example_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    workflow = yaml.load(active_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    assert workflow["on"]["pull_request"]["branches"] == ["main"]
    assert "workflow_dispatch" in workflow["on"]
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["qualify-checkpoint"]["permissions"] == {
        "contents": "read",
        "id-token": "write",
        "attestations": "write",
    }
    assert (
        example["jobs"]["qualify-checkpoint"]["permissions"]
        == workflow["jobs"]["qualify-checkpoint"]["permissions"]
    )
    assert (
        workflow["jobs"]["qualify-checkpoint"]["steps"]
        == example["jobs"]["qualify-checkpoint"]["steps"]
    )

    quality = workflow["jobs"]["quality"]
    assert quality["runs-on"] == "ubuntu-latest"
    assert quality["strategy"]["matrix"]["python-version"] == ["3.11", "3.12"]
    assert [step["run"] for step in quality["steps"] if "run" in step] == [
        'python -m pip install ".[dev,hf]"',
        "python -m ruff check .",
        "python -m ruff format --check .",
        "python -m pytest -q",
    ]

    steps = workflow["jobs"]["qualify-checkpoint"]["steps"]
    diagnostic_upload = next(
        step for step in steps if step.get("name") == "Upload diagnostic reports, JUnit, and SARIF"
    )
    attestation_upload = next(
        step
        for step in steps
        if step.get("name") == "Upload verified recovery attestations and provenance"
    )

    assert diagnostic_upload["if"] == "always()"
    assert attestation_upload["if"] == "success()"
    assert "runs/**/recovery.attestation.json" in attestation_upload["with"]["path"]
    assert "runs/**/recovery.attestation.signature.json" in attestation_upload["with"]["path"]
    assert "runs/ci-signing/ed25519-public.pem" in attestation_upload["with"]["path"]
    assert "examples/ci/qualification-policy.yml" in attestation_upload["with"]["path"]
    assert "runs/ci-policy/policy-evaluation.json" in attestation_upload["with"]["path"]
    assert (
        "runs/ci-provenance/github-oidc-provenance.sigstore.json"
        in attestation_upload["with"]["path"]
    )
    assert "runs/ci-provenance/verification.json" in attestation_upload["with"]["path"]
    assert "runs/ci-provenance" not in diagnostic_upload["with"]["path"]
    assert "ed25519-private.pem" not in attestation_upload["with"]["path"]
    assert "runs/**/results.sarif" in diagnostic_upload["with"]["path"]
    assert "runs/**/audit.json" in diagnostic_upload["with"]["path"]
    assert "runs/**/policy-evaluation.json" in diagnostic_upload["with"]["path"]
    assert "examples/ci/qualification-policy.yml" in diagnostic_upload["with"]["path"]
    assert "schemas/attestation-signature-v1.schema.json" in diagnostic_upload["with"]["path"]
    assert "schemas/qualification-policy-v1.schema.json" in diagnostic_upload["with"]["path"]
    assert (
        "schemas/qualification-policy-evaluation-v1.schema.json"
        in diagnostic_upload["with"]["path"]
    )
    serialized = active_path.read_text(encoding="utf-8")
    for required in (
        "flashpilot audit-checkpoint",
        "flashpilot qualify hf-trainer",
        "flashpilot qualify distributed-pytorch",
        "--strategy fsdp",
        "flashpilot qualify deepspeed",
        "--zero-stage 2",
        "--backend gloo",
        "--world-size 2",
        "flashpilot certify-preemption",
        "--signal SIGTERM",
        "--grace-period 300",
        "flashpilot emit-junit",
        "flashpilot generate-signing-key",
        "flashpilot sign-attestation",
        "flashpilot enforce-policy",
        "--policy examples/ci/qualification-policy.yml",
        "--public-key runs/ci-signing/ed25519-public.pem",
        "--run hf-process-termination=runs/ci-hf",
        "--run fsdp-checkpoint-restart=runs/ci-distributed",
        "--run fsdp-rank-termination-0=runs/ci-distributed-fault-rank-0",
        "--run fsdp-rank-termination-1=runs/ci-distributed-fault-rank-1",
        "--run deepspeed-checkpoint-restart=runs/ci-deepspeed",
        "--run deepspeed-rank-termination-0=runs/ci-deepspeed-fault-rank-0",
        "--run deepspeed-rank-termination-1=runs/ci-deepspeed-fault-rank-1",
        "--run hf-managed-preemption=runs/ci-preemption",
        "--run hf-static-audit=runs/ci-audit",
        "uses: actions/attest@v4",
        "subject-path: runs/ci-policy/policy-evaluation.json",
        "gh attestation verify runs/ci-policy/policy-evaluation.json",
        '--repo "${GITHUB_REPOSITORY}"',
        '--signer-workflow "${GITHUB_REPOSITORY}/.github/workflows/flashpilot-qualification.yml"',
        '--signer-digest "${GITHUB_WORKFLOW_SHA}"',
        '--source-digest "${GITHUB_SHA}"',
        '--source-ref "${GITHUB_REF}"',
        '--predicate-type "https://slsa.dev/provenance/v1"',
        '--cert-oidc-issuer "https://token.actions.githubusercontent.com"',
        "--deny-self-hosted-runners",
        'rm -f -- "${RUNNER_TEMP}/flashpilot-signing-key/ed25519-private.pem"',
    ):
        assert required in serialized
    for forbidden in (
        "OPENAI_API_KEY",
        "live-contract",
        "live-failure",
        "push-to-registry",
        "artifact-metadata: write",
        "packages: write",
        "runs-on: self-hosted",
        "secrets.",
    ):
        assert forbidden not in serialized

    oidc_step = next(step for step in steps if step.get("id") == "oidc-provenance")
    policy_step_index = next(
        index
        for index, step in enumerate(steps)
        if step.get("name") == "Enforce the complete typed qualification-suite policy"
    )
    oidc_step_index = steps.index(oidc_step)
    assert oidc_step_index > policy_step_index
    assert oidc_step == {
        "name": "Attest the verified suite with GitHub OIDC provenance",
        "if": "success()",
        "id": "oidc-provenance",
        "uses": "actions/attest@v4",
        "with": {"subject-path": "runs/ci-policy/policy-evaluation.json"},
    }
