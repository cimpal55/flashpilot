from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

import pytest
import torch
from typer.testing import CliRunner

from flashpilot.audit import (
    AUDIT_EXIT_CODES,
    AuditFramework,
    AuditStatus,
    FrameworkSelection,
    run_static_audit,
)
from flashpilot.audit.safety import AuditSafetyError, validate_safetensors_metadata
from flashpilot.checkpoints.adapter_strategies import save_missing_training_state
from flashpilot.cli import app
from flashpilot.contracts.models import QualificationProfile
from flashpilot.contracts.native import native_minimum_persistence_contract
from flashpilot.workload.profiles import CI_PROFILE
from flashpilot.workload.trainer import create_training_runtime, train_until
from tests.conftest import SafeFullFixture


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def _write_safetensors(path: Path) -> None:
    header = json.dumps(
        {"weight": {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}},
        separators=(",", ":"),
    ).encode("utf-8")
    path.write_bytes(len(header).to_bytes(8, "little") + header + b"\x00\x00\x00\x00")


def _hf_complete(root: Path) -> Path:
    checkpoint = root / "checkpoint-12"
    checkpoint.mkdir(parents=True)
    _write_safetensors(checkpoint / "model.safetensors")
    torch.save({"state": {0: {"step": torch.tensor(12)}}}, checkpoint / "optimizer.pt")
    torch.save({"last_epoch": 12}, checkpoint / "scheduler.pt")
    torch.save(
        {
            "python": [3, [1, 2, 3], None],
            "numpy": ["MT19937", [1, 2, 3], 0, 0, 0.0],
            "cpu": torch.arange(8, dtype=torch.uint8),
        },
        checkpoint / "rng_state.pth",
    )
    _write_json(
        checkpoint / "trainer_state.json",
        {"global_step": 12, "max_steps": 24, "epoch": 0.5},
    )
    _write_json(
        checkpoint / "training_args.json",
        {
            "seed": 17,
            "data_seed": 23,
            "per_device_train_batch_size": 2,
            "gradient_accumulation_steps": 1,
        },
    )
    _write_json(
        checkpoint / "config.json",
        {"model_type": "flashpilot-test", "_commit_hash": "a" * 40},
    )
    return checkpoint


def _hf_model_only(root: Path) -> Path:
    checkpoint = root / "model-only"
    checkpoint.mkdir(parents=True)
    _write_safetensors(checkpoint / "model.safetensors")
    _write_json(checkpoint / "config.json", {"model_type": "flashpilot-test"})
    return checkpoint


def _run(
    checkpoint: Path,
    output: Path,
    *,
    profile: QualificationProfile = QualificationProfile.EXACT_TRAINING_RESUME,
):
    return run_static_audit(
        checkpoint_path=checkpoint,
        framework_selection=FrameworkSelection.AUTO,
        profile=profile,
        output_dir=output,
    )


def _check(result, check_id: str):
    return next(check for check in result.checks if check.check_id == check_id)


def test_complete_native_checkpoint_passes_static_exact_audit(
    safe_full_fixture: SafeFullFixture,
    tmp_path: Path,
    monkeypatch,
) -> None:
    def reject_training(*args, **kwargs):
        raise AssertionError("static audit must not run training")

    monkeypatch.setattr("flashpilot.workload.trainer.train_until", reject_training)
    run = _run(
        safe_full_fixture.commit.checkpoint_path,
        tmp_path / "native-audit",
    )

    assert run.result.status is AuditStatus.PASS
    assert run.result.framework is AuditFramework.NATIVE_PYTORCH
    assert run.result.static_only is True
    assert run.result.recovery_verified is False
    assert run.audit_json.is_file()
    assert run.report_markdown.is_file()
    assert run.junit_xml.is_file()
    assert "VERIFIED" not in run.audit_json.read_text(encoding="utf-8")
    assert "never means VERIFIED recovery" in run.report_markdown.read_text(encoding="utf-8")
    required_state = {
        item.state_id
        for item in native_minimum_persistence_contract(
            QualificationProfile.EXACT_TRAINING_RESUME
        ).items
    }
    audited_state = {
        check.requirement_state_id
        for check in run.result.checks
        if check.requirement_state_id is not None and check.status is AuditStatus.PASS
    }
    assert required_state <= audited_state


