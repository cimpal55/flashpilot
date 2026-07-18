"""Self-contained deterministic HTML rendered only from a repair-loop result."""

from __future__ import annotations

from html import escape

from flashpilot.domain.repair import RepairLoopResult


def _value(value: object) -> str:
    return escape(str(value))


def render_repair_html(result: RepairLoopResult) -> str:
    """Render one static report without network assets or experiment logic."""

    initial_checks = "".join(
        f"<li><code>{escape(check_id)}</code></li>"
        for check_id in result.initial_failure.gate.failed_check_ids
    )
    action_rows = "".join(
        "<tr>"
        f"<td><code>{escape(decision.action)}</code></td>"
        f'<td class="{escape(decision.disposition)}">'
        f"{escape(decision.disposition.upper())}</td>"
        f"<td>{escape(decision.reason)}</td>"
        "</tr>"
        for decision in result.plan_validation.decisions
    )
    gate_rows = "".join(
        "<tr>"
        f"<td>{escape(check.category)}</td>"
        f"<td><code>{escape(check.check_id)}</code></td>"
        f'<td class="{escape(check.status)}">{escape(check.status.upper())}</td>'
        f"<td>{escape(check.label)}</td>"
        "</tr>"
        for check in result.repaired_run.gate.checks
    )
    storage_html = (
        "<section><h2>Verified storage comparison</h2>"
        '<p class="verified headline">'
        f"{result.storage_comparison.structural_reduction_bytes:,} fewer recurring "
        "logical bytes "
        f"({result.storage_comparison.structural_reduction_percent:.2f}%)</p>"
        "<dl>"
        f"<dt>safe_full recurring logical bytes</dt><dd>"
        f"{result.storage_comparison.safe_full_bytes:,}</dd>"
        f"<dt>Repaired recurring logical bytes</dt><dd>"
        f"{result.storage_comparison.repaired_recurring_bytes:,}</dd>"
        f"<dt>One-time frozen-base cost</dt><dd>"
        f"{result.storage_comparison.repaired_one_time_base_bytes:,}</dd>"
        "</dl>"
        "<p>The first adapter-aware write is not presented as savings; the immutable "
        "base is a separate one-time cost.</p></section>"
        if result.repaired_run.gate.passed and result.storage_comparison is not None
        else "<section><h2>Storage comparison withheld</h2>"
        "<p>No savings are reported because the final Recovery Gate did not pass.</p></section>"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FlashPilot bounded repair report</title>
<style>
:root {{ color-scheme: dark; --bg:#0b1020; --card:#121a2f; --text:#e8edf8;
--muted:#9ca9c6; --pass:#46d17d; --fail:#ff6577; --warn:#f6c85f; --info:#71b7ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--text);
font:16px/1.5 system-ui,sans-serif; }} main {{ max-width:1100px; margin:auto; padding:32px 20px; }}
section {{ background:var(--card); border:1px solid #263351; border-radius:12px;
padding:20px; margin:18px 0; }} h1,h2 {{ margin-top:0; }} .eyebrow {{ color:var(--info);
font-weight:700; letter-spacing:.08em; text-transform:uppercase; }} .verified,.pass {{ color:var(--pass); }}
.fail {{ color:var(--fail); }} .unsupported {{ color:var(--warn); }} .accepted {{ color:var(--info); }}
.headline {{ font-size:1.6rem; font-weight:800; }} table {{ border-collapse:collapse; width:100%; }}
th,td {{ border-bottom:1px solid #2b3858; padding:10px; text-align:left; vertical-align:top; }}
code {{ color:#c9d7ff; }} dl {{ display:grid; grid-template-columns:2fr 1fr; gap:8px 18px; }}
dt {{ color:var(--muted); }} dd {{ margin:0; font-weight:700; }} .disclaimer {{ color:var(--warn); }}
</style>
</head>
<body><main>
<p class="eyebrow">Checkpoint recovery qualification and verification harness</p>
<h1>FlashPilot bounded repair report</h1>
<p>Final verdict: <strong class="{escape(result.final_verdict.lower())}">
{escape(result.final_verdict)}</strong>. Only the deterministic Recovery Gate sets this verdict.</p>
<section><h2>Initial designed failure</h2>
<p>Worker PID {_value(result.initial_failure.crash.worker_pid)} was terminated; recovery used PID
{_value(result.initial_failure.recovery.worker_pid)}. The valid checkpoint loaded and the gate failed:</p>
<ul>{initial_checks}</ul></section>
<section><h2>GPT-5.6 captured-response fixture/replay</h2>
<p><strong>GPT source:</strong> GPT-5.6 captured-response fixture/replay</p>
<p>The recommendation is evidence-bounded and cannot declare recovery or execute changes.</p>
<table><thead><tr><th>Proposed action</th><th>Guardrail decision</th><th>Reason</th></tr></thead>
<tbody>{action_rows}</tbody></table></section>
<section><h2>Deterministic bounded repair</h2>
<p>Attempt {_value(result.repair_attempt_count)} created strategy
<code>{escape(result.repair_execution.repaired_config.strategy_id)}</code> without modifying the
historical failed checkpoint.</p></section>
<section><h2>Final Recovery Gate</h2>
<p>Worker PID {_value(result.repaired_run.crash.worker_pid)} was terminated; recovery used PID
{_value(result.repaired_run.recovery.worker_pid)}. Comparison remained exact at
atol={_value(result.repaired_run.gate.comparison_policy.atol)},
rtol={_value(result.repaired_run.gate.comparison_policy.rtol)}.</p>
<table><thead><tr><th>Category</th><th>Check ID</th><th>Status</th><th>Check</th></tr></thead>
<tbody>{gate_rows}</tbody></table></section>
{storage_html}
<section class="disclaimer"><strong>Measurement limitation:</strong> Logical checkpoint bytes were
measured in the controlled demo. Physical NAND writes, write amplification, and SSD lifetime were
not measured.</section>
</main></body></html>
"""
