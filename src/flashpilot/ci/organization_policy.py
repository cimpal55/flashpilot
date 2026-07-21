"""Safe deterministic enforcement of a closed organization policy baseline."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from flashpilot.ci.exits import EXIT_QUALIFICATION_FAILED, EXIT_VERIFIED
from flashpilot.ci.models import CICheck, CICheckStatus
from flashpilot.ci.organization_policy_models import (
    OrganizationPolicyEvaluationV1,
    OrganizationQualificationPolicyV1,
    OrganizationRequirementEvaluation,
)
from flashpilot.ci.organization_policy_reporters import (
    ORGANIZATION_POLICY_EVALUATION_PATH,
    ORGANIZATION_POLICY_JUNIT_PATH,
    ORGANIZATION_POLICY_SARIF_PATH,
    ORGANIZATION_POLICY_SUMMARY_PATH,
    REPOSITORY_POLICY_OUTPUT_PATH,
    render_organization_policy_junit,
    render_organization_policy_sarif,
    render_organization_policy_summary,
)
from flashpilot.ci.qualification_policy import (
    QualificationPolicyArtifactResult,
    QualificationPolicyError,
    QualificationPolicyEvidenceError,
    enforce_qualification_policy,
    load_qualification_policy,
)
from flashpilot.ci.qualification_policy_models import (
    QualificationPolicyEvaluationV1,
    QualificationPolicyRequirement,
    QualificationPolicyV1,
    RuntimePolicyRequirement,
    StaticAuditPolicyRequirement,
    qualification_requirement_selector,
)
from flashpilot.orchestration.artifacts import write_text_artifact

MAX_ORGANIZATION_POLICY_BYTES = 64 * 1024
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,79}$")
_ORGANIZATION_OUTPUTS = frozenset(
    {
        ORGANIZATION_POLICY_EVALUATION_PATH,
        ORGANIZATION_POLICY_JUNIT_PATH,
        ORGANIZATION_POLICY_SUMMARY_PATH,
        ORGANIZATION_POLICY_SARIF_PATH,
        REPOSITORY_POLICY_OUTPUT_PATH,
    }
)


class OrganizationPolicyError(ValueError):
    """The closed organization policy or explicit scope is unsupported."""


class OrganizationPolicyEvidenceError(ValueError):
    """Repository evidence or generated organization artifacts are invalid."""


@dataclass(frozen=True, slots=True)
class LoadedOrganizationPolicy:
    policy: OrganizationQualificationPolicyV1
    source_sha256: str


@dataclass(frozen=True, slots=True)
class OrganizationPolicyArtifactResult:
    evaluation: OrganizationPolicyEvaluationV1
    repository_policy_result: QualificationPolicyArtifactResult
    evaluation_path: Path
    junit_path: Path
    job_summary_path: Path
    sarif_path: Path
    exit_code: int


def load_organization_policy(path: Path) -> LoadedOrganizationPolicy:
    """Load one bounded YAML source through the closed organization schema."""

    if not path.is_file() or path.is_symlink():
        raise OrganizationPolicyError("organization policy must be a regular non-symlink file")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise OrganizationPolicyError("organization policy is unreadable") from error
    if len(raw) > MAX_ORGANIZATION_POLICY_BYTES:
        raise OrganizationPolicyError("organization policy exceeds the 64 KiB limit")
    try:
        payload = yaml.safe_load(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise OrganizationPolicyError("organization policy root must be a mapping")
        policy = OrganizationQualificationPolicyV1.model_validate(payload)
    except (UnicodeError, yaml.YAMLError, ValidationError) as error:
        raise OrganizationPolicyError("organization policy is malformed or unsupported") from error
    return LoadedOrganizationPolicy(
        policy=policy,
        source_sha256=hashlib.sha256(raw).hexdigest(),
    )


def _display(value: object) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return str(value).lower()
    return str(getattr(value, "value", value))


def _check(
    check_id: str,
    passed: bool,
    summary: str,
    expected: object,
    actual: object,
) -> CICheck:
    return CICheck(
        check_id=check_id,
        status=CICheckStatus.PASS if passed else CICheckStatus.FAIL,
        summary=summary,
        expected=_display(expected),
        actual=_display(actual),
    )


def _requirement_evaluation(
    *,
    organization_requirement: QualificationPolicyRequirement,
    repository_requirement: QualificationPolicyRequirement | None,
    repository_evaluation: QualificationPolicyEvaluationV1,
) -> OrganizationRequirementEvaluation:
    organization_id = organization_requirement.requirement_id
    prefix = f"organization.{organization_id}."
    checks = [
        _check(
            prefix + "repository-requirement-present",
            repository_requirement is not None,
            "The repository policy must contain this exact closed scenario selector.",
            "present",
            "present" if repository_requirement is not None else "missing",
        )
    ]
    repository_requirement_id = (
        repository_requirement.requirement_id if repository_requirement is not None else None
    )
    repository_result = (
        next(
            (
                item
                for item in repository_evaluation.requirements
                if item.requirement_id == repository_requirement_id
            ),
            None,
        )
        if repository_requirement_id is not None
        else None
    )
    if repository_requirement is not None:
        checks.append(
            _check(
                prefix + "repository-evidence-present",
                repository_result is not None,
                "The repository suite evaluation must include its matched requirement.",
                repository_requirement_id,
                repository_result.requirement_id if repository_result is not None else None,
            )
        )
        if isinstance(organization_requirement, RuntimePolicyRequirement):
            assert isinstance(repository_requirement, RuntimePolicyRequirement)
            checks.extend(
                (
                    _check(
                        prefix + "max-rpo-policy",
                        repository_requirement.max_rpo_steps
                        <= organization_requirement.max_rpo_steps,
                        "The repository RPO bound may only equal or tighten the organization bound.",
                        f"<= {organization_requirement.max_rpo_steps}",
                        repository_requirement.max_rpo_steps,
                    ),
                    _check(
                        prefix + "max-rto-policy",
                        repository_requirement.max_rto_seconds
                        <= organization_requirement.max_rto_seconds,
                        "The repository RTO bound may only equal or tighten the organization bound.",
                        f"<= {organization_requirement.max_rto_seconds}",
                        repository_requirement.max_rto_seconds,
                    ),
                    _check(
                        prefix + "signed-attestation-policy",
                        repository_requirement.require_signed_attestation,
                        "The repository policy must require a verified detached signature.",
                        True,
                        repository_requirement.require_signed_attestation,
                    ),
                )
            )
        if repository_result is not None:
            checks.append(
                _check(
                    prefix + "repository-evidence-pass",
                    repository_result.passed,
                    "The matched deterministic repository requirement must pass.",
                    True,
                    repository_result.passed,
                )
            )
            evidence = repository_result.evidence
            if isinstance(organization_requirement, RuntimePolicyRequirement):
                checks.extend(
                    (
                        _check(
                            prefix + "exact-recovery-evidence",
                            evidence is not None
                            and evidence.evidence.atol == 0.0
                            and evidence.evidence.rtol == 0.0,
                            "Runtime evidence must retain exact zero-tolerance recovery.",
                            "atol=0.0,rtol=0.0",
                            (
                                "missing"
                                if evidence is None
                                else f"atol={evidence.evidence.atol},rtol={evidence.evidence.rtol}"
                            ),
                        ),
                        _check(
                            prefix + "signed-attestation-evidence",
                            evidence is not None
                            and evidence.attestation_signature_status == "verified"
                            and evidence.signing_key_sha256 is not None
                            and evidence.signature_artifact_sha256 is not None,
                            "Runtime evidence must contain verified detached-signature evidence.",
                            "verified",
                            (
                                evidence.attestation_signature_status
                                if evidence is not None
                                else "missing"
                            ),
                        ),
                    )
                )
            else:
                assert isinstance(organization_requirement, StaticAuditPolicyRequirement)
                checks.append(
                    _check(
                        prefix + "static-audit-non-attesting",
                        evidence is not None
                        and evidence.attestation_status == "not-applicable"
                        and evidence.attestation_signature_status == "not-applicable",
                        "Static audit must remain non-verifying and non-attesting.",
                        "not-applicable",
                        evidence.attestation_status if evidence is not None else "missing",
                    )
                )
    failed = tuple(check.check_id for check in checks if check.status is CICheckStatus.FAIL)
    return OrganizationRequirementEvaluation(
        requirement_id=organization_id,
        repository_requirement_id=repository_requirement_id,
        passed=not failed,
        checks=tuple(checks),
        failed_check_ids=failed,
    )


def evaluate_organization_policy(
    *,
    policy: OrganizationQualificationPolicyV1,
    policy_sha256: str,
    scope_id: str,
    repository_policy: QualificationPolicyV1,
    repository_policy_sha256: str,
    repository_evaluation: QualificationPolicyEvaluationV1,
    repository_evaluation_sha256: str,
) -> OrganizationPolicyEvaluationV1:
    """Apply the fixed organization baseline to one verified repository suite."""

    if not _IDENTIFIER.fullmatch(scope_id):
        raise OrganizationPolicyError("scope ID must be a canonical lowercase identifier")
    organization_selectors = {
        qualification_requirement_selector(item): item for item in policy.requirements
    }
    repository_selectors = {
        qualification_requirement_selector(item): item for item in repository_policy.requirements
    }
    inventory_matches = set(organization_selectors) == set(repository_selectors)
    checks = (
        _check(
            "organization.requirement-inventory",
            inventory_matches,
            "The repository policy must implement the exact organization scenario inventory.",
            len(organization_selectors),
            len(repository_selectors),
        ),
        _check(
            "organization.repository-policy-identity",
            repository_evaluation.policy_id == repository_policy.policy_id
            and repository_evaluation.policy_sha256 == repository_policy_sha256,
            "The repository evaluation must bind the exact supplied repository policy source.",
            f"{repository_policy.policy_id}:{repository_policy_sha256}",
            f"{repository_evaluation.policy_id}:{repository_evaluation.policy_sha256}",
        ),
        _check(
            "organization.repository-policy-verdict",
            repository_evaluation.passed,
            "The complete deterministic repository suite policy must pass.",
            True,
            repository_evaluation.passed,
        ),
    )
    requirements = tuple(
        _requirement_evaluation(
            organization_requirement=requirement,
            repository_requirement=repository_selectors.get(
                qualification_requirement_selector(requirement)
            ),
            repository_evaluation=repository_evaluation,
        )
        for requirement in policy.requirements
    )
    all_checks = checks + tuple(check for item in requirements for check in item.checks)
    failed = tuple(check.check_id for check in all_checks if check.status is CICheckStatus.FAIL)
    return OrganizationPolicyEvaluationV1(
        organization_id=policy.organization_id,
        policy_id=policy.policy_id,
        scope_id=scope_id,
        organization_policy_sha256=policy_sha256,
        repository_policy_id=repository_policy.policy_id,
        repository_policy_sha256=repository_policy_sha256,
        repository_policy_evaluation_sha256=repository_evaluation_sha256,
        repository_policy_evaluation=repository_evaluation,
        passed=not failed,
        exit_code=EXIT_VERIFIED if not failed else EXIT_QUALIFICATION_FAILED,
        merge_decision="allowed" if not failed else "blocked",
        checks=checks,
        requirements=requirements,
        failed_check_ids=failed,
    )


def _write_or_verify(root: Path, relative_path: str, expected: str) -> Path:
    destination = root / relative_path
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise OrganizationPolicyEvidenceError(f"existing {relative_path} is not a safe file")
        try:
            actual = destination.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise OrganizationPolicyEvidenceError(
                f"existing {relative_path} is unreadable"
            ) from error
        if actual != expected:
            raise OrganizationPolicyEvidenceError(
                f"existing {relative_path} differs from deterministic organization evidence"
            )
        return destination
    return write_text_artifact(run_root=root, relative_path=relative_path, text=expected)


def _prepare_output_root(path: Path, run_bindings: dict[str, Path]) -> Path:
    candidate = path.resolve(strict=False)
    for run in run_bindings.values():
        try:
            run_root = run.resolve(strict=True)
        except OSError as error:
            raise OrganizationPolicyEvidenceError("bound run root cannot be resolved") from error
        if candidate == run_root or candidate.is_relative_to(run_root):
            raise OrganizationPolicyError("organization output directory cannot be inside a run")
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise OrganizationPolicyEvidenceError(
                "organization output root must be a non-symlink directory"
            )
        children = tuple(path.iterdir())
        if any(child.is_symlink() for child in children):
            raise OrganizationPolicyEvidenceError("organization output root refuses symbolic links")
        unexpected = sorted(
            child.name for child in children if child.name not in _ORGANIZATION_OUTPUTS
        )
        if unexpected:
            raise OrganizationPolicyEvidenceError(
                "organization output root contains unexpected entries: " + ", ".join(unexpected)
            )
    else:
        path.mkdir(parents=True)
    return path.resolve(strict=True)


def enforce_organization_policy(
    *,
    organization_policy_path: Path,
    repository_policy_path: Path,
    scope_id: str,
    run_bindings: dict[str, Path],
    output_dir: Path,
    public_key_path: Path | None = None,
) -> OrganizationPolicyArtifactResult:
    """Re-verify one suite and enforce one closed organization baseline over it."""

    loaded_organization = load_organization_policy(organization_policy_path)
    loaded_repository_before = load_qualification_policy(repository_policy_path)
    output_root = _prepare_output_root(output_dir, run_bindings)
    try:
        repository_result = enforce_qualification_policy(
            policy_path=repository_policy_path,
            run_bindings=run_bindings,
            output_dir=output_root / REPOSITORY_POLICY_OUTPUT_PATH,
            public_key_path=public_key_path,
        )
    except QualificationPolicyError as error:
        raise OrganizationPolicyError(str(error)) from error
    except QualificationPolicyEvidenceError as error:
        raise OrganizationPolicyEvidenceError(str(error)) from error
    loaded_repository_after = load_qualification_policy(repository_policy_path)
    if loaded_repository_after != loaded_repository_before:
        raise OrganizationPolicyEvidenceError(
            "repository policy source changed during organization enforcement"
        )
    try:
        repository_evaluation_bytes = repository_result.evaluation_path.read_bytes()
    except OSError as error:
        raise OrganizationPolicyEvidenceError(
            "repository policy evaluation became unreadable"
        ) from error
    expected_repository_evaluation = (
        json.dumps(
            repository_result.evaluation.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    if repository_evaluation_bytes != expected_repository_evaluation:
        raise OrganizationPolicyEvidenceError(
            "repository policy evaluation differs from deterministic evidence"
        )
    repository_evaluation_sha256 = hashlib.sha256(repository_evaluation_bytes).hexdigest()
    evaluation = evaluate_organization_policy(
        policy=loaded_organization.policy,
        policy_sha256=loaded_organization.source_sha256,
        scope_id=scope_id,
        repository_policy=loaded_repository_before.policy,
        repository_policy_sha256=loaded_repository_before.source_sha256,
        repository_evaluation=repository_result.evaluation,
        repository_evaluation_sha256=repository_evaluation_sha256,
    )
    evaluation_text = (
        json.dumps(evaluation.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    )
    evaluation_path = _write_or_verify(
        output_root,
        ORGANIZATION_POLICY_EVALUATION_PATH,
        evaluation_text,
    )
    junit_path = _write_or_verify(
        output_root,
        ORGANIZATION_POLICY_JUNIT_PATH,
        render_organization_policy_junit(evaluation),
    )
    summary_path = _write_or_verify(
        output_root,
        ORGANIZATION_POLICY_SUMMARY_PATH,
        render_organization_policy_summary(evaluation),
    )
    sarif_path = _write_or_verify(
        output_root,
        ORGANIZATION_POLICY_SARIF_PATH,
        render_organization_policy_sarif(evaluation),
    )
    return OrganizationPolicyArtifactResult(
        evaluation=evaluation,
        repository_policy_result=repository_result,
        evaluation_path=evaluation_path,
        junit_path=junit_path,
        job_summary_path=summary_path,
        sarif_path=sarif_path,
        # Single source: the artifact already records this, validated against
        # the verdict. Recomputing it here could drift from what was persisted.
        exit_code=evaluation.exit_code,
    )
