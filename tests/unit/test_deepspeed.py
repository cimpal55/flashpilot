from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from flashpilot.attestation.models import RecoveryAttestationV1
from flashpilot.cli import app
from flashpilot.contracts import deepspeed_zero2_persistence_contract
from flashpilot.deepspeed.models import (
    DEEPSPEED_SERIALIZED_STATE,
    DeepSpeedCheckpointManifest,
    DeepSpeedCheckpointPayload,
)
from flashpilot.deepspeed.schema import deepspeed_schema_documents


def _payload(
    role: str,
    path: str,
    *,
    rank: int | None = None,
) -> DeepSpeedCheckpointPayload:
    return DeepSpeedCheckpointPayload(
        role=role,
        path=path,
        sha256="a" * 64,
        size_bytes=1,
        rank=rank,
    )


def _manifest() -> DeepSpeedCheckpointManifest:
    tag = "global_step000004"
    return DeepSpeedCheckpointManifest(
        checkpoint_id="checkpoint-step-000004",
        global_step=4,
        checkpoint_tag=tag,
        created_at=datetime(2026, 7, 20, tzinfo=UTC),
        payloads=(
            _payload("deepspeed-latest", "latest"),
            _payload("deepspeed-conversion-helper", "zero_to_fp32.py"),
            _payload("deepspeed-model-state", f"{tag}/mp_rank_00_model_states.pt"),
            _payload(
                "deepspeed-optimizer-shard",
                f"{tag}/zero_pp_rank_0_mp_rank_00_optim_states.pt",
                rank=0,
            ),
            _payload(
                "deepspeed-optimizer-shard",
                f"{tag}/zero_pp_rank_1_mp_rank_00_optim_states.pt",
                rank=1,
            ),
            _payload("rank-state", "rank-state-000.json", rank=0),
            _payload("rank-state", "rank-state-001.json", rank=1),
        ),
    )


def _attestation() -> RecoveryAttestationV1:
    return RecoveryAttestationV1(
        framework="deepspeed",
        framework_version="0.19.2",
        adapter="deepspeed-engine",
        run_id="deepspeed-run",
        issued_at=datetime(2026, 7, 20, tzinfo=UTC),
        code_commit="a" * 40,
        source_tree_state="clean",
        dependency_environment_sha256="b" * 64,
        checkpoint_path="checkpoints/checkpoint-step-000004",
        checkpoint_sha256="c" * 64,
        checkpoint_file_count=10,
        checkpoint_logical_bytes=100,
        persistence_contract_sha256="d" * 64,
        evidence_manifest_sha256="e" * 64,
        fault_scenario="checkpoint_restart",
        distributed_strategy="zero",
        distributed_implementation="zero-stage-2",
        distributed_backend="gloo",
        distributed_world_size=2,
        distributed_zero_stage=2,
        original_worker_pid=101,
        recovery_worker_pid=201,
        original_worker_pids=(101, 102),
        recovery_worker_pids=(201, 202),
        control_digest="f" * 64,
        resumed_digest="f" * 64,
        control_evaluation_digest="1" * 64,
        resumed_evaluation_digest="1" * 64,
        checks_passed=30,
        checks_total=30,
        rpo_steps=0,
        max_rpo_steps=0,
        rto_seconds=1.0,
        verified_persisted_bytes=100,
        limitations=("Same-world-size two-rank qualification only.",),
    )


def test_deepspeed_manifest_requires_exact_zero2_layout_and_state() -> None:
    manifest = _manifest()

    assert manifest.world_size == 2
    assert manifest.strategy == "zero"
    assert manifest.implementation == "zero-stage-2"
    assert manifest.zero_stage == 2
    assert manifest.backend == "gloo"
    assert manifest.serialized_state == DEEPSPEED_SERIALIZED_STATE
    assert tuple(
        payload.rank for payload in manifest.payloads if payload.role == "deepspeed-optimizer-shard"
    ) == (0, 1)


@pytest.mark.parametrize(
    "update",
    [
        {"world_size": 4},
        {"backend": "nccl"},
        {"zero_stage": 3},
        {"checkpoint_tag": "global_step000005"},
        {"serialized_state": ("model", "optimizer")},
        {"payloads": _manifest().payloads[:-1]},
        {"unexpected": "field"},
    ],
)
def test_deepspeed_manifest_fails_closed_on_unsupported_or_incomplete_input(
    update: dict[str, object],
) -> None:
    payload = _manifest().model_dump(mode="python")
    payload.update(update)

    with pytest.raises(ValidationError):
        DeepSpeedCheckpointManifest.model_validate(payload)


@pytest.mark.parametrize(
    "update",
    [
        {"distributed_zero_stage": None},
        {"distributed_strategy": "fsdp"},
        {"distributed_implementation": "fully_shard"},
        {"adapter": "pytorch-fsdp"},
        {"recovery_worker_pids": (102, 202)},
    ],
)
def test_deepspeed_attestation_fails_closed_on_wrong_identity(
    update: dict[str, object],
) -> None:
    payload = _attestation().model_dump(mode="python")
    payload.update(update)

    with pytest.raises(ValidationError):
        RecoveryAttestationV1.model_validate(payload)


def test_deepspeed_contract_is_exact_same_world_size_zero2() -> None:
    contract = deepspeed_zero2_persistence_contract()
    by_id = {item.state_id: item for item in contract.items}

    assert contract.framework == "deepspeed"
    assert contract.adapter == "deepspeed-engine"
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
        "world_size=2",
        "zero_stage=2",
    )
    assert all(item.exactness == "exact" for item in contract.items)


def test_deepspeed_schemas_match_checked_files() -> None:
    for filename, expected in deepspeed_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


@pytest.mark.parametrize(
    "arguments",
    [
        ("--zero-stage", "3"),
        ("--backend", "nccl"),
        ("--world-size", "4"),
        ("--profile", "model-only-inference"),
        ("--fault", "unsupported"),
        ("--fault", "rank-termination"),
        ("--target-rank", "0"),
    ],
)
def test_deepspeed_cli_rejects_unsupported_contract_without_starting_workers(
    tmp_path: Path,
    arguments: tuple[str, str],
) -> None:
    run_root = tmp_path / "unsupported"
    invocation = CliRunner().invoke(
        app,
        ["qualify", "deepspeed", "--run-dir", str(run_root), *arguments],
    )

    assert invocation.exit_code == 5
    assert "unsupported" in invocation.output.lower() or "could not run" in invocation.output
    assert not run_root.exists()


@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows fail-closed path")
def test_deepspeed_cli_rejects_windows_before_creating_run_directory(tmp_path: Path) -> None:
    run_root = tmp_path / "windows-rejected"
    invocation = CliRunner().invoke(
        app,
        ["qualify", "deepspeed", "--run-dir", str(run_root)],
    )

    assert invocation.exit_code == 5
    assert "requires a Linux host" in invocation.output
    assert not run_root.exists()
