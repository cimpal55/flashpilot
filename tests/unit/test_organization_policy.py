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
    EXIT_VERIFIED,
)
from flashpilot.ci.models import CICheck, CICheckStatus, CIRunEvidence, CIStatus
from flashpilot.ci.organization_policy import (
    OrganizationPolicyError,
    enforce_organization_policy,
    evaluate_organization_policy,
    load_organization_policy,
)
from flashpilot.ci.organization_policy_models import (
    OrganizationPolicyEvaluationV1,
    OrganizationQualificationPolicyV1,
)
from flashpilot.ci.organization_policy_reporters import (
    render_organization_policy_junit,
    render_organization_policy_sarif,
    render_organization_policy_summary,
)
from flashpilot.ci.organization_policy_schema import organization_policy_schema_documents
from flashpilot.ci.qualification_policy import evaluate_qualification_policy
from flashpilot.ci.qualification_policy_models import (
    DeepSpeedPolicyRequirement,
    DistributedPolicyRequirement,
    HFPolicyRequirement,
    QualificationPolicyEvaluationV1,
    QualificationPolicyEvidence,
    QualificationPolicyV1,
    StaticAuditPolicyRequirement,
)
from flashpilot.cli import app
from flashpilot.contracts.models import QualificationProfile

_ORGANIZATION_POLICY_PATH = Path("examples/ci/organization-policy.yml")
_REPOSITORY_POLICY_PATH = Path("examples/ci/qualification-policy.yml")


def _pass_check() -> tuple[CICheck, ...]:
    return (
        CICheck(
            check_id="gate.proof",
            status=CICheckStatus.PASS,
            summary="Deterministic proof passed.",
        ),
    )


def _static_requirement(requirement_id: str = "hf-static-audit"):
    return StaticAuditPolicyRequirement(
        requirement_id=requirement_id,
        kind="static-audit",
        framework="huggingface-trainer",
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
    )


def _runtime_requirement(
    *,
    requirement_id: str = "hf-process-termination",
    max_rpo_steps: int = 0,
    max_rto_seconds: float = 60.0,
    require_signed_attestation: bool = True,
):
    return HFPolicyRequirement(
        requirement_id=requirement_id,
        kind="hf-qualification",
        framework="huggingface-trainer",
        adapter="huggingface-trainer",
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        fault="process_termination",
        max_rpo_steps=max_rpo_steps,
        max_rto_seconds=max_rto_seconds,
        require_signed_attestation=require_signed_attestation,
    )


def _organization_policy(*requirements) -> OrganizationQualificationPolicyV1:
    return OrganizationQualificationPolicyV1(
        organization_id="example-organization",
        policy_id="production-baseline",
        requirements=tuple(requirements),
    )


def _repository_evaluation(
    policy: QualificationPolicyV1,
    *,
    signed: bool = True,
) -> QualificationPolicyEvaluationV1:
    evidence = {}
    for requirement in policy.requirements:
        if isinstance(requirement, StaticAuditPolicyRequirement):
            normalized = CIRunEvidence(
                kind="static-audit",
                status=CIStatus.PASS,
                qualification_profile=requirement.qualification_profile,
                framework=requirement.framework,
                checks=_pass_check(),
            )
            evidence[requirement.requirement_id] = QualificationPolicyEvidence(
                source_artifact="audit.json",
                source_sha256="a" * 64,
                attestation_status="not-applicable",
                attestation_signature_status="not-applicable",
                evidence=normalized,
            )
            continue
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
        normalized = CIRunEvidence.model_validate(values)
        evidence[requirement.requirement_id] = QualificationPolicyEvidence(
            source_artifact="result.json",
            source_sha256="a" * 64,
            attestation_status="verified",
            attestation_sha256="b" * 64,
            attestation_signature_status="verified" if signed else "unsigned",
            signing_key_sha256="c" * 64 if signed else None,
            signature_artifact_sha256="d" * 64 if signed else None,
            evidence=normalized,
        )
    return evaluate_qualification_policy(
        policy=policy,
        policy_sha256="e" * 64,
        evidence_by_requirement=evidence,
    )


def _evaluation_sha256(evaluation: QualificationPolicyEvaluationV1) -> str:
    value = (
        json.dumps(evaluation.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _evaluate(
    organization_policy: OrganizationQualificationPolicyV1,
    repository_policy: QualificationPolicyV1,
    repository_evaluation: QualificationPolicyEvaluationV1,
) -> OrganizationPolicyEvaluationV1:
    return evaluate_organization_policy(
        policy=organization_policy,
        policy_sha256="f" * 64,
        scope_id="repository-one",
        repository_policy=repository_policy,
        repository_policy_sha256="e" * 64,
        repository_evaluation=repository_evaluation,
        repository_evaluation_sha256=_evaluation_sha256(repository_evaluation),
    )


def _write_yaml(path: Path, model: object) -> None:
    assert hasattr(model, "model_dump")
    path.write_text(
        yaml.safe_dump(model.model_dump(mode="json"), sort_keys=False),
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


def test_checked_in_organization_policy_is_exact_signed_production_matrix() -> None:
    loaded = load_organization_policy(_ORGANIZATION_POLICY_PATH)
    repository = yaml.safe_load(_REPOSITORY_POLICY_PATH.read_text(encoding="utf-8"))

    assert loaded.policy.organization_id == "flashpilot-reference-organization"
    assert loaded.policy.policy_id == "flashpilot-v1-production-baseline"
    assert loaded.policy.requirement_inventory == "exact"
    assert loaded.policy.unknown_state == "fail"
    assert len(loaded.policy.requirements) == 9
    assert [item.model_dump(mode="json") for item in loaded.policy.requirements] == repository[
        "requirements"
    ]
    assert all(
        item.require_signed_attestation is True
        for item in loaded.policy.requirements
        if not isinstance(item, StaticAuditPolicyRequirement)
    )
    assert (
        loaded.source_sha256 == hashlib.sha256(_ORGANIZATION_POLICY_PATH.read_bytes()).hexdigest()
    )


def test_complete_checked_in_matrix_passes_71_organization_checks() -> None:
    organization = load_organization_policy(_ORGANIZATION_POLICY_PATH)
    repository = QualificationPolicyV1.model_validate(
        yaml.safe_load(_REPOSITORY_POLICY_PATH.read_text(encoding="utf-8"))
    )
    repository_evaluation = _repository_evaluation(repository)

    evaluation = evaluate_organization_policy(
        policy=organization.policy,
        policy_sha256=organization.source_sha256,
        scope_id="flashpilot-main",
        repository_policy=repository,
        repository_policy_sha256="e" * 64,
        repository_evaluation=repository_evaluation,
        repository_evaluation_sha256=_evaluation_sha256(repository_evaluation),
    )

    assert repository_evaluation.passed is True
    assert len(repository_evaluation.checks) == 153
    assert evaluation.passed is True
    assert len(evaluation.all_checks) == 71
    assert evaluation.failed_check_ids == ()


@pytest.mark.parametrize(
    "update",
    [
        {"unknown_state": "pass"},
        {"scope_binding": "scan"},
        {"requirement_inventory": "minimum"},
        {"all_requirements_must_pass": False},
        {"arbitrary_expression": "evaluation.passed"},
    ],
)
def test_organization_policy_rejects_weakened_or_executable_fields(
    update: dict[str, object],
) -> None:
    values = _organization_policy(_static_requirement()).model_dump(mode="python")
    values.update(update)

    with pytest.raises(ValidationError):
        OrganizationQualificationPolicyV1.model_validate(values)


def test_organization_policy_requires_signed_runtime_and_unique_selectors() -> None:
    with pytest.raises(ValidationError, match="must require signed"):
        _organization_policy(_runtime_requirement(require_signed_attestation=False))
    requirement = _static_requirement()
    duplicate = requirement.model_copy(update={"requirement_id": "other-static-audit"})
    with pytest.raises(ValidationError, match="selectors must be unique"):
        _organization_policy(requirement, duplicate)


def test_equal_or_stricter_repository_policy_with_signed_evidence_passes() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=30),),
    )
    repository_evaluation = _repository_evaluation(repository)

    evaluation = _evaluate(organization, repository, repository_evaluation)

    assert evaluation.passed is True
    assert evaluation.failed_check_ids == ()
    assert all(check.status is CICheckStatus.PASS for check in evaluation.all_checks)
    assert evaluation.repository_policy_evaluation == repository_evaluation


