from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.domain.recovery import RngStateDigests, RuntimeSnapshot
from flashpilot.fallback.models import (
    FallbackCheckpointRecord,
    FallbackCheckpointSetEvent,
)
from flashpilot.fallback.qualification import (
    FallbackQualificationError,
    _worker_environment,
    run_previous_valid_fallback,
)
from flashpilot.fallback.schema import fallback_schema_documents

SHA = "a" * 64


def _snapshot(step: int) -> RuntimeSnapshot:
    return RuntimeSnapshot(
        global_step=step,
        loss_history=tuple(float(index) for index in range(step)),
        trainable_state_sha256=SHA,
        evaluation_sha256=SHA,
        optimizer_sha256=SHA,
        scheduler_sha256=SHA,
    )


def _record(step: int) -> FallbackCheckpointRecord:
    return FallbackCheckpointRecord(
        checkpoint_path=f"checkpoints/checkpoint-step-{step:06d}",
        global_step=step,
        committed_at=datetime.now(UTC),
        snapshot=_snapshot(step),
        rng_state=RngStateDigests(
            python_sha256=SHA,
            numpy_sha256=SHA,
            torch_sha256=SHA,
        ),
    )


def test_fallback_event_requires_exact_previous_and_newest_steps() -> None:
    with pytest.raises(ValidationError, match="steps 2 and 4"):
        FallbackCheckpointSetEvent(
            worker_pid=123,
            checkpoints=(_record(2), _record(3)),
        )


def test_fallback_worker_environment_strips_api_keys(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "secret-openai")
    monkeypatch.setenv("INTERNAL_API_KEY", "secret-internal")

    environment = _worker_environment()

    assert "OPENAI_API_KEY" not in environment
    assert "INTERNAL_API_KEY" not in environment
    assert environment["CUDA_VISIBLE_DEVICES"] == ""
    assert environment["PYTHONHASHSEED"] == "20260720"


def test_fallback_qualification_rejects_nonempty_output_without_mutation(tmp_path: Path) -> None:
    run_root = tmp_path / "owned"
    run_root.mkdir()
    owned = run_root / "keep.txt"
    owned.write_text("preserve\n", encoding="utf-8")

    with pytest.raises(FallbackQualificationError, match="new or empty"):
        run_previous_valid_fallback(run_root=run_root)

    assert owned.read_text(encoding="utf-8") == "preserve\n"


def test_fallback_timeout_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="positive"):
        run_previous_valid_fallback(run_root=tmp_path / "run", timeout_seconds=0)


def test_checked_in_fallback_schemas_match_strict_models() -> None:
    for filename, expected in fallback_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected
