"""Validate and persist secret-free exchanges for both GPT-5.6 roles."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.base import ContractProvider, FailureProvider
from flashpilot.agent.guardrails import (
    GuardrailViolation,
    assert_safe_contract_request,
    assert_safe_failure_request,
    validate_checkpoint_contract,
    validate_failure_analysis,
)
from flashpilot.agent.prompts import CONTRACT_PROMPT_VERSION, FAILURE_PROMPT_VERSION
from flashpilot.domain.agent import (
    AgentCallMetadata,
    AgentRole,
    AgentValidationRejection,
    ContractInferenceRequest,
    ContractValidationResult,
    FailureAnalysis,
    ProviderResponseMetadata,
    RepairPlanValidationResult,
    ValidationStatus,
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
    validation_status: ValidationStatus,
) -> AgentCallMetadata:
    if provider_metadata.provider == "openai":
        source = "captured_live_response"
    elif provider_metadata.fixture_provenance == "live_gpt_5_6_capture":
        source = "captured_live_response_replay"
    else:
        source = "deterministic_local_fixture"
    return AgentCallMetadata(
        provider=provider_metadata.provider,
        role=role,
        prompt_version=(
            CONTRACT_PROMPT_VERSION if role == "checkpoint-contract" else FAILURE_PROMPT_VERSION
        ),
        output_schema_version=schema_version,
        live_or_fixture=provider_metadata.live_or_fixture,
        source=source,
        fixture_provenance=provider_metadata.fixture_provenance,
        response_id=provider_metadata.response_id,
        timestamp=datetime.now(UTC),
        request_sha256=hashlib.sha256(request_json.encode("utf-8")).hexdigest(),
        validation_status=validation_status,
    )


def _persist_exchange(
    *,
    run_root: Path,
    role_directory: str,
    request: BaseModel,
    response: BaseModel,
    metadata: AgentCallMetadata,
    validation: BaseModel,
    rejected: bool,
) -> None:
    prefix = f"agent/{role_directory}"
    response_name = "response.parsed.rejected.json" if rejected else "response.parsed.json"
    validation_name = "validation.rejected.json" if rejected else "validation.json"
    write_json_artifact(
        run_root=run_root,
        relative_path=f"{prefix}/request.redacted.json",
        value=request,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=f"{prefix}/{response_name}",
        value=response,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=f"{prefix}/metadata.json",
        value=metadata,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=f"{prefix}/{validation_name}",
        value=validation,
    )


def infer_checkpoint_contract(
    *,
    provider: ContractProvider,
    request: ContractInferenceRequest,
    run_root: Path | None = None,
) -> ContractValidationResult:
    request_json = assert_safe_contract_request(request)
    response = provider.infer_contract(request)
    try:
        validation = validate_checkpoint_contract(request, response.output)
    except GuardrailViolation as error:
        metadata = _metadata(
            role="checkpoint-contract",
            schema_version=response.output.schema_version,
            request_json=request_json,
            provider_metadata=response.provider_metadata,
            validation_status="rejected",
        )
        if run_root is not None:
            _persist_exchange(
                run_root=run_root,
                role_directory="contract",
                request=request,
                response=response.output,
                metadata=metadata,
                validation=AgentValidationRejection(reason=str(error)),
                rejected=True,
            )
        raise
    metadata = _metadata(
        role="checkpoint-contract",
        schema_version=response.output.schema_version,
        request_json=request_json,
        provider_metadata=response.provider_metadata,
        validation_status="accepted",
    )
    if run_root is not None:
        _persist_exchange(
            run_root=run_root,
            role_directory="contract",
            request=request,
            response=response.output,
            metadata=metadata,
            validation=validation,
            rejected=False,
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
    try:
        validation = validate_failure_analysis(request, response.output)
    except GuardrailViolation as error:
        metadata = _metadata(
            role="failure-analysis",
            schema_version=response.output.schema_version,
            request_json=request_json,
            provider_metadata=response.provider_metadata,
            validation_status="rejected",
        )
        if run_root is not None:
            _persist_exchange(
                run_root=run_root,
                role_directory="failure",
                request=request,
                response=response.output,
                metadata=metadata,
                validation=AgentValidationRejection(reason=str(error)),
                rejected=True,
            )
        raise
    metadata = _metadata(
        role="failure-analysis",
        schema_version=response.output.schema_version,
        request_json=request_json,
        provider_metadata=response.provider_metadata,
        validation_status="accepted",
    )
    if run_root is not None:
        _persist_exchange(
            run_root=run_root,
            role_directory="failure",
            request=request,
            response=response.output,
            metadata=metadata,
            validation=validation,
            rejected=False,
        )
    return response.output, validation
