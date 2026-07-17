"""Contained, durable JSON artifacts used by process orchestration."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from flashpilot.checkpoints.atomic import fsync_directory
from flashpilot.security.paths import PathSandbox


def write_json_artifact(
    *,
    run_root: Path,
    relative_path: str,
    value: BaseModel | dict[str, Any],
) -> Path:
    """Atomically write one JSON artifact inside the run sandbox."""

    sandbox = PathSandbox.create(run_root)
    destination = sandbox.resolve_relative(relative_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    parent_sandbox = PathSandbox.create(destination.parent)
    temporary = parent_sandbox.resolve_relative(f".{destination.name}.tmp-{uuid.uuid4().hex}")
    if isinstance(value, BaseModel):
        payload = value.model_dump(mode="json")
    else:
        payload = value
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
        directory_sync = fsync_directory(destination.parent)
        if directory_sync.supported and not directory_sync.succeeded:
            raise OSError(directory_sync.detail)
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination
