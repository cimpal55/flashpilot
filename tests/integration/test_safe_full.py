import json
import random
from pathlib import Path

import numpy as np
import torch
from typer.testing import CliRunner

from flashpilot.checkpoints.loader import validate_checkpoint
from flashpilot.checkpoints.strategies import restore_safe_full
from flashpilot.cli import app
from flashpilot.workload.control import run_control
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import summarize_runtime, train_until
from tests.conftest import SafeFullFixture


def test_safe_full_direct_restore_matches_uninterrupted_control(
    safe_full_fixture: SafeFullFixture,
) -> None:
    control = run_control("ci")
    validated = validate_checkpoint(
        run_root=safe_full_fixture.run_root,
        checkpoint_path=safe_full_fixture.commit.checkpoint_path,
    )
    restored = restore_safe_full(
        run_root=safe_full_fixture.run_root,
        checkpoint_path=validated.path,
    )

    assert restored.runtime.global_step == CI_PROFILE.steps // 2
    assert restored.runtime.loss_history == safe_full_fixture.runtime.loss_history
    train_until(restored.runtime, CI_PROFILE.steps)

    assert summarize_runtime(restored.runtime) == control
    assert restored.checkpoint.logical_bytes == safe_full_fixture.commit.logical_bytes_written
    assert restored.duration_seconds > 0


def test_safe_full_restores_python_numpy_and_torch_rng(
    safe_full_fixture: SafeFullFixture,
) -> None:
    expected_python = random.random()
    expected_numpy = float(np.random.random())
    expected_torch = torch.rand(4)

    random.seed(999)
    np.random.seed(999)
    torch.manual_seed(999)
    restore_safe_full(
        run_root=safe_full_fixture.run_root,
        checkpoint_path=safe_full_fixture.commit.checkpoint_path,
    )

    assert random.random() == expected_python
    assert float(np.random.random()) == expected_numpy
    assert torch.equal(torch.rand(4), expected_torch)


def test_control_cli_emits_json() -> None:
    result = CliRunner().invoke(app, ["control", "--profile", "ci"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["final_global_step"] == CI_PROFILE.steps
    assert payload["environment"]["device"] == "cpu"


def test_safe_full_cli_runs_direct_restore_baseline(tmp_path: Path) -> None:
    run_dir = tmp_path / "cli-run"

    result = CliRunner().invoke(
        app,
        ["safe-full", "--profile", "ci", "--run-dir", str(run_dir)],
    )

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["direct_restore_matches_control"] is True
    assert payload["logical_checkpoint_bytes_written"] > 0
    assert payload["checkpoint_duration_seconds"] > 0
    assert payload["restore_duration_seconds"] > 0
    assert "Recovery Gate" in payload["limitations"][0]
