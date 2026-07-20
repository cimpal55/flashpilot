"""Trainer callback that emits checkpoint lifecycle evidence but no verdict."""

from __future__ import annotations

import os
import threading
from datetime import UTC, datetime
from pathlib import Path

from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

from flashpilot.checkpoints.integrity import sha256_file
from flashpilot.hf.models import HFCheckpointLifecycleEvidence, HFRngMetadata, HFScenario
from flashpilot.orchestration.artifacts import write_json_artifact


class FlashPilotTrainerCallback(TrainerCallback):
    """Bridge Trainer save completion to the parent-owned fault harness."""

    def __init__(
        self,
        *,
        run_root: Path,
        scenario: HFScenario,
        checkpoint_step: int,
        pause_for_parent_kill: bool,
    ) -> None:
        self.run_root = run_root.resolve()
        self.scenario = scenario
        self.checkpoint_step = checkpoint_step
        self.pause_for_parent_kill = pause_for_parent_kill

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> TrainerControl:
        if int(state.global_step) != self.checkpoint_step:
            return control
        checkpoint = Path(args.output_dir).resolve() / f"checkpoint-{state.global_step}"
        try:
            relative_checkpoint = checkpoint.relative_to(self.run_root).as_posix()
        except ValueError as error:
            raise RuntimeError("Trainer checkpoint escaped the run-owned sandbox") from error
        rng_present = any(checkpoint.glob("rng_state*.pth"))
        evidence = HFCheckpointLifecycleEvidence(
            worker_pid=os.getpid(),
            global_step=int(state.global_step),
            checkpoint_path=relative_checkpoint,
            scenario=self.scenario,
            model_present=(checkpoint / "model.safetensors").is_file()
            or (checkpoint / "pytorch_model.bin").is_file(),
            trainer_state_present=(checkpoint / "trainer_state.json").is_file(),
            optimizer_present=(checkpoint / "optimizer.pt").is_file(),
            scheduler_present=(checkpoint / "scheduler.pt").is_file(),
            rng_state_present=rng_present,
            emitted_at=datetime.now(UTC),
        )
        training_arguments = {
            "seed": args.seed,
            "data_seed": args.data_seed,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "max_steps": args.max_steps,
            "save_only_model": args.save_only_model,
            "train_sampling_strategy": str(args.train_sampling_strategy),
        }
        write_json_artifact(
            run_root=self.run_root,
            relative_path=f"{relative_checkpoint}/training_args.json",
            value=training_arguments,
        )
        write_json_artifact(
            run_root=self.run_root,
            relative_path=f"{relative_checkpoint}/flashpilot-callback.json",
            value=evidence,
        )
        if evidence.rng_state_present:
            rng_path = checkpoint / "rng_state.pth"
            write_json_artifact(
                run_root=self.run_root,
                relative_path=f"{relative_checkpoint}/flashpilot-rng-metadata.json",
                value=HFRngMetadata(payload_sha256=sha256_file(rng_path)),
            )
        print(evidence.model_dump_json(), flush=True)
        if self.pause_for_parent_kill:
            threading.Event().wait(timeout=60.0)
        return control
