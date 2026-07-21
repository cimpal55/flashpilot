"""Tests for optional storage telemetry.

The central guarantee under test is negative: this subsystem must never be able
to influence a verdict, never estimate a counter it did not read, and never
express a NAND-wear or drive-lifetime claim.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.telemetry.models import (
    MAX_OBSERVATION_SECONDS,
    MIN_OBSERVATION_SECONDS,
    NVME_COUNTER_GRANULARITY_BYTES,
    STORAGE_TELEMETRY_LIMITATIONS,
    StorageTelemetryAvailability,
    StorageTelemetryCounters,
    StorageTelemetryDelta,
    StorageTelemetryEvidenceV1,
    StorageTelemetrySample,
)
from flashpilot.telemetry.service import (
    StorageTelemetryCapture,
    StorageTelemetryError,
    finish_capture,
    observe,
    read_storage_telemetry,
    start_capture,
    write_storage_telemetry,
)


def _sample(
    *,
    device: str = "/dev/nvme0",
    units: int | None = 1_000,
    when: datetime | None = None,
) -> StorageTelemetrySample:
    return StorageTelemetrySample(
        captured_at=when or datetime.now(UTC),
        device_id=device,
        device_kind="nvme",
        source="linux-nvme-cli",
        counters=StorageTelemetryCounters(data_units_written=units, host_write_commands=10),
    )


def _available() -> StorageTelemetryAvailability:
    return StorageTelemetryAvailability(available=True, reason="collected", detail="test")


def test_evidence_is_structurally_supporting_only() -> None:
    evidence = StorageTelemetryEvidenceV1(
        availability=StorageTelemetryAvailability(
            available=False, reason="unsupported-platform", detail="test"
        ),
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )
    assert evidence.evidence_class == "supporting-only"
    assert evidence.influences_verdict is False


def test_influences_verdict_cannot_be_set_true() -> None:
    # The guarantee is enforced by the type, not by convention.
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=StorageTelemetryAvailability(
                available=False, reason="unsupported-platform", detail="test"
            ),
            influences_verdict=True,
            limitations=STORAGE_TELEMETRY_LIMITATIONS,
        )


def test_attribution_cannot_claim_process_attribution() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(window_seconds=1.0, attribution="this-run")


def test_limitations_state_what_is_not_measured() -> None:
    joined = " ".join(STORAGE_TELEMETRY_LIMITATIONS).lower()
    assert "nand wear" in joined
    assert "lifetime" in joined
    assert "device-wide" in joined
    assert "does not contribute" in joined


def test_limitations_are_required() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=StorageTelemetryAvailability(
                available=False, reason="unsupported-platform", detail="test"
            ),
            limitations=(),
        )


def test_unavailable_evidence_may_not_carry_samples() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=StorageTelemetryAvailability(
                available=False, reason="tool-unavailable", detail="test"
            ),
            before=_sample(),
            limitations=STORAGE_TELEMETRY_LIMITATIONS,
        )


def test_available_evidence_requires_both_samples() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=_available(),
            before=_sample(),
            limitations=STORAGE_TELEMETRY_LIMITATIONS,
        )


def test_mismatched_devices_are_rejected() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=_available(),
            before=_sample(device="/dev/nvme0"),
            after=_sample(device="/dev/nvme1"),
            limitations=STORAGE_TELEMETRY_LIMITATIONS,
        )


def test_reversed_samples_are_rejected() -> None:
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        StorageTelemetryEvidenceV1(
            availability=_available(),
            before=_sample(when=now),
            after=_sample(when=now - timedelta(seconds=5)),
            limitations=STORAGE_TELEMETRY_LIMITATIONS,
        )


def test_no_byte_field_exists_on_the_delta() -> None:
    # NVMe Data Units Written is rounded at both ends of the window, so no
    # byte count and no byte lower bound honestly follows from a unit delta.
    # The safest guarantee is that there is nowhere to record one.
    assert "host_write_bytes_lower_bound" not in StorageTelemetryDelta.model_fields
    assert not any(
        "byte" in name and name != "counter_granularity_bytes"
        for name in StorageTelemetryDelta.model_fields
    )
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(window_seconds=1.0, host_write_bytes_lower_bound=512_000)


def test_units_are_published_with_their_granularity_uninterpreted() -> None:
    delta = StorageTelemetryDelta(
        window_seconds=2.0,
        data_units_written_delta=3,
        counter_granularity_bytes=NVME_COUNTER_GRANULARITY_BYTES,
    )
    assert delta.data_units_written_delta == 3
    assert delta.counter_granularity_bytes == NVME_COUNTER_GRANULARITY_BYTES
    assert delta.attribution == "device-wide-not-attributable"


def test_granularity_requires_a_unit_delta_and_must_be_the_real_value() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(window_seconds=1.0, counter_granularity_bytes=512_000)
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(
            window_seconds=1.0,
            data_units_written_delta=3,
            counter_granularity_bytes=4096,
        )


def test_disabled_collection_reports_disabled_without_running_anything() -> None:
    capture = start_capture(enabled=False)
    assert capture.before is None
    assert capture.availability.reason == "collection-disabled"
    evidence = finish_capture(capture)
    assert evidence.availability.available is False
    assert evidence.delta is None


def test_finish_without_opening_sample_is_unavailable_not_an_error() -> None:
    capture = StorageTelemetryCapture(
        before=None,
        availability=StorageTelemetryAvailability(
            available=False, reason="insufficient-privileges", detail="no root"
        ),
        device=None,
    )
    evidence = finish_capture(capture)
    assert evidence.availability.reason == "insufficient-privileges"
    assert evidence.before is None


def test_backwards_counter_drops_the_delta_rather_than_clamping(monkeypatch) -> None:
    """A wrapped or reset counter must not look like a real zero-write window."""
    from flashpilot.telemetry import service

    before = _sample(units=5_000, when=datetime.now(UTC))
    after = _sample(units=10, when=before.captured_at + timedelta(seconds=1))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None, run_dir=None: _Result())
    evidence = finish_capture(
        StorageTelemetryCapture(before=before, availability=_available(), device=None)
    )
    assert evidence.delta is not None
    assert evidence.delta.counter_wrapped is True
    assert evidence.delta.data_units_written_delta is None
    assert evidence.delta.counter_granularity_bytes is None


def test_normal_window_publishes_units_and_granularity(monkeypatch) -> None:
    from flashpilot.telemetry import service

    before = _sample(units=1_000, when=datetime.now(UTC))
    after = _sample(units=1_004, when=before.captured_at + timedelta(seconds=3))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None, run_dir=None: _Result())
    evidence = finish_capture(
        StorageTelemetryCapture(before=before, availability=_available(), device=None)
    )
    assert evidence.delta is not None
    assert evidence.delta.data_units_written_delta == 4
    assert evidence.delta.counter_granularity_bytes == NVME_COUNTER_GRANULARITY_BYTES
    assert evidence.delta.counter_wrapped is False
    assert evidence.influences_verdict is False


def test_device_change_between_samples_is_rejected(monkeypatch) -> None:
    from flashpilot.telemetry import service

    before = _sample(device="/dev/nvme0")
    after = _sample(device="/dev/nvme1", when=before.captured_at + timedelta(seconds=1))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None, run_dir=None: _Result())
    evidence = finish_capture(
        StorageTelemetryCapture(before=before, availability=_available(), device=None)
    )
    assert evidence.availability.available is False
    assert evidence.availability.reason == "no-supported-device"


def test_round_trip_is_stable(tmp_path: Path) -> None:
    evidence = StorageTelemetryEvidenceV1(
        availability=StorageTelemetryAvailability(
            available=False, reason="unsupported-platform", detail="test"
        ),
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )
    target = write_storage_telemetry(evidence, tmp_path)
    assert target.name == "storage-telemetry.json"
    assert read_storage_telemetry(target) == evidence

    first = target.read_bytes()
    write_storage_telemetry(evidence, tmp_path)
    assert target.read_bytes() == first


def test_written_artifact_declares_it_is_not_verdict_bearing(tmp_path: Path) -> None:
    evidence = StorageTelemetryEvidenceV1(
        availability=StorageTelemetryAvailability(
            available=False, reason="tool-unavailable", detail="test"
        ),
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )
    payload = json.loads(write_storage_telemetry(evidence, tmp_path).read_text(encoding="utf-8"))
    assert payload["evidence_class"] == "supporting-only"
    assert payload["influences_verdict"] is False


def test_missing_run_directory_is_an_error(tmp_path: Path) -> None:
    evidence = StorageTelemetryEvidenceV1(
        availability=StorageTelemetryAvailability(
            available=False, reason="tool-unavailable", detail="test"
        ),
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )
    with pytest.raises(StorageTelemetryError):
        write_storage_telemetry(evidence, tmp_path / "absent")


def test_malformed_artifact_fails_closed(tmp_path: Path) -> None:
    target = tmp_path / "storage-telemetry.json"
    target.write_text('{"schema_version": "wrong"}', encoding="utf-8")
    with pytest.raises(ValidationError):
        read_storage_telemetry(target)


def test_counter_coercion_never_guesses() -> None:
    from flashpilot.telemetry.collectors import _coerce_counter

    assert _coerce_counter(12) == 12
    assert _coerce_counter("1,024") == 1024
    assert _coerce_counter(3.0) == 3
    # Anything ambiguous is dropped rather than approximated.
    assert _coerce_counter(-1) is None
    assert _coerce_counter(1.5) is None
    assert _coerce_counter(True) is None
    assert _coerce_counter("about 40") is None
    assert _coerce_counter(None) is None
    assert _coerce_counter({"value": 1}) is None


def test_collector_reports_unsupported_platform(monkeypatch) -> None:
    from flashpilot.telemetry import collectors

    monkeypatch.setattr(collectors.sys, "platform", "sunos5")
    result = collectors.collect_sample()
    assert result.sample is None
    assert result.availability.reason == "unsupported-platform"


# ---- Observation window (plan 4.2) -------------------------------------


def test_observation_window_is_bounded() -> None:
    capture = start_capture(enabled=False)
    for bad in (0, -1, MAX_OBSERVATION_SECONDS + 1):
        with pytest.raises(StorageTelemetryError):
            observe(capture, bad)


def test_observation_window_does_not_sleep_when_unavailable() -> None:
    # Nothing can be measured without an opening sample, so the window is
    # skipped rather than blocking the caller for no reason.
    capture = start_capture(enabled=False)
    started = time.monotonic()
    evidence = observe(capture, MIN_OBSERVATION_SECONDS)
    assert time.monotonic() - started < 0.5
    assert evidence.availability.available is False


def test_observation_window_records_the_actual_elapsed_duration(monkeypatch) -> None:
    from flashpilot.telemetry import service

    before = _sample(units=1_000, when=datetime.now(UTC))
    after = _sample(units=1_002, when=before.captured_at + timedelta(seconds=7.5))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None, run_dir=None: _Result())
    monkeypatch.setattr(service.time, "sleep", lambda seconds: None)

    evidence = observe(
        StorageTelemetryCapture(before=before, availability=_available(), device=None), 5
    )
    # The recorded window is the real gap between the samples, not the request.
    assert evidence.delta is not None
    assert evidence.delta.window_seconds == pytest.approx(7.5)


# ---- Output cap (plan 4.3) ---------------------------------------------


def test_output_cap_stops_an_oversized_collector() -> None:
    from flashpilot.telemetry import collectors

    argv = [
        sys.executable,
        "-c",
        "import sys\nsys.stdout.write('x' * (2 * 1024 * 1024))",
    ]
    with pytest.raises(collectors._OutputLimitExceeded):
        collectors._run_readonly(argv)


def test_bounded_output_is_returned_intact() -> None:
    from flashpilot.telemetry import collectors

    argv = [sys.executable, "-c", "print('flashpilot')"]
    result = collectors._run_readonly(argv)
    assert result is not None
    returncode, stdout = result
    assert returncode == 0
    assert "flashpilot" in stdout


def test_failed_process_launch_is_reported_as_none() -> None:
    from flashpilot.telemetry import collectors

    assert collectors._run_readonly(["definitely-not-a-real-binary-xyz"]) is None


# ---- Safe artifact writing (plan 4.4) ----------------------------------


def _unavailable_evidence() -> StorageTelemetryEvidenceV1:
    return StorageTelemetryEvidenceV1(
        availability=StorageTelemetryAvailability(
            available=False, reason="tool-unavailable", detail="test"
        ),
        limitations=STORAGE_TELEMETRY_LIMITATIONS,
    )


def test_existing_different_artifact_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "storage-telemetry.json"
    target.write_text('{"schema_version": "something-else"}\n', encoding="utf-8")
    with pytest.raises(StorageTelemetryError):
        write_storage_telemetry(_unavailable_evidence(), tmp_path)
    # The pre-existing file is left untouched rather than overwritten.
    assert "something-else" in target.read_text(encoding="utf-8")


def test_identical_rewrite_is_a_no_op(tmp_path: Path) -> None:
    evidence = _unavailable_evidence()
    first = write_storage_telemetry(evidence, tmp_path).read_bytes()
    again = write_storage_telemetry(evidence, tmp_path).read_bytes()
    assert first == again


def test_symlinked_target_is_rejected(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    try:
        (run_dir / "storage-telemetry.json").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are unavailable on this host")
    with pytest.raises(StorageTelemetryError):
        write_storage_telemetry(_unavailable_evidence(), run_dir)
    assert outside.read_text(encoding="utf-8") == "{}"


def test_no_temporary_file_survives_a_successful_write(tmp_path: Path) -> None:
    write_storage_telemetry(_unavailable_evidence(), tmp_path)
    assert list(tmp_path.glob("*.tmp")) == []


def test_partial_temporary_file_never_becomes_the_artifact(tmp_path: Path, monkeypatch) -> None:
    from flashpilot.telemetry import service

    def explode(temporary, target):
        raise OSError("simulated replace failure")

    monkeypatch.setattr(service.os, "replace", explode)
    with pytest.raises(StorageTelemetryError):
        write_storage_telemetry(_unavailable_evidence(), tmp_path)

    assert not (tmp_path / "storage-telemetry.json").exists()
    assert list(tmp_path.glob("*.tmp")) == []


# ---- Device binding (plan 4.5) -----------------------------------------


def test_windows_collector_fails_closed_without_a_run_directory(monkeypatch) -> None:
    from flashpilot.telemetry import collectors

    monkeypatch.setattr(collectors.sys, "platform", "win32")
    monkeypatch.setattr(collectors.shutil, "which", lambda name: "powershell")
    result = collectors.collect_sample(run_dir=None)
    assert result.sample is None
    assert result.availability.reason == "device-not-bound"


def test_windows_collector_fails_closed_on_an_unbindable_path(monkeypatch, tmp_path) -> None:
    from flashpilot.telemetry import collectors

    monkeypatch.setattr(collectors.sys, "platform", "win32")
    monkeypatch.setattr(collectors.shutil, "which", lambda name: "powershell")
    monkeypatch.setattr(collectors, "_windows_drive_letter", lambda run_dir: None)
    result = collectors.collect_sample(run_dir=tmp_path)
    assert result.sample is None
    assert result.availability.reason == "device-not-bound"


def test_windows_drive_letter_rejects_unbindable_paths(tmp_path: Path) -> None:
    from flashpilot.telemetry.collectors import _windows_drive_letter

    # A UNC path has no drive letter, so it cannot be bound to a physical disk.
    assert _windows_drive_letter(Path("//server/share/run")) is None
    # A path that does not exist must not fall back to the current drive.
    assert _windows_drive_letter(tmp_path / "absent") is None
    # A file is not a run directory.
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")
    assert _windows_drive_letter(target) is None


def test_wear_is_not_collected() -> None:
    # The project makes no wear claim, so the counter is not even requested.
    from flashpilot.telemetry import collectors

    assert "Wear" not in collectors._WINDOWS_COUNTER_SCRIPT
    assert "wear" not in str(StorageTelemetryCounters.model_fields.keys()).lower()


# ---- The negative guarantee (plan 4.6) ---------------------------------


def _module_sources() -> str:
    roots = [
        Path("src/flashpilot/verification"),
        Path("src/flashpilot/attestation"),
        Path("src/flashpilot/ci"),
    ]
    text = []
    for root in roots:
        for path in root.rglob("*.py"):
            text.append(path.read_text(encoding="utf-8"))
    return "\n".join(text)


def test_telemetry_is_not_imported_by_gate_attestation_or_policy() -> None:
    # The strongest available guarantee that telemetry cannot influence a
    # verdict: the verdict-bearing packages never import it at all.
    assert "flashpilot.telemetry" not in _module_sources()


def test_telemetry_does_not_import_verdict_bearing_modules() -> None:
    sources = "\n".join(
        path.read_text(encoding="utf-8") for path in Path("src/flashpilot/telemetry").rglob("*.py")
    )
    for forbidden in (
        "flashpilot.verification",
        "flashpilot.attestation",
        "flashpilot.ci",
    ):
        assert forbidden not in sources
