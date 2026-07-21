"""Deterministic CI projections for organization policy enforcement."""

from __future__ import annotations

from xml.etree import ElementTree

from flashpilot.ci.models import CICheck, CICheckStatus
from flashpilot.ci.organization_policy_models import OrganizationPolicyEvaluationV1
from flashpilot.ci.sarif import render_sarif_checks

ORGANIZATION_POLICY_EVALUATION_PATH = "organization-policy-evaluation.json"
ORGANIZATION_POLICY_JUNIT_PATH = "junit.xml"
ORGANIZATION_POLICY_SUMMARY_PATH = "job-summary.md"
ORGANIZATION_POLICY_SARIF_PATH = "results.sarif"
REPOSITORY_POLICY_OUTPUT_PATH = "repository-policy"


def _detail(check: CICheck) -> str:
    detail = check.summary
    if check.expected is not None or check.actual is not None:
        detail += f" Expected={check.expected!s}; actual={check.actual!s}."
    return detail


def render_organization_policy_junit(evaluation: OrganizationPolicyEvaluationV1) -> str:
    checks = evaluation.all_checks
    failures = sum(check.status is CICheckStatus.FAIL for check in checks)
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": f"flashpilot.organization-policy.{evaluation.policy_id}",
            "tests": str(len(checks)),
            "failures": str(failures),
            "errors": "0",
            "skipped": "0",
        },
    )
    properties = ElementTree.SubElement(suite, "properties")
    for name, value in (
        ("organization_id", evaluation.organization_id),
        ("policy_id", evaluation.policy_id),
        ("scope_id", evaluation.scope_id),
        ("organization_policy_sha256", evaluation.organization_policy_sha256),
        ("repository_policy_id", evaluation.repository_policy_id),
        ("repository_policy_sha256", evaluation.repository_policy_sha256),
        ("passed", str(evaluation.passed).lower()),
        ("exit_code", str(evaluation.exit_code)),
        ("merge_decision", evaluation.merge_decision),
    ):
        ElementTree.SubElement(properties, "property", {"name": name, "value": value})
    repository_by_requirement = {
        item.requirement_id: item.repository_requirement_id for item in evaluation.requirements
    }
    for check in checks:
        requirement_id = next(
            (
                item.requirement_id
                for item in evaluation.requirements
                if check.check_id.startswith(f"organization.{item.requirement_id}.")
            ),
            "policy",
        )
        case = ElementTree.SubElement(
            suite,
            "testcase",
            {
                "classname": f"flashpilot.organization.{requirement_id}",
                "name": check.check_id,
            },
        )
        if requirement_id in repository_by_requirement:
            case.set(
                "repository_requirement_id",
                repository_by_requirement[requirement_id] or "missing",
            )
        detail = _detail(check)
        if check.status is CICheckStatus.FAIL:
            failure = ElementTree.SubElement(
                case,
                "failure",
                {"message": check.summary, "type": "organization-policy-requirement"},
            )
            failure.text = detail
        output = ElementTree.SubElement(case, "system-out")
        output.text = detail
    ElementTree.indent(suite, space="  ")
    return ElementTree.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def render_organization_policy_summary(evaluation: OrganizationPolicyEvaluationV1) -> str:
    passed = len(evaluation.requirements) - sum(not item.passed for item in evaluation.requirements)
    lines = [
        "# FlashPilot organization qualification policy",
        "",
        f"- Outcome: **{'PASS' if evaluation.passed else 'FAIL'}**",
        f"- Exit code: `{evaluation.exit_code}`",
        f"- Merge: **{evaluation.merge_decision}**",
        f"- Organization: `{evaluation.organization_id}`",
        f"- Organization policy: `{evaluation.policy_id}`",
        f"- Scope: `{evaluation.scope_id}`",
        f"- Organization policy SHA-256: `{evaluation.organization_policy_sha256}`",
        f"- Repository policy: `{evaluation.repository_policy_id}`",
        f"- Repository policy SHA-256: `{evaluation.repository_policy_sha256}`",
        f"- Requirements: `{passed}/{len(evaluation.requirements)}` passed",
        "",
        "| Organization requirement | Repository requirement | Outcome |",
        "| --- | --- | --- |",
    ]
    for requirement in evaluation.requirements:
        lines.append(
            f"| `{requirement.requirement_id}` | "
            f"`{requirement.repository_requirement_id or 'missing'}` | "
            f"{'PASS' if requirement.passed else 'FAIL'} |"
        )
    lines.extend(("", "## Exact failed organization checks", ""))
    failed = [check for check in evaluation.all_checks if check.status is CICheckStatus.FAIL]
    if failed:
        lines.extend(f"- `{check.check_id}` — {check.summary}" for check in failed)
    else:
        lines.append("- None")
    lines.extend(
        (
            "",
            "The organization policy constrains one explicit local repository policy and "
            "its explicit run bindings. No expressions, scripts, repository scans, remote "
            "policy retrieval, or waivers were evaluated.",
            "",
            "This policy result does not create a Recovery Gate verdict or re-certify a "
            "checkpoint. It is derived from the existing deterministic suite evaluation.",
            "",
        )
    )
    return "\n".join(lines)


def render_organization_policy_sarif(evaluation: OrganizationPolicyEvaluationV1) -> str:
    return render_sarif_checks(
        kind="organization-policy",
        framework="suite",
        checks=evaluation.all_checks,
        source_uri=ORGANIZATION_POLICY_EVALUATION_PATH,
    )
