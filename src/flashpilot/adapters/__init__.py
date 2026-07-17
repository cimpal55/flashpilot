"""The single controlled P0 trainer adapter."""

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.adapters.registry import get_adapter

__all__ = ["NativePyTorchAdapter", "get_adapter"]
