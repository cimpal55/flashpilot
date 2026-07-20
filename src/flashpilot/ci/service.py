"""Shared local/CI evidence normalization, artifact emission, and exit behavior."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from flashpilot.audit.models import StaticAuditResult
from flashpilot.audit.reporters import render_junit as render_audit_junit
from flashpilot.ci.exits import (
    EXIT_QUALIFICATION_FAILED,
    EXIT_REVIEW,
    EXIT_VERIFIED,
)
from flashpilot.ci.models import (
    CICheck,
    CICheckStatus,
    CIPolicyEvaluation,
    CIPolicyV1,
    CIRunEvidence,
    CIStatus,
)
from flashpilot.ci.policy import evaluate_ci_policy
from flashpilot.ci.reporters import (
    JOB_SUMMARY_PATH,
    QUALIFICATION_JUNIT_PATH,
    render_job_summary,
    render_qualification_junit,
)
from flashpilot.contracts.models import QualificationProfile
from flashpilot.domain.recovery import CrashExperimentResult
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.hf.models import HFQualificationResult
from flashpilot.orchestration.artifacts import write_text_artifact
from flashpilot.security.paths import PathSandbox


class CIEvidenceError(ValueError):
    """Run evidence is missing, malformed, inconsistent, or unsupported."""


@dataclass(frozen=True, slots=True)
class CIArtifactResult:
    evidence: CIRunEvidence
    junit_path: Path
    job_summary_path: Path
    policy_evaluation: CIPolicyEvaluation | None
    exit_code: int


def _status(value: object) -> CICheckStatus:
    normalized = str(value).upper()
    if normalized == "PASS":
        return CICheckStatus.PASS
    if normalized == "FAIL":
        return CICheckStatus.FAIL
    if normalized == "WARN":
        return CICheckStatus.WARN
    if normalized == "UNKNOWN":
        return CICheckStatus.UNKNOWN
    raise CIEvidenceError(f"unsupported check status: {value}")


def _audit_evidence(result: StaticAuditResult) -> CIRunEvidence:
    checks = tuple(
        CICheck(
            check_id=check.check_id,
            status=_status(check.status.value),
            summary=check.summary,
        )
        for check in result.checks
    )
    return CIRunEvidence(
        kind="static-audit",
        status=(
            CIStatus.FAILED if result.status.value == "FAIL" else CIStatus(result.status.value)
        ),
        qualification_profile=result.qualification_profile,
        framework=result.framework.value,
        checks=checks,
    )


def _native_gate_evidence(
    result: CrashExperimentResult,
    *,
    kind: str = "native-qualification",
) -> CIRunEvidence:
    gate = result.gate
    checks = tuple(
        CICheck(
            check_id=check.check_id,
            status=_status(check.status),
            summary=check.label,
            expected=check.expected,
            actual=check.actual,
        )
        for check in gate.checks
    )
    rto = (
        result.recovery_process.completed_at - result.recovery_process.started_at
    ).total_seconds()
    return CIRunEvidence(
        kind=kind,
        status=CIStatus.VERIFIED if gate.passed else CIStatus.FAILED,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="native-pytorch",
        checks=checks,
        fault="process_termination",
        rpo_steps=gate.achieved_rollback_steps,
        rto_seconds=rto,
    )


def _repair_evidence(result: RepairLoopResult) -> CIRunEvidence:
    return _native_gate_evidence(result.repaired_run)


def _hf_evidence(result: HFQualificationResult) -> CIRunEvidence:
    checks = tuple(
        CICheck(
            check_id=check.check_id,
            status=_status(check.status),
            summary=check.label,
            expected=check.expected,
            actual=check.actual,
        )
        for check in result.gate.checks
    )
    rto = (
        result.recovery_process.completed_at - result.recovery_process.started_at
    ).total_seconds()
    return CIRunEvidence(
        kind="hf-qualification",
        status=CIStatus.VERIFIED if result.gate.passed else CIStatus.FAILED,
        qualification_profile=QualificationProfile.EXACT_TRAINING_RESUME,
        framework="huggingface-trainer",
        checks=checks,
        fault="process_termination",
        rpo_steps=result.gate.achieved_rpo_steps,
        rto_seconds=rto,
    )


def normalize_run_evidence(result: object) -> CIRunEvidence:
    if isinstance(result, StaticAuditResult):
        return _audit_evidence(result)
    if isinstance(result, RepairLoopResult):
        return _repair_evidence(result)
    if isinstance(result, CrashExperimentResult):
        return _native_gate_evidence(result)
    if isinstance(result, HFQualificationResult):
        return _hf_evidence(result)
    raise CIEvidenceError("unsupported run evidence type")


def _read_run_result(run_root: Path) -> object:
    candidates = (run_root / "result.json", run_root / "audit.json")
    source = next((candidate for candidate in candidates if candidate.is_file()), None)
    if source is None or source.is_symlink():
        raise CIEvidenceError("run directory lacks a safe result.json or audit.json")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
        schema = payload.get("schema_version") if isinstance(payload, dict) else None
        model = {
            "repair-loop-result-v1": RepairLoopResult,
            "crash-experiment-v1": CrashExperimentResult,
            "flashpilot-hf-qualification-v1": HFQualificationResult,
            "flashpilot-static-audit-v1": StaticAuditResult,
        }.get(schema)
        if model is None:
            raise CIEvidenceError(f"unsupported run schema: {schema}")
        return model.model_validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValidationError) as error:
        raise CIEvidenceError("run result is malformed") from error


def _base_exit_code(evidence: CIRunEvidence) -> int:
    if evidence.status in {CIStatus.VERIFIED, CIStatus.PASS}:
        return EXIT_VERIFIED
    if evidence.status in {CIStatus.WARN, CIStatus.UNKNOWN}:
        return EXIT_REVIEW
    return EXIT_QUALIFICATION_FAILED


def _write_or_verify_text(
    *,
    root: Path,
    relative_path: str,
    expected: str,
    allow_create: bool = True,
) -> Path:
    path = PathSandbox.create(root).resolve_relative(relative_path)
    if path.exists():
        try:
            actual = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise CIEvidenceError(f"existing {relative_path} is unreadable") from error
        if actual != expected:
            raise CIEvidenceError(f"existing {relative_path} differs from run evidence")
        return path
    if not allow_create:
        raise CIEvidenceError(f"attested run is missing {relative_path}")
    return write_text_artifact(run_root=root, relative_path=relative_path, text=expected)


def write_qualification_ci_outputs(
    *,
    run_root: Path,
    result: RepairLoopResult | CrashExperimentResult | HFQualificationResult,
) -> tuple[Path, Path]:
    evidence = normalize_run_evidence(result)
    junit = _write_or_verify_text(
        root=run_root,
        relative_path=QUALIFICATION_JUNIT_PATH,
        expected=render_qualification_junit(evidence),
    )
    summary = _write_or_verify_text(
        root=run_root,
        relative_path=JOB_SUMMARY_PATH,
        expected=render_job_summary(evidence),
    )
    return junit, summary


def write_static_audit_job_summary(
    *,
    run_root: Path,
    result: StaticAuditResult,
) -> Path:
    evidence = normalize_run_evidence(result)
    return _write_or_verify_text(
        root=run_root,
        relative_path=JOB_SUMMARY_PATH,
        expected=render_job_summary(evidence),
    )


def emit_ci_outputs(
    *,
    run_root: Path,
    policy: CIPolicyV1 | None = None,
) -> CIArtifactResult:
    root = PathSandbox.create(run_root).root
    attestation_exists = (root / "recovery.attestation.json").exists()
    result = _read_run_result(root)
    evidence = normalize_run_evidence(result)
    if isinstance(result, StaticAuditResult):
        junit_text = render_audit_junit(result)
        summary_text = render_job_summary(evidence)
    else:
        junit_text = render_qualification_junit(evidence)
        summary_text = render_job_summary(evidence)
    junit = _write_or_verify_text(
        root=root,
        relative_path=QUALIFICATION_JUNIT_PATH,
        expected=junit_text,
        allow_create=not attestation_exists,
    )
    summary = _write_or_verify_text(
        root=root,
        relative_path=JOB_SUMMARY_PATH,
        expected=summary_text,
        allow_create=not attestation_exists,
    )
    if attestation_exists:
        if evidence.status is not CIStatus.VERIFIED:
            raise CIEvidenceError("non-verified run must not contain a recovery attestation")
        from flashpilot.attestation import (
            AttestationVerificationError,
            verify_recovery_attestation,
        )

        try:
            verify_recovery_attestation(root / "recovery.attestation.json")
        except (
            AttestationVerificationError,
            OSError,
            UnicodeError,
            ValueError,
        ) as error:
            raise CIEvidenceError("existing recovery attestation is invalid or tampered") from error
    evaluation = (
        evaluate_ci_policy(run_root=root, evidence=evidence, policy=policy)
        if policy is not None
        else None
    )
    exit_code = _base_exit_code(evidence)
    if evaluation is not None and not evaluation.passed:
        exit_code = EXIT_QUALIFICATION_FAILED
    return CIArtifactResult(
        evidence=evidence,
        junit_path=junit,
        job_summary_path=summary,
        policy_evaluation=evaluation,
        exit_code=exit_code,
    )
