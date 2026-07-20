"""Deterministic JSON-derived conversion reports and JUnit."""

from __future__ import annotations

from html import escape
from xml.etree.ElementTree import Element, SubElement, tostring

from flashpilot.conversion.models import ConversionCaseResult, ConversionQualificationResult


def render_case_markdown(result: ConversionCaseResult) -> str:
    checks = "\n".join(
        f"- `{check.check_id}`: **{check.status.upper()}** -- {check.summary}"
        for check in result.checks
    )
    return (
        f"# Checkpoint conversion: {result.conversion_kind.value}\n\n"
        f"- Verdict: **{'PASS' if result.passed else 'FAILED'}**\n"
        f"- Source: `{result.source_representation.value}`\n"
        f"- Candidate: `{result.candidate_representation.value}`\n"
        f"- Equivalence: `{result.comparison_policy.mode}` "
        f"(`atol={result.comparison_policy.atol}`, `rtol={result.comparison_policy.rtol}`)\n"
        f"- Maximum absolute difference: `{result.maximum_absolute_difference}`\n"
        f"- Source unmodified: `{str(result.source_unmodified).lower()}`\n"
        f"- Candidate unmodified: `{str(result.candidate_unmodified).lower()}`\n"
        f"- Comparison PID: `{result.comparison_process_pid}`\n"
        f"- Resume worker PID: `{result.resume_worker_pid or 'not-applicable'}`\n"
        "- Recovery verified: `false`\n"
        "- Storage savings reported: `false`\n\n"
        "## Checks\n\n"
        f"{checks}\n"
    )


def render_case_junit(result: ConversionCaseResult) -> str:
    suite = Element(
        "testsuite",
        name=f"flashpilot.conversion.{result.conversion_kind.value}",
        tests=str(len(result.checks)),
        failures=str(len(result.failed_check_ids)),
        errors="0",
        skipped="0",
    )
    for check in result.checks:
        case = SubElement(
            suite,
            "testcase",
            classname=f"flashpilot.conversion.{result.conversion_kind.value}",
            name=check.check_id,
        )
        if check.status == "fail":
            failure = SubElement(case, "failure", message=check.summary, type="equivalence")
            failure.text = f"expected={check.expected}; actual={check.actual}"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(
            suite,
            encoding="unicode",
            short_empty_elements=True,
        )
        + "\n"
    )


def render_qualification_markdown(result: ConversionQualificationResult) -> str:
    rows = "\n".join(
        "| `{}` | **{}** | `{}` | `{}` | `{}` |".format(
            case.conversion_kind.value,
            "PASS" if case.passed else "FAILED",
            case.comparison_policy.mode,
            case.maximum_absolute_difference,
            str(case.source_unmodified).lower(),
        )
        for case in result.cases
    )
    return (
        "# Checkpoint conversion equivalence qualification\n\n"
        f"- Verdict: **{result.verdict}**\n"
        "- Recovery verified: `false`\n"
        "- Attestation emitted: `false`\n"
        "- Storage savings reported: `false`\n\n"
        "| Conversion | Verdict | Policy | Maximum absolute difference | Source unmodified |\n"
        "| --- | --- | --- | ---: | --- |\n"
        f"{rows}\n\n"
        "## Limitations\n\n" + "\n".join(f"- {item}" for item in result.limitations) + "\n"
    )


def render_qualification_junit(result: ConversionQualificationResult) -> str:
    checks = [(case, check) for case in result.cases for check in case.checks]
    failures = sum(check.status == "fail" for _, check in checks)
    suite = Element(
        "testsuite",
        name="flashpilot.conversion-qualification",
        tests=str(len(checks)),
        failures=str(failures),
        errors="0",
        skipped="0",
    )
    for case_result, check in checks:
        case = SubElement(
            suite,
            "testcase",
            classname=f"flashpilot.conversion.{case_result.conversion_kind.value}",
            name=f"{case_result.conversion_kind.value}.{check.check_id}",
        )
        if check.status == "fail":
            failure = SubElement(case, "failure", message=check.summary, type="equivalence")
            failure.text = f"expected={check.expected}; actual={check.actual}"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(
            suite,
            encoding="unicode",
            short_empty_elements=True,
        )
        + "\n"
    )


def render_job_summary(result: ConversionQualificationResult) -> str:
    failed = ", ".join(case.value for case in result.failed_cases) or "none"
    return (
        "# FlashPilot conversion qualification\n\n"
        f"**Verdict: {escape(result.verdict)}**\n\n"
        f"Failed conversions: {escape(failed)}\n\n"
        "This is deterministic conversion-equivalence evidence, not a Recovery Gate verdict.\n"
    )
