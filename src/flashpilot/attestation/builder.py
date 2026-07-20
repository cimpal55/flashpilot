"""Build an unsigned attestation only from a deterministic verified run."""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import torch

from flashpilot.attestation.integrity import (
    canonical_model_sha256,
    collect_evidence_entries,
)
from flashpilot.attestation.models import (
    ATTESTATION_JUNIT_PATH,
    ENVIRONMENT_PATH,
    EVIDENCE_MANIFEST_PATH,
    PERSISTENCE_CONTRACT_PATH,
    RECOVERY_ATTESTATION_PATH,
    AttestationVerificationResult,
    DependencyEnvironmentV1,
    DependencyVersion,
    EvidenceManifestV1,
    RecoveryAttestationV1,
)
from flashpilot.attestation.reporters import render_attestation_junit
from flashpilot.checkpoints.integrity import directory_content_fingerprint, sha256_file
from flashpilot.contracts import (
    QualificationProfile,
    canonical_contract_json,
    huggingface_trainer_persistence_contract,
    native_minimum_persistence_contract,
    persistence_contract_sha256,
    pytorch_lightning_persistence_contract,
)
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.hf.models import HFQualificationResult
from flashpilot.hf.reporting import render_hf_html, render_hf_markdown
from flashpilot.lightning.models import LightningQualificationResult
from flashpilot.lightning.reporting import render_lightning_html, render_lightning_markdown
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.orchestration.repair_loop import render_repair_report
from flashpilot.preemption.models import HFPreemptionCertificationResult
from flashpilot.preemption.reporting import render_preemption_html, render_preemption_markdown
from flashpilot.presentation.html_report import render_repair_html
from flashpilot.security.paths import PathSandbox


class AttestationEmissionError(RuntimeError):
    """A verified attestation cannot be safely emitted for this experiment."""


@dataclass(frozen=True, slots=True)
class AttestationEmission:
    attestation: RecoveryAttestationV1
    evidence_manifest: EvidenceManifestV1
    verification: AttestationVerificationResult
    attestation_path: Path
    evidence_manifest_path: Path
    junit_path: Path


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def _dependency_environment(
    *,
    code_commit: str,
    source_tree_state: str,
    extra_dependencies: tuple[str, ...] = (),
) -> DependencyEnvironmentV1:
    dependencies = tuple(
        DependencyVersion(
            name=name,
            version=str(torch.__version__) if name == "torch" else _package_version(name),
        )
        for name in (
            "flashpilot",
            "numpy",
            "openai",
            "pydantic",
            "rich",
            "torch",
            "typer",
            *extra_dependencies,
        )
    )
    return DependencyEnvironmentV1(
        python_version=platform.python_version(),
        platform=platform.platform(),
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        torch_threads=torch.get_num_threads(),
        deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
        dependencies=dependencies,
    )


def _source_identity() -> tuple[str, str]:
    repository = Path(__file__).resolve().parents[3]
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            capture_output=True,
            check=True,
            encoding="utf-8",
            shell=False,
            timeout=3,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=repository,
            capture_output=True,
            check=True,
            encoding="utf-8",
            shell=False,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable", "unavailable"
    candidate = revision.stdout.strip().lower()
    if len(candidate) != 40 or any(character not in "0123456789abcdef" for character in candidate):
        return "unavailable", "unavailable"
    return candidate, "dirty" if status.stdout.strip() else "clean"


def _require_verified_result(result: RepairLoopResult) -> None:
    gate = result.repaired_run.gate
    if result.final_verdict != "VERIFIED" or not gate.passed or gate.failed_check_ids:
        raise AttestationEmissionError(
            "verified attestation requires a passing deterministic Recovery Gate"
        )
    if result.storage_comparison is None:
        raise AttestationEmissionError("verified attestation requires post-gate storage evidence")
    if not result.original_checkpoint_unmodified:
        raise AttestationEmissionError("verified attestation requires immutable failed evidence")
    if gate.comparison_policy.atol != 0.0 or gate.comparison_policy.rtol != 0.0:
        raise AttestationEmissionError("verified attestation requires the exact comparison policy")


