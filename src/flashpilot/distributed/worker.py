"""Rank worker for the fixed two-rank FSDP qualification workload."""

from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import torch.distributed as dist

from flashpilot.distributed.checkpoint import validate_distributed_checkpoint
from flashpilot.distributed.workload import (
    create_distributed_runtime,
    load_distributed_runtime,
    save_distributed_runtime,
    summarize_distributed_runtime,
    train_distributed_until,
)
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox
from flashpilot.workload.profiles import get_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot distributed FSDP rank worker")
    parser.add_argument("--mode", choices=("control", "checkpoint", "recovery"), required=True)
    parser.add_argument("--rank", type=int, choices=(0, 1), required=True)
    parser.add_argument("--world-size", type=int, choices=(2,), required=True)
    parser.add_argument("--backend", choices=("gloo",), required=True)
    parser.add_argument("--init-method", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workload-profile", choices=("ci", "demo"), required=True)
    parser.add_argument("--checkpoint-step", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--temporary-checkpoint")
    parser.add_argument("--checkpoint")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    profile = get_profile(arguments.workload_profile)
    if arguments.checkpoint_step <= 0 or arguments.checkpoint_step >= profile.steps:
        raise ValueError("checkpoint step must be positive and precede the final step")
    sandbox = PathSandbox.create(arguments.run_root)
    dist.init_process_group(
        arguments.backend,
        init_method=arguments.init_method,
        rank=arguments.rank,
        world_size=arguments.world_size,
        timeout=timedelta(seconds=60),
    )
    try:
        runtime = create_distributed_runtime(
            profile=profile,
            rank=arguments.rank,
            world_size=arguments.world_size,
        )
        checkpoint_step = 0
        if arguments.mode == "control":
            if arguments.temporary_checkpoint or arguments.checkpoint:
                raise ValueError("control worker cannot receive checkpoint paths")
            train_distributed_until(runtime, profile.steps)
        elif arguments.mode == "checkpoint":
            if not arguments.temporary_checkpoint or arguments.checkpoint:
                raise ValueError("checkpoint worker requires only a temporary checkpoint path")
            temporary = sandbox.resolve_relative(arguments.temporary_checkpoint, must_exist=True)
            final_relative = f"checkpoints/checkpoint-step-{arguments.checkpoint_step:06d}"
            final = sandbox.resolve_relative(final_relative)
            train_distributed_until(runtime, arguments.checkpoint_step)
            save_distributed_runtime(
                runtime=runtime,
                run_root=sandbox.root,
                temporary_checkpoint_path=temporary,
                final_checkpoint_path=final,
                checkpoint_id=final.name,
            )
            checkpoint_step = arguments.checkpoint_step
        else:
            if arguments.temporary_checkpoint or not arguments.checkpoint:
                raise ValueError("recovery worker requires only a final checkpoint path")
            checkpoint = sandbox.resolve_relative(arguments.checkpoint, must_exist=True)
            validate_distributed_checkpoint(run_root=sandbox.root, checkpoint_path=checkpoint)
            checkpoint_step = load_distributed_runtime(
                runtime=runtime,
                run_root=sandbox.root,
                checkpoint_path=checkpoint,
            )
            if checkpoint_step != arguments.checkpoint_step:
                raise ValueError("loaded checkpoint step differs from the fixed qualification step")
            train_distributed_until(runtime, profile.steps)
        summary = summarize_distributed_runtime(
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
