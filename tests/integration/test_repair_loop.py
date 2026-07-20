from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from xml.etree import ElementTree

import pytest
import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import ValidationError
from rich.console import Console
from typer.testing import CliRunner

import flashpilot.attestation.signing as signing_module
from flashpilot.agent.guardrails import RepairAttemptLimitError
from flashpilot.attestation import (
    ATTESTATION_JUNIT_PATH,
    ATTESTATION_SIGNATURE_PATH,
    EVIDENCE_MANIFEST_PATH,
    RECOVERY_ATTESTATION_PATH,
    AttestationSignatureEmissionError,
    AttestationSignatureV1,
    EvidenceManifestV1,
    RecoveryAttestationV1,
    generate_ed25519_signing_key,
    sign_recovery_attestation,
    verify_recovery_attestation,
)
from flashpilot.attestation.builder import AttestationEmissionError, emit_recovery_attestation
from flashpilot.attestation.integrity import collect_evidence_entries
from flashpilot.attestation.models import LEGACY_STATEMENT_ARTIFACT_PATHS
from flashpilot.attestation.reporters import render_attestation_summary
from flashpilot.attestation.schema import attestation_schema_documents
from flashpilot.attestation.verifier import AttestationVerificationError
from flashpilot.checkpoints.integrity import directory_content_fingerprint, sha256_file
from flashpilot.ci.qualification_policy_models import (
    NativePolicyRequirement,
    QualificationPolicyV1,
)
from flashpilot.cli import app
from flashpilot.contracts import (
    PersistenceContract,
    canonical_contract_json,
    persistence_contract_sha256,
)
from flashpilot.domain.agent import NATIVE_PYTORCH_REPAIR_ACTIONS
from flashpilot.domain.repair import RepairLoopResult
from flashpilot.orchestration.repair_loop import run_bounded_repair_loop
from flashpilot.presentation.console import (
    GPT_SOURCE,
    MEASUREMENT_DISCLAIMER,
    render_demo_result,
)
from flashpilot.registry import verify_attestation_registry
from flashpilot.repair.executor import execute_bounded_repair


def _write_json(path: Path, value: object) -> None:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _copy_bundle(completed_repair_loop, destination: Path) -> Path:
    source, _ = completed_repair_loop
    return Path(shutil.copytree(source, destination))


def _refresh_bundle_inventory(bundle: Path, **attestation_updates: object) -> None:
    manifest = EvidenceManifestV1(entries=collect_evidence_entries(bundle))
    manifest_path = bundle / EVIDENCE_MANIFEST_PATH
    _write_json(manifest_path, manifest)
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    attestation["evidence_manifest_sha256"] = sha256_file(manifest_path)
    attestation.update(attestation_updates)
    _write_json(attestation_path, attestation)


@pytest.fixture(scope="module")
def completed_repair_loop(tmp_path_factory: pytest.TempPathFactory):
    run_root = tmp_path_factory.mktemp("repair-loop") / "run"
    result = run_bounded_repair_loop(
        profile_name="ci",
        run_root=run_root,
        checkpoint_step=4,
    )
    return run_root, result


