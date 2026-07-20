from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import torch
from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.adapters import lightning as lightning_adapter_module
from flashpilot.adapters.lightning import (
    LightningDependencyError,
    PyTorchLightningAdapter,
)
from flashpilot.ci.exits import EXIT_UNSUPPORTED


def test_lightning_adapter_capabilities_are_explicit_and_non_repairing() -> None:
    capabilities = PyTorchLightningAdapter().capabilities()

    assert capabilities.adapter_name == "pytorch-lightning"
    assert capabilities.supported_profiles == ("exact-training-resume",)
    assert capabilities.supported_faults == ("process-kill",)
    assert capabilities.supported_scenarios == ("complete", "weights-only")
    assert capabilities.callback_can_declare_verdict is False
    assert capabilities.arbitrary_module_compatibility is False
    assert capabilities.repair_capability is False


def test_lightning_worker_command_is_an_argument_array(tmp_path: Path) -> None:
    command = PyTorchLightningAdapter().worker_command(
        python_executable="python",
        script_path=tmp_path / "train.py",
        mode="recover",
        run_root=tmp_path,
        scenario="complete",
        checkpoint_step=4,
        total_steps=8,
        seed=42,
        result_path="recovery/result.json",
        checkpoint_path="crash/checkpoints/checkpoint-4",
        forwarded_arguments=("--user-option", "safe value"),
    )

    assert isinstance(command, tuple)
    assert command[0] == "python"
    assert "--flashpilot-checkpoint-path" in command
    assert command[-3:] == ("--", "--user-option", "safe value")


def test_checkpoint_presence_uses_bounded_weights_only_loading(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint-4"
    checkpoint.mkdir()
    torch.save(
        {
            "state_dict": {"weight": torch.ones(2)},
            "loops": {"fit_loop": {}},
            "optimizer_states": [{"state": {}, "param_groups": []}],
            "lr_schedulers": [{"last_epoch": 4}],
            "flashpilot_exact_resume": {
                "loss_history": [1.0],
                "rng": {"python": [], "numpy": {}, "torch": torch.get_rng_state()},
            },
        },
        checkpoint / "state.ckpt",
    )

    adapter = PyTorchLightningAdapter()
    assert adapter.checkpoint_inventory(checkpoint) == (
        "flashpilot_exact_resume",
        "loops",
        "lr_schedulers",
        "optimizer_states",
        "state_dict",
    )
    assert all(adapter.training_state_presence(checkpoint).values())


def test_checkpoint_requires_exactly_one_non_symlink_ckpt(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint"
    checkpoint.mkdir()
    torch.save({}, checkpoint / "one.ckpt")
    torch.save({}, checkpoint / "two.ckpt")

    with pytest.raises(ValueError, match="exactly one"):
        PyTorchLightningAdapter().checkpoint_file(checkpoint)


def test_missing_lightning_extra_has_actionable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    actual_find_spec = importlib.util.find_spec

    def missing(name: str):
        return None if name == "lightning" else actual_find_spec(name)

    monkeypatch.setattr(lightning_adapter_module.importlib.util, "find_spec", missing)
    with pytest.raises(LightningDependencyError, match=r"flashpilot\[lightning\]"):
        lightning_adapter_module.require_lightning_dependencies()


def test_forwarded_flashpilot_control_argument_is_rejected() -> None:
    with pytest.raises(ValueError, match="cannot override"):
        PyTorchLightningAdapter().validate_forwarded_arguments(("--flashpilot-seed=1",))


def test_missing_lightning_extra_has_actionable_cli_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    message = (
        "PyTorch Lightning qualification requires the optional dependency; "
        "install with `pip install 'flashpilot[lightning]'`"
    )

    def missing() -> str:
        raise LightningDependencyError(message)

    monkeypatch.setattr(cli, "require_lightning_dependencies", missing)
    invocation = CliRunner().invoke(
        cli.app,
        ["qualify", "lightning", "--run-dir", str(tmp_path / "lightning")],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert message in invocation.output
    assert "OPENAI_API_KEY" not in invocation.output
