"""Deterministic verification for unsigned recovery-attestation bundles."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from flashpilot.adapters.lightning import PyTorchLightningAdapter
from flashpilot.attestation.integrity import (
    canonical_model_sha256,
    collect_evidence_entries,
)
from flashpilot.attestation.models import (
    RECOVERY_ATTESTATION_PATH,
    AttestationVerificationCheck,
    AttestationVerificationResult,
    DependencyEnvironmentV1,
    EvidenceManifestV1,
    RecoveryAttestationV1,
)
from flashpilot.checkpoints.base_artifact import (
    BaseArtifactValidationError,
    validate_base_artifact,
)
from flashpilot.checkpoints.integrity import directory_content_fingerprint, sha256_file
from flashpilot.checkpoints.loader import CheckpointValidationError, validate_checkpoint
from flashpilot.contracts import (
    PersistenceContract,
    QualificationProfile,
    huggingface_trainer_persistence_contract,
    native_minimum_persistence_contract,
    persistence_contract_sha256,
    pytorch_lightning_persistence_contract,
    validate_persistence_contract,
)
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.hf.models import HFQualificationResult
from flashpilot.hf.reporting import render_hf_html, render_hf_markdown
from flashpilot.lightning.models import LightningQualificationResult
from flashpilot.lightning.reporting import render_lightning_html, render_lightning_markdown
from flashpilot.orchestration.repair_loop import render_repair_report
from flashpilot.preemption.models import (
    PREEMPTION_INCOMPLETE_MARKER,
    HFPreemptionCertificationResult,
)
from flashpilot.preemption.reporting import render_preemption_html, render_preemption_markdown
from flashpilot.presentation.html_report import render_repair_html
from flashpilot.security.paths import PathContainmentError, PathSandbox


class AttestationVerificationError(RuntimeError):
    """Attestation evidence is invalid, inconsistent, missing, or tampered."""


def _passed(check_id: str, detail: str) -> AttestationVerificationCheck:
    return AttestationVerificationCheck(check_id=check_id, detail=detail)


def _read_model(path: Path, model_type: type):
    try:
        return model_type.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise AttestationVerificationError(f"invalid {path.name}") from error


def _require_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise AttestationVerificationError(message)


def _verify_hf_result(
    *,
    sandbox: PathSandbox,
    attestation: RecoveryAttestationV1,
    resolved_attestation: Path,
    checks: list[AttestationVerificationCheck],
) -> AttestationVerificationResult:
    try:
        result_path = sandbox.resolve_relative(attestation.result_path, must_exist=True)
    except PathContainmentError as error:
        raise AttestationVerificationError("HF result path is missing or unsafe") from error
    result = _read_model(result_path, HFQualificationResult)
    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationVerificationError("HF result does not contain a passing exact gate")
    _require_equal(result.run_id, attestation.run_id, "HF attestation run ID mismatch")
    _require_equal(result.created_at, attestation.issued_at, "HF attestation timestamp mismatch")
    _require_equal(
        result.crash_process.worker_pid,
        attestation.original_worker_pid,
        "HF terminated worker PID mismatch",
    )
    _require_equal(
        result.recovery_process.worker_pid,
        attestation.recovery_worker_pid,
        "HF recovery worker PID mismatch",
    )
    _require_equal(
        result.control.trainable_state_sha256,
        attestation.control_digest,
        "HF control digest mismatch",
    )
    _require_equal(
        result.recovery.trainable_state_sha256,
        attestation.resumed_digest,
        "HF resumed digest mismatch",
    )
    _require_equal(
        result.control.evaluation_sha256,
        attestation.control_evaluation_digest,
        "HF control evaluation digest mismatch",
    )
    _require_equal(
        result.recovery.evaluation_sha256,
        attestation.resumed_evaluation_digest,
        "HF resumed evaluation digest mismatch",
    )
    _require_equal(len(result.gate.checks), attestation.checks_total, "HF gate total mismatch")
    _require_equal(
        sum(check.status == "pass" for check in result.gate.checks),
        attestation.checks_passed,
        "HF gate passed-check count mismatch",
    )
    _require_equal(result.gate.atol, attestation.atol, "HF atol mismatch")
    _require_equal(result.gate.rtol, attestation.rtol, "HF rtol mismatch")
    _require_equal(result.gate.achieved_rpo_steps, attestation.rpo_steps, "HF RPO mismatch")
    _require_equal(result.gate.max_rpo_steps, attestation.max_rpo_steps, "HF max RPO mismatch")
    rto_seconds = (
        result.recovery_process.completed_at - result.recovery_process.started_at
    ).total_seconds()
    _require_equal(rto_seconds, attestation.rto_seconds, "HF RTO mismatch")
    _require_equal(
        result.verified_persisted_bytes,
        attestation.verified_persisted_bytes,
        "HF verified checkpoint bytes mismatch",
    )
    checks.append(
        _passed("consistency.result", "HF result, exact gate, process, trajectory, and RPO agree.")
    )

    try:
        report_path = sandbox.resolve_relative(attestation.report_path, must_exist=True)
        html_path = sandbox.resolve_relative(attestation.html_report_path, must_exist=True)
        markdown = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, PathContainmentError) as error:
        raise AttestationVerificationError("HF report paths are unsafe or unreadable") from error
    _require_equal(markdown, render_hf_markdown(result), "HF Markdown report/result mismatch")
    _require_equal(html, render_hf_html(result), "HF HTML report/result mismatch")
    checks.append(_passed("consistency.reports", "HF reports are exact result-derived views."))

    try:
        checkpoint_path = sandbox.resolve_relative(attestation.checkpoint_path, must_exist=True)
        checkpoint = directory_content_fingerprint(checkpoint_path)
        from safetensors.torch import load_file

        model_path = checkpoint_path / "model.safetensors"
        tensors = load_file(model_path, device="cpu")
        if not tensors:
            raise AttestationVerificationError("HF model tensor file is empty")
        for required in (
            "trainer_state.json",
            "optimizer.pt",
            "scheduler.pt",
            "rng_state.pth",
        ):
            if not (checkpoint_path / required).is_file():
                raise AttestationVerificationError(f"HF checkpoint lacks {required}")
    except (OSError, ValueError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "HF checkpoint is missing, unsafe, or invalid"
        ) from error
    _require_equal(
        attestation.checkpoint_path,
        result.checkpoint_event.checkpoint_path,
        "HF checkpoint path differs from result",
    )
    _require_equal(checkpoint.sha256, attestation.checkpoint_sha256, "HF checkpoint hash mismatch")
    _require_equal(
        checkpoint.file_count,
        attestation.checkpoint_file_count,
        "HF checkpoint file count mismatch",
    )
    _require_equal(
        checkpoint.logical_bytes,
        attestation.checkpoint_logical_bytes,
        "HF checkpoint logical bytes mismatch",
    )
    _require_equal(
        checkpoint.logical_bytes,
        attestation.verified_persisted_bytes,
        "HF checkpoint bytes differ from verified bytes",
    )
    checks.append(_passed("integrity.checkpoint", "HF checkpoint hash and state files agree."))
    return AttestationVerificationResult(
        attestation_sha256=sha256_file(resolved_attestation),
        checks=tuple(checks),
    )


def _verify_hf_preemption_result(
    *,
    sandbox: PathSandbox,
    attestation: RecoveryAttestationV1,
    resolved_attestation: Path,
    checks: list[AttestationVerificationCheck],
) -> AttestationVerificationResult:
    try:
        result_path = sandbox.resolve_relative(attestation.result_path, must_exist=True)
    except PathContainmentError as error:
        raise AttestationVerificationError("preemption result path is missing or unsafe") from error
    result = _read_model(result_path, HFPreemptionCertificationResult)
    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationVerificationError("preemption result lacks a passing exact Gate")
    comparisons = (
        (result.run_id, attestation.run_id, "preemption attestation run ID mismatch"),
        (result.created_at, attestation.issued_at, "preemption timestamp mismatch"),
        (
            result.preemption_process.worker_pid,
            attestation.original_worker_pid,
            "preemption worker PID mismatch",
        ),
        (
            result.recovery_process.worker_pid,
            attestation.recovery_worker_pid,
            "preemption recovery PID mismatch",
        ),
        (
            result.control.trainable_state_sha256,
            attestation.control_digest,
            "preemption control digest mismatch",
        ),
        (
            result.recovery.trainable_state_sha256,
            attestation.resumed_digest,
            "preemption resumed digest mismatch",
        ),
        (
            result.control.evaluation_sha256,
            attestation.control_evaluation_digest,
            "preemption control evaluation mismatch",
        ),
        (
            result.recovery.evaluation_sha256,
            attestation.resumed_evaluation_digest,
            "preemption resumed evaluation mismatch",
        ),
        (len(result.gate.checks), attestation.checks_total, "preemption Gate total mismatch"),
        (
            sum(check.status == "pass" for check in result.gate.checks),
            attestation.checks_passed,
            "preemption Gate passed count mismatch",
        ),
        (result.gate.atol, attestation.atol, "preemption atol mismatch"),
        (result.gate.rtol, attestation.rtol, "preemption rtol mismatch"),
        (result.gate.achieved_rpo_steps, attestation.rpo_steps, "preemption RPO mismatch"),
        (result.gate.max_rpo_steps, attestation.max_rpo_steps, "preemption max RPO mismatch"),
        (result.gate.achieved_rpo_tokens, attestation.rpo_tokens, "preemption token RPO mismatch"),
        (result.signal_name, attestation.preemption_signal, "preemption signal mismatch"),
        (
            result.grace_period_seconds,
            attestation.grace_period_seconds,
            "preemption grace-period mismatch",
        ),
        (
            result.checkpoint_commit_seconds,
            attestation.checkpoint_commit_seconds,
            "preemption checkpoint duration mismatch",
        ),
        (
            result.graceful_exit_seconds,
            attestation.graceful_exit_seconds,
            "preemption exit duration mismatch",
        ),
        (result.recovery_rto_seconds, attestation.rto_seconds, "preemption RTO mismatch"),
        (
            result.verified_persisted_bytes,
            attestation.verified_persisted_bytes,
            "preemption verified bytes mismatch",
        ),
    )
    for actual, expected, message in comparisons:
        _require_equal(actual, expected, message)
    if result.commit_event.incomplete_marker_present:
        raise AttestationVerificationError("preemption result claims an incomplete marker")
    if (sandbox.root / PREEMPTION_INCOMPLETE_MARKER).exists():
        raise AttestationVerificationError("preemption-incomplete marker remains in bundle")
    checks.append(
        _passed(
            "consistency.result",
            "Preemption signal, grace period, exact Gate, RPO, RTO, and trajectory agree.",
        )
    )

    try:
        report_path = sandbox.resolve_relative(attestation.report_path, must_exist=True)
        html_path = sandbox.resolve_relative(attestation.html_report_path, must_exist=True)
        markdown = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "preemption report paths are unsafe or unreadable"
        ) from error
    _require_equal(
        markdown,
        render_preemption_markdown(result),
        "preemption Markdown report/result mismatch",
    )
    _require_equal(
        html,
        render_preemption_html(result),
        "preemption HTML report/result mismatch",
    )
    checks.append(_passed("consistency.reports", "Preemption reports derive from the result."))

    try:
        checkpoint_path = sandbox.resolve_relative(attestation.checkpoint_path, must_exist=True)
        checkpoint = directory_content_fingerprint(checkpoint_path)
        from safetensors.torch import load_file

        model_path = checkpoint_path / "model.safetensors"
        tensors = load_file(model_path, device="cpu")
        if not tensors:
            raise AttestationVerificationError("preemption model tensor file is empty")
        for required in (
            "trainer_state.json",
            "optimizer.pt",
            "scheduler.pt",
            "rng_state.pth",
        ):
            if not (checkpoint_path / required).is_file():
                raise AttestationVerificationError(f"preemption checkpoint lacks {required}")
    except (OSError, ValueError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "preemption checkpoint is missing, unsafe, or invalid"
        ) from error
    for actual, expected, message in (
        (
            attestation.checkpoint_path,
            result.commit_event.checkpoint.checkpoint_path,
            "preemption checkpoint path differs from result",
        ),
        (checkpoint.sha256, attestation.checkpoint_sha256, "preemption hash mismatch"),
        (
            checkpoint.file_count,
            attestation.checkpoint_file_count,
            "preemption file-count mismatch",
        ),
        (
            checkpoint.logical_bytes,
            attestation.checkpoint_logical_bytes,
            "preemption logical-byte mismatch",
        ),
        (
            checkpoint.logical_bytes,
            attestation.verified_persisted_bytes,
            "preemption verified-byte mismatch",
        ),
    ):
        _require_equal(actual, expected, message)
    checks.append(_passed("integrity.checkpoint", "Preemption checkpoint hash and state agree."))
    return AttestationVerificationResult(
        attestation_sha256=sha256_file(resolved_attestation),
        checks=tuple(checks),
    )


def _verify_lightning_result(
    *,
    sandbox: PathSandbox,
    attestation: RecoveryAttestationV1,
    resolved_attestation: Path,
    checks: list[AttestationVerificationCheck],
) -> AttestationVerificationResult:
    try:
        result_path = sandbox.resolve_relative(attestation.result_path, must_exist=True)
    except PathContainmentError as error:
        raise AttestationVerificationError("Lightning result path is missing or unsafe") from error
    result = _read_model(result_path, LightningQualificationResult)
    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationVerificationError("Lightning result lacks a passing exact gate")
    comparisons = (
        (result.run_id, attestation.run_id, "Lightning run ID mismatch"),
        (result.created_at, attestation.issued_at, "Lightning timestamp mismatch"),
        (
            result.crash_process.worker_pid,
            attestation.original_worker_pid,
            "Lightning terminated worker PID mismatch",
        ),
        (
            result.recovery_process.worker_pid,
            attestation.recovery_worker_pid,
            "Lightning recovery worker PID mismatch",
        ),
        (
            result.control.trainable_state_sha256,
            attestation.control_digest,
            "Lightning control digest mismatch",
        ),
        (
            result.recovery.trainable_state_sha256,
            attestation.resumed_digest,
            "Lightning resumed digest mismatch",
        ),
        (
            result.control.evaluation_sha256,
            attestation.control_evaluation_digest,
            "Lightning control evaluation mismatch",
        ),
        (
            result.recovery.evaluation_sha256,
            attestation.resumed_evaluation_digest,
            "Lightning resumed evaluation mismatch",
        ),
        (len(result.gate.checks), attestation.checks_total, "Lightning gate total mismatch"),
        (
            sum(check.status == "pass" for check in result.gate.checks),
            attestation.checks_passed,
            "Lightning gate passed count mismatch",
        ),
        (result.gate.atol, attestation.atol, "Lightning atol mismatch"),
        (result.gate.rtol, attestation.rtol, "Lightning rtol mismatch"),
        (result.gate.achieved_rpo_steps, attestation.rpo_steps, "Lightning RPO mismatch"),
        (result.gate.max_rpo_steps, attestation.max_rpo_steps, "Lightning max RPO mismatch"),
        (
            result.verified_persisted_bytes,
            attestation.verified_persisted_bytes,
            "Lightning verified bytes mismatch",
        ),
    )
    for actual, expected, message in comparisons:
        _require_equal(actual, expected, message)
    rto_seconds = (
        result.recovery_process.completed_at - result.recovery_process.started_at
    ).total_seconds()
    _require_equal(rto_seconds, attestation.rto_seconds, "Lightning RTO mismatch")
    checks.append(
        _passed(
            "consistency.result",
            "Lightning result, exact gate, process, trajectory, and RPO agree.",
        )
    )

    try:
        report_path = sandbox.resolve_relative(attestation.report_path, must_exist=True)
        html_path = sandbox.resolve_relative(attestation.html_report_path, must_exist=True)
        markdown = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "Lightning report paths are unsafe or unreadable"
        ) from error
    _require_equal(
        markdown,
        render_lightning_markdown(result),
        "Lightning Markdown report/result mismatch",
    )
    _require_equal(html, render_lightning_html(result), "Lightning HTML report/result mismatch")
    checks.append(_passed("consistency.reports", "Lightning reports derive from the result."))

    try:
        checkpoint_path = sandbox.resolve_relative(attestation.checkpoint_path, must_exist=True)
        checkpoint = directory_content_fingerprint(checkpoint_path)
        state = PyTorchLightningAdapter().training_state_presence(checkpoint_path)
    except (OSError, ValueError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "Lightning checkpoint is missing, unsafe, or invalid"
        ) from error
    if not all(state.values()):
        raise AttestationVerificationError("Lightning checkpoint lacks exact-resume state")
    for actual, expected, message in (
        (
            attestation.checkpoint_path,
            result.checkpoint_event.checkpoint_path,
            "Lightning checkpoint path differs from result",
        ),
        (checkpoint.sha256, attestation.checkpoint_sha256, "Lightning checkpoint hash mismatch"),
        (
            checkpoint.file_count,
            attestation.checkpoint_file_count,
            "Lightning checkpoint file count mismatch",
        ),
        (
            checkpoint.logical_bytes,
            attestation.checkpoint_logical_bytes,
            "Lightning checkpoint logical bytes mismatch",
        ),
        (
            checkpoint.logical_bytes,
            attestation.verified_persisted_bytes,
            "Lightning checkpoint bytes differ from verified bytes",
        ),
    ):
        _require_equal(actual, expected, message)
    checks.append(
        _passed("integrity.checkpoint", "Lightning checkpoint hash and exact state agree.")
    )
    return AttestationVerificationResult(
        attestation_sha256=sha256_file(resolved_attestation),
        checks=tuple(checks),
    )


def verify_recovery_attestation(attestation_path: Path) -> AttestationVerificationResult:
    """Verify schema, closed evidence inventory, hashes, and result consistency."""

    lexical = attestation_path.absolute()
    if lexical.name != RECOVERY_ATTESTATION_PATH:
        raise AttestationVerificationError(
            f"attestation filename must be {RECOVERY_ATTESTATION_PATH}"
        )
    root = lexical.parent
    try:
        sandbox = PathSandbox.create(root)
        resolved_attestation = sandbox.require_contained(lexical, must_exist=True)
    except PathContainmentError as error:
        raise AttestationVerificationError("attestation path is missing or unsafe") from error
    if not resolved_attestation.is_file():
        raise AttestationVerificationError("attestation path is not a regular file")

    attestation = _read_model(resolved_attestation, RecoveryAttestationV1)
    checks: list[AttestationVerificationCheck] = [
        _passed("schema.attestation", "RecoveryAttestationV1 schema is valid."),
    ]

    try:
        manifest_path = sandbox.resolve_relative(
            attestation.evidence_manifest_path,
            must_exist=True,
        )
    except PathContainmentError as error:
        raise AttestationVerificationError("evidence manifest path is missing or unsafe") from error
    _require_equal(
        sha256_file(manifest_path),
        attestation.evidence_manifest_sha256,
        "evidence manifest SHA-256 mismatch",
    )
    manifest = _read_model(manifest_path, EvidenceManifestV1)
    checks.append(
        _passed("integrity.evidence-manifest", "Evidence manifest schema and SHA-256 passed.")
    )
    try:
        current_entries = collect_evidence_entries(sandbox.root)
    except (OSError, ValueError) as error:
        raise AttestationVerificationError("evidence inventory is unsafe or unreadable") from error
    _require_equal(
        current_entries,
        manifest.entries,
        "evidence inventory contains missing, extra, or mutated artifacts",
    )
    checks.append(
        _passed(
            "integrity.evidence-files",
            f"Closed inventory verified {len(manifest.entries)} evidence artifacts.",
        )
    )

    try:
        environment_path = sandbox.resolve_relative(
            attestation.dependency_environment_path,
            must_exist=True,
        )
    except PathContainmentError as error:
        raise AttestationVerificationError(
            "dependency environment path is missing or unsafe"
        ) from error
    environment = _read_model(environment_path, DependencyEnvironmentV1)
    _require_equal(
        canonical_model_sha256(environment),
        attestation.dependency_environment_sha256,
        "dependency environment SHA-256 mismatch",
    )
    framework_dependency = {
        "transformers": "transformers",
        "lightning": "lightning",
        "native-pytorch": "torch",
    }[attestation.framework]
    framework_version = next(
        (item.version for item in environment.dependencies if item.name == framework_dependency),
        None,
    )
    _require_equal(
        framework_version,
        attestation.framework_version,
        "framework version differs from dependency evidence",
    )
    _require_equal(
        environment.code_commit,
        attestation.code_commit,
        "code commit differs from dependency evidence",
    )
    _require_equal(
        environment.source_tree_state,
        attestation.source_tree_state,
        "source-tree state differs from dependency evidence",
    )
    checks.append(
        _passed("integrity.environment", "Dependency environment identity is consistent.")
    )

    try:
        contract_path = sandbox.resolve_relative(
            attestation.persistence_contract_path,
            must_exist=True,
        )
    except PathContainmentError as error:
        raise AttestationVerificationError(
            "persistence contract path is missing or unsafe"
        ) from error
    contract = _read_model(contract_path, PersistenceContract)
    try:
        validate_persistence_contract(contract)
    except ValueError as error:
        raise AttestationVerificationError(
            "persistence contract fails closed validation"
        ) from error
    _require_equal(
        persistence_contract_sha256(contract),
        attestation.persistence_contract_sha256,
        "persistence contract SHA-256 mismatch",
    )
    expected_contract = (
        huggingface_trainer_persistence_contract(attestation.qualification_profile)
        if attestation.framework == "transformers"
        else pytorch_lightning_persistence_contract()
        if attestation.framework == "lightning"
        else native_minimum_persistence_contract(
            attestation.qualification_profile,
            max_rpo_steps=attestation.max_rpo_steps,
        )
    )
    _require_equal(
        contract,
        expected_contract,
        "persistence contract differs from the deterministic native minimum",
    )
    checks.append(_passed("consistency.contract", "Contract hash and deterministic minimum agree."))

    if (
        attestation.framework == "transformers"
        and attestation.qualification_profile is QualificationProfile.PREEMPTION_SAFE_TRAINING
    ):
        return _verify_hf_preemption_result(
            sandbox=sandbox,
            attestation=attestation,
            resolved_attestation=resolved_attestation,
            checks=checks,
        )
    if attestation.framework == "transformers":
        return _verify_hf_result(
            sandbox=sandbox,
            attestation=attestation,
            resolved_attestation=resolved_attestation,
            checks=checks,
        )
    if attestation.framework == "lightning":
        return _verify_lightning_result(
            sandbox=sandbox,
            attestation=attestation,
            resolved_attestation=resolved_attestation,
            checks=checks,
        )

    try:
        result_path = sandbox.resolve_relative(attestation.result_path, must_exist=True)
    except PathContainmentError as error:
        raise AttestationVerificationError("result path is missing or unsafe") from error
    result = _read_model(result_path, RepairLoopResult)
    gate = result.repaired_run.gate
    if result.final_verdict != "VERIFIED" or not gate.passed or gate.failed_check_ids:
        raise AttestationVerificationError("result does not contain a passing deterministic gate")
    if result.storage_comparison is None:
        raise AttestationVerificationError("verified result lacks storage evidence")
    _require_equal(result.run_id, attestation.run_id, "attestation run ID mismatch")
    _require_equal(result.created_at, attestation.issued_at, "attestation timestamp mismatch")
    _require_equal(
        result.repaired_run.crash.worker_pid,
        attestation.original_worker_pid,
        "original worker PID mismatch",
    )
    _require_equal(
        result.repaired_run.recovery.worker_pid,
        attestation.recovery_worker_pid,
        "recovery worker PID mismatch",
    )
    _require_equal(
        result.repaired_run.control.trainable_state_sha256,
        attestation.control_digest,
        "control trainable-state digest mismatch",
    )
    _require_equal(
        result.repaired_run.recovery.final.trainable_state_sha256,
        attestation.resumed_digest,
        "resumed trainable-state digest mismatch",
    )
    _require_equal(
        result.repaired_run.control.evaluation_sha256,
        attestation.control_evaluation_digest,
        "control evaluation digest mismatch",
    )
    _require_equal(
        result.repaired_run.recovery.final.evaluation_sha256,
        attestation.resumed_evaluation_digest,
        "resumed evaluation digest mismatch",
    )
    _require_equal(len(gate.checks), attestation.checks_total, "gate check total mismatch")
    _require_equal(
        sum(check.status != "fail" for check in gate.checks),
        attestation.checks_passed,
        "gate passed-check count mismatch",
    )
    _require_equal(gate.comparison_policy.atol, attestation.atol, "atol mismatch")
    _require_equal(gate.comparison_policy.rtol, attestation.rtol, "rtol mismatch")
    _require_equal(gate.achieved_rollback_steps, attestation.rpo_steps, "RPO mismatch")
    _require_equal(
        gate.hard_rollback_limit_steps,
        attestation.max_rpo_steps,
        "maximum RPO mismatch",
    )
    rto_seconds = (
        result.repaired_run.recovery_process.completed_at
        - result.repaired_run.recovery_process.started_at
    ).total_seconds()
    _require_equal(rto_seconds, attestation.rto_seconds, "RTO mismatch")
    _require_equal(
        result.storage_comparison.repaired_recurring_bytes,
        attestation.verified_persisted_bytes,
        "verified persisted bytes mismatch",
    )
    checks.append(
        _passed("consistency.result", "Result, gate, process, trajectory, RPO, and RTO agree.")
    )

    try:
        report_path = sandbox.resolve_relative(attestation.report_path, must_exist=True)
        html_path = sandbox.resolve_relative(attestation.html_report_path, must_exist=True)
        markdown = report_path.read_text(encoding="utf-8")
        html = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, PathContainmentError) as error:
        raise AttestationVerificationError(
            "report paths are missing, unsafe, or unreadable"
        ) from error
    _require_equal(markdown, render_repair_report(result), "Markdown report/result mismatch")
    _require_equal(html, render_repair_html(result), "HTML report/result mismatch")
    checks.append(
        _passed("consistency.reports", "Markdown and HTML are exact result-derived views.")
    )

    try:
        checkpoint_path = sandbox.resolve_relative(attestation.checkpoint_path, must_exist=True)
        checkpoint = directory_content_fingerprint(checkpoint_path)
    except (OSError, ValueError, PathContainmentError) as error:
        raise AttestationVerificationError("checkpoint reference is missing or unsafe") from error
    try:
        repaired_root = sandbox.resolve_relative("repaired", must_exist=True)
        validated_checkpoint = validate_checkpoint(
            run_root=repaired_root,
            checkpoint_path=checkpoint_path,
        )
        if validated_checkpoint.manifest.base_artifact is None:
            raise AttestationVerificationError(
                "attested adapter checkpoint lacks immutable base identity"
            )
        validate_base_artifact(
            run_root=repaired_root,
            reference=validated_checkpoint.manifest.base_artifact,
        )
    except (
        BaseArtifactValidationError,
        CheckpointValidationError,
        PathContainmentError,
    ) as error:
        raise AttestationVerificationError(
            "checkpoint failed native integrity or base validation"
        ) from error
    _require_equal(
        validated_checkpoint.manifest.global_step,
        result.repaired_run.crash.checkpoint_step,
        "checkpoint step differs from the repaired result",
    )
    _require_equal(checkpoint.sha256, attestation.checkpoint_sha256, "checkpoint SHA-256 mismatch")
    _require_equal(
        checkpoint.file_count,
        attestation.checkpoint_file_count,
        "checkpoint file-count mismatch",
    )
    _require_equal(
        checkpoint.logical_bytes,
        attestation.checkpoint_logical_bytes,
        "checkpoint logical-byte mismatch",
    )
    _require_equal(
        checkpoint.logical_bytes,
        attestation.verified_persisted_bytes,
        "checkpoint bytes differ from verified persisted bytes",
    )
    expected_checkpoint_path = f"repaired/{result.repaired_run.crash.checkpoint_path}"
    _require_equal(
        attestation.checkpoint_path,
        expected_checkpoint_path,
        "checkpoint reference differs from the repaired result",
    )
    checks.append(_passed("integrity.checkpoint", "Referenced checkpoint hash and metrics agree."))

    return AttestationVerificationResult(
        attestation_sha256=sha256_file(resolved_attestation),
        checks=tuple(checks),
    )
