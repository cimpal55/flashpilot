"""The deterministic Recovery Gate and all mandatory Prompt 3 checks."""

from __future__ import annotations

from pathlib import Path

from flashpilot.checkpoints.base_artifact import (
    BaseArtifactValidationError,
    validate_base_artifact,
)
from flashpilot.checkpoints.loader import ValidatedCheckpoint
from flashpilot.domain.recovery import (
    CheckpointCommittedEvent,
    ComparisonPolicy,
    CrashMetadata,
    GateCategory,
    GateCheck,
    RecoveryEvidenceId,
    RecoveryGateCheckId,
    RecoveryGateResult,
    RecoveryProcessMetadata,
    RecoveryWorkerResult,
    RuntimeSnapshot,
)


def _check(
    check_id: RecoveryGateCheckId,
    category: GateCategory,
    label: str,
    *,
    passed: bool,
    evidence_id: RecoveryEvidenceId,
    expected: str,
    actual: str,
    details: str | None = None,
) -> GateCheck:
    return GateCheck(
        check_id=check_id,
        category=category,
        label=label,
        status="pass" if passed else "fail",
        evidence_ids=(evidence_id,),
        expected=expected,
        actual=actual,
        details=details,
    )


def _not_applicable(
    check_id: RecoveryGateCheckId,
    category: GateCategory,
    label: str,
    *,
    evidence_id: RecoveryEvidenceId,
    details: str,
) -> GateCheck:
    return GateCheck(
        check_id=check_id,
        category=category,
        label=label,
        status="not_applicable",
        evidence_ids=(evidence_id,),
        expected="not required",
        actual="not applicable",
        details=details,
    )


def _base_checks(*, run_root: Path, checkpoint: ValidatedCheckpoint) -> tuple[GateCheck, GateCheck]:
    reference = checkpoint.manifest.base_artifact
    if reference is None:
        return (
            _not_applicable(
                "integrity.base_present",
                "Integrity",
                "Base artifact present when required",
                evidence_id="base:presence",
                details="This strategy stores its complete model in the checkpoint.",
            ),
            _not_applicable(
                "integrity.base_hash",
                "Integrity",
                "Base artifact hash matches",
                evidence_id="base:sha256",
                details="This strategy has no external base artifact.",
            ),
        )
    try:
        validate_base_artifact(run_root=run_root, reference=reference)
    except BaseArtifactValidationError as error:
        detail = str(error)
        return (
            _check(
                "integrity.base_present",
                "Integrity",
                "Base artifact present when required",
                passed="missing" not in detail,
                evidence_id="base:presence",
                expected="contained immutable base artifact",
                actual=detail,
            ),
            _check(
                "integrity.base_hash",
                "Integrity",
                "Base artifact hash matches",
                passed=False,
                evidence_id="base:sha256",
                expected=reference.sha256,
                actual="base validation failed",
                details=detail,
            ),
        )
    return (
        _check(
            "integrity.base_present",
            "Integrity",
            "Base artifact present when required",
            passed=True,
            evidence_id="base:presence",
            expected="contained immutable base artifact",
            actual="present",
        ),
        _check(
            "integrity.base_hash",
            "Integrity",
            "Base artifact hash matches",
            passed=True,
            evidence_id="base:sha256",
            expected=reference.sha256,
            actual=reference.sha256,
        ),
    )


