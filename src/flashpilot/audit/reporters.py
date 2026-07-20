"""Deterministic JSON, Markdown, and JUnit output for static audits."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from flashpilot.audit.models import AuditStatus, StaticAuditResult

AUDIT_JSON = "audit.json"
AUDIT_MARKDOWN = "report.md"
AUDIT_JUNIT = "junit.xml"


def render_markdown(result: StaticAuditResult) -> str:
    lines = [
        "# FlashPilot static checkpoint audit",
        "",
        f"- Status: **{result.status.value}**",
        f"- Framework: `{result.framework.value}`",
        f"- Qualification profile: `{result.qualification_profile.value}`",
        f"- Checkpoint: `{result.checkpoint_name}`",
        "- Scope: static metadata and artifact inspection only",
        "- Recovery verified: `false`",
        "",
        "A static PASS is not a Recovery Gate verdict and never means VERIFIED recovery.",
        "",
        "## Checks",
        "",
        "| Status | Check | Requirement | Summary |",
        "|---|---|---|---|",
    ]
    for check in result.checks:
        requirement = check.requirement_state_id or "-"
        summary = check.summary.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {check.status.value} | `{check.check_id}` | `{requirement}` | {summary} |")
    lines.append("")
    return "\n".join(lines)


def render_junit(result: StaticAuditResult) -> str:
    failures = sum(check.status is AuditStatus.FAIL for check in result.checks)
    skipped = sum(
        check.status in {AuditStatus.WARN, AuditStatus.UNKNOWN} for check in result.checks
    )
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": "flashpilot.static-audit",
            "tests": str(len(result.checks)),
            "failures": str(failures),
            "errors": "0",
            "skipped": str(skipped),
        },
    )
    properties = ElementTree.SubElement(suite, "properties")
    for name, value in (
        ("status", result.status.value),
        ("framework", result.framework.value),
        ("qualification_profile", result.qualification_profile.value),
        ("recovery_verified", "false"),
    ):
        ElementTree.SubElement(properties, "property", {"name": name, "value": value})
    for check in result.checks:
        case = ElementTree.SubElement(
            suite,
            "testcase",
            {
                "classname": f"flashpilot.audit.{result.framework.value}",
                "name": check.check_id,
            },
        )
        if check.status is AuditStatus.FAIL:
            failure = ElementTree.SubElement(
                case,
                "failure",
                {"message": check.summary, "type": "static-audit-requirement"},
            )
            failure.text = check.summary
        elif check.status in {AuditStatus.WARN, AuditStatus.UNKNOWN}:
            ElementTree.SubElement(
                case,
                "skipped",
                {"message": f"{check.status.value}: {check.summary}"},
            )
        output = ElementTree.SubElement(case, "system-out")
        output.text = check.summary
    ElementTree.indent(suite, space="  ")
    return ElementTree.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def write_audit_outputs(result: StaticAuditResult, output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / AUDIT_JSON
    markdown_path = output_dir / AUDIT_MARKDOWN
    junit_path = output_dir / AUDIT_JUNIT
    json_path.write_text(
        result.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    markdown_path.write_text(render_markdown(result), encoding="utf-8", newline="\n")
    junit_path.write_text(render_junit(result), encoding="utf-8", newline="\n")
    return json_path, markdown_path, junit_path
