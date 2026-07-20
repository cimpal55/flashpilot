"""Canonical identities and closed evidence inventories for attestations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from flashpilot.attestation.models import STATEMENT_ARTIFACT_PATHS, EvidenceEntry
from flashpilot.checkpoints.integrity import sha256_file


def canonical_model_json(model: BaseModel) -> str:
    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_model_sha256(model: BaseModel) -> str:
    return hashlib.sha256(canonical_model_json(model).encode("utf-8")).hexdigest()


def collect_evidence_entries(root: Path) -> tuple[EvidenceEntry, ...]:
    """Inventory every file except the three circular/derived statement artifacts."""

    if not root.is_dir() or root.is_symlink():
        raise ValueError("evidence root must be a non-symlink directory")
    excluded = set(STATEMENT_ARTIFACT_PATHS)
    entries: list[EvidenceEntry] = []
    for candidate in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        if candidate.is_symlink():
            raise ValueError("evidence inventory refuses symbolic links")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root).as_posix()
        if relative in excluded:
            continue
        entries.append(
            EvidenceEntry(
                path=relative,
                size_bytes=candidate.stat().st_size,
                sha256=sha256_file(candidate),
            )
        )
    if not entries:
        raise ValueError("evidence inventory requires at least one artifact")
    return tuple(entries)
