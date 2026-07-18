"""Map validated P0 actions to explicit strategy fields exactly once."""

from __future__ import annotations

from pathlib import Path

from flashpilot.agent.guardrails import admit_single_repair_attempt
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS, RepairPlanValidationResult
from flashpilot.domain.repair import (
    REPAIR_ACTION_TO_FIELD,
    CheckpointStrategyConfig,
    RepairExecutionResult,
)
from flashpilot.orchestration.artifacts import write_json_artifact

INITIAL_INCOMPLETE_CONFIG = CheckpointStrategyConfig(
    strategy_id="native-incomplete-v1",
    include_optimizer=False,
    include_scheduler=False,
    include_python_rng=False,
    include_numpy_rng=False,
    include_torch_rng=False,
    restore_before_next_batch=False,
)

REPAIRED_STRATEGY_ID = "native-repaired-complete-v1"


class RepairExecutionError(RuntimeError):
    """Raised when a validated plan cannot be represented by the bounded executor."""


def execute_bounded_repair(
    *,
    validation: RepairPlanValidationResult,
    run_root: Path,
    original_config: CheckpointStrategyConfig = INITIAL_INCOMPLETE_CONFIG,
) -> RepairExecutionResult:
    """Apply the exact six supported actions to copied typed configuration fields."""

    if validation.accepted_actions != NATIVE_PYTORCH_REPAIR_ACTIONS:
        raise RepairExecutionError(
            "the primary repair requires exactly the six NativePyTorchAdapter actions"
        )
    unknown = tuple(
        action for action in validation.accepted_actions if action not in REPAIR_ACTION_TO_FIELD
    )
    if unknown:
        raise RepairExecutionError(f"accepted actions are not executable in P0: {unknown}")

    admission = admit_single_repair_attempt(run_root=run_root)
    updates: dict[str, bool | str] = {"strategy_id": REPAIRED_STRATEGY_ID}
    for action in validation.accepted_actions:
        updates[REPAIR_ACTION_TO_FIELD[action]] = True
    repaired_config = original_config.model_copy(update=updates)
    repaired_config.require_complete_training_state()
    result = RepairExecutionResult(
        admitted_at=admission.admitted_at,
        original_config=original_config,
        repaired_config=repaired_config,
        applied_actions=validation.accepted_actions,
        unsupported_actions=validation.unsupported_actions,
        rejected_actions=validation.rejected_actions,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path="agent/repair/repaired-strategy.json",
        value=repaired_config,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path="agent/repair/execution.json",
        value=result,
    )
    return result
