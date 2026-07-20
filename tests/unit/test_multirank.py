from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from flashpilot.multirank.gate import evaluate_multi_rank_failure_checks
from flashpilot.multirank.models import (
    MultiRankFailureEvent,
    MultiRankFaultProcessEvidence,
    MultiRankFaultReadyEvidence,
    MultiRankPeerFailureEvidence,
)
from flashpilot.multirank.schema import multi_rank_schema_documents

NOW = datetime(2026, 7, 20, tzinfo=UTC)


def _event(*, framework: str = "pytorch-distributed", target_rank: int = 0):
    is_deepspeed = framework == "deepspeed"
    checkpoint_step = 4
    ready = tuple(
        MultiRankFaultReadyEvidence(
            framework=framework,
            adapter="deepspeed-engine" if is_deepspeed else "pytorch-fsdp",
            strategy="zero" if is_deepspeed else "fsdp",
            implementation="zero-stage-2" if is_deepspeed else "fully_shard",
            zero_stage=2 if is_deepspeed else None,
            rank=rank,
            worker_pid=100 + rank,
            checkpoint_path="checkpoints/checkpoint-step-000004",
            checkpoint_id="checkpoint-step-000004",
            checkpoint_tag="global_step000004" if is_deepspeed else None,
            checkpoint_step=checkpoint_step,
            ready_at=NOW + timedelta(seconds=rank),
        )
        for rank in range(2)
    )
    peer_rank = 1 - target_rank
    processes = tuple(
        MultiRankFaultProcessEvidence(
            rank=rank,
            worker_pid=100 + rank,
            started_at=NOW - timedelta(seconds=1),
            ready_at=ready[rank].ready_at,
            completed_at=NOW + timedelta(seconds=4),
            exit_code=-9 if rank == target_rank else 17,
            externally_terminated=rank == target_rank,
            collective_failure_observed=rank == peer_rank,
            cleanup_forced=False,
        )
        for rank in range(2)
    )
    return MultiRankFailureEvent(
        framework=framework,
        adapter="deepspeed-engine" if is_deepspeed else "pytorch-fsdp",
        strategy="zero" if is_deepspeed else "fsdp",
        implementation="zero-stage-2" if is_deepspeed else "fully_shard",
        zero_stage=2 if is_deepspeed else None,
        target_rank=target_rank,
        checkpoint_path="checkpoints/checkpoint-step-000004",
        checkpoint_id="checkpoint-step-000004",
        checkpoint_tag="global_step000004" if is_deepspeed else None,
        checkpoint_step=checkpoint_step,
        ready_evidence=ready,
        peer_failure=MultiRankPeerFailureEvidence(
            framework=framework,
            target_rank=target_rank,
            observer_rank=peer_rank,
            observer_pid=100 + peer_rank,
            checkpoint_step=checkpoint_step,
            observed_at=NOW + timedelta(seconds=3),
        ),
        rank_processes=processes,
        delivered_at=NOW + timedelta(seconds=2),
        emitted_at=NOW + timedelta(seconds=5),
    )


@pytest.mark.parametrize("framework", ["pytorch-distributed", "deepspeed"])
@pytest.mark.parametrize("target_rank", [0, 1])
def test_multi_rank_failure_event_requires_exact_runtime_and_rank_roles(
    framework: str,
    target_rank: int,
) -> None:
    event = _event(framework=framework, target_rank=target_rank)

    assert tuple(item.rank for item in event.ready_evidence) == (0, 1)
    assert event.rank_processes[target_rank].externally_terminated is True
    assert event.rank_processes[1 - target_rank].collective_failure_observed is True
    assert event.peer_failure.observer_rank == 1 - target_rank
    assert event.failure_rpo_steps == 0


@pytest.mark.parametrize(
    "update,match",
    [
        ({"adapter": "deepspeed-engine"}, "identity"),
        ({"checkpoint_step": 5}, "checkpoint ID"),
        ({"target_rank": 1}, "roles"),
        ({"unexpected": "field"}, "Extra inputs"),
    ],
)
def test_multi_rank_failure_event_fails_closed_on_contradictory_evidence(
    update: dict[str, object],
    match: str,
) -> None:
    payload = _event().model_dump(mode="python")
    payload.update(update)

    with pytest.raises(ValidationError, match=match):
        MultiRankFailureEvent.model_validate(payload)


def test_multi_rank_failure_event_rejects_ready_timestamp_rewriting() -> None:
    payload = _event().model_dump(mode="python")
    payload["rank_processes"][0]["ready_at"] = NOW + timedelta(milliseconds=1)

    with pytest.raises(ValidationError, match="timestamps must agree"):
        MultiRankFailureEvent.model_validate(payload)


def test_multi_rank_gate_fails_if_peer_propagation_claim_is_false() -> None:
    event = _event().model_copy(update={"peer_failure_propagated": False})

    checks = evaluate_multi_rank_failure_checks(
        event=event,
        expected_framework="pytorch-distributed",
        expected_target_rank=0,
        expected_checkpoint_path="checkpoints/checkpoint-step-000004",
        expected_checkpoint_step=4,
        existing_phase_pids=(1, 2, 3, 4, 5, 6),
        recovery_started_at=NOW + timedelta(seconds=6),
    )

    failed = tuple(check.check_id for check in checks if check.status == "fail")
    assert failed == ("fault.peer-propagation",)


def test_multi_rank_schemas_match_checked_files() -> None:
    import json
    from pathlib import Path

    for filename, expected in multi_rank_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected
