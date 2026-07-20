from __future__ import annotations

import json
import shutil
from pathlib import Path
from xml.etree import ElementTree

import pytest
from typer.testing import CliRunner

from flashpilot.attestation import RECOVERY_ATTESTATION_PATH, verify_recovery_attestation
from flashpilot.audit import AuditStatus, FrameworkSelection, run_static_audit
from flashpilot.checkpoints.integrity import logical_directory_bytes
from flashpilot.ci.exits import EXIT_QUALIFICATION_FAILED
from flashpilot.cli import app
from flashpilot.contracts.models import QualificationProfile
from flashpilot.hf.models import HFQualificationResult
from flashpilot.hf.qualification import run_hf_qualification

SCRIPT = Path(__file__).resolve().parents[2] / "examples" / "hf_trainer" / "train.py"


@pytest.fixture(scope="module")
def complete_hf_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, HFQualificationResult]:
    root = tmp_path_factory.mktemp("hf-complete")
    return root, run_hf_qualification(script_path=SCRIPT, run_root=root, scenario="complete")


@pytest.fixture(scope="module")
def model_only_hf_run(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, HFQualificationResult]:
    root = tmp_path_factory.mktemp("hf-model-only")
    return root, run_hf_qualification(script_path=SCRIPT, run_root=root, scenario="model-only")


def test_complete_hf_checkpoint_survives_real_kill_with_exact_trajectory(
    complete_hf_run: tuple[Path, HFQualificationResult],
) -> None:
    root, result = complete_hf_run
    checkpoint = root / result.checkpoint_event.checkpoint_path

    assert result.final_verdict == "VERIFIED"
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert result.gate.atol == result.gate.rtol == 0.0
    assert result.gate.achieved_rpo_steps == result.gate.max_rpo_steps == 0
    assert result.crash_process.exit_verified is True
    assert result.crash_process.exit_code != 0
    assert (
        len(
            {
                result.control_process.worker_pid,
                result.crash_process.worker_pid,
                result.recovery_process.worker_pid,
            }
        )
        == 3
    )
    assert result.control.loss_history == result.recovery.loss_history
    assert result.control.trainable_state_sha256 == result.recovery.trainable_state_sha256
    assert result.control.evaluation_sha256 == result.recovery.evaluation_sha256
    assert result.control.optimizer_sha256 == result.recovery.optimizer_sha256
    assert result.control.scheduler_sha256 == result.recovery.scheduler_sha256
    assert result.control.offline_environment is result.recovery.offline_environment is True
    assert result.verified_persisted_bytes == logical_directory_bytes(checkpoint)
    assert (checkpoint / "flashpilot-rng-metadata.json").is_file()
    assert (root / "inputs" / "train.py").read_bytes() == SCRIPT.read_bytes()
    suite = ElementTree.parse(root / "junit.xml").getroot()
    assert suite.attrib["tests"] == "13"
    assert suite.attrib["failures"] == "0"
    assert "Exact failed requirements\n\n- None" in (root / "job-summary.md").read_text(
        encoding="utf-8"
    )
    sarif = json.loads((root / "results.sarif").read_text(encoding="utf-8"))
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == 13
    assert sarif["runs"][0]["results"] == []


def test_complete_hf_run_emits_verifiable_unsigned_attestation(
    complete_hf_run: tuple[Path, HFQualificationResult],
) -> None:
    root, result = complete_hf_run
    verification = verify_recovery_attestation(root / RECOVERY_ATTESTATION_PATH)

    assert verification.valid is True
    assert result.verified_persisted_bytes is not None
    assert (root / "attestation.junit.xml").is_file()


def test_complete_runtime_hf_checkpoint_passes_safe_static_audit(
    complete_hf_run: tuple[Path, HFQualificationResult],
    tmp_path: Path,
) -> None:
    root, result = complete_hf_run
    checkpoint = root / result.checkpoint_event.checkpoint_path

    audit = run_static_audit(
        checkpoint_path=checkpoint,
        framework_selection=FrameworkSelection.AUTO,
        profile=QualificationProfile.EXACT_TRAINING_RESUME,
        output_dir=tmp_path / "audit",
    )

    assert audit.result.status is AuditStatus.PASS
    assert audit.job_summary.is_file()


def test_rng_bridge_hash_mismatch_fails_static_audit(
    complete_hf_run: tuple[Path, HFQualificationResult],
    tmp_path: Path,
) -> None:
    root, result = complete_hf_run
    source = root / result.checkpoint_event.checkpoint_path
    checkpoint = Path(shutil.copytree(source, tmp_path / "checkpoint-4"))
    rng_path = checkpoint / "rng_state.pth"
    with rng_path.open("r+b") as stream:
        first = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first[0] ^ 0xFF]))

    audit = run_static_audit(
        checkpoint_path=checkpoint,
        framework_selection=FrameworkSelection.AUTO,
        profile=QualificationProfile.EXACT_TRAINING_RESUME,
        output_dir=tmp_path / "audit-tampered",
    )

    assert audit.result.status is AuditStatus.FAIL
    failed = {check.check_id for check in audit.result.checks if check.status is AuditStatus.FAIL}
    assert {"state.python_rng", "state.numpy_rng", "state.torch_rng"} <= failed


def test_model_only_checkpoint_loads_but_fails_exact_trajectory(
    model_only_hf_run: tuple[Path, HFQualificationResult],
) -> None:
    root, result = model_only_hf_run

    assert result.final_verdict == "FAILED"
    assert result.model_checkpoint_load_succeeded is True
    assert result.model_only_diverged is True
    assert result.gate.passed is False
    assert {"checkpoint.optimizer", "checkpoint.scheduler", "checkpoint.rng"}.issubset(
        result.gate.failed_check_ids
    )
    assert "trajectory.loss-history" in result.gate.failed_check_ids
    assert result.checkpoint_event.model_present is True
    assert result.checkpoint_event.trainer_state_present is True
    assert result.checkpoint_event.optimizer_present is False
    assert result.checkpoint_event.scheduler_present is False
    assert result.checkpoint_event.rng_state_present is False
    assert result.recovery.trainer_global_step == result.control.trainer_global_step == 8
    assert result.recovery.loss_history != result.control.loss_history
    assert result.verified_persisted_bytes is None
    assert not (root / RECOVERY_ATTESTATION_PATH).exists()
    suite = ElementTree.parse(root / "junit.xml").getroot()
    assert suite.attrib["tests"] == "13"
    assert int(suite.attrib["failures"]) == len(result.gate.failed_check_ids)
    junit = (root / "junit.xml").read_text(encoding="utf-8")
    summary = (root / "job-summary.md").read_text(encoding="utf-8")
    for check_id in result.gate.failed_check_ids:
        assert check_id in junit
        assert f"`{check_id}`" in summary
    sarif = json.loads((root / "results.sarif").read_text(encoding="utf-8"))
    assert {finding["ruleId"] for finding in sarif["runs"][0]["results"]} == set(
        result.gate.failed_check_ids
    )


def test_hf_ci_policy_passes_verified_and_fails_model_only(
    complete_hf_run: tuple[Path, HFQualificationResult],
    model_only_hf_run: tuple[Path, HFQualificationResult],
) -> None:
    complete_root, _ = complete_hf_run
    model_only_root, model_only = model_only_hf_run
    runner = CliRunner()

    complete = runner.invoke(
        app,
        [
            "emit-junit",
            "--run-dir",
            str(complete_root),
            "--policy",
            "examples/ci/policy.yml",
        ],
    )
    failed = runner.invoke(
        app,
        [
            "emit-junit",
            "--run-dir",
            str(model_only_root),
            "--policy",
            "examples/ci/policy.yml",
        ],
    )

    assert complete.exit_code == 0, complete.output
    assert "Policy: PASS" in complete.output
    assert failed.exit_code == EXIT_QUALIFICATION_FAILED
    assert failed.output.startswith("FAILED")
    assert "FAILED REQUIREMENT policy.qualification-verdict" in failed.output
    for check_id in model_only.gate.failed_check_ids:
        assert check_id in (model_only_root / "junit.xml").read_text(encoding="utf-8")
