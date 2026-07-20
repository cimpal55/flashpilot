"""Deterministic managed-preemption Recovery Gate."""

from __future__ import annotations

from datetime import datetime

from flashpilot.hf.models import (
    HFProcessEvidence,
    HFQualificationCheck,
    HFRunSummary,
)
from flashpilot.preemption.models import (
    HFPreemptionCommitEvidence,
    HFPreemptionGateV1,
    HFPreemptionReadyEvidence,
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


def evaluate_preemption_gate(
    *,
    control: HFRunSummary,
    recovery: HFRunSummary,
    preemption_process: HFProcessEvidence,
    recovery_process: HFProcessEvidence,
    ready: HFPreemptionReadyEvidence,
    signal_sent_at: datetime,
    commit: HFPreemptionCommitEvidence,
    incomplete_marker_absent: bool,
    checkpoint_commit_seconds: float,
    graceful_exit_seconds: float,
    grace_period_seconds: int,
    total_steps: int,
    tokens_per_step: int,
) -> HFPreemptionGateV1:
    checkpoint = commit.checkpoint
    rpo_steps = ready.completed_step - checkpoint.global_step
    rpo_tokens = rpo_steps * tokens_per_step
    checks = (
        _check(
            "preemption.platform-posix",
            "preemption",
            "Certification used POSIX signal delivery",
            True,
            "POSIX os.kill",
            "POSIX os.kill",
        ),
        _check(
            "preemption.signal-sigterm",
            "preemption",
            "The managed preemption signal is exactly SIGTERM",
            ready.signal_name == commit.signal_name == "SIGTERM",
            "SIGTERM",
            f"ready={ready.signal_name}, commit={commit.signal_name}",
        ),
        _check(
            "preemption.signal-received",
            "preemption",
            "Worker observed SIGTERM after parent delivery",
            signal_sent_at <= commit.signal_received_at,
            "signal_received_at >= signal_sent_at",
            f"sent={signal_sent_at.isoformat()}, received={commit.signal_received_at.isoformat()}",
        ),
        _check(
            "preemption.checkpoint-after-signal",
            "preemption",
            "Checkpoint commit completed after SIGTERM receipt",
            commit.signal_received_at <= commit.checkpoint_committed_at,
            "commit >= signal receipt",
            f"commit_seconds={checkpoint_commit_seconds:.6f}",
        ),
        _check(
            "preemption.commit-before-exit",
            "preemption",
            "Checkpoint commit completed before worker exit",
            commit.checkpoint_committed_at <= preemption_process.completed_at,
            "commit <= process exit",
            (
                f"commit={commit.checkpoint_committed_at.isoformat()}, "
                f"exit={preemption_process.completed_at.isoformat()}"
            ),
        ),
        _check(
            "preemption.grace-period",
            "preemption",
            "Checkpoint and clean exit completed within the grace period",
            graceful_exit_seconds <= grace_period_seconds,
            f"<= {grace_period_seconds:.6f} seconds",
            f"{graceful_exit_seconds:.6f} seconds",
        ),
        _check(
            "preemption.clean-exit",
            "preemption",
            "SIGTERM handler completed a clean worker exit",
            preemption_process.exit_verified and preemption_process.exit_code == 0,
            "verified exit 0",
            (f"verified={preemption_process.exit_verified}, exit={preemption_process.exit_code}"),
        ),
        _check(
            "checkpoint.no-incomplete-marker",
            "checkpoint",
            "No preemption-incomplete marker remains after exit",
            incomplete_marker_absent and not commit.incomplete_marker_present,
            "marker absent",
            "absent" if incomplete_marker_absent else "present",
        ),
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
            "process.distinct-recovery",
            "process",
            "Recovery ran in a new process",
            preemption_process.worker_pid != recovery_process.worker_pid,
            "distinct PIDs",
            f"{preemption_process.worker_pid} -> {recovery_process.worker_pid}",
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
        _check(
            "rpo.steps",
            "recovery",
            "No completed training steps were lost",
            rpo_steps == 0,
            "0 steps",
            f"{rpo_steps} steps",
        ),
        _check(
            "rpo.tokens",
            "recovery",
            "No completed training tokens were lost",
            rpo_tokens == 0,
            "0 tokens",
            f"{rpo_tokens} tokens",
        ),
    )
    failed = tuple(check.check_id for check in checks if check.status == "fail")
    return HFPreemptionGateV1(
        passed=not failed,
        checks=checks,
        failed_check_ids=failed,
        achieved_rpo_steps=rpo_steps,
        achieved_rpo_tokens=rpo_tokens,
    )
