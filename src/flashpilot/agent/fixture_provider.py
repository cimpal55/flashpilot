"""Clearly labeled offline fixture/replay providers."""

from __future__ import annotations

from pathlib import Path

from flashpilot.agent.guardrails import assert_safe_contract_request, assert_safe_failure_request
from flashpilot.domain.agent import (
    CheckpointContract,
    ContractInferenceRequest,
    ContractProviderResult,
    FailureAnalysis,
    FailureProviderResult,
    ProviderResponseMetadata,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact

_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_FIXTURE = _REPOSITORY_ROOT / "demo" / "contract_fixture.json"
DEFAULT_FAILURE_FIXTURE = _REPOSITORY_ROOT / "demo" / "failure_analysis_fixture.json"


class FixtureContractProvider:
    """Replay a typed deterministic-local contract fixture; no API call occurs."""

    def __init__(self, fixture_path: Path = DEFAULT_CONTRACT_FIXTURE) -> None:
        self._fixture_path = fixture_path

    def infer_contract(self, request: ContractInferenceRequest) -> ContractProviderResult:
        assert_safe_contract_request(request)
        output = CheckpointContract.model_validate_json(
            self._fixture_path.read_text(encoding="utf-8")
        )
        return ContractProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="fixture",
                live_or_fixture="fixture",
                response_id=None,
                fixture_provenance="deterministic_local_fixture",
            ),
        )


class FixtureFailureProvider:
    """Replay a typed deterministic-local diagnosis fixture; no API call occurs."""

    def __init__(self, fixture_path: Path = DEFAULT_FAILURE_FIXTURE) -> None:
        self._fixture_path = fixture_path

    def analyze_failure(self, request: SanitizedFailureArtifact) -> FailureProviderResult:
        assert_safe_failure_request(request)
        output = FailureAnalysis.model_validate_json(self._fixture_path.read_text(encoding="utf-8"))
        return FailureProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="fixture",
                live_or_fixture="fixture",
                response_id=None,
                fixture_provenance="deterministic_local_fixture",
            ),
        )
