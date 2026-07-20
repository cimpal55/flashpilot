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


def build_checkpoint_lifecycle_evidence(
    *,
    run_root: Path,
    checkpoint: Path,
    global_step: int,
    scenario: HFScenario,
) -> HFCheckpointLifecycleEvidence:
    """Inspect a completed Trainer save without assigning a recovery verdict."""

    try:
        relative_checkpoint = checkpoint.resolve().relative_to(run_root.resolve()).as_posix()
    except ValueError as error:
        raise RuntimeError("Trainer checkpoint escaped the run-owned sandbox") from error
    return HFCheckpointLifecycleEvidence(
        worker_pid=os.getpid(),
        global_step=global_step,
        checkpoint_path=relative_checkpoint,
        scenario=scenario,
        model_present=(checkpoint / "model.safetensors").is_file()
        or (checkpoint / "pytorch_model.bin").is_file(),
        trainer_state_present=(checkpoint / "trainer_state.json").is_file(),
        optimizer_present=(checkpoint / "optimizer.pt").is_file(),
        scheduler_present=(checkpoint / "scheduler.pt").is_file(),
        rng_state_present=any(checkpoint.glob("rng_state*.pth")),
        emitted_at=datetime.now(UTC),
    )


def persist_checkpoint_lifecycle_metadata(
    *,
    run_root: Path,
    checkpoint: Path,
    evidence: HFCheckpointLifecycleEvidence,
    args: TrainingArguments,
) -> None:
    """Persist callback-owned metadata after Trainer has completed the save."""

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
        run_root=run_root,
        relative_path=f"{evidence.checkpoint_path}/training_args.json",
        value=training_arguments,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=f"{evidence.checkpoint_path}/flashpilot-callback.json",
        value=evidence,
    )
    if evidence.rng_state_present:
        rng_path = checkpoint / "rng_state.pth"
        write_json_artifact(
            run_root=run_root,
            relative_path=f"{evidence.checkpoint_path}/flashpilot-rng-metadata.json",
            value=HFRngMetadata(payload_sha256=sha256_file(rng_path)),
        )


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
        evidence = build_checkpoint_lifecycle_evidence(
            run_root=self.run_root,
            checkpoint=checkpoint,
            global_step=int(state.global_step),
            scenario=self.scenario,
        )
        persist_checkpoint_lifecycle_metadata(
            run_root=self.run_root,
            checkpoint=checkpoint,
            evidence=evidence,
            args=args,
        )
        print(evidence.model_dump_json(), flush=True)
        if self.pause_for_parent_kill:
            threading.Event().wait(timeout=60.0)
        return control
