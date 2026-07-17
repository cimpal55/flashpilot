from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from flashpilot.checkpoints.atomic import AtomicCommitResult
from flashpilot.checkpoints.strategies import save_safe_full
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import TrainingRuntime, create_training_runtime, train_until


def pytest_configure(config: pytest.Config) -> None:
    """Create the ignored parent required by pytest's repository-local basetemp."""

    (config.rootpath / ".pytest-local").mkdir(exist_ok=True)


@dataclass(frozen=True, slots=True)
class SafeFullFixture:
    run_root: Path
    runtime: TrainingRuntime
    commit: AtomicCommitResult


@pytest.fixture
def safe_full_fixture(tmp_path: Path) -> SafeFullFixture:
    run_root = tmp_path / "run"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, CI_PROFILE.steps // 2)
    commit = save_safe_full(runtime, run_root=run_root)
    return SafeFullFixture(run_root=run_root, runtime=runtime, commit=commit)
