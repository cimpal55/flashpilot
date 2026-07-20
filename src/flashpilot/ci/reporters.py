"""Deterministic JUnit and GitHub job-summary views of qualification evidence."""

from __future__ import annotations

from xml.etree import ElementTree

from flashpilot.ci.models import CICheckStatus, CIRunEvidence

QUALIFICATION_JUNIT_PATH = "junit.xml"
JOB_SUMMARY_PATH = "job-summary.md"


def render_qualification_junit(evidence: CIRunEvidence) -> str:
    failures = sum(check.status is CICheckStatus.FAIL for check in evidence.checks)
    skipped = sum(
        check.status in {CICheckStatus.WARN, CICheckStatus.UNKNOWN} for check in evidence.checks
    )
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": f"flashpilot.{evidence.kind}",
            "tests": str(len(evidence.checks)),
            "failures": str(failures),
            "errors": "0",
            "skipped": str(skipped),
        },
    )
    properties = ElementTree.SubElement(suite, "properties")
    for name, value in (
        ("status", evidence.status.value),
        ("framework", evidence.framework),
        ("qualification_profile", evidence.qualification_profile.value),
        ("rpo_steps", "" if evidence.rpo_steps is None else str(evidence.rpo_steps)),
        ("rto_seconds", "" if evidence.rto_seconds is None else str(evidence.rto_seconds)),
    ):
        ElementTree.SubElement(properties, "property", {"name": name, "value": value})
    for check in evidence.checks:
        case = ElementTree.SubElement(
            suite,
            "testcase",
            {"classname": f"flashpilot.{evidence.framework}", "name": check.check_id},
        )
        detail = check.summary
        if check.expected is not None or check.actual is not None:
            detail += f" Expected={check.expected!s}; actual={check.actual!s}."
        if check.status is CICheckStatus.FAIL:
            failure = ElementTree.SubElement(
                case,
                "failure",
                {"message": check.summary, "type": "qualification-requirement"},
            )
            failure.text = detail
        elif check.status in {CICheckStatus.WARN, CICheckStatus.UNKNOWN}:
            ElementTree.SubElement(
                case,
                "skipped",
                {"message": f"{check.status.value}: {check.summary}"},
            )
        output = ElementTree.SubElement(case, "system-out")
        output.text = detail
    ElementTree.indent(suite, space="  ")
    return ElementTree.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def render_job_summary(evidence: CIRunEvidence) -> str:
    failed = [check for check in evidence.checks if check.status is CICheckStatus.FAIL]
    lines = [
        "# FlashPilot CI summary",
        "",
        f"- Outcome: **{evidence.status.value}**",
        f"- Evidence kind: `{evidence.kind}`",
        f"- Framework: `{evidence.framework}`",
        f"- Qualification profile: `{evidence.qualification_profile.value}`",
        f"- Checks: `{len(evidence.checks) - len(failed)}/{len(evidence.checks)}` non-failing",
    ]
    if evidence.rpo_steps is not None:
        lines.append(f"- RPO: `{evidence.rpo_steps}` steps")
    if evidence.rto_seconds is not None:
        lines.append(f"- RTO: `{evidence.rto_seconds:.6f}` seconds")
    lines.extend(("", "## Exact failed requirements", ""))
    if failed:
        lines.extend(f"- `{check.check_id}` — {check.summary}" for check in failed)
    else:
        lines.append("- None")
    lines.extend(
        (
            "",
            "This summary is derived from the same typed evidence used by the local CLI.",
            "",
        )
    )
    return "\n".join(lines)
