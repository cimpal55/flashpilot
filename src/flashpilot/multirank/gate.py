"""Deterministic checks for a targeted multi-rank process failure."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from flashpilot.multirank.models import MultiRankFailureEvent

if TYPE_CHECKING:
    from flashpilot.distributed.models import DistributedQualificationCheck


def _check(
    check_id: str,
    label: str,
    passed: bool,
    expected: str,
    actual: str,
) -> DistributedQualificationCheck:
    from flashpilot.distributed.models import DistributedQualificationCheck

    return DistributedQualificationCheck(
        check_id=check_id,
        category="multi-rank-fault",
        label=label,
        status="pass" if passed else "fail",
        expected=expected,
        actual=actual,
    )


def evaluate_multi_rank_failure_checks(
    *,
    event: MultiRankFailureEvent,
    expected_framework: str,
    expected_target_rank: int,
    expected_checkpoint_path: str,
    expected_checkpoint_step: int,
    existing_phase_pids: tuple[int, ...],
    recovery_started_at: datetime,
) -> tuple[DistributedQualificationCheck, ...]:
    """Return exact, non-authoritative checks to append to a Recovery Gate."""

    fault_pids = tuple(item.worker_pid for item in event.rank_processes)
    exit_codes = tuple(item.exit_code for item in event.rank_processes)
    ready_ranks = tuple(item.rank for item in event.ready_evidence)
    ready_loaded = tuple(item.checkpoint_loaded for item in event.ready_evidence)
    target = event.rank_processes[event.target_rank]
    peer = event.rank_processes[1 - event.target_rank]
    comparisons = (
        (
            "fault.scenario",
            "The selected scenario is targeted rank process termination",
            event.fault_scenario == "rank_process_termination",
            "rank_process_termination",
            event.fault_scenario,
        ),
        (
            "fault.framework",
            "Failure evidence identifies the qualified distributed runtime",
            event.framework == expected_framework,
            expected_framework,
            event.framework,
        ),
        (
            "fault.target-rank",
            "The parent terminated exactly the selected rank",
            event.target_rank == expected_target_rank,
            str(expected_target_rank),
            str(event.target_rank),
        ),
        (
            "fault.all-ranks-ready",
            "Both ranks loaded the checkpoint before fault delivery",
            ready_ranks == (0, 1) and ready_loaded == (True, True),
            "ranks=(0, 1), loaded=(true, true)",
            f"ranks={ready_ranks}, loaded={ready_loaded}",
        ),
        (
            "fault.checkpoint-identity",
            "Every fault rank loaded the validated checkpoint identity",
            str(event.checkpoint_path) == expected_checkpoint_path
            and event.checkpoint_step == expected_checkpoint_step,
            f"{expected_checkpoint_path}@{expected_checkpoint_step}",
            f"{event.checkpoint_path}@{event.checkpoint_step}",
        ),
        (
            "fault.zero-rpo-boundary",
            "Fault delivery occurred at the committed checkpoint boundary",
            event.failure_rpo_steps == 0,
            "0 steps",
            f"{event.failure_rpo_steps} steps",
        ),
        (
            "fault.target-exit",
            "The target rank was externally terminated with a nonzero exit",
            target.externally_terminated and target.exit_code != 0,
            "externally terminated, nonzero exit",
            f"external={target.externally_terminated}, exit={target.exit_code}",
        ),
        (
            "fault.peer-propagation",
            "The surviving rank observed a Gloo collective failure",
            event.peer_failure_propagated and peer.collective_failure_observed,
            "typed peer collective-failure evidence",
            f"observed={peer.collective_failure_observed}",
        ),
        (
            "fault.group-nonzero-exit",
            "No failed-group rank reported a clean exit",
            all(code != 0 for code in exit_codes),
            "two nonzero exits",
            str(exit_codes),
        ),
        (
            "fault.group-cleanup",
            "The parent confirmed the entire failed process group stopped",
            event.group_cleanup_complete,
            "true",
            str(event.group_cleanup_complete).lower(),
        ),
        (
            "fault.distinct-processes",
            "Failed-group ranks are distinct from all clean qualification ranks",
            len(set(existing_phase_pids + fault_pids)) == len(existing_phase_pids) + 2,
            f"{len(existing_phase_pids) + 2} unique PIDs",
            f"{len(set(existing_phase_pids + fault_pids))} unique PIDs",
        ),
        (
            "restore.after-fault",
            "Fresh recovery ranks started only after failed-group cleanup",
            recovery_started_at >= event.emitted_at,
            "recovery start >= failure evidence emission",
            f"recovery={recovery_started_at.isoformat()}, fault={event.emitted_at.isoformat()}",
        ),
    )
    return tuple(_check(*comparison) for comparison in comparisons)
