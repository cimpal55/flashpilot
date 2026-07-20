from __future__ import annotations

import hashlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from flashpilot.audit.models import AuditCheck, AuditFramework, AuditStatus, StaticAuditResult
from flashpilot.ci.exits import (
    EXIT_INVALID_EVIDENCE,
    EXIT_QUALIFICATION_FAILED,
    EXIT_UNSUPPORTED,
)
from flashpilot.ci.models import CICheck, CICheckStatus, CIRunEvidence, CIStatus
from flashpilot.ci.qualification_policy import (
    QualificationPolicyError,
    enforce_qualification_policy,
    evaluate_qualification_policy,
    load_qualification_policy,
    parse_policy_run_bindings,
)
from flashpilot.ci.qualification_policy_models import (
    DeepSpeedPolicyRequirement,
    DistributedPolicyRequirement,
    QualificationPolicyEvaluationV1,
    QualificationPolicyEvidence,
    QualificationPolicyRequirement,
    QualificationPolicyV1,
    StaticAuditPolicyRequirement,
)
from flashpilot.ci.qualification_policy_reporters import (
    render_qualification_policy_junit,
    render_qualification_policy_sarif,
    render_qualification_policy_summary,
)
from flashpilot.ci.qualification_policy_schema import (
    qualification_policy_evaluation_schema_document,
    qualification_policy_schema_document,
)
from flashpilot.cli import app
from flashpilot.contracts.models import QualificationProfile

_POLICY_PATH = Path("examples/ci/qualification-policy.yml")


def _pass_check() -> tuple[CICheck, ...]:
    return (
        CICheck(
            check_id="gate.proof",
            status=CICheckStatus.PASS,
            summary="Deterministic proof passed.",
        ),
    )


def _evidence_for(requirement: QualificationPolicyRequirement) -> QualificationPolicyEvidence:
    if isinstance(requirement, StaticAuditPolicyRequirement):
        evidence = CIRunEvidence(
            kind="static-audit",
            status=CIStatus.PASS,
            qualification_profile=requirement.qualification_profile,
            framework=requirement.framework,
            checks=_pass_check(),
        )
        return QualificationPolicyEvidence(
            source_artifact="audit.json",
            source_sha256="a" * 64,
            attestation_status="not-applicable",
            evidence=evidence,
        )

    values: dict[str, object] = {
        "kind": requirement.kind,
        "status": CIStatus.VERIFIED,
        "qualification_profile": requirement.qualification_profile,
        "framework": requirement.framework,
        "adapter": requirement.adapter,
        "checks": _pass_check(),
        "fault": requirement.fault,
        "rpo_steps": 0,
        "rto_seconds": 1.0,
        "atol": 0.0,
        "rtol": 0.0,
    }
    if isinstance(requirement, (DistributedPolicyRequirement, DeepSpeedPolicyRequirement)):
        values.update(
            strategy=requirement.strategy,
            implementation=requirement.implementation,
            backend=requirement.backend,
            world_size=requirement.world_size,
            fault_target_rank=requirement.fault_target_rank,
        )
        if isinstance(requirement, DeepSpeedPolicyRequirement):
            values["zero_stage"] = requirement.zero_stage
    evidence = CIRunEvidence.model_validate(values)
    return QualificationPolicyEvidence(
        source_artifact="result.json",
        source_sha256="a" * 64,
        attestation_status="verified",
        attestation_sha256="b" * 64,
        evidence=evidence,
    )


def _loaded_policy() -> QualificationPolicyV1:
    return load_qualification_policy(_POLICY_PATH).policy


def _static_policy() -> QualificationPolicyV1:
    return QualificationPolicyV1(
        policy_id="static-audit-only",
        requirements=(
            StaticAuditPolicyRequirement(
                requirement_id="hf-static-audit",
                kind="static-audit",
                framework="huggingface-trainer",
                qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
            ),
        ),
    )


