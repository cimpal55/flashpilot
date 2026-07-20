"""Two-checkpoint producer used by previous-valid fallback qualification."""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path

from flashpilot.checkpoints.strategies import save_safe_full
from flashpilot.fallback.models import (
    FallbackCheckpointRecord,
    FallbackCheckpointSetEvent,
)
from flashpilot.security.paths import PathSandbox
from flashpilot.verification.observations import observe_rng_state, observe_runtime
from flashpilot.workload.profiles import get_profile
from flashpilot.workload.trainer import create_training_runtime, train_until


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot fallback checkpoint producer")
    parser.add_argument("--run-root", type=Path, required=True)
    return parser


def produce(run_root: Path) -> FallbackCheckpointSetEvent:
    root = PathSandbox.create(run_root.resolve()).root
    runtime = create_training_runtime(get_profile("ci"))
    records = []
    for checkpoint_step in (2, 4):
        train_until(runtime, checkpoint_step)

        def committed(path: Path) -> None:
            contained = PathSandbox.create(root).require_contained(path, must_exist=True)
            records.append(
                FallbackCheckpointRecord(
                    checkpoint_path=contained.relative_to(root).as_posix(),
                    global_step=runtime.global_step,
                    committed_at=datetime.now(UTC),
                    snapshot=observe_runtime(runtime),
                    rng_state=observe_rng_state(),
                )
            )

        save_safe_full(runtime, run_root=root, on_committed=committed)
    return FallbackCheckpointSetEvent(
        worker_pid=os.getpid(),
        checkpoints=tuple(records),
        last_completed_step=runtime.global_step,
    )


def main() -> int:
    args = _parser().parse_args()
    try:
        event = produce(args.run_root)
        print(event.model_dump_json(), flush=True)
        threading.Event().wait()
        return 0
    except Exception as error:
        print(
            json.dumps(
                {
                    "event": "fallback_worker_failed",
                    "error_type": type(error).__name__,
                    "message": str(error),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
