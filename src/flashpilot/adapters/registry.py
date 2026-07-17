"""Fixed P0 adapter lookup with no plugin or entry-point discovery."""

from flashpilot.adapters.base import TrainerAdapter
from flashpilot.adapters.native_pytorch import NativePyTorchAdapter

_NATIVE_PYTORCH = NativePyTorchAdapter()


def get_adapter(name: str) -> TrainerAdapter:
    if name == "native-pytorch":
        return _NATIVE_PYTORCH
    raise ValueError(f"unsupported trainer adapter: {name}")
