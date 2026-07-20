"""Deterministic aggregate reports for randomized fault timing."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from flashpilot.fault_timing.models import RandomizedFaultTimingResult


def render_timing_markdown(result: RandomizedFaultTimingResult) -> str:
    rows = "\n".join(
        "| {} | {} | {} | {} | {} | {:.6f} | **{}** |".format(
            trial.schedule.iteration,
            trial.schedule.checkpoint_step,
            trial.schedule.fault_after_step,
            trial.achieved_rpo_steps,
            f"{trial.producer_pid} -> {trial.recovery_pid}",
            trial.rto_seconds,
            "PASS" if trial.passed else "FAILED",
        )
        for trial in result.trials
    )
    return (
        "# Repeated randomized fault-timing qualification\n\n"
        f"- Verdict: **{result.final_verdict}**\n"
        f"- Seed: `{result.seed}`\n"
        f"- Trials: `{result.passed_trials}/{result.iterations}`\n"
        f"- Unique timing pairs: `{result.unique_timing_pairs}`\n"
        f"- Observed RPO values: `{result.observed_rpo_steps}`\n"
        f"- Schedule SHA-256: `{result.schedule_sha256}`\n"
        "- Exact Recovery Gate: `24/24 required per trial`\n"
        "- Attestation emitted: `false`\n"
        "- Storage savings reported: `false`\n\n"
        "| Trial | Checkpoint step | Fault after step | RPO | PIDs | RTO seconds | Verdict |\n"
        "| ---: | ---: | ---: | ---: | --- | ---: | --- |\n"
        f"{rows}\n\n"
        "## Limitations\n\n"
        + "\n".join(f"- {limitation}" for limitation in result.limitations)
        + "\n"
    )


def render_timing_junit(result: RandomizedFaultTimingResult) -> str:
    suite = Element(
        "testsuite",
        name="flashpilot.randomized-fault-timing",
        tests=str(result.iterations),
        failures=str(result.failed_trials),
        errors="0",
        skipped="0",
    )
    for trial in result.trials:
        case = SubElement(
            suite,
            "testcase",
            classname="flashpilot.fault-timing.native-safe-full",
            name=f"trial-{trial.schedule.iteration:04d}",
            time=f"{trial.rto_seconds:.9f}",
        )
        if not trial.passed:
            failure = SubElement(
                case,
                "failure",
                message="randomized fault-timing trial failed",
                type="recovery-gate",
            )
            failure.text = (
                f"checkpoint_step={trial.schedule.checkpoint_step}; "
                f"fault_after_step={trial.schedule.fault_after_step}; "
                f"failed_checks={trial.failed_gate_check_ids}"
            )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(suite, encoding="unicode", short_empty_elements=True)
        + "\n"
    )


def render_timing_job_summary(result: RandomizedFaultTimingResult) -> str:
    return (
        "# FlashPilot repeated randomized fault timing\n\n"
        f"**Verdict: {result.final_verdict}**\n\n"
        f"{result.passed_trials}/{result.iterations} real process-kill trials passed "
        f"with RPO coverage {result.observed_rpo_steps}.\n\n"
        f"Schedule SHA-256: `{result.schedule_sha256}`.\n"
    )
