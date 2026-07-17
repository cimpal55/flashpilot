from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

import flashpilot.cli as cli
from flashpilot.agent.fixture_provider import FixtureContractProvider, FixtureFailureProvider
from flashpilot.agent.guardrails import assert_safe_contract_request, assert_safe_failure_request
from flashpilot.domain.agent import (
    ContractInferenceRequest,
    ContractProviderResult,
    FailureProviderResult,
    ProviderResponseMetadata,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact


def _failure_request() -> SanitizedFailureArtifact:
    failed = (
        ("state.optimizer", "restore:optimizer-state"),
        ("state.scheduler", "restore:scheduler-state"),
        ("state.python_rng", "restore:python-rng"),
        ("state.numpy_rng", "restore:numpy-rng"),
        ("state.torch_rng", "restore:torch-rng"),
        ("trajectory.final_trainable", "trajectory:final-trainable"),
        ("trajectory.final_evaluation", "trajectory:final-evaluation"),
        ("trajectory.loss_history", "trajectory:loss-history"),
        ("contract.no_mandatory_omission", "contract:mandatory-state"),
    )
    evidence = {
        evidence_id: f"Observed evidence for {check_id}" for check_id, evidence_id in failed
    }
    evidence["process:next-step"] = "Recovery continued at the expected next step"
    return SanitizedFailureArtifact(
        user_objective={"recovery_correctness": "strict", "hard_rollback_limit_steps": 0},
        workload_capabilities={"framework": "native-pytorch", "uses_dropout": True},
        checkpoint_contract={"correctness_priority": "strict"},
        save_restore_summary={"restored_global_step": 4},
        manifest_summary={"global_step": 4, "serialized_state": ["adapter", "global_step"]},
        restore_order=(
            "validate integrity metadata",
            "load declared model state",
            "resume from restored step",
        ),
        gate_checks=tuple(
            {"check_id": check_id, "status": "fail", "evidence_ids": [evidence_id]}
            for check_id, evidence_id in failed
        ),
        state_differences={"optimizer_match": False, "torch_rng_match": False},
        trajectory_summary={"loss_history_match": False, "final_trainable_match": False},
        integrity_summary={"checksums_valid": True, "checkpoint_load_succeeded": True},
        crash_metadata={"checkpoint_step": 4, "termination_exit_code": 1},
        evidence_catalog=evidence,
    )


class RecordingLiveContractProvider:
    def __init__(self) -> None:
        self.calls: list[ContractInferenceRequest] = []

    def infer_contract(self, request: ContractInferenceRequest) -> ContractProviderResult:
        self.calls.append(request)
        output = FixtureContractProvider().infer_contract(request).output
        return ContractProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="openai",
                live_or_fixture="live",
                response_id="resp_live_contract",
                fixture_provenance="not_applicable",
            ),
        )


class RecordingLiveFailureProvider:
    def __init__(self) -> None:
        self.calls: list[SanitizedFailureArtifact] = []

    def analyze_failure(self, request: SanitizedFailureArtifact) -> FailureProviderResult:
        self.calls.append(request)
        output = FixtureFailureProvider().analyze_failure(request).output
        return FailureProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="openai",
                live_or_fixture="live",
                response_id="resp_live_failure",
                fixture_provenance="not_applicable",
            ),
        )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_live_contract_command_makes_one_guarded_call_and_records_provenance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    provider = RecordingLiveContractProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-not-a-real-key")
    monkeypatch.setattr(cli, "OpenAIContractProvider", lambda: provider)
    run_dir = tmp_path / "live-contract"

    result = CliRunner().invoke(cli.app, ["live-contract", "--run-dir", str(run_dir)])

    assert result.exit_code == 0, result.output
    assert len(provider.calls) == 1
    metadata = _read_json(run_dir / "agent/contract/metadata.json")
    request_json = assert_safe_contract_request(provider.calls[0])
    assert metadata["provider"] == "openai"
    assert metadata["model"] == "gpt-5.6"
    assert metadata["source"] == "captured_live_response"
    assert metadata["response_id"] == "resp_live_contract"
    assert metadata["request_sha256"] == hashlib.sha256(request_json.encode()).hexdigest()
    assert metadata["store"] is False
    assert metadata["validation_status"] == "accepted"
    assert "test-only-not-a-real-key" not in json.dumps(metadata)


def test_live_failure_command_uses_only_fixed_capture_and_makes_one_guarded_call(
    tmp_path: Path,
    monkeypatch,
) -> None:
    request = _failure_request()
    captured_request = tmp_path / "request.redacted.json"
    captured_request.write_text(request.model_dump_json(indent=2), encoding="utf-8")
    provider = RecordingLiveFailureProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-not-a-real-key")
    monkeypatch.setattr(cli, "_CAPTURED_FAILURE_REQUEST", captured_request)
    monkeypatch.setattr(cli, "OpenAIFailureProvider", lambda: provider)
    run_dir = tmp_path / "live-failure"

    result = CliRunner().invoke(cli.app, ["live-failure", "--run-dir", str(run_dir)])

    assert result.exit_code == 0, result.output
    assert provider.calls == [request]
    metadata = _read_json(run_dir / "agent/failure/metadata.json")
    request_json = assert_safe_failure_request(request)
    assert metadata["provider"] == "openai"
    assert metadata["source"] == "captured_live_response"
    assert metadata["response_id"] == "resp_live_failure"
    assert metadata["request_sha256"] == hashlib.sha256(request_json.encode()).hexdigest()
    assert metadata["validation_status"] == "accepted"
    validation = _read_json(run_dir / "agent/failure/validation.json")
    assert validation["execution_performed"] is False
    assert "test-only-not-a-real-key" not in json.dumps(metadata)
