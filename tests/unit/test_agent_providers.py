from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.fixture_provider import FixtureContractProvider, FixtureFailureProvider
from flashpilot.agent.guardrails import GuardrailViolation
from flashpilot.agent.openai_provider import (
    OpenAIContractProvider,
    OpenAIFailureProvider,
    OpenAIProviderError,
)
from flashpilot.agent.service import (
    analyze_recovery_failure,
    build_contract_request,
    infer_checkpoint_contract,
)
from flashpilot.domain.agent import (
    CheckpointContract,
    FailureAnalysis,
    FailureProviderResult,
    ProviderResponseMetadata,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact
from flashpilot.verification.failure_artifact import FORBIDDEN_FAILURE_PAYLOAD_TERMS


def contract_request():
    return build_contract_request(
        adapter=NativePyTorchAdapter(),
        user_objective=(
            "Lose no completed steps. Recovery correctness is more important than checkpoint size."
        ),
        hard_rollback_limit_steps=0,
    )


def failure_request() -> SanitizedFailureArtifact:
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
            {
                "check_id": check_id,
                "status": "fail",
                "evidence_ids": [evidence_id],
            }
            for check_id, evidence_id in failed
        ),
        state_differences={"optimizer_match": False, "torch_rng_match": False},
        trajectory_summary={"loss_history_match": False, "final_trainable_match": False},
        integrity_summary={"checksums_valid": True, "checkpoint_load_succeeded": True},
        crash_metadata={"checkpoint_step": 4, "termination_exit_code": 1},
        evidence_catalog=evidence,
    )


