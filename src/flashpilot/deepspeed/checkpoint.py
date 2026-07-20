"""Atomic, checksum-closed metadata around a DeepSpeed ZeRO-2 checkpoint."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import numpy as np
import torch
from pydantic import BaseModel, ConfigDict, ValidationError

from flashpilot.checkpoints.atomic import fsync_directory, fsync_file, write_model_durable
from flashpilot.checkpoints.integrity import logical_directory_bytes, sha256_file
from flashpilot.deepspeed.models import (
    DeepSpeedCheckpointEvent,
    DeepSpeedCheckpointManifest,
    DeepSpeedCheckpointPayload,
    DeepSpeedRankCheckpointState,
)
from flashpilot.distributed.models import (
    LinearSchedulerState,
    NumPyRngState,
    PythonRngState,
    TorchRngState,
)
from flashpilot.domain.manifests import ChecksumDocument, ChecksumEntry, CompletionMarker
from flashpilot.security.paths import PathContainmentError, PathSandbox


class DeepSpeedCheckpointError(RuntimeError):
    """DeepSpeed checkpoint metadata is incomplete, corrupt, or unsafe."""


class DeepSpeedClientState(BaseModel):
    """Small strict client state saved through DeepSpeed's checkpoint API."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["flashpilot-deepspeed-client-state-v1"] = (
        "flashpilot-deepspeed-client-state-v1"
    )
    checkpoint_id: str
    checkpoint_tag: str
    global_step: int
    world_size: Literal[2] = 2
    zero_stage: Literal[2] = 2


@dataclass(frozen=True, slots=True)
class ValidatedDeepSpeedCheckpoint:
    path: Path
    manifest: DeepSpeedCheckpointManifest
    checksums: ChecksumDocument
    inventory: tuple[str, ...]
    logical_bytes: int


def _scheduler_state(scheduler: torch.optim.lr_scheduler.LinearLR) -> LinearSchedulerState:
    state = scheduler.state_dict()
    expected = {
        "start_factor",
        "end_factor",
        "total_iters",
        "base_lrs",
        "last_epoch",
        "_step_count",
        "_is_initial",
        "_get_lr_called_within_step",
        "_last_lr",
    }
    if set(state) != expected:
        raise DeepSpeedCheckpointError("LinearLR scheduler state shape changed unexpectedly")
    return LinearSchedulerState(
        start_factor=state["start_factor"],
        end_factor=state["end_factor"],
        total_iters=state["total_iters"],
        base_lrs=tuple(state["base_lrs"]),
        last_epoch=state["last_epoch"],
        step_count=state["_step_count"],
        is_initial=state["_is_initial"],
        get_lr_called_within_step=state["_get_lr_called_within_step"],
        last_lrs=tuple(state["_last_lr"]),
    )


def capture_rank_checkpoint_state(
    *,
    rank: int,
    global_step: int,
    loss_history: tuple[float, ...],
    scheduler: torch.optim.lr_scheduler.LinearLR,
) -> DeepSpeedRankCheckpointState:
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.get_rng_state()
    return DeepSpeedRankCheckpointState(
        rank=rank,
        global_step=global_step,
        loss_history=loss_history,
        scheduler=_scheduler_state(scheduler),
        python_rng=PythonRngState(
            version=python_state[0],
            internal_state=tuple(python_state[1]),
            gaussian_cache=python_state[2],
        ),
        numpy_rng=NumPyRngState(
            algorithm=numpy_state[0],
            keys=tuple(int(value) for value in numpy_state[1]),
            position=numpy_state[2],
            has_gaussian=numpy_state[3],
            cached_gaussian=numpy_state[4],
        ),
        torch_rng=TorchRngState(bytes=tuple(int(value) for value in torch_state.tolist())),
    )


def restore_rank_rng_state(state: DeepSpeedRankCheckpointState) -> None:
    """Restore only rank-local RNG; DeepSpeed must restore scheduler state itself."""

    random.setstate(
        (
            state.python_rng.version,
            tuple(state.python_rng.internal_state),
            state.python_rng.gaussian_cache,
        )
    )
    np.random.set_state(
        (
            state.numpy_rng.algorithm,
            np.asarray(state.numpy_rng.keys, dtype=np.uint32),
            state.numpy_rng.position,
            state.numpy_rng.has_gaussian,
            state.numpy_rng.cached_gaussian,
        )
    )
    torch.set_rng_state(torch.tensor(state.torch_rng.bytes, dtype=torch.uint8))


def scheduler_state_matches(
    scheduler: torch.optim.lr_scheduler.LinearLR, state: DeepSpeedRankCheckpointState
) -> bool:
    return _scheduler_state(scheduler) == state.scheduler


