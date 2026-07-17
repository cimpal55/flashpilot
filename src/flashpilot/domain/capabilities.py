"""Deterministic descriptions of the supported workload and checkpoint state."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

StateName = Literal[
    "model",
    "adapter",
    "optimizer",
    "scheduler",
    "scaler",
    "global_step",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "torch_cuda_rng",
    "sampler",
    "base_model_identity",
]


class StrictCapabilityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkloadCapabilities(StrictCapabilityModel):
    adapter_name: str
    framework: Literal["native-pytorch"]
    has_frozen_base: bool
    has_trainable_adapter: bool
    optimizer_type: str
    scheduler_type: str | None
    uses_dropout: bool
    uses_python_rng: bool
    uses_numpy_rng: bool
    uses_torch_rng: bool
    uses_cuda_rng: bool
    batch_position_is_step_derived: bool
    supported_state: tuple[StateName, ...]
    supported_repair_actions: tuple[str, ...]
    assumptions: tuple[str, ...] = Field(default_factory=tuple)


class SaveRestoreSummary(StrictCapabilityModel):
    checkpoint_strategy: str
    serialized_state: tuple[StateName, ...]
    restored_state: tuple[StateName, ...]
    restore_order: tuple[str, ...]
    integrity_controls: tuple[str, ...]
    completion_protocol: tuple[str, ...]
    immutable_artifacts: tuple[str, ...]
    omitted_state: tuple[StateName, ...]
    sanitized_source_snippets: tuple[str, ...] = Field(default_factory=tuple)
