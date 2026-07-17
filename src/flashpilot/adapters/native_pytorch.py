"""Native PyTorch support for the controlled P0 workload."""

from __future__ import annotations

from collections.abc import Mapping

from torch import Tensor

from flashpilot.adapters.base import TrainerAdapter
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS
from flashpilot.domain.capabilities import SaveRestoreSummary, WorkloadCapabilities
from flashpilot.workload.model import TinyTransformerLanguageModel

_COMPLETE_STATE = (
    "adapter",
    "optimizer",
    "scheduler",
    "global_step",
    "python_rng",
    "numpy_rng",
    "torch_rng",
    "base_model_identity",
)
_OMITTED_TRAINING_STATE = (
    "optimizer",
    "scheduler",
    "python_rng",
    "numpy_rng",
    "torch_rng",
)


class NativePyTorchAdapter(TrainerAdapter):
    """The only P0 adapter; it contains no discovery or framework detection."""

    def capabilities(self) -> WorkloadCapabilities:
        return WorkloadCapabilities(
            adapter_name="native-pytorch",
            framework="native-pytorch",
            has_frozen_base=True,
            has_trainable_adapter=True,
            optimizer_type="AdamW",
            scheduler_type="LinearLR",
            uses_dropout=True,
            uses_python_rng=True,
            uses_numpy_rng=True,
            uses_torch_rng=True,
            uses_cuda_rng=False,
            batch_position_is_step_derived=True,
            supported_state=("model", *_COMPLETE_STATE),
            supported_repair_actions=NATIVE_PYTORCH_REPAIR_ACTIONS,
            assumptions=(
                "CPU-only controlled workload",
                "Only residual-adapter parameters are trainable",
            ),
        )

    def summarize_save_restore(self, strategy_name: str) -> SaveRestoreSummary:
        common = {
            "integrity_controls": (
                "manifest",
                "SHA-256 checksums",
                "completion marker",
                "atomic directory commit",
                "base artifact SHA-256",
            ),
            "completion_protocol": (
                "write temporary sibling",
                "fsync files",
                "write COMPLETE",
                "atomic directory rename",
            ),
            "immutable_artifacts": ("frozen base stored once per run",),
        }
        if strategy_name == "safe_adapter_aware":
            return SaveRestoreSummary(
                checkpoint_strategy=strategy_name,
                serialized_state=_COMPLETE_STATE,
                restored_state=_COMPLETE_STATE,
                restore_order=(
                    "validate checkpoint integrity",
                    "validate immutable base identity and SHA-256",
                    "restore frozen base and trainable adapter",
                    "restore optimizer and scheduler",
                    "restore global step",
                    "restore Python, NumPy, and Torch RNG before the next batch",
                ),
                omitted_state=(),
                **common,
            )
        if strategy_name == "missing_training_state":
            included = ("adapter", "global_step", "base_model_identity")
            return SaveRestoreSummary(
                checkpoint_strategy=strategy_name,
                serialized_state=included,
                restored_state=included,
                restore_order=(
                    "validate checkpoint integrity",
                    "validate immutable base identity and SHA-256",
                    "restore frozen base and trainable adapter",
                    "restore global step",
                ),
                omitted_state=_OMITTED_TRAINING_STATE,
                **common,
            )
        raise ValueError(f"unsupported adapter-aware checkpoint strategy: {strategy_name}")

    def frozen_base_state(self, model: TinyTransformerLanguageModel) -> dict[str, Tensor]:
        return {
            name: value.detach().cpu()
            for name, value in model.state_dict().items()
            if not name.startswith("adapter.")
        }

    def trainable_adapter_state(self, model: TinyTransformerLanguageModel) -> dict[str, Tensor]:
        return {name: value.detach().cpu() for name, value in model.adapter.state_dict().items()}

    def restore_partitioned_model(
        self,
        model: TinyTransformerLanguageModel,
        *,
        frozen_base: Mapping[str, Tensor],
        adapter_state: Mapping[str, Tensor],
    ) -> None:
        expected_base = {name for name in model.state_dict() if not name.startswith("adapter.")}
        if set(frozen_base) != expected_base:
            raise RuntimeError("frozen base keys do not match the native model")
        incompatible = model.load_state_dict(dict(frozen_base), strict=False)
        expected_missing = {name for name in model.state_dict() if name.startswith("adapter.")}
        if set(incompatible.missing_keys) != expected_missing or incompatible.unexpected_keys:
            raise RuntimeError("frozen base state is incompatible with the native model")
        model.adapter.load_state_dict(dict(adapter_state), strict=True)
