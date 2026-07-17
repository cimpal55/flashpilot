"""Containment-safe checkpoint retention with explicit protection."""

from __future__ import annotations

import shutil
from pathlib import Path

from flashpilot.checkpoints.loader import (
    CheckpointValidationError,
    discover_valid_checkpoints,
    validate_checkpoint,
)
from flashpilot.security.paths import PathContainmentError, PathSandbox


class RetentionError(RuntimeError):
    """Raised when a retention request is unsafe or invalid."""


def enforce_retention(
    *,
    run_root: Path,
    checkpoint_root: Path,
    keep_count: int,
    latest_verified_checkpoint: Path | None = None,
) -> tuple[Path, ...]:
    """Delete only excess valid checkpoints while preserving an explicit verified one."""

    if keep_count < 1:
        raise RetentionError("keep_count must be at least one")
    try:
        run_sandbox = PathSandbox.create(run_root)
        resolved_root = run_sandbox.require_contained(checkpoint_root, must_exist=True)
    except PathContainmentError as error:
        raise RetentionError("checkpoint root failed containment") from error

    protected_path: Path | None = None
    if latest_verified_checkpoint is not None:
        try:
            protected = validate_checkpoint(
                run_root=run_root,
                checkpoint_path=latest_verified_checkpoint,
            )
        except CheckpointValidationError as error:
            raise RetentionError("protected checkpoint must be valid and contained") from error
        protected_path = protected.path

    valid = discover_valid_checkpoints(run_root=run_root, checkpoint_root=resolved_root)
    keep = {checkpoint.path for checkpoint in valid[-keep_count:]}
    if protected_path is not None:
        keep.add(protected_path)

    deleted: list[Path] = []
    for checkpoint in valid:
        candidate = checkpoint.path
        if candidate in keep:
            continue
        try:
            contained = run_sandbox.require_contained(candidate, must_exist=True)
        except PathContainmentError as error:
            raise RetentionError("retention candidate failed containment") from error
        if contained.parent != resolved_root or contained.is_symlink():
            raise RetentionError("retention candidate is not a direct checkpoint child")
        shutil.rmtree(contained)
        deleted.append(contained)
    return tuple(deleted)
