"""Adapter-aware and intentionally incomplete Prompt 2 checkpoint strategies."""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import torch
from pydantic import ValidationError

from flashpilot.adapters.base import TrainerAdapter
from flashpilot.adapters.registry import get_adapter
from flashpilot.checkpoints.atomic import AtomicCommitResult, PayloadWriter, commit_checkpoint
from flashpilot.checkpoints.base_artifact import (
    BaseArtifactResult,
    BaseArtifactValidationError,
    ensure_base_artifact,
    load_frozen_base_state,
    validate_base_artifact,
)
from flashpilot.checkpoints.loader import ValidatedCheckpoint, validate_checkpoint
from flashpilot.checkpoints.strategies import (
    SafeFullRestoreError,
    _capture_rng_state,
    _load_safe_tensor_file,
    _restore_rng_state,
    _torch_save_writer,
)
from flashpilot.domain.manifests import (
    MISSING_TRAINING_STATE_OMISSIONS,
    MISSING_TRAINING_STATE_PAYLOADS,
    MISSING_TRAINING_STATE_SERIALIZED_STATE,
    SAFE_ADAPTER_AWARE_PAYLOADS,
    SAFE_ADAPTER_AWARE_SERIALIZED_STATE,
    AdapterCheckpointState,
    CheckpointManifest,
    ChecksumDocument,
    ManifestPayload,
    WorkloadProfileSnapshot,
)
from flashpilot.workload.profiles import get_profile
from flashpilot.workload.trainer import TrainingRuntime, create_training_runtime

ADAPTER_CHECKPOINT_ROOT = "checkpoints/safe-adapter-aware"
MISSING_STATE_CHECKPOINT_ROOT = "checkpoints/missing-training-state"


class AdapterCheckpointRestoreError(RuntimeError):
    """Raised when a validated adapter checkpoint cannot be restored safely."""


@dataclass(frozen=True, slots=True)
class AdapterCheckpointCommit:
    checkpoint: AtomicCommitResult
    base_artifact: BaseArtifactResult


@dataclass(frozen=True, slots=True)
class AdapterCheckpointRestoreResult:
    runtime: TrainingRuntime
    checkpoint: ValidatedCheckpoint
    base_artifact: BaseArtifactResult
    duration_seconds: float


def _json_state_writer(state: AdapterCheckpointState) -> PayloadWriter:
    def write(path: Path) -> None:
        path.write_text(state.model_dump_json(indent=2) + "\n", encoding="utf-8", newline="\n")

    return write


