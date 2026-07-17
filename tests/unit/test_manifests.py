from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from flashpilot.domain.manifests import (
    SAFE_FULL_PAYLOADS,
    SAFE_FULL_SERIALIZED_STATE,
    CheckpointManifest,
    ChecksumDocument,
    ChecksumEntry,
    ManifestPayload,
)

_SHA256 = "a" * 64


@pytest.mark.parametrize(
    "unsafe_path",
    ["../model.pt", "nested/../../model.pt", "/absolute/model.pt", "C:/model.pt", "./model.pt"],
)
def test_checksum_entry_rejects_unsafe_managed_paths(unsafe_path: str) -> None:
    with pytest.raises(ValidationError):
        ChecksumEntry(path=unsafe_path, sha256=_SHA256, size_bytes=1)


def test_checksum_document_rejects_duplicate_paths() -> None:
    entry = ChecksumEntry(path="model.pt", sha256=_SHA256, size_bytes=1)

    with pytest.raises(ValidationError, match="unique"):
        ChecksumDocument(files=(entry, entry))


def test_safe_full_manifest_requires_every_payload_role() -> None:
    payloads = tuple(
        ManifestPayload(role=role, path=path, sha256=_SHA256, size_bytes=1)
        for role, path in SAFE_FULL_PAYLOADS.items()
        if role != "rng"
    )

    with pytest.raises(ValidationError, match="incomplete"):
        CheckpointManifest(
            checkpoint_id="checkpoint-step-000004",
            profile="ci",
            global_step=4,
            created_at=datetime.now(UTC),
            serialized_state=SAFE_FULL_SERIALIZED_STATE,
            payloads=payloads,
        )
