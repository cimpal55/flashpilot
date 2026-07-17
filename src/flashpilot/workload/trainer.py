"""Reusable deterministic training primitives for control and direct restore."""

from __future__ import annotations

import platform
import random
from dataclasses import dataclass, field

import numpy as np
import torch
from torch import nn

from flashpilot.workload.data import synthetic_token_batch
from flashpilot.workload.model import TinyTransformerLanguageModel
from flashpilot.workload.profiles import WorkloadProfile
from flashpilot.workload.state import (
    ControlRunSummary,
    EnvironmentSummary,
    OptimizerSummary,
    SchedulerSummary,
    state_digest,
    summarize_evaluation,
    summarize_trainable_state,
)


@dataclass(slots=True)
class TrainingRuntime:
    """Mutable training state that can be checkpointed and resumed."""

    profile: WorkloadProfile
    model: TinyTransformerLanguageModel
    optimizer: torch.optim.Optimizer
    scheduler: torch.optim.lr_scheduler.LRScheduler
    global_step: int = 0
    loss_history: list[float] = field(default_factory=list)


def configure_determinism(seed: int) -> None:
    """Reset supported RNGs and deterministic CPU execution settings."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def build_model(profile: WorkloadProfile) -> TinyTransformerLanguageModel:
    return TinyTransformerLanguageModel(
        vocabulary_size=profile.vocabulary_size,
        sequence_length=profile.sequence_length,
        model_width=profile.model_width,
        attention_heads=profile.attention_heads,
        transformer_layers=profile.transformer_layers,
        adapter_width=profile.adapter_width,
        dropout=profile.dropout,
    ).cpu()


def create_training_runtime(profile: WorkloadProfile) -> TrainingRuntime:
    configure_determinism(profile.global_seed)
    model = build_model(profile)
    optimizer = torch.optim.AdamW(model.trainable_parameters(), lr=profile.learning_rate)
    scheduler = torch.optim.lr_scheduler.LinearLR(
        optimizer,
        start_factor=1.0,
        end_factor=0.5,
        total_iters=profile.steps,
    )
    return TrainingRuntime(
        profile=profile,
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
    )


def train_until(runtime: TrainingRuntime, target_step: int) -> None:
    """Advance a runtime to an inclusive count of completed training steps."""

    if target_step < runtime.global_step:
        raise ValueError("target_step cannot precede the current global step")
    if target_step > runtime.profile.steps:
        raise ValueError("target_step cannot exceed the profile's final step")

    profile = runtime.profile
    loss_function = nn.CrossEntropyLoss()
    runtime.model.train()
    while runtime.global_step < target_step:
        batch = synthetic_token_batch(
            global_seed=profile.global_seed,
            global_step=runtime.global_step,
            batch_size=profile.batch_size,
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


def summarize_runtime(runtime: TrainingRuntime) -> ControlRunSummary:
    """Create the same observable summary used by the uninterrupted control."""

    profile = runtime.profile
    runtime.model.eval()
    evaluation_batch = synthetic_token_batch(
        global_seed=profile.global_seed,
        global_step=profile.steps,
        batch_size=profile.batch_size,
        sequence_length=profile.sequence_length,
        vocabulary_size=profile.vocabulary_size,
        evaluation=True,
    )
    with torch.no_grad():
        evaluation_logits = runtime.model(evaluation_batch.input_ids)

    return ControlRunSummary(
        schema_version="control-run-v1",
        profile=profile.name,
        seed=profile.global_seed,
        final_global_step=runtime.global_step,
        loss_history=tuple(runtime.loss_history),
        trainable_state=summarize_trainable_state(runtime.model),
        evaluation=summarize_evaluation(evaluation_logits),
        optimizer=OptimizerSummary(
            optimizer_type=type(runtime.optimizer).__name__,
            state_entries=len(runtime.optimizer.state),
            parameter_groups=len(runtime.optimizer.param_groups),
            sha256=state_digest(runtime.optimizer.state_dict()),
        ),
        scheduler=SchedulerSummary(
            scheduler_type=type(runtime.scheduler).__name__,
            last_epoch=runtime.scheduler.last_epoch,
            learning_rates=tuple(runtime.scheduler.get_last_lr()),
            sha256=state_digest(runtime.scheduler.state_dict()),
        ),
        environment=EnvironmentSummary(
            python_version=platform.python_version(),
            torch_version=torch.__version__,
            numpy_version=np.__version__,
            platform=platform.platform(),
            device="cpu",
            dtype="float32",
            deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
            torch_threads=torch.get_num_threads(),
        ),
    )
