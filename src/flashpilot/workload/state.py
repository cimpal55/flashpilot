"""JSON-safe summaries and deterministic state digests for control runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
from torch import Tensor


def _update_digest(digest: Any, value: Any) -> None:
    if isinstance(value, Tensor):
        tensor = value.detach().cpu().contiguous()
        digest.update(b"tensor:")
        digest.update(str(tensor.dtype).encode())
        digest.update(json.dumps(list(tensor.shape)).encode())
        digest.update(tensor.numpy().tobytes())
        return
    if isinstance(value, dict):
        digest.update(b"dict:")
        for key in sorted(value, key=lambda item: repr(item)):
            _update_digest(digest, key)
            _update_digest(digest, value[key])
        return
    if isinstance(value, (list, tuple)):
        digest.update(b"sequence:")
        for item in value:
            _update_digest(digest, item)
        return
    digest.update(json.dumps(value, sort_keys=True, default=str).encode())


def state_digest(value: Any) -> str:
    """Hash nested scalar, collection, and tensor state deterministically."""

    digest = hashlib.sha256()
    _update_digest(digest, value)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class TrainableStateSummary:
    parameter_count: int
    tensor_count: int
    sha256: str


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    batch_size: int
    sequence_length: int
    vocabulary_size: int
    dtype: str
    minimum: float
    maximum: float
    mean: float
    sha256: str


@dataclass(frozen=True, slots=True)
class OptimizerSummary:
    optimizer_type: str
    state_entries: int
    parameter_groups: int
    sha256: str


@dataclass(frozen=True, slots=True)
class SchedulerSummary:
    scheduler_type: str
    last_epoch: int
    learning_rates: tuple[float, ...]
    sha256: str


@dataclass(frozen=True, slots=True)
class EnvironmentSummary:
    python_version: str
    torch_version: str
    numpy_version: str
    platform: str
    device: str
    dtype: str
    deterministic_algorithms: bool
    torch_threads: int


@dataclass(frozen=True, slots=True)
class ControlRunSummary:
    schema_version: str
    profile: str
    seed: int
    final_global_step: int
    loss_history: tuple[float, ...]
    trainable_state: TrainableStateSummary
    evaluation: EvaluationSummary
    optimizer: OptimizerSummary
    scheduler: SchedulerSummary
    environment: EnvironmentSummary

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def write_json(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_json(), encoding="utf-8")


def summarize_trainable_state(model: torch.nn.Module) -> TrainableStateSummary:
    state = {
        name: parameter.detach()
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    }
    return TrainableStateSummary(
        parameter_count=sum(parameter.numel() for parameter in state.values()),
        tensor_count=len(state),
        sha256=state_digest(state),
    )


def summarize_evaluation(logits: Tensor) -> EvaluationSummary:
    batch_size, sequence_length, vocabulary_size = logits.shape
    return EvaluationSummary(
        batch_size=batch_size,
        sequence_length=sequence_length,
        vocabulary_size=vocabulary_size,
        dtype=str(logits.dtype),
        minimum=float(logits.min().item()),
        maximum=float(logits.max().item()),
        mean=float(logits.mean().item()),
        sha256=state_digest(logits),
    )