def _write_policy(path: Path, policy: QualificationPolicyV1) -> None:
    path.write_text(
        yaml.safe_dump(policy.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def _write_passing_audit(root: Path) -> None:
    root.mkdir()
    result = StaticAuditResult(
        status=AuditStatus.PASS,
        framework=AuditFramework.HUGGINGFACE_TRAINER,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        checkpoint_name="checkpoint-4",
        checks=(
            AuditCheck(
                check_id="inventory.closed",
                status=AuditStatus.PASS,
                summary="Inventory is closed.",
            ),
        ),
    )
    (root / "audit.json").write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")


def test_checked_in_qualification_policy_is_exact_closed_nine_run_matrix() -> None:
    loaded = load_qualification_policy(_POLICY_PATH)
    policy = loaded.policy

    assert policy.policy_id == "flashpilot-v1-production-suite"
    assert policy.unknown_state == "fail"
    assert policy.evidence_binding == "explicit"
    assert len(policy.requirements) == 9
    assert tuple(item.requirement_id for item in policy.requirements) == (
        "hf-process-termination",
        "fsdp-checkpoint-restart",
        "fsdp-rank-termination-0",
        "fsdp-rank-termination-1",
        "deepspeed-checkpoint-restart",
        "deepspeed-rank-termination-0",
        "deepspeed-rank-termination-1",
        "hf-managed-preemption",
        "hf-static-audit",
    )
    assert loaded.source_sha256 == hashlib.sha256(_POLICY_PATH.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    "update",
    [
        {"unknown_state": "pass"},
        {"evidence_binding": "scan"},
        {"all_requirements_must_pass": False},
        {"arbitrary_expression": "evidence.status == 'VERIFIED'"},
    ],
)
def test_policy_rejects_weakened_or_executable_configuration(update: dict[str, object]) -> None:
    values = _static_policy().model_dump(mode="python")
    values.update(update)

    with pytest.raises(ValidationError):
        QualificationPolicyV1.model_validate(values)


def test_policy_rejects_duplicate_ids_and_duplicate_selectors() -> None:
    requirement = _static_policy().requirements[0]
    with pytest.raises(ValidationError):
        QualificationPolicyV1(
            policy_id="duplicate",
            requirements=(requirement, requirement),
        )
    duplicate_selector = requirement.model_copy(update={"requirement_id": "other-static-audit"})
    with pytest.raises(ValidationError):
        QualificationPolicyV1(
            policy_id="duplicate-selector",
            requirements=(requirement, duplicate_selector),
        )


def test_distributed_policy_schema_rejects_contradictory_target_identity() -> None:
    values = next(
        item.model_dump(mode="python")
        for item in _loaded_policy().requirements
        if item.requirement_id == "fsdp-rank-termination-0"
    )
    values["fault_target_rank"] = None
    with pytest.raises(ValidationError, match="requires target rank"):
        DistributedPolicyRequirement.model_validate(values)

    clean = next(
        item.model_dump(mode="python")
        for item in _loaded_policy().requirements
        if item.requirement_id == "deepspeed-checkpoint-restart"
    )
    clean["fault_target_rank"] = 1
    with pytest.raises(ValidationError, match="cannot select a target rank"):
        DeepSpeedPolicyRequirement.model_validate(clean)


def test_policy_loader_rejects_yaml_object_construction(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.yml"
    path.write_text("!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8")

    with pytest.raises(QualificationPolicyError):
        load_qualification_policy(path)


def test_policy_loader_rejects_oversized_source(tmp_path: Path) -> None:
    path = tmp_path / "oversized.yml"
    path.write_text("x" * (64 * 1024 + 1), encoding="utf-8")

    with pytest.raises(QualificationPolicyError, match="64 KiB"):
        load_qualification_policy(path)


def test_explicit_binding_parser_rejects_duplicates_and_untyped_values() -> None:
    assert parse_policy_run_bindings(["hf-run=runs/hf"]) == {"hf-run": Path("runs/hf")}
    with pytest.raises(QualificationPolicyError, match="duplicate"):
        parse_policy_run_bindings(["hf-run=runs/one", "hf-run=runs/two"])
    with pytest.raises(QualificationPolicyError, match="requirement-id"):
        parse_policy_run_bindings(["runs/hf"])


def test_complete_explicit_matrix_passes_all_typed_requirements() -> None:
    policy = _loaded_policy()
    evidence = {
        requirement.requirement_id: _evidence_for(requirement)
        for requirement in policy.requirements
    }

    evaluation = evaluate_qualification_policy(
        policy=policy,
        policy_sha256="c" * 64,
        evidence_by_requirement=evidence,
    )

    assert evaluation.passed is True
    assert evaluation.failed_requirement_ids == ()
    assert all(check.status is CICheckStatus.PASS for check in evaluation.checks)


def test_missing_evidence_fails_with_exact_requirement_id() -> None:
    policy = _static_policy()

    evaluation = evaluate_qualification_policy(
        policy=policy,
        policy_sha256="c" * 64,
        evidence_by_requirement={},
    )

    assert evaluation.passed is False
    assert evaluation.failed_requirement_ids == ("hf-static-audit",)
    assert evaluation.requirements[0].failed_check_ids == (
        "policy.hf-static-audit.evidence-present",
    )


def test_unknown_state_and_underlying_unknown_check_fail_closed() -> None:
    policy = _static_policy()
    requirement = policy.requirements[0]
    unknown = QualificationPolicyEvidence(
        source_artifact="audit.json",
        source_sha256="a" * 64,
        attestation_status="not-applicable",
        evidence=CIRunEvidence(
            kind="static-audit",
            status=CIStatus.UNKNOWN,
            qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
            framework="huggingface-trainer",
            checks=(
                CICheck(
                    check_id="detection.framework",
                    status=CICheckStatus.UNKNOWN,
                    summary="Framework is unknown.",
                ),
            ),
        ),
    )

    evaluation = evaluate_qualification_policy(
        policy=policy,
        policy_sha256="c" * 64,
        evidence_by_requirement={requirement.requirement_id: unknown},
    )

    assert evaluation.passed is False
    assert set(evaluation.requirements[0].failed_check_ids) >= {
        "policy.hf-static-audit.unknown-state",
        "policy.hf-static-audit.required-status",
        "policy.hf-static-audit.checks",
    }


def test_wrong_target_rank_cannot_satisfy_other_rank_requirement() -> None:
    policy = _loaded_policy()
    target_zero = next(item for item in policy.requirements if item.requirement_id.endswith("-0"))
    target_one = next(
        item
        for item in policy.requirements
        if item.requirement_id == target_zero.requirement_id.removesuffix("-0") + "-1"
    )

    evaluation = evaluate_qualification_policy(
        policy=QualificationPolicyV1(policy_id="target-zero", requirements=(target_zero,)),
        policy_sha256="c" * 64,
        evidence_by_requirement={target_zero.requirement_id: _evidence_for(target_one)},
    )

    assert evaluation.passed is False
    assert evaluation.requirements[0].failed_check_ids == (
        f"policy.{target_zero.requirement_id}.fault-target-rank",
    )


def test_runtime_bounds_exactness_and_attestation_fail_independently() -> None:
    policy = _loaded_policy()
    requirement = policy.requirements[0]
    bound = _evidence_for(requirement)
    weakened = bound.evidence.model_copy(update={"rpo_steps": 1, "rto_seconds": 61.0, "atol": 1e-6})
    evidence = QualificationPolicyEvidence(
        source_artifact="result.json",
        source_sha256="a" * 64,
        attestation_status="missing",
        evidence=weakened,
    )

    evaluation = evaluate_qualification_policy(
        policy=QualificationPolicyV1(policy_id="bounded", requirements=(requirement,)),
        policy_sha256="c" * 64,
        evidence_by_requirement={requirement.requirement_id: evidence},
    )

    assert evaluation.requirements[0].failed_check_ids == (
        "policy.hf-process-termination.exact-recovery",
        "policy.hf-process-termination.max-rpo",
        "policy.hf-process-termination.max-rto",
        "policy.hf-process-termination.attestation",
    )


def test_unlisted_evidence_binding_is_rejected_without_scanning() -> None:
    with pytest.raises(QualificationPolicyError, match="unlisted"):
        evaluate_qualification_policy(
            policy=_static_policy(),
            policy_sha256="c" * 64,
            evidence_by_requirement={"unlisted": _evidence_for(_static_policy().requirements[0])},
        )


def test_static_policy_cli_persists_deterministic_json_junit_summary_and_sarif(
    tmp_path: Path,
) -> None:
    policy_path = tmp_path / "policy.yml"
    run_root = tmp_path / "audit-run"
    output_root = tmp_path / "policy-output"
    _write_policy(policy_path, _static_policy())
    _write_passing_audit(run_root)

    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"hf-static-audit={run_root}",
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "POLICY PASS" in invocation.output
    assert "Requirements: 1/1" in invocation.output
    evaluation = QualificationPolicyEvaluationV1.model_validate_json(
        (output_root / "policy-evaluation.json").read_text(encoding="utf-8")
    )
    assert evaluation.passed is True
    junit = ElementTree.parse(output_root / "junit.xml").getroot()
    assert junit.attrib["failures"] == "0"
    assert "Exact failed requirements" in (output_root / "job-summary.md").read_text(
        encoding="utf-8"
    )
    sarif = json.loads((output_root / "results.sarif").read_text(encoding="utf-8"))
    assert sarif["runs"][0]["results"] == []
    assert set(item.name for item in output_root.iterdir()) == {
        "policy-evaluation.json",
        "junit.xml",
        "job-summary.md",
        "results.sarif",
    }
    before = {item.name: item.read_bytes() for item in output_root.iterdir()}
    repeated = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"hf-static-audit={run_root}",
        ],
    )
    assert repeated.exit_code == 0, repeated.output
    assert {item.name: item.read_bytes() for item in output_root.iterdir()} == before


def test_missing_binding_persists_failed_policy_artifacts(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yml"
    output_root = tmp_path / "policy-output"
    _write_policy(policy_path, _static_policy())

    result = enforce_qualification_policy(
        policy_path=policy_path,
        run_bindings={},
        output_dir=output_root,
    )

    assert result.exit_code == EXIT_QUALIFICATION_FAILED
    assert result.evaluation.failed_requirement_ids == ("hf-static-audit",)
    assert "policy.hf-static-audit.evidence-present" in result.junit_path.read_text(
        encoding="utf-8"
    )


def test_policy_output_cannot_mutate_bound_run_or_accept_stale_artifacts(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.yml"
    run_root = tmp_path / "audit-run"
    _write_policy(policy_path, _static_policy())
    _write_passing_audit(run_root)

    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(run_root / "policy"),
            "--run",
            f"hf-static-audit={run_root}",
        ],
    )
    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert not (run_root / "policy").exists()

    output = tmp_path / "stale"
    output.mkdir()
    (output / "unexpected.txt").write_text("stale", encoding="utf-8")
    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output),
            "--run",
            f"hf-static-audit={run_root}",
        ],
    )
    assert invocation.exit_code == EXIT_INVALID_EVIDENCE