def test_native_missing_training_state_fails_exact_resume_and_identifies_requirements(
    tmp_path: Path,
) -> None:
    run_root = tmp_path / "native-missing"
    runtime = create_training_runtime(CI_PROFILE)
    train_until(runtime, CI_PROFILE.steps // 2)
    saved = save_missing_training_state(runtime, run_root=run_root)

    run = _run(saved.checkpoint.checkpoint_path, tmp_path / "missing-audit")

    assert run.result.status is AuditStatus.FAIL
    failed = {
        check.requirement_state_id
        for check in run.result.checks
        if check.status is AuditStatus.FAIL
    }
    assert {"optimizer", "scheduler", "python_rng", "numpy_rng", "torch_rng"} <= failed
    root = ElementTree.parse(run.junit_xml).getroot()
    failed_cases = {
        case.attrib["name"] for case in root.findall("testcase") if case.find("failure") is not None
    }
    assert "state.optimizer" in failed_cases
    assert "state.scheduler" in failed_cases


def test_native_corrupted_payload_fails_static_audit(
    safe_full_fixture: SafeFullFixture,
    tmp_path: Path,
) -> None:
    model_path = safe_full_fixture.commit.checkpoint_path / "model.pt"
    with model_path.open("r+b") as stream:
        first = stream.read(1)
        stream.seek(0)
        stream.write(bytes([first[0] ^ 0xFF]))

    run = _run(safe_full_fixture.commit.checkpoint_path, tmp_path / "corrupt-audit")

    assert run.result.status is AuditStatus.FAIL
    assert _check(run.result, "integrity.checkpoint").status is AuditStatus.FAIL
    assert "checksum mismatch" in _check(run.result, "integrity.checkpoint").summary


def test_incomplete_native_temp_checkpoint_fails(tmp_path: Path) -> None:
    checkpoint = tmp_path / ".checkpoint-step-000012.tmp-interrupted"
    checkpoint.mkdir()
    (checkpoint / "model.pt").write_bytes(b"partial")

    run = _run(checkpoint, tmp_path / "incomplete-audit")

    assert run.result.framework is AuditFramework.NATIVE_PYTORCH
    assert run.result.status is AuditStatus.FAIL
    assert _check(run.result, "lifecycle.incomplete").status is AuditStatus.FAIL


def test_hf_complete_checkpoint_passes_supported_exact_audit(tmp_path: Path) -> None:
    checkpoint = _hf_complete(tmp_path / "hf-complete")

    run = _run(checkpoint, tmp_path / "hf-complete-audit")

    assert run.result.status is AuditStatus.PASS
    assert run.result.framework is AuditFramework.HUGGINGFACE_TRAINER
    assert all(check.status is AuditStatus.PASS for check in run.result.checks)


def test_hf_model_only_fails_exact_resume_but_passes_model_only_profile(tmp_path: Path) -> None:
    checkpoint = _hf_model_only(tmp_path / "hf-model-only")

    exact = _run(checkpoint, tmp_path / "hf-model-exact")
    model_only = _run(
        checkpoint,
        tmp_path / "hf-model-inference",
        profile=QualificationProfile.MODEL_ONLY_INFERENCE,
    )

    assert exact.result.status is AuditStatus.FAIL
    assert _check(exact.result, "state.optimizer").status is AuditStatus.FAIL
    assert _check(exact.result, "state.scheduler").status is AuditStatus.FAIL
    assert model_only.result.status is AuditStatus.PASS
    assert model_only.result.recovery_verified is False


def test_unknown_layout_is_unknown_and_never_passes(tmp_path: Path) -> None:
    checkpoint = tmp_path / "unrecognized-checkpoint"
    checkpoint.mkdir()
    (checkpoint / "opaque.data").write_bytes(b"unknown")

    run = _run(checkpoint, tmp_path / "unknown-audit")

    assert run.result.status is AuditStatus.UNKNOWN
    assert run.result.framework is AuditFramework.UNKNOWN
    assert run.result.recovery_verified is False
    assert AUDIT_EXIT_CODES[run.result.status] == 2


def test_shared_training_payload_name_alone_does_not_claim_hf_layout(tmp_path: Path) -> None:
    checkpoint = tmp_path / "ambiguous-payload"
    checkpoint.mkdir()
    torch.save({"state": {}}, checkpoint / "optimizer.pt")

    run = _run(checkpoint, tmp_path / "ambiguous-audit")

    assert run.result.status is AuditStatus.UNKNOWN
    assert run.result.framework is AuditFramework.UNKNOWN


def test_unknown_hf_file_is_reported_and_changes_pass_to_warn(tmp_path: Path) -> None:
    checkpoint = _hf_complete(tmp_path / "hf-unknown-file")
    (checkpoint / "custom_state.pkl").write_bytes(b"not loaded")

    run = _run(checkpoint, tmp_path / "hf-warning-audit")

    assert run.result.status is AuditStatus.WARN
    inventory = _check(run.result, "inventory.unknown-files")
    assert inventory.status is AuditStatus.WARN
    assert inventory.evidence_paths == ("custom_state.pkl",)


def test_training_args_binary_is_never_unpickled(tmp_path: Path, monkeypatch) -> None:
    checkpoint = _hf_complete(tmp_path / "hf-binary-args")
    (checkpoint / "training_args.json").unlink()
    (checkpoint / "training_args.bin").write_bytes(b"unsafe-pickle-placeholder")
    real_torch_load = torch.load
    loaded_names: list[str] = []

    def recording_load(path, *args, **kwargs):
        loaded_names.append(Path(path).name)
        return real_torch_load(path, *args, **kwargs)

    monkeypatch.setattr(torch, "load", recording_load)
    run = _run(checkpoint, tmp_path / "hf-binary-audit")

    assert run.result.status is AuditStatus.FAIL
    assert "training_args.bin" not in loaded_names
    assert "was not unpickled" in _check(run.result, "metadata.training-arguments").summary


def test_invalid_safetensors_offsets_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "model.safetensors"
    header = json.dumps({"weight": {"dtype": "F32", "shape": [1], "data_offsets": [0, 8]}}).encode(
        "utf-8"
    )
    path.write_bytes(len(header).to_bytes(8, "little") + header + b"\x00" * 4)

    with pytest.raises(AuditSafetyError, match="escape"):
        validate_safetensors_metadata(path)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (AuditStatus.PASS, 0),
        (AuditStatus.WARN, 2),
        (AuditStatus.UNKNOWN, 2),
        (AuditStatus.FAIL, 3),
    ],
)
def test_static_audit_exit_codes_are_stable(status: AuditStatus, expected: int) -> None:
    assert AUDIT_EXIT_CODES[status] == expected


