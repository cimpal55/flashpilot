from pathlib import Path

import pytest

from flashpilot.checkpoints.retention import RetentionError, enforce_retention
from flashpilot.checkpoints.strategies import save_safe_full
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import create_training_runtime, train_until


def test_retention_preserves_latest_and_explicit_verified_checkpoint(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    runtime = create_training_runtime(CI_PROFILE)
    commits = []
    for step in (2, 4, 6):
        train_until(runtime, step)
        commits.append(save_safe_full(runtime, run_root=run_root))

    deleted = enforce_retention(
        run_root=run_root,
        checkpoint_root=run_root / "checkpoints",
        keep_count=1,
        latest_verified_checkpoint=commits[0].checkpoint_path,
    )

    assert deleted == (commits[1].checkpoint_path,)
    assert commits[0].checkpoint_path.exists()
    assert commits[2].checkpoint_path.exists()


def test_retention_rejects_checkpoint_root_outside_run_root(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    run_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "must-remain.txt"
    sentinel.write_text("preserve", encoding="utf-8")

    with pytest.raises(RetentionError, match="containment"):
        enforce_retention(
            run_root=run_root,
            checkpoint_root=outside,
            keep_count=1,
        )

    assert sentinel.read_text(encoding="utf-8") == "preserve"
