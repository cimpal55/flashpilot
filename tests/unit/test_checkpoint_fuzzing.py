from __future__ import annotations

import json
from pathlib import Path

import pytest
import torch
from pydantic import ValidationError

from flashpilot.checkpoints.integrity import directory_content_fingerprint
from flashpilot.domain.manifests import ChecksumEntry
from flashpilot.fuzzing.artifacts import (
    FuzzArtifactError,
    commit_fuzz_artifact,
    validate_fuzz_artifact,
)
from flashpilot.fuzzing.models import (
    FuzzCheckpointManifestV1,
    FuzzRejectionReason,
    FuzzScenario,
    FuzzShardV1,
)
from flashpilot.fuzzing.schema import fuzz_schema_documents
from flashpilot.fuzzing.service import PartialWriteFuzzError, run_partial_write_fuzz

SHA_ZERO = "0" * 64
SHA_ONE = "1" * 64


def _payloads() -> dict[str, bytes]:
    import io

    payloads = {}
    for rank in (0, 1):
        stream = io.BytesIO()
        torch.save({"rank": rank, "tensor": torch.arange(4)}, stream)
        payloads[f"rank-{rank:03d}.pt"] = stream.getvalue()
    return payloads


def test_fuzz_manifest_rejects_duplicate_rank_metadata() -> None:
    with pytest.raises(ValidationError, match="ranks 0 and 1"):
        FuzzCheckpointManifestV1(
            checkpoint_id="checkpoint-0001",
            iteration=1,
            global_step=1,
            shards=(
                FuzzShardV1(
                    rank=0,
                    path="rank-000.pt",
                    sha256=SHA_ZERO,
                    size_bytes=1,
                ),
                FuzzShardV1(
                    rank=0,
                    path="rank-001.pt",
                    sha256=SHA_ONE,
                    size_bytes=1,
                ),
            ),
        )


def test_atomic_fuzz_source_is_complete_valid_and_immutable(tmp_path: Path) -> None:
    commit = commit_fuzz_artifact(
        run_root=tmp_path,
        iteration=1,
        payloads=_payloads(),
    )
    before = directory_content_fingerprint(commit.path)
    validated = validate_fuzz_artifact(commit.path)
    after = directory_content_fingerprint(commit.path)

    assert validated.manifest.iteration == 1
    assert (commit.path / "COMPLETE").is_file()
    assert commit.atomic_rename_succeeded is True
    assert commit.payload_files_fsynced is True
    assert commit.metadata_files_fsynced is True
    assert before == after == commit.fingerprint


def test_atomic_fuzz_source_rejects_rank_content_mismatch(tmp_path: Path) -> None:
    payloads = _payloads()
    payloads["rank-001.pt"] = payloads["rank-000.pt"]

    with pytest.raises(FuzzArtifactError) as captured:
        commit_fuzz_artifact(
            run_root=tmp_path,
            iteration=1,
            payloads=payloads,
        )

    assert captured.value.reason is FuzzRejectionReason.PAYLOAD_INVALID
    assert not (tmp_path / "sources" / "checkpoint-0001").exists()


def test_fuzz_validator_rejects_unmanifested_file(tmp_path: Path) -> None:
    commit = commit_fuzz_artifact(
        run_root=tmp_path,
        iteration=1,
        payloads=_payloads(),
    )
    (commit.path / "unexpected.txt").write_text("not committed\n", encoding="utf-8")

    with pytest.raises(FuzzArtifactError) as captured:
        validate_fuzz_artifact(commit.path)

    assert captured.value.reason is FuzzRejectionReason.INVENTORY_MISMATCH


@pytest.mark.parametrize("iterations", [0, 1001])
def test_fuzz_iterations_are_bounded(tmp_path: Path, iterations: int) -> None:
    with pytest.raises(ValueError, match="between 1 and 1000"):
        run_partial_write_fuzz(run_root=tmp_path / "run", iterations=iterations)


def test_fuzz_output_requires_new_or_empty_directory(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    run_root.mkdir()
    (run_root / "owned.txt").write_text("preserve\n", encoding="utf-8")

    with pytest.raises(PartialWriteFuzzError, match="new or empty"):
        run_partial_write_fuzz(run_root=run_root, iterations=1)

    assert (run_root / "owned.txt").read_text(encoding="utf-8") == "preserve\n"


def test_checked_in_fuzz_schemas_match_strict_models() -> None:
    for filename, expected in fuzz_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


def test_scenario_inventory_is_fixed_and_complete() -> None:
    assert tuple(FuzzScenario) == (
        FuzzScenario.TRUNCATED_PAYLOAD,
        FuzzScenario.MISSING_SHARD,
        FuzzScenario.STALE_MANIFEST,
        FuzzScenario.CHECKSUM_MISMATCH,
        FuzzScenario.DUPLICATE_RANK,
        FuzzScenario.REORDERED_WRITES,
    )
    entry = ChecksumEntry(path="rank-000.pt", sha256=SHA_ZERO, size_bytes=1)
    assert entry.path == "rank-000.pt"