def test_initial_failure_and_captured_plan_are_preserved(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.initial_failure.gate.passed is False
    assert set(result.initial_failure.gate.failed_check_ids) == {
        "state.optimizer",
        "state.scheduler",
        "state.python_rng",
        "state.numpy_rng",
        "state.torch_rng",
        "trajectory.final_trainable",
        "trajectory.final_evaluation",
        "trajectory.loss_history",
        "contract.no_mandatory_omission",
    }
    assert result.replay_call_metadata.source == "captured_live_response_replay"
    assert result.captured_live_failure_metadata.source == "captured_live_response"
    assert result.captured_live_failure_metadata.response_id
    assert tuple(action.action for action in result.proposed_analysis.repair_plan.actions) == (
        "change_supported_checkpoint_strategy",
        *NATIVE_PYTORCH_REPAIR_ACTIONS,
    )


def test_exactly_six_supported_actions_are_applied(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.repair_execution.applied_actions == NATIVE_PYTORCH_REPAIR_ACTIONS
    assert result.plan_validation.unsupported_actions == ("change_supported_checkpoint_strategy",)
    assert result.plan_validation.rejected_actions == ()
    assert "change_supported_checkpoint_strategy" not in result.repair_execution.applied_actions
    assert result.repair_attempt_count == 1
    assert result.repair_execution.repaired_config.complete_training_state_enabled is True


def test_original_checkpoint_is_unchanged_and_attempt_two_is_refused(
    completed_repair_loop,
) -> None:
    run_root, result = completed_repair_loop

    assert result.original_checkpoint_unmodified is True
    assert result.original_checkpoint_before == result.original_checkpoint_after
    with pytest.raises(RepairAttemptLimitError, match="one repair attempt"):
        execute_bounded_repair(validation=result.plan_validation, run_root=run_root)


def test_second_real_process_and_exact_final_gate_pass(completed_repair_loop) -> None:
    _, result = completed_repair_loop

    assert result.repaired_run.crash.termination_verified is True
    assert result.repaired_run.crash.worker_pid != result.repaired_run.recovery.worker_pid
    assert result.repaired_run.recovery_process.exit_verified is True
    assert result.repaired_run.recovery.final == result.repaired_run.control
    assert result.repaired_run.gate.passed is True
    assert result.repaired_run.gate.failed_check_ids == ()
    assert all(
        check.status in {"pass", "not_applicable"} for check in result.repaired_run.gate.checks
    )
    assert result.repaired_run.gate.comparison_policy.atol == 0.0
    assert result.repaired_run.gate.comparison_policy.rtol == 0.0
    assert result.final_verdict == "VERIFIED"
    assert result.storage_comparison is not None


def test_prompt5_artifacts_and_read_only_cli_commands(completed_repair_loop) -> None:
    run_root, result = completed_repair_loop

    assert (
        RepairLoopResult.model_validate_json((run_root / "result.json").read_text(encoding="utf-8"))
        == result
    )
    assert (run_root / "report.md").is_file()
    assert (run_root / "report.html").is_file()
    assert (run_root / "agent/request.redacted.json").is_file()
    assert (run_root / "agent/failure/captured-live-metadata.json").is_file()
    assert (run_root / "agent/repair/repaired-strategy.json").is_file()
    runner = CliRunner()
    for command in ("audit", "verify", "replay"):
        invocation = runner.invoke(app, [command, "--run-dir", str(run_root)])
        assert invocation.exit_code == 0, invocation.output


def test_prompt6_console_and_html_are_result_only_presentations(completed_repair_loop) -> None:
    run_root, result = completed_repair_loop
    console = Console(record=True, width=180, color_system=None)

    render_demo_result(
        console=console,
        result=result,
        run_dir=run_root,
        runtime_seconds=12.34,
    )
    rendered = console.export_text()
    for stage in (
        "Uninterrupted control",
        "Initial checkpoint",
        "First real process termination",
        "Initial Recovery Gate",
        "GPT-5.6 captured-response fixture/replay diagnosis",
        "Deterministic bounded repair",
        "Second real process termination",
        "Final Recovery Gate",
        "Verified storage comparison",
    ):
        assert stage in rendered
    assert GPT_SOURCE in rendered
    assert "PASS" in rendered
    assert "FAIL" in rendered
    assert "VERIFIED" in rendered
    assert "UNSUPPORTED" in rendered
    assert "GPT RECOMMENDATION" in rendered
    assert "GUARDRAIL ACCEPTED" in rendered
    assert MEASUREMENT_DISCLAIMER in rendered
    assert "safe_full recurring logical bytes" in rendered
    assert "Repaired recurring logical bytes" in rendered
    assert "One-time frozen-base cost (separate)" in rendered

    html = (run_root / "report.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert "Final Recovery Gate" in html
    assert "Verified storage comparison" in html
    assert MEASUREMENT_DISCLAIMER in " ".join(html.split())
    assert "http://" not in html
    assert "https://" not in html

    markdown = (run_root / "report.md").read_text(encoding="utf-8")
    storage = result.storage_comparison
    assert storage is not None
    for expected in (
        f"safe_full recurring logical bytes: {storage.safe_full_bytes}",
        f"repaired recurring logical bytes: {storage.repaired_recurring_bytes}",
        f"one-time frozen base bytes: {storage.repaired_one_time_base_bytes}",
        f"structural reduction: {storage.structural_reduction_bytes} bytes ",
        MEASUREMENT_DISCLAIMER,
    ):
        assert expected in markdown


def test_verified_demo_emits_closed_recovery_attestation(completed_repair_loop) -> None:
    run_root, result = completed_repair_loop
    attestation_path = run_root / RECOVERY_ATTESTATION_PATH
    manifest_path = run_root / EVIDENCE_MANIFEST_PATH
    junit_path = run_root / ATTESTATION_JUNIT_PATH

    attestation = RecoveryAttestationV1.model_validate_json(
        attestation_path.read_text(encoding="utf-8")
    )
    manifest = EvidenceManifestV1.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    verification = verify_recovery_attestation(attestation_path)

    assert attestation.verdict == "verified"
    assert attestation.signature_status == "unsigned"
    assert attestation.qualification_profile == "exact-training-resume"
    assert attestation.original_worker_pid == result.repaired_run.crash.worker_pid
    assert attestation.recovery_worker_pid == result.repaired_run.recovery.worker_pid
    assert attestation.original_worker_pid != attestation.recovery_worker_pid
    assert attestation.control_digest == attestation.resumed_digest
    assert attestation.control_evaluation_digest == attestation.resumed_evaluation_digest
    assert attestation.checks_passed == attestation.checks_total == 24
    assert attestation.atol == attestation.rtol == 0.0
    assert attestation.rpo_steps == 0
    assert (
        attestation.verified_persisted_bytes == result.storage_comparison.repaired_recurring_bytes
    )
    assert attestation.evidence_manifest_sha256 == sha256_file(manifest_path)
    assert manifest.entries == collect_evidence_entries(run_root)
    assert verification.valid is True
    assert verification.verdict == "VERIFIED"
    assert len(verification.checks) == 8
    junit = ElementTree.parse(junit_path).getroot()
    assert junit.attrib == {
        "name": "flashpilot.attestation-verification",
        "tests": "8",
        "failures": "0",
        "errors": "0",
        "skipped": "0",
    }
    qualification_junit = ElementTree.parse(run_root / "junit.xml").getroot()
    assert qualification_junit.attrib["tests"] == "24"
    assert qualification_junit.attrib["failures"] == "0"
    assert "Exact failed requirements\n\n- None" in (run_root / "job-summary.md").read_text(
        encoding="utf-8"
    )
    assert (run_root / "results.sarif").is_file()


def test_emit_junit_enforces_policy_without_mutating_attested_bundle(
    completed_repair_loop,
) -> None:
    run_root, _ = completed_repair_loop
    before = collect_evidence_entries(run_root)

    invocation = CliRunner().invoke(
        app,
        [
            "emit-junit",
            "--run-dir",
            str(run_root),
            "--policy",
            "examples/ci/policy.yml",
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "VERIFIED" in invocation.output
    assert "Policy: PASS" in invocation.output
    assert collect_evidence_entries(run_root) == before
    assert verify_recovery_attestation(run_root / RECOVERY_ATTESTATION_PATH).valid is True


def _write_native_qualification_policy(path: Path, *, require_signed: bool = False) -> None:
    policy = QualificationPolicyV1(
        policy_id="native-exact-recovery",
        requirements=(
            NativePolicyRequirement(
                requirement_id="native-process-termination",
                kind="native-qualification",
                framework="native-pytorch",
                adapter="native-pytorch",
                qualification_profile="exact-training-resume",
                fault="process_termination",
                max_rpo_steps=0,
                max_rto_seconds=60,
                require_signed_attestation=require_signed,
            ),
        ),
    )
    path.write_text(
        yaml.safe_dump(policy.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )


def test_qualification_policy_verifies_attested_run_without_mutating_it(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    run_root, _ = completed_repair_loop
    policy_path = tmp_path / "policy.yml"
    output_root = tmp_path / "policy-output"
    _write_native_qualification_policy(policy_path)
    before = directory_content_fingerprint(run_root)

    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"native-process-termination={run_root}",
        ],
    )

    assert invocation.exit_code == 0, invocation.output
    assert "POLICY PASS" in invocation.output
    assert "Requirements: 1/1" in invocation.output
    assert directory_content_fingerprint(run_root) == before
    assert verify_recovery_attestation(run_root / RECOVERY_ATTESTATION_PATH).valid is True
    evaluation = json.loads((output_root / "policy-evaluation.json").read_text("utf-8"))
    bound = evaluation["requirements"][0]["evidence"]
    assert bound["attestation_status"] == "verified"
    assert len(bound["attestation_sha256"]) == 64
    assert bound["attestation_signature_status"] == "unsigned"


def test_qualification_policy_requires_and_records_trusted_signature(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signed-policy-bundle")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    generated = generate_ed25519_signing_key(tmp_path / "policy-key")
    wrong_key = generate_ed25519_signing_key(tmp_path / "policy-wrong-key")
    emission = sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=generated.private_key_path,
    )
    policy_path = tmp_path / "signed-policy.yml"
    _write_native_qualification_policy(policy_path, require_signed=True)
    runner = CliRunner()

    missing_key = runner.invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(tmp_path / "missing-key-output"),
            "--run",
            f"native-process-termination={bundle}",
        ],
    )
    invalid_key = runner.invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(tmp_path / "wrong-key-output"),
            "--run",
            f"native-process-termination={bundle}",
            "--public-key",
            str(wrong_key.public_key_path),
        ],
    )
    output_root = tmp_path / "signed-policy-output"
    accepted = runner.invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"native-process-termination={bundle}",
            "--public-key",
            str(generated.public_key_path),
        ],
    )

    assert missing_key.exit_code == 5
    assert "need one explicitly trusted --public-key" in missing_key.output
    assert invalid_key.exit_code == 4
    assert "bound recovery attestation is invalid or tampered" in invalid_key.output
    assert accepted.exit_code == 0, accepted.output
    evaluation = json.loads((output_root / "policy-evaluation.json").read_text("utf-8"))
    bound = evaluation["requirements"][0]["evidence"]
    assert bound["attestation_signature_status"] == "verified"
    assert bound["signing_key_sha256"] == generated.public_key_sha256
    assert bound["signature_artifact_sha256"] == emission.signature_sha256
    assert evaluation["requirements"][0]["checks"][-1]["check_id"] == (
        "policy.native-process-termination.signed-attestation"
    )


