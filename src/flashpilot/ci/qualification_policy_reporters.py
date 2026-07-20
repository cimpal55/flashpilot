"""Deterministic CI projections of typed qualification-suite policy results."""

from __future__ import annotations

from xml.etree import ElementTree

from flashpilot.ci.models import CICheckStatus
from flashpilot.ci.qualification_policy_models import QualificationPolicyEvaluationV1
from flashpilot.ci.sarif import render_sarif_checks

POLICY_EVALUATION_PATH = "policy-evaluation.json"
POLICY_JUNIT_PATH = "junit.xml"
POLICY_SUMMARY_PATH = "job-summary.md"
POLICY_SARIF_PATH = "results.sarif"


def _check_detail(summary: str, expected: str | None, actual: str | None) -> str:
    detail = summary
    if expected is not None or actual is not None:
        detail += f" Expected={expected!s}; actual={actual!s}."
    return detail


def render_qualification_policy_junit(evaluation: QualificationPolicyEvaluationV1) -> str:
    checks = evaluation.checks
    failures = sum(check.status is CICheckStatus.FAIL for check in checks)
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": f"flashpilot.qualification-policy.{evaluation.policy_id}",
            "tests": str(len(checks)),
            "failures": str(failures),
            "errors": "0",
            "skipped": "0",
        },
    )
    properties = ElementTree.SubElement(suite, "properties")
    for name, value in (
        ("policy_id", evaluation.policy_id),
        ("policy_sha256", evaluation.policy_sha256),
        ("passed", str(evaluation.passed).lower()),
        ("requirements", str(len(evaluation.requirements))),
    ):
        ElementTree.SubElement(properties, "property", {"name": name, "value": value})
    for requirement in evaluation.requirements:
        for check in requirement.checks:
            case = ElementTree.SubElement(
                suite,
                "testcase",
                {
                    "classname": f"flashpilot.policy.{requirement.requirement_id}",
                    "name": check.check_id,
                },
            )
            detail = _check_detail(check.summary, check.expected, check.actual)
            if check.status is CICheckStatus.FAIL:
                failure = ElementTree.SubElement(
                    case,
                    "failure",
                    {"message": check.summary, "type": "qualification-policy-requirement"},
                )
                failure.text = detail
            output = ElementTree.SubElement(case, "system-out")
            output.text = detail
    ElementTree.indent(suite, space="  ")
    return ElementTree.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def render_qualification_policy_summary(evaluation: QualificationPolicyEvaluationV1) -> str:
    passed = len(evaluation.requirements) - len(evaluation.failed_requirement_ids)
    lines = [
        "# FlashPilot qualification policy",
        "",
        f"- Outcome: **{'PASS' if evaluation.passed else 'FAIL'}**",
        f"- Policy ID: `{evaluation.policy_id}`",
        f"- Policy SHA-256: `{evaluation.policy_sha256}`",
        f"- Requirements: `{passed}/{len(evaluation.requirements)}` passed",
        "",
        "| Requirement | Evidence | Checks | Outcome |",
        "| --- | --- | ---: | --- |",
    ]
    for requirement in evaluation.requirements:
        non_failing = len(requirement.checks) - len(requirement.failed_check_ids)
        evidence = (
            "missing"
            if requirement.evidence is None
            else (f"{requirement.evidence.evidence.kind}/{requirement.evidence.evidence.framework}")
        )
        lines.append(
            f"| `{requirement.requirement_id}` | `{evidence}` | "
            f"{non_failing}/{len(requirement.checks)} | "
            f"{'PASS' if requirement.passed else 'FAIL'} |"
        )
    lines.extend(("", "## Exact failed requirements", ""))
    failed_checks = [
        check
        for requirement in evaluation.requirements
        for check in requirement.checks
        if check.status is CICheckStatus.FAIL
    ]
    if failed_checks:
        lines.extend(f"- `{check.check_id}` — {check.summary}" for check in failed_checks)
    else:
        lines.append("- None")
    lines.extend(
        (
            "",
            "This verdict is derived only from explicitly bound strict local evidence. "
            "No policy expressions or scripts were executed.",
            "",
        )
    )
    return "\n".join(lines)


def render_qualification_policy_sarif(evaluation: QualificationPolicyEvaluationV1) -> str:
    return render_sarif_checks(
        kind="qualification-policy",
        framework="suite",
        checks=evaluation.checks,
        source_uri="policy-evaluation.json",
    )