def evaluate_recovery_gate(
    *,
    run_root: Path,
    checkpoint: ValidatedCheckpoint,
    committed_event: CheckpointCommittedEvent,
    crash: CrashMetadata,
    recovery_process: RecoveryProcessMetadata,
    recovery: RecoveryWorkerResult,
    control: RuntimeSnapshot,
    hard_rollback_limit_steps: int,
    managed_paths_contained: bool,
) -> RecoveryGateResult:
    """Evaluate every mandatory check without allowing a tolerance override."""

    if hard_rollback_limit_steps < 0:
        raise ValueError("hard rollback limit cannot be negative")
    manifest = checkpoint.manifest
    serialized = set(manifest.serialized_state)
    checkpoint_snapshot = committed_event.checkpoint_snapshot
    restored_snapshot = recovery.after_restore
    base_present, base_hash = _base_checks(run_root=run_root, checkpoint=checkpoint)
    checks: list[GateCheck] = [
        _check(
            "integrity.manifest_schema",
            "Integrity",
            "Manifest schema valid",
            passed=True,
            evidence_id="manifest:schema",
            expected="checkpoint-manifest-v1",
            actual=manifest.schema_version,
        ),
        _check(
            "integrity.completion_marker",
            "Integrity",
            "Completion marker present",
            passed=(checkpoint.path / "COMPLETE").is_file(),
            evidence_id="integrity:completion-marker",
            expected="COMPLETE present in final checkpoint",
            actual="present" if (checkpoint.path / "COMPLETE").is_file() else "missing",
        ),
        _check(
            "integrity.checksums",
            "Integrity",
            "All payload checksums valid",
            passed=True,
            evidence_id="integrity:sha256",
            expected="every manifest payload matches SHA-256 and size",
            actual=f"{len(checkpoint.checksums.files)} payloads validated",
        ),
        base_present,
        base_hash,
    ]

    valid_step = (
        manifest.global_step == committed_event.checkpoint_step
        and manifest.global_step == recovery.restored_global_step
        and 0 < manifest.global_step < control.global_step
    )
    checks.append(
        _check(
            "state.global_step",
            "Required training state",
            "Checkpoint global step is valid",
            passed=valid_step,
            evidence_id="manifest:global-step",
            expected=f"0 < step < {control.global_step}, consistent across restore",
            actual=(
                f"manifest={manifest.global_step}, event={committed_event.checkpoint_step}, "
                f"restored={recovery.restored_global_step}"
            ),
        )
    )
    model_state_name = "model" if manifest.strategy == "safe_full" else "adapter"
    model_matches = (
        restored_snapshot.trainable_state_sha256 == checkpoint_snapshot.trainable_state_sha256
    )
    checks.append(
        _check(
            "state.model_or_adapter",
            "Required training state",
            "Model or adapter state restores",
            passed=model_state_name in serialized and model_matches,
            evidence_id="restore:model-state",
            expected=f"serialized {model_state_name} and exact trainable-state digest",
            actual=(f"serialized={model_state_name in serialized}, digest_match={model_matches}"),
        )
    )

    optimizer_matches = restored_snapshot.optimizer_sha256 == checkpoint_snapshot.optimizer_sha256
    scheduler_matches = restored_snapshot.scheduler_sha256 == checkpoint_snapshot.scheduler_sha256
    checks.extend(
        (
            _check(
                "state.optimizer",
                "Required training state",
                "Optimizer state restores when required",
                passed="optimizer" in serialized and optimizer_matches,
                evidence_id="restore:optimizer-state",
                expected="serialized optimizer with exact digest",
                actual=(
                    f"serialized={'optimizer' in serialized}, digest_match={optimizer_matches}"
                ),
            ),
            _check(
                "state.scheduler",
                "Required training state",
                "Scheduler state restores when required",
                passed="scheduler" in serialized and scheduler_matches,
                evidence_id="restore:scheduler-state",
                expected="serialized scheduler with exact digest",
                actual=(
                    f"serialized={'scheduler' in serialized}, digest_match={scheduler_matches}"
                ),
            ),
        )
    )

    rng_pairs = (
        (
            "python_rng",
            "state.python_rng",
            "Python RNG state restores when required",
            "restore:python-rng",
            checkpoint_snapshot,
            committed_event.rng_state.python_sha256,
            recovery.after_restore_rng.python_sha256,
        ),
        (
            "numpy_rng",
            "state.numpy_rng",
            "NumPy RNG state restores when required",
            "restore:numpy-rng",
            checkpoint_snapshot,
            committed_event.rng_state.numpy_sha256,
            recovery.after_restore_rng.numpy_sha256,
        ),
        (
            "torch_rng",
            "state.torch_rng",
            "Torch RNG state restores when required",
            "restore:torch-rng",
            checkpoint_snapshot,
            committed_event.rng_state.torch_sha256,
            recovery.after_restore_rng.torch_sha256,
        ),
    )
    for state_name, check_id, label, evidence_id, _, expected_digest, actual_digest in rng_pairs:
        digest_matches = actual_digest == expected_digest
        checks.append(
            _check(
                check_id,
                "Required training state",
                label,
                passed=state_name in serialized and digest_matches,
                evidence_id=evidence_id,
                expected="serialized state with exact digest",
                actual=(f"serialized={state_name in serialized}, digest_match={digest_matches}"),
            )
        )

    next_step_matches = (
        recovery.first_resumed_batch_step == manifest.global_step
        and recovery.first_completed_step == manifest.global_step + 1
    )
    achieved_rollback = crash.last_completed_step - manifest.global_step
    checks.extend(
        (
            _check(
                "process.next_step",
                "Process recovery",
                "Resumed run continues from the expected next step",
                passed=next_step_matches,
                evidence_id="process:next-step",
                expected=(
                    f"first batch at {manifest.global_step}, first completion at "
                    f"{manifest.global_step + 1}"
                ),
                actual=(
                    f"first batch at {recovery.first_resumed_batch_step}, first completion at "
                    f"{recovery.first_completed_step}"
                ),
            ),
            _check(
                "process.original_pid",
                "Process recovery",
                "Original worker PID is recorded",
                passed=(crash.worker_pid == committed_event.worker_pid and crash.worker_pid > 0),
                evidence_id="process:original-pid",
                expected=str(committed_event.worker_pid),
                actual=str(crash.worker_pid),
            ),
            _check(
                "process.expected_termination",
                "Process recovery",
                "Original worker termination is verified",
                passed=crash.termination_verified and crash.termination_exit_code != 0,
                evidence_id="process:termination",
                expected="parent termination with nonzero exit code",
                actual=(
                    f"method={crash.termination_method}, exit={crash.termination_exit_code}, "
                    f"verified={crash.termination_verified}"
                ),
            ),
            _check(
                "process.new_recovery_pid",
                "Process recovery",
                "Recovery uses a different PID",
                passed=(
                    recovery.worker_pid != crash.worker_pid
                    and recovery.worker_pid == recovery_process.worker_pid
                ),
                evidence_id="process:recovery-pid",
                expected=f"PID different from {crash.worker_pid}",
                actual=str(recovery.worker_pid),
            ),
            _check(
                "process.recovery_exit",
                "Process recovery",
                "Recovery worker exits successfully",
                passed=recovery_process.exit_verified and recovery_process.exit_code == 0,
                evidence_id="process:recovery-exit",
                expected="exit code 0",
                actual=(
                    f"exit={recovery_process.exit_code}, verified={recovery_process.exit_verified}"
                ),
            ),
            _check(
                "rollback.hard_limit",
                "Safety and rollback",
                "Achieved rollback is within the hard limit",
                passed=achieved_rollback <= hard_rollback_limit_steps,
                evidence_id="rollback:achieved",
                expected=f"<= {hard_rollback_limit_steps} steps",
                actual=f"{achieved_rollback} steps",
            ),
        )
    )

    checkpoint_evaluation_matches = (
        restored_snapshot.evaluation_sha256 == checkpoint_snapshot.evaluation_sha256
    )
    final_trainable_matches = (
        recovery.final.trainable_state_sha256 == control.trainable_state_sha256
    )
    final_evaluation_matches = recovery.final.evaluation_sha256 == control.evaluation_sha256
    loss_matches = recovery.final.loss_history == control.loss_history
    checks.extend(
        (
            _check(
                "trajectory.checkpoint_evaluation",
                "Trajectory correctness",
                "Fixed evaluation after restore matches",
                passed=checkpoint_evaluation_matches,
                evidence_id="trajectory:checkpoint-evaluation",
                expected=checkpoint_snapshot.evaluation_sha256,
                actual=restored_snapshot.evaluation_sha256,
                details="Exact SHA-256 comparison; no numerical tolerance is applied.",
            ),
            _check(
                "trajectory.final_trainable",
                "Trajectory correctness",
                "Final trainable parameters match control",
                passed=final_trainable_matches,
                evidence_id="trajectory:final-trainable",
                expected=control.trainable_state_sha256,
                actual=recovery.final.trainable_state_sha256,
                details="Exact SHA-256 comparison; no numerical tolerance is applied.",
            ),
            _check(
                "trajectory.final_evaluation",
                "Trajectory correctness",
                "Final evaluation logits match control",
                passed=final_evaluation_matches,
                evidence_id="trajectory:final-evaluation",
                expected=control.evaluation_sha256,
                actual=recovery.final.evaluation_sha256,
                details="Exact SHA-256 comparison; no numerical tolerance is applied.",
            ),
            _check(
                "trajectory.loss_history",
                "Trajectory correctness",
                "Continued loss trajectory matches control",
                passed=loss_matches,
                evidence_id="trajectory:loss-history",
                expected="exact loss sequence equality",
                actual="exact match" if loss_matches else "sequence differs",
                details="Exact float sequence comparison; no numerical tolerance is applied.",
            ),
            _check(
                "safety.path_containment",
                "Safety and rollback",
                "All managed write paths passed containment",
                passed=managed_paths_contained,
                evidence_id="safety:path-containment",
                expected="all paths contained; symlink escapes rejected",
                actual="contained" if managed_paths_contained else "containment failure",
            ),
        )
    )

    mandatory_state = {
        model_state_name,
        "optimizer",
        "scheduler",
        "global_step",
        "python_rng",
        "numpy_rng",
        "torch_rng",
        "config",
    }
    if manifest.base_artifact is not None:
        mandatory_state.add("base_model_identity")
    absent = sorted(mandatory_state - serialized)
    checks.append(
        _check(
            "contract.no_mandatory_omission",
            "Safety and rollback",
            "No mandatory contract requirement was silently omitted",
            passed=not absent,
            evidence_id="contract:mandatory-state",
            expected="all mandatory continuation state declared",
            actual="complete" if not absent else f"manifest lacks: {', '.join(absent)}",
        )
    )

    failed = tuple(check.check_id for check in checks if check.status == "fail")
    policy = ComparisonPolicy(
        evidence=(
            "The controlled CPU workload uses deterministic algorithms, one Torch thread, "
            "fixed seeds, and step-derived batches. Cross-process comparisons fail on any "
            "digest or loss-sequence difference."
        )
    )
    return RecoveryGateResult(
        passed=not failed,
        checks=tuple(checks),
        failed_check_ids=failed,
        achieved_rollback_steps=achieved_rollback,
        hard_rollback_limit_steps=hard_rollback_limit_steps,
        comparison_policy=policy,
    )
