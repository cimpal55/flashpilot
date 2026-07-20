"""Static audit for FlashPilot's native PyTorch checkpoint contract."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import torch
from pydantic import ValidationError

from flashpilot.audit.models import AuditCheck, AuditStatus
from flashpilot.audit.safety import AuditSafetyError, file_inventory, load_weights_only
from flashpilot.checkpoints.base_artifact import (
    BaseArtifactValidationError,
    validate_base_artifact,
)
from flashpilot.checkpoints.loader import CheckpointValidationError, validate_checkpoint
from flashpilot.contracts.models import QualificationProfile
from flashpilot.domain.manifests import (
    AdapterCheckpointState,
    CheckpointManifest,
    ChecksumDocument,
    CompletionMarker,
    SafeFullState,
)

_NATIVE_METADATA_FILES = frozenset({"COMPLETE", "checksums.json", "manifest.json"})
_INCOMPLETE_MARKERS = frozenset({"INCOMPLETE", "SAVE_IN_PROGRESS", ".incomplete"})


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


def _read_model(path: Path, model_type: type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise AuditSafetyError(f"{path.name} is invalid") from error


def _metadata_checks(checkpoint_path: Path) -> tuple[list[AuditCheck], CheckpointManifest | None]:
    checks: list[AuditCheck] = []
    manifest: CheckpointManifest | None = None
    metadata_models = (
        ("metadata.completion-marker", "COMPLETE", CompletionMarker),
        ("metadata.manifest", "manifest.json", CheckpointManifest),
        ("metadata.checksums", "checksums.json", ChecksumDocument),
    )
    for check_id, name, model_type in metadata_models:
        path = checkpoint_path / name
        try:
            parsed = _read_model(path, model_type)
            checks.append(
                _check(
                    check_id,
                    AuditStatus.PASS,
                    f"{name} is present and schema-valid.",
                    evidence=(name,),
                )
            )
            if name == "manifest.json":
                manifest = parsed
        except AuditSafetyError as error:
            checks.append(_check(check_id, AuditStatus.FAIL, str(error)))
    return checks, manifest


def _integrity_check(checkpoint_path: Path) -> AuditCheck:
    try:
        validate_checkpoint(run_root=checkpoint_path.parent, checkpoint_path=checkpoint_path)
    except CheckpointValidationError as error:
        return _check(
            "integrity.checkpoint",
            AuditStatus.FAIL,
            f"Checkpoint integrity validation failed: {error}",
        )
    return _check(
        "integrity.checkpoint",
        AuditStatus.PASS,
        "Containment, completion, manifest, checksums, sizes, and payload hashes passed.",
        evidence=("COMPLETE", "checksums.json", "manifest.json"),
    )


def _incomplete_check(checkpoint_path: Path) -> AuditCheck:
    markers = tuple(
        sorted(name for name in _INCOMPLETE_MARKERS if (checkpoint_path / name).exists())
    )
    temporary_name = checkpoint_path.name.startswith(".") and ".tmp-" in checkpoint_path.name
    if temporary_name or markers:
        evidence = markers
        return _check(
            "lifecycle.incomplete",
            AuditStatus.FAIL,
            "The directory is temporary or contains incomplete-save evidence.",
            evidence=evidence,
        )
    return _check(
        "lifecycle.incomplete",
        AuditStatus.PASS,
        "No supported incomplete-save evidence was found.",
    )


def _payload_by_role(
    checkpoint_path: Path,
    manifest: CheckpointManifest | None,
) -> dict[str, Path]:
    if manifest is None:
        return {}
    return {payload.role: checkpoint_path / payload.path for payload in manifest.payloads}


def _safe_mapping_check(
    *,
    check_id: str,
    state_id: str,
    role: str,
    payloads: Mapping[str, Path],
    required: bool,
    tensor_values: bool = False,
) -> AuditCheck:
    path = payloads.get(role)
    if path is None:
        if not required:
            return _check(
                check_id,
                AuditStatus.PASS,
                f"{state_id} is not required by the selected profile.",
                state_id=state_id,
            )
        return _check(
            check_id,
            AuditStatus.FAIL,
            f"Required {state_id} payload is absent.",
            state_id=state_id,
        )
    try:
        value = load_weights_only(path)
        if not isinstance(value, Mapping):
            raise AuditSafetyError(f"{path.name} must contain a mapping")
        if tensor_values and not all(
            isinstance(key, str) and isinstance(item, torch.Tensor) for key, item in value.items()
        ):
            raise AuditSafetyError(f"{path.name} must contain a string-to-tensor mapping")
    except AuditSafetyError as error:
        return _check(check_id, AuditStatus.FAIL, str(error), state_id=state_id)
    return _check(
        check_id,
        AuditStatus.PASS,
        f"{state_id} is present and passed weights-only inspection.",
        state_id=state_id,
        evidence=(path.name,),
    )


def _rng_checks(
    payloads: Mapping[str, Path],
    *,
    required: bool,
) -> list[AuditCheck]:
    path = payloads.get("rng")
    state_ids = ("python_rng", "numpy_rng", "torch_rng")
    if path is None:
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
    try:
        value = load_weights_only(path)
        if not isinstance(value, Mapping) or value.get("schema_version") != "rng-state-v1":
            raise AuditSafetyError("rng.pt has an unsupported RNG schema")
        sections = {"python": "python_rng", "numpy": "numpy_rng", "torch": "torch_rng"}
        missing = [state_id for key, state_id in sections.items() if key not in value]
        if missing:
            raise AuditSafetyError(f"rng.pt omits RNG sections: {', '.join(missing)}")
        if not isinstance(value["torch"], torch.Tensor):
            raise AuditSafetyError("rng.pt Torch RNG section is not a tensor")
    except AuditSafetyError as error:
        return [
            _check(
                f"state.{state_id}",
                AuditStatus.FAIL,
                str(error),
                state_id=state_id,
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


def _state_metadata_checks(
    checkpoint_path: Path,
    manifest: CheckpointManifest | None,
    *,
    training_required: bool,
) -> list[AuditCheck]:
    if manifest is None:
        return [
            _check(
                "state.global-step",
                AuditStatus.FAIL if training_required else AuditStatus.PASS,
                "Global-step metadata cannot be established without a valid manifest.",
                state_id="global_step",
            ),
            _check(
                "state.batch-position",
                AuditStatus.FAIL if training_required else AuditStatus.PASS,
                "Batch position cannot be derived without valid progress metadata.",
                state_id="batch_position",
            ),
            _check(
                "metadata.runtime",
                AuditStatus.FAIL,
                "Framework/runtime metadata cannot be established without a valid manifest.",
            ),
        ]
    state_payload = next(
        (
            checkpoint_path / payload.path
            for payload in manifest.payloads
            if payload.role == "state"
        ),
        None,
    )
    if state_payload is None:
        return [
            _check(
                "state.global-step",
                AuditStatus.FAIL if training_required else AuditStatus.PASS,
                "The state metadata payload is absent.",
                state_id="global_step",
            ),
            _check(
                "state.batch-position",
                AuditStatus.FAIL if training_required else AuditStatus.PASS,
                "Batch position cannot be derived without state metadata.",
                state_id="batch_position",
            ),
            _check("metadata.runtime", AuditStatus.FAIL, "The state metadata payload is absent."),
        ]
    model_type = SafeFullState if manifest.strategy == "safe_full" else AdapterCheckpointState
    try:
        state = _read_model(state_payload, model_type)
        if (
            state.checkpoint_id != manifest.checkpoint_id
            or state.global_step != manifest.global_step
        ):
            raise AuditSafetyError("state.json does not agree with manifest progress metadata")
    except AuditSafetyError as error:
        return [
            _check(
                "state.global-step",
                AuditStatus.FAIL,
                str(error),
                state_id="global_step",
            ),
            _check(
                "state.batch-position",
                AuditStatus.FAIL if training_required else AuditStatus.PASS,
                str(error),
                state_id="batch_position",
            ),
            _check("metadata.runtime", AuditStatus.FAIL, str(error)),
        ]
    return [
        _check(
            "state.global-step",
            AuditStatus.PASS,
            f"Global step {state.global_step} agrees across manifest and state metadata.",
            state_id="global_step",
            evidence=("manifest.json", state_payload.name),
        ),
        _check(
            "state.batch-position",
            AuditStatus.PASS,
            "Global seed and completed step deterministically identify the next batch.",
            state_id="batch_position",
            evidence=(state_payload.name,),
        ),
        _check(
            "metadata.runtime",
            AuditStatus.PASS,
            "Native profile and runtime configuration metadata are schema-valid.",
            evidence=(state_payload.name,),
        ),
    ]


def _base_identity_check(
    checkpoint_path: Path,
    manifest: CheckpointManifest | None,
    payloads: Mapping[str, Path],
) -> AuditCheck:
    if manifest is None:
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            "Base/model identity cannot be established without a valid manifest.",
            state_id="base_model_identity",
        )
    model_path = payloads.get("model")
    if model_path is not None:
        return _check(
            "state.base-model-identity",
            AuditStatus.PASS,
            "The complete model payload is identity-bound by the manifest checksum.",
            state_id="base_model_identity",
            evidence=("manifest.json", model_path.name),
        )
    reference = manifest.base_artifact
    if reference is None:
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            "Adapter state has no immutable base-artifact identity.",
            state_id="base_model_identity",
        )
    candidates = checkpoint_path.parents[:3]
    run_root = next(
        (candidate for candidate in candidates if (candidate / reference.path).is_file()),
        None,
    )
    if run_root is None:
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            "The referenced immutable base artifact is unavailable in the supported layout.",
            state_id="base_model_identity",
            evidence=("manifest.json",),
        )
    try:
        validate_base_artifact(run_root=run_root, reference=reference)
    except BaseArtifactValidationError as error:
        return _check(
            "state.base-model-identity",
            AuditStatus.FAIL,
            f"Immutable base validation failed: {error}",
            state_id="base_model_identity",
            evidence=("manifest.json",),
        )
    return _check(
        "state.base-model-identity",
        AuditStatus.PASS,
        "Immutable base identity, completion marker, size, and SHA-256 passed.",
        state_id="base_model_identity",
        evidence=("manifest.json",),
    )


def _inventory_check(
    checkpoint_path: Path,
    manifest: CheckpointManifest | None,
) -> AuditCheck:
    try:
        inventory = set(file_inventory(checkpoint_path))
    except AuditSafetyError as error:
        return _check("inventory.unknown-files", AuditStatus.FAIL, str(error))
    known = set(_NATIVE_METADATA_FILES) | set(_INCOMPLETE_MARKERS)
    if manifest is not None:
        known.update(payload.path for payload in manifest.payloads)
    unknown = tuple(sorted(inventory - known))
    if unknown:
        return _check(
            "inventory.unknown-files",
            AuditStatus.WARN,
            f"Unknown files were not trusted: {', '.join(unknown)}",
            evidence=unknown,
        )
    return _check(
        "inventory.unknown-files",
        AuditStatus.PASS,
        "Every checkpoint file has a supported metadata or payload role.",
    )


def audit_native_checkpoint(
    checkpoint_path: Path,
    profile: QualificationProfile,
) -> tuple[AuditCheck, ...]:
    """Audit a native checkpoint without restoring or running training."""

    checks, manifest = _metadata_checks(checkpoint_path)
    checks.append(_integrity_check(checkpoint_path))
    checks.append(_incomplete_check(checkpoint_path))
    payloads = _payload_by_role(checkpoint_path, manifest)
    training_required = profile is QualificationProfile.EXACT_TRAINING_RESUME
    model_role = "model" if "model" in payloads else "adapter"
    checks.append(
        _safe_mapping_check(
            check_id="state.model-or-adapter",
            state_id="adapter",
            role=model_role,
            payloads=payloads,
            required=True,
            tensor_values=True,
        )
    )
    checks.append(
        _safe_mapping_check(
            check_id="state.optimizer",
            state_id="optimizer",
            role="optimizer",
            payloads=payloads,
            required=training_required,
        )
    )
    checks.append(
        _safe_mapping_check(
            check_id="state.scheduler",
            state_id="scheduler",
            role="scheduler",
            payloads=payloads,
            required=training_required,
        )
    )
    checks.extend(_rng_checks(payloads, required=training_required))
    checks.extend(
        _state_metadata_checks(
            checkpoint_path,
            manifest,
            training_required=training_required,
        )
    )
    checks.append(_base_identity_check(checkpoint_path, manifest, payloads))
    checks.append(_inventory_check(checkpoint_path, manifest))
    return tuple(checks)