def _require_source_consistency(root: Path, result: RepairLoopResult) -> RepairLoopResult:
    try:
        persisted = RepairLoopResult.model_validate_json(
            (root / result.result_path).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise AttestationEmissionError("persisted result is unavailable or invalid") from error
    if persisted != result:
        raise AttestationEmissionError(
            "persisted result differs from the verified in-memory result"
        )
    try:
        markdown = (root / result.report_path).read_text(encoding="utf-8")
        html = (root / result.html_report_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise AttestationEmissionError("deterministic reports are unavailable") from error
    if markdown != render_repair_report(persisted) or html != render_repair_html(persisted):
        raise AttestationEmissionError("persisted reports differ from the authoritative result")
    return persisted


def emit_recovery_attestation(
    *,
    run_root: Path,
    result: RepairLoopResult,
) -> AttestationEmission:
    """Emit a closed evidence bundle and unsigned attestation after VERIFIED only."""

    _require_verified_result(result)
    root = PathSandbox.create(run_root).root
    for relative in (
        EVIDENCE_MANIFEST_PATH,
        RECOVERY_ATTESTATION_PATH,
        ATTESTATION_JUNIT_PATH,
        PERSISTENCE_CONTRACT_PATH,
        ENVIRONMENT_PATH,
    ):
        if (root / relative).exists():
            raise AttestationEmissionError(f"attestation artifact already exists: {relative}")
    persisted = _require_source_consistency(root, result)

    contract = native_minimum_persistence_contract(
        QualificationProfile.EXACT_TRAINING_RESUME,
        max_rpo_steps=persisted.repaired_run.gate.hard_rollback_limit_steps,
    )
    write_text_artifact(
        run_root=root,
        relative_path=PERSISTENCE_CONTRACT_PATH,
        text=canonical_contract_json(contract) + "\n",
    )
    code_commit, source_tree_state = _source_identity()
    environment = _dependency_environment(
        code_commit=code_commit,
        source_tree_state=source_tree_state,
    )
    write_json_artifact(run_root=root, relative_path=ENVIRONMENT_PATH, value=environment)

    checkpoint_relative = f"repaired/{persisted.repaired_run.crash.checkpoint_path}"
    checkpoint = PathSandbox.create(root).resolve_relative(checkpoint_relative, must_exist=True)
    try:
        checkpoint_fingerprint = directory_content_fingerprint(checkpoint)
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("repaired checkpoint cannot be fingerprinted") from error
    storage = persisted.storage_comparison
    assert storage is not None
    if checkpoint_fingerprint.logical_bytes != storage.repaired_recurring_bytes:
        raise AttestationEmissionError("checkpoint bytes disagree with verified storage evidence")

    try:
        evidence_manifest = EvidenceManifestV1(entries=collect_evidence_entries(root))
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("evidence inventory cannot be closed safely") from error
    evidence_manifest_path = write_json_artifact(
        run_root=root,
        relative_path=EVIDENCE_MANIFEST_PATH,
        value=evidence_manifest,
    )
    evidence_manifest_sha256 = sha256_file(evidence_manifest_path)

    gate = persisted.repaired_run.gate
    recovery_process = persisted.repaired_run.recovery_process
    rto_seconds = (recovery_process.completed_at - recovery_process.started_at).total_seconds()
    checks_passed = sum(check.status != "fail" for check in gate.checks)
    attestation = RecoveryAttestationV1(
        framework_version=str(torch.__version__),
        run_id=persisted.run_id,
        issued_at=persisted.created_at,
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        dependency_environment_sha256=canonical_model_sha256(environment),
        checkpoint_path=checkpoint_relative,
        checkpoint_sha256=checkpoint_fingerprint.sha256,
        checkpoint_file_count=checkpoint_fingerprint.file_count,
        checkpoint_logical_bytes=checkpoint_fingerprint.logical_bytes,
        persistence_contract_sha256=persistence_contract_sha256(contract),
        evidence_manifest_sha256=evidence_manifest_sha256,
        original_worker_pid=persisted.repaired_run.crash.worker_pid,
        recovery_worker_pid=persisted.repaired_run.recovery.worker_pid,
        control_digest=persisted.repaired_run.control.trainable_state_sha256,
        resumed_digest=persisted.repaired_run.recovery.final.trainable_state_sha256,
        control_evaluation_digest=persisted.repaired_run.control.evaluation_sha256,
        resumed_evaluation_digest=persisted.repaired_run.recovery.final.evaluation_sha256,
        checks_passed=checks_passed,
        checks_total=len(gate.checks),
        rpo_steps=gate.achieved_rollback_steps,
        max_rpo_steps=gate.hard_rollback_limit_steps,
        rto_seconds=rto_seconds,
        verified_persisted_bytes=storage.repaired_recurring_bytes,
        limitations=(
            "This is a machine-verifiable experiment record, not legal certification.",
            "The attestation is unsigned and provides integrity, not publisher authentication.",
            "Physical NAND writes, write amplification, and SSD lifetime were not measured.",
        ),
    )
    attestation_path = write_json_artifact(
        run_root=root,
        relative_path=RECOVERY_ATTESTATION_PATH,
        value=attestation,
    )

    from flashpilot.attestation.verifier import verify_recovery_attestation

    verification = verify_recovery_attestation(attestation_path)
    junit_path = write_text_artifact(
        run_root=root,
        relative_path=ATTESTATION_JUNIT_PATH,
        text=render_attestation_junit(verification),
    )
    return AttestationEmission(
        attestation=attestation,
        evidence_manifest=evidence_manifest,
        verification=verification,
        attestation_path=attestation_path,
        evidence_manifest_path=evidence_manifest_path,
        junit_path=junit_path,
    )


def emit_hf_recovery_attestation(
    *,
    run_root: Path,
    result: HFQualificationResult,
) -> AttestationEmission:
    """Emit and verify an unsigned attestation for a passing HF qualification."""

    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationEmissionError("HF attestation requires a passing deterministic gate")
    if result.verified_persisted_bytes is None:
        raise AttestationEmissionError("HF attestation requires post-gate storage evidence")
    root = PathSandbox.create(run_root).root
    for relative in (
        EVIDENCE_MANIFEST_PATH,
        RECOVERY_ATTESTATION_PATH,
        ATTESTATION_JUNIT_PATH,
        PERSISTENCE_CONTRACT_PATH,
        ENVIRONMENT_PATH,
    ):
        if (root / relative).exists():
            raise AttestationEmissionError(f"attestation artifact already exists: {relative}")
    try:
        persisted = HFQualificationResult.model_validate_json(
            (root / result.result_path).read_text(encoding="utf-8")
        )
        markdown = (root / result.report_path).read_text(encoding="utf-8")
        html = (root / result.html_report_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise AttestationEmissionError("persisted HF evidence is unavailable or invalid") from error
    if persisted != result:
        raise AttestationEmissionError("persisted HF result differs from verified memory evidence")
    if markdown != render_hf_markdown(persisted) or html != render_hf_html(persisted):
        raise AttestationEmissionError("persisted HF reports differ from the verified result")

    contract = huggingface_trainer_persistence_contract()
    write_text_artifact(
        run_root=root,
        relative_path=PERSISTENCE_CONTRACT_PATH,
        text=canonical_contract_json(contract) + "\n",
    )
    code_commit, source_tree_state = _source_identity()
    environment = _dependency_environment(
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        extra_dependencies=("accelerate", "transformers"),
    )
    write_json_artifact(run_root=root, relative_path=ENVIRONMENT_PATH, value=environment)

    checkpoint = PathSandbox.create(root).resolve_relative(
        persisted.checkpoint_event.checkpoint_path,
        must_exist=True,
    )
    try:
        checkpoint_fingerprint = directory_content_fingerprint(checkpoint)
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("HF checkpoint cannot be fingerprinted") from error
    if checkpoint_fingerprint.logical_bytes != persisted.verified_persisted_bytes:
        raise AttestationEmissionError("HF checkpoint bytes disagree with verified result")

    try:
        evidence_manifest = EvidenceManifestV1(entries=collect_evidence_entries(root))
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("HF evidence inventory cannot be closed safely") from error
    evidence_manifest_path = write_json_artifact(
        run_root=root,
        relative_path=EVIDENCE_MANIFEST_PATH,
        value=evidence_manifest,
    )
    evidence_manifest_sha256 = sha256_file(evidence_manifest_path)
    recovery_process = persisted.recovery_process
    checks_passed = sum(check.status == "pass" for check in persisted.gate.checks)
    attestation = RecoveryAttestationV1(
        framework="transformers",
        framework_version=persisted.control.transformers_version,
        adapter="huggingface-trainer",
        run_id=persisted.run_id,
        issued_at=persisted.created_at,
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        dependency_environment_sha256=canonical_model_sha256(environment),
        checkpoint_path=persisted.checkpoint_event.checkpoint_path,
        checkpoint_sha256=checkpoint_fingerprint.sha256,
        checkpoint_file_count=checkpoint_fingerprint.file_count,
        checkpoint_logical_bytes=checkpoint_fingerprint.logical_bytes,
        persistence_contract_sha256=persistence_contract_sha256(contract),
        evidence_manifest_sha256=evidence_manifest_sha256,
        fault_scenario="process_termination",
        original_worker_pid=persisted.crash_process.worker_pid,
        recovery_worker_pid=persisted.recovery_process.worker_pid,
        control_digest=persisted.control.trainable_state_sha256,
        resumed_digest=persisted.recovery.trainable_state_sha256,
        control_evaluation_digest=persisted.control.evaluation_sha256,
        resumed_evaluation_digest=persisted.recovery.evaluation_sha256,
        checks_passed=checks_passed,
        checks_total=len(persisted.gate.checks),
        rpo_steps=persisted.gate.achieved_rpo_steps,
        max_rpo_steps=persisted.gate.max_rpo_steps,
        rto_seconds=(recovery_process.completed_at - recovery_process.started_at).total_seconds(),
        verified_persisted_bytes=persisted.verified_persisted_bytes,
        limitations=persisted.limitations,
    )
    attestation_path = write_json_artifact(
        run_root=root,
        relative_path=RECOVERY_ATTESTATION_PATH,
        value=attestation,
    )
    from flashpilot.attestation.verifier import verify_recovery_attestation

    verification = verify_recovery_attestation(attestation_path)
    junit_path = write_text_artifact(
        run_root=root,
        relative_path=ATTESTATION_JUNIT_PATH,
        text=render_attestation_junit(verification),
    )
    return AttestationEmission(
        attestation=attestation,
        evidence_manifest=evidence_manifest,
        verification=verification,
        attestation_path=attestation_path,
        evidence_manifest_path=evidence_manifest_path,
        junit_path=junit_path,
    )


def emit_hf_preemption_attestation(
    *,
    run_root: Path,
    result: HFPreemptionCertificationResult,
) -> AttestationEmission:
    """Emit and verify an unsigned attestation for managed SIGTERM certification."""

    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationEmissionError("preemption attestation requires a passing Gate")
    if result.verified_persisted_bytes is None:
        raise AttestationEmissionError("preemption attestation requires post-Gate bytes")
    root = PathSandbox.create(run_root).root
    for relative in (
        EVIDENCE_MANIFEST_PATH,
        RECOVERY_ATTESTATION_PATH,
        ATTESTATION_JUNIT_PATH,
        PERSISTENCE_CONTRACT_PATH,
        ENVIRONMENT_PATH,
    ):
        if (root / relative).exists():
            raise AttestationEmissionError(f"attestation artifact already exists: {relative}")
    try:
        persisted = HFPreemptionCertificationResult.model_validate_json(
            (root / result.result_path).read_text(encoding="utf-8")
        )
        markdown = (root / result.report_path).read_text(encoding="utf-8")
        html = (root / result.html_report_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise AttestationEmissionError("persisted preemption evidence is invalid") from error
    if persisted != result:
        raise AttestationEmissionError("persisted preemption result differs from memory evidence")
    if markdown != render_preemption_markdown(persisted) or html != render_preemption_html(
        persisted
    ):
        raise AttestationEmissionError("preemption reports differ from the verified result")

    contract = huggingface_trainer_persistence_contract(
        QualificationProfile.PREEMPTION_SAFE_TRAINING
    )
    write_text_artifact(
        run_root=root,
        relative_path=PERSISTENCE_CONTRACT_PATH,
        text=canonical_contract_json(contract) + "\n",
    )
    code_commit, source_tree_state = _source_identity()
    environment = _dependency_environment(
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        extra_dependencies=("accelerate", "transformers"),
    )
    write_json_artifact(run_root=root, relative_path=ENVIRONMENT_PATH, value=environment)

    checkpoint = PathSandbox.create(root).resolve_relative(
        persisted.commit_event.checkpoint.checkpoint_path,
        must_exist=True,
    )
    try:
        checkpoint_fingerprint = directory_content_fingerprint(checkpoint)
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("preemption checkpoint cannot be fingerprinted") from error
    if checkpoint_fingerprint.logical_bytes != persisted.verified_persisted_bytes:
        raise AttestationEmissionError("preemption checkpoint bytes disagree with result")

    try:
        evidence_manifest = EvidenceManifestV1(entries=collect_evidence_entries(root))
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("preemption evidence inventory cannot be closed") from error
    evidence_manifest_path = write_json_artifact(
        run_root=root,
        relative_path=EVIDENCE_MANIFEST_PATH,
        value=evidence_manifest,
    )
    evidence_manifest_sha256 = sha256_file(evidence_manifest_path)
    checks_passed = sum(check.status == "pass" for check in persisted.gate.checks)
    attestation = RecoveryAttestationV1(
        qualification_profile=QualificationProfile.PREEMPTION_SAFE_TRAINING,
        framework="transformers",
        framework_version=persisted.control.transformers_version,
        adapter="huggingface-trainer",
        run_id=persisted.run_id,
        issued_at=persisted.created_at,
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        dependency_environment_sha256=canonical_model_sha256(environment),
        checkpoint_path=persisted.commit_event.checkpoint.checkpoint_path,
        checkpoint_sha256=checkpoint_fingerprint.sha256,
        checkpoint_file_count=checkpoint_fingerprint.file_count,
        checkpoint_logical_bytes=checkpoint_fingerprint.logical_bytes,
        persistence_contract_sha256=persistence_contract_sha256(contract),
        evidence_manifest_sha256=evidence_manifest_sha256,
        fault_scenario="managed_preemption",
        preemption_signal=persisted.signal_name,
        grace_period_seconds=persisted.grace_period_seconds,
        checkpoint_commit_seconds=persisted.checkpoint_commit_seconds,
        graceful_exit_seconds=persisted.graceful_exit_seconds,
        rpo_tokens=persisted.gate.achieved_rpo_tokens,
        original_worker_pid=persisted.preemption_process.worker_pid,
        recovery_worker_pid=persisted.recovery_process.worker_pid,
        control_digest=persisted.control.trainable_state_sha256,
        resumed_digest=persisted.recovery.trainable_state_sha256,
        control_evaluation_digest=persisted.control.evaluation_sha256,
        resumed_evaluation_digest=persisted.recovery.evaluation_sha256,
        checks_passed=checks_passed,
        checks_total=len(persisted.gate.checks),
        rpo_steps=persisted.gate.achieved_rpo_steps,
        max_rpo_steps=persisted.gate.max_rpo_steps,
        rto_seconds=persisted.recovery_rto_seconds,
        verified_persisted_bytes=persisted.verified_persisted_bytes,
        limitations=persisted.limitations,
    )
    attestation_path = write_json_artifact(
        run_root=root,
        relative_path=RECOVERY_ATTESTATION_PATH,
        value=attestation,
    )
    from flashpilot.attestation.verifier import verify_recovery_attestation

    verification = verify_recovery_attestation(attestation_path)
    junit_path = write_text_artifact(
        run_root=root,
        relative_path=ATTESTATION_JUNIT_PATH,
        text=render_attestation_junit(verification),
    )
    return AttestationEmission(
        attestation=attestation,
        evidence_manifest=evidence_manifest,
        verification=verification,
        attestation_path=attestation_path,
        evidence_manifest_path=evidence_manifest_path,
        junit_path=junit_path,
    )


def emit_lightning_recovery_attestation(
    *,
    run_root: Path,
    result: LightningQualificationResult,
) -> AttestationEmission:
    """Emit and verify an unsigned attestation for a passing Lightning run."""

    if result.final_verdict != "VERIFIED" or not result.gate.passed:
        raise AttestationEmissionError("Lightning attestation requires a passing exact gate")
    if result.verified_persisted_bytes is None:
        raise AttestationEmissionError("Lightning attestation requires post-gate storage evidence")
    root = PathSandbox.create(run_root).root
    for relative in (
        EVIDENCE_MANIFEST_PATH,
        RECOVERY_ATTESTATION_PATH,
        ATTESTATION_JUNIT_PATH,
        PERSISTENCE_CONTRACT_PATH,
        ENVIRONMENT_PATH,
    ):
        if (root / relative).exists():
            raise AttestationEmissionError(f"attestation artifact already exists: {relative}")
    try:
        persisted = LightningQualificationResult.model_validate_json(
            (root / result.result_path).read_text(encoding="utf-8")
        )
        markdown = (root / result.report_path).read_text(encoding="utf-8")
        html = (root / result.html_report_path).read_text(encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as error:
        raise AttestationEmissionError(
            "persisted Lightning evidence is unavailable or invalid"
        ) from error
    if persisted != result:
        raise AttestationEmissionError(
            "persisted Lightning result differs from verified memory evidence"
        )
    if markdown != render_lightning_markdown(persisted) or html != render_lightning_html(persisted):
        raise AttestationEmissionError("persisted Lightning reports differ from the result")

    contract = pytorch_lightning_persistence_contract()
    write_text_artifact(
        run_root=root,
        relative_path=PERSISTENCE_CONTRACT_PATH,
        text=canonical_contract_json(contract) + "\n",
    )
    code_commit, source_tree_state = _source_identity()
    environment = _dependency_environment(
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        extra_dependencies=("lightning",),
    )
    write_json_artifact(run_root=root, relative_path=ENVIRONMENT_PATH, value=environment)

    checkpoint = PathSandbox.create(root).resolve_relative(
        persisted.checkpoint_event.checkpoint_path,
        must_exist=True,
    )
    try:
        checkpoint_fingerprint = directory_content_fingerprint(checkpoint)
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("Lightning checkpoint cannot be fingerprinted") from error
    if checkpoint_fingerprint.logical_bytes != persisted.verified_persisted_bytes:
        raise AttestationEmissionError("Lightning checkpoint bytes disagree with result")

    try:
        evidence_manifest = EvidenceManifestV1(entries=collect_evidence_entries(root))
    except (OSError, ValueError) as error:
        raise AttestationEmissionError("Lightning evidence inventory cannot close") from error
    evidence_manifest_path = write_json_artifact(
        run_root=root,
        relative_path=EVIDENCE_MANIFEST_PATH,
        value=evidence_manifest,
    )
    evidence_manifest_sha256 = sha256_file(evidence_manifest_path)
    recovery_process = persisted.recovery_process
    attestation = RecoveryAttestationV1(
        framework="lightning",
        framework_version=persisted.control.lightning_version,
        adapter="pytorch-lightning",
        run_id=persisted.run_id,
        issued_at=persisted.created_at,
        code_commit=code_commit,
        source_tree_state=source_tree_state,
        dependency_environment_sha256=canonical_model_sha256(environment),
        checkpoint_path=persisted.checkpoint_event.checkpoint_path,
        checkpoint_sha256=checkpoint_fingerprint.sha256,
        checkpoint_file_count=checkpoint_fingerprint.file_count,
        checkpoint_logical_bytes=checkpoint_fingerprint.logical_bytes,
        persistence_contract_sha256=persistence_contract_sha256(contract),
        evidence_manifest_sha256=evidence_manifest_sha256,
        original_worker_pid=persisted.crash_process.worker_pid,
        recovery_worker_pid=persisted.recovery_process.worker_pid,
        control_digest=persisted.control.trainable_state_sha256,
        resumed_digest=persisted.recovery.trainable_state_sha256,
        control_evaluation_digest=persisted.control.evaluation_sha256,
        resumed_evaluation_digest=persisted.recovery.evaluation_sha256,
        checks_passed=sum(check.status == "pass" for check in persisted.gate.checks),
        checks_total=len(persisted.gate.checks),
        rpo_steps=persisted.gate.achieved_rpo_steps,
        max_rpo_steps=persisted.gate.max_rpo_steps,
        rto_seconds=(recovery_process.completed_at - recovery_process.started_at).total_seconds(),
        verified_persisted_bytes=persisted.verified_persisted_bytes,
        limitations=persisted.limitations,
    )
    attestation_path = write_json_artifact(
        run_root=root,
        relative_path=RECOVERY_ATTESTATION_PATH,
        value=attestation,
    )
    from flashpilot.attestation.verifier import verify_recovery_attestation

    verification = verify_recovery_attestation(attestation_path)
    junit_path = write_text_artifact(
        run_root=root,
        relative_path=ATTESTATION_JUNIT_PATH,
        text=render_attestation_junit(verification),
    )
    return AttestationEmission(
        attestation=attestation,
        evidence_manifest=evidence_manifest,
        verification=verification,
        attestation_path=attestation_path,
        evidence_manifest_path=evidence_manifest_path,
        junit_path=junit_path,
    )
