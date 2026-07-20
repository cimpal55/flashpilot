"""Bounded YAML loading and deterministic CI policy evaluation."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from flashpilot.attestation import RECOVERY_ATTESTATION_PATH, verify_recovery_attestation
from flashpilot.attestation.verifier import AttestationVerificationError
from flashpilot.ci.models import (
    CICheck,
    CICheckStatus,
    CIPolicyEvaluation,
    CIPolicyV1,
    CIRunEvidence,
)

MAX_POLICY_BYTES = 64 * 1024


class CIPolicyError(ValueError):
    """Policy input or referenced attestation evidence is invalid."""


def load_ci_policy(path: Path) -> CIPolicyV1:
    """Load one small safe YAML mapping into the closed policy schema."""

    if not path.is_file() or path.is_symlink():
        raise CIPolicyError("CI policy must be a regular non-symlink file")
    if path.stat().st_size > MAX_POLICY_BYTES:
        raise CIPolicyError("CI policy exceeds the 64 KiB limit")
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise CIPolicyError("CI policy root must be a mapping")
        return CIPolicyV1.model_validate(payload)
    except (OSError, UnicodeError, yaml.YAMLError, ValidationError) as error:
        raise CIPolicyError("CI policy is malformed or unsupported") from error


def _check(check_id: str, passed: bool, summary: str, expected: str, actual: str) -> CICheck:
    return CICheck(
        check_id=check_id,
        status=CICheckStatus.PASS if passed else CICheckStatus.FAIL,
        summary=summary,
        expected=expected,
        actual=actual,
    )


def evaluate_ci_policy(
    *,
    run_root: Path,
    evidence: CIRunEvidence,
    policy: CIPolicyV1,
) -> CIPolicyEvaluation:
    """Evaluate fixed policy fields; arbitrary expressions are impossible."""

    checks = [
        _check(
            "policy.qualification-profile",
            evidence.qualification_profile == policy.qualification_profile,
            "Qualification profile matches the required policy profile.",
            policy.qualification_profile.value,
            evidence.qualification_profile.value,
        ),
        _check(
            "policy.unknown-state",
            evidence.status.value != "UNKNOWN",
            "UNKNOWN evidence fails closed and can never become PASS.",
            "not UNKNOWN",
            evidence.status.value,
        ),
    ]
    if evidence.kind == "static-audit":
        checks.extend(
            (
                _check(
                    "policy.static-audit-status",
                    evidence.status.value == "PASS",
                    "Enforced static audit must pass every deterministic requirement.",
                    "PASS",
                    evidence.status.value,
                ),
                _check(
                    "policy.static-audit-non-verification",
                    evidence.status.value != "VERIFIED",
                    "Static audit remains non-verifying.",
                    "PASS/WARN/FAIL/UNKNOWN only",
                    evidence.status.value,
                ),
            )
        )
    else:
        checks.extend(
            (
                _check(
                    "policy.qualification-verdict",
                    evidence.status.value == "VERIFIED",
                    "Qualification must have a deterministic VERIFIED verdict.",
                    "VERIFIED",
                    evidence.status.value,
                ),
                _check(
                    "policy.required-fault",
                    evidence.fault in policy.required_faults,
                    "Qualification fault class is allowed by the per-run policy.",
                    ",".join(policy.required_faults),
                    str(evidence.fault),
                ),
                _check(
                    "policy.max-rpo",
                    evidence.rpo_steps is not None and evidence.rpo_steps <= policy.max_rpo_steps,
                    "Observed RPO stays within policy.",
                    str(policy.max_rpo_steps),
                    str(evidence.rpo_steps),
                ),
                _check(
                    "policy.max-rto",
                    evidence.rto_seconds is not None
                    and evidence.rto_seconds <= policy.max_rto_seconds,
                    "Observed RTO stays within policy.",
                    str(policy.max_rto_seconds),
                    str(evidence.rto_seconds),
                ),
            )
        )
        attestation_path = run_root / RECOVERY_ATTESTATION_PATH
        is_verified = evidence.status.value == "VERIFIED"
        if not is_verified and attestation_path.exists():
            raise CIPolicyError("failed qualification must not contain a verified attestation")
        attestation_valid = not policy.require_attestation
        if policy.require_attestation and is_verified:
            try:
                attestation_valid = verify_recovery_attestation(attestation_path).valid
            except (AttestationVerificationError, OSError, UnicodeError, ValueError) as error:
                raise CIPolicyError(
                    "required attestation is missing, invalid, or tampered"
                ) from error
        checks.append(
            _check(
                "policy.attestation",
                attestation_valid if is_verified else not attestation_path.exists(),
                "Verified runs require a valid attestation; failed runs must not have one.",
                "valid attestation for VERIFIED only",
                (
                    "valid"
                    if attestation_valid and is_verified
                    else "not present for failed run"
                    if not is_verified and not attestation_path.exists()
                    else "missing or invalid"
                ),
            )
        )
    failed = tuple(check.check_id for check in checks if check.status is CICheckStatus.FAIL)
    return CIPolicyEvaluation(passed=not failed, checks=tuple(checks), failed_check_ids=failed)
