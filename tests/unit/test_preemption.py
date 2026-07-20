from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.ci.exits import EXIT_UNSUPPORTED
from flashpilot.ci.models import CIPolicyV1
from flashpilot.ci.policy import evaluate_ci_policy
from flashpilot.ci.sarif import build_sarif_log
from flashpilot.ci.service import normalize_run_evidence
from flashpilot.contracts.huggingface import huggingface_trainer_persistence_contract
from flashpilot.contracts.models import QualificationProfile
from flashpilot.hf.models import (
    HFCheckpointLifecycleEvidence,
    HFProcessEvidence,
    HFRunSummary,
)
from flashpilot.preemption.gate import evaluate_preemption_gate
from flashpilot.preemption.models import (
    HFPreemptionCertificationResult,
    HFPreemptionCommitEvidence,
    HFPreemptionReadyEvidence,
)
from flashpilot.preemption.schema import preemption_schema_documents


def _summary(*, mode: str, pid: int, checkpoint_step: int) -> HFRunSummary:
    return HFRunSummary(
        mode=mode,
        scenario="complete",
        worker_pid=pid,
        trainer_global_step=8,
        semantic_global_step=8,
        checkpoint_step=checkpoint_step,
        model_loaded_from_checkpoint=mode == "recover",
        loss_history=tuple(float(index) for index in range(8)),
        trainable_state_sha256="a" * 64,
        evaluation_sha256="b" * 64,
        optimizer_sha256="c" * 64,
        scheduler_sha256="d" * 64,
        transformers_version="5.14.0",
        torch_version="2.7.0",
        offline_environment=True,
    )


def _evidence() -> tuple[
    HFRunSummary,
    HFRunSummary,
    HFProcessEvidence,
    HFProcessEvidence,
    HFPreemptionReadyEvidence,
    datetime,
    HFPreemptionCommitEvidence,
]:
    start = datetime(2026, 7, 20, tzinfo=UTC)
    ready = HFPreemptionReadyEvidence(
        worker_pid=202,
        completed_step=4,
        emitted_at=start + timedelta(seconds=1),
    )
    signal_sent = start + timedelta(seconds=2)
    checkpoint = HFCheckpointLifecycleEvidence(
        worker_pid=202,
        global_step=4,
        checkpoint_path="preemption/checkpoints/checkpoint-4",
        scenario="complete",
        model_present=True,
        trainer_state_present=True,
        optimizer_present=True,
        scheduler_present=True,
        rng_state_present=True,
        emitted_at=start + timedelta(seconds=3),
    )
    commit = HFPreemptionCommitEvidence(
        worker_pid=202,
        signal_received_at=start + timedelta(seconds=2, milliseconds=100),
        checkpoint_committed_at=start + timedelta(seconds=3, milliseconds=100),
        checkpoint=checkpoint,
    )
    preemption_process = HFProcessEvidence(
        worker_pid=202,
        started_at=start,
        completed_at=start + timedelta(seconds=4),
        exit_code=0,
        exit_verified=True,
    )
    recovery_process = HFProcessEvidence(
        worker_pid=303,
        started_at=start + timedelta(seconds=5),
        completed_at=start + timedelta(seconds=6),
        exit_code=0,
        exit_verified=True,
    )
    return (
        _summary(mode="control", pid=101, checkpoint_step=0),
        _summary(mode="recover", pid=303, checkpoint_step=4),
        preemption_process,
        recovery_process,
        ready,
        signal_sent,
        commit,
    )


def test_preemption_gate_requires_signal_commit_marker_and_exact_trajectory() -> None:
    control, recovery, process, recovery_process, ready, signal_sent, commit = _evidence()

    gate = evaluate_preemption_gate(
        control=control,
        recovery=recovery,
        preemption_process=process,
        recovery_process=recovery_process,
        ready=ready,
        signal_sent_at=signal_sent,
        commit=commit,
        incomplete_marker_absent=True,
        checkpoint_commit_seconds=1.1,
        graceful_exit_seconds=2.0,
        grace_period_seconds=30,
        total_steps=8,
        tokens_per_step=32,
    )

    assert gate.passed is True
    assert gate.failed_check_ids == ()
    assert gate.achieved_rpo_steps == gate.achieved_rpo_tokens == 0
    assert len(gate.checks) == 22
    assert {check.check_id for check in gate.checks} >= {
        "preemption.signal-received",
        "preemption.grace-period",
        "checkpoint.no-incomplete-marker",
        "trajectory.loss-history",
        "rpo.steps",
        "rpo.tokens",
    }


