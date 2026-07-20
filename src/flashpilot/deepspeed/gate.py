"""Deterministic exact Recovery Gate for two-rank DeepSpeed ZeRO-2."""

from __future__ import annotations

from collections.abc import Callable

from flashpilot.deepspeed.checkpoint import ValidatedDeepSpeedCheckpoint
from flashpilot.deepspeed.models import (
    DEEPSPEED_SERIALIZED_STATE,
    DeepSpeedCheckpointEvent,
    DeepSpeedRankSummary,
    DeepSpeedRecoveryGateV1,
)
from flashpilot.distributed.models import (
    DistributedPhaseProcessEvidence,
    DistributedQualificationCheck,
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
    summaries: tuple[DeepSpeedRankSummary, ...],
    selector: Callable[[DeepSpeedRankSummary], object],
) -> tuple[object, ...]:
    return tuple(selector(summary) for summary in summaries)


def evaluate_deepspeed_recovery_gate(
    *,
    control_processes: DistributedPhaseProcessEvidence,
    control: tuple[DeepSpeedRankSummary, ...],
    checkpoint_processes: DistributedPhaseProcessEvidence,
    checkpoint: tuple[DeepSpeedRankSummary, ...],
    recovery_processes: DistributedPhaseProcessEvidence,
    recovery: tuple[DeepSpeedRankSummary, ...],
    checkpoint_event: DeepSpeedCheckpointEvent,
    validated_checkpoint: ValidatedDeepSpeedCheckpoint,
    checkpoint_step: int,
    total_steps: int,
) -> DeepSpeedRecoveryGateV1:
    phases = (control_processes, checkpoint_processes, recovery_processes)
    all_summaries = control + checkpoint + recovery
    all_pids = tuple(item.worker_pid for phase in phases for item in phase.ranks)
    manifest = validated_checkpoint.manifest
    payload_roles = tuple(payload.role for payload in manifest.payloads)
    control_losses = _rank_values(control, lambda item: item.loss_history)
    checkpoint_losses = _rank_values(checkpoint, lambda item: item.loss_history)
    recovery_losses = _rank_values(recovery, lambda item: item.loss_history)
    expected_loaded_path = (
        f"checkpoints/{manifest.checkpoint_id}/{manifest.checkpoint_tag}/mp_rank_00_model_states.pt"
    )

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
            "Every phase uses the Gloo backend",
            all(phase.backend == "gloo" for phase in phases),
            "gloo",
            ", ".join(phase.backend for phase in phases),
        ),
        (
            "topology.zero-stage",
            "topology",
            "Every rank uses DeepSpeed ZeRO stage 2",
            all(
                item.zero_stage == 2 and item.implementation == "zero-stage-2"
                for item in all_summaries
            ),
            "zero-stage-2 on 6 rank processes",
            str(tuple((item.rank, item.zero_stage) for item in all_summaries)),
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
            "checkpoint.collective-save",
            "checkpoint",
            "Both ranks completed DeepSpeed save_checkpoint",
            all(item.checkpoint_saved for item in checkpoint),
            "rank 0 and rank 1 saved",
            str(tuple((item.rank, item.checkpoint_saved) for item in checkpoint)),
        ),
        (
            "checkpoint.rank-zero-commit",
            "checkpoint",
            "Rank 0 committed the atomic checkpoint directory",
            checkpoint_event.writer_pid == checkpoint_processes.ranks[0].worker_pid,
            str(checkpoint_processes.ranks[0].worker_pid),
            str(checkpoint_event.writer_pid),
        ),
        (
            "checkpoint.atomic-rename",
            "checkpoint",
            "Checkpoint directory commit used an atomic same-filesystem rename",
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
            "checkpoint.deepspeed-tag",
            "checkpoint",
            "DeepSpeed latest pointer and tag use the exact checkpoint step",
            manifest.checkpoint_tag == f"global_step{checkpoint_step:06d}"
            and checkpoint_event.checkpoint_tag == manifest.checkpoint_tag,
            f"global_step{checkpoint_step:06d}",
            manifest.checkpoint_tag,
        ),
        (
            "checkpoint.model-state",
            "checkpoint",
            "DeepSpeed model and scheduler state file is present",
            payload_roles.count("deepspeed-model-state") == 1,
            "1 model-state payload",
            str(payload_roles.count("deepspeed-model-state")),
        ),
        (
            "checkpoint.zero-shards",
            "checkpoint",
            "DeepSpeed contains exact rank 0 and 1 ZeRO optimizer shards",
            payload_roles.count("deepspeed-optimizer-shard") == 2,
            "2 ZeRO optimizer shards",
            str(payload_roles.count("deepspeed-optimizer-shard")),
        ),
        (
            "checkpoint.rank-states",
            "checkpoint",
            "Checkpoint contains exact rank 0 and 1 local stochastic state",
            payload_roles.count("rank-state") == 2,
            "2 rank-state payloads",
            str(payload_roles.count("rank-state")),
        ),
        (
            "checkpoint.serialized-state",
            "checkpoint",
            "Checkpoint declares the complete ZeRO-2 resume state",
            tuple(manifest.serialized_state) == DEEPSPEED_SERIALIZED_STATE,
            ",".join(DEEPSPEED_SERIALIZED_STATE),
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
            "checkpoint.client-state",
            "checkpoint",
            "Both saving ranks bound strict FlashPilot client state",
            all(item.client_state_valid for item in checkpoint),
            "valid on rank 0 and rank 1",
            str(tuple(item.client_state_valid for item in checkpoint)),
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
            "Both recovery ranks loaded the DeepSpeed checkpoint",
            all(
                item.checkpoint_loaded and item.checkpoint_step == checkpoint_step
                for item in recovery
            ),
            "rank 0 and rank 1 loaded step checkpoint",
            str(tuple((item.rank, item.checkpoint_loaded) for item in recovery)),
        ),
        (
            "restore.exact-tag-path",
            "restore",
            "Both recovery ranks loaded the validated DeepSpeed tag path",
            all(item.loaded_checkpoint_path == expected_loaded_path for item in recovery),
            expected_loaded_path,
            str(tuple(item.loaded_checkpoint_path for item in recovery)),
        ),
        (
            "restore.client-state",
            "restore",
            "Both recovery ranks accepted the strict DeepSpeed client state",
            all(item.client_state_valid for item in recovery),
            "valid on rank 0 and rank 1",
            str(tuple(item.client_state_valid for item in recovery)),
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
            "Recovered trainable-state digest exactly matches control",
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
            "Recovered ZeRO optimizer digest exactly matches control per rank",
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
    return DeepSpeedRecoveryGateV1(
        passed=not failed,
        checks=checks,
        failed_check_ids=failed,
    )
