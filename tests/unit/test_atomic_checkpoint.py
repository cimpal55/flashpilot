import os
from pathlib import Path

import pytest

import flashpilot.checkpoints.atomic as atomic_module
from flashpilot.checkpoints.loader import validate_checkpoint
from flashpilot.checkpoints.strategies import save_safe_full
from tests.conftest import SafeFullFixture


def test_atomic_commit_writes_metadata_and_emits_after_rename(
    tmp_path: Path,
) -> None:
    from flashpilot.workload.profiles import CI_PROFILE
    from flashpilot.workload.trainer import create_training_runtime, train_until

    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    committed_paths: list[Path] = []

    def on_committed(path: Path) -> None:
        assert path.is_dir()
        assert (path / "COMPLETE").is_file()
        committed_paths.append(path)

    result = save_safe_full(runtime, run_root=tmp_path / "run", on_committed=on_committed)

    assert committed_paths == [result.checkpoint_path]
    assert result.logical_bytes_written > 0
    assert result.duration_seconds > 0
    assert result.payload_files_synced is True
    assert result.metadata_files_synced is True
    assert result.atomic_rename_succeeded is True
    assert (
        validate_checkpoint(run_root=tmp_path / "run", checkpoint_path=result.checkpoint_path).path
        == result.checkpoint_path
    )
    if os.name == "nt":
        assert result.temp_directory_sync.supported is False
        assert result.parent_directory_sync.supported is False


def test_no_commit_callback_when_atomic_rename_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from flashpilot.workload.profiles import CI_PROFILE
    from flashpilot.workload.trainer import create_training_runtime, train_until

    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    committed_paths: list[Path] = []

    def fail_rename(source, destination) -> None:
        raise OSError("injected rename failure")

    monkeypatch.setattr(atomic_module.os, "rename", fail_rename)

    with pytest.raises(OSError, match="injected rename failure"):
        save_safe_full(
            runtime,
            run_root=tmp_path / "run",
            on_committed=committed_paths.append,
        )

    assert committed_paths == []
    checkpoint_root = tmp_path / "run" / "checkpoints"
    assert not (checkpoint_root / "checkpoint-step-000002").exists()
    assert list(checkpoint_root.glob(".*.tmp-*")) == []


def test_checkpoint_destination_must_be_unique(safe_full_fixture: SafeFullFixture) -> None:
    with pytest.raises(FileExistsError):
        save_safe_full(safe_full_fixture.runtime, run_root=safe_full_fixture.run_root)