def test_policy_reporters_name_exact_failed_requirements() -> None:
    evaluation = evaluate_qualification_policy(
        policy=_static_policy(),
        policy_sha256="c" * 64,
        evidence_by_requirement={},
    )

    junit = render_qualification_policy_junit(evaluation)
    summary = render_qualification_policy_summary(evaluation)
    sarif = json.loads(render_qualification_policy_sarif(evaluation))

    assert "policy.hf-static-audit.evidence-present" in junit
    assert "`policy.hf-static-audit.evidence-present`" in summary
    assert sarif["runs"][0]["results"][0]["ruleId"] == ("policy.hf-static-audit.evidence-present")
    assert (
        sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"][
            "uri"
        ]
        == "policy-evaluation.json"
    )

    payload = evaluation.model_dump(mode="python")
    payload["passed"] = True
    with pytest.raises(ValidationError, match="derive from every requirement"):
        QualificationPolicyEvaluationV1.model_validate(payload)


def test_checked_in_policy_schemas_match_generators() -> None:
    policy = json.loads(Path("schemas/qualification-policy-v1.schema.json").read_text("utf-8"))
    evaluation = json.loads(
        Path("schemas/qualification-policy-evaluation-v1.schema.json").read_text("utf-8")
    )

    assert policy == qualification_policy_schema_document()
    assert evaluation == qualification_policy_evaluation_schema_document()
