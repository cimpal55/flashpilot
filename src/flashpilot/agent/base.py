"""Provider protocols for the two permitted model roles."""

from __future__ import annotations

from typing import Protocol

from flashpilot.domain.agent import (
    ContractInferenceRequest,
    ContractProviderResult,
    FailureProviderResult,
)
from flashpilot.domain.recovery import SanitizedFailureArtifact


class ContractProvider(Protocol):
    def infer_contract(self, request: ContractInferenceRequest) -> ContractProviderResult:
        """Return one typed checkpoint contract."""


class FailureProvider(Protocol):
    def analyze_failure(self, request: SanitizedFailureArtifact) -> FailureProviderResult:
        """Return one typed diagnosis and bounded repair plan."""
