"""Narrow VNext adapter contract for the included Hugging Face Trainer example."""

from __future__ import annotations

import importlib.util
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from flashpilot.hf.models import HFAdapterCapabilities, HFScenario, HFWorkerMode


class HuggingFaceDependencyError(RuntimeError):
    """The optional Hugging Face dependency group is unavailable."""


def require_huggingface_dependencies() -> tuple[str, str]:
    missing = [
        name
        for name in ("accelerate", "safetensors", "transformers")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        raise HuggingFaceDependencyError(
            "Hugging Face qualification requires the optional dependencies; "
            "install with `pip install 'flashpilot[hf]'`"
        )
    try:
        return version("transformers"), version("accelerate")
    except PackageNotFoundError as error:
        raise HuggingFaceDependencyError(
            "Hugging Face dependency metadata is unavailable; reinstall `flashpilot[hf]`"
        ) from error


class HuggingFaceTrainerAdapter:
    """Explicit adapter for one documented local Trainer script contract."""

    def capabilities(self) -> HFAdapterCapabilities:
        return HFAdapterCapabilities()

    def dependency_versions(self) -> tuple[str, str]:
        return require_huggingface_dependencies()

    def validate_forwarded_arguments(self, arguments: tuple[str, ...]) -> tuple[str, ...]:
        if len(arguments) > 32:
            raise ValueError("at most 32 trusted forwarded arguments are supported")
        for argument in arguments:
            if not argument or "\x00" in argument or len(argument) > 1_000:
                raise ValueError("forwarded arguments must be bounded nonempty strings")
            if argument.startswith("--flashpilot-"):
                raise ValueError("forwarded arguments cannot override FlashPilot control fields")
        return arguments

    def worker_command(
        self,
        *,
        python_executable: str,
        script_path: Path,
        mode: HFWorkerMode,
        run_root: Path,
        scenario: HFScenario,
        checkpoint_step: int,
        total_steps: int,
        seed: int,
        result_path: str,
        checkpoint_path: str | None = None,
        grace_period_seconds: int | None = None,
        forwarded_arguments: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        self.dependency_versions()
        forwarded = self.validate_forwarded_arguments(forwarded_arguments)
        command = [
            python_executable,
            str(script_path),
            "--flashpilot-mode",
            mode,
            "--flashpilot-run-root",
            str(run_root),
            "--flashpilot-scenario",
            scenario,
            "--flashpilot-checkpoint-step",
            str(checkpoint_step),
            "--flashpilot-total-steps",
            str(total_steps),
            "--flashpilot-seed",
            str(seed),
            "--flashpilot-result-path",
            result_path,
        ]
        if checkpoint_path is not None:
            command.extend(("--flashpilot-checkpoint-path", checkpoint_path))
        if grace_period_seconds is not None:
            command.extend(("--flashpilot-grace-period-seconds", str(grace_period_seconds)))
        if forwarded:
            command.append("--")
            command.extend(forwarded)
        return tuple(command)

    def checkpoint_inventory(self, checkpoint_path: Path) -> tuple[str, ...]:
        if not checkpoint_path.is_dir() or checkpoint_path.is_symlink():
            raise ValueError("HF checkpoint must be a non-symlink directory")
        inventory = []
        for path in sorted(
            checkpoint_path.rglob("*"),
            key=lambda candidate: candidate.relative_to(checkpoint_path).as_posix(),
        ):
            if path.is_symlink():
                raise ValueError("HF checkpoint inventory refuses symbolic links")
            if path.is_file():
                inventory.append(path.relative_to(checkpoint_path).as_posix())
        if not inventory:
            raise ValueError("HF checkpoint is empty")
        return tuple(inventory)

    def training_state_presence(self, checkpoint_path: Path) -> dict[str, bool]:
        inventory = set(self.checkpoint_inventory(checkpoint_path))
        return {
            "model": bool(
                inventory
                & {
                    "adapter_model.safetensors",
                    "model.safetensors",
                    "pytorch_model.bin",
                }
            ),
            "trainer_state": "trainer_state.json" in inventory,
            "optimizer": "optimizer.pt" in inventory,
            "scheduler": "scheduler.pt" in inventory,
            "rng": any(
                name == "rng_state.pth" or name.startswith("rng_state_") for name in inventory
            ),
        }
