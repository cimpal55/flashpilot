"""Minimal trainer-adapter contract required by the P0 checkpoint strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from torch import Tensor

from flashpilot.domain.capabilities import SaveRestoreSummary, WorkloadCapabilities
from flashpilot.workload.model import TinyTransformerLanguageModel


class TrainerAdapter(ABC):
    """Describe and partition one controlled training workload."""

    @abstractmethod
    def capabilities(self) -> WorkloadCapabilities:
        """Return a deterministic capability description."""

    @abstractmethod
    def summarize_save_restore(self, strategy_name: str) -> SaveRestoreSummary:
        """Describe exactly what a supported strategy persists and restores."""

    @abstractmethod
    def frozen_base_state(self, model: TinyTransformerLanguageModel) -> dict[str, Tensor]:
        """Extract the immutable non-adapter model state."""

    @abstractmethod
    def trainable_adapter_state(self, model: TinyTransformerLanguageModel) -> dict[str, Tensor]:
        """Extract the trainable adapter state."""

    @abstractmethod
    def restore_partitioned_model(
        self,
        model: TinyTransformerLanguageModel,
        *,
        frozen_base: Mapping[str, Tensor],
        adapter_state: Mapping[str, Tensor],
    ) -> None:
        """Restore both model partitions with strict key validation."""
