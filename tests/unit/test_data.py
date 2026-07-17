import pytest
import torch

from flashpilot.workload.data import synthetic_token_batch


def test_synthetic_batch_is_reproducible_and_step_derived() -> None:
    arguments = {
        "global_seed": 42,
        "batch_size": 2,
        "sequence_length": 4,
        "vocabulary_size": 16,
    }

    first = synthetic_token_batch(global_step=3, **arguments)
    repeated = synthetic_token_batch(global_step=3, **arguments)
    next_step = synthetic_token_batch(global_step=4, **arguments)

    assert torch.equal(first.input_ids, repeated.input_ids)
    assert torch.equal(first.target_ids, repeated.target_ids)
    assert not torch.equal(first.input_ids, next_step.input_ids)


@pytest.mark.parametrize("field", ["global_seed", "global_step"])
def test_synthetic_batch_rejects_negative_seed_inputs(field: str) -> None:
    arguments = {
        "global_seed": 1,
        "global_step": 1,
        "batch_size": 2,
        "sequence_length": 4,
        "vocabulary_size": 16,
    }
    arguments[field] = -1

    with pytest.raises(ValueError):
        synthetic_token_batch(**arguments)