def write_rank_checkpoint_state(path: Path, state: DeepSpeedRankCheckpointState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_model_durable(path, state)


def read_rank_checkpoint_state(
    *, run_root: Path, checkpoint_path: Path, rank: int
) -> DeepSpeedRankCheckpointState:
    try:
        checkpoint = PathSandbox.create(run_root).require_contained(
            checkpoint_path, must_exist=True
        )
        path = PathSandbox.create(checkpoint).resolve_relative(
            f"rank-state-{rank:03d}.json", must_exist=True
        )
        state = DeepSpeedRankCheckpointState.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, PathContainmentError) as error:
        raise DeepSpeedCheckpointError(f"invalid DeepSpeed state for rank {rank}") from error
    if state.rank != rank:
        raise DeepSpeedCheckpointError("DeepSpeed rank checkpoint state identity mismatch")
    return state


def _payload_role(relative: str, checkpoint_tag: str) -> tuple[str, int | None]:
    if relative == "latest":
        return "deepspeed-latest", None
    if relative == "zero_to_fp32.py":
        return "deepspeed-conversion-helper", None
    if relative == f"{checkpoint_tag}/mp_rank_00_model_states.pt":
        return "deepspeed-model-state", None
    for rank in (0, 1):
        if relative == f"{checkpoint_tag}/zero_pp_rank_{rank}_mp_rank_00_optim_states.pt":
            return "deepspeed-optimizer-shard", rank
        if relative == f"rank-state-{rank:03d}.json":
            return "rank-state", rank
    raise DeepSpeedCheckpointError(f"unexpected DeepSpeed checkpoint payload: {relative}")


def finalize_deepspeed_checkpoint(
    *,
    run_root: Path,
    temporary_checkpoint_path: Path,
    final_checkpoint_path: Path,
    checkpoint_id: str,
    checkpoint_tag: str,
    global_step: int,
    writer_pid: int,
    save_started_at: float,
) -> DeepSpeedCheckpointEvent:
    """Checksum and atomically rename a collectively written DeepSpeed checkpoint."""

    sandbox = PathSandbox.create(run_root)
    try:
        temporary = sandbox.require_contained(temporary_checkpoint_path, must_exist=True)
        final = sandbox.require_contained(final_checkpoint_path)
    except PathContainmentError as error:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint path failed containment") from error
    if temporary.is_symlink() or not temporary.is_dir():
        raise DeepSpeedCheckpointError("temporary DeepSpeed checkpoint must be a directory")
    if final.exists() or final.name != checkpoint_id or temporary.parent != final.parent:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint destination is invalid")
    try:
        latest = (temporary / "latest").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        raise DeepSpeedCheckpointError("DeepSpeed latest tag is unavailable") from error
    if latest != checkpoint_tag:
        raise DeepSpeedCheckpointError("DeepSpeed latest tag differs from committed tag")

    entries: list[ChecksumEntry] = []
    payloads: list[DeepSpeedCheckpointPayload] = []
    for candidate in sorted(
        temporary.rglob("*"), key=lambda path: path.relative_to(temporary).as_posix()
    ):
        if candidate.is_symlink():
            raise DeepSpeedCheckpointError("DeepSpeed checkpoint refuses symbolic links")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(temporary).as_posix()
        role, rank = _payload_role(relative, checkpoint_tag)
        fsync_file(candidate)
        digest = sha256_file(candidate)
        size = candidate.stat().st_size
        entries.append(ChecksumEntry(path=relative, sha256=digest, size_bytes=size))
        payloads.append(
            DeepSpeedCheckpointPayload(
                role=role,
                path=relative,
                sha256=digest,
                size_bytes=size,
                rank=rank,
            )
        )

    checksums = ChecksumDocument(files=tuple(entries))
    manifest = DeepSpeedCheckpointManifest(
        checkpoint_id=checkpoint_id,
        global_step=global_step,
        checkpoint_tag=checkpoint_tag,
        created_at=datetime.now(UTC),
        payloads=tuple(payloads),
    )
    write_model_durable(temporary / "checksums.json", checksums)
    write_model_durable(temporary / "manifest.json", manifest)
    write_model_durable(temporary / "COMPLETE", CompletionMarker(checkpoint_id=checkpoint_id))
    temporary_sync = fsync_directory(temporary)
    if temporary_sync.supported and not temporary_sync.succeeded:
        raise DeepSpeedCheckpointError(temporary_sync.detail)
    os.rename(temporary, final)
    parent_sync = fsync_directory(final.parent)
    if parent_sync.supported and not parent_sync.succeeded:
        raise DeepSpeedCheckpointError(parent_sync.detail)
    return DeepSpeedCheckpointEvent(
        writer_pid=writer_pid,
        checkpoint_path=final.relative_to(sandbox.root).as_posix(),
        checkpoint_tag=checkpoint_tag,
        global_step=global_step,
        commit_duration_seconds=time.perf_counter() - save_started_at,
        logical_bytes=logical_directory_bytes(final),
        directory_fsync_supported=temporary_sync.supported and parent_sync.supported,
        directory_fsync_succeeded=temporary_sync.succeeded and parent_sync.succeeded,
        emitted_at=datetime.now(UTC),
    )