def test_qualification_policy_missing_attestation_fails_exact_requirement(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "missing-policy-attestation")
    (bundle / RECOVERY_ATTESTATION_PATH).unlink()
    policy_path = tmp_path / "policy.yml"
    output_root = tmp_path / "policy-output"
    _write_native_qualification_policy(policy_path)

    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"native-process-termination={bundle}",
        ],
    )

    assert invocation.exit_code == 3
    assert "FAILED REQUIREMENT policy.native-process-termination.attestation" in invocation.output
    assert (output_root / "policy-evaluation.json").is_file()


def test_qualification_policy_rejects_tampered_attestation_before_evaluation(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "tampered-policy-attestation")
    attestation = bundle / RECOVERY_ATTESTATION_PATH
    payload = bytearray(attestation.read_bytes())
    payload[-2] ^= 1
    attestation.write_bytes(payload)
    policy_path = tmp_path / "policy.yml"
    output_root = tmp_path / "policy-output"
    _write_native_qualification_policy(policy_path)

    invocation = CliRunner().invoke(
        app,
        [
            "enforce-policy",
            "--policy",
            str(policy_path),
            "--output-dir",
            str(output_root),
            "--run",
            f"native-process-termination={bundle}",
        ],
    )

    assert invocation.exit_code == 4
    assert "bound recovery attestation is invalid or tampered" in invocation.output
    assert not output_root.exists()


