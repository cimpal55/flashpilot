"""The Prompt 1 safe_full checkpoint strategy and direct-restore baseline."""

from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from pydantic import ValidationError

from flashpilot.checkpoints.atomic import (
    AtomicCommitResult,
    CommittedCallback,
    PayloadWriter,
    commit_checkpoint,
)
from flashpilot.checkpoints.loader import ValidatedCheckpoint, validate_checkpoint
from flashpilot.domain.manifests import (
    SAFE_FULL_PAYLOADS,
    SAFE_FULL_SERIALIZED_STATE,
    CheckpointManifest,
    ChecksumDocument,
    ManifestPayload,
    SafeFullState,
    WorkloadProfileSnapshot,
)
from flashpilot.workload.control import run_control
from flashpilot.workload.profiles import WorkloadProfile, get_profile
from flashpilot.workload.state import ControlRunSummary
from flashpilot.workload.trainer import (
    TrainingRuntime,
    create_training_runtime,
    summarize_runtime,
    train_until,
)


class SafeFullRestoreError(RuntimeError):
    """Raised when a validated safe_full checkpoint cannot be restored exactly."""


@dataclass(frozen=True, slots=True)
class SafeFullRestoreResult:
    runtime: TrainingRuntime
    checkpoint: ValidatedCheckpoint
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class SafeFullBaselineResult:
    profile: str
    run_root: Path
    checkpoint_step: int
    checkpoint_path: Path
    logical_checkpoint_bytes_written: int
    checkpoint_duration_seconds: float
    restore_duration_seconds: float
    direct_restore_matches_control: bool
    control_summary: ControlRunSummary
    resumed_summary: ControlRunSummary
    durability: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "run_root": str(self.run_root),
            "checkpoint_step": self.checkpoint_step,
            "checkpoint_path": str(self.checkpoint_path),
            "logical_checkpoint_bytes_written": self.logical_checkpoint_bytes_written,
            "checkpoint_duration_seconds": self.checkpoint_duration_seconds,
            "restore_duration_seconds": self.restore_duration_seconds,
            "direct_restore_matches_control": self.direct_restore_matches_control,
            "control_summary": self.control_summary.to_dict(),
            "resumed_summary": self.resumed_summary.to_dict(),
            "durability": self.durability,
            "limitations": [
                "This is a direct-restore baseline, not a Recovery Gate verdict.",
                "Physical NAND writes, write amplification, and SSD lifetime were not measured.",
            ],
        }


def _capture_rng_state() -> dict[str, Any]:
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    return {
        "schema_version": "rng-state-v1",
        "python": {
            "version": python_state[0],
            "state": list(python_state[1]),
            "gauss": python_state[2],
        },
        "numpy": {
            "bit_generator": numpy_state[0],
            "state": numpy_state[1].astype(np.uint32).tolist(),
            "position": numpy_state[2],
            "has_gauss": numpy_state[3],
            "cached_gaussian": numpy_state[4],
        },
        "torch": torch.get_rng_state(),
    }


def _restore_rng_state(payload: object) -> None:
    if not isinstance(payload, dict) or payload.get("schema_version") != "rng-state-v1":
        raise SafeFullRestoreError("RNG payload schema is invalid")
    try:
        python_state = payload["python"]
        numpy_state = payload["numpy"]
        torch_state = payload["torch"]
        if not isinstance(python_state, dict) or not isinstance(numpy_state, dict):
            raise TypeError("RNG state sections must be mappings")
        if not isinstance(torch_state, torch.Tensor) or torch_state.dtype != torch.uint8:
            raise TypeError("Torch RNG state must be a uint8 tensor")
        random.setstate(
            (
                int(python_state["version"]),
                tuple(int(value) for value in python_state["state"]),
                python_state["gauss"],
            )
        )
        np.random.set_state(
            (
                str(numpy_state["bit_generator"]),
                np.asarray(numpy_state["state"], dtype=np.uint32),
                int(numpy_state["position"]),
                int(numpy_state["has_gauss"]),
                float(numpy_state["cached_gaussian"]),
            )
        )
        torch.set_rng_state(torch_state.cpu())
    except (KeyError, TypeError, ValueError) as error:
        raise SafeFullRestoreError("RNG payload content is invalid") from error


def _torch_save_writer(value: object) -> PayloadWriter:
    def write(path: Path) -> None:
        torch.save(value, path)

    return write


def _json_state_writer(state: SafeFullState) -> PayloadWriter:
    def write(path: Path) -> None:
        path.write_text(state.model_dump_json(indent=2) + "\n", encoding="utf-8", newline="\n")

    return write


