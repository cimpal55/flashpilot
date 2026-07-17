import torch

from flashpilot.workload.control import build_model, configure_determinism
from flashpilot.workload.data import synthetic_token_batch
from flashpilot.workload.model import count_parameters
from flashpilot.workload.profiles import CI_PROFILE


def test_only_residual_adapter_is_trainable() -> None:
    configure_determinism(CI_PROFILE.global_seed)
    model = build_model(CI_PROFILE)

    trainable_names = {name for name, value in model.named_parameters() if value.requires_grad}

    assert trainable_names
    assert all(name.startswith("adapter.") for name in trainable_names)
    assert count_parameters(model.trainable_parameters()) > 0
    assert count_parameters(model.frozen_parameters()) > count_parameters(
        model.trainable_parameters()
    )


def test_dropout_is_stochastic_during_training_and_disabled_for_evaluation() -> None:
    configure_determinism(CI_PROFILE.global_seed)
    model = build_model(CI_PROFILE)
    batch = synthetic_token_batch(
        global_seed=CI_PROFILE.global_seed,
        global_step=0,
        batch_size=CI_PROFILE.batch_size,
        sequence_length=CI_PROFILE.sequence_length,
        vocabulary_size=CI_PROFILE.vocabulary_size,
    )

    model.train()
    first_training_logits = model(batch.input_ids)
    second_training_logits = model(batch.input_ids)
    model.eval()
    first_evaluation_logits = model(batch.input_ids)
    second_evaluation_logits = model(batch.input_ids)

    assert not torch.equal(first_training_logits, second_training_logits)
    assert torch.equal(first_evaluation_logits, second_evaluation_logits)
