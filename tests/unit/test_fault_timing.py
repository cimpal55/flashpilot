from __future__ import annotations

import json
from pathlib import Path

import pytest

from flashpilot.fault_timing.schedule import (
    build_fault_timing_schedule,
    schedule_sha256,
)
from flashpilot.fault_timing.schema import timing_schema_documents
from flashpilot.fault_timing.service import (
    RandomizedFaultTimingError,
    run_randomized_fault_timing,
)


def test_seeded_schedule_is_reproducible_and_stratified() -> None:
    first = build_fault_timing_schedule(iterations=8, seed=20_260_720)
    repeated = build_fault_timing_schedule(iterations=8, seed=20_260_720)
    different = build_fault_timing_schedule(iterations=8, seed=20_260_721)

    assert first == repeated
    assert first != different
    assert schedule_sha256(first, seed=20_260_720) == schedule_sha256(
        repeated,
        seed=20_260_720,
    )
    assert {entry.post_commit_steps for entry in first[:4]} == {0, 1, 2, 3}
    assert {entry.post_commit_steps for entry in first[4:]} == {0, 1, 2, 3}
    assert all(entry.fault_after_step <= 7 for entry in first)
    assert len({(entry.checkpoint_step, entry.post_commit_steps) for entry in first}) == 8


@pytest.mark.parametrize(
    ("iterations", "seed"),
    [(3, 0), (33, 0), (4, -1), (4, 9_223_372_036_854_775_808)],
)
def test_schedule_rejects_out_of_contract_inputs(iterations: int, seed: int) -> None:
    with pytest.raises(ValueError):
        build_fault_timing_schedule(iterations=iterations, seed=seed)


def test_runner_refuses_nonempty_output_without_mutation(tmp_path: Path) -> None:
    run_root = tmp_path / "existing"
    run_root.mkdir()
    sentinel = run_root / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(RandomizedFaultTimingError, match="new or empty"):
        run_randomized_fault_timing(run_root=run_root, iterations=4, seed=1)

    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert tuple(run_root.iterdir()) == (sentinel,)


def test_runner_rejects_nonpositive_timeout_before_creating_output(tmp_path: Path) -> None:
    run_root = tmp_path / "not-created"

    with pytest.raises(ValueError, match="timeout must be positive"):
        run_randomized_fault_timing(
            run_root=run_root,
            iterations=4,
            seed=1,
            timeout_seconds=0.0,
        )

    assert not run_root.exists()


@pytest.mark.parametrize(
    "filename",
    [
        "fault-timing-trial-v1.schema.json",
        "randomized-fault-timing-v1.schema.json",
    ],
)
def test_fault_timing_schema_is_checked_in_without_drift(filename: str) -> None:
    expected = timing_schema_documents()[filename]
    actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))

    assert actual == expected
