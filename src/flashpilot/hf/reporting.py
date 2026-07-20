"""Deterministic human-readable HF qualification reports."""

from __future__ import annotations

from html import escape

from flashpilot.hf.models import HFQualificationResult


def render_hf_markdown(result: HFQualificationResult) -> str:
    checks = "\n".join(
        f"- `{check.check_id}`: **{check.status.upper()}** — {check.label}"
        for check in result.gate.checks
    )
    storage = (
        f"{result.verified_persisted_bytes} bytes"
        if result.verified_persisted_bytes is not None
        else "not reported because recovery did not pass"
    )
    return (
        "# Hugging Face Trainer qualification\n\n"
        f"- Verdict: **{result.final_verdict}**\n"
        f"- Scenario: `{result.scenario}`\n"
        f"- Adapter: `{result.adapter}`\n"
        f"- Control PID: `{result.control_process.worker_pid}`\n"
        f"- Terminated PID: `{result.crash_process.worker_pid}`\n"
        f"- Recovery PID: `{result.recovery_process.worker_pid}`\n"
        f"- Exact comparison: `atol=0.0`, `rtol=0.0`\n"
        f"- Verified persisted bytes: {storage}\n\n"
        "## Deterministic gate\n\n"
        f"{checks}\n\n"
        "## Limitations\n\n" + "\n".join(f"- {item}" for item in result.limitations) + "\n"
    )


def render_hf_html(result: HFQualificationResult) -> str:
    checks = "".join(
        f"<li><code>{escape(check.check_id)}</code>: "
        f"<strong>{escape(check.status.upper())}</strong> — {escape(check.label)}</li>"
        for check in result.gate.checks
    )
    storage = (
        f"{result.verified_persisted_bytes} bytes"
        if result.verified_persisted_bytes is not None
        else "not reported because recovery did not pass"
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in result.limitations)
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        "<title>FlashPilot HF qualification</title></head><body>"
        "<h1>Hugging Face Trainer qualification</h1>"
        f"<p><strong>Verdict: {escape(result.final_verdict)}</strong></p>"
        f"<p>Scenario: <code>{escape(result.scenario)}</code></p>"
        f"<p>PIDs: {result.control_process.worker_pid} / "
        f"{result.crash_process.worker_pid} / {result.recovery_process.worker_pid}</p>"
        "<p>Exact comparison: <code>atol=0.0, rtol=0.0</code></p>"
        f"<p>Verified persisted bytes: {escape(storage)}</p>"
        f"<h2>Deterministic gate</h2><ul>{checks}</ul>"
        f"<h2>Limitations</h2><ul>{limitations}</ul>"
        "</body></html>\n"
    )
