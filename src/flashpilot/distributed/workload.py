"""Real two-rank FSDP2 workload and distributed-checkpoint restore."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
import torch.distributed as dist
import torch.distributed.checkpoint as dcp
from torch import nn
from torch.distributed.checkpoint.state_dict import (
    StateDictOptions,
    get_state_dict,
    set_state_dict,
)
from torch.distributed.device_mesh import init_device_mesh
from torch.distributed.fsdp import fully_shard

from flashpilot.distributed.checkpoint import (
    capture_rank_checkpoint_state,
    finalize_distributed_checkpoint,
    read_rank_checkpoint_state,
    restore_rank_checkpoint_state,
    write_rank_checkpoint_state,
)
from flashpilot.distributed.models import DistributedCheckpointEvent, DistributedRankSummary
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.workload.data import synthetic_token_batch
from flashpilot.workload.model import TinyTransformerLanguageModel
from flashpilot.workload.profiles import WorkloadProfile
from flashpilot.workload.state import state_digest
from flashpilot.workload.trainer import build_model, configure_determinism


@dataclass(slots=True)
class DistributedRuntime:
    profile: WorkloadProfile
    rank: int
    world_size: int
    model: nn.Module
    optimizer: torch.optim.Optimizer
    scheduler: torch.optim.lr_scheduler.LinearLR
    global_step: int = 0
    loss_history: list[float] = field(default_factory=list)


def _rank_seed(global_seed: int, rank: int) -> int:
    return global_seed + (rank + 1) * 1_000_003


def create_distributed_runtime(
    *, profile: WorkloadProfile, rank: int, world_size: int
) -> DistributedRuntime:
    if world_size != 2 or rank not in (0, 1):
        raise ValueError("the supported distributed workload requires exact ranks 0 and 1")
    if profile.batch_size % world_size:
        raise ValueError("profile batch size must divide evenly across distributed ranks")

    configure_determinism(profile.global_seed)
    model: TinyTransformerLanguageModel = build_model(profile)
    mesh = init_device_mesh("cpu", (world_size,))
    fully_shard(model, mesh=mesh)
    optimizer = torch.optim.AdamW(
        (parameter for parameter in model.parameters() if parameter.requires_grad),
        lr=profile.learning_rate,
    )
    scheduler = torch.optim.lr_scheduler.LinearLR(
        optimizer,
        start_factor=1.0,
        end_factor=0.5,
        total_iters=profile.steps,
    )
    seed = _rank_seed(profile.global_seed, rank)
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    return DistributedRuntime(
        profile=profile,
        rank=rank,
        world_size=world_size,
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
    )


def train_distributed_until(runtime: DistributedRuntime, target_step: int) -> None:
    if target_step < runtime.global_step or target_step > runtime.profile.steps:
        raise ValueError("distributed target step is outside the workload bounds")
    profile = runtime.profile
    local_batch_size = profile.batch_size // runtime.world_size
    loss_function = nn.CrossEntropyLoss()
    runtime.model.train()
    while runtime.global_step < target_step:
        batch = synthetic_token_batch(
            global_seed=_rank_seed(profile.global_seed, runtime.rank),
            global_step=runtime.global_step,
            batch_size=local_batch_size,
            sequence_length=profile.sequence_length,
            vocabulary_size=profile.vocabulary_size,
        )
        runtime.optimizer.zero_grad(set_to_none=True)
        logits = runtime.model(batch.input_ids)
        loss = loss_function(
            logits.reshape(-1, profile.vocabulary_size), batch.target_ids.reshape(-1)
        )
        loss.backward()
        runtime.optimizer.step()
        runtime.scheduler.step()
        runtime.loss_history.append(float(loss.detach().item()))
        runtime.global_step += 1


def save_distributed_runtime(
    *,
    runtime: DistributedRuntime,
    run_root: Path,
    temporary_checkpoint_path: Path,
    final_checkpoint_path: Path,
    checkpoint_id: str,
) -> DistributedCheckpointEvent | None:
    save_started_at = time.perf_counter()
    rank_state = capture_rank_checkpoint_state(
        rank=runtime.rank,
        global_step=runtime.global_step,
        loss_history=tuple(runtime.loss_history),
        scheduler=runtime.scheduler,
    )
    write_rank_checkpoint_state(
        temporary_checkpoint_path / f"rank-state-{runtime.rank:03d}.json",
        rank_state,
    )
    model_state, optimizer_state = get_state_dict(runtime.model, runtime.optimizer)
    dcp.save(
        {"model": model_state, "optimizer": optimizer_state},
        checkpoint_id=temporary_checkpoint_path / "dcp",
    )
    dist.barrier()
    event: DistributedCheckpointEvent | None = None
    if runtime.rank == 0:
        event = finalize_distributed_checkpoint(
            run_root=run_root,
            temporary_checkpoint_path=temporary_checkpoint_path,
            final_checkpoint_path=final_checkpoint_path,
            checkpoint_id=checkpoint_id,
            global_step=runtime.global_step,
            writer_pid=os.getpid(),
            save_started_at=save_started_at,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="checkpoint-event.json",
            value=event,
        )
    dist.barrier()
    return event


def load_distributed_runtime(
    *, runtime: DistributedRuntime, run_root: Path, checkpoint_path: Path
) -> int:
    model_state, optimizer_state = get_state_dict(runtime.model, runtime.optimizer)
    dcp.load(
        {"model": model_state, "optimizer": optimizer_state},
        checkpoint_id=checkpoint_path / "dcp",
    )
    incompatible = set_state_dict(
        runtime.model,
        runtime.optimizer,
        model_state_dict=model_state,
        optim_state_dict=optimizer_state,
    )
    if incompatible.missing_keys or incompatible.unexpected_keys:
        raise RuntimeError("distributed checkpoint load returned incompatible model keys")
    rank_state = read_rank_checkpoint_state(
        run_root=run_root,
        checkpoint_path=checkpoint_path,
        rank=runtime.rank,
    )
    restore_rank_checkpoint_state(state=rank_state, scheduler=runtime.scheduler)
    runtime.global_step = rank_state.global_step
    runtime.loss_history = list(rank_state.loss_history)
    dist.barrier()
    return rank_state.global_step


def _broadcast_rank_zero(value: str, rank: int) -> str:
    values = [value if rank == 0 else ""]
    dist.broadcast_object_list(values, src=0)
    return values[0]


def summarize_distributed_runtime(
    *, runtime: DistributedRuntime, phase: str, checkpoint_step: int
) -> DistributedRankSummary:
    options = StateDictOptions(full_state_dict=True, cpu_offload=True)
    model_state, optimizer_state = get_state_dict(
        runtime.model,
        runtime.optimizer,
        options=options,
    )
    if runtime.rank == 0:
        trainable_state = {
            key: value
            for key, value in model_state.items()
            if key.startswith("adapter.") or ".adapter." in key
        }
        if not trainable_state:
            raise RuntimeError("distributed full state lacks trainable adapter parameters")
        trainable_digest = state_digest(trainable_state)
        optimizer_digest = state_digest(optimizer_state)
    else:
        trainable_digest = ""
        optimizer_digest = ""
    trainable_digest = _broadcast_rank_zero(trainable_digest, runtime.rank)
    optimizer_digest = _broadcast_rank_zero(optimizer_digest, runtime.rank)

    runtime.model.eval()
    batch = synthetic_token_batch(
        global_seed=runtime.profile.global_seed,
        global_step=runtime.profile.steps,
        batch_size=runtime.profile.batch_size // runtime.world_size,
        sequence_length=runtime.profile.sequence_length,
        vocabulary_size=runtime.profile.vocabulary_size,
        evaluation=True,
    )
    with torch.no_grad():
        evaluation = runtime.model(batch.input_ids)
    evaluation_digest = state_digest(evaluation)

    local_probe = torch.tensor([runtime.loss_history[-1]], dtype=torch.float64)
    gathered = [torch.zeros_like(local_probe) for _ in range(runtime.world_size)]
    dist.all_gather(gathered, local_probe)
    collective_digest = state_digest(tuple(float(item.item()) for item in gathered))
    return DistributedRankSummary(
        phase=phase,
        rank=runtime.rank,
        worker_pid=os.getpid(),
        final_global_step=runtime.global_step,
        checkpoint_step=checkpoint_step,
        checkpoint_loaded=phase == "recovery",
        loss_history=tuple(runtime.loss_history),
        trainable_state_sha256=trainable_digest,
        evaluation_sha256=evaluation_digest,
        optimizer_sha256=optimizer_digest,
        scheduler_sha256=state_digest(runtime.scheduler.state_dict()),
        collective_probe_sha256=collective_digest,
        torch_version=torch.__version__,
    )
