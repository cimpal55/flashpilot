import json
from pathlib import Path

import pytest
import torch

from flashpilot.checkpoints.adapter_strategies import (
    AdapterCheckpointRestoreError,
    restore_missing_training_state,
    restore_safe_adapter_aware,
    save_missing_training_state,
    save_safe_adapter_aware,
)
from flashpilot.checkpoints.base_artifact import BaseArtifactValidationError
from flashpilot.checkpoints.loader import validate_checkpoint
from flashpilot.checkpoints.strategies import save_safe_full
from flashpilot.domain.manifests import MISSING_TRAINING_STATE_OMISSIONS
from flashpilot.workload.control import run_control
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import (
    create_training_runtime,
    summarize_runtime,
    train_until,
)


def _checkpoint_runtime():
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, CI_PROFILE.steps // 2)
    return runtime


def test_safe_adapter_aware_direct_restore_matches_control(tmp_path: Path) -> None:
    run_root = tmp_path / "adapter-run"
    control = run_control("ci")
    runtime = _checkpoint_runtime()
    saved = save_safe_adapter_aware(runtime, run_root=run_root)

    validated = validate_checkpoint(
        run_root=run_root,
        checkpoint_path=saved.checkpoint.checkpoint_path,
    )
    assert validated.manifest.strategy == "safe_adapter_aware"
    assert validated.manifest.base_artifact == saved.base_artifact.reference
    assert (saved.checkpoint.checkpoint_path / "COMPLETE").is_file()
    restored = restore_safe_adapter_aware(
        run_root=run_root,
        checkpoint_path=saved.checkpoint.checkpoint_path,
    )
    train_until(restored.runtime, CI_PROFILE.steps)

    assert summarize_runtime(restored.runtime) == control
    assert restored.duration_seconds > 0


def test_frozen_base_is_stored_once_and_reused(tmp_path: Path) -> None:
    run_root = tmp_path / "base-once"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    first = save_safe_adapter_aware(runtime, run_root=run_root)
    base_mtime = (first.base_artifact.artifact_path / "base.pt").stat().st_mtime_ns
    train_until(runtime, 4)
    second = save_safe_adapter_aware(runtime, run_root=run_root)

    assert first.base_artifact.created is True
    assert second.base_artifact.created is False
    assert second.base_artifact.reference == first.base_artifact.reference
    assert (second.base_artifact.artifact_path / "base.pt").stat().st_mtime_ns == base_mtime
    assert list((run_root / "artifacts").iterdir()) == [first.base_artifact.artifact_path]


def test_frozen_base_cannot_change_within_a_run(tmp_path: Path) -> None:
    run_root = tmp_path / "immutable-base"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, 2)
    save_safe_adapter_aware(runtime, run_root=run_root)
    with torch.no_grad():
        runtime.model.token_embedding.weight.add_(1.0)

    with pytest.raises(BaseArtifactValidationError, match="differs from the immutable"):
        save_safe_adapter_aware(runtime, run_root=run_root)


def test_adapter_checkpoint_is_structurally_smaller_than_safe_full(tmp_path: Path) -> None:
    full_runtime = _checkpoint_runtime()
    full = save_safe_full(full_runtime, run_root=tmp_path / "full")
    adapter_runtime = _checkpoint_runtime()
    adapter = save_safe_adapter_aware(adapter_runtime, run_root=tmp_path / "adapter")

    assert adapter.checkpoint.logical_bytes_written < full.logical_bytes_written
    assert adapter.base_artifact.logical_bytes > 0
    assert (
        adapter.checkpoint.logical_bytes_written + adapter.base_artifact.logical_bytes
        > adapter.checkpoint.logical_bytes_written
    )


def test_missing_training_state_is_valid_loadable_and_diverges(tmp_path: Path) -> None:
    run_root = tmp_path / "missing-state"
    control = run_control("ci")
    runtime = _checkpoint_runtime()
    saved = save_missing_training_state(runtime, run_root=run_root)
    validated = validate_checkpoint(
        run_root=run_root,
        checkpoint_path=saved.checkpoint.checkpoint_path,
    )

    assert validated.manifest.strategy == "missing_training_state"
    assert validated.manifest.omitted_state == MISSING_TRAINING_STATE_OMISSIONS
    assert {payload.role for payload in validated.manifest.payloads} == {"adapter", "state"}
    restored = restore_missing_training_state(
        run_root=run_root,
        checkpoint_path=saved.checkpoint.checkpoint_path,
    )
    assert restored.runtime.global_step == runtime.global_step
    assert restored.runtime.loss_history == runtime.loss_history
    assert restored.runtime.optimizer.state == {}
    for actual, expected in zip(
        restored.runtime.model.adapter.parameters(),
        runtime.model.adapter.parameters(),
        strict=True,
    ):
        assert torch.equal(actual, expected)

    train_until(restored.runtime, CI_PROFILE.steps)
    resumed = summarize_runtime(restored.runtime)

    assert resumed.final_global_step == control.final_global_step
    assert (
        resumed.loss_history[: CI_PROFILE.steps // 2]
        == control.loss_history[: CI_PROFILE.steps // 2]
    )
    assert (
        resumed.loss_history[CI_PROFILE.steps // 2 :]
        != control.loss_history[CI_PROFILE.steps // 2 :]
    )
    assert resumed.trainable_state.sha256 != control.trainable_state.sha256
    assert resumed.evaluation.sha256 != control.evaluation.sha256
    assert resumed.optimizer.sha256 != control.optimizer.sha256
    assert resumed.scheduler.sha256 != control.scheduler.sha256


def test_missing_base_artifact_is_rejected(tmp_path: Path) -> None:
    run_root = tmp_path / "missing-base"
    saved = save_safe_adapter_aware(_checkpoint_runtime(), run_root=run_root)
    (saved.base_artifact.artifact_path / "base.pt").unlink()

    with pytest.raises(AdapterCheckpointRestoreError, match="base validation"):
        restore_safe_adapter_aware(
            run_root=run_root,
            checkpoint_path=saved.checkpoint.checkpoint_path,
        )


def test_wrong_base_hash_is_rejected(tmp_path: Path) -> None:
    run_root = tmp_path / "wrong-base-hash"
    saved = save_safe_adapter_aware(_checkpoint_runtime(), run_root=run_root)
    manifest_path = saved.checkpoint.checkpoint_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["base_artifact"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(AdapterCheckpointRestoreError, match="base validation"):
        restore_safe_adapter_aware(
            run_root=run_root,
            checkpoint_path=saved.checkpoint.checkpoint_path,
        )