def test_verified_preemption_result_projects_exact_ci_policy_and_sarif_evidence(
    tmp_path: Path,
) -> None:
    control, recovery, process, recovery_process, ready, signal_sent, commit = _evidence()
    gate = evaluate_preemption_gate(
        control=control,
        recovery=recovery,
        preemption_process=process,
        recovery_process=recovery_process,
        ready=ready,
        signal_sent_at=signal_sent,
        commit=commit,
        incomplete_marker_absent=True,
        checkpoint_commit_seconds=1.1,
        graceful_exit_seconds=2.0,
        grace_period_seconds=30,
        total_steps=8,
        tokens_per_step=32,
    )
    result = HFPreemptionCertificationResult(
        run_id="synthetic-preemption",
        created_at=recovery_process.completed_at + timedelta(seconds=1),
        grace_period_seconds=30,
        preemption_step=4,
        total_steps=8,
        tokens_per_step=32,
        script_path="inputs/train.py",
        forwarded_arguments=(),
        control_process=HFProcessEvidence(
            worker_pid=101,
            started_at=datetime(2026, 7, 20, tzinfo=UTC),
            completed_at=datetime(2026, 7, 20, tzinfo=UTC) + timedelta(seconds=1),
            exit_code=0,
            exit_verified=True,
        ),
        control=control,
        preemption_process=process,
        ready_event=ready,
        signal_sent_at=signal_sent,
        commit_event=commit,
        checkpoint_inventory=("model.safetensors", "optimizer.pt"),
        checkpoint_commit_seconds=1.1,
        graceful_exit_seconds=2.0,
        recovery_process=recovery_process,
        recovery=recovery,
        recovery_rto_seconds=1.0,
        gate=gate,
        final_verdict="VERIFIED",
        verified_persisted_bytes=100,
        limitations=("Synthetic typed-model test only.",),
    )

    evidence = normalize_run_evidence(result)
    sarif = build_sarif_log(evidence).runs[0]
    evaluation = evaluate_ci_policy(
        run_root=tmp_path,
        evidence=evidence,
        policy=CIPolicyV1(
            qualification_profile=QualificationProfile.PREEMPTION_SAFE_TRAINING,
            required_faults=("managed_preemption",),
            max_rpo_steps=0,
            max_rto_seconds=2.0,
            require_attestation=False,
        ),
    )

    assert evidence.kind == "hf-preemption-certification"
    assert evidence.qualification_profile == "preemption-safe-training"
    assert evidence.fault == "managed_preemption"
    assert evidence.rpo_steps == 0
    assert len(evidence.checks) == 22
    assert evaluation.passed is True
    assert evaluation.failed_check_ids == ()
    assert len(sarif.tool.driver.rules) == 22
    assert sarif.results == ()


def test_preemption_gate_fails_closed_when_incomplete_marker_remains() -> None:
    control, recovery, process, recovery_process, ready, signal_sent, commit = _evidence()

    gate = evaluate_preemption_gate(
        control=control,
        recovery=recovery,
        preemption_process=process,
        recovery_process=recovery_process,
        ready=ready,
        signal_sent_at=signal_sent,
        commit=commit,
        incomplete_marker_absent=False,
        checkpoint_commit_seconds=1.1,
        graceful_exit_seconds=2.0,
        grace_period_seconds=30,
        total_steps=8,
        tokens_per_step=32,
    )

    assert gate.passed is False
    assert gate.failed_check_ids == ("checkpoint.no-incomplete-marker",)


def test_preemption_commit_rejects_out_of_order_signal_evidence() -> None:
    *_, commit = _evidence()

    with pytest.raises(ValidationError, match="cannot commit before signal"):
        HFPreemptionCommitEvidence(
            worker_pid=commit.worker_pid,
            signal_received_at=commit.checkpoint_committed_at + timedelta(seconds=1),
            checkpoint_committed_at=commit.checkpoint_committed_at,
            checkpoint=commit.checkpoint,
        )


def test_preemption_contract_reuses_exact_hf_state_minimum() -> None:
    exact = huggingface_trainer_persistence_contract()
    preemption = huggingface_trainer_persistence_contract(
        QualificationProfile.PREEMPTION_SAFE_TRAINING
    )

    assert preemption.qualification_profile == "preemption-safe-training"
    assert preemption.items == exact.items
    assert all(item.exactness == "exact" for item in preemption.items)
    assert preemption.max_rpo_steps == 0


def test_preemption_schemas_match_checked_files() -> None:
    for filename, expected in preemption_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


def test_preemption_cli_fails_closed_when_posix_sigterm_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import flashpilot.preemption.service as service

    monkeypatch.setattr(service, "supports_posix_sigterm", lambda: False)
    run_root = tmp_path / "unsupported"
    invocation = CliRunner().invoke(
        cli.app,
        [
            "certify-preemption",
            "--framework",
            "hf",
            "--signal",
            "SIGTERM",
            "--grace-period",
            "300",
            "--run-dir",
            str(run_root),
        ],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert "requires a POSIX host" in invocation.output
    assert "TerminateProcess is not equivalent" in invocation.output
    assert not run_root.exists()


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (("--framework", "lightning"), "Unsupported preemption framework or signal"),
        (("--signal", "SIGKILL"), "Unsupported preemption framework or signal"),
    ],
)
def test_preemption_cli_rejects_unsupported_surface(
    arguments: tuple[str, str],
    message: str,
) -> None:
    invocation = CliRunner().invoke(cli.app, ["certify-preemption", *arguments])

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert message in invocation.output
