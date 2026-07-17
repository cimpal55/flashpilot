"""Grouped plain-text rendering for Recovery Gate results."""

from flashpilot.domain.recovery import GateCategory, RecoveryGateResult

_CATEGORY_ORDER: tuple[GateCategory, ...] = (
    "Integrity",
    "Required training state",
    "Process recovery",
    "Trajectory correctness",
    "Safety and rollback",
)


def render_recovery_gate(result: RecoveryGateResult) -> str:
    verdict = "VERIFIED" if result.passed else "FAILED"
    lines = [f"Recovery Gate — {verdict}"]
    for category in _CATEGORY_ORDER:
        lines.append(f"\n{category}")
        for check in result.checks:
            if check.category != category:
                continue
            status = check.status.upper().replace("_", " ")
            lines.append(f"  [{status}] {check.check_id}: {check.label}")
    lines.append(
        f"\nAchieved rollback: {result.achieved_rollback_steps} steps "
        f"(hard limit: {result.hard_rollback_limit_steps})"
    )
    lines.append("Comparison policy: exact equality (atol=0.0, rtol=0.0)")
    return "\n".join(lines) + "\n"
