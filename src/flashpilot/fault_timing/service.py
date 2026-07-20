"""Repeated seeded native process-kill timing qualification."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from flashpilot.checkpoints.integrity import directory_content_fingerprint, sha256_file
from flashpilot.domain.recovery import CrashExperimentResult
from flashpilot.fault_timing.models import (
    FaultTimingScheduleEntry,
    FaultTimingTrialResult,
    RandomizedFaultTimingResult,
)
from flashpilot.fault_timing.reporting import (
    render_timing_job_summary,
    render_timing_junit,
    render_timing_markdown,
)
from flashpilot.fault_timing.schedule import (
    MAX_RPO_STEPS,
    build_fault_timing_schedule,
    schedule_sha256,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.orchestration.experiment import run_crash_recovery_experiment
from flashpilot.security.paths import PathContainmentError, PathSandbox

DEFAULT_TIMING_SEED = 20_260_720
DEFAULT_TIMING_ITERATIONS = 8


class RandomizedFaultTimingError(RuntimeError):
    """Repeated fault timing could not produce or verify trustworthy evidence."""


def _trial_from_experiment(
    *,
    root: Path,
    schedule: FaultTimingScheduleEntry,
    experiment: CrashExperimentResult,
) -> FaultTimingTrialResult:
    trial_relative = f"trials/trial-{schedule.iteration:04d}"
    trial_root = PathSandbox.create(root).resolve_relative(trial_relative, must_exist=True)
    result_path = trial_root / "result.json"
    fingerprint = directory_content_fingerprint(trial_root)
    rto = (
        experiment.recovery_process.completed_at - experiment.recovery_process.started_at
    ).total_seconds()
    checks_passed = sum(check.status != "fail" for check in experiment.gate.checks)
    exact_match = experiment.recovery.final == experiment.control
    passed = (
        experiment.crash.termination_verified
        and experiment.crash.termination_exit_code != 0
        and experiment.recovery_process.exit_verified
        and experiment.recovery_process.exit_code == 0
        and len(experiment.gate.checks) == 24
        and checks_passed == 24
        and not experiment.gate.failed_check_ids
        and experiment.gate.achieved_rollback_steps == schedule.post_commit_steps
        and experiment.gate.hard_rollback_limit_steps == MAX_RPO_STEPS
        and experiment.gate.comparison_policy.mode == "exact"
        and experiment.gate.comparison_policy.atol == 0.0
        and experiment.gate.comparison_policy.rtol == 0.0
        and exact_match
    )
    return FaultTimingTrialResult(
        schedule=schedule,
        trial_path=trial_relative,
        trial_result_path=f"{trial_relative}/result.json",
        trial_result_sha256=sha256_file(result_path),
        trial_directory_sha256=fingerprint.sha256,
        trial_file_count=fingerprint.file_count,
        producer_pid=experiment.crash.worker_pid,
        producer_exit_code=experiment.crash.termination_exit_code,
        producer_termination_verified=experiment.crash.termination_verified,
        recovery_pid=experiment.recovery.worker_pid,
        recovery_exit_code=experiment.recovery_process.exit_code,
        recovery_exit_verified=experiment.recovery_process.exit_verified,
        gate_checks_passed=checks_passed,
        failed_gate_check_ids=experiment.gate.failed_check_ids,
        achieved_rpo_steps=experiment.gate.achieved_rollback_steps,
        rto_seconds=rto,
        exact_control_match=exact_match,
        passed=passed,
    )


def _load_experiment(path: Path) -> CrashExperimentResult:
    try:
        return CrashExperimentResult.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise RandomizedFaultTimingError("randomized timing trial result is invalid") from error


def verify_randomized_fault_timing(run_root: Path) -> RandomizedFaultTimingResult:
    """Revalidate the aggregate schedule and every closed trial directory."""

    root = PathSandbox.create(run_root).root
    aggregate_path = root / "result.json"
    if not aggregate_path.is_file() or aggregate_path.is_symlink():
        raise RandomizedFaultTimingError("randomized timing aggregate is missing or unsafe")
    try:
        aggregate = RandomizedFaultTimingResult.model_validate_json(
            aggregate_path.read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise RandomizedFaultTimingError("randomized timing aggregate is invalid") from error
    expected_schedule = build_fault_timing_schedule(
        iterations=aggregate.iterations,
        seed=aggregate.seed,
    )
    if tuple(trial.schedule for trial in aggregate.trials) != expected_schedule:
        raise RandomizedFaultTimingError("persisted trial schedule differs from its seed")
    if aggregate.schedule_sha256 != schedule_sha256(expected_schedule, seed=aggregate.seed):
        raise RandomizedFaultTimingError("randomized timing schedule hash mismatch")
    for trial in aggregate.trials:
        try:
            trial_root = PathSandbox.create(root).resolve_relative(
                trial.trial_path,
                must_exist=True,
            )
            trial_result_path = PathSandbox.create(root).resolve_relative(
                trial.trial_result_path,
                must_exist=True,
            )
        except PathContainmentError as error:
            raise RandomizedFaultTimingError("trial evidence path is missing or unsafe") from error
        fingerprint = directory_content_fingerprint(trial_root)
        if (
            fingerprint.sha256 != trial.trial_directory_sha256
            or fingerprint.file_count != trial.trial_file_count
        ):
            raise RandomizedFaultTimingError("trial directory fingerprint mismatch")
        if sha256_file(trial_result_path) != trial.trial_result_sha256:
            raise RandomizedFaultTimingError("trial result SHA-256 mismatch")
        experiment = _load_experiment(trial_result_path)
        schedule = trial.schedule
        rto = (
            experiment.recovery_process.completed_at - experiment.recovery_process.started_at
        ).total_seconds()
        expected = {
            "run_id": Path(trial.trial_path).name,
            "checkpoint_step": schedule.checkpoint_step,
            "fault_after_step": schedule.fault_after_step,
            "producer_pid": trial.producer_pid,
            "producer_exit": trial.producer_exit_code,
            "producer_termination_verified": trial.producer_termination_verified,
            "recovery_pid": trial.recovery_pid,
            "recovery_exit": trial.recovery_exit_code,
            "recovery_exit_verified": trial.recovery_exit_verified,
            "gate_checks": trial.gate_checks_total,
            "gate_passes": trial.gate_checks_passed,
            "failed_checks": trial.failed_gate_check_ids,
            "rpo": trial.achieved_rpo_steps,
            "max_rpo": trial.max_rpo_steps,
            "rto": trial.rto_seconds,
            "exact": trial.exact_control_match,
            "comparison_mode": "exact",
            "atol": 0.0,
            "rtol": 0.0,
        }
        actual = {
            "run_id": experiment.run_id,
            "checkpoint_step": experiment.crash.checkpoint_step,
            "fault_after_step": experiment.crash.last_completed_step,
            "producer_pid": experiment.crash.worker_pid,
            "producer_exit": experiment.crash.termination_exit_code,
            "producer_termination_verified": experiment.crash.termination_verified,
            "recovery_pid": experiment.recovery.worker_pid,
            "recovery_exit": experiment.recovery_process.exit_code,
            "recovery_exit_verified": experiment.recovery_process.exit_verified,
            "gate_checks": len(experiment.gate.checks),
            "gate_passes": sum(check.status != "fail" for check in experiment.gate.checks),
            "failed_checks": experiment.gate.failed_check_ids,
            "rpo": experiment.gate.achieved_rollback_steps,
            "max_rpo": experiment.gate.hard_rollback_limit_steps,
            "rto": rto,
            "exact": experiment.recovery.final == experiment.control,
            "comparison_mode": experiment.gate.comparison_policy.mode,
            "atol": experiment.gate.comparison_policy.atol,
            "rtol": experiment.gate.comparison_policy.rtol,
        }
        if actual != expected or experiment.profile != "ci" or experiment.strategy != "safe_full":
            raise RandomizedFaultTimingError(
                "trial aggregate differs from full experiment evidence"
            )
        if (trial_root / "recovery.attestation.json").exists():
            raise RandomizedFaultTimingError("timing trial unexpectedly contains an attestation")
    return aggregate


def run_randomized_fault_timing(
    *,
    run_root: Path,
    iterations: int = DEFAULT_TIMING_ITERATIONS,
    seed: int = DEFAULT_TIMING_SEED,
    timeout_seconds: float = 60.0,
) -> RandomizedFaultTimingResult:
    """Run every seeded process-kill trial and verify its aggregate evidence."""

    if timeout_seconds <= 0:
        raise ValueError("randomized timing timeout must be positive")
    schedule = build_fault_timing_schedule(iterations=iterations, seed=seed)
    if run_root.exists() and (not run_root.is_dir() or any(run_root.iterdir())):
        raise RandomizedFaultTimingError("randomized timing requires a new or empty run root")
    run_root.mkdir(parents=True, exist_ok=True)
    root = PathSandbox.create(run_root.resolve()).root
    trials = []
    try:
        for entry in schedule:
            trial_root = root / f"trials/trial-{entry.iteration:04d}"
            experiment = run_crash_recovery_experiment(
                profile_name="ci",
                strategy="safe_full",
                run_root=trial_root,
                checkpoint_step=entry.checkpoint_step,
                post_commit_steps=entry.post_commit_steps,
                hard_rollback_limit_steps=MAX_RPO_STEPS,
                timeout_seconds=timeout_seconds,
            )
            trials.append(
                _trial_from_experiment(
                    root=root,
                    schedule=entry,
                    experiment=experiment,
                )
            )
    except (OSError, RuntimeError, ValueError) as error:
        raise RandomizedFaultTimingError("randomized timing trial failed closed") from error
    passed = sum(trial.passed for trial in trials)
    failed = iterations - passed
    result = RandomizedFaultTimingResult(
        seed=seed,
        iterations=iterations,
        schedule_sha256=schedule_sha256(schedule, seed=seed),
        trials=tuple(trials),
        observed_rpo_steps=tuple(sorted({trial.achieved_rpo_steps for trial in trials})),
        unique_timing_pairs=len(
            {(trial.schedule.checkpoint_step, trial.schedule.post_commit_steps) for trial in trials}
        ),
        passed_trials=passed,
        failed_trials=failed,
        recovery_verified=failed == 0,
        final_verdict="VERIFIED" if failed == 0 else "FAILED",
        limitations=(
            "Trials use the fixed local native-PyTorch CI workload and safe_full strategy.",
            "The seeded schedule randomizes completed-step boundaries, not mid-instruction timing.",
            "The fixed policy allows at most three completed post-checkpoint steps of RPO.",
            "No storage byte metric, storage-savings claim, GPT call, repair, or attestation is emitted.",
        ),
    )
    write_json_artifact(run_root=root, relative_path=result.result_path, value=result)
    verified = verify_randomized_fault_timing(root)
    write_text_artifact(
        run_root=root,
        relative_path=result.report_path,
        text=render_timing_markdown(verified),
    )
    write_text_artifact(
        run_root=root,
        relative_path=result.junit_path,
        text=render_timing_junit(verified),
    )
    write_text_artifact(
        run_root=root,
        relative_path=result.job_summary_path,
        text=render_timing_job_summary(verified),
    )
    return verified


def load_randomized_fault_timing(path: Path) -> RandomizedFaultTimingResult:
    try:
        return RandomizedFaultTimingResult.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
        raise RandomizedFaultTimingError("randomized timing result is invalid") from error
