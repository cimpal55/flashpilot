"""Synthetic, step-derived language-model training data."""

from dataclasses import dataclass

import torch
from torch import Tensor

_MAX_GENERATOR_SEED = 2**63 - 1
_TRAIN_STREAM = 0x545241494E
_EVALUATION_STREAM = 0x4556414C


@dataclass(frozen=True, slots=True)
class SyntheticBatch:
    """One deterministic next-token-prediction batch."""

    input_ids: Tensor
    target_ids: Tensor


def _step_seed(global_seed: int, global_step: int, *, evaluation: bool) -> int:
    if global_seed < 0:
        raise ValueError("global_seed must be non-negative")
    if global_step < 0:
        raise ValueError("global_step must be non-negative")

    stream = _EVALUATION_STREAM if evaluation else _TRAIN_STREAM
    return (global_seed * 1_000_003 + global_step * 9_176 + stream) % _MAX_GENERATOR_SEED


def synthetic_token_batch(
    *,
    global_seed: int,
    global_step: int,
    batch_size: int,
    sequence_length: int,
    vocabulary_size: int,
    evaluation: bool = False,
) -> SyntheticBatch:
    """Build a batch from only the seed, step, stream, and tensor dimensions."""

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if sequence_length <= 0:
        raise ValueError("sequence_length must be positive")
    if vocabulary_size < 2:
        raise ValueError("vocabulary_size must be at least two")

    generator = torch.Generator(device="cpu")
    generator.manual_seed(_step_seed(global_seed, global_step, evaluation=evaluation))
    tokens = torch.randint(
        low=0,
        high=vocabulary_size,
        size=(batch_size, sequence_length + 1),
        generator=generator,
        dtype=torch.long,
        device="cpu",
    )
    return SyntheticBatch(input_ids=tokens[:, :-1], target_ids=tokens[:, 1:])
