"""Static checkpoint audit orchestration without workload execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flashpilot.audit.detector import detect_checkpoint_framework
from flashpilot.audit.huggingface import audit_huggingface_checkpoint
from flashpilot.audit.models import (
    AuditCheck,
    AuditFramework,
    AuditStatus,
    FrameworkSelection,
    StaticAuditResult,
    aggregate_status,
)
from flashpilot.audit.native import audit_native_checkpoint
from flashpilot.audit.reporters import write_audit_outputs
from flashpilot.audit.safety import (
    AuditSafetyError,
    reject_output_overlap,
    require_safe_checkpoint_directory,
)
from flashpilot.contracts.models import QualificationProfile


class StaticAuditError(ValueError):
    """The requested static audit cannot be configured or persisted safely."""


@dataclass(frozen=True, slots=True)
class StaticAuditRun:
    result: StaticAuditResult
    output_dir: Path
    audit_json: Path
    report_markdown: Path
    junit_xml: Path
    job_summary: Path


def _detection_check(framework: AuditFramework) -> AuditCheck:
    return AuditCheck(
        check_id="detection.framework",
        status=AuditStatus.PASS,
        summary=f"Detected the supported {framework.value} checkpoint layout.",
    )


def _unknown_result(
    *,
    checkpoint_path: Path,
    profile: QualificationProfile,
    summary: str,
) -> StaticAuditResult:
    checks = (
        AuditCheck(
            check_id="detection.framework",
            status=AuditStatus.UNKNOWN,
            summary=summary,
        ),
    )
    return StaticAuditResult(
        status=AuditStatus.UNKNOWN,
        framework=AuditFramework.UNKNOWN,
        qualification_profile=profile,
        checkpoint_name=checkpoint_path.name,
        checks=checks,
    )


def run_static_audit(
    *,
    checkpoint_path: Path,
    framework_selection: FrameworkSelection,
    profile: QualificationProfile,
    output_dir: Path,
) -> StaticAuditRun:
    """Inspect one checkpoint and persist static-only evidence artifacts."""

    try:
        safe_checkpoint = require_safe_checkpoint_directory(checkpoint_path)
        safe_output = reject_output_overlap(
            checkpoint_path=safe_checkpoint,
            output_dir=output_dir,
        )
    except AuditSafetyError as error:
        raise StaticAuditError(str(error)) from error

    detected = detect_checkpoint_framework(safe_checkpoint)
    if framework_selection is FrameworkSelection.AUTO:
        selected = detected
    else:
        selected = AuditFramework(framework_selection.value)

    if detected is AuditFramework.UNKNOWN:
        result = _unknown_result(
            checkpoint_path=safe_checkpoint,
            profile=profile,
            summary="Checkpoint layout is unknown or ambiguous; it was not trusted.",
        )
    elif selected is not detected:
        result = _unknown_result(
            checkpoint_path=safe_checkpoint,
            profile=profile,
            summary=(
                f"Requested {selected.value}, but deterministic detection found {detected.value}."
            ),
        )
    else:
        if selected is AuditFramework.NATIVE_PYTORCH:
            checks = audit_native_checkpoint(safe_checkpoint, profile)
        elif selected is AuditFramework.HUGGINGFACE_TRAINER:
            checks = audit_huggingface_checkpoint(safe_checkpoint, profile)
        else:
            raise StaticAuditError("unsupported static audit framework")
        checks = (_detection_check(selected), *checks)
        result = StaticAuditResult(
            status=aggregate_status(checks),
            framework=selected,
            qualification_profile=profile,
            checkpoint_name=safe_checkpoint.name,
            checks=checks,
        )
    try:
        audit_json, report_markdown, junit_xml = write_audit_outputs(result, safe_output)
        from flashpilot.ci.service import write_static_audit_job_summary

        job_summary = write_static_audit_job_summary(run_root=safe_output, result=result)
    except OSError as error:
        raise StaticAuditError("static audit outputs could not be written") from error
    return StaticAuditRun(
        result=result,
        output_dir=safe_output,
        audit_json=audit_json,
        report_markdown=report_markdown,
        junit_xml=junit_xml,
        job_summary=job_summary,
    )
