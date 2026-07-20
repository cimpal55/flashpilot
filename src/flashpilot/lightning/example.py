"""Tiny deterministic CPU Lightning workload with real dropout."""

from __future__ import annotations

import os
import random
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import lightning
import numpy as np
import torch
from lightning.pytorch import LightningModule, Trainer, seed_everything
from torch import nn
from torch.nn import functional as functional
from torch.utils.data import DataLoader, TensorDataset

from flashpilot.lightning.models import LightningRunSummary, LightningScenario
from flashpilot.workload.state import state_digest

LIGHTNING_INPUT_WIDTH = 8
LIGHTNING_HIDDEN_WIDTH = 16
LIGHTNING_BATCH_SIZE = 4
LIGHTNING_TOTAL_STEPS = 8
LIGHTNING_CHECKPOINT_STEP = 4
LIGHTNING_SEED = 20260720


def _python_rng_state() -> list[object]:
    version, values, gaussian = random.getstate()
    return [version, list(values), gaussian]


def _numpy_rng_state() -> dict[str, object]:
    algorithm, values, position, has_gaussian, cached_gaussian = np.random.get_state()
    return {
        "algorithm": algorithm,
        "values": values.tolist(),
        "position": position,
        "has_gaussian": has_gaussian,
        "cached_gaussian": cached_gaussian,
    }


def _restore_rng_state(state: dict[str, object]) -> None:
    python_state = state["python"]
    numpy_state = state["numpy"]
    if not isinstance(python_state, list) or not isinstance(numpy_state, dict):
        raise RuntimeError("Lightning checkpoint RNG bridge is malformed")
    random.setstate((int(python_state[0]), tuple(python_state[1]), python_state[2]))
    np.random.set_state(
        (
            str(numpy_state["algorithm"]),
            np.asarray(numpy_state["values"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gaussian"]),
            float(numpy_state["cached_gaussian"]),
        )
    )
    torch.set_rng_state(state["torch"])


class FlashPilotLightningModule(LightningModule):
    """Small module whose exact trajectory depends on optimizer, scheduler, and RNG."""

    def __init__(
        self,
        *,
        seed: int,
        scenario: LightningScenario,
        semantic_offset: int = 0,
    ) -> None:
        super().__init__()
        self.save_hyperparameters()
        self.seed = seed
        self.scenario = scenario
        self.semantic_offset = semantic_offset
        self.loss_history: list[float] = []
        self._pending_rng_state: dict[str, object] | None = None
        self.network = nn.Sequential(
            nn.Linear(LIGHTNING_INPUT_WIDTH, LIGHTNING_HIDDEN_WIDTH),
            nn.Tanh(),
            nn.Dropout(0.25),
            nn.Linear(LIGHTNING_HIDDEN_WIDTH, 1),
        )

    def training_step(self, batch: torch.Tensor, batch_idx: int) -> torch.Tensor:
        del batch, batch_idx
        semantic_step = self.semantic_offset + int(self.global_step)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(self.seed + semantic_step * 104_729)
        features = torch.randn(
            LIGHTNING_BATCH_SIZE,
            LIGHTNING_INPUT_WIDTH,
            generator=generator,
        )
        target = (features.square().mean(dim=1, keepdim=True) - 0.5).tanh()
        loss = functional.mse_loss(self.network(features), target)
        self.loss_history.append(float(loss.detach().cpu()))
        return loss

    def configure_optimizers(self) -> dict[str, Any]:
        optimizer = torch.optim.Adam(self.parameters(), lr=0.01)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.9)
        return {
            "optimizer": optimizer,
            "lr_scheduler": {"scheduler": scheduler, "interval": "step"},
        }

    def on_save_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        if self.scenario != "complete":
            return
        checkpoint["flashpilot_exact_resume"] = {
            "loss_history": list(self.loss_history),
            "rng": {
                "python": _python_rng_state(),
                "numpy": _numpy_rng_state(),
                "torch": torch.get_rng_state(),
            },
        }

    def on_load_checkpoint(self, checkpoint: dict[str, Any]) -> None:
        state = checkpoint.get("flashpilot_exact_resume")
        if state is None:
            return
        if not isinstance(state, dict) or not isinstance(state.get("loss_history"), list):
            raise RuntimeError("Lightning exact-resume bridge is malformed")
        self.loss_history = [float(value) for value in state["loss_history"]]
        rng = state.get("rng")
        if not isinstance(rng, dict):
            raise RuntimeError("Lightning exact-resume RNG bridge is malformed")
        self._pending_rng_state = rng

    def on_train_batch_start(self, batch: object, batch_idx: int) -> None:
        del batch, batch_idx
        if self._pending_rng_state is not None:
            _restore_rng_state(self._pending_rng_state)
            self._pending_rng_state = None


def configure_determinism(seed: int) -> None:
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    seed_everything(seed, workers=True, verbose=False)


def training_loader(total_steps: int) -> DataLoader[torch.Tensor]:
    return DataLoader(
        TensorDataset(torch.zeros(total_steps, 1)),
        batch_size=1,
        shuffle=False,
        num_workers=0,
    )


def create_trainer(
    *,
    root_dir: Path,
    max_steps: int,
    callbacks: list[object] | None = None,
    enable_checkpointing: bool = False,
) -> Trainer:
    return Trainer(
        accelerator="cpu",
        devices=1,
        deterministic=True,
        max_steps=max_steps,
        default_root_dir=root_dir,
        callbacks=callbacks,
        enable_checkpointing=enable_checkpointing,
        logger=False,
        enable_progress_bar=False,
        enable_model_summary=False,
        num_sanity_val_steps=0,
        log_every_n_steps=1,
    )


def _parameter_iterator(model: nn.Module) -> Iterator[torch.Tensor]:
    for _, value in sorted(model.state_dict().items()):
        yield value.detach().cpu()


def fixed_evaluation_digest(model: FlashPilotLightningModule, *, seed: int) -> str:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed + 999_983)
    features = torch.randn(6, LIGHTNING_INPUT_WIDTH, generator=generator)
    model.eval()
    with torch.no_grad():
        output = model.network(features).detach().cpu()
    return state_digest(output)


def summarize_trainer(
    trainer: Trainer,
    model: FlashPilotLightningModule,
    *,
    mode: str,
    scenario: LightningScenario,
    checkpoint_step: int,
    semantic_global_step: int,
    model_loaded_from_checkpoint: bool,
    seed: int,
) -> LightningRunSummary:
    if not trainer.optimizers or not trainer.lr_scheduler_configs:
        raise RuntimeError("Lightning Trainer did not retain optimizer and scheduler evidence")
    optimizer = trainer.optimizers[0]
    scheduler = trainer.lr_scheduler_configs[0].scheduler
    return LightningRunSummary(
        mode=mode,
        scenario=scenario,
        worker_pid=os.getpid(),
        trainer_global_step=int(trainer.global_step),
        semantic_global_step=semantic_global_step,
        checkpoint_step=checkpoint_step,
        model_loaded_from_checkpoint=model_loaded_from_checkpoint,
        loss_history=tuple(model.loss_history),
        trainable_state_sha256=state_digest(tuple(_parameter_iterator(model))),
        evaluation_sha256=fixed_evaluation_digest(model, seed=seed),
        optimizer_sha256=state_digest(optimizer.state_dict()),
        scheduler_sha256=state_digest(scheduler.state_dict()),
        lightning_version=lightning.__version__,
        torch_version=str(torch.__version__),
    )
