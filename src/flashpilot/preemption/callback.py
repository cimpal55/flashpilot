"""Signal-safe Trainer callback for managed preemption checkpoint commits."""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime
from pathlib import Path

from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments

from flashpilot.checkpoints.atomic import fsync_directory
from flashpilot.hf.callback import (
    build_checkpoint_lifecycle_evidence,
    persist_checkpoint_lifecycle_metadata,
)
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.preemption.models import (
    PREEMPTION_INCOMPLETE_MARKER,
    HFPreemptionCommitEvidence,
    HFPreemptionReadyEvidence,
)
from flashpilot.security.paths import PathSandbox


class PreemptionSignalState:
    """Minimal state shared by the main-thread signal handler and callback."""

    def __init__(self) -> None:
        self.received_at: datetime | None = None

    def record_sigterm(self) -> None:
        if self.received_at is None:
            self.received_at = datetime.now(UTC)


class FlashPilotPreemptionCallback(TrainerCallback):
    """Request one save only after the worker has observed SIGTERM."""

    def __init__(
        self,
        *,
        run_root: Path,
        checkpoint_step: int,
        grace_period_seconds: int,
        signal_state: PreemptionSignalState,
    ) -> None:
        self.run_root = PathSandbox.create(run_root).root
        self.checkpoint_step = checkpoint_step
        self.grace_period_seconds = grace_period_seconds
        self.signal_state = signal_state
        self._save_requested = False

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> TrainerControl:
        del args, kwargs
        if int(state.global_step) != self.checkpoint_step:
            return control
        ready = HFPreemptionReadyEvidence(
            worker_pid=os.getpid(),
            completed_step=int(state.global_step),
            emitted_at=datetime.now(UTC),
        )
        print(ready.model_dump_json(), flush=True)
        deadline = time.monotonic() + float(self.grace_period_seconds)
        while self.signal_state.received_at is None:
            if time.monotonic() >= deadline:
                raise RuntimeError("SIGTERM was not received before the grace-period deadline")
            time.sleep(0.01)
        write_json_artifact(
            run_root=self.run_root,
            relative_path=PREEMPTION_INCOMPLETE_MARKER,
            value={
                "schema_version": "flashpilot-preemption-incomplete-v1",
                "signal_name": "SIGTERM",
                "worker_pid": os.getpid(),
                "checkpoint_step": self.checkpoint_step,
            },
        )
        self._save_requested = True
        control.should_save = True
        control.should_training_stop = True
        return control

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: object,
    ) -> TrainerControl:
        del kwargs
        if not self._save_requested or int(state.global_step) != self.checkpoint_step:
            return control
        received_at = self.signal_state.received_at
        if received_at is None:
            raise RuntimeError("preemption save cannot occur without SIGTERM evidence")
        checkpoint = Path(args.output_dir).resolve() / f"checkpoint-{state.global_step}"
        checkpoint_event = build_checkpoint_lifecycle_evidence(
            run_root=self.run_root,
            checkpoint=checkpoint,
            global_step=int(state.global_step),
            scenario="complete",
        )
        persist_checkpoint_lifecycle_metadata(
            run_root=self.run_root,
            checkpoint=checkpoint,
            evidence=checkpoint_event,
            args=args,
        )
        marker = PathSandbox.create(self.run_root).resolve_relative(
            PREEMPTION_INCOMPLETE_MARKER,
            must_exist=True,
        )
        marker.unlink()
        directory_sync = fsync_directory(marker.parent)
        if directory_sync.supported and not directory_sync.succeeded:
            raise OSError(directory_sync.detail)
        commit = HFPreemptionCommitEvidence(
            worker_pid=os.getpid(),
            signal_received_at=received_at,
            checkpoint_committed_at=datetime.now(UTC),
            checkpoint=checkpoint_event,
        )
        write_json_artifact(
            run_root=self.run_root,
            relative_path="preemption/commit.json",
            value=commit,
        )
        print(commit.model_dump_json(), flush=True)
        return control
