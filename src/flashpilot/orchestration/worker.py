"""Checkpoint and recovery subprocess entry point."""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path

from flashpilot.checkpoints.adapter_strategies import (
    restore_missing_training_state,
    restore_safe_adapter_aware,
    save_missing_training_state,
    save_safe_adapter_aware,
)
from flashpilot.checkpoints.strategies import restore_safe_full, save_safe_full
from flashpilot.domain.recovery import (
    CheckpointCommittedEvent,
    CheckpointStrategy,
    RecoveryCompletedEvent,
    RecoveryWorkerResult,
    RngStateDigests,
    RuntimeSnapshot,
)
from flashpilot.domain.repair import CheckpointStrategyConfig
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.verification.observations import observe_rng_state, observe_runtime
from flashpilot.workload.profiles import get_profile
from flashpilot.workload.trainer import TrainingRuntime, create_training_runtime, train_until


def _strategy_values() -> tuple[str, ...]:
    return ("safe_full", "safe_adapter_aware", "missing_training_state")


def _load_strategy_config(
    args: argparse.Namespace,
    *,
    sandbox: PathSandbox,
    strategy: CheckpointStrategy,
) -> CheckpointStrategyConfig | None:
    if args.strategy_config is None:
        return None
    if strategy != "safe_adapter_aware":
        raise ValueError("a repaired strategy config requires safe_adapter_aware storage")
    path = sandbox.resolve_relative(args.strategy_config, must_exist=True)
    config = CheckpointStrategyConfig.model_validate_json(path.read_text(encoding="utf-8"))
    config.require_complete_training_state()
    return config


def _checkpoint_worker(args: argparse.Namespace) -> int:
    run_root = Path(args.run_root).resolve()
    sandbox = PathSandbox.create(run_root)
    profile = get_profile(args.profile)
    if args.checkpoint_step <= 0 or args.checkpoint_step >= profile.steps:
        raise ValueError("checkpoint step must be before the final profile step")
    if args.post_commit_steps < 0:
        raise ValueError("post-commit steps cannot be negative")

    runtime = create_training_runtime(profile)
    train_until(runtime, args.checkpoint_step)
    committed_path: Path | None = None
    checkpoint_snapshot: RuntimeSnapshot | None = None
    checkpoint_rng: RngStateDigests | None = None
    committed_at: datetime | None = None

    def after_atomic_rename(path: Path) -> None:
        nonlocal committed_path, checkpoint_snapshot, checkpoint_rng, committed_at
        committed_path = sandbox.require_contained(path, must_exist=True)
        checkpoint_snapshot = observe_runtime(runtime)
        checkpoint_rng = observe_rng_state()
        committed_at = datetime.now(UTC)

    strategy: CheckpointStrategy = args.strategy
    strategy_config = _load_strategy_config(args, sandbox=sandbox, strategy=strategy)
    if strategy == "safe_full":
        save_safe_full(runtime, run_root=run_root, on_committed=after_atomic_rename)
    elif strategy == "safe_adapter_aware":
        checkpoint_root = (
            f"checkpoints/repaired/{strategy_config.strategy_id}"
            if strategy_config is not None
            else "checkpoints/safe-adapter-aware"
        )
        save_safe_adapter_aware(
            runtime,
            run_root=run_root,
            checkpoint_root_relative=checkpoint_root,
            on_committed=after_atomic_rename,
        )
    else:
        save_missing_training_state(runtime, run_root=run_root, on_committed=after_atomic_rename)

    if (
        committed_path is None
        or checkpoint_snapshot is None
        or checkpoint_rng is None
        or committed_at is None
    ):
        raise RuntimeError("checkpoint commit callback did not complete")

    train_until(runtime, args.checkpoint_step + args.post_commit_steps)
    relative_checkpoint = committed_path.relative_to(sandbox.root).as_posix()
    event = CheckpointCommittedEvent(
        worker_pid=os.getpid(),
        checkpoint_step=args.checkpoint_step,
        last_completed_step=runtime.global_step,
        checkpoint_path=relative_checkpoint,
        committed_at=committed_at,
        checkpoint_snapshot=checkpoint_snapshot,
        rng_state=checkpoint_rng,
    )
    print(event.model_dump_json(), flush=True)

    # The parent owns termination after validating the committed event and path.
    threading.Event().wait()
    return 0


