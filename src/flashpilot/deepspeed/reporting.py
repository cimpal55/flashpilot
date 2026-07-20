"""Deterministic Markdown and HTML for DeepSpeed ZeRO-2 qualification."""

from __future__ import annotations

from html import escape

from flashpilot.deepspeed.models import DeepSpeedQualificationResult


def render_deepspeed_markdown(result: DeepSpeedQualificationResult) -> str:
    checks = "\n".join(
        f"- `{check.check_id}`: **{check.status.upper()}** - {check.label}"
        for check in result.gate.checks
    )
    storage = (
        f"{result.verified_persisted_bytes} bytes"
        if result.verified_persisted_bytes is not None
        else "not reported because recovery did not pass"
    )
    return (
        "# DeepSpeed ZeRO-2 qualification\n\n"
        f"- Verdict: **{result.final_verdict}**\n"
        f"- Strategy: `{result.strategy}` (`{result.implementation}`)\n"
        f"- Backend: `{result.backend}`\n"
        f"- World size: `{result.world_size}`\n"
        f"- Control PIDs: `{tuple(item.worker_pid for item in result.control_processes.ranks)}`\n"
        f"- Checkpoint PIDs: "
        f"`{tuple(item.worker_pid for item in result.checkpoint_processes.ranks)}`\n"
        f"- Recovery PIDs: `{tuple(item.worker_pid for item in result.recovery_processes.ranks)}`\n"
        "- Exact comparison: `atol=0.0`, `rtol=0.0`\n"
        f"- Recovery RTO: `{result.recovery_rto_seconds:.6f}` seconds\n"
        f"- Verified persisted bytes: {storage}\n\n"
        "## Deterministic Recovery Gate\n\n"
        f"{checks}\n\n"
        "## Limitations\n\n" + "\n".join(f"- {item}" for item in result.limitations) + "\n"
    )


def render_deepspeed_html(result: DeepSpeedQualificationResult) -> str:
    checks = "".join(
        f"<li><code>{escape(check.check_id)}</code>: "
        f"<strong>{escape(check.status.upper())}</strong> - {escape(check.label)}</li>"
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
        "<title>FlashPilot DeepSpeed ZeRO-2 qualification</title></head><body>"
        "<h1>DeepSpeed ZeRO-2 qualification</h1>"
        f"<p><strong>Verdict: {escape(result.final_verdict)}</strong></p>"
        f"<p>Strategy: <code>{escape(result.strategy)}</code> "
        f"(<code>{escape(result.implementation)}</code>)</p>"
        f"<p>Backend: <code>{escape(result.backend)}</code>; "
        f"world size: {result.world_size}</p>"
        "<p>Exact comparison: <code>atol=0.0, rtol=0.0</code></p>"
        f"<p>Recovery RTO: {result.recovery_rto_seconds:.6f} seconds</p>"
        f"<p>Verified persisted bytes: {escape(storage)}</p>"
        f"<h2>Deterministic Recovery Gate</h2><ul>{checks}</ul>"
        f"<h2>Limitations</h2><ul>{limitations}</ul>"
        "</body></html>\n"
    )
