"""Deterministic reports for previous-valid fallback evidence."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from flashpilot.fallback.models import PreviousValidFallbackResult


def render_fallback_markdown(result: PreviousValidFallbackResult) -> str:
    selection = "\n".join(
        f"- `{check.check_id}`: **{check.status.upper()}** -- {check.summary}"
        for check in result.selection_checks
    )
    gate = "\n".join(
        f"- `{check.check_id}`: **{check.status.upper()}** -- {check.label}"
        for check in result.gate.checks
    )
    return (
        "# Previous-valid checkpoint fallback qualification\n\n"
        f"- Verdict: **{result.final_verdict}**\n"
        f"- Rejected newest checkpoint: `{result.newest_checkpoint_path}`\n"
        f"- Selected previous checkpoint: `{result.selected_checkpoint_path}`\n"
        f"- Achieved RPO: `{result.gate.achieved_rollback_steps}` steps\n"
        f"- Hard RPO limit: `{result.gate.hard_rollback_limit_steps}` steps\n"
        f"- Producer PID: `{result.checkpoint_set_event.worker_pid}`\n"
        f"- Recovery PID: `{result.recovery.worker_pid}`\n"
        f"- Recovery Gate: `{len(result.gate.checks) - len(result.gate.failed_check_ids)}/"
        f"{len(result.gate.checks)}`\n"
        "- Attestation emitted: `false`\n"
        "- Storage savings reported: `false`\n\n"
        "## Fallback selection checks\n\n"
        f"{selection}\n\n"
        "## Recovery Gate\n\n"
        f"{gate}\n\n"
        "## Limitations\n\n"
        + "\n".join(f"- {limitation}" for limitation in result.limitations)
        + "\n"
    )


def render_fallback_junit(result: PreviousValidFallbackResult) -> str:
    total = len(result.selection_checks) + len(result.gate.checks)
    failures = sum(check.status == "fail" for check in result.selection_checks) + len(
        result.gate.failed_check_ids
    )
    suite = Element(
        "testsuite",
        name="flashpilot.previous-valid-fallback",
        tests=str(total),
        failures=str(failures),
        errors="0",
        skipped="0",
    )
    for check in result.selection_checks:
        case = SubElement(
            suite,
            "testcase",
            classname="flashpilot.fallback.selection",
            name=check.check_id,
        )
        if check.status == "fail":
            failure = SubElement(case, "failure", message=check.summary, type="selection")
            failure.text = f"expected={check.expected}; actual={check.actual}"
    for check in result.gate.checks:
        case = SubElement(
            suite,
            "testcase",
            classname="flashpilot.fallback.recovery-gate",
            name=check.check_id,
        )
        if check.status == "fail":
            failure = SubElement(case, "failure", message=check.label, type="recovery-gate")
            failure.text = f"expected={check.expected}; actual={check.actual}"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(suite, encoding="unicode", short_empty_elements=True)
        + "\n"
    )


def render_fallback_job_summary(result: PreviousValidFallbackResult) -> str:
    return (
        "# FlashPilot previous-valid fallback qualification\n\n"
        f"**Verdict: {result.final_verdict}**\n\n"
        f"Selected step {result.selected_checkpoint_step} after rejecting step 4; "
        f"RPO {result.gate.achieved_rollback_steps}/"
        f"{result.gate.hard_rollback_limit_steps} steps.\n\n"
        f"Recovery Gate: {len(result.gate.checks) - len(result.gate.failed_check_ids)}/"
        f"{len(result.gate.checks)}.\n"
    )