def test_weaker_repository_bounds_and_unsigned_policy_fail_exact_checks() -> None:
    organization = _organization_policy(_runtime_requirement(max_rpo_steps=0, max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(
            _runtime_requirement(
                max_rpo_steps=1,
                max_rto_seconds=61,
                require_signed_attestation=False,
            ),
        ),
    )
    repository_evaluation = _repository_evaluation(repository, signed=False)

    evaluation = _evaluate(organization, repository, repository_evaluation)

    assert evaluation.passed is False
    assert set(evaluation.failed_check_ids) >= {
        "organization.hf-process-termination.max-rpo-policy",
        "organization.hf-process-termination.max-rto-policy",
        "organization.hf-process-termination.signed-attestation-policy",
        "organization.hf-process-termination.signed-attestation-evidence",
    }


def test_exact_inventory_rejects_missing_and_additional_repository_scenarios() -> None:
    organization = _organization_policy(_runtime_requirement())
    missing = QualificationPolicyV1(
        policy_id="missing-runtime",
        requirements=(_static_requirement(),),
    )
    missing_evaluation = _repository_evaluation(missing)

    evaluation = _evaluate(organization, missing, missing_evaluation)

    assert "organization.requirement-inventory" in evaluation.failed_check_ids
    assert (
        "organization.hf-process-termination.repository-requirement-present"
        in evaluation.failed_check_ids
    )

    additional = QualificationPolicyV1(
        policy_id="additional-static",
        requirements=(_runtime_requirement(), _static_requirement()),
    )
    additional_evaluation = _repository_evaluation(additional)
    evaluation = _evaluate(organization, additional, additional_evaluation)
    assert evaluation.failed_check_ids == ("organization.requirement-inventory",)


def test_repository_failure_propagates_without_upgrading_verdict() -> None:
    organization = _organization_policy(_static_requirement())
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_static_requirement(),),
    )
    failed = evaluate_qualification_policy(
        policy=repository,
        policy_sha256="e" * 64,
        evidence_by_requirement={},
    )

    evaluation = _evaluate(organization, repository, failed)

    assert evaluation.passed is False
    assert set(evaluation.failed_check_ids) == {
        "organization.repository-policy-verdict",
        "organization.hf-static-audit.repository-evidence-pass",
        "organization.hf-static-audit.static-audit-non-attesting",
    }


def test_scope_and_loader_fail_closed_without_yaml_object_execution(tmp_path: Path) -> None:
    unsafe = tmp_path / "unsafe.yml"
    unsafe.write_text("!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8")
    with pytest.raises(OrganizationPolicyError):
        load_organization_policy(unsafe)

    oversized = tmp_path / "oversized.yml"
    oversized.write_text("x" * (64 * 1024 + 1), encoding="utf-8")
    with pytest.raises(OrganizationPolicyError, match="64 KiB"):
        load_organization_policy(oversized)

    organization = _organization_policy(_static_requirement())
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_static_requirement(),),
    )
    repository_evaluation = _repository_evaluation(repository)
    with pytest.raises(OrganizationPolicyError, match="scope ID"):
        evaluate_organization_policy(
            policy=organization,
            policy_sha256="f" * 64,
            scope_id="../escape",
            repository_policy=repository,
            repository_policy_sha256="e" * 64,
            repository_evaluation=repository_evaluation,
            repository_evaluation_sha256=_evaluation_sha256(repository_evaluation),
        )