def save_safe_full(
    runtime: TrainingRuntime,
    *,
    run_root: Path,
    checkpoint_root_relative: str = "checkpoints",
    on_committed: CommittedCallback | None = None,
) -> AtomicCommitResult:
    """Persist complete CPU training state through the atomic commit protocol."""

    checkpoint_id = f"checkpoint-step-{runtime.global_step:06d}"
    profile_snapshot = WorkloadProfileSnapshot.model_validate(asdict(runtime.profile))
    state = SafeFullState(
        checkpoint_id=checkpoint_id,
        global_step=runtime.global_step,
        profile=profile_snapshot,
        loss_history=tuple(runtime.loss_history),
    )
    rng_state = _capture_rng_state()
    payload_writers = {
        SAFE_FULL_PAYLOADS["model"]: _torch_save_writer(runtime.model.state_dict()),
        SAFE_FULL_PAYLOADS["optimizer"]: _torch_save_writer(runtime.optimizer.state_dict()),
        SAFE_FULL_PAYLOADS["scheduler"]: _torch_save_writer(runtime.scheduler.state_dict()),
        SAFE_FULL_PAYLOADS["rng"]: _torch_save_writer(rng_state),
        SAFE_FULL_PAYLOADS["state"]: _json_state_writer(state),
    }
    role_by_path = {path: role for role, path in SAFE_FULL_PAYLOADS.items()}

    def build_manifest(checksums: ChecksumDocument) -> CheckpointManifest:
        return CheckpointManifest(
            checkpoint_id=checkpoint_id,
            profile=runtime.profile.name,
            global_step=runtime.global_step,
            created_at=datetime.now(UTC),
            serialized_state=SAFE_FULL_SERIALIZED_STATE,
            payloads=tuple(
                ManifestPayload(
                    role=role_by_path[entry.path],
                    path=entry.path,
                    sha256=entry.sha256,
                    size_bytes=entry.size_bytes,
                )
                for entry in checksums.files
            ),
        )

    return commit_checkpoint(
        run_root=run_root,
        checkpoint_root_relative=checkpoint_root_relative,
        checkpoint_id=checkpoint_id,
        payload_writers=payload_writers,
        manifest_factory=build_manifest,
        on_committed=on_committed,
    )


def _load_safe_tensor_file(path: Path) -> object:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except Exception as error:
        raise SafeFullRestoreError(
            f"safe tensor payload could not be loaded: {path.name}"
        ) from error


def restore_safe_full(*, run_root: Path, checkpoint_path: Path) -> SafeFullRestoreResult:
    """Validate integrity first, then restore all training state before the next batch."""

    started_at = time.perf_counter()
    checkpoint = validate_checkpoint(run_root=run_root, checkpoint_path=checkpoint_path)
    payload_by_role = {
        payload.role: checkpoint.path / payload.path for payload in checkpoint.manifest.payloads
    }
    try:
        state = SafeFullState.model_validate_json(
            payload_by_role["state"].read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValidationError) as error:
        raise SafeFullRestoreError("safe_full state metadata is invalid") from error
    if state.checkpoint_id != checkpoint.manifest.checkpoint_id:
        raise SafeFullRestoreError("state checkpoint_id does not match manifest")
    if state.global_step != checkpoint.manifest.global_step:
        raise SafeFullRestoreError("state global_step does not match manifest")

    profile = get_profile(state.profile.name)
    expected_profile = WorkloadProfileSnapshot.model_validate(asdict(profile))
    if state.profile != expected_profile:
        raise SafeFullRestoreError("checkpoint profile differs from the local supported profile")

    runtime = create_training_runtime(profile)
    try:
        runtime.model.load_state_dict(_load_safe_tensor_file(payload_by_role["model"]), strict=True)
        runtime.optimizer.load_state_dict(_load_safe_tensor_file(payload_by_role["optimizer"]))
        runtime.scheduler.load_state_dict(_load_safe_tensor_file(payload_by_role["scheduler"]))
    except (RuntimeError, TypeError, ValueError) as error:
        raise SafeFullRestoreError("training state payload is incompatible") from error
    runtime.global_step = state.global_step
    runtime.loss_history = list(state.loss_history)
    _restore_rng_state(_load_safe_tensor_file(payload_by_role["rng"]))
    return SafeFullRestoreResult(
        runtime=runtime,
        checkpoint=checkpoint,
        duration_seconds=time.perf_counter() - started_at,
    )


def run_safe_full_baseline(
    *,
    profile_name: str,
    run_root: Path,
    checkpoint_step: int | None = None,
) -> SafeFullBaselineResult:
    """Measure one safe_full commit and direct restore against the control."""

    profile: WorkloadProfile = get_profile(profile_name)
    selected_step = checkpoint_step if checkpoint_step is not None else profile.steps // 2
    if selected_step <= 0 or selected_step >= profile.steps:
        raise ValueError("checkpoint_step must be between zero and the profile's final step")

    control = run_control(profile.name)
    runtime = create_training_runtime(profile)
    train_until(runtime, selected_step)
    commit = save_safe_full(runtime, run_root=run_root)
    restored = restore_safe_full(run_root=run_root, checkpoint_path=commit.checkpoint_path)
    train_until(restored.runtime, profile.steps)
    resumed = summarize_runtime(restored.runtime)
    return SafeFullBaselineResult(
        profile=profile.name,
        run_root=run_root.resolve(),
        checkpoint_step=selected_step,
        checkpoint_path=commit.checkpoint_path,
        logical_checkpoint_bytes_written=commit.logical_bytes_written,
        checkpoint_duration_seconds=commit.duration_seconds,
        restore_duration_seconds=restored.duration_seconds,
        direct_restore_matches_control=resumed == control,
        control_summary=control,
        resumed_summary=resumed,
        durability={
            "payload_files_fsynced": commit.payload_files_synced,
            "metadata_files_fsynced": commit.metadata_files_synced,
            "atomic_rename_succeeded": commit.atomic_rename_succeeded,
            "temp_directory_fsync": asdict(commit.temp_directory_sync),
            "parent_directory_fsync": asdict(commit.parent_directory_sync),
        },
    )


def baseline_json(result: SafeFullBaselineResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"
