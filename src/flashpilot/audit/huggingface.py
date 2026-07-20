"""Metadata-first static audit for a narrow Hugging Face Trainer layout."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import torch

from flashpilot.audit.models import AuditCheck, AuditStatus
from flashpilot.audit.safety import (
    AuditSafetyError,
    file_inventory,
    load_weights_only,
    read_json_object,
    validate_safetensors_metadata,
)
from flashpilot.checkpoints.integrity import sha256_file
from flashpilot.contracts.models import QualificationProfile
from flashpilot.hf.models import HFCheckpointLifecycleEvidence, HFRngMetadata

_INCOMPLETE_MARKERS = frozenset({"INCOMPLETE", "SAVE_IN_PROGRESS", ".incomplete"})
_WEIGHT_FILES = (
    "model.safetensors",
    "adapter_model.safetensors",
    "pytorch_model.bin",
    "adapter_model.bin",
)
_KNOWN_EXACT_FILES = frozenset(
    {
        "adapter_config.json",
        "config.json",
        "flashpilot-callback.json",
        "flashpilot-rng-metadata.json",
        "optimizer.pt",
        "scheduler.pt",
        "trainer_state.json",
        "training_args.json",
        "training_args.bin",
        *_INCOMPLETE_MARKERS,
        *_WEIGHT_FILES,
    }
)


def _check(
    check_id: str,
    status: AuditStatus,
    summary: str,
    *,
    state_id: str | None = None,
    evidence: tuple[str, ...] = (),
) -> AuditCheck:
    return AuditCheck(
        check_id=check_id,
        status=status,
        requirement_state_id=state_id,
        summary=summary,
        evidence_paths=evidence,
    )


def _incomplete_check(checkpoint_path: Path) -> AuditCheck:
    markers = tuple(
        sorted(name for name in _INCOMPLETE_MARKERS if (checkpoint_path / name).exists())
    )
    temporary = checkpoint_path.name.startswith(".") or checkpoint_path.name.endswith(".tmp")
    if markers or temporary:
        return _check(
            "lifecycle.incomplete",
            AuditStatus.FAIL,
            "The directory is temporary or contains incomplete-save evidence.",
            evidence=markers,
        )
    return _check(
        "lifecycle.incomplete",
        AuditStatus.PASS,
        "No supported incomplete-save marker was found.",
    )


def _model_weights_check(checkpoint_path: Path) -> AuditCheck:
    present = [name for name in _WEIGHT_FILES if (checkpoint_path / name).is_file()]
    if len(present) != 1:
        return _check(
            "state.model-or-adapter",
            AuditStatus.FAIL,
            "Exactly one supported model or adapter weight file is required.",
            state_id="adapter",
            evidence=tuple(present),
        )
    name = present[0]
    path = checkpoint_path / name
    try:
        if name.endswith(".safetensors"):
            tensor_count = validate_safetensors_metadata(path)
            summary = f"Safetensors metadata is valid for {tensor_count} tensor(s)."
        else:
            value = load_weights_only(path)
            if not isinstance(value, Mapping) or not all(
                isinstance(key, str) and isinstance(item, torch.Tensor)
                for key, item in value.items()
            ):
                raise AuditSafetyError(
                    f"{name} must contain a weights-only string-to-tensor mapping"
                )
            summary = "The allowlisted PyTorch weight file passed weights-only inspection."
    except AuditSafetyError as error:
        return _check(
            "state.model-or-adapter",
            AuditStatus.FAIL,
            str(error),
            state_id="adapter",
            evidence=(name,),
        )
    return _check(
        "state.model-or-adapter",
        AuditStatus.PASS,
        summary,
        state_id="adapter",
        evidence=(name,),
    )


def _mapping_payload_check(
    checkpoint_path: Path,
    *,
    name: str,
    check_id: str,
    state_id: str,
    required: bool,
) -> AuditCheck:
    path = checkpoint_path / name
    if not path.is_file():
        return _check(
            check_id,
            AuditStatus.FAIL if required else AuditStatus.PASS,
            (
                f"Required {state_id} payload is absent."
                if required
                else f"{state_id} is not required by the selected profile."
            ),
            state_id=state_id,
        )
    try:
        value = load_weights_only(path)
        if not isinstance(value, Mapping):
            raise AuditSafetyError(f"{name} must contain a mapping")
    except AuditSafetyError as error:
        return _check(
            check_id,
            AuditStatus.FAIL,
            str(error),
            state_id=state_id,
            evidence=(name,),
        )
    return _check(
        check_id,
        AuditStatus.PASS,
        f"{state_id} passed allowlisted weights-only inspection.",
        state_id=state_id,
        evidence=(name,),
    )


def _rng_checks(checkpoint_path: Path, *, required: bool) -> list[AuditCheck]:
    candidates = sorted(checkpoint_path.glob("rng_state*.pth"))
    candidates = [path for path in candidates if path.is_file() and not path.is_symlink()]
    state_ids = ("python_rng", "numpy_rng", "torch_rng")
    if not candidates:
        return [
            _check(
                f"state.{state_id}",
                AuditStatus.FAIL if required else AuditStatus.PASS,
                (
                    f"Required {state_id} is absent."
                    if required
                    else f"{state_id} is not required by the selected profile."
                ),
                state_id=state_id,
            )
            for state_id in state_ids
        ]
    if len(candidates) != 1:
        return [
            _check(
                f"state.{state_id}",
                AuditStatus.UNKNOWN,
                "Multiple per-rank RNG files require distributed support not available in v0.2.",
                state_id=state_id,
                evidence=tuple(path.name for path in candidates),
            )
            for state_id in state_ids
        ]
    path = candidates[0]
    metadata_path = checkpoint_path / "flashpilot-rng-metadata.json"
    if metadata_path.is_file():
        try:
            metadata = HFRngMetadata.model_validate(read_json_object(metadata_path))
            if metadata.payload_sha256 != sha256_file(path):
                raise AuditSafetyError("RNG metadata SHA-256 does not match rng_state.pth")
        except (AuditSafetyError, ValueError) as error:
            return [
                _check(
                    f"state.{state_id}",
                    AuditStatus.FAIL,
                    str(error),
                    state_id=state_id,
                    evidence=(metadata_path.name, path.name),
                )
                for state_id in state_ids
            ]
        return [
            _check(
                f"state.{state_id}",
                AuditStatus.PASS,
                f"{state_id} is bound by callback metadata to the RNG payload SHA-256.",
                state_id=state_id,
                evidence=(metadata_path.name, path.name),
            )
            for state_id in state_ids
        ]
    try:
        value = load_weights_only(path)
        if not isinstance(value, Mapping):
            raise AuditSafetyError(f"{path.name} must contain an RNG mapping")
        aliases = {
            "python_rng": ("python", "python_rng_state"),
            "numpy_rng": ("numpy", "numpy_rng_state"),
            "torch_rng": ("cpu", "torch", "cpu_rng_state"),
        }
        missing = [
            state_id for state_id, keys in aliases.items() if not any(key in value for key in keys)
        ]
        if missing:
            raise AuditSafetyError(f"{path.name} omits RNG sections: {', '.join(missing)}")
    except AuditSafetyError as error:
        return [
            _check(
                f"state.{state_id}",
                AuditStatus.FAIL,
                str(error),
                state_id=state_id,
                evidence=(path.name,),
            )
            for state_id in state_ids
        ]
    return [
        _check(
            f"state.{state_id}",
            AuditStatus.PASS,
            f"{state_id} is present in the safely inspected RNG payload.",
            state_id=state_id,
            evidence=(path.name,),
        )
        for state_id in state_ids
    ]


def _trainer_state_checks(
    checkpoint_path: Path,
    *,
    required: bool,
) -> list[AuditCheck]:
    path = checkpoint_path / "trainer_state.json"
    if not path.is_file():
        status = AuditStatus.FAIL if required else AuditStatus.PASS
        message = (
            "trainer_state.json is required for exact training resume."
            if required
            else "Trainer progress is not required by the selected profile."
        )
        return [
            _check(
                "metadata.trainer-state",
                status,
                message,
            ),
            _check(
                "state.global-step",
                status,
                message,
                state_id="global_step",
            ),
        ]
    try:
        state = read_json_object(path)
        global_step = state.get("global_step")
        if not isinstance(global_step, int) or isinstance(global_step, bool) or global_step < 0:
            raise AuditSafetyError("trainer_state.json has no valid nonnegative global_step")
        match = re.fullmatch(r"checkpoint-([0-9]+)", checkpoint_path.name)
        if match is None or int(match.group(1)) != global_step:
            raise AuditSafetyError("checkpoint directory and trainer global_step disagree")
    except AuditSafetyError as error:
        return [
            _check(
                "metadata.trainer-state",
                AuditStatus.FAIL,
                str(error),
                evidence=(path.name,),
            ),
            _check(
                "state.global-step",
                AuditStatus.FAIL,
                str(error),
                state_id="global_step",
                evidence=(path.name,),
            ),
        ]
    return [
        _check(
            "metadata.trainer-state",
            AuditStatus.PASS,
            "trainer_state.json is valid JSON with supported progress metadata.",
            evidence=(path.name,),
        ),
        _check(
            "state.global-step",
            AuditStatus.PASS,
            f"Checkpoint directory identity agrees with global step {global_step}.",
            state_id="global_step",
            evidence=(path.name,),
        ),
    ]


def _training_arguments_check(checkpoint_path: Path, *, required: bool) -> AuditCheck:
    json_path = checkpoint_path / "training_args.json"
    binary_path = checkpoint_path / "training_args.bin"
    if not required and not json_path.exists() and not binary_path.exists():
        return _check(
            "metadata.training-arguments",
            AuditStatus.PASS,
            "Training arguments are not required by the selected profile.",
        )
    if not json_path.is_file():
        if binary_path.is_file():
            return _check(
                "metadata.training-arguments",
                AuditStatus.FAIL if required else AuditStatus.WARN,
                "training_args.bin was not unpickled; supported audit requires JSON metadata.",
                evidence=(binary_path.name,),
            )
        return _check(
            "metadata.training-arguments",
            AuditStatus.FAIL if required else AuditStatus.PASS,
            "Resume-relevant training arguments are absent.",
        )
    try:
        arguments = read_json_object(json_path)
        required_keys = {
            "data_seed",
            "gradient_accumulation_steps",
            "per_device_train_batch_size",
            "seed",
        }
        missing = sorted(required_keys - arguments.keys())
        if missing:
            raise AuditSafetyError(
                f"training_args.json omits resume-relevant fields: {', '.join(missing)}"
            )
    except AuditSafetyError as error:
        return _check(
            "metadata.training-arguments",
            AuditStatus.FAIL,
            str(error),
            evidence=(json_path.name,),
        )
    return _check(
        "metadata.training-arguments",
        AuditStatus.PASS,
        "Resume-relevant training arguments are available as safe JSON metadata.",
        evidence=(json_path.name,),
    )


def _callback_metadata_check(checkpoint_path: Path) -> AuditCheck:
    path = checkpoint_path / "flashpilot-callback.json"
    if not path.exists():
        return _check(
            "metadata.flashpilot-callback",
            AuditStatus.PASS,
            "The optional FlashPilot callback metadata bridge is absent.",
        )
    try:
        event = HFCheckpointLifecycleEvidence.model_validate(read_json_object(path))
        match = re.fullmatch(r"checkpoint-([0-9]+)", checkpoint_path.name)
        if match is None or event.global_step != int(match.group(1)):
            raise AuditSafetyError("callback metadata step disagrees with checkpoint identity")
    except (AuditSafetyError, ValueError) as error:
        return _check(
            "metadata.flashpilot-callback",
            AuditStatus.FAIL,
            str(error),
            evidence=(path.name,),
        )
    return _check(
        "metadata.flashpilot-callback",
        AuditStatus.PASS,
        "FlashPilot callback lifecycle metadata is schema-valid and step-consistent.",
        evidence=(path.name,),
    )


def _base_identity_check(checkpoint_path: Path) -> AuditCheck:
    adapter_weights = (checkpoint_path / "adapter_model.safetensors").is_file() or (
        checkpoint_path / "adapter_model.bin"
    ).is_file()
    name = "adapter_config.json" if adapter_weights else "config.json"
    path = checkpoint_path / name
    if not path.is_file():
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            f"{name} is required to bind model/base identity.",
            state_id="base_model_identity",
        )
    try:
        config = read_json_object(path)
        if adapter_weights:
            identity = config.get("base_model_name_or_path")
            if not isinstance(identity, str) or not identity.strip():
                raise AuditSafetyError("adapter_config.json has no base_model_name_or_path")
        elif not any(
            isinstance(config.get(key), str) and config[key].strip()
            for key in ("_commit_hash", "_name_or_path", "model_type")
        ):
            raise AuditSafetyError("config.json has no supported model identity field")
        digest = sha256_file(path)
    except AuditSafetyError as error:
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            str(error),
            state_id="base_model_identity",
            evidence=(name,),
        )
    return _check(
        "state.base-model-identity",
        AuditStatus.PASS,
        f"Model/base configuration identity is bound to SHA-256 {digest}.",
        state_id="base_model_identity",
        evidence=(name,),
    )


def _inventory_check(checkpoint_path: Path) -> AuditCheck:
    try:
        inventory = set(file_inventory(checkpoint_path))
    except AuditSafetyError as error:
        return _check("inventory.unknown-files", AuditStatus.FAIL, str(error))
    known = set(_KNOWN_EXACT_FILES)
    known.update(name for name in inventory if re.fullmatch(r"rng_state(?:_[0-9]+)?\.pth", name))
    unknown = tuple(sorted(inventory - known))
    if unknown:
        return _check(
            "inventory.unknown-files",
            AuditStatus.WARN,
            f"Unknown files were reported and not trusted: {', '.join(unknown)}",
            evidence=unknown,
        )
    return _check(
        "inventory.unknown-files",
        AuditStatus.PASS,
        "Every file has a supported Hugging Face audit role.",
    )


def audit_huggingface_checkpoint(
    checkpoint_path: Path,
    profile: QualificationProfile,
) -> tuple[AuditCheck, ...]:
    """Audit known Trainer metadata and payloads without importing user code."""

    training_required = profile is QualificationProfile.EXACT_TRAINING_RESUME
    checks: list[AuditCheck] = [
        _incomplete_check(checkpoint_path),
        _model_weights_check(checkpoint_path),
        _mapping_payload_check(
            checkpoint_path,
            name="optimizer.pt",
            check_id="state.optimizer",
            state_id="optimizer",
            required=training_required,
        ),
        _mapping_payload_check(
            checkpoint_path,
            name="scheduler.pt",
            check_id="state.scheduler",
            state_id="scheduler",
            required=training_required,
        ),
    ]
    checks.extend(_rng_checks(checkpoint_path, required=training_required))
    checks.extend(_trainer_state_checks(checkpoint_path, required=training_required))
    checks.append(_training_arguments_check(checkpoint_path, required=training_required))
    checks.append(_callback_metadata_check(checkpoint_path))
    checks.append(_base_identity_check(checkpoint_path))
    checks.append(_inventory_check(checkpoint_path))
    return tuple(checks)