def test_cli_reverifies_static_suite_and_writes_deterministic_closed_outputs(
    tmp_path: Path,
) -> None:
    organization_path = tmp_path / "organization.yml"
    repository_path = tmp_path / "repository.yml"
    audit_root = tmp_path / "audit"
    output_root = tmp_path / "organization-output"
    _write_yaml(organization_path, _organization_policy(_static_requirement()))
    _write_yaml(
        repository_path,
        QualificationPolicyV1(
            policy_id="repository-suite",
            requirements=(_static_requirement(),),
        ),
    )
    _write_passing_audit(audit_root)
    arguments = [
        "enforce-organization-policy",
        "--organization-policy",
        str(organization_path),
        "--repository-policy",
        str(repository_path),
        "--scope-id",
        "repository-one",
        "--output-dir",
        str(output_root),
        "--run",
        f"hf-static-audit={audit_root}",
    ]

    invocation = CliRunner().invoke(app, arguments)

    assert invocation.exit_code == 0, invocation.output
    assert "ORGANIZATION POLICY PASS" in invocation.output
    assert "Requirements: 1/1" in invocation.output
    evaluation = OrganizationPolicyEvaluationV1.model_validate_json(
        (output_root / "organization-policy-evaluation.json").read_text(encoding="utf-8")
    )
    assert evaluation.passed is True
    assert evaluation.repository_policy_evaluation.passed is True
    assert ElementTree.parse(output_root / "junit.xml").getroot().attrib["failures"] == "0"
    assert (
        json.loads((output_root / "results.sarif").read_text(encoding="utf-8"))["runs"][0][
            "results"
        ]
        == []
    )
    assert set(item.name for item in output_root.iterdir()) == {
        "organization-policy-evaluation.json",
        "repository-policy",
        "junit.xml",
        "job-summary.md",
        "results.sarif",
    }
    assert set(item.name for item in (output_root / "repository-policy").iterdir()) == {
        "policy-evaluation.json",
        "junit.xml",
        "job-summary.md",
        "results.sarif",
    }
    before = {
        path.relative_to(output_root): path.read_bytes()
        for path in output_root.rglob("*")
        if path.is_file()
    }
    repeated = CliRunner().invoke(app, arguments)
    assert repeated.exit_code == 0, repeated.output
    assert {
        path.relative_to(output_root): path.read_bytes()
        for path in output_root.rglob("*")
        if path.is_file()
    } == before


def test_missing_binding_persists_failed_organization_evidence(tmp_path: Path) -> None:
    organization_path = tmp_path / "organization.yml"
    repository_path = tmp_path / "repository.yml"
    output_root = tmp_path / "organization-output"
    _write_yaml(organization_path, _organization_policy(_static_requirement()))
    _write_yaml(
        repository_path,
        QualificationPolicyV1(
            policy_id="repository-suite",
            requirements=(_static_requirement(),),
        ),
    )

    result = enforce_organization_policy(
        organization_policy_path=organization_path,
        repository_policy_path=repository_path,
        scope_id="repository-one",
        run_bindings={},
        output_dir=output_root,
    )

    assert result.exit_code == EXIT_QUALIFICATION_FAILED
    assert "organization.repository-policy-verdict" in result.evaluation.failed_check_ids
    assert result.evaluation_path.is_file()


def test_cli_rejects_output_inside_evidence_and_stale_output(tmp_path: Path) -> None:
    organization_path = tmp_path / "organization.yml"
    repository_path = tmp_path / "repository.yml"
    audit_root = tmp_path / "audit"
    _write_yaml(organization_path, _organization_policy(_static_requirement()))
    _write_yaml(
        repository_path,
        QualificationPolicyV1(
            policy_id="repository-suite",
            requirements=(_static_requirement(),),
        ),
    )
    _write_passing_audit(audit_root)

    inside = CliRunner().invoke(
        app,
        [
            "enforce-organization-policy",
            "--organization-policy",
            str(organization_path),
            "--repository-policy",
            str(repository_path),
            "--scope-id",
            "repository-one",
            "--output-dir",
            str(audit_root / "organization"),
            "--run",
            f"hf-static-audit={audit_root}",
        ],
    )
    assert inside.exit_code == EXIT_UNSUPPORTED
    assert not (audit_root / "organization").exists()

    stale = tmp_path / "stale"
    stale.mkdir()
    (stale / "unexpected.txt").write_text("stale", encoding="utf-8")
    invocation = CliRunner().invoke(
        app,
        [
            "enforce-organization-policy",
            "--organization-policy",
            str(organization_path),
            "--repository-policy",
            str(repository_path),
            "--scope-id",
            "repository-one",
            "--output-dir",
            str(stale),
            "--run",
            f"hf-static-audit={audit_root}",
        ],
    )
    assert invocation.exit_code == EXIT_INVALID_EVIDENCE


