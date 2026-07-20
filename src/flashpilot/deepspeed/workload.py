"""Real two-rank CPU DeepSpeed ZeRO-2 workload and checkpoint restart."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import deepspeed
import numpy as np
import torch
import torch.distributed as dist
from pydantic import ValidationError
from torch import nn

from flashpilot.deepspeed.checkpoint import (
    DeepSpeedCheckpointError,
    DeepSpeedClientState,
    capture_rank_checkpoint_state,
    finalize_deepspeed_checkpoint,
    read_rank_checkpoint_state,
    restore_rank_rng_state,
    scheduler_state_matches,
    write_rank_checkpoint_state,
)
from flashpilot.deepspeed.models import DeepSpeedCheckpointEvent, DeepSpeedRankSummary
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.workload.data import synthetic_token_batch
from flashpilot.workload.profiles import WorkloadProfile
from flashpilot.workload.state import state_digest
from flashpilot.workload.trainer import build_model, configure_determinism


@dataclass(slots=True)
class DeepSpeedRuntime:
    profile: WorkloadProfile
    rank: int
    world_size: int
    engine: Any
    scheduler: torch.optim.lr_scheduler.LinearLR
    global_step: int = 0
    loss_history: list[float] = field(default_factory=list)
    checkpoint_saved: bool = False
    checkpoint_loaded: bool = False
    checkpoint_tag: str | None = None
    loaded_checkpoint_path: str | None = None
    client_state_valid: bool = False


def _rank_seed(global_seed: int, rank: int) -> int:
    return global_seed + (rank + 1) * 1_000_003


def create_deepspeed_runtime(
    *, profile: WorkloadProfile, rank: int, world_size: int
) -> DeepSpeedRuntime:
    if world_size != 2 or rank not in (0, 1):
        raise ValueError("the supported DeepSpeed workload requires exact ranks 0 and 1")
    if profile.batch_size % world_size:
        raise ValueError("profile batch size must divide evenly across DeepSpeed ranks")

    configure_determinism(profile.global_seed)
    model = build_model(profile)
    parameters = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    optimizer = torch.optim.AdamW(parameters, lr=profile.learning_rate)
    scheduler = torch.optim.lr_scheduler.LinearLR(
        optimizer,
        start_factor=1.0,
        end_factor=0.5,
        total_iters=profile.steps,
    )
    config = {
        "train_batch_size": profile.batch_size,
        "train_micro_batch_size_per_gpu": profile.batch_size // world_size,
        "gradient_accumulation_steps": 1,
        "zero_optimization": {"stage": 2},
        "steps_per_print": 1_000,
        "wall_clock_breakdown": False,
    }
    engine, _, _, returned_scheduler = deepspeed.initialize(
        model=model,
        model_parameters=parameters,
        optimizer=optimizer,
        lr_scheduler=scheduler,
        config=config,
        dist_init_required=False,
    )
    if engine.zero_optimization_stage() != 2:
        raise RuntimeError("DeepSpeed did not initialize ZeRO stage 2")
    if returned_scheduler is not scheduler or engine.lr_scheduler is not scheduler:
        raise RuntimeError("DeepSpeed did not retain the supplied deterministic scheduler")
    seed = _rank_seed(profile.global_seed, rank)
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    return DeepSpeedRuntime(
        profile=profile,
        rank=rank,
        world_size=world_size,
        engine=engine,
        scheduler=scheduler,
    )


def train_deepspeed_until(runtime: DeepSpeedRuntime, target_step: int) -> None:
    if target_step < runtime.global_step or target_step > runtime.profile.steps:
        raise ValueError("DeepSpeed target step is outside the workload bounds")
    profile = runtime.profile
    local_batch_size = profile.batch_size // runtime.world_size
    loss_function = nn.CrossEntropyLoss()
    runtime.engine.train()
    while runtime.global_step < target_step:
        batch = synthetic_token_batch(
            global_seed=_rank_seed(profile.global_seed, runtime.rank),
            global_step=runtime.global_step,
            batch_size=local_batch_size,
            sequence_length=profile.sequence_length,
            vocabulary_size=profile.vocabulary_size,
        )
        runtime.engine.zero_grad()
        logits = runtime.engine(batch.input_ids)
        loss = loss_function(
            logits.reshape(-1, profile.vocabulary_size), batch.target_ids.reshape(-1)
        )
        runtime.engine.backward(loss)
        runtime.engine.step()
        runtime.loss_history.append(float(loss.detach().item()))
        runtime.global_step += 1
        if runtime.engine.global_steps != runtime.global_step:
            raise RuntimeError("DeepSpeed and FlashPilot global steps diverged")


def _client_state(*, checkpoint_id: str, checkpoint_tag: str, global_step: int) -> dict[str, Any]:
    return {
        "flashpilot": DeepSpeedClientState(
            checkpoint_id=checkpoint_id,
            checkpoint_tag=checkpoint_tag,
            global_step=global_step,
        ).model_dump(mode="json")
    }


def save_deepspeed_runtime(
    *,
    runtime: DeepSpeedRuntime,
    run_root: Path,
    temporary_checkpoint_path: Path,
    final_checkpoint_path: Path,
    checkpoint_id: str,
    checkpoint_tag: str,
) -> DeepSpeedCheckpointEvent | None:
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
    saved = runtime.engine.save_checkpoint(
        str(temporary_checkpoint_path),
        tag=checkpoint_tag,
        client_state=_client_state(
            checkpoint_id=checkpoint_id,
            checkpoint_tag=checkpoint_tag,
            global_step=runtime.global_step,
        ),
        save_latest=True,
    )
    if not saved:
        raise RuntimeError("DeepSpeed save_checkpoint did not confirm success")
    runtime.checkpoint_saved = True
    runtime.checkpoint_tag = checkpoint_tag
    runtime.client_state_valid = True
    dist.barrier()
    event: DeepSpeedCheckpointEvent | None = None
    if runtime.rank == 0:
        event = finalize_deepspeed_checkpoint(
            run_root=run_root,
            temporary_checkpoint_path=temporary_checkpoint_path,
            final_checkpoint_path=final_checkpoint_path,
            checkpoint_id=checkpoint_id,
            checkpoint_tag=checkpoint_tag,
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


def load_deepspeed_runtime(
    *,
    runtime: DeepSpeedRuntime,
    run_root: Path,
    checkpoint_path: Path,
    checkpoint_id: str,
    checkpoint_tag: str,
) -> int:
    loaded_path, raw_client_state = runtime.engine.load_checkpoint(
        str(checkpoint_path),
        tag=checkpoint_tag,
        load_module_strict=True,
        load_optimizer_states=True,
        load_lr_scheduler_states=True,
    )
    if loaded_path is None:
        raise DeepSpeedCheckpointError("DeepSpeed load_checkpoint returned no checkpoint path")
    expected_loaded_path = (
        checkpoint_path / checkpoint_tag / "mp_rank_00_model_states.pt"
    ).resolve()
    if Path(loaded_path).resolve() != expected_loaded_path:
        raise DeepSpeedCheckpointError("DeepSpeed loaded path differs from the validated tag")
    rank_state = read_rank_checkpoint_state(
        run_root=run_root,
        checkpoint_path=checkpoint_path,
        rank=runtime.rank,
    )
    allowed_deepspeed_client_keys = {
        "buffer_names",
        "ds_config",
        "ds_version",
        "flashpilot",
        "frozen_param_fragments",
        "frozen_param_shapes",
        "global_samples",
        "optimizer",
        "param_shapes",
        "shared_params",
    }
    if not isinstance(raw_client_state, dict) or not set(raw_client_state).issubset(
        allowed_deepspeed_client_keys
    ):
        raise DeepSpeedCheckpointError("DeepSpeed returned unknown client-state fields")
    try:
        client_state = DeepSpeedClientState.model_validate(raw_client_state["flashpilot"])
    except (KeyError, ValidationError) as error:
        raise DeepSpeedCheckpointError("FlashPilot DeepSpeed client state is malformed") from error
    expected_client_state = DeepSpeedClientState(
        checkpoint_id=checkpoint_id,
        checkpoint_tag=checkpoint_tag,
        global_step=rank_state.global_step,
    )
    if client_state != expected_client_state:
        raise DeepSpeedCheckpointError("DeepSpeed client state identity mismatch")
    if runtime.engine.global_steps != rank_state.global_step:
        raise DeepSpeedCheckpointError("DeepSpeed engine progress was not restored")
    if not scheduler_state_matches(runtime.scheduler, rank_state):
        raise DeepSpeedCheckpointError("DeepSpeed scheduler state was not restored")
    restore_rank_rng_state(rank_state)
    runtime.global_step = rank_state.global_step
    runtime.loss_history = list(rank_state.loss_history)
    runtime.checkpoint_loaded = True
    runtime.checkpoint_tag = checkpoint_tag
    runtime.loaded_checkpoint_path = (
        f"checkpoints/{checkpoint_id}/{checkpoint_tag}/mp_rank_00_model_states.pt"
    )
    runtime.client_state_valid = True
    dist.barrier()
    return rank_state.global_step


def _broadcast_rank_zero(value: str, rank: int) -> str:
    values = [value if rank == 0 else ""]
    dist.broadcast_object_list(values, src=0)
    return values[0]


def _optimizer_state(runtime: DeepSpeedRuntime) -> dict[str, Any]:
    optimizer = getattr(runtime.engine.optimizer, "optimizer", None)
    if optimizer is None:
        raise RuntimeError("DeepSpeed ZeRO optimizer lacks its wrapped optimizer state")
    return optimizer.state_dict()


def summarize_deepspeed_runtime(
    *, runtime: DeepSpeedRuntime, phase: str, checkpoint_step: int
) -> DeepSpeedRankSummary:
    trainable_state = {
        key: value
        for key, value in runtime.engine.module.state_dict().items()
        if key.startswith("adapter.") or ".adapter." in key
    }
    if not trainable_state:
        raise RuntimeError("DeepSpeed module lacks trainable adapter parameters")
    trainable_digest = state_digest(trainable_state)
    optimizer_digest = state_digest(_optimizer_state(runtime))

    runtime.engine.eval()
    batch = synthetic_token_batch(
        global_seed=runtime.profile.global_seed,
        global_step=runtime.profile.steps,
        batch_size=runtime.profile.batch_size // runtime.world_size,
        sequence_length=runtime.profile.sequence_length,
        vocabulary_size=runtime.profile.vocabulary_size,
        evaluation=True,
    )
    with torch.no_grad():
        evaluation = runtime.engine(batch.input_ids)
    evaluation_digest = state_digest(evaluation)

    local_probe = torch.tensor([runtime.loss_history[-1]], dtype=torch.float64)
    gathered = [torch.zeros_like(local_probe) for _ in range(runtime.world_size)]
    dist.all_gather(gathered, local_probe)
    collective_digest = state_digest(tuple(float(item.item()) for item in gathered))
    return DeepSpeedRankSummary(
        phase=phase,
        rank=runtime.rank,
        worker_pid=os.getpid(),
        final_global_step=runtime.global_step,
        checkpoint_step=checkpoint_step,
        checkpoint_tag=runtime.checkpoint_tag,
        checkpoint_saved=runtime.checkpoint_saved,
        checkpoint_loaded=runtime.checkpoint_loaded,
        loaded_checkpoint_path=runtime.loaded_checkpoint_path,
        client_state_valid=runtime.client_state_valid,
        loss_history=tuple(runtime.loss_history),
        trainable_state_sha256=_broadcast_rank_zero(trainable_digest, runtime.rank),
        evaluation_sha256=evaluation_digest,
        optimizer_sha256=optimizer_digest,
        scheduler_sha256=state_digest(runtime.scheduler.state_dict()),
        collective_probe_sha256=collective_digest,
        torch_version=torch.__version__,
        deepspeed_version=deepspeed.__version__,
    )
