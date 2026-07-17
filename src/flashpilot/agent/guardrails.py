"""Deterministic request, contract, and repair-plan guardrails."""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from flashpilot.adapters.registry import get_adapter
from flashpilot.checkpoints.atomic import fsync_directory
from flashpilot.domain.agent import (
    CheckpointContract,
    ContractInferenceRequest,
    ContractValidationResult,
    FailureAnalysis,
    IntegrityControl,
    RepairActionDecision,
    RepairAttemptAdmission,
    RepairPlanValidationResult,
)
from flashpilot.domain.capabilities import StateName
from flashpilot.domain.recovery import SanitizedFailureArtifact
from flashpilot.security.paths import PathSandbox
from flashpilot.verification.failure_artifact import assert_sanitized_failure_payload

MAX_REQUEST_CHARACTERS = 100_000
MAX_OUTPUT_CHARACTERS = 50_000
MAX_SOURCE_SNIPPET_CHARACTERS = 4_000
MAX_REPAIR_ACTIONS = 21
MANDATORY_INTEGRITY_CONTROLS: tuple[IntegrityControl, ...] = (
    "manifest",
    "checksums",
    "completion_marker",
    "atomic_commit",
)

_WINDOWS_ABSOLUTE_PATH = re.compile(r"(?i)(?:[a-z]:[\\/]|\\\\[a-z0-9_.-]+[\\/])")
_POSIX_ABSOLUTE_PATH = re.compile(r'(?:^|[\s"])/(?:[a-z0-9_.-]+/)+[a-z0-9_.-]*', re.IGNORECASE)
_URL = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)
_SECRET = re.compile(r"(?:\bsk-[a-z0-9_-]{8,}|api[_ -]?key\s*[:=])", re.IGNORECASE)
_COMMAND = re.compile(
    r"(?:^|\s)(?:powershell|cmd\.exe|bash|sh|rm\s+-|del\s+/|curl\s+|wget\s+|"
    r"pip\s+install|python(?:\.exe)?\s+-m)(?:\s|$)",
    re.IGNORECASE,
)
_CODE_PATCH = re.compile(r"(?:^|\n)(?:diff --git|@@\s|\+\+\+\s|---\s|def\s+|class\s+)", re.I)
_TOLERANCE = re.compile(r"\b(?:atol|rtol|numerical tolerance|comparison tolerance)\b", re.I)
_DISABLE_GATE = re.compile(r"\b(?:disable|skip|bypass|remove)\b.{0,40}\b(?:gate|check)\b", re.I)
_VERIFIED_CLAIM = re.compile(
    r"\b(?:recovery is verified|recovery verified|verified recovery)\b", re.I
)
_CORRUPTION_REPAIR_CLAIM = re.compile(
    r"\b(?:repaired|fixed|restored)\b.{0,30}\b(?:corrupt|corrupted)\b|"
    r"\b(?:corrupt|corrupted)\b.{0,30}\b(?:repaired|fixed|restored)\b",
    re.I,
)
_PROHIBITED_REQUEST_KEY_PARTS = ("api_key", "dataset", "sample", "secret", "tensor", "weight")


class GuardrailViolation(ValueError):
    """Raised when typed model input or output crosses a deterministic boundary."""


class RepairAttemptLimitError(RuntimeError):
    """Raised when a second repair attempt is requested for one run."""


