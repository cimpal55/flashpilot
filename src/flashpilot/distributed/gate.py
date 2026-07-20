"""Deterministic exact Recovery Gate for two-rank FSDP qualification."""

from __future__ import annotations

from collections.abc import Callable

from flashpilot.distributed.checkpoint import ValidatedDistributedCheckpoint
from flashpilot.distributed.models import (
    DISTRIBUTED_SERIALIZED_STATE,
    DistributedCheckpointEvent,
    DistributedPhaseProcessEvidence,
    DistributedQualificationCheck,
    DistributedRankSummary,
    DistributedRecoveryGateV1,
)


def _check(
    check_id: str,
    category: str,
    label: str,
    passed: bool,
    expected: str,
    actual: str,
) -> DistributedQualificationCheck:
    return DistributedQualificationCheck(
        check_id=check_id,
        category=category,
        label=label,
        status="pass" if passed else "fail",
        expected=expected,
        actual=actual,
    )


def _rank_values(
    summaries: tuple[DistributedRankSummary, ...],
    selector: Callable[[DistributedRankSummary], object],
) -> tuple[object, ...]:
    return tuple(selector(summary) for summary in summaries)


def evaluate_distributed_recovery_gate(
    *,
    control_processes: DistributedPhaseProcessEvidence,
    control: tuple[DistributedRankSummary, ...],
    checkpoint_processes: DistributedPhaseProcessEvidence,
    checkpoint: tuple[DistributedRankSummary, ...],
    recovery_processes: DistributedPhaseProcessEvidence,
    recovery: tuple[DistributedRankSummary, ...],
    checkpoint_event: DistributedCheckpointEvent,
    validated_checkpoint: ValidatedDistributedCheckpoint,
    checkpoint_step: int,
    total_steps: int,
) -> DistributedRecoveryGateV1:
    phases = (control_processes, checkpoint_processes, recovery_processes)
    all_pids = tuple(item.worker_pid for phase in phases for item in phase.ranks)
    manifest = validated_checkpoint.manifest
    payload_roles = tuple(payload.role for payload in manifest.payloads)
    control_losses = _rank_values(control, lambda item: item.loss_history)
    checkpoint_losses = _rank_values(checkpoint, lambda item: item.loss_history)
    recovery_losses = _rank_values(recovery, lambda item: item.loss_history)

    comparisons = (
        (
            "topology.world-size",
            "topology",
            "Every phase uses exactly two ranks",
            all(phase.world_size == 2 for phase in phases),
            "2 ranks in every phase",
            ", ".join(str(phase.world_size) for phase in phases),
        ),
        (
            "topology.rank-set",
            "topology",
            "Every phase contains exact ranks 0 and 1",
            all(tuple(item.rank for item in phase.ranks) == (0, 1) for phase in phases),
            "(0, 1) in every phase",
            "; ".join(str(tuple(item.rank for item in phase.ranks)) for phase in phases),
        ),
        (
            "topology.backend",
            "topology",
            "Every phase uses the declared Gloo backend",
            all(phase.backend == "gloo" for phase in phases),
            "gloo",
            ", ".join(phase.backend for phase in phases),
        ),
        (
            "process.clean-exit",
            "process",
            "All six rank workers exited cleanly",
            all(
                item.exit_verified and item.exit_code == 0
                for phase in phases
                for item in phase.ranks
            ),
            "6 verified zero exits",
            str(sum(item.exit_code == 0 for phase in phases for item in phase.ranks)),
        ),
        (
            "process.distinct-groups",
            "process",
            "Control, checkpoint, and recovery use distinct processes",
            len(all_pids) == len(set(all_pids)) == 6,
            "6 unique PIDs",
            f"{len(set(all_pids))} unique PIDs",
        ),
        (
            "checkpoint.rank-zero-writer",
            "checkpoint",
            "Rank 0 emitted the atomic checkpoint commit",
            checkpoint_event.writer_pid == checkpoint_processes.ranks[0].worker_pid,
            str(checkpoint_processes.ranks[0].worker_pid),
            str(checkpoint_event.writer_pid),
        ),
        (
            "checkpoint.atomic-rename",
            "checkpoint",
            "Checkpoint directory commit used an atomic rename",
            checkpoint_event.atomic_rename_succeeded,
            "true",
            str(checkpoint_event.atomic_rename_succeeded).lower(),
        ),
        (
            "checkpoint.payload-fsync",
            "checkpoint",
            "Checkpoint payload and metadata files were fsynced",
            checkpoint_event.payload_files_synced and checkpoint_event.metadata_files_synced,
            "payload=true, metadata=true",
            (
                f"payload={str(checkpoint_event.payload_files_synced).lower()}, "
                f"metadata={str(checkpoint_event.metadata_files_synced).lower()}"
            ),
        ),
        (
            "checkpoint.complete-marker",
            "checkpoint",
            "Final checkpoint contains a matching completion marker",
            "COMPLETE" in validated_checkpoint.inventory,
            "COMPLETE",
            "present" if "COMPLETE" in validated_checkpoint.inventory else "missing",
        ),
        (
            "checkpoint.closed-inventory",
            "checkpoint",
            "Manifest and checksum inventory is closed",
            len(validated_checkpoint.checksums.files) == len(manifest.payloads),
            f"{len(manifest.payloads)} checksummed payloads",
            f"{len(validated_checkpoint.checksums.files)} checksummed payloads",
        ),
        (
            "checkpoint.dcp-metadata",
            "checkpoint",
            "PyTorch Distributed Checkpoint metadata is present",
            payload_roles.count("dcp-metadata") == 1,
            "1 DCP metadata payload",
            str(payload_roles.count("dcp-metadata")),
        ),
        (
            "checkpoint.dcp-shards",
            "checkpoint",
            "Distributed checkpoint contains sharded tensor payloads",
            payload_roles.count("dcp-shard") >= 1,
            ">=1 DCP shard payload",
            str(payload_roles.count("dcp-shard")),
        ),
        (
            "checkpoint.rank-states",
            "checkpoint",
            "Checkpoint contains exact rank 0 and 1 local training state",
            payload_roles.count("rank-state") == 2,
            "2 rank-state payloads",
            str(payload_roles.count("rank-state")),
        ),
        (
            "checkpoint.serialized-state",
            "checkpoint",
            "Checkpoint declares the complete distributed resume state",
            tuple(manifest.serialized_state) == DISTRIBUTED_SERIALIZED_STATE,
            ",".join(DISTRIBUTED_SERIALIZED_STATE),
            ",".join(manifest.serialized_state),
        ),
        (
            "checkpoint.global-step",
            "checkpoint",
            "Checkpoint step matches every checkpoint rank",
            manifest.global_step
            == checkpoint_event.global_step
            == checkpoint_step
            == checkpoint[0].final_global_step
            == checkpoint[1].final_global_step,
            str(checkpoint_step),
            str(manifest.global_step),
        ),
        (
            "trajectory.checkpoint-prefix",
            "trajectory",
            "Checkpoint-group trajectory matches the control prefix per rank",
            checkpoint_losses
            == tuple(tuple(history[:checkpoint_step]) for history in control_losses),
            "exact per-rank control prefixes",
            "exact match"
            if checkpoint_losses
            == tuple(tuple(history[:checkpoint_step]) for history in control_losses)
            else "different",
        ),
        (
            "restore.all-ranks-loaded",
            "restore",
            "Every recovery rank loaded the distributed checkpoint",
            all(
                item.checkpoint_loaded and item.checkpoint_step == checkpoint_step
                for item in recovery
            ),
            "rank 0 and 1 loaded step checkpoint",
            str(
                tuple(
                    (item.rank, item.checkpoint_loaded, item.checkpoint_step) for item in recovery
                )
            ),
        ),
        (
            "progress.global-step",
            "trajectory",
            "Every control and recovery rank reaches the final step",
            all(item.final_global_step == total_steps for item in control + recovery),
            str(total_steps),
            str(tuple(item.final_global_step for item in control + recovery)),
        ),
        (
            "trajectory.loss-history",
            "trajectory",
            "Per-rank stochastic loss histories exactly match control",
            recovery_losses == control_losses,
            "exact per-rank control histories",
            "exact match" if recovery_losses == control_losses else "different",
        ),
        (
            "state.trainable",
            "state",
            "Recovered full trainable-state digest exactly matches control",
            _rank_values(recovery, lambda item: item.trainable_state_sha256)
            == _rank_values(control, lambda item: item.trainable_state_sha256),
            str(_rank_values(control, lambda item: item.trainable_state_sha256)),
            str(_rank_values(recovery, lambda item: item.trainable_state_sha256)),
        ),
        (
            "state.evaluation",
            "state",
            "Recovered evaluation digest exactly matches control",
            _rank_values(recovery, lambda item: item.evaluation_sha256)
            == _rank_values(control, lambda item: item.evaluation_sha256),
            str(_rank_values(control, lambda item: item.evaluation_sha256)),
            str(_rank_values(recovery, lambda item: item.evaluation_sha256)),
        ),
        (
            "state.optimizer",
            "state",
            "Recovered full optimizer digest exactly matches control",
            _rank_values(recovery, lambda item: item.optimizer_sha256)
            == _rank_values(control, lambda item: item.optimizer_sha256),
            str(_rank_values(control, lambda item: item.optimizer_sha256)),
            str(_rank_values(recovery, lambda item: item.optimizer_sha256)),
        ),
        (
            "state.scheduler",
            "state",
            "Recovered scheduler digest exactly matches control",
            _rank_values(recovery, lambda item: item.scheduler_sha256)
            == _rank_values(control, lambda item: item.scheduler_sha256),
            str(_rank_values(control, lambda item: item.scheduler_sha256)),
            str(_rank_values(recovery, lambda item: item.scheduler_sha256)),
        ),
        (
            "collective.probe",
            "collective",
            "Recovered all-gather probe exactly matches control",
            _rank_values(recovery, lambda item: item.collective_probe_sha256)
            == _rank_values(control, lambda item: item.collective_probe_sha256),
            str(_rank_values(control, lambda item: item.collective_probe_sha256)),
            str(_rank_values(recovery, lambda item: item.collective_probe_sha256)),
        ),
    )
    checks = tuple(_check(*comparison) for comparison in comparisons)
    failed = tuple(check.check_id for check in checks if check.status == "fail")
    return DistributedRecoveryGateV1(
        passed=not failed,
        checks=checks,
        failed_check_ids=failed,
    )
