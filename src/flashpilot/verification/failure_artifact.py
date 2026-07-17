"""Build the redacted failure-analysis request without GPT integration."""

from __future__ import annotations

import json
from pathlib import Path

from flashpilot.adapters.registry import get_adapter
from flashpilot.checkpoints.loader import ValidatedCheckpoint
from flashpilot.domain.recovery import (
    CheckpointCommittedEvent,
    CrashMetadata,
    RecoveryGateResult,
    RecoveryWorkerResult,
    SanitizedFailureArtifact,
)

FORBIDDEN_FAILURE_PAYLOAD_TERMS = (
    "missing_training_state",
    "missing-training-state",
    "injection label",
    "failure-injection",
    "expected diagnosis",
    "repair preset",
    "intentionally omitted",
    "deliberately omitted",
)


def assert_sanitized_failure_payload(serialized: str) -> None:
    lowered = serialized.lower()
    found = [term for term in FORBIDDEN_FAILURE_PAYLOAD_TERMS if term in lowered]
    home_variants = {str(Path.home()).lower(), str(Path.home()).replace("\\", "/").lower()}
    if found:
        raise ValueError(f"sanitized failure payload contains forbidden terms: {found}")
    if any(home and home in lowered for home in home_variants):
        raise ValueError("sanitized failure payload contains an absolute home path")


def build_sanitized_failure_artifact(
    *,
    checkpoint: ValidatedCheckpoint,
    event: CheckpointCommittedEvent,
    crash: CrashMetadata,
    recovery: RecoveryWorkerResult,
    gate: RecoveryGateResult,
) -> SanitizedFailureArtifact:
    manifest = checkpoint.manifest
    model_state_name = "model" if "model" in manifest.serialized_state else "adapter"
    required_state = [
        model_state_name,
        "optimizer",
        "scheduler",
        "global_step",
        "python_rng",
        "numpy_rng",
        "torch_rng",
    ]
    required_integrity = [
        "manifest",
        "checksums",
        "completion_marker",
        "atomic_commit",
    ]
    if manifest.base_artifact is not None:
        required_state.append("base_model_identity")
        required_integrity.append("base_artifact_hash")
    capabilities = get_adapter("native-pytorch").capabilities().model_dump(mode="json")
    evidence_catalog = {
        evidence_id: check.label for check in gate.checks for evidence_id in check.evidence_ids
    }
    artifact = SanitizedFailureArtifact(
        user_objective={
            "recovery_correctness": "strict",
            "hard_rollback_limit_steps": gate.hard_rollback_limit_steps,
        },
        workload_capabilities=capabilities,
        checkpoint_contract={
            "required_state": required_state,
            "required_integrity_controls": required_integrity,
            "correctness_priority": "strict",
        },
        save_restore_summary={
            "serialized_state": list(manifest.serialized_state),
            "restored_global_step": recovery.restored_global_step,
            "integrity_controls": [
                "manifest",
                "SHA-256 checksums",
                "completion marker",
                "atomic directory commit",
                "base artifact SHA-256",
            ],
        },
        manifest_summary={
            "schema_version": manifest.schema_version,
            "profile": manifest.profile,
            "global_step": manifest.global_step,
            "serialized_state": list(manifest.serialized_state),
            "payload_roles": [payload.role for payload in manifest.payloads],
            "has_base_reference": manifest.base_artifact is not None,
        },
        restore_order=(
            "validate checkpoint metadata and payload checksums",
            "validate immutable base identity when referenced",
            "load declared model state",
            "resume from the restored global step",
        ),
        gate_checks=tuple(check.model_dump(mode="json") for check in gate.checks),
        state_differences={
            "checkpoint_trainable_match": (
                event.checkpoint_snapshot.trainable_state_sha256
                == recovery.after_restore.trainable_state_sha256
            ),
            "optimizer_match": (
                event.checkpoint_snapshot.optimizer_sha256
                == recovery.after_restore.optimizer_sha256
            ),
            "scheduler_match": (
                event.checkpoint_snapshot.scheduler_sha256
                == recovery.after_restore.scheduler_sha256
            ),
            "python_rng_match": (
                event.rng_state.python_sha256 == recovery.after_restore_rng.python_sha256
            ),
            "numpy_rng_match": (
                event.rng_state.numpy_sha256 == recovery.after_restore_rng.numpy_sha256
            ),
            "torch_rng_match": (
                event.rng_state.torch_sha256 == recovery.after_restore_rng.torch_sha256
            ),
        },
        trajectory_summary={
            "checkpoint_step": manifest.global_step,
            "final_step": recovery.final.global_step,
            "loss_history_match": not any(
                check.check_id == "trajectory.loss_history" and check.status == "fail"
                for check in gate.checks
            ),
            "final_trainable_match": not any(
                check.check_id == "trajectory.final_trainable" and check.status == "fail"
                for check in gate.checks
            ),
            "final_evaluation_match": not any(
                check.check_id == "trajectory.final_evaluation" and check.status == "fail"
                for check in gate.checks
            ),
        },
        integrity_summary={
            "manifest_valid": True,
            "completion_marker_present": True,
            "checksums_valid": True,
            "checkpoint_load_succeeded": True,
        },
        crash_metadata={
            "worker_pid": crash.worker_pid,
            "checkpoint_step": crash.checkpoint_step,
            "last_completed_step": crash.last_completed_step,
            "checkpoint_id": Path(crash.checkpoint_path).name,
            "termination_method": crash.termination_method,
            "termination_exit_code": crash.termination_exit_code,
            "recovery_worker_pid": recovery.worker_pid,
        },
        evidence_catalog=evidence_catalog,
    )
    serialized = json.dumps(artifact.model_dump(mode="json"), sort_keys=True)
    assert_sanitized_failure_payload(serialized)
    return artifact
