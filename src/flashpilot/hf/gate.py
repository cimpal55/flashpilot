"""Deterministic exact-trajectory gate for the HF Trainer qualification."""

from __future__ import annotations

from flashpilot.hf.models import (
    HFCheckpointLifecycleEvidence,
    HFProcessEvidence,
    HFQualificationCheck,
    HFRecoveryGateV1,
    HFRunSummary,
)


def _check(
    check_id: str,
    category: str,
    label: str,
    passed: bool,
    expected: str,
    actual: str,
) -> HFQualificationCheck:
    return HFQualificationCheck(
        check_id=check_id,
        category=category,
        label=label,
        status="pass" if passed else "fail",
        expected=expected,
        actual=actual,
    )


def evaluate_hf_recovery_gate(
    *,
    control: HFRunSummary,
    recovery: HFRunSummary,
    checkpoint: HFCheckpointLifecycleEvidence,
    crash_process: HFProcessEvidence,
    recovery_process: HFProcessEvidence,
    total_steps: int,
) -> HFRecoveryGateV1:
    """Compare all required state and trajectory evidence with zero tolerance."""

    checks = (
        _check(
            "checkpoint.model",
            "checkpoint",
            "Model state is present",
            checkpoint.model_present,
            "present",
            "present" if checkpoint.model_present else "missing",
        ),
        _check(
            "checkpoint.trainer-state",
            "checkpoint",
            "Trainer state is present",
            checkpoint.trainer_state_present,
            "present",
            "present" if checkpoint.trainer_state_present else "missing",
        ),
        _check(
            "checkpoint.optimizer",
            "checkpoint",
            "Optimizer state is present",
            checkpoint.optimizer_present,
            "present",
            "present" if checkpoint.optimizer_present else "missing",
        ),
        _check(
            "checkpoint.scheduler",
            "checkpoint",
            "Scheduler state is present",
            checkpoint.scheduler_present,
            "present",
            "present" if checkpoint.scheduler_present else "missing",
        ),
        _check(
            "checkpoint.rng",
            "checkpoint",
            "RNG state is present",
            checkpoint.rng_state_present,
            "present",
            "present" if checkpoint.rng_state_present else "missing",
        ),
        _check(
            "process.real-termination",
            "process",
            "Checkpoint worker was really terminated",
            crash_process.exit_verified and crash_process.exit_code != 0,
            "verified nonzero exit",
            f"verified={crash_process.exit_verified}, exit={crash_process.exit_code}",
        ),
        _check(
            "process.distinct-recovery",
            "process",
            "Recovery ran in a new process",
            crash_process.worker_pid != recovery_process.worker_pid,
            "distinct PIDs",
            f"{crash_process.worker_pid} -> {recovery_process.worker_pid}",
        ),
        _check(
            "progress.global-step",
            "trajectory",
            "Recovered global step matches control",
            recovery.trainer_global_step == control.trainer_global_step == total_steps,
            str(total_steps),
            str(recovery.trainer_global_step),
        ),
        _check(
            "trajectory.loss-history",
            "trajectory",
            "Loss history exactly matches control",
            recovery.loss_history == control.loss_history,
            "exact control loss history",
            "exact match" if recovery.loss_history == control.loss_history else "different",
        ),
        _check(
            "state.trainable",
            "state",
            "Trainable state digest exactly matches control",
            recovery.trainable_state_sha256 == control.trainable_state_sha256,
            control.trainable_state_sha256,
            recovery.trainable_state_sha256,
        ),
        _check(
            "state.evaluation",
            "state",
            "Evaluation digest exactly matches control",
            recovery.evaluation_sha256 == control.evaluation_sha256,
            control.evaluation_sha256,
            recovery.evaluation_sha256,
        ),
        _check(
            "state.optimizer",
            "state",
            "Optimizer digest exactly matches control",
            recovery.optimizer_sha256 == control.optimizer_sha256,
            control.optimizer_sha256,
            recovery.optimizer_sha256,
        ),
        _check(
            "state.scheduler",
            "state",
            "Scheduler digest exactly matches control",
            recovery.scheduler_sha256 == control.scheduler_sha256,
            control.scheduler_sha256,
            recovery.scheduler_sha256,
        ),
    )
    failed = tuple(check.check_id for check in checks if check.status == "fail")
    return HFRecoveryGateV1(
        passed=not failed,
        checks=checks,
        failed_check_ids=failed,
        achieved_rpo_steps=0,
    )