def test_emit_junit_does_not_repair_missing_artifact_in_attested_bundle(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "missing-ci-junit")
    (bundle / "junit.xml").unlink()

    invocation = CliRunner().invoke(app, ["emit-junit", "--run-dir", str(bundle)])

    assert invocation.exit_code == 4
    assert "attested run is missing junit.xml" in invocation.output
    assert not (bundle / "junit.xml").exists()


def test_emit_junit_rejects_tampered_existing_attestation(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "tampered-ci-attestation")
    attestation = bundle / RECOVERY_ATTESTATION_PATH
    payload = bytearray(attestation.read_bytes())
    payload[-2] ^= 1
    attestation.write_bytes(payload)

    invocation = CliRunner().invoke(app, ["emit-junit", "--run-dir", str(bundle)])

    assert invocation.exit_code == 4
    assert "existing recovery attestation is invalid or tampered" in invocation.output


def test_emit_sarif_rejects_tampered_attested_sarif(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "tampered-ci-sarif")
    sarif = bundle / "results.sarif"
    sarif.write_text(sarif.read_text(encoding="utf-8") + " ", encoding="utf-8")

    invocation = CliRunner().invoke(app, ["emit-sarif", "--run-dir", str(bundle)])

    assert invocation.exit_code == 4
    assert "existing results.sarif differs from run evidence" in invocation.output


def test_attestation_verification_is_deterministic(completed_repair_loop) -> None:
    run_root, _ = completed_repair_loop
    path = run_root / RECOVERY_ATTESTATION_PATH

    first = verify_recovery_attestation(path)
    second = verify_recovery_attestation(path)

    assert first == second


