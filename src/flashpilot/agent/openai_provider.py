"""Official OpenAI Responses API providers for the two permitted roles."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from flashpilot.agent.guardrails import (
    assert_safe_contract_request,
    assert_safe_failure_request,
)
from flashpilot.agent.prompts import (
    CONTRACT_SYSTEM_PROMPT,
    FAILURE_SYSTEM_PROMPT,
    MODEL_ALIAS,
)
from flashpilot.domain.agent import (
    CheckpointContract,
    ContractInferenceRequest,
    ContractProviderResult,
    FailureAnalysis,
    FailureProviderResult,
    ProviderResponseMetadata,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact
from flashpilot.verification.failure_artifact import assert_sanitized_failure_payload


class OpenAIProviderError(RuntimeError):
    """Raised when a live structured response is absent or unusable."""


def _response_id(response: Any) -> str | None:
    value = getattr(response, "id", None)
    return value if isinstance(value, str) and value else None


class OpenAIContractProvider:
    """Live GPT-5.6 checkpoint-contract inference through Responses.parse."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client if client is not None else OpenAI()

    def infer_contract(self, request: ContractInferenceRequest) -> ContractProviderResult:
        serialized = assert_safe_contract_request(request)
        response = self._client.responses.parse(
            model=MODEL_ALIAS,
            input=[
                {"role": "system", "content": CONTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": serialized},
            ],
            text_format=CheckpointContract,
            store=False,
        )
        output = getattr(response, "output_parsed", None)
        if not isinstance(output, CheckpointContract):
            raise OpenAIProviderError("live contract response did not contain parsed output")
        return ContractProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="openai",
                live_or_fixture="live",
                response_id=_response_id(response),
                fixture_provenance="not_applicable",
            ),
        )


class OpenAIFailureProvider:
    """Live GPT-5.6 blind diagnosis through Responses.parse."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client if client is not None else OpenAI()

    def analyze_failure(self, request: SanitizedFailureArtifact) -> FailureProviderResult:
        serialized = assert_safe_failure_request(request)
        assert_sanitized_failure_payload(f"{FAILURE_SYSTEM_PROMPT}\n{serialized}")
        response = self._client.responses.parse(
            model=MODEL_ALIAS,
            input=[
                {"role": "system", "content": FAILURE_SYSTEM_PROMPT},
                {"role": "user", "content": serialized},
            ],
            text_format=FailureAnalysis,
            store=False,
        )
        output = getattr(response, "output_parsed", None)
        if not isinstance(output, FailureAnalysis):
            raise OpenAIProviderError("live failure response did not contain parsed output")
        return FailureProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="openai",
                live_or_fixture="live",
                response_id=_response_id(response),
                fixture_provenance="not_applicable",
            ),
        )
