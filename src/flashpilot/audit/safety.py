"""Bounded, metadata-first readers shared by static auditors."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import torch

from flashpilot.domain.manifests import validate_managed_relative_path

MAX_JSON_BYTES = 8 * 1024 * 1024
MAX_SAFETENSORS_HEADER_BYTES = 16 * 1024 * 1024


class AuditSafetyError(ValueError):
    """An audit input cannot be inspected through the supported safe readers."""


def require_safe_checkpoint_directory(path: Path) -> Path:
    """Resolve a real directory while rejecting symlink components and entries."""

    lexical = path.absolute()
    if not lexical.exists():
        raise AuditSafetyError("checkpoint path does not exist")
    if lexical.is_symlink() or not lexical.is_dir():
        raise AuditSafetyError("checkpoint path must be a non-symlink directory")
    resolved = lexical.resolve(strict=True)
    current = lexical
    while current != current.parent:
        if current.is_symlink():
            raise AuditSafetyError("checkpoint path contains a symlink component")
        current = current.parent
    try:
        for candidate in resolved.rglob("*"):
            if candidate.is_symlink():
                raise AuditSafetyError("checkpoint contents contain a symlink")
    except OSError as error:
        raise AuditSafetyError("checkpoint contents cannot be enumerated safely") from error
    return resolved


def relative_evidence(path: Path, *, root: Path) -> str:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as error:
        raise AuditSafetyError("evidence path escapes the checkpoint") from error
    return validate_managed_relative_path(relative)


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        if not path.is_file() or path.is_symlink():
            raise AuditSafetyError(f"{path.name} is not a regular metadata file")
        if path.stat().st_size > MAX_JSON_BYTES:
            raise AuditSafetyError(f"{path.name} exceeds the metadata size limit")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditSafetyError(f"{path.name} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise AuditSafetyError(f"{path.name} must contain a JSON object")
    return value


def load_weights_only(path: Path) -> object:
    if not path.is_file() or path.is_symlink():
        raise AuditSafetyError(f"{path.name} is not a regular payload file")
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except Exception as error:
        raise AuditSafetyError(f"{path.name} failed weights-only loading") from error


_DTYPE_BYTES: dict[str, float] = {
    "BOOL": 1,
    "U8": 1,
    "I8": 1,
    "U16": 2,
    "I16": 2,
    "F16": 2,
    "BF16": 2,
    "U32": 4,
    "I32": 4,
    "F32": 4,
    "U64": 8,
    "I64": 8,
    "F64": 8,
    "F8_E4M3": 1,
    "F8_E5M2": 1,
    "I4": 0.5,
    "U4": 0.5,
}


def validate_safetensors_metadata(path: Path) -> int:
    """Validate a safetensors header and offsets without materializing tensors."""

    if not path.is_file() or path.is_symlink():
        raise AuditSafetyError(f"{path.name} is not a regular safetensors file")
    try:
        file_size = path.stat().st_size
        with path.open("rb") as stream:
            header_length_bytes = stream.read(8)
            if len(header_length_bytes) != 8:
                raise AuditSafetyError(f"{path.name} has no complete safetensors header")
            header_length = int.from_bytes(header_length_bytes, "little", signed=False)
            if header_length <= 0 or header_length > MAX_SAFETENSORS_HEADER_BYTES:
                raise AuditSafetyError(f"{path.name} has an invalid safetensors header length")
            if 8 + header_length > file_size:
                raise AuditSafetyError(f"{path.name} has a truncated safetensors header")
            header = json.loads(stream.read(header_length).decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AuditSafetyError(f"{path.name} has invalid safetensors metadata") from error
    if not isinstance(header, dict):
        raise AuditSafetyError(f"{path.name} safetensors metadata must be an object")

    data_size = file_size - 8 - header_length
    ranges: list[tuple[int, int]] = []
    tensor_count = 0
    for name, entry in header.items():
        if name == "__metadata__":
            if not isinstance(entry, dict):
                raise AuditSafetyError(f"{path.name} has invalid safetensors metadata values")
            continue
        if not isinstance(name, str) or not name or not isinstance(entry, dict):
            raise AuditSafetyError(f"{path.name} has an invalid tensor header entry")
        dtype = entry.get("dtype")
        shape = entry.get("shape")
        offsets = entry.get("data_offsets")
        if dtype not in _DTYPE_BYTES:
            raise AuditSafetyError(f"{path.name} uses an unsupported tensor dtype")
        if not isinstance(shape, list) or any(
            not isinstance(size, int) or isinstance(size, bool) or size < 0 for size in shape
        ):
            raise AuditSafetyError(f"{path.name} has an invalid tensor shape")
        if (
            not isinstance(offsets, list)
            or len(offsets) != 2
            or any(not isinstance(value, int) or isinstance(value, bool) for value in offsets)
        ):
            raise AuditSafetyError(f"{path.name} has invalid tensor offsets")
        start, end = offsets
        if start < 0 or end < start or end > data_size:
            raise AuditSafetyError(f"{path.name} tensor offsets escape the data section")
        element_count = math.prod(shape)
        expected_bytes = math.ceil(element_count * _DTYPE_BYTES[dtype])
        if end - start != expected_bytes:
            raise AuditSafetyError(f"{path.name} tensor size does not match its metadata")
        ranges.append((start, end))
        tensor_count += 1
    if tensor_count == 0:
        raise AuditSafetyError(f"{path.name} contains no tensor metadata")
    for previous, current in zip(sorted(ranges), sorted(ranges)[1:], strict=False):
        if current[0] < previous[1]:
            raise AuditSafetyError(f"{path.name} contains overlapping tensor ranges")
    if ranges and max(end for _, end in ranges) != data_size:
        raise AuditSafetyError(f"{path.name} contains unreferenced tensor data")
    return tensor_count


def file_inventory(root: Path) -> tuple[str, ...]:
    try:
        files = [
            relative_evidence(path, root=root)
            for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
        ]
    except OSError as error:
        raise AuditSafetyError("checkpoint file inventory cannot be read") from error
    return tuple(sorted(files))


def reject_output_overlap(*, checkpoint_path: Path, output_dir: Path) -> Path:
    output = output_dir.absolute().resolve(strict=False)
    if output == checkpoint_path or output.is_relative_to(checkpoint_path):
        raise AuditSafetyError("audit output directory must be outside the checkpoint")
    if output.exists() and (output.is_symlink() or not output.is_dir()):
        raise AuditSafetyError("audit output path must be a non-symlink directory")
    if output.exists() and any(output.iterdir()):
        raise AuditSafetyError("audit output directory must be new or empty")
    return output
