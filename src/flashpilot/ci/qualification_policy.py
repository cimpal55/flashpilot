"""Safe loading and deterministic enforcement for a closed qualification-suite policy."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from flashpilot.attestation import (
    ATTESTATION_SIGNATURE_PATH,
    RECOVERY_ATTESTATION_PATH,
    verify_recovery_attestation,
)
from flashpilot.attestation.verifier import AttestationVerificationError
from flashpilot.ci.exits import EXIT_QUALIFICATION_FAILED, EXIT_VERIFIED
from flashpilot.ci.models import CICheck, CICheckStatus, CIStatus
from flashpilot.ci.qualification_policy_models import (
    DeepSpeedPolicyRequirement,
    DistributedPolicyRequirement,
    QualificationPolicyEvaluationV1,
    QualificationPolicyEvidence,
    QualificationPolicyRequirement,
    QualificationPolicyV1,
    QualificationRequirementEvaluation,
    StaticAuditPolicyRequirement,
)
from flashpilot.ci.qualification_policy_reporters import (
    POLICY_EVALUATION_PATH,
    POLICY_JUNIT_PATH,
    POLICY_SARIF_PATH,
    POLICY_SUMMARY_PATH,
    render_qualification_policy_junit,
    render_qualification_policy_sarif,
    render_qualification_policy_summary,
)
from flashpilot.ci.service import CIEvidenceError, normalize_run_evidence, read_run_result
from flashpilot.orchestration.artifacts import write_text_artifact

MAX_QUALIFICATION_POLICY_BYTES = 64 * 1024
_REQUIREMENT_ID = re.compile(r"^[a-z][a-z0-9-]{0,79}$")
_POLICY_OUTPUTS = frozenset(
    {
        POLICY_EVALUATION_PATH,
        POLICY_JUNIT_PATH,
        POLICY_SUMMARY_PATH,
        POLICY_SARIF_PATH,
    }
)


class QualificationPolicyError(ValueError):
    """The typed policy or its explicit run bindings are unsupported."""


class QualificationPolicyEvidenceError(ValueError):
    """A bound run or generated policy artifact is invalid or tampered."""


@dataclass(frozen=True, slots=True)
class LoadedQualificationPolicy:
    policy: QualificationPolicyV1
    source_sha256: str


@dataclass(frozen=True, slots=True)
class _LoadedPolicyEvidence:
    root: Path
    value: QualificationPolicyEvidence


@dataclass(frozen=True, slots=True)
class QualificationPolicyArtifactResult:
    evaluation: QualificationPolicyEvaluationV1
    evaluation_path: Path
    junit_path: Path
    job_summary_path: Path
    sarif_path: Path
    exit_code: int


def load_qualification_policy(path: Path) -> LoadedQualificationPolicy:
    """Load one bounded YAML source into the closed qualification policy schema."""

    if not path.is_file() or path.is_symlink():
        raise QualificationPolicyError("qualification policy must be a regular non-symlink file")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise QualificationPolicyError("qualification policy is unreadable") from error
    if len(raw) > MAX_QUALIFICATION_POLICY_BYTES:
        raise QualificationPolicyError("qualification policy exceeds the 64 KiB limit")
    try:
        payload = yaml.safe_load(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise QualificationPolicyError("qualification policy root must be a mapping")
        policy = QualificationPolicyV1.model_validate(payload)
    except (UnicodeError, yaml.YAMLError, ValidationError) as error:
        raise QualificationPolicyError(
            "qualification policy is malformed or unsupported"
        ) from error
    return LoadedQualificationPolicy(
        policy=policy,
        source_sha256=hashlib.sha256(raw).hexdigest(),
    )


def parse_policy_run_bindings(values: list[str]) -> dict[str, Path]:
    """Parse repeated requirement-id=run-directory bindings without path discovery."""

    bindings: dict[str, Path] = {}
    for value in values:
        requirement_id, separator, raw_path = value.partition("=")
        if not separator or not _REQUIREMENT_ID.fullmatch(requirement_id) or not raw_path:
            raise QualificationPolicyError(
                "each --run must be an exact requirement-id=run-directory binding"
            )
        if requirement_id in bindings:
            raise QualificationPolicyError(f"duplicate run binding: {requirement_id}")
        bindings[requirement_id] = Path(raw_path)
    return bindings


def _safe_run_root(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise QualificationPolicyEvidenceError(
            "bound run root must be an existing non-symlink directory"
        )
    try:
        return path.resolve(strict=True)
    except OSError as error:
        raise QualificationPolicyEvidenceError("bound run root cannot be resolved") from error


def _load_policy_evidence(
    path: Path,
    *,
    public_key_path: Path | None,
) -> _LoadedPolicyEvidence:
    root = _safe_run_root(path)
    sources = tuple(
        candidate for candidate in (root / "result.json", root / "audit.json") if candidate.exists()
    )
    if len(sources) != 1 or not sources[0].is_file() or sources[0].is_symlink():
        raise QualificationPolicyEvidenceError(
            "bound run must contain exactly one regular result.json or audit.json"
        )
    source = sources[0]
    try:
        source_before = source.read_bytes()
        result = read_run_result(root)
        evidence = normalize_run_evidence(result)
    except (CIEvidenceError, OSError, UnicodeError, ValidationError, ValueError) as error:
        raise QualificationPolicyEvidenceError(
            "bound run result is malformed or unsupported"
        ) from error

    attestation_path = root / RECOVERY_ATTESTATION_PATH
    signature_path = root / ATTESTATION_SIGNATURE_PATH
    attestation_status: str
    attestation_signature_status: str
    attestation_sha256: str | None = None
    signing_key_sha256: str | None = None
    signature_artifact_sha256: str | None = None
    if evidence.kind == "static-audit":
        if attestation_path.exists() or signature_path.exists():
            raise QualificationPolicyEvidenceError(
                "static audit must not contain recovery attestation artifacts"
            )
        attestation_status = "not-applicable"
        attestation_signature_status = "not-applicable"
    elif evidence.status is CIStatus.VERIFIED:
        if not attestation_path.exists():
            if signature_path.exists():
                raise QualificationPolicyEvidenceError(
                    "detached signature cannot exist without a recovery attestation"
                )
            attestation_status = "missing"
            attestation_signature_status = "missing"
        else:
            try:
                verification = verify_recovery_attestation(
                    attestation_path,
                    public_key_path=public_key_path if signature_path.exists() else None,
                    require_signed=signature_path.exists(),
                )
            except (AttestationVerificationError, OSError, UnicodeError, ValueError) as error:
                raise QualificationPolicyEvidenceError(
                    "bound recovery attestation is invalid or tampered"
                ) from error
            if not verification.valid:
                raise QualificationPolicyEvidenceError("bound recovery attestation is invalid")
            attestation_status = "verified"
            attestation_sha256 = verification.attestation_sha256
            attestation_signature_status = verification.signature_status
            signing_key_sha256 = verification.signing_key_sha256
            signature_artifact_sha256 = verification.signature_artifact_sha256
    else:
        if attestation_path.exists() or signature_path.exists():
            raise QualificationPolicyEvidenceError(
                "non-verified run must not contain recovery attestation artifacts"
            )
        attestation_status = "missing"
        attestation_signature_status = "missing"

    try:
        source_after = source.read_bytes()
    except OSError as error:
        raise QualificationPolicyEvidenceError("bound run result became unreadable") from error
    if source_after != source_before:
        raise QualificationPolicyEvidenceError("bound run result changed during policy validation")
    return _LoadedPolicyEvidence(
        root=root,
        value=QualificationPolicyEvidence(
            source_artifact=source.name,
            source_sha256=hashlib.sha256(source_before).hexdigest(),
            attestation_status=attestation_status,
            attestation_sha256=attestation_sha256,
            attestation_signature_status=attestation_signature_status,
            signing_key_sha256=signing_key_sha256,
            signature_artifact_sha256=signature_artifact_sha256,
            evidence=evidence,
        ),
    )


def _display(value: object) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return str(value).lower()
    return str(getattr(value, "value", value))


def _check(
    requirement_id: str,
    suffix: str,
    passed: bool,
    summary: str,
    expected: object,
    actual: object,
) -> CICheck:
    return CICheck(
        check_id=f"policy.{requirement_id}.{suffix}",
        status=CICheckStatus.PASS if passed else CICheckStatus.FAIL,
        summary=summary,
        expected=_display(expected),
        actual=_display(actual),
    )


def _field_check(
    requirement: QualificationPolicyRequirement,
    evidence: QualificationPolicyEvidence,
    field: str,
    suffix: str,
    summary: str,
) -> CICheck:
    expected = getattr(requirement, field)
    actual = getattr(evidence.evidence, field)
    return _check(
        requirement.requirement_id,
        suffix,
        actual == expected,
        summary,
        expected,
        actual,
    )


def _evaluate_requirement(
    requirement: QualificationPolicyRequirement,
    evidence: QualificationPolicyEvidence | None,
) -> QualificationRequirementEvaluation:
    requirement_id = requirement.requirement_id
    if evidence is None:
        checks = (
            _check(
                requirement_id,
                "evidence-present",
                False,
                "An explicit run binding is required for this policy requirement.",
                "present",
                "missing",
            ),
        )
    else:
        normalized = evidence.evidence
        checks_list = [
            _check(
                requirement_id,
                "evidence-present",
                True,
                "An explicit run binding is present for this policy requirement.",
                "present",
                "present",
            ),
            _field_check(requirement, evidence, "kind", "kind", "Evidence kind matches policy."),
            _field_check(
                requirement,
                evidence,
                "framework",
                "framework",
                "Framework identity matches policy.",
            ),
            _field_check(
                requirement,
                evidence,
                "qualification_profile",
                "qualification-profile",
                "Qualification profile matches policy.",
            ),
            _check(
                requirement_id,
                "unknown-state",
                normalized.status is not CIStatus.UNKNOWN,
                "UNKNOWN evidence fails closed and can never satisfy policy.",
                "not UNKNOWN",
                normalized.status.value,
            ),
            _check(
                requirement_id,
                "required-status",
                normalized.status.value == requirement.required_status,
                "Deterministic evidence status matches the required policy status.",
                requirement.required_status,
                normalized.status.value,
            ),
            _check(
                requirement_id,
                "checks",
                all(
                    check.status in {CICheckStatus.PASS, CICheckStatus.NOT_APPLICABLE}
                    for check in normalized.checks
                ),
                "Every underlying deterministic evidence check must be non-failing.",
                "PASS or NOT_APPLICABLE",
                ",".join(sorted({check.status.value for check in normalized.checks})),
            ),
        ]
        if isinstance(requirement, StaticAuditPolicyRequirement):
            checks_list.append(
                _check(
                    requirement_id,
                    "attestation",
                    evidence.attestation_status == "not-applicable",
                    "Static audit remains non-verifying and cannot carry an attestation.",
                    "not-applicable",
                    evidence.attestation_status,
                )
            )
        else:
            checks_list.extend(
                (
                    _field_check(
                        requirement,
                        evidence,
                        "adapter",
                        "adapter",
                        "Adapter identity matches policy.",
                    ),
                    _field_check(
                        requirement,
                        evidence,
                        "fault",
                        "fault",
                        "Fault identity matches policy.",
                    ),
                    _check(
                        requirement_id,
                        "exact-recovery",
                        normalized.atol == 0.0 and normalized.rtol == 0.0,
                        "Recovery comparison remains exact with zero tolerances.",
                        "atol=0.0,rtol=0.0",
                        f"atol={normalized.atol},rtol={normalized.rtol}",
                    ),
                    _check(
                        requirement_id,
                        "max-rpo",
                        normalized.rpo_steps is not None
                        and normalized.rpo_steps <= requirement.max_rpo_steps,
                        "Observed RPO stays within the typed policy bound.",
                        requirement.max_rpo_steps,
                        normalized.rpo_steps,
                    ),
                    _check(
                        requirement_id,
                        "max-rto",
                        normalized.rto_seconds is not None
                        and normalized.rto_seconds <= requirement.max_rto_seconds,
                        "Observed RTO stays within the typed policy bound.",
                        requirement.max_rto_seconds,
                        normalized.rto_seconds,
                    ),
                    _check(
                        requirement_id,
                        "attestation",
                        evidence.attestation_status == "verified",
                        "A verified run requires an integrity-verified local attestation.",
                        "verified",
                        evidence.attestation_status,
                    ),
                    _check(
                        requirement_id,
                        "signed-attestation",
                        not requirement.require_signed_attestation
                        or evidence.attestation_signature_status == "verified",
                        "A signed-attestation policy requires the explicitly trusted key.",
                        "verified" if requirement.require_signed_attestation else "optional",
                        evidence.attestation_signature_status,
                    ),
                )
            )
            if isinstance(requirement, (DistributedPolicyRequirement, DeepSpeedPolicyRequirement)):
                for field, suffix, summary in (
                    ("strategy", "strategy", "Distributed strategy matches policy."),
                    ("implementation", "implementation", "Implementation matches policy."),
                    ("backend", "backend", "Distributed backend matches policy."),
                    ("world_size", "world-size", "Distributed world size matches policy."),
                    (
                        "fault_target_rank",
                        "fault-target-rank",
                        "Fault target rank matches policy.",
                    ),
                ):
                    checks_list.append(_field_check(requirement, evidence, field, suffix, summary))
                if isinstance(requirement, DeepSpeedPolicyRequirement):
                    checks_list.append(
                        _field_check(
                            requirement,
                            evidence,
                            "zero_stage",
                            "zero-stage",
                            "DeepSpeed ZeRO stage matches policy.",
                        )
                    )
        checks = tuple(checks_list)
    failed = tuple(check.check_id for check in checks if check.status is CICheckStatus.FAIL)
    return QualificationRequirementEvaluation(
        requirement_id=requirement_id,
        passed=not failed,
        evidence=evidence,
        checks=checks,
        failed_check_ids=failed,
    )


def evaluate_qualification_policy(
    *,
    policy: QualificationPolicyV1,
    policy_sha256: str,
    evidence_by_requirement: dict[str, QualificationPolicyEvidence],
) -> QualificationPolicyEvaluationV1:
    """Evaluate all explicit requirements; no expressions or arbitrary code are accepted."""

    expected_ids = {requirement.requirement_id for requirement in policy.requirements}
    unexpected = sorted(set(evidence_by_requirement) - expected_ids)
    if unexpected:
        raise QualificationPolicyError(
            "unlisted run bindings are forbidden: " + ", ".join(unexpected)
        )
    requirements = tuple(
        _evaluate_requirement(
            requirement,
            evidence_by_requirement.get(requirement.requirement_id),
        )
        for requirement in policy.requirements
    )
    failed = tuple(item.requirement_id for item in requirements if not item.passed)
    return QualificationPolicyEvaluationV1(
        policy_id=policy.policy_id,
        policy_sha256=policy_sha256,
        passed=not failed,
        requirements=requirements,
        failed_requirement_ids=failed,
    )


def _write_or_verify(root: Path, relative_path: str, expected: str) -> Path:
    destination = root / relative_path
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise QualificationPolicyEvidenceError(f"existing {relative_path} is not a safe file")
        try:
            actual = destination.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise QualificationPolicyEvidenceError(
                f"existing {relative_path} is unreadable"
            ) from error
        if actual != expected:
            raise QualificationPolicyEvidenceError(
                f"existing {relative_path} differs from deterministic policy evidence"
            )
        return destination
    return write_text_artifact(run_root=root, relative_path=relative_path, text=expected)


def _prepare_output_root(path: Path, evidence_roots: tuple[Path, ...]) -> Path:
    candidate = path.resolve(strict=False)
    if any(candidate == root or candidate.is_relative_to(root) for root in evidence_roots):
        raise QualificationPolicyError("policy output directory cannot be inside a bound run")
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise QualificationPolicyEvidenceError(
                "policy output root must be a non-symlink directory"
            )
        unexpected = sorted(
            item.name for item in path.iterdir() if item.name not in _POLICY_OUTPUTS
        )
        if unexpected:
            raise QualificationPolicyEvidenceError(
                "policy output root contains unexpected entries: " + ", ".join(unexpected)
            )
    else:
        path.mkdir(parents=True)
    return path.resolve(strict=True)


def enforce_qualification_policy(
    *,
    policy_path: Path,
    run_bindings: dict[str, Path],
    output_dir: Path,
    public_key_path: Path | None = None,
) -> QualificationPolicyArtifactResult:
    """Load, verify, evaluate, and persist one explicit qualification-suite policy."""

    loaded_policy = load_qualification_policy(policy_path)
    requirement_ids = {item.requirement_id for item in loaded_policy.policy.requirements}
    unexpected = sorted(set(run_bindings) - requirement_ids)
    if unexpected:
        raise QualificationPolicyError(
            "unlisted run bindings are forbidden: " + ", ".join(unexpected)
        )
    signed_requirements = tuple(
        item.requirement_id
        for item in loaded_policy.policy.requirements
        if not isinstance(item, StaticAuditPolicyRequirement) and item.require_signed_attestation
    )
    if signed_requirements and public_key_path is None:
        raise QualificationPolicyError(
            "signed-attestation requirements need one explicitly trusted --public-key"
        )
    loaded_evidence = {
        requirement_id: _load_policy_evidence(
            path,
            public_key_path=public_key_path,
        )
        for requirement_id, path in run_bindings.items()
    }
    evaluation = evaluate_qualification_policy(
        policy=loaded_policy.policy,
        policy_sha256=loaded_policy.source_sha256,
        evidence_by_requirement={
            requirement_id: loaded.value for requirement_id, loaded in loaded_evidence.items()
        },
    )
    output_root = _prepare_output_root(
        output_dir,
        tuple(loaded.root for loaded in loaded_evidence.values()),
    )
    evaluation_text = (
        json.dumps(
            evaluation.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    evaluation_path = _write_or_verify(output_root, POLICY_EVALUATION_PATH, evaluation_text)
    junit_path = _write_or_verify(
        output_root,
        POLICY_JUNIT_PATH,
        render_qualification_policy_junit(evaluation),
    )
    summary_path = _write_or_verify(
        output_root,
        POLICY_SUMMARY_PATH,
        render_qualification_policy_summary(evaluation),
    )
    sarif_path = _write_or_verify(
        output_root,
        POLICY_SARIF_PATH,
        render_qualification_policy_sarif(evaluation),
    )
    return QualificationPolicyArtifactResult(
        evaluation=evaluation,
        evaluation_path=evaluation_path,
        junit_path=junit_path,
        job_summary_path=summary_path,
        sarif_path=sarif_path,
        exit_code=EXIT_VERIFIED if evaluation.passed else EXIT_QUALIFICATION_FAILED,
    )
