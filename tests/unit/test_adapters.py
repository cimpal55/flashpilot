import pytest
import torch

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.adapters.registry import get_adapter
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import build_model


def test_registry_exposes_only_native_pytorch() -> None:
    assert isinstance(get_adapter("native-pytorch"), NativePyTorchAdapter)

    with pytest.raises(ValueError, match="unsupported trainer adapter"):
        get_adapter("huggingface-peft")


def test_native_capabilities_describe_controlled_cpu_workload() -> None:
    capabilities = get_adapter("native-pytorch").capabilities()

    assert capabilities.framework == "native-pytorch"
    assert capabilities.has_frozen_base is True
    assert capabilities.has_trainable_adapter is True
    assert capabilities.uses_dropout is True
    assert capabilities.uses_torch_rng is True
    assert capabilities.uses_cuda_rng is False
    assert capabilities.supported_repair_actions == NATIVE_PYTORCH_REPAIR_ACTIONS


def test_save_restore_summaries_declare_exact_omissions() -> None:
    adapter = get_adapter("native-pytorch")
    safe = adapter.summarize_save_restore("safe_adapter_aware")
    incomplete = adapter.summarize_save_restore("missing_training_state")

    assert safe.omitted_state == ()
    assert safe.serialized_state == safe.restored_state
    assert incomplete.omitted_state == (
        "optimizer",
        "scheduler",
        "python_rng",
        "numpy_rng",
        "torch_rng",
    )
    assert "base artifact SHA-256" in safe.integrity_controls


def test_native_adapter_partitions_and_strictly_reassembles_model() -> None:
    adapter = get_adapter("native-pytorch")
    source = build_model(CI_PROFILE)
    restored = build_model(CI_PROFILE)
    base = adapter.frozen_base_state(source)
    trainable = adapter.trainable_adapter_state(source)

    assert base
    assert trainable
    assert all(not key.startswith("adapter.") for key in base)
    adapter.restore_partitioned_model(restored, frozen_base=base, adapter_state=trainable)

    for name, expected in source.state_dict().items():
        assert torch.equal(restored.state_dict()[name], expected)

    with pytest.raises(RuntimeError, match="keys do not match"):
        adapter.restore_partitioned_model(
            restored,
            frozen_base={key: value for key, value in base.items() if key != next(iter(base))},
            adapter_state=trainable,
        )