def test_audit_cli_writes_outputs_and_uses_status_exit_code(tmp_path: Path) -> None:
    checkpoint = _hf_model_only(tmp_path / "cli-model-only")
    output = tmp_path / "cli-audit"

    result = CliRunner().invoke(
        app,
        [
            "audit-checkpoint",
            str(checkpoint),
            "--framework",
            "auto",
            "--profile",
            "exact-training-resume",
            "--output-dir",
            str(output),
        ],
    )

    assert result.exit_code == 3, result.output
    assert result.output.splitlines()[0] == "FAIL"
    assert "recovery_verified=false" in result.output
    assert (output / "audit.json").is_file()
    assert (output / "report.md").is_file()
    assert (output / "junit.xml").is_file()


def test_audit_cli_rejects_unsupported_framework_with_stable_exit_code(tmp_path: Path) -> None:
    checkpoint = _hf_model_only(tmp_path / "cli-unsupported")

    result = CliRunner().invoke(
        app,
        ["audit-checkpoint", str(checkpoint), "--framework", "tensorflow"],
    )

    assert result.exit_code == 5
    assert "Unsupported audit configuration" in result.output


def test_audit_output_cannot_modify_checkpoint(tmp_path: Path) -> None:
    checkpoint = _hf_model_only(tmp_path / "overlap")

    with pytest.raises(ValueError, match="outside the checkpoint"):
        run_static_audit(
            checkpoint_path=checkpoint,
            framework_selection=FrameworkSelection.AUTO,
            profile=QualificationProfile.MODEL_ONLY_INFERENCE,
            output_dir=checkpoint / "audit-output",
        )
