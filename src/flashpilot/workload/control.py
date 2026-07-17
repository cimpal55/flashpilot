"""Uninterrupted deterministic control-run implementation."""

from __future__ import annotations

import argparse
import platform
import random
import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn

from flashpilot.workload.data import synthetic_token_batch
from flashpilot.workload.model import TinyTransformerLanguageModel
from flashpilot.workload.profiles import WorkloadProfile, get_profile
from flashpilot.workload.state import (
    ControlRunSummary,
    EnvironmentSummary,
    OptimizerSummary,
    SchedulerSummary,
    state_digest,
    summarize_evaluation,
    summarize_trainable_state,
)


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


def run_control(
    profile_name: str = "ci",
    *,
    output_path: Path | None = None,
) -> ControlRunSummary:
    """Run training without interruption and return its observable reference state."""

    profile = get_profile(profile_name)
    configure_determinism(profile.global_seed)
    model = build_model(profile)
    optimizer = torch.optim.AdamW(model.trainable_parameters(), lr=profile.learning_rate)
    scheduler = torch.optim.lr_scheduler.LinearLR(
        optimizer,
        start_factor=1.0,
        end_factor=0.5,
        total_iters=profile.steps,
    )
    loss_function = nn.CrossEntropyLoss()
    loss_history: list[float] = []

    model.train()
    for global_step in range(profile.steps):
        batch = synthetic_token_batch(
            global_seed=profile.global_seed,
            global_step=global_step,
            batch_size=profile.batch_size,
            sequence_length=profile.sequence_length,
            vocabulary_size=profile.vocabulary_size,
        )
        optimizer.zero_grad(set_to_none=True)
        logits = model(batch.input_ids)
        loss = loss_function(
            logits.reshape(-1, profile.vocabulary_size), batch.target_ids.reshape(-1)
        )
        loss.backward()
        optimizer.step()
        scheduler.step()
        loss_history.append(float(loss.detach().item()))

    model.eval()
    evaluation_batch = synthetic_token_batch(
        global_seed=profile.global_seed,
        global_step=profile.steps,
        batch_size=profile.batch_size,
        sequence_length=profile.sequence_length,
        vocabulary_size=profile.vocabulary_size,
        evaluation=True,
    )
    with torch.no_grad():
        evaluation_logits = model(evaluation_batch.input_ids)

    summary = ControlRunSummary(
        schema_version="control-run-v1",
        profile=profile.name,
        seed=profile.global_seed,
        final_global_step=profile.steps,
        loss_history=tuple(loss_history),
        trainable_state=summarize_trainable_state(model),
        evaluation=summarize_evaluation(evaluation_logits),
        optimizer=OptimizerSummary(
            optimizer_type=type(optimizer).__name__,
            state_entries=len(optimizer.state),
            parameter_groups=len(optimizer.param_groups),
            sha256=state_digest(optimizer.state_dict()),
        ),
        scheduler=SchedulerSummary(
            scheduler_type=type(scheduler).__name__,
            last_epoch=scheduler.last_epoch,
            learning_rates=tuple(scheduler.get_last_lr()),
            sha256=state_digest(scheduler.state_dict()),
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
    if output_path is not None:
        summary.write_json(output_path)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the FlashPilot uninterrupted control workload."
    )
    parser.add_argument("--profile", choices=("ci", "demo"), default="ci")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    summary = run_control(arguments.profile, output_path=arguments.output)
    sys.stdout.write(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
