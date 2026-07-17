"""Validate and persist secret-free exchanges for both GPT-5.6 roles."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.base import ContractProvider, FailureProvider
from flashpilot.agent.guardrails import (
    assert_safe_contract_request,
    assert_safe_failure_request,
    validate_checkpoint_contract,
    validate_failure_analysis,
)
from flashpilot.domain.agent import (
    AgentCallMetadata,
    AgentRole,
    ContractInferenceRequest,
    ContractValidationResult,
    FailureAnalysis,
    ProviderResponseMetadata,
    RepairPlanValidationResult,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact
from flashpilot.orchestration.artifacts import write_json_artifact


def build_contract_request(
    *,
    adapter: NativePyTorchAdapter,
    user_objective: str,
    hard_rollback_limit_steps: int,
) -> ContractInferenceRequest:
    capabilities = adapter.capabilities()
    request = ContractInferenceRequest(
        user_objective=user_objective,
        hard_rollback_limit_steps=hard_rollback_limit_steps,
        workload_capabilities=capabilities,
        save_restore_summary=adapter.summarize_save_restore("safe_adapter_aware"),
        integrity_protocol=(
            "manifest",
            "checksums",
            "completion_marker",
            "atomic_commit",
            "base_artifact_hash",
        ),
        supported_state=capabilities.supported_state,
        mandatory_gate_requirements=(
            "all applicable Recovery Gate checks remain enabled",
            "only deterministic code can declare recovery",
            "rollback cannot exceed the user hard limit",
        ),
    )
    assert_safe_contract_request(request)
    return request


def _metadata(
    *,
    role: AgentRole,
    schema_version: str,
    request_json: str,
    provider_metadata: ProviderResponseMetadata,
) -> AgentCallMetadata:
    return AgentCallMetadata(
        provider=provider_metadata.provider,
        role=role,
        output_schema_version=schema_version,
        live_or_fixture=provider_metadata.live_or_fixture,
        fixture_provenance=provider_metadata.fixture_provenance,
        response_id=provider_metadata.response_id,
        timestamp=datetime.now(UTC),
        request_sha256=hashlib.sha256(request_json.encode("utf-8")).hexdigest(),
    )


def infer_checkpoint_contract(
    *,
    provider: ContractProvider,
    request: ContractInferenceRequest,
    run_root: Path | None = None,
) -> ContractValidationResult:
    request_json = assert_safe_contract_request(request)
    response = provider.infer_contract(request)
    validation = validate_checkpoint_contract(request, response.output)
    metadata = _metadata(
        role="checkpoint-contract",
        schema_version=response.output.schema_version,
        request_json=request_json,
        provider_metadata=response.provider_metadata,
    )
    if run_root is not None:
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/contract/request.redacted.json",
            value=request.model_dump(mode="json"),
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/contract/response.parsed.json",
            value=response.output,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/contract/validation.json",
            value=validation,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/contract/metadata.json",
            value=metadata,
        )
    return validation


def analyze_recovery_failure(
    *,
    provider: FailureProvider,
    request: SanitizedFailureArtifact,
    run_root: Path | None = None,
) -> tuple[FailureAnalysis, RepairPlanValidationResult]:
    request_json = assert_safe_failure_request(request)
    response = provider.analyze_failure(request)
    validation = validate_failure_analysis(request, response.output)
    metadata = _metadata(
        role="failure-analysis",
        schema_version=response.output.schema_version,
        request_json=request_json,
        provider_metadata=response.provider_metadata,
    )
    if run_root is not None:
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/failure/request.redacted.json",
            value=request.model_dump(mode="json"),
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/failure/response.parsed.json",
            value=response.output,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/failure/validation.json",
            value=validation,
        )
        write_json_artifact(
            run_root=run_root,
            relative_path="agent/failure/metadata.json",
            value=metadata,
        )
    return response.output, validation
