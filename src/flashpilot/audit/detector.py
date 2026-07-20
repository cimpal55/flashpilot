"""Narrow, deterministic checkpoint-layout detection."""

from __future__ import annotations

import re
from pathlib import Path

from flashpilot.audit.models import AuditFramework

_HF_METADATA = frozenset({"trainer_state.json", "training_args.json", "training_args.bin"})
_HF_WEIGHT_NAMES = frozenset(
    {
        "adapter_model.bin",
        "adapter_model.safetensors",
        "model.safetensors",
        "pytorch_model.bin",
    }
)


def detect_checkpoint_framework(checkpoint_path: Path) -> AuditFramework:
    """Detect only the two explicitly supported layouts; ambiguity is UNKNOWN."""

    try:
        names = {entry.name for entry in checkpoint_path.iterdir()}
    except OSError:
        return AuditFramework.UNKNOWN
    native_temporary = (
        checkpoint_path.name.startswith(".checkpoint-step-") and ".tmp-" in checkpoint_path.name
    )
    native_strong = bool(names & {"checksums.json", "manifest.json"}) or (
        "COMPLETE" in names and checkpoint_path.name.startswith("checkpoint-step-")
    )
    huggingface_strong = "trainer_state.json" in names or (
        re.fullmatch(r"checkpoint-[0-9]+", checkpoint_path.name) is not None
    )
    if native_strong and huggingface_strong:
        return AuditFramework.UNKNOWN
    if native_strong or native_temporary:
        return AuditFramework.NATIVE_PYTORCH
    if huggingface_strong or bool(names & _HF_METADATA) or bool(names & _HF_WEIGHT_NAMES):
        return AuditFramework.HUGGINGFACE_TRAINER
    return AuditFramework.UNKNOWN