def _save_adapter_checkpoint(
    runtime: TrainingRuntime,
    *,
    run_root: Path,
    strategy: str,
    checkpoint_root_relative: str,
    trainer_adapter: TrainerAdapter,
) -> AdapterCheckpointCommit:
    base_artifact = ensure_base_artifact(
        runtime,
        run_root=run_root,
        trainer_adapter=trainer_adapter,
    )
    checkpoint_id = f"checkpoint-step-{runtime.global_step:06d}"
    profile_snapshot = WorkloadProfileSnapshot.model_validate(asdict(runtime.profile))
    state = AdapterCheckpointState(
        checkpoint_id=checkpoint_id,
        strategy=strategy,
        global_step=runtime.global_step,
        profile=profile_snapshot,
        loss_history=tuple(runtime.loss_history),
        base_artifact=base_artifact.reference,
    )
    if strategy == "safe_adapter_aware":
        payload_paths = SAFE_ADAPTER_AWARE_PAYLOADS
        serialized_state = SAFE_ADAPTER_AWARE_SERIALIZED_STATE
        omitted_state = ()
        payload_writers = {
            payload_paths["adapter"]: _torch_save_writer(
                trainer_adapter.trainable_adapter_state(runtime.model)
            ),
            payload_paths["optimizer"]: _torch_save_writer(runtime.optimizer.state_dict()),
            payload_paths["scheduler"]: _torch_save_writer(runtime.scheduler.state_dict()),
            payload_paths["rng"]: _torch_save_writer(_capture_rng_state()),
            payload_paths["state"]: _json_state_writer(state),
        }
    elif strategy == "missing_training_state":
        payload_paths = MISSING_TRAINING_STATE_PAYLOADS
        serialized_state = MISSING_TRAINING_STATE_SERIALIZED_STATE
        omitted_state = MISSING_TRAINING_STATE_OMISSIONS
        payload_writers = {
            payload_paths["adapter"]: _torch_save_writer(
                trainer_adapter.trainable_adapter_state(runtime.model)
            ),
            payload_paths["state"]: _json_state_writer(state),
        }
    else:
        raise ValueError(f"unsupported adapter checkpoint strategy: {strategy}")
    role_by_path = {path: role for role, path in payload_paths.items()}

    def build_manifest(checksums: ChecksumDocument) -> CheckpointManifest:
        return CheckpointManifest(
            checkpoint_id=checkpoint_id,
            strategy=strategy,
            profile=runtime.profile.name,
            global_step=runtime.global_step,
            created_at=datetime.now(UTC),
            serialized_state=serialized_state,
            omitted_state=omitted_state,
            base_artifact=base_artifact.reference,
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

    checkpoint = commit_checkpoint(
        run_root=run_root,
        checkpoint_root_relative=checkpoint_root_relative,
        checkpoint_id=checkpoint_id,
        payload_writers=payload_writers,
        manifest_factory=build_manifest,
    )
    return AdapterCheckpointCommit(checkpoint=checkpoint, base_artifact=base_artifact)


def save_safe_adapter_aware(
    runtime: TrainingRuntime,
    *,
    run_root: Path,
    checkpoint_root_relative: str = ADAPTER_CHECKPOINT_ROOT,
    trainer_adapter: TrainerAdapter | None = None,
) -> AdapterCheckpointCommit:
    """Persist adapter training state while referencing one immutable frozen base."""

    return _save_adapter_checkpoint(
        runtime,
        run_root=run_root,
        strategy="safe_adapter_aware",
        checkpoint_root_relative=checkpoint_root_relative,
        trainer_adapter=trainer_adapter or get_adapter("native-pytorch"),
    )


def save_missing_training_state(
    runtime: TrainingRuntime,
    *,
    run_root: Path,
    checkpoint_root_relative: str = MISSING_STATE_CHECKPOINT_ROOT,
    trainer_adapter: TrainerAdapter | None = None,
) -> AdapterCheckpointCommit:
    """Persist a valid, loadable checkpoint with known training-state omissions."""

    return _save_adapter_checkpoint(
        runtime,
        run_root=run_root,
        strategy="missing_training_state",
        checkpoint_root_relative=checkpoint_root_relative,
        trainer_adapter=trainer_adapter or get_adapter("native-pytorch"),
    )


def _require_tensor_mapping(value: object, *, payload_name: str) -> Mapping[str, torch.Tensor]:
    if not isinstance(value, Mapping) or not all(
        isinstance(key, str) and isinstance(tensor, torch.Tensor) for key, tensor in value.items()
    ):
        raise AdapterCheckpointRestoreError(f"{payload_name} is not a tensor state mapping")
    return value


def _restore_adapter_checkpoint(
    *,
    run_root: Path,
    checkpoint_path: Path,
    expected_strategy: str,
    trainer_adapter: TrainerAdapter,
) -> AdapterCheckpointRestoreResult:
    started_at = time.perf_counter()
    checkpoint = validate_checkpoint(run_root=run_root, checkpoint_path=checkpoint_path)
    manifest = checkpoint.manifest
    if manifest.strategy != expected_strategy or manifest.base_artifact is None:
        raise AdapterCheckpointRestoreError("checkpoint strategy does not match restore request")
    try:
        base_artifact = validate_base_artifact(
            run_root=run_root,
            reference=manifest.base_artifact,
        )
    except BaseArtifactValidationError as error:
        raise AdapterCheckpointRestoreError("frozen base validation failed") from error
    payload_by_role = {
        payload.role: checkpoint.path / payload.path for payload in manifest.payloads
    }
    try:
        state = AdapterCheckpointState.model_validate_json(
            payload_by_role["state"].read_text(encoding="utf-8")
        )
    except (KeyError, OSError, UnicodeError, ValidationError) as error:
        raise AdapterCheckpointRestoreError(
            "adapter checkpoint state metadata is invalid"
        ) from error
    if (
        state.checkpoint_id != manifest.checkpoint_id
        or state.global_step != manifest.global_step
        or state.strategy != manifest.strategy
        or state.base_artifact != manifest.base_artifact
    ):
        raise AdapterCheckpointRestoreError("adapter state metadata does not match the manifest")
    profile = get_profile(state.profile.name)
    expected_profile = WorkloadProfileSnapshot.model_validate(asdict(profile))
    if state.profile != expected_profile:
        raise AdapterCheckpointRestoreError("checkpoint profile differs from the supported profile")

    try:
        frozen_base = _require_tensor_mapping(
            load_frozen_base_state(run_root=run_root, reference=manifest.base_artifact),
            payload_name="frozen base",
        )
        adapter_state = _require_tensor_mapping(
            _load_safe_tensor_file(payload_by_role["adapter"]),
            payload_name="adapter payload",
        )
        runtime = create_training_runtime(profile)
        trainer_adapter.restore_partitioned_model(
            runtime.model,
            frozen_base=frozen_base,
            adapter_state=adapter_state,
        )
        if expected_strategy == "safe_adapter_aware":
            runtime.optimizer.load_state_dict(_load_safe_tensor_file(payload_by_role["optimizer"]))
            runtime.scheduler.load_state_dict(_load_safe_tensor_file(payload_by_role["scheduler"]))
        runtime.global_step = state.global_step
        runtime.loss_history = list(state.loss_history)
        if expected_strategy == "safe_adapter_aware":
            _restore_rng_state(_load_safe_tensor_file(payload_by_role["rng"]))
    except (
        BaseArtifactValidationError,
        KeyError,
        RuntimeError,
        SafeFullRestoreError,
        TypeError,
        ValueError,
    ) as error:
        raise AdapterCheckpointRestoreError("adapter checkpoint payload is incompatible") from error
    return AdapterCheckpointRestoreResult(
        runtime=runtime,
        checkpoint=checkpoint,
        base_artifact=base_artifact,
        duration_seconds=time.perf_counter() - started_at,
    )


def restore_safe_adapter_aware(
    *,
    run_root: Path,
    checkpoint_path: Path,
    trainer_adapter: TrainerAdapter | None = None,
) -> AdapterCheckpointRestoreResult:
    return _restore_adapter_checkpoint(
        run_root=run_root,
        checkpoint_path=checkpoint_path,
        expected_strategy="safe_adapter_aware",
        trainer_adapter=trainer_adapter or get_adapter("native-pytorch"),
    )


def restore_missing_training_state(
    *,
    run_root: Path,
    checkpoint_path: Path,
    trainer_adapter: TrainerAdapter | None = None,
) -> AdapterCheckpointRestoreResult:
    return _restore_adapter_checkpoint(
        run_root=run_root,
        checkpoint_path=checkpoint_path,
        expected_strategy="missing_training_state",
        trainer_adapter=trainer_adapter or get_adapter("native-pytorch"),
    )