def test_failed_gate_cannot_emit_verified_attestation(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    _, result = completed_repair_loop
    failed_gate = result.repaired_run.gate.model_copy(
        update={"passed": False, "failed_check_ids": ("state.optimizer",)}
    )
    failed_run = result.repaired_run.model_copy(update={"gate": failed_gate})
    failed_result = result.model_copy(
        update={
            "repaired_run": failed_run,
            "final_verdict": "FAILED",
            "storage_comparison": None,
            "fallback_status": "documented_not_invoked_after_failure",
        }
    )
    failed_root = tmp_path / "failed"

    with pytest.raises(AttestationEmissionError, match="passing deterministic Recovery Gate"):
        emit_recovery_attestation(run_root=failed_root, result=failed_result)

    assert not (failed_root / RECOVERY_ATTESTATION_PATH).exists()


def test_one_byte_evidence_mutation_is_detected(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "mutated-evidence")
    report = bundle / "report.md"
    payload = bytearray(report.read_bytes())
    payload[0] ^= 0x01
    report.write_bytes(payload)

    with pytest.raises(AttestationVerificationError, match="mutated artifacts"):
        verify_recovery_attestation(bundle / RECOVERY_ATTESTATION_PATH)


def test_checkpoint_mutation_is_detected(completed_repair_loop, tmp_path: Path) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "mutated-checkpoint")
    attestation = RecoveryAttestationV1.model_validate_json(
        (bundle / RECOVERY_ATTESTATION_PATH).read_text(encoding="utf-8")
    )
    checkpoint = bundle / attestation.checkpoint_path
    payload = checkpoint / "adapter.pt"
    content = bytearray(payload.read_bytes())
    content[-1] ^= 0x01
    payload.write_bytes(content)

    with pytest.raises(AttestationVerificationError, match="mutated artifacts"):
        verify_recovery_attestation(bundle / RECOVERY_ATTESTATION_PATH)


def test_native_checkpoint_checksum_rejects_mutation_even_if_statement_hashes_are_refreshed(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "refreshed-checkpoint")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    attestation = RecoveryAttestationV1.model_validate_json(
        attestation_path.read_text(encoding="utf-8")
    )
    checkpoint_path = bundle / attestation.checkpoint_path
    payload = checkpoint_path / "adapter.pt"
    content = bytearray(payload.read_bytes())
    content[-1] ^= 0x01
    payload.write_bytes(content)
    fingerprint = directory_content_fingerprint(checkpoint_path)
    _refresh_bundle_inventory(
        bundle,
        checkpoint_sha256=fingerprint.sha256,
        checkpoint_file_count=fingerprint.file_count,
        checkpoint_logical_bytes=fingerprint.logical_bytes,
    )

    with pytest.raises(AttestationVerificationError, match="native integrity"):
        verify_recovery_attestation(attestation_path)


def test_missing_evidence_is_detected(completed_repair_loop, tmp_path: Path) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "missing-evidence")
    (bundle / "agent" / "request.redacted.json").unlink()

    with pytest.raises(AttestationVerificationError, match="missing, extra, or mutated"):
        verify_recovery_attestation(bundle / RECOVERY_ATTESTATION_PATH)


def test_report_mismatch_is_detected_even_with_refreshed_file_hashes(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "report-mismatch")
    with (bundle / "report.md").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("tampered report claim\n")
    _refresh_bundle_inventory(bundle)

    with pytest.raises(AttestationVerificationError, match="Markdown report/result mismatch"):
        verify_recovery_attestation(bundle / RECOVERY_ATTESTATION_PATH)


def test_contract_mismatch_is_detected_even_with_refreshed_hashes(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "contract-mismatch")
    contract_path = bundle / "persistence-contract.json"
    contract = PersistenceContract.model_validate_json(contract_path.read_text(encoding="utf-8"))
    changed = contract.model_copy(update={"warnings": (*contract.warnings, "tampered warning")})
    contract_path.write_text(
        canonical_contract_json(changed) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _refresh_bundle_inventory(
        bundle,
        persistence_contract_sha256=persistence_contract_sha256(changed),
    )

    with pytest.raises(AttestationVerificationError, match="deterministic native minimum"):
        verify_recovery_attestation(bundle / RECOVERY_ATTESTATION_PATH)


def test_attestation_metric_mismatch_is_detected(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "metric-mismatch")
    path = bundle / RECOVERY_ATTESTATION_PATH
    value = json.loads(path.read_text(encoding="utf-8"))
    value["verified_persisted_bytes"] += 1
    _write_json(path, value)

    with pytest.raises(AttestationVerificationError, match="persisted bytes mismatch"):
        verify_recovery_attestation(path)


def test_path_traversal_in_evidence_manifest_is_rejected(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "path-traversal")
    manifest_path = bundle / EVIDENCE_MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0]["path"] = "../outside.json"
    _write_json(manifest_path, manifest)
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    attestation["evidence_manifest_sha256"] = sha256_file(manifest_path)
    _write_json(attestation_path, attestation)

    with pytest.raises(AttestationVerificationError, match="invalid evidence-manifest.json"):
        verify_recovery_attestation(attestation_path)


