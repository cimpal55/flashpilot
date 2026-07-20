from __future__ import annotations

import json
import os
from pathlib import Path
from xml.etree import ElementTree

import pytest

from flashpilot.attestation import RECOVERY_ATTESTATION_PATH, verify_recovery_attestation
from flashpilot.checkpoints.integrity import logical_directory_bytes
from flashpilot.preemption.models import PREEMPTION_INCOMPLETE_MARKER
from flashpilot.preemption.service import run_hf_preemption_certification

SCRIPT = Path(__file__).resolve().parents[2] / "examples" / "hf_trainer" / "train.py"


@pytest.mark.skipif(os.name != "posix", reason="real external POSIX SIGTERM is unavailable")
def test_sigterm_commits_before_exit_and_exact_resume_is_attested(tmp_path: Path) -> None:
    root = tmp_path / "preemption"
    result = run_hf_preemption_certification(
        script_path=SCRIPT,
        run_root=root,
        grace_period_seconds=30,
    )
    checkpoint = root / result.commit_event.checkpoint.checkpoint_path

    assert result.final_verdict == "VERIFIED"
    assert result.preemption_process.exit_code == 0
    assert result.preemption_process.exit_verified is True
    assert result.ready_event.emitted_at <= result.signal_sent_at
    assert result.signal_sent_at <= result.commit_event.signal_received_at
    assert (
        result.commit_event.signal_received_at
        <= result.commit_event.checkpoint_committed_at
        <= result.preemption_process.completed_at
    )
    assert result.checkpoint_commit_seconds <= result.graceful_exit_seconds <= 30
    assert not (root / PREEMPTION_INCOMPLETE_MARKER).exists()
    assert result.gate.passed is True
    assert result.gate.failed_check_ids == ()
    assert result.gate.atol == result.gate.rtol == 0.0
    assert result.gate.achieved_rpo_steps == result.gate.achieved_rpo_tokens == 0
    assert result.control.loss_history == result.recovery.loss_history
    assert result.control.trainable_state_sha256 == result.recovery.trainable_state_sha256
    assert result.control.evaluation_sha256 == result.recovery.evaluation_sha256
    assert result.control.optimizer_sha256 == result.recovery.optimizer_sha256
    assert result.control.scheduler_sha256 == result.recovery.scheduler_sha256
    assert result.verified_persisted_bytes == logical_directory_bytes(checkpoint)
    assert verify_recovery_attestation(root / RECOVERY_ATTESTATION_PATH).valid is True

    suite = ElementTree.parse(root / "junit.xml").getroot()
    assert suite.attrib["tests"] == "22"
    assert suite.attrib["failures"] == "0"
    sarif = json.loads((root / "results.sarif").read_text(encoding="utf-8"))
    assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) == 22
    assert sarif["runs"][0]["results"] == []

    for relative in (
        "result.json",
        "report.md",
        "report.html",
        "junit.xml",
        "job-summary.md",
        "results.sarif",
        "recovery.attestation.json",
    ):
        text = (root / relative).read_text(encoding="utf-8")
        assert str(root.resolve()) not in text
        assert "OPENAI_API_KEY" not in text
