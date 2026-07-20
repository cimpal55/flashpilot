"""Rich and JUnit summaries for attestation verification."""

from __future__ import annotations

from xml.etree import ElementTree

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flashpilot.attestation.models import (
    AttestationVerificationResult,
    RecoveryAttestationV1,
)


def render_attestation_junit(result: AttestationVerificationResult) -> str:
    suite = ElementTree.Element(
        "testsuite",
        {
            "name": "flashpilot.attestation-verification",
            "tests": str(len(result.checks)),
            "failures": "0",
            "errors": "0",
            "skipped": "0",
        },
    )
    properties = ElementTree.SubElement(suite, "properties")
    ElementTree.SubElement(
        properties,
        "property",
        {"name": "verdict", "value": result.verdict},
    )
    ElementTree.SubElement(
        properties,
        "property",
        {"name": "attestation_sha256", "value": result.attestation_sha256},
    )
    for check in result.checks:
        case = ElementTree.SubElement(
            suite,
            "testcase",
            {"classname": "flashpilot.attestation", "name": check.check_id},
        )
        output = ElementTree.SubElement(case, "system-out")
        output.text = check.detail
    ElementTree.indent(suite, space="  ")
    return ElementTree.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def render_attestation_summary(
    *,
    console: Console,
    attestation: RecoveryAttestationV1,
    verification: AttestationVerificationResult,
) -> None:
    table = Table(title="Recovery attestation v1", show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Verdict", f"[green]{verification.verdict}[/green]")
    table.add_row("Profile", attestation.qualification_profile.value)
    table.add_row("Framework", f"{attestation.framework} {attestation.framework_version}")
    table.add_row(
        "Source",
        f"{attestation.code_commit[:12]} ({attestation.source_tree_state})",
    )
    table.add_row(
        "Recovery processes",
        f"{attestation.original_worker_pid} -> {attestation.recovery_worker_pid}",
    )
    table.add_row("Recovery Gate", f"{attestation.checks_passed}/{attestation.checks_total}")
    table.add_row("Exact policy", f"atol={attestation.atol}, rtol={attestation.rtol}")
    table.add_row("RPO / RTO", f"{attestation.rpo_steps} steps / {attestation.rto_seconds:.3f}s")
    table.add_row("Persisted bytes", f"{attestation.verified_persisted_bytes:,}")
    table.add_row("Signature", "unsigned (integrity only; no publisher authentication)")
    console.print(Panel(table, border_style="green"))