def _read_model(path: Path, model_type: type[BaseModel]) -> BaseModel:
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise DeepSpeedCheckpointError(f"invalid DeepSpeed metadata: {path.name}") from error


def validate_deepspeed_checkpoint(
    *, run_root: Path, checkpoint_path: Path
) -> ValidatedDeepSpeedCheckpoint:
    """Validate marker, strict layout, closed inventory, sizes, and SHA-256."""

    try:
        checkpoint = PathSandbox.create(run_root).require_contained(
            checkpoint_path, must_exist=True
        )
    except PathContainmentError as error:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint failed containment") from error
    if checkpoint.is_symlink() or not checkpoint.is_dir() or checkpoint.name.startswith("."):
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint must be a final directory")
    sandbox = PathSandbox.create(checkpoint)
    try:
        marker = _read_model(
            sandbox.resolve_relative("COMPLETE", must_exist=True), CompletionMarker
        )
        manifest = _read_model(
            sandbox.resolve_relative("manifest.json", must_exist=True),
            DeepSpeedCheckpointManifest,
        )
        checksums = _read_model(
            sandbox.resolve_relative("checksums.json", must_exist=True), ChecksumDocument
        )
    except PathContainmentError as error:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint metadata is missing") from error
    assert isinstance(marker, CompletionMarker)
    assert isinstance(manifest, DeepSpeedCheckpointManifest)
    assert isinstance(checksums, ChecksumDocument)
    if marker.checkpoint_id != manifest.checkpoint_id or manifest.checkpoint_id != checkpoint.name:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint identity mismatch")

    checksum_by_path = {entry.path: entry for entry in checksums.files}
    payload_by_path = {payload.path: payload for payload in manifest.payloads}
    if checksum_by_path.keys() != payload_by_path.keys():
        raise DeepSpeedCheckpointError("DeepSpeed manifest and checksums differ")
    expected_files = set(checksum_by_path) | {"COMPLETE", "checksums.json", "manifest.json"}
    actual_files: set[str] = set()
    actual_directories: set[str] = set()
    for candidate in checkpoint.rglob("*"):
        if candidate.is_symlink():
            raise DeepSpeedCheckpointError("DeepSpeed checkpoint contains a symbolic link")
        relative = candidate.relative_to(checkpoint).as_posix()
        if candidate.is_file():
            actual_files.add(relative)
        elif candidate.is_dir():
            actual_directories.add(relative)
    if actual_files != expected_files:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint inventory is not closed")
    if actual_directories != {manifest.checkpoint_tag}:
        raise DeepSpeedCheckpointError("DeepSpeed checkpoint directory layout is not closed")

    for relative, checksum in checksum_by_path.items():
        try:
            payload_path = sandbox.resolve_relative(relative, must_exist=True)
        except PathContainmentError as error:
            raise DeepSpeedCheckpointError(f"unsafe DeepSpeed payload: {relative}") from error
        payload = payload_by_path[relative]
        size = payload_path.stat().st_size
        digest = sha256_file(payload_path)
        if size != checksum.size_bytes or size != payload.size_bytes:
            raise DeepSpeedCheckpointError(f"DeepSpeed payload size mismatch: {relative}")
        if digest != checksum.sha256 or digest != payload.sha256:
            raise DeepSpeedCheckpointError(f"DeepSpeed payload checksum mismatch: {relative}")
    try:
        latest = (checkpoint / "latest").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as error:
        raise DeepSpeedCheckpointError("DeepSpeed latest tag cannot be read") from error
    if latest != manifest.checkpoint_tag:
        raise DeepSpeedCheckpointError("DeepSpeed latest tag differs from manifest")

    return ValidatedDeepSpeedCheckpoint(
        path=checkpoint,
        manifest=manifest,
        checksums=checksums,
        inventory=tuple(sorted(actual_files)),
        logical_bytes=logical_directory_bytes(checkpoint),
    )
