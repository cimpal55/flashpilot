"""Reproducible RPO-stratified randomized fault schedule."""

from __future__ import annotations

import hashlib
import json
import random

from flashpilot.fault_timing.models import FaultTimingScheduleEntry

MIN_TIMING_ITERATIONS = 4
MAX_TIMING_ITERATIONS = 32
MAX_RPO_STEPS = 3
MAX_SEED = 9_223_372_036_854_775_807


def build_fault_timing_schedule(
    *,
    iterations: int,
    seed: int,
) -> tuple[FaultTimingScheduleEntry, ...]:
    """Build seeded randomized boundaries with complete 0-3 RPO coverage."""

    if not MIN_TIMING_ITERATIONS <= iterations <= MAX_TIMING_ITERATIONS:
        raise ValueError(
            f"iterations must be between {MIN_TIMING_ITERATIONS} and {MAX_TIMING_ITERATIONS}"
        )
    if not 0 <= seed <= MAX_SEED:
        raise ValueError(f"seed must be between 0 and {MAX_SEED}")
    generator = random.Random(seed)
    buckets = {rpo: list(range(1, 8 - rpo)) for rpo in range(MAX_RPO_STEPS + 1)}
    for values in buckets.values():
        generator.shuffle(values)
    cursors = {rpo: 0 for rpo in buckets}
    entries = []
    while len(entries) < iterations:
        rpo_order = list(range(MAX_RPO_STEPS + 1))
        generator.shuffle(rpo_order)
        for rpo in rpo_order:
            if len(entries) == iterations:
                break
            choices = buckets[rpo]
            cursor = cursors[rpo]
            if cursor == len(choices):
                generator.shuffle(choices)
                cursor = 0
            checkpoint_step = choices[cursor]
            cursors[rpo] = cursor + 1
            entries.append(
                FaultTimingScheduleEntry(
                    iteration=len(entries) + 1,
                    checkpoint_step=checkpoint_step,
                    post_commit_steps=rpo,
                    fault_after_step=checkpoint_step + rpo,
                )
            )
    return tuple(entries)


def schedule_sha256(schedule: tuple[FaultTimingScheduleEntry, ...], *, seed: int) -> str:
    payload = {
        "schema_version": "flashpilot-fault-timing-schedule-v1",
        "seed": seed,
        "schedule": [entry.model_dump(mode="json") for entry in schedule],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
