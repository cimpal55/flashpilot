"""Hash-only observations used across worker process boundaries."""

from flashpilot.checkpoints.strategies import capture_rng_state
from flashpilot.domain.recovery import RngStateDigests, RuntimeSnapshot
from flashpilot.workload.state import ControlRunSummary, state_digest
from flashpilot.workload.trainer import TrainingRuntime, summarize_runtime


def snapshot_from_summary(summary: ControlRunSummary) -> RuntimeSnapshot:
    return RuntimeSnapshot(
        global_step=summary.final_global_step,
        loss_history=summary.loss_history,
        trainable_state_sha256=summary.trainable_state.sha256,
        evaluation_sha256=summary.evaluation.sha256,
        optimizer_sha256=summary.optimizer.sha256,
        scheduler_sha256=summary.scheduler.sha256,
    )


def observe_runtime(runtime: TrainingRuntime) -> RuntimeSnapshot:
    return snapshot_from_summary(summarize_runtime(runtime))


def observe_rng_state() -> RngStateDigests:
    state = capture_rng_state()
    return RngStateDigests(
        python_sha256=state_digest(state["python"]),
        numpy_sha256=state_digest(state["numpy"]),
        torch_sha256=state_digest(state["torch"]),
    )
