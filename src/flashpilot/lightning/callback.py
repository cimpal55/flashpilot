"""Lightning callback that reports a durable checkpoint but never a verdict."""

from __future__ import annotations

import os
import threading
from datetime import UTC, datetime
from pathlib import Path

from lightning.pytorch import Callback, LightningModule, Trainer

from flashpilot.adapters.lightning import PyTorchLightningAdapter
from flashpilot.lightning.models import (
    LightningCheckpointLifecycleEvidence,
    LightningScenario,
)
from flashpilot.orchestration.artifacts import write_json_artifact


class FlashPilotLightningCallback(Callback):
    """Emit lifecycle evidence only after the checkpoint file is safely loadable."""

    def __init__(
        self,
        *,
        run_root: Path,
        checkpoint_directory: Path,
        scenario: LightningScenario,
        checkpoint_step: int,
        pause_for_parent_kill: bool,
    ) -> None:
        self.run_root = run_root.resolve()
        self.checkpoint_directory = checkpoint_directory.resolve()
        self.scenario = scenario
        self.checkpoint_step = checkpoint_step
        self.pause_for_parent_kill = pause_for_parent_kill
        self.emitted = False

    def on_train_batch_end(
        self,
        trainer: Trainer,
        pl_module: LightningModule,
        outputs: object,
        batch: object,
        batch_idx: int,
    ) -> None:
        del pl_module, outputs, batch, batch_idx
        if self.emitted or int(trainer.global_step) != self.checkpoint_step:
            return
        try:
            relative = self.checkpoint_directory.relative_to(self.run_root).as_posix()
        except ValueError as error:
            raise RuntimeError("Lightning checkpoint escaped the run-owned sandbox") from error
        self.checkpoint_directory.mkdir(parents=True, exist_ok=False)
        trainer.save_checkpoint(
            self.checkpoint_directory / "state.ckpt",
            weights_only=self.scenario == "weights-only",
        )
        state = PyTorchLightningAdapter().training_state_presence(self.checkpoint_directory)
        evidence = LightningCheckpointLifecycleEvidence(
            worker_pid=os.getpid(),
            global_step=int(trainer.global_step),
            checkpoint_path=relative,
            scenario=self.scenario,
            model_present=state["model"],
            loop_state_present=state["loop_state"],
            optimizer_present=state["optimizer"],
            scheduler_present=state["scheduler"],
            rng_state_present=state["rng"],
            loss_history_present=state["loss_history"],
            emitted_at=datetime.now(UTC),
        )
        write_json_artifact(
            run_root=self.run_root,
            relative_path=f"{relative}/flashpilot-checkpoint-event.json",
            value=evidence,
        )
        self.emitted = True
        print(evidence.model_dump_json(), flush=True)
        if self.pause_for_parent_kill:
            threading.Event().wait(timeout=300.0)