def test_reporters_and_model_preserve_exact_failed_check_ids() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=61),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    junit = render_organization_policy_junit(evaluation)
    summary = render_organization_policy_summary(evaluation)
    sarif = json.loads(render_organization_policy_sarif(evaluation))

    failed_id = "organization.hf-process-termination.max-rto-policy"
    assert failed_id in junit
    assert f"`{failed_id}`" in summary
    assert sarif["runs"][0]["results"][0]["ruleId"] == failed_id
    assert (
        sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"][
            "uri"
        ]
        == "organization-policy-evaluation.json"
    )
    payload = evaluation.model_dump(mode="python")
    payload["passed"] = True
    with pytest.raises(ValidationError, match="derive from every check"):
        OrganizationPolicyEvaluationV1.model_validate(payload)


def test_checked_in_organization_policy_schemas_match_generators() -> None:
    for filename, expected in organization_policy_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


def test_passing_evaluation_records_exit_code_and_merge_decision() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=30),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    assert evaluation.passed is True
    assert evaluation.exit_code == EXIT_VERIFIED
    assert evaluation.merge_decision == "allowed"


def test_failing_evaluation_records_blocking_exit_code_and_merge_decision() -> None:
    organization = _organization_policy(_runtime_requirement(max_rpo_steps=0, max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rpo_steps=5, max_rto_seconds=600),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    assert evaluation.passed is False
    assert evaluation.exit_code == EXIT_QUALIFICATION_FAILED
    assert evaluation.merge_decision == "blocked"


def _mutated_evaluation(evaluation: OrganizationPolicyEvaluationV1, **overrides: object) -> dict:
    payload = evaluation.model_dump(mode="json")
    payload.update(overrides)
    return payload


def test_passing_verdict_with_blocking_exit_code_is_rejected() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=30),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    with pytest.raises(ValidationError):
        OrganizationPolicyEvaluationV1.model_validate(
            _mutated_evaluation(evaluation, exit_code=EXIT_QUALIFICATION_FAILED)
        )


def test_failing_verdict_with_allowed_merge_is_rejected() -> None:
    organization = _organization_policy(_runtime_requirement(max_rpo_steps=0, max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rpo_steps=5, max_rto_seconds=600),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    with pytest.raises(ValidationError):
        OrganizationPolicyEvaluationV1.model_validate(
            _mutated_evaluation(evaluation, merge_decision="allowed")
        )


def test_unsupported_exit_codes_and_merge_decisions_are_rejected() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=30),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    for override in ({"exit_code": 2}, {"exit_code": 4}, {"merge_decision": "review"}):
        with pytest.raises(ValidationError):
            OrganizationPolicyEvaluationV1.model_validate(
                _mutated_evaluation(evaluation, **override)
            )


def test_evaluation_round_trips_without_change() -> None:
    organization = _organization_policy(_runtime_requirement(max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rto_seconds=30),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    serialized = json.dumps(evaluation.model_dump(mode="json"), indent=2, sort_keys=True)
    restored = OrganizationPolicyEvaluationV1.model_validate_json(serialized)

    assert restored == evaluation
    assert json.dumps(restored.model_dump(mode="json"), indent=2, sort_keys=True) == serialized


def test_reporters_publish_the_recorded_merge_decision() -> None:
    organization = _organization_policy(_runtime_requirement(max_rpo_steps=0, max_rto_seconds=60))
    repository = QualificationPolicyV1(
        policy_id="repository-suite",
        requirements=(_runtime_requirement(max_rpo_steps=5, max_rto_seconds=600),),
    )
    evaluation = _evaluate(organization, repository, _repository_evaluation(repository))

    suite = ElementTree.fromstring(render_organization_policy_junit(evaluation))
    properties = {node.get("name"): node.get("value") for node in suite.iter("property")}
    assert properties["exit_code"] == str(EXIT_QUALIFICATION_FAILED)
    assert properties["merge_decision"] == "blocked"

    summary = render_organization_policy_summary(evaluation)
    assert f"- Exit code: `{EXIT_QUALIFICATION_FAILED}`" in summary
    assert "- Merge: **blocked**" in summary