def canonical_json(value: BaseModel | dict[str, Any]) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _walk(value: Any) -> list[tuple[str | None, str]]:
    strings: list[tuple[str | None, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if any(part in normalized for part in _PROHIBITED_REQUEST_KEY_PARTS):
                raise GuardrailViolation(f"request contains prohibited field: {key}")
            if isinstance(child, str):
                strings.append((str(key), child))
            else:
                strings.extend(_walk(child))
    elif isinstance(value, (list, tuple)):
        if value and all(
            isinstance(child, (int, float)) and not isinstance(child, bool) for child in value
        ):
            raise GuardrailViolation("request contains a raw numeric array")
        for child in value:
            if isinstance(child, str):
                strings.append((None, child))
            else:
                strings.extend(_walk(child))
    return strings


def _assert_no_paths_urls_or_secrets(serialized: str) -> None:
    if _WINDOWS_ABSOLUTE_PATH.search(serialized) or _POSIX_ABSOLUTE_PATH.search(serialized):
        raise GuardrailViolation("request contains an absolute local path")
    if _URL.search(serialized):
        raise GuardrailViolation("request contains a URL")
    if _SECRET.search(serialized):
        raise GuardrailViolation("request contains secret-like data")
    if _COMMAND.search(serialized) or _CODE_PATCH.search(serialized):
        raise GuardrailViolation("request contains executable command or patch text")


def assert_safe_contract_request(request: ContractInferenceRequest) -> str:
    payload = request.model_dump(mode="json")
    _walk(payload)
    serialized = canonical_json(payload)
    if len(serialized) > MAX_REQUEST_CHARACTERS:
        raise GuardrailViolation("contract request exceeds the character limit")
    snippet_characters = sum(
        len(value) for value in request.save_restore_summary.sanitized_source_snippets
    )
    if snippet_characters > MAX_SOURCE_SNIPPET_CHARACTERS:
        raise GuardrailViolation("sanitized source snippets exceed the character limit")
    _assert_no_paths_urls_or_secrets(serialized)
    if len(request.supported_state) != len(set(request.supported_state)):
        raise GuardrailViolation("contract request contains duplicate supported state")
    if not set(request.supported_state).issubset(request.workload_capabilities.supported_state):
        raise GuardrailViolation("contract request advertises unsupported state")
    required_controls = set(MANDATORY_INTEGRITY_CONTROLS)
    if request.workload_capabilities.has_frozen_base:
        required_controls.add("base_artifact_hash")
    if not required_controls.issubset(request.integrity_protocol):
        raise GuardrailViolation("contract request omits a mandatory integrity control")
    return serialized


def assert_safe_failure_request(request: SanitizedFailureArtifact) -> str:
    payload = request.model_dump(mode="json")
    _walk(payload)
    serialized = canonical_json(payload)
    if len(serialized) > MAX_REQUEST_CHARACTERS:
        raise GuardrailViolation("failure request exceeds the character limit")
    try:
        assert_sanitized_failure_payload(serialized)
    except ValueError as error:
        raise GuardrailViolation(str(error)) from error
    _assert_no_paths_urls_or_secrets(serialized)
    return serialized


def _all_output_strings(value: BaseModel) -> tuple[str, ...]:
    return tuple(text for _, text in _walk(value.model_dump(mode="json")))


def _unsafe_output_reason(text: str) -> str | None:
    if _WINDOWS_ABSOLUTE_PATH.search(text) or _POSIX_ABSOLUTE_PATH.search(text):
        return "contains an absolute local path"
    if _URL.search(text):
        return "contains a URL"
    if _SECRET.search(text):
        return "contains secret-like data"
    if _COMMAND.search(text):
        return "contains a command"
    if _CODE_PATCH.search(text):
        return "contains code or patch text"
    if _TOLERANCE.search(text):
        return "attempts to discuss or modify comparison tolerances"
    if _DISABLE_GATE.search(text):
        return "attempts to weaken a Recovery Gate check"
    if _VERIFIED_CLAIM.search(text):
        return "claims recovery is verified"
    if _CORRUPTION_REPAIR_CLAIM.search(text):
        return "claims corrupted bytes were repaired"
    return None


def _mandatory_state(request: ContractInferenceRequest) -> tuple[StateName, ...]:
    capabilities = request.workload_capabilities
    required: list[StateName] = []
    if capabilities.has_trainable_adapter:
        required.append("adapter")
    else:
        required.append("model")
    required.extend(("optimizer", "global_step"))
    if capabilities.scheduler_type is not None:
        required.append("scheduler")
    if capabilities.uses_python_rng:
        required.append("python_rng")
    if capabilities.uses_numpy_rng:
        required.append("numpy_rng")
    if capabilities.uses_torch_rng:
        required.append("torch_rng")
    if capabilities.has_frozen_base:
        required.append("base_model_identity")
    return tuple(required)


def validate_checkpoint_contract(
    request: ContractInferenceRequest,
    contract: CheckpointContract,
) -> ContractValidationResult:
    assert_safe_contract_request(request)
    if len(canonical_json(contract)) > MAX_OUTPUT_CHARACTERS:
        raise GuardrailViolation("checkpoint contract exceeds the character limit")
    for text in _all_output_strings(contract):
        unsafe = _unsafe_output_reason(text)
        if unsafe is not None:
            raise GuardrailViolation(f"checkpoint contract {unsafe}")
    if contract.rollback_limit_steps > request.hard_rollback_limit_steps:
        raise GuardrailViolation("checkpoint contract exceeds the user rollback limit")
    if not any(
        "before the next batch" in requirement.lower()
        for requirement in contract.restore_order_requirements
    ):
        raise GuardrailViolation("checkpoint contract does not restore state before the next batch")
    requirements = {requirement.state: requirement for requirement in contract.required_state}
    for state in _mandatory_state(request):
        requirement = requirements.get(state)
        if requirement is None or not requirement.required:
            raise GuardrailViolation(f"checkpoint contract weakens mandatory state: {state}")

    required_controls: list[IntegrityControl] = list(MANDATORY_INTEGRITY_CONTROLS)
    if request.workload_capabilities.has_frozen_base:
        required_controls.append("base_artifact_hash")
    controls = list(contract.required_integrity_controls)
    added = tuple(control for control in required_controls if control not in controls)
    controls.extend(added)
    normalized = contract.model_copy(update={"required_integrity_controls": tuple(controls)})
    unsupported = tuple(
        requirement.state
        for requirement in normalized.required_state
        if requirement.required
        and requirement.state not in request.workload_capabilities.supported_state
    )
    warnings = tuple(
        [f"Deterministic minimum added integrity control: {control}" for control in added]
        + [f"Native adapter does not support required state: {state}" for state in unsupported]
    )
    return ContractValidationResult(
        contract=normalized,
        added_integrity_controls=added,
        unsupported_required_state=unsupported,
        warnings=warnings,
    )


def validate_failure_analysis(
    request: SanitizedFailureArtifact,
    analysis: FailureAnalysis,
) -> RepairPlanValidationResult:
    assert_safe_failure_request(request)
    if len(canonical_json(analysis)) > MAX_OUTPUT_CHARACTERS:
        raise GuardrailViolation("failure analysis exceeds the character limit")
    if len(analysis.repair_plan.actions) > MAX_REPAIR_ACTIONS:
        raise GuardrailViolation("repair plan exceeds the action limit")
    for key, text in _walk(analysis.model_dump(mode="json")):
        if key in {"reason"}:
            continue
        unsafe = _unsafe_output_reason(text)
        if unsafe is not None:
            raise GuardrailViolation(f"failure analysis {unsafe}")
    failed_checks = {
        str(check.get("check_id")) for check in request.gate_checks if check.get("status") == "fail"
    }
    if len(analysis.affected_gate_checks) != len(set(analysis.affected_gate_checks)):
        raise GuardrailViolation("failure analysis contains duplicate affected gate checks")
    unknown_checks = set(analysis.affected_gate_checks) - failed_checks
    if unknown_checks:
        raise GuardrailViolation(
            f"failure analysis references unknown gate checks: {unknown_checks}"
        )
    known_evidence = set(request.evidence_catalog)
    if len(analysis.confirming_evidence) != len(set(analysis.confirming_evidence)):
        raise GuardrailViolation("failure analysis contains duplicate confirming evidence")
    unknown_evidence = set(analysis.confirming_evidence) - known_evidence
    if unknown_evidence:
        raise GuardrailViolation(
            f"failure analysis references unknown confirming evidence: {unknown_evidence}"
        )

    native_supported_actions = set(
        get_adapter("native-pytorch").capabilities().supported_repair_actions
    )
    decisions: list[RepairActionDecision] = []
    seen = set()
    for action in analysis.repair_plan.actions:
        unsafe = _unsafe_output_reason(action.reason)
        if unsafe is not None:
            disposition = "rejected"
            reason = f"Rejected because the proposal {unsafe}."
        elif action.action not in native_supported_actions:
            disposition = "unsupported"
            reason = "Known action is unsupported by NativePyTorchAdapter in P0."
        elif action.action in seen:
            disposition = "rejected"
            reason = "Duplicate action conflicts with the first proposal."
        elif len(action.evidence_ids) != len(set(action.evidence_ids)):
            disposition = "rejected"
            reason = "Supported action contains duplicate evidence IDs."
        elif not action.evidence_ids:
            disposition = "rejected"
            reason = "Supported action lacks a stable evidence ID."
        elif not set(action.evidence_ids).issubset(known_evidence):
            disposition = "rejected"
            reason = "Supported action references evidence outside the request catalog."
        else:
            disposition = "accepted"
            reason = "Typed action is supported and linked to request evidence."
        decisions.append(
            RepairActionDecision(
                action=action.action,
                disposition=disposition,
                reason=reason,
                evidence_ids=action.evidence_ids,
            )
        )
        seen.add(action.action)

    return RepairPlanValidationResult(
        decisions=tuple(decisions),
        accepted_actions=tuple(
            decision.action for decision in decisions if decision.disposition == "accepted"
        ),
        rejected_actions=tuple(
            decision.action for decision in decisions if decision.disposition == "rejected"
        ),
        unsupported_actions=tuple(
            decision.action for decision in decisions if decision.disposition == "unsupported"
        ),
    )


def admit_single_repair_attempt(*, run_root: Path) -> RepairAttemptAdmission:
    """Reserve attempt one without applying a repair or launching an experiment."""

    sandbox = PathSandbox.create(run_root)
    path = sandbox.resolve_relative("agent/repair-attempt-admission.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    admission = RepairAttemptAdmission(admitted_at=datetime.now(UTC))
    serialized = json.dumps(admission.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise RepairAttemptLimitError(
            "one repair attempt is already admitted for this run"
        ) from error
    directory_sync = fsync_directory(path.parent)
    if directory_sync.supported and not directory_sync.succeeded:
        raise OSError(directory_sync.detail)
    return admission
