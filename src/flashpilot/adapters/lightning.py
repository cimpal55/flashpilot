"""Explicit qualification adapter for the included PyTorch Lightning workload."""

from __future__ import annotations

import importlib.util
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import torch

from flashpilot.lightning.models import (
    LightningAdapterCapabilities,
    LightningScenario,
    LightningWorkerMode,
)

MAX_LIGHTNING_CHECKPOINT_BYTES = 64 * 1024 * 1024


class LightningDependencyError(RuntimeError):
    """The optional PyTorch Lightning dependency group is unavailable."""


def require_lightning_dependencies() -> str:
    if importlib.util.find_spec("lightning") is None:
        raise LightningDependencyError(
            "PyTorch Lightning qualification requires the optional dependency; "
            "install with `pip install 'flashpilot[lightning]'`"
        )
    try:
        return version("lightning")
    except PackageNotFoundError as error:
        raise LightningDependencyError(
            "Lightning dependency metadata is unavailable; reinstall `flashpilot[lightning]`"
        ) from error


class PyTorchLightningAdapter:
    """Narrow adapter for qualification only; it has no repair capability."""

    def capabilities(self) -> LightningAdapterCapabilities:
        return LightningAdapterCapabilities()

    def dependency_version(self) -> str:
        return require_lightning_dependencies()

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
        mode: LightningWorkerMode,
        run_root: Path,
        scenario: LightningScenario,
        checkpoint_step: int,
        total_steps: int,
        seed: int,
        result_path: str,
        checkpoint_path: str | None = None,
        forwarded_arguments: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        self.dependency_version()
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
        forwarded = self.validate_forwarded_arguments(forwarded_arguments)
        if forwarded:
            command.append("--")
            command.extend(forwarded)
        return tuple(command)

    def checkpoint_file(self, checkpoint_path: Path) -> Path:
        if not checkpoint_path.is_dir() or checkpoint_path.is_symlink():
            raise ValueError("Lightning checkpoint must be a non-symlink directory")
        files = []
        for candidate in checkpoint_path.rglob("*"):
            if candidate.is_symlink():
                raise ValueError("Lightning checkpoint refuses symbolic links")
            if candidate.is_file() and candidate.suffix == ".ckpt":
                files.append(candidate)
        if len(files) != 1:
            raise ValueError("Lightning checkpoint must contain exactly one .ckpt file")
        if files[0].stat().st_size > MAX_LIGHTNING_CHECKPOINT_BYTES:
            raise ValueError("Lightning checkpoint exceeds the supported size limit")
        return files[0]

    def checkpoint_payload(self, checkpoint_path: Path) -> dict[str, object]:
        checkpoint_file = self.checkpoint_file(checkpoint_path)
        try:
            payload = torch.load(checkpoint_file, map_location="cpu", weights_only=True)
        except (OSError, RuntimeError, ValueError, TypeError) as error:
            raise ValueError("Lightning checkpoint is not safely loadable") from error
        if not isinstance(payload, dict):
            raise ValueError("Lightning checkpoint payload must be a mapping")
        return payload

    def checkpoint_inventory(self, checkpoint_path: Path) -> tuple[str, ...]:
        payload = self.checkpoint_payload(checkpoint_path)
        return tuple(sorted(str(key) for key in payload))

    def training_state_presence(self, checkpoint_path: Path) -> dict[str, bool]:
        payload = self.checkpoint_payload(checkpoint_path)
        flashpilot_state = payload.get("flashpilot_exact_resume")
        bridge = flashpilot_state if isinstance(flashpilot_state, dict) else {}
        return {
            "model": isinstance(payload.get("state_dict"), dict),
            "loop_state": isinstance(payload.get("loops"), dict),
            "optimizer": bool(payload.get("optimizer_states")),
            "scheduler": bool(payload.get("lr_schedulers")),
            "rng": isinstance(bridge.get("rng"), dict),
            "loss_history": isinstance(bridge.get("loss_history"), list),
        }