def _restore_runtime(
    strategy: CheckpointStrategy, *, run_root: Path, checkpoint_path: Path
) -> TrainingRuntime:
    if strategy == "safe_full":
        return restore_safe_full(run_root=run_root, checkpoint_path=checkpoint_path).runtime
    if strategy == "safe_adapter_aware":
        return restore_safe_adapter_aware(
            run_root=run_root,
            checkpoint_path=checkpoint_path,
        ).runtime
    return restore_missing_training_state(
        run_root=run_root,
        checkpoint_path=checkpoint_path,
    ).runtime


def _recovery_worker(args: argparse.Namespace) -> int:
    started_at = datetime.now(UTC)
    run_root = Path(args.run_root).resolve()
    sandbox = PathSandbox.create(run_root)
    checkpoint_path = sandbox.resolve_relative(args.checkpoint_path, must_exist=True)
    profile = get_profile(args.profile)
    strategy: CheckpointStrategy = args.strategy
    _load_strategy_config(args, sandbox=sandbox, strategy=strategy)
    runtime = _restore_runtime(strategy, run_root=run_root, checkpoint_path=checkpoint_path)
    if runtime.global_step >= profile.steps:
        raise ValueError("recovery checkpoint must precede the final profile step")

    restored_step = runtime.global_step
    after_restore = observe_runtime(runtime)
    after_restore_rng = observe_rng_state()
    first_resumed_batch_step = runtime.global_step
    train_until(runtime, runtime.global_step + 1)
    first_completed_step = runtime.global_step
    train_until(runtime, profile.steps)
    final = observe_runtime(runtime)
    result = RecoveryWorkerResult(
        worker_pid=os.getpid(),
        strategy=strategy,
        checkpoint_path=args.checkpoint_path,
        restored_global_step=restored_step,
        first_resumed_batch_step=first_resumed_batch_step,
        first_completed_step=first_completed_step,
        after_restore=after_restore,
        after_restore_rng=after_restore_rng,
        final=final,
        started_at=started_at,
        completed_at=datetime.now(UTC),
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=args.output_path,
        value=result,
    )
    print(
        RecoveryCompletedEvent(
            worker_pid=os.getpid(),
            output_path=args.output_path,
        ).model_dump_json(),
        flush=True,
    )
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flashpilot-worker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    checkpoint = subparsers.add_parser("checkpoint")
    checkpoint.add_argument("--run-root", required=True)
    checkpoint.add_argument("--profile", choices=("ci", "demo"), required=True)
    checkpoint.add_argument("--strategy", choices=_strategy_values(), required=True)
    checkpoint.add_argument("--checkpoint-step", type=int, required=True)
    checkpoint.add_argument("--post-commit-steps", type=int, default=0)
    checkpoint.add_argument("--strategy-config")

    recover = subparsers.add_parser("recover")
    recover.add_argument("--run-root", required=True)
    recover.add_argument("--profile", choices=("ci", "demo"), required=True)
    recover.add_argument("--strategy", choices=_strategy_values(), required=True)
    recover.add_argument("--checkpoint-path", required=True)
    recover.add_argument("--output-path", required=True)
    recover.add_argument("--strategy-config")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "checkpoint":
            return _checkpoint_worker(args)
        return _recovery_worker(args)
    except Exception as error:
        print(
            f'{{"event":"worker_failed","error_type":"{type(error).__name__}",'
            f'"message":{error_message_json(error)}}}',
            file=sys.stderr,
            flush=True,
        )
        return 2


def error_message_json(error: Exception) -> str:
    return json.dumps(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