class RecordingResponses:
    def __init__(self, output: Any, *, response_id: str = "resp_fixture") -> None:
        self.output = output
        self.response_id = response_id
        self.calls: list[dict[str, Any]] = []

    def parse(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(id=self.response_id, output_parsed=self.output)


class RecordingClient:
    def __init__(self, output: Any) -> None:
        self.responses = RecordingResponses(output)


def test_contract_fixture_is_typed_labeled_and_guarded(tmp_path: Path) -> None:
    request = contract_request()
    validation = infer_checkpoint_contract(
        provider=FixtureContractProvider(),
        request=request,
        run_root=tmp_path / "run",
    )

    assert validation.contract.rollback_limit_steps == 0
    assert validation.added_integrity_controls == ()
    assert validation.unsupported_required_state == ()
    metadata = json.loads(
        (tmp_path / "run/agent/contract/metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["provider"] == "fixture"
    assert metadata["live_or_fixture"] == "fixture"
    assert metadata["source"] == "deterministic_local_fixture"
    assert metadata["fixture_provenance"] == "deterministic_local_fixture"
    assert metadata["model"] == "gpt-5.6"
    assert metadata["store"] is False
    assert metadata["validation_status"] == "accepted"
    assert "api_key" not in json.dumps(metadata).lower()


def test_failure_fixture_is_typed_labeled_and_accepts_six_actions(tmp_path: Path) -> None:
    request = failure_request()
    analysis, validation = analyze_recovery_failure(
        provider=FixtureFailureProvider(),
        request=request,
        run_root=tmp_path / "run",
    )

    assert analysis.confidence == "high"
    assert validation.accepted_actions == (
        "persist_optimizer_state",
        "persist_scheduler_state",
        "persist_python_rng_state",
        "persist_numpy_rng_state",
        "persist_torch_rng_state",
        "restore_state_before_next_batch",
    )
    assert validation.rejected_actions == ()
    assert validation.unsupported_actions == ()
    assert validation.execution_performed is False
    metadata = json.loads(
        (tmp_path / "run/agent/failure/metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["live_or_fixture"] == "fixture"
    assert metadata["source"] == "deterministic_local_fixture"
    assert metadata["fixture_provenance"] == "deterministic_local_fixture"
    assert metadata["validation_status"] == "accepted"


@pytest.mark.parametrize("forbidden", FORBIDDEN_FAILURE_PAYLOAD_TERMS)
def test_failure_provider_input_contains_no_forbidden_disclosure(forbidden: str) -> None:
    client = RecordingClient(FixtureFailureProvider().analyze_failure(failure_request()).output)
    OpenAIFailureProvider(client).analyze_failure(failure_request())
    call = client.responses.calls[0]
    serialized_input = json.dumps(call["input"], sort_keys=True).lower()

    assert forbidden not in serialized_input


def test_live_contract_provider_uses_responses_parse_structured_output_and_no_storage() -> None:
    fixture = FixtureContractProvider().infer_contract(contract_request()).output
    client = RecordingClient(fixture)
    result = OpenAIContractProvider(client).infer_contract(contract_request())
    call = client.responses.calls[0]

    assert result.output == fixture
    assert result.provider_metadata.live_or_fixture == "live"
    assert call["model"] == "gpt-5.6"
    assert call["text_format"] is CheckpointContract
    assert call["store"] is False
    assert "tools" not in call


def test_live_failure_provider_uses_responses_parse_structured_output_and_no_storage() -> None:
    fixture = FixtureFailureProvider().analyze_failure(failure_request()).output
    client = RecordingClient(fixture)
    result = OpenAIFailureProvider(client).analyze_failure(failure_request())
    call = client.responses.calls[0]

    assert result.output == fixture
    assert result.provider_metadata.live_or_fixture == "live"
    assert call["model"] == "gpt-5.6"
    assert call["text_format"] is FailureAnalysis
    assert call["store"] is False
    assert "tools" not in call


def test_live_provider_fails_if_parsed_output_is_absent() -> None:
    client = RecordingClient(None)

    with pytest.raises(OpenAIProviderError, match="parsed output"):
        OpenAIContractProvider(client).infer_contract(contract_request())


def test_live_provider_fails_if_response_id_is_absent() -> None:
    fixture = FixtureContractProvider().infer_contract(contract_request()).output
    client = RecordingClient(fixture)
    client.responses.response_id = ""

    with pytest.raises(OpenAIProviderError, match="response ID"):
        OpenAIContractProvider(client).infer_contract(contract_request())


def test_fixture_provider_rejects_invalid_structured_output(tmp_path: Path) -> None:
    fixture = tmp_path / "invalid.json"
    fixture.write_text('{"schema_version":"checkpoint-contract-v1","extra":true}', encoding="utf-8")

    with pytest.raises(ValidationError):
        FixtureContractProvider(fixture).infer_contract(contract_request())


def test_provider_metadata_rejects_mislabeled_live_and_fixture_sources() -> None:
    with pytest.raises(ValidationError, match="must be labeled live"):
        ProviderResponseMetadata(
            provider="openai",
            live_or_fixture="fixture",
            response_id=None,
            fixture_provenance="deterministic_local_fixture",
        )
    with pytest.raises(ValidationError, match="without response ID"):
        ProviderResponseMetadata(
            provider="fixture",
            live_or_fixture="fixture",
            response_id="not-allowed",
            fixture_provenance="live_gpt_5_6_capture",
        )


def test_rejected_live_failure_output_is_preserved_with_audit_metadata(
    tmp_path: Path,
) -> None:
    request = failure_request()
    fixture = FixtureFailureProvider().analyze_failure(request).output
    rejected_output = fixture.model_copy(
        update={
            "affected_gate_checks": fixture.affected_gate_checks
            + ("state.optimizer [restore:optimizer-state]",)
        }
    )

    class RejectedLiveProvider:
        def analyze_failure(self, _: SanitizedFailureArtifact) -> FailureProviderResult:
            return FailureProviderResult(
                output=rejected_output,
                provider_metadata=ProviderResponseMetadata(
                    provider="openai",
                    live_or_fixture="live",
                    response_id="resp_rejected_live",
                    fixture_provenance="not_applicable",
                ),
            )

    run_root = tmp_path / "rejected-live"
    with pytest.raises(GuardrailViolation, match="unknown gate checks"):
        analyze_recovery_failure(
            provider=RejectedLiveProvider(),
            request=request,
            run_root=run_root,
        )

    artifact_root = run_root / "agent/failure"
    persisted_response = json.loads(
        (artifact_root / "response.parsed.rejected.json").read_text(encoding="utf-8")
    )
    metadata = json.loads((artifact_root / "metadata.json").read_text(encoding="utf-8"))
    rejection = json.loads((artifact_root / "validation.rejected.json").read_text(encoding="utf-8"))
    assert (artifact_root / "request.redacted.json").is_file()
    assert persisted_response == rejected_output.model_dump(mode="json")
    assert metadata["provider"] == "openai"
    assert metadata["model"] == "gpt-5.6"
    assert metadata["source"] == "captured_live_response"
    assert metadata["live_or_fixture"] == "live"
    assert metadata["response_id"] == "resp_rejected_live"
    assert metadata["store"] is False
    assert metadata["validation_status"] == "rejected"
    assert rejection["validation_status"] == "rejected"
    assert rejection["error_type"] == "GuardrailViolation"
    assert "unknown gate checks" in rejection["reason"]
    assert "state.optimizer [restore:optimizer-state]" in rejection["reason"]
    assert not (artifact_root / "response.parsed.json").exists()
    assert not (artifact_root / "validation.json").exists()
