"""Deterministic reports for managed-preemption certification."""

from __future__ import annotations

from html import escape

from flashpilot.preemption.models import HFPreemptionCertificationResult


def render_preemption_markdown(result: HFPreemptionCertificationResult) -> str:
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
        "# Hugging Face managed-preemption certification\n\n"
        f"- Verdict: **{result.final_verdict}**\n"
        f"- Profile: `{result.qualification_profile}`\n"
        f"- Signal: `{result.signal_name}` via `{result.signal_delivery}`\n"
        f"- Grace period: `{result.grace_period_seconds}` seconds\n"
        f"- Checkpoint commit after signal: `{result.checkpoint_commit_seconds:.6f}` seconds\n"
        f"- Graceful exit after signal: `{result.graceful_exit_seconds:.6f}` seconds\n"
        f"- RPO: `{result.gate.achieved_rpo_steps}` steps / "
        f"`{result.gate.achieved_rpo_tokens}` tokens\n"
        f"- Recovery RTO: `{result.recovery_rto_seconds:.6f}` seconds\n"
        f"- Exact comparison: `atol=0.0`, `rtol=0.0`\n"
        f"- Verified persisted bytes: {storage}\n\n"
        "## Deterministic Gate\n\n"
        f"{checks}\n\n"
        "## Limitations\n\n" + "\n".join(f"- {item}" for item in result.limitations) + "\n"
    )


def render_preemption_html(result: HFPreemptionCertificationResult) -> str:
    checks = "".join(
        f"<li><code>{escape(check.check_id)}</code>: "
        f"<strong>{escape(check.status.upper())}</strong> - {escape(check.label)}</li>"
        for check in result.gate.checks
    )
    limitations = "".join(f"<li>{escape(item)}</li>" for item in result.limitations)
    storage = (
        f"{result.verified_persisted_bytes} bytes"
        if result.verified_persisted_bytes is not None
        else "not reported because recovery did not pass"
    )
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        "<title>FlashPilot managed-preemption certification</title></head><body>"
        "<h1>Hugging Face managed-preemption certification</h1>"
        f"<p><strong>Verdict: {escape(result.final_verdict)}</strong></p>"
        f"<p>Signal: <code>{result.signal_name}</code>; grace period: "
        f"{result.grace_period_seconds} seconds</p>"
        f"<p>Checkpoint commit: {result.checkpoint_commit_seconds:.6f} seconds; "
        f"graceful exit: {result.graceful_exit_seconds:.6f} seconds</p>"
        f"<p>RPO: {result.gate.achieved_rpo_steps} steps / "
        f"{result.gate.achieved_rpo_tokens} tokens; "
        f"recovery RTO: {result.recovery_rto_seconds:.6f} seconds</p>"
        "<p>Exact comparison: <code>atol=0.0, rtol=0.0</code></p>"
        f"<p>Verified persisted bytes: {escape(storage)}</p>"
        f"<h2>Deterministic Gate</h2><ul>{checks}</ul>"
        f"<h2>Limitations</h2><ul>{limitations}</ul>"
        "</body></html>\n"
    )
