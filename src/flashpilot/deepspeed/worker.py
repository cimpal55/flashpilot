"""Rank worker for the fixed two-rank CPU DeepSpeed ZeRO-2 workload."""

from __future__ import annotations

import argparse
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import torch.distributed as dist

from flashpilot.deepspeed.checkpoint import validate_deepspeed_checkpoint
from flashpilot.deepspeed.workload import (
    create_deepspeed_runtime,
    load_deepspeed_runtime,
    save_deepspeed_runtime,
    summarize_deepspeed_runtime,
    train_deepspeed_until,
)
from flashpilot.multirank.models import (
    MultiRankFaultReadyEvidence,
    MultiRankPeerFailureEvidence,
)
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.workload.profiles import get_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot DeepSpeed ZeRO-2 rank worker")
    parser.add_argument(
        "--mode", choices=("control", "checkpoint", "fault", "recovery"), required=True
    )
    parser.add_argument("--rank", type=int, choices=(0, 1), required=True)
    parser.add_argument("--world-size", type=int, choices=(2,), required=True)
    parser.add_argument("--backend", choices=("gloo",), required=True)
    parser.add_argument("--zero-stage", type=int, choices=(2,), required=True)
    parser.add_argument("--init-method", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workload-profile", choices=("ci", "demo"), required=True)
    parser.add_argument("--checkpoint-step", type=int, required=True)
    parser.add_argument("--checkpoint-tag", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--temporary-checkpoint")
    parser.add_argument("--checkpoint")
    parser.add_argument("--fault-target-rank", type=int, choices=(0, 1))
    parser.add_argument("--peer-failure-output")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    profile = get_profile(arguments.workload_profile)
    if arguments.checkpoint_step <= 0 or arguments.checkpoint_step >= profile.steps:
        raise ValueError("checkpoint step must be positive and precede the final step")
    if arguments.checkpoint_tag != f"global_step{arguments.checkpoint_step:06d}":
        raise ValueError("checkpoint tag must derive from the checkpoint step")
    sandbox = PathSandbox.create(arguments.run_root)
    os.environ.update(
        {
            "RANK": str(arguments.rank),
            "LOCAL_RANK": str(arguments.rank),
            "WORLD_SIZE": str(arguments.world_size),
            "LOCAL_SIZE": str(arguments.world_size),
        }
    )
    dist.init_process_group(
        arguments.backend,
        init_method=arguments.init_method,
        rank=arguments.rank,
        world_size=arguments.world_size,
        timeout=timedelta(seconds=20 if arguments.mode == "fault" else 180),
    )
    try:
        runtime = create_deepspeed_runtime(
            profile=profile,
            rank=arguments.rank,
            world_size=arguments.world_size,
        )
        checkpoint_step = 0
        if arguments.mode == "control":
            if arguments.temporary_checkpoint or arguments.checkpoint:
                raise ValueError("control worker cannot receive checkpoint paths")
            train_deepspeed_until(runtime, profile.steps)
        elif arguments.mode == "checkpoint":
            if not arguments.temporary_checkpoint or arguments.checkpoint:
                raise ValueError("checkpoint worker requires only a temporary checkpoint path")
            temporary = sandbox.resolve_relative(arguments.temporary_checkpoint, must_exist=True)
            final_relative = f"checkpoints/checkpoint-step-{arguments.checkpoint_step:06d}"
            final = sandbox.resolve_relative(final_relative)
            train_deepspeed_until(runtime, arguments.checkpoint_step)
            save_deepspeed_runtime(
                runtime=runtime,
                run_root=sandbox.root,
                temporary_checkpoint_path=temporary,
                final_checkpoint_path=final,
                checkpoint_id=final.name,
                checkpoint_tag=arguments.checkpoint_tag,
            )
            checkpoint_step = arguments.checkpoint_step
        elif arguments.mode in {"fault", "recovery"}:
            if arguments.temporary_checkpoint or not arguments.checkpoint:
                raise ValueError("restore worker requires only a final checkpoint path")
            checkpoint = sandbox.resolve_relative(arguments.checkpoint, must_exist=True)
            validated = validate_deepspeed_checkpoint(
                run_root=sandbox.root,
                checkpoint_path=checkpoint,
            )
            checkpoint_step = load_deepspeed_runtime(
                runtime=runtime,
                run_root=sandbox.root,
                checkpoint_path=checkpoint,
                checkpoint_id=validated.manifest.checkpoint_id,
                checkpoint_tag=arguments.checkpoint_tag,
            )
            if checkpoint_step != arguments.checkpoint_step:
                raise ValueError("loaded checkpoint step differs from the qualification step")
            if arguments.mode == "fault":
                if arguments.fault_target_rank is None or not arguments.peer_failure_output:
                    raise ValueError("fault worker requires target-rank and peer-failure outputs")
                ready = MultiRankFaultReadyEvidence(
                    framework="deepspeed",
                    adapter="deepspeed-engine",
                    strategy="zero",
                    implementation="zero-stage-2",
                    zero_stage=2,
                    rank=arguments.rank,
                    worker_pid=os.getpid(),
                    checkpoint_path=arguments.checkpoint,
                    checkpoint_id=checkpoint.name,
                    checkpoint_tag=arguments.checkpoint_tag,
                    checkpoint_step=checkpoint_step,
                    ready_at=datetime.now(UTC),
                )
                write_json_artifact(
                    run_root=sandbox.root,
                    relative_path=arguments.output,
                    value=ready,
                )
                try:
                    while True:
                        dist.monitored_barrier(
                            timeout=timedelta(seconds=5),
                            wait_all_ranks=True,
                        )
                except RuntimeError:
                    if arguments.rank == arguments.fault_target_rank:
                        raise
                    peer_failure = MultiRankPeerFailureEvidence(
                        framework="deepspeed",
                        target_rank=arguments.fault_target_rank,
                        observer_rank=arguments.rank,
                        observer_pid=os.getpid(),
                        checkpoint_step=checkpoint_step,
                        observed_at=datetime.now(UTC),
                    )
                    write_json_artifact(
                        run_root=sandbox.root,
                        relative_path=arguments.peer_failure_output,
                        value=peer_failure,
                    )
                    return 17
            train_deepspeed_until(runtime, profile.steps)
        else:
            raise ValueError(f"unsupported DeepSpeed worker mode: {arguments.mode}")
        summary = summarize_deepspeed_runtime(
            runtime=runtime,
            phase=arguments.mode,
            checkpoint_step=checkpoint_step,
        )
        write_json_artifact(
            run_root=sandbox.root,
            relative_path=arguments.output,
            value=summary,
        )
        dist.barrier()
        return 0
    finally:
        dist.destroy_process_group()


if __name__ == "__main__":
    raise SystemExit(main())