def test_verify_attestation_cli_uses_integrity_exit_code(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    run_root, _ = completed_repair_loop
    runner = CliRunner()
    valid = runner.invoke(
        app,
        ["verify-attestation", str(run_root / RECOVERY_ATTESTATION_PATH)],
    )
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "cli-invalid")
    with (bundle / "report.md").open("a", encoding="utf-8") as stream:
        stream.write("mutation")
    invalid = runner.invoke(
        app,
        ["verify-attestation", str(bundle / RECOVERY_ATTESTATION_PATH)],
    )

    assert valid.exit_code == 0, valid.output
    assert "VERIFIED" in valid.output
    assert "Unsigned integrity verification passed" in valid.output
    assert invalid.exit_code == 4
    assert "INVALID OR TAMPERED" in invalid.output


def test_attestation_rich_summary_is_explicitly_unsigned(completed_repair_loop) -> None:
    run_root, _ = completed_repair_loop
    path = run_root / RECOVERY_ATTESTATION_PATH
    attestation = RecoveryAttestationV1.model_validate_json(path.read_text(encoding="utf-8"))
    verification = verify_recovery_attestation(path)
    console = Console(record=True, width=180, color_system=None)

    render_attestation_summary(
        console=console,
        attestation=attestation,
        verification=verification,
    )

    rendered = console.export_text()
    assert "Recovery attestation v1" in rendered
    assert "VERIFIED" in rendered
    assert "24/24" in rendered
    assert "unsigned" in rendered
    assert "no publisher authentication" in rendered


def test_checked_in_attestation_schemas_match_generator() -> None:
    for filename, expected in attestation_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


def test_detached_ed25519_signature_round_trip_requires_explicit_trusted_key(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signed-bundle")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    attestation_before = attestation_path.read_bytes()
    manifest_before = collect_evidence_entries(bundle)
    generated = generate_ed25519_signing_key(tmp_path / "signing-key")

    first = sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=generated.private_key_path,
    )
    signature_before = first.signature_path.read_bytes()
    second = sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=generated.private_key_path,
    )

    assert first == second
    assert first.signature_path.name == ATTESTATION_SIGNATURE_PATH
    assert signature_before == first.signature_path.read_bytes()
    assert attestation_before == attestation_path.read_bytes()
    assert collect_evidence_entries(bundle) == manifest_before
    assert first.signature.public_key_sha256 == generated.public_key_sha256
    with pytest.raises(AttestationVerificationError, match="no trusted public key"):
        verify_recovery_attestation(attestation_path)

    verification = verify_recovery_attestation(
        attestation_path,
        public_key_path=generated.public_key_path,
        require_signed=True,
    )

    assert verification.valid is True
    assert verification.signature_status == "verified"
    assert verification.signing_key_sha256 == generated.public_key_sha256
    assert verification.signature_artifact_sha256 == first.signature_sha256
    assert verification.checks[-1].check_id == "signature.ed25519"
    assert verification.attestation_sha256 == first.signature.signed_artifact_sha256


