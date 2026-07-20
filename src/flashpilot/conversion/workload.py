"""Deterministic model representation and training-state conversion helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path

import torch
from torch import Tensor
from torch.nn import functional

from flashpilot.checkpoints.strategies import capture_rng_state, restore_rng_state
from flashpilot.conversion.artifacts import (
    ConversionArtifactError,
    ValidatedConversionArtifact,
    safe_load_torch_payload,
)
from flashpilot.conversion.models import UpgradedTrainingStateV2
from flashpilot.workload.control import run_control
from flashpilot.workload.profiles import get_profile
from flashpilot.workload.state import ControlRunSummary, state_digest
from flashpilot.workload.trainer import (
    TrainingRuntime,
    create_training_runtime,
    summarize_runtime,
    train_until,
)

CONVERSION_SEED = 20_260_720
INPUT_WIDTH = 6
OUTPUT_WIDTH = 5
ADAPTER_RANK = 2
ADAPTER_SCALE = 0.25
MERGE_ATOL = 1e-12
MERGE_RTOL = 1e-12
VERSION_CHECKPOINT_STEP = 4


def _require_tensor_mapping(value: object, *, label: str) -> dict[str, Tensor]:
    if not isinstance(value, Mapping) or not all(
        isinstance(key, str) and isinstance(tensor, Tensor) for key, tensor in value.items()
    ):
        raise ConversionArtifactError(f"{label} must be a string-to-tensor mapping")
    return {key: tensor.detach().cpu() for key, tensor in value.items()}


def build_full_model_state() -> dict[str, Tensor]:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(CONVERSION_SEED)
    base_weight = torch.randn(
        OUTPUT_WIDTH,
        INPUT_WIDTH,
        dtype=torch.float64,
        generator=generator,
    )
    base_bias = torch.randn(OUTPUT_WIDTH, dtype=torch.float64, generator=generator)
    adapter_a = torch.randn(
        ADAPTER_RANK,
        INPUT_WIDTH,
        dtype=torch.float64,
        generator=generator,
    )
    adapter_b = torch.randn(
        OUTPUT_WIDTH,
        ADAPTER_RANK,
        dtype=torch.float64,
        generator=generator,
    )
    return {
        "model.bias": base_bias.clone(),
        "model.weight": base_weight + ADAPTER_SCALE * (adapter_b @ adapter_a),
        "reference_base.bias": base_bias,
        "reference_base.weight": base_weight,
    }


def split_full_to_peft(
    state: Mapping[str, Tensor],
) -> tuple[dict[str, Tensor], dict[str, Tensor]]:
    expected = {
        "model.bias",
        "model.weight",
        "reference_base.bias",
        "reference_base.weight",
    }
    if set(state) != expected:
        raise ConversionArtifactError("full model state has an unsupported parameter inventory")
    delta = state["model.weight"] - state["reference_base.weight"]
    left, singular_values, right = torch.linalg.svd(delta, full_matrices=False)
    if torch.any(singular_values[ADAPTER_RANK:] > MERGE_ATOL):
        raise ConversionArtifactError("full-model delta exceeds the supported PEFT rank")
    adapter_b = left[:, :ADAPTER_RANK] * singular_values[:ADAPTER_RANK]
    adapter_a = right[:ADAPTER_RANK, :]
    base = {
        "base.bias": state["reference_base.bias"].detach().cpu(),
        "base.weight": state["reference_base.weight"].detach().cpu(),
    }
    adapter = {
        "adapter.a": adapter_a.detach().cpu(),
        "adapter.b": adapter_b.detach().cpu(),
        "adapter.scale": torch.tensor(1.0, dtype=torch.float64),
    }
    return base, adapter


def reconstruct_full_state(
    base: Mapping[str, Tensor],
    adapter: Mapping[str, Tensor],
) -> dict[str, Tensor]:
    if set(base) != {"base.bias", "base.weight"} or set(adapter) != {
        "adapter.a",
        "adapter.b",
        "adapter.scale",
    }:
        raise ConversionArtifactError("PEFT state has an unsupported parameter inventory")
    return {**base, **adapter}


def merge_peft_state(
    base: Mapping[str, Tensor],
    adapter: Mapping[str, Tensor],
) -> dict[str, Tensor]:
    full = reconstruct_full_state(base, adapter)
    merged_weight = full["base.weight"] + full["adapter.scale"] * (
        full["adapter.b"] @ full["adapter.a"]
    )
    return {
        "bias": full["base.bias"].detach().cpu(),
        "weight": merged_weight.detach().cpu(),
    }


def full_effective_state(state: Mapping[str, Tensor]) -> dict[str, Tensor]:
    if set(state) != {
        "model.bias",
        "model.weight",
        "reference_base.bias",
        "reference_base.weight",
    }:
        raise ConversionArtifactError("full model state has an unsupported parameter inventory")
    return {
        "bias": state["model.bias"].detach().cpu(),
        "weight": state["model.weight"].detach().cpu(),
    }


def fixed_inputs() -> Tensor:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(CONVERSION_SEED + 999_983)
    return torch.randn(7, INPUT_WIDTH, dtype=torch.float64, generator=generator)


def evaluate_full_state(state: Mapping[str, Tensor]) -> Tensor:
    full = reconstruct_full_state(
        {key: state[key] for key in ("base.bias", "base.weight")},
        {key: state[key] for key in ("adapter.a", "adapter.b", "adapter.scale")},
    )
    inputs = fixed_inputs()
    base_output = functional.linear(inputs, full["base.weight"], full["base.bias"])
    adapter_output = functional.linear(
        functional.linear(inputs, full["adapter.a"]),
        full["adapter.b"],
    )
    return base_output + full["adapter.scale"] * adapter_output


def evaluate_peft_state(
    base: Mapping[str, Tensor],
    adapter: Mapping[str, Tensor],
) -> Tensor:
    return evaluate_full_state(reconstruct_full_state(base, adapter))


def evaluate_merged_state(state: Mapping[str, Tensor]) -> Tensor:
    if set(state) != {"bias", "weight"}:
        raise ConversionArtifactError("merged state has an unsupported parameter inventory")
    return functional.linear(fixed_inputs(), state["weight"], state["bias"])


def exact_tensor_mapping_equal(
    left: Mapping[str, Tensor],
    right: Mapping[str, Tensor],
) -> bool:
    return set(left) == set(right) and all(torch.equal(left[key], right[key]) for key in left)


def maximum_absolute_difference(left: Tensor, right: Tensor) -> float:
    if left.shape != right.shape:
        return float("inf")
    return float((left - right).abs().max().item())


def shard_full_state(state: Mapping[str, Tensor]) -> tuple[dict[str, Tensor], dict[str, Tensor]]:
    ordered = sorted(state)
    midpoint = (len(ordered) + 1) // 2
    return (
        {key: state[key].detach().cpu() for key in ordered[:midpoint]},
        {key: state[key].detach().cpu() for key in ordered[midpoint:]},
    )


def legacy_training_checkpoint() -> dict[str, object]:
    profile = get_profile("ci")
    runtime = create_training_runtime(profile)
    train_until(runtime, VERSION_CHECKPOINT_STEP)
    return {
        "schema_version": "flashpilot-training-checkpoint-v1",
        "profile_name": profile.name,
        "profile_snapshot": asdict(profile),
        "completed_step": runtime.global_step,
        "losses": list(runtime.loss_history),
        "model_state": runtime.model.state_dict(),
        "optimizer_state": runtime.optimizer.state_dict(),
        "scheduler_state": runtime.scheduler.state_dict(),
        "random_state": capture_rng_state(),
    }


def validate_legacy_training_checkpoint(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "profile_name",
        "profile_snapshot",
        "completed_step",
        "losses",
        "model_state",
        "optimizer_state",
        "scheduler_state",
        "random_state",
    }:
        raise ConversionArtifactError("legacy checkpoint has an unsupported field inventory")
    if (
        value["schema_version"] != "flashpilot-training-checkpoint-v1"
        or value["profile_name"] != "ci"
        or value["profile_snapshot"] != asdict(get_profile("ci"))
        or value["completed_step"] != VERSION_CHECKPOINT_STEP
        or not isinstance(value["losses"], list)
        or len(value["losses"]) != VERSION_CHECKPOINT_STEP
    ):
        raise ConversionArtifactError("legacy checkpoint metadata is incompatible")
    _require_tensor_mapping(value["model_state"], label="legacy model state")
    if not isinstance(value["optimizer_state"], dict) or not isinstance(
        value["scheduler_state"], dict
    ):
        raise ConversionArtifactError("legacy training state is malformed")
    if not isinstance(value["random_state"], dict):
        raise ConversionArtifactError("legacy RNG state is malformed")
    return value


def load_upgraded_runtime(artifact: ValidatedConversionArtifact) -> TrainingRuntime:
    try:
        state = UpgradedTrainingStateV2.model_validate_json(
            (artifact.path / "state.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise ConversionArtifactError("upgraded state metadata is invalid") from error
    if state.global_step != artifact.manifest.global_step:
        raise ConversionArtifactError("upgraded progress differs from its manifest")
    runtime = create_training_runtime(get_profile(state.profile))
    model_state = _require_tensor_mapping(
        safe_load_torch_payload(artifact, "model.pt"),
        label="upgraded model state",
    )
    optimizer_state = safe_load_torch_payload(artifact, "optimizer.pt")
    scheduler_state = safe_load_torch_payload(artifact, "scheduler.pt")
    rng_state = safe_load_torch_payload(artifact, "rng.pt")
    if not isinstance(optimizer_state, dict) or not isinstance(scheduler_state, dict):
        raise ConversionArtifactError("upgraded optimizer or scheduler state is malformed")
    try:
        runtime.model.load_state_dict(model_state, strict=True)
        runtime.optimizer.load_state_dict(optimizer_state)
        runtime.scheduler.load_state_dict(scheduler_state)
        runtime.global_step = state.global_step
        runtime.loss_history = list(state.loss_history)
        restore_rng_state(rng_state)
    except (RuntimeError, TypeError, ValueError) as error:
        raise ConversionArtifactError("upgraded checkpoint cannot restore training") from error
    return runtime


def resume_upgraded_to_control(
    artifact: ValidatedConversionArtifact,
) -> tuple[ControlRunSummary, ControlRunSummary]:
    control = run_control("ci")
    runtime = load_upgraded_runtime(artifact)
    train_until(runtime, get_profile("ci").steps)
    return control, summarize_runtime(runtime)


def canonical_legacy_digest(value: dict[str, object]) -> str:
    return state_digest(
        {
            "global_step": value["completed_step"],
            "loss_history": value["losses"],
            "model": value["model_state"],
            "optimizer": value["optimizer_state"],
            "scheduler": value["scheduler_state"],
            "rng": value["random_state"],
        }
    )


def canonical_upgraded_digest(artifact: ValidatedConversionArtifact) -> str:
    try:
        state = UpgradedTrainingStateV2.model_validate_json(
            (artifact.path / "state.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise ConversionArtifactError("upgraded state metadata is invalid") from error
    return state_digest(
        {
            "global_step": state.global_step,
            "loss_history": state.loss_history,
            "model": safe_load_torch_payload(artifact, "model.pt"),
            "optimizer": safe_load_torch_payload(artifact, "optimizer.pt"),
            "scheduler": safe_load_torch_payload(artifact, "scheduler.pt"),
            "rng": safe_load_torch_payload(artifact, "rng.pt"),
        }
    )


def load_full_payload(artifact: ValidatedConversionArtifact, relative: str) -> dict[str, Tensor]:
    return _require_tensor_mapping(
        safe_load_torch_payload(artifact, relative),
        label=f"{artifact.manifest.representation.value} state",
    )


def load_json_index(path: Path) -> dict[str, str]:
    import json

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConversionArtifactError("shard index is invalid JSON") from error
    if (
        not isinstance(value, dict)
        or not value
        or not all(
            isinstance(key, str) and shard in {"shard-000.pt", "shard-001.pt"}
            for key, shard in value.items()
        )
    ):
        raise ConversionArtifactError("shard index is malformed")
    return value
