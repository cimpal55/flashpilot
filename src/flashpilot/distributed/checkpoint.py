"""Atomic, checksum-closed distributed checkpoint metadata and rank state."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from pydantic import ValidationError

from flashpilot.checkpoints.atomic import fsync_directory, fsync_file, write_model_durable
from flashpilot.checkpoints.integrity import logical_directory_bytes, sha256_file
from flashpilot.distributed.models import (
    DistributedCheckpointEvent,
    DistributedCheckpointManifest,
    DistributedCheckpointPayload,
    DistributedRankCheckpointState,
    LinearSchedulerState,
    NumPyRngState,
    PythonRngState,
    TorchRngState,
)
from flashpilot.domain.manifests import ChecksumDocument, ChecksumEntry, CompletionMarker
from flashpilot.security.paths import PathContainmentError, PathSandbox


class DistributedCheckpointError(RuntimeError):
    """Distributed checkpoint metadata is incomplete, corrupt, or unsafe."""


@dataclass(frozen=True, slots=True)
class ValidatedDistributedCheckpoint:
    path: Path
    manifest: DistributedCheckpointManifest
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
        raise DistributedCheckpointError("LinearLR scheduler state shape changed unexpectedly")
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


def _scheduler_dict(state: LinearSchedulerState) -> dict[str, object]:
    return {
        "start_factor": state.start_factor,
        "end_factor": state.end_factor,
        "total_iters": state.total_iters,
        "base_lrs": list(state.base_lrs),
        "last_epoch": state.last_epoch,
        "_step_count": state.step_count,
        "_is_initial": state.is_initial,
        "_get_lr_called_within_step": state.get_lr_called_within_step,
        "_last_lr": list(state.last_lrs),
    }


def capture_rank_checkpoint_state(
    *,
    rank: int,
    global_step: int,
    loss_history: tuple[float, ...],
    scheduler: torch.optim.lr_scheduler.LinearLR,
) -> DistributedRankCheckpointState:
    python_state = random.getstate()
    numpy_state = np.random.get_state()
    torch_state = torch.get_rng_state()
    return DistributedRankCheckpointState(
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


def restore_rank_checkpoint_state(
    *,
    state: DistributedRankCheckpointState,
    scheduler: torch.optim.lr_scheduler.LinearLR,
) -> None:
    scheduler.load_state_dict(_scheduler_dict(state.scheduler))
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


def write_rank_checkpoint_state(path: Path, state: DistributedRankCheckpointState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_model_durable(path, state)


def read_rank_checkpoint_state(
    *, run_root: Path, checkpoint_path: Path, rank: int
) -> DistributedRankCheckpointState:
    try:
        checkpoint = PathSandbox.create(run_root).require_contained(
            checkpoint_path, must_exist=True
        )
        path = PathSandbox.create(checkpoint).resolve_relative(
            f"rank-state-{rank:03d}.json", must_exist=True
        )
        state = DistributedRankCheckpointState.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, PathContainmentError) as error:
        raise DistributedCheckpointError(f"invalid checkpoint state for rank {rank}") from error
    if state.rank != rank:
        raise DistributedCheckpointError("rank checkpoint state identity mismatch")
    return state


def _payload_role(relative: str) -> tuple[str, int | None]:
    if relative == "dcp/.metadata":
        return "dcp-metadata", None
    if relative.startswith("dcp/") and relative.endswith(".distcp"):
        return "dcp-shard", None
    if relative in {"rank-state-000.json", "rank-state-001.json"}:
        return "rank-state", int(relative[11:14])
    raise DistributedCheckpointError(f"unexpected distributed checkpoint payload: {relative}")


def finalize_distributed_checkpoint(
    *,
    run_root: Path,
    temporary_checkpoint_path: Path,
    final_checkpoint_path: Path,
    checkpoint_id: str,
    global_step: int,
    writer_pid: int,
    save_started_at: float,
) -> DistributedCheckpointEvent:
    """Checksum and atomically rename a complete multi-rank DCP checkpoint."""

    sandbox = PathSandbox.create(run_root)
    try:
        temporary = sandbox.require_contained(temporary_checkpoint_path, must_exist=True)
        final = sandbox.require_contained(final_checkpoint_path)
    except PathContainmentError as error:
        raise DistributedCheckpointError(
            "distributed checkpoint path failed containment"
        ) from error
    if temporary.is_symlink() or not temporary.is_dir():
        raise DistributedCheckpointError("temporary distributed checkpoint must be a directory")
    if final.exists() or final.name != checkpoint_id or temporary.parent != final.parent:
        raise DistributedCheckpointError("distributed checkpoint destination is invalid")

    entries: list[ChecksumEntry] = []
    payloads: list[DistributedCheckpointPayload] = []
    for candidate in sorted(
        temporary.rglob("*"), key=lambda path: path.relative_to(temporary).as_posix()
    ):
        if candidate.is_symlink():
            raise DistributedCheckpointError("distributed checkpoint refuses symbolic links")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(temporary).as_posix()
        role, rank = _payload_role(relative)
        fsync_file(candidate)
        digest = sha256_file(candidate)
        size = candidate.stat().st_size
        entries.append(ChecksumEntry(path=relative, sha256=digest, size_bytes=size))
        payloads.append(
            DistributedCheckpointPayload(
                role=role,
                path=relative,
                sha256=digest,
                size_bytes=size,
                rank=rank,
            )
        )

    checksums = ChecksumDocument(files=tuple(entries))
    manifest = DistributedCheckpointManifest(
        checkpoint_id=checkpoint_id,
        global_step=global_step,
        created_at=datetime.now(UTC),
        payloads=tuple(payloads),
    )
    write_model_durable(temporary / "checksums.json", checksums)
    write_model_durable(temporary / "manifest.json", manifest)
    write_model_durable(temporary / "COMPLETE", CompletionMarker(checkpoint_id=checkpoint_id))
    temporary_sync = fsync_directory(temporary)
    if temporary_sync.supported and not temporary_sync.succeeded:
        raise DistributedCheckpointError(temporary_sync.detail)
    os.rename(temporary, final)
    parent_sync = fsync_directory(final.parent)
    if parent_sync.supported and not parent_sync.succeeded:
        raise DistributedCheckpointError(parent_sync.detail)
    return DistributedCheckpointEvent(
        writer_pid=writer_pid,
        checkpoint_path=final.relative_to(sandbox.root).as_posix(),
        global_step=global_step,
        commit_duration_seconds=time.perf_counter() - save_started_at,
        logical_bytes=logical_directory_bytes(final),
        directory_fsync_supported=temporary_sync.supported and parent_sync.supported,
        directory_fsync_succeeded=temporary_sync.succeeded and parent_sync.succeeded,
        emitted_at=datetime.now(UTC),
    )


def _read_model(path: Path, model_type: type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise DistributedCheckpointError(f"invalid distributed metadata: {path.name}") from error


def validate_distributed_checkpoint(
    *, run_root: Path, checkpoint_path: Path
) -> ValidatedDistributedCheckpoint:
    """Validate marker, strict manifest, closed inventory, sizes, and SHA-256."""

    try:
        checkpoint = PathSandbox.create(run_root).require_contained(
            checkpoint_path, must_exist=True
        )
    except PathContainmentError as error:
        raise DistributedCheckpointError("distributed checkpoint failed containment") from error
    if checkpoint.is_symlink() or not checkpoint.is_dir() or checkpoint.name.startswith("."):
        raise DistributedCheckpointError("distributed checkpoint must be a final directory")
    sandbox = PathSandbox.create(checkpoint)
    try:
        marker = _read_model(
            sandbox.resolve_relative("COMPLETE", must_exist=True), CompletionMarker
        )
        manifest = _read_model(
            sandbox.resolve_relative("manifest.json", must_exist=True),
            DistributedCheckpointManifest,
        )
        checksums = _read_model(
            sandbox.resolve_relative("checksums.json", must_exist=True), ChecksumDocument
        )
    except PathContainmentError as error:
        raise DistributedCheckpointError("distributed checkpoint metadata is missing") from error
    if marker.checkpoint_id != manifest.checkpoint_id or manifest.checkpoint_id != checkpoint.name:
        raise DistributedCheckpointError("distributed checkpoint identity mismatch")

    checksum_by_path = {entry.path: entry for entry in checksums.files}
    payload_by_path = {payload.path: payload for payload in manifest.payloads}
    if checksum_by_path.keys() != payload_by_path.keys():
        raise DistributedCheckpointError("distributed manifest and checksums differ")
    expected_files = set(checksum_by_path) | {"COMPLETE", "checksums.json", "manifest.json"}
    actual_files: set[str] = set()
    for candidate in checkpoint.rglob("*"):
        if candidate.is_symlink():
            raise DistributedCheckpointError("distributed checkpoint contains a symbolic link")
        if candidate.is_file():
            actual_files.add(candidate.relative_to(checkpoint).as_posix())
    if actual_files != expected_files:
        raise DistributedCheckpointError("distributed checkpoint inventory is not closed")

    for relative, checksum in checksum_by_path.items():
        try:
            payload_path = sandbox.resolve_relative(relative, must_exist=True)
        except PathContainmentError as error:
            raise DistributedCheckpointError(f"unsafe distributed payload: {relative}") from error
        payload = payload_by_path[relative]
        size = payload_path.stat().st_size
        digest = sha256_file(payload_path)
        if size != checksum.size_bytes or size != payload.size_bytes:
            raise DistributedCheckpointError(f"distributed payload size mismatch: {relative}")
        if digest != checksum.sha256 or digest != payload.sha256:
            raise DistributedCheckpointError(f"distributed payload checksum mismatch: {relative}")

    return ValidatedDistributedCheckpoint(
        path=checkpoint,
        manifest=manifest,
        checksums=checksums,
        inventory=tuple(sorted(actual_files)),
        logical_bytes=logical_directory_bytes(checkpoint),
    )