def test_signed_attestation_cli_is_fail_closed_and_secret_free(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signed-cli-bundle")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    key_dir = tmp_path / "cli-key"
    runner = CliRunner()

    generated = runner.invoke(app, ["generate-signing-key", str(key_dir)])
    private_key = key_dir / "ed25519-private.pem"
    public_key = key_dir / "ed25519-public.pem"
    signed = runner.invoke(
        app,
        ["sign-attestation", str(attestation_path), "--private-key", str(private_key)],
    )
    untrusted = runner.invoke(app, ["verify-attestation", str(attestation_path)])
    unsupported = runner.invoke(
        app,
        ["verify-attestation", str(attestation_path), "--require-signed"],
    )
    trusted = runner.invoke(
        app,
        [
            "verify-attestation",
            str(attestation_path),
            "--public-key",
            str(public_key),
            "--require-signed",
        ],
    )
    ci_untrusted = runner.invoke(app, ["emit-junit", "--run-dir", str(bundle)])
    ci_trusted = runner.invoke(
        app,
        [
            "emit-junit",
            "--run-dir",
            str(bundle),
            "--public-key",
            str(public_key),
            "--require-signed",
        ],
    )
    repeated_keygen = runner.invoke(app, ["generate-signing-key", str(key_dir)])

    assert generated.exit_code == 0, generated.output
    assert "ED25519 KEY GENERATED" in generated.output
    assert "BEGIN PRIVATE KEY" not in generated.output
    assert private_key.read_text(encoding="ascii") not in generated.output
    if os.name == "nt":
        assert "Windows private-key file permissions are best-effort" in generated.output
    else:
        assert private_key.stat().st_mode & 0o777 == 0o600
    assert signed.exit_code == 0, signed.output
    assert "SIGNED" in signed.output
    assert "BEGIN PRIVATE KEY" not in signed.output
    assert untrusted.exit_code == 4
    assert "no trusted public key" in untrusted.output
    assert unsupported.exit_code == 5
    assert "--require-signed requires --public-key" in unsupported.output
    assert trusted.exit_code == 0, trusted.output
    assert "Detached Ed25519 signature: VERIFIED" in trusted.output
    assert "Trusted public key SHA-256" in trusted.output
    assert ci_untrusted.exit_code == 4
    assert "existing recovery attestation is invalid or tampered" in ci_untrusted.output
    assert ci_trusted.exit_code == 0, ci_trusted.output
    assert repeated_keygen.exit_code == 5
    assert "must not already exist" in repeated_keygen.output


def test_local_registry_admits_only_the_real_verified_signed_bundle(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "registry-source-bundle")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    generated = generate_ed25519_signing_key(tmp_path / "registry-key")
    wrong_key = generate_ed25519_signing_key(tmp_path / "registry-wrong-key")
    attestation_bytes = attestation_path.read_bytes()
    registry_root = tmp_path / "attestation-registry"
    runner = CliRunner()

    initialized = runner.invoke(
        app,
        ["attestation-registry", "init", str(registry_root)],
    )
    unsigned = runner.invoke(
        app,
        [
            "attestation-registry",
            "add",
            str(attestation_path),
            "--registry-root",
            str(registry_root),
            "--public-key",
            str(generated.public_key_path),
        ],
    )
    sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=generated.private_key_path,
    )
    signature_bytes = (bundle / ATTESTATION_SIGNATURE_PATH).read_bytes()
    untrusted = runner.invoke(
        app,
        [
            "attestation-registry",
            "add",
            str(attestation_path),
            "--registry-root",
            str(registry_root),
            "--public-key",
            str(wrong_key.public_key_path),
        ],
    )
    registered = runner.invoke(
        app,
        [
            "attestation-registry",
            "add",
            str(attestation_path),
            "--registry-root",
            str(registry_root),
            "--public-key",
            str(generated.public_key_path),
        ],
    )
    verified = runner.invoke(
        app,
        ["attestation-registry", "verify", str(registry_root)],
    )
    duplicate = runner.invoke(
        app,
        [
            "attestation-registry",
            "add",
            str(attestation_path),
            "--registry-root",
            str(registry_root),
            "--public-key",
            str(generated.public_key_path),
        ],
    )
    history = verify_attestation_registry(registry_root)
    stored_root = next((registry_root / "entries").iterdir())

    assert initialized.exit_code == 0, initialized.output
    assert unsigned.exit_code == 4
    assert "valid signed recovery-attestation bundle" in unsigned.output
    assert untrusted.exit_code == 4
    assert "valid signed recovery-attestation bundle" in untrusted.output
    assert registered.exit_code == 0, registered.output
    assert "REGISTERED" in registered.output
    assert verified.exit_code == 0, verified.output
    assert "Entries: 1" in verified.output
    assert duplicate.exit_code == 4
    assert "already registered" in duplicate.output
    assert history.entry_count == 1
    assert history.entries[0].verification_check_ids[-1] == "signature.ed25519"
    assert (stored_root / RECOVERY_ATTESTATION_PATH).read_bytes() == attestation_bytes
    assert (stored_root / ATTESTATION_SIGNATURE_PATH).read_bytes() == signature_bytes
    assert generated.private_key_path.read_bytes() not in b"".join(
        path.read_bytes() for path in stored_root.iterdir() if path.is_file()
    )


def test_signing_rejects_a_non_ed25519_private_key(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "wrong-algorithm-bundle")
    private_key = rsa.generate_private_key(public_exponent=65_537, key_size=2_048)
    private_key_path = tmp_path / "rsa-private.pem"
    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "sign-attestation",
            str(bundle / RECOVERY_ATTESTATION_PATH),
            "--private-key",
            str(private_key_path),
        ],
    )

    assert result.exit_code == 4
    assert "private key algorithm must be Ed25519" in result.output
    assert not (bundle / ATTESTATION_SIGNATURE_PATH).exists()


