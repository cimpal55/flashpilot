from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from flashpilot.attestation.models import RecoveryAttestationV1
from flashpilot.cli import app
from flashpilot.contracts import distributed_fsdp_persistence_contract
from flashpilot.distributed.models import (
    DISTRIBUTED_SERIALIZED_STATE,
    DistributedCheckpointManifest,
    DistributedCheckpointPayload,
)
from flashpilot.distributed.schema import distributed_schema_documents


def _payload(
    role: str,
    path: str,
    *,
    rank: int | None = None,
) -> DistributedCheckpointPayload:
    return DistributedCheckpointPayload(
        role=role,
        path=path,
        sha256="a" * 64,
        size_bytes=1,
        rank=rank,
    )


def _manifest() -> DistributedCheckpointManifest:
    return DistributedCheckpointManifest(
        checkpoint_id="checkpoint-step-000004",
        global_step=4,
        created_at=datetime(2026, 7, 20, tzinfo=UTC),
        payloads=(
            _payload("dcp-metadata", "dcp/.metadata"),
            _payload("dcp-shard", "dcp/__0_0.distcp"),
            _payload("rank-state", "rank-state-000.json", rank=0),
            _payload("rank-state", "rank-state-001.json", rank=1),
        ),
    )


def _distributed_attestation() -> RecoveryAttestationV1:
    return RecoveryAttestationV1(
        framework="pytorch-distributed",
        framework_version="2.13.0",
        adapter="pytorch-fsdp",
        run_id="distributed-run",
        issued_at=datetime(2026, 7, 20, tzinfo=UTC),
        code_commit="a" * 40,
        source_tree_state="clean",
        dependency_environment_sha256="b" * 64,
        checkpoint_path="checkpoints/checkpoint-step-000004",
        checkpoint_sha256="c" * 64,
        checkpoint_file_count=7,
        checkpoint_logical_bytes=100,
        persistence_contract_sha256="d" * 64,
        evidence_manifest_sha256="e" * 64,
        fault_scenario="checkpoint_restart",
        distributed_strategy="fsdp",
        distributed_implementation="fully_shard",
        distributed_backend="gloo",
        distributed_world_size=2,
        original_worker_pid=101,
        recovery_worker_pid=201,
        original_worker_pids=(101, 102),
        recovery_worker_pids=(201, 202),
        control_digest="f" * 64,
        resumed_digest="f" * 64,
        control_evaluation_digest="1" * 64,
        resumed_evaluation_digest="1" * 64,
        checks_passed=24,
        checks_total=24,
        rpo_steps=0,
        max_rpo_steps=0,
        rto_seconds=1.0,
        verified_persisted_bytes=100,
        limitations=("Same-world-size two-rank qualification only.",),
    )


def test_distributed_manifest_requires_exact_topology_and_complete_state() -> None:
    manifest = _manifest()

    assert manifest.world_size == 2
    assert manifest.strategy == "fsdp"
    assert manifest.implementation == "fully_shard"
    assert manifest.backend == "gloo"
    assert manifest.serialized_state == DISTRIBUTED_SERIALIZED_STATE
    assert tuple(payload.rank for payload in manifest.payloads if payload.role == "rank-state") == (
        0,
        1,
    )


@pytest.mark.parametrize(
    "update",
    [
        {"world_size": 4},
        {"backend": "nccl"},
        {"strategy": "ddp"},
        {"serialized_state": ("model", "optimizer")},
        {"payloads": _manifest().payloads[:-1]},
        {"unexpected": "field"},
    ],
)
def test_distributed_manifest_fails_closed_on_unsupported_or_incomplete_input(
    update: dict[str, object],
) -> None:
    payload = _manifest().model_dump(mode="python")
    payload.update(update)

    with pytest.raises(ValidationError):
        DistributedCheckpointManifest.model_validate(payload)


def test_distributed_attestation_requires_separate_disjoint_rank_groups() -> None:
    attestation = _distributed_attestation()
    payload = attestation.model_dump(mode="python")
    payload["recovery_worker_pids"] = (102, 202)

    with pytest.raises(ValidationError, match="process groups are invalid"):
        RecoveryAttestationV1.model_validate(payload)


def test_distributed_rank_termination_attestation_requires_separate_fault_evidence() -> None:
    payload = _distributed_attestation().model_dump(mode="python")
    payload.update(
        {
            "fault_scenario": "rank_process_termination",
            "distributed_fault_target_rank": 0,
            "distributed_fault_worker_pids": (301, 302),
            "distributed_peer_failure_observer_rank": 1,
            "distributed_failure_event_path": "failure-event.json",
            "distributed_failure_event_sha256": "9" * 64,
        }
    )

    attestation = RecoveryAttestationV1.model_validate(payload)
    assert attestation.distributed_fault_target_rank == 0

    payload["distributed_peer_failure_observer_rank"] = 0
    with pytest.raises(ValidationError, match="process evidence is invalid"):
        RecoveryAttestationV1.model_validate(payload)


def test_distributed_contract_is_exact_and_same_world_size() -> None:
    contract = distributed_fsdp_persistence_contract()
    by_id = {item.state_id: item for item in contract.items}

    assert contract.framework == "pytorch-distributed"
    assert contract.adapter == "pytorch-fsdp"
    assert contract.max_rpo_steps == 0
    assert set(by_id) == {
        "global_step",
        "loss_history",
        "model",
        "numpy_rng",
        "optimizer",
        "python_rng",
        "scheduler",
        "topology",
        "torch_rng",
    }
    assert by_id["topology"].identity_controls == (
        "backend=gloo",
        "implementation=fully_shard",
        "world_size=2",
    )
    assert all(item.exactness == "exact" for item in contract.items)


def test_distributed_schemas_match_checked_files() -> None:
    for filename, expected in distributed_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


@pytest.mark.parametrize(
    "arguments",
    [
        ("--strategy", "ddp"),
        ("--backend", "nccl"),
        ("--world-size", "4"),
        ("--profile", "model-only-inference"),
        ("--fault", "unsupported"),
        ("--fault", "rank-termination"),
        ("--target-rank", "0"),
    ],
)
def test_distributed_cli_rejects_unsupported_contract_without_starting_workers(
    tmp_path: Path,
    arguments: tuple[str, str],
) -> None:
    run_root = tmp_path / "unsupported"
    invocation = CliRunner().invoke(
        app,
        ["qualify", "distributed-pytorch", "--run-dir", str(run_root), *arguments],
    )

    assert invocation.exit_code == 5
    assert "unsupported" in invocation.output.lower() or "could not run" in invocation.output
    assert not run_root.exists()
