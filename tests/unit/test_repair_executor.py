from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.agent.fixture_provider import FixtureFailureProvider
from flashpilot.agent.guardrails import (
    RepairAttemptLimitError,
    validate_failure_analysis,
)
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS
from flashpilot.domain.repair import CheckpointStrategyConfig
from flashpilot.repair.executor import execute_bounded_repair
from tests.unit.test_agent_providers import failure_request


def _accepted_validation():
    request = failure_request()
    analysis = FixtureFailureProvider().analyze_failure(request).output
    return validate_failure_analysis(request, analysis)


def test_executor_maps_only_six_actions_to_explicit_fields(tmp_path: Path) -> None:
    validation = _accepted_validation()
    result = execute_bounded_repair(validation=validation, run_root=tmp_path / "run")

    assert result.applied_actions == NATIVE_PYTORCH_REPAIR_ACTIONS
    assert result.unsupported_actions == ("change_supported_checkpoint_strategy",)
    assert result.rejected_actions == ()
    assert result.repaired_config.strategy_id == "native-repaired-complete-v1"
    assert result.repaired_config.include_optimizer is True
    assert result.repaired_config.include_scheduler is True
    assert result.repaired_config.include_python_rng is True
    assert result.repaired_config.include_numpy_rng is True
    assert result.repaired_config.include_torch_rng is True
    assert result.repaired_config.restore_before_next_batch is True
    assert result.original_config.complete_training_state_enabled is False
    assert result.repaired_config.complete_training_state_enabled is True


def test_executor_refuses_a_second_repair_attempt(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    validation = _accepted_validation()
    execute_bounded_repair(validation=validation, run_root=run_root)

    with pytest.raises(RepairAttemptLimitError, match="one repair attempt"):
        execute_bounded_repair(validation=validation, run_root=run_root)


def test_strategy_config_rejects_model_defined_extra_execution_surface() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        CheckpointStrategyConfig.model_validate(
            {
                "strategy_id": "malformed-strategy",
                "include_optimizer": True,
                "include_scheduler": True,
                "include_python_rng": True,
                "include_numpy_rng": True,
                "include_torch_rng": True,
                "restore_before_next_batch": True,
                "command": "arbitrary model text",
            }
        )
