from __future__ import annotations

import sys
from pathlib import Path

import pytest

from flashpilot.adapters.huggingface import HuggingFaceTrainerAdapter
from flashpilot.contracts.huggingface import huggingface_trainer_persistence_contract
from flashpilot.hf.models import HFCheckpointLifecycleEvidence


def test_hf_adapter_is_explicit_and_narrow() -> None:
    capabilities = HuggingFaceTrainerAdapter().capabilities()

    assert capabilities.adapter_name == "huggingface-trainer"
    assert capabilities.supported_profiles == ("exact-training-resume",)
    assert capabilities.supported_faults == ("process-kill",)
    assert capabilities.supported_scenarios == ("complete", "model-only")
    assert capabilities.callback_can_declare_verdict is False
    assert capabilities.arbitrary_script_compatibility is False


def test_hf_adapter_builds_argument_vector_without_shell_text(tmp_path: Path) -> None:
    adapter = HuggingFaceTrainerAdapter()
    command = adapter.worker_command(
        python_executable=sys.executable,
        script_path=tmp_path / "train.py",
        mode="control",
        run_root=tmp_path,
        scenario="complete",
        checkpoint_step=4,
        total_steps=8,
        seed=7,
        result_path="control/result.json",
        forwarded_arguments=("--trusted-option", "value with spaces"),
    )

    assert isinstance(command, tuple)
    assert command[0] == sys.executable
    assert command[-3:] == ("--", "--trusted-option", "value with spaces")


@pytest.mark.parametrize(
    "arguments",
    [
        ("--flashpilot-mode=control",),
        ("",),
        ("bad\x00value",),
        tuple(str(index) for index in range(33)),
    ],
)
def test_hf_adapter_rejects_unsafe_forwarded_arguments(arguments: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        HuggingFaceTrainerAdapter().validate_forwarded_arguments(arguments)


def test_hf_contract_requires_all_exact_trainer_state() -> None:
    contract = huggingface_trainer_persistence_contract()

    assert contract.framework == "transformers"
    assert contract.adapter == "huggingface-trainer"
    assert contract.max_rpo_steps == 0
    assert {item.state_id for item in contract.items} == {
        "batch_position",
        "global_step",
        "model",
        "numpy_rng",
        "optimizer",
        "python_rng",
        "scheduler",
        "torch_rng",
        "trainer_state",
    }
    assert all(item.requirement == "required" for item in contract.items)
    assert all(item.exactness == "exact" for item in contract.items)


def test_hf_callback_event_schema_cannot_carry_a_verdict() -> None:
    properties = HFCheckpointLifecycleEvidence.model_json_schema()["properties"]

    assert "verdict" not in properties
    assert "passed" not in properties
    assert "repair" not in properties
