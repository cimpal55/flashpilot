import json
from pathlib import Path

import pytest

from flashpilot.checkpoints.loader import (
    CheckpointValidationError,
    latest_valid_checkpoint,
    validate_checkpoint,
)
from flashpilot.checkpoints.strategies import save_safe_full
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import create_training_runtime, train_until
from tests.conftest import SafeFullFixture


def test_corrupted_payload_is_rejected(safe_full_fixture: SafeFullFixture) -> None:
    model_path = safe_full_fixture.commit.checkpoint_path / "model.pt"
    with model_path.open("r+b") as stream:
        first_byte = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first_byte[0] ^ 0xFF]))

    with pytest.raises(CheckpointValidationError, match="checksum mismatch"):
        validate_checkpoint(
            run_root=safe_full_fixture.run_root,
            checkpoint_path=safe_full_fixture.commit.checkpoint_path,
        )


def test_missing_completion_marker_is_rejected(safe_full_fixture: SafeFullFixture) -> None:
    (safe_full_fixture.commit.checkpoint_path / "COMPLETE").unlink()

    with pytest.raises(CheckpointValidationError, match="metadata"):
        validate_checkpoint(
            run_root=safe_full_fixture.run_root,
            checkpoint_path=safe_full_fixture.commit.checkpoint_path,
        )


def test_manifest_path_traversal_is_rejected(safe_full_fixture: SafeFullFixture) -> None:
    manifest_path = safe_full_fixture.commit.checkpoint_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["payloads"][0]["path"] = "../outside.pt"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(CheckpointValidationError, match="metadata"):
        validate_checkpoint(
            run_root=safe_full_fixture.run_root,
            checkpoint_path=safe_full_fixture.commit.checkpoint_path,
        )


def test_latest_valid_ignores_incomplete_temp_directory(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    first = save_safe_full(runtime, run_root=run_root)
    incomplete = run_root / "checkpoints" / ".checkpoint-step-000003.tmp-incomplete"
    incomplete.mkdir()
    (incomplete / "model.pt").write_bytes(b"incomplete")

    latest = latest_valid_checkpoint(
        run_root=run_root,
        checkpoint_root=run_root / "checkpoints",
    )

    assert latest is not None
    assert latest.path == first.checkpoint_path


def test_latest_valid_selects_highest_valid_step(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    save_safe_full(runtime, run_root=run_root)
    train_until(runtime, 4)
    expected = save_safe_full(runtime, run_root=run_root)

    latest = latest_valid_checkpoint(
        run_root=run_root,
        checkpoint_root=run_root / "checkpoints",
    )

    assert latest is not None
    assert latest.path == expected.checkpoint_path


def test_latest_valid_falls_back_from_corrupted_newer_checkpoint(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    expected = save_safe_full(runtime, run_root=run_root)
    train_until(runtime, 4)
    corrupted = save_safe_full(runtime, run_root=run_root)
    model_path = corrupted.checkpoint_path / "model.pt"
    with model_path.open("r+b") as stream:
        first_byte = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first_byte[0] ^ 0xFF]))

    latest = latest_valid_checkpoint(
        run_root=run_root,
        checkpoint_root=run_root / "checkpoints",
    )

    assert latest is not None
    assert latest.path == expected.checkpoint_path


def test_checkpoint_outside_run_root_is_rejected(
    tmp_path: Path,
    safe_full_fixture: SafeFullFixture,
) -> None:
    with pytest.raises(CheckpointValidationError, match="containment"):
        validate_checkpoint(
            run_root=tmp_path / "different-run",
            checkpoint_path=safe_full_fixture.commit.checkpoint_path,
        )
