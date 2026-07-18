"""Clearly labeled offline fixture/replay providers."""

from __future__ import annotations

import sysconfig
from pathlib import Path

from flashpilot.agent.guardrails import assert_safe_contract_request, assert_safe_failure_request
from flashpilot.domain.agent import (
    AgentCallMetadata,
    CheckpointContract,
    ContractInferenceRequest,
    ContractProviderResult,
    FailureAnalysis,
    FailureProviderResult,
    ProviderResponseMetadata,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact

_SOURCE_FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "demo"
_INSTALLED_FIXTURE_ROOT = Path(sysconfig.get_path("data")) / "share" / "flashpilot" / "fixtures"


def _fixture_root() -> Path:
    if (_SOURCE_FIXTURE_ROOT / "failure_analysis_fixture.json").is_file():
        return _SOURCE_FIXTURE_ROOT
    return _INSTALLED_FIXTURE_ROOT


FIXTURE_ROOT = _fixture_root()
DEFAULT_CONTRACT_FIXTURE = FIXTURE_ROOT / "contract_fixture.json"
DEFAULT_FAILURE_FIXTURE = FIXTURE_ROOT / "failure_analysis_fixture.json"
DEFAULT_CONTRACT_CAPTURE_METADATA = FIXTURE_ROOT / "contract_fixture.metadata.json"
DEFAULT_FAILURE_CAPTURE_METADATA = FIXTURE_ROOT / "failure_analysis_fixture.metadata.json"


def _load_capture_metadata(path: Path, *, role: str) -> AgentCallMetadata:
    metadata = AgentCallMetadata.model_validate_json(path.read_text(encoding="utf-8"))
    if (
        metadata.provider != "openai"
        or metadata.role != role
        or metadata.source != "captured_live_response"
        or metadata.validation_status != "accepted"
    ):
        raise ValueError("fixture capture metadata is not an accepted live OpenAI response")
    return metadata


class FixtureContractProvider:
    """Replay the accepted typed GPT-5.6 contract capture; no API call occurs."""

    def __init__(
        self,
        fixture_path: Path = DEFAULT_CONTRACT_FIXTURE,
        capture_metadata_path: Path | None = None,
    ) -> None:
        self._fixture_path = fixture_path
        self._capture_metadata_path = capture_metadata_path
        if capture_metadata_path is None and fixture_path == DEFAULT_CONTRACT_FIXTURE:
            self._capture_metadata_path = DEFAULT_CONTRACT_CAPTURE_METADATA

    @property
    def captured_live_metadata(self) -> AgentCallMetadata | None:
        if self._capture_metadata_path is None:
            return None
        return _load_capture_metadata(
            self._capture_metadata_path,
            role="checkpoint-contract",
        )

    def infer_contract(self, request: ContractInferenceRequest) -> ContractProviderResult:
        assert_safe_contract_request(request)
        output = CheckpointContract.model_validate_json(
            self._fixture_path.read_text(encoding="utf-8")
        )
        provenance = (
            "live_gpt_5_6_capture"
            if self.captured_live_metadata is not None
            else "deterministic_local_fixture"
        )
        return ContractProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="fixture",
                live_or_fixture="fixture",
                response_id=None,
                fixture_provenance=provenance,
            ),
        )


class FixtureFailureProvider:
    """Replay the accepted typed GPT-5.6 diagnosis capture; no API call occurs."""

    def __init__(
        self,
        fixture_path: Path = DEFAULT_FAILURE_FIXTURE,
        capture_metadata_path: Path | None = None,
    ) -> None:
        self._fixture_path = fixture_path
        self._capture_metadata_path = capture_metadata_path
        if capture_metadata_path is None and fixture_path == DEFAULT_FAILURE_FIXTURE:
            self._capture_metadata_path = DEFAULT_FAILURE_CAPTURE_METADATA

    @property
    def captured_live_metadata(self) -> AgentCallMetadata | None:
        if self._capture_metadata_path is None:
            return None
        return _load_capture_metadata(
            self._capture_metadata_path,
            role="failure-analysis",
        )

    def analyze_failure(self, request: SanitizedFailureArtifact) -> FailureProviderResult:
        assert_safe_failure_request(request)
        output = FailureAnalysis.model_validate_json(self._fixture_path.read_text(encoding="utf-8"))
        provenance = (
            "live_gpt_5_6_capture"
            if self.captured_live_metadata is not None
            else "deterministic_local_fixture"
        )
        return FailureProviderResult(
            output=output,
            provider_metadata=ProviderResponseMetadata(
                provider="fixture",
                live_or_fixture="fixture",
                response_id=None,
                fixture_provenance=provenance,
            ),
        )