def test_signed_attestation_rejects_wrong_key_and_mutated_signature(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signature-mutations")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    expected_key = generate_ed25519_signing_key(tmp_path / "expected-key")
    wrong_key = generate_ed25519_signing_key(tmp_path / "wrong-key")
    emission = sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=expected_key.private_key_path,
    )

    with pytest.raises(AttestationVerificationError, match="invalid or tampered"):
        verify_recovery_attestation(
            attestation_path,
            public_key_path=wrong_key.public_key_path,
            require_signed=True,
        )

    payload = json.loads(emission.signature_path.read_text(encoding="utf-8"))
    payload["signature"] = ("A" if payload["signature"][0] != "A" else "B") + payload["signature"][
        1:
    ]
    _write_json(emission.signature_path, payload)
    with pytest.raises(AttestationVerificationError, match="invalid or tampered"):
        verify_recovery_attestation(
            attestation_path,
            public_key_path=expected_key.public_key_path,
            require_signed=True,
        )


def test_signed_attestation_rejects_exact_byte_mutation_even_when_bundle_integrity_passes(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signed-byte-mutation")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    generated = generate_ed25519_signing_key(tmp_path / "byte-key")
    sign_recovery_attestation(
        attestation_path=attestation_path,
        private_key_path=generated.private_key_path,
    )
    value = json.loads(attestation_path.read_text(encoding="utf-8"))
    value["limitations"] = [*value["limitations"], "Unauthenticated mutation."]
    _write_json(attestation_path, value)

    with pytest.raises(AttestationVerificationError, match="changed between"):
        verify_recovery_attestation(
            attestation_path,
            public_key_path=generated.public_key_path,
            require_signed=True,
        )


def test_signing_refuses_invalid_bundle_before_writing_signature(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "invalid-signing-bundle")
    report = bundle / "report.md"
    report.write_text(report.read_text(encoding="utf-8") + "mutation", encoding="utf-8")
    generated = generate_ed25519_signing_key(tmp_path / "refusal-key")

    with pytest.raises(AttestationVerificationError, match="mutated artifacts"):
        sign_recovery_attestation(
            attestation_path=bundle / RECOVERY_ATTESTATION_PATH,
            private_key_path=generated.private_key_path,
        )

    assert not (bundle / ATTESTATION_SIGNATURE_PATH).exists()


def test_signing_refuses_attestation_change_after_bundle_verification(
    completed_repair_loop,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "signing-race-bundle")
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    generated = generate_ed25519_signing_key(tmp_path / "signing-race-key")
    create_signature = signing_module.create_attestation_signature

    def sign_then_mutate(*, attestation_path: Path, private_key_path: Path):
        signature = create_signature(
            attestation_path=attestation_path,
            private_key_path=private_key_path,
        )
        with attestation_path.open("ab") as stream:
            stream.write(b" ")
        return signature

    monkeypatch.setattr(signing_module, "create_attestation_signature", sign_then_mutate)

    with pytest.raises(AttestationSignatureEmissionError, match="changed after"):
        sign_recovery_attestation(
            attestation_path=attestation_path,
            private_key_path=generated.private_key_path,
        )

    assert not (bundle / ATTESTATION_SIGNATURE_PATH).exists()


def test_signature_schema_rejects_unknown_algorithm_or_executable_fields() -> None:
    valid = AttestationSignatureV1(
        signed_artifact_sha256="a" * 64,
        public_key_sha256="b" * 64,
        signature="A" * 86 + "==",
    )
    for update in (
        {"algorithm": "rsa"},
        {"signature_scope": "canonical-json"},
        {"command": "sign arbitrary data"},
    ):
        values = valid.model_dump(mode="python")
        values.update(update)
        with pytest.raises(ValidationError):
            AttestationSignatureV1.model_validate(values)


def test_legacy_unsigned_manifest_exclusions_remain_verifiable(
    completed_repair_loop,
    tmp_path: Path,
) -> None:
    bundle = _copy_bundle(completed_repair_loop, tmp_path / "legacy-unsigned-bundle")
    manifest_path = bundle / EVIDENCE_MANIFEST_PATH
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["excluded_statement_artifacts"] = list(LEGACY_STATEMENT_ARTIFACT_PATHS)
    _write_json(manifest_path, manifest)
    attestation_path = bundle / RECOVERY_ATTESTATION_PATH
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    attestation["evidence_manifest_sha256"] = sha256_file(manifest_path)
    _write_json(attestation_path, attestation)

    verification = verify_recovery_attestation(attestation_path)

    assert verification.valid is True
    assert verification.signature_status == "unsigned"
