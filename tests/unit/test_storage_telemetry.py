"""Tests for optional storage telemetry.

The central guarantee under test is negative: this subsystem must never be able
to influence a verdict, never estimate a counter it did not read, and never
express a NAND-wear or drive-lifetime claim.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.telemetry.models import (
    NVME_DATA_UNIT_BYTES,
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


def test_byte_lower_bound_must_derive_from_the_unit_delta() -> None:
    # A byte figure that does not follow from the measured units would be a
    # fabricated metric.
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(
            window_seconds=1.0,
            data_units_written_delta=10,
            host_write_bytes_lower_bound=1,
        )


def test_byte_lower_bound_requires_a_unit_delta() -> None:
    with pytest.raises(ValidationError):
        StorageTelemetryDelta(window_seconds=1.0, host_write_bytes_lower_bound=512_000)


def test_derived_byte_lower_bound_is_accepted() -> None:
    delta = StorageTelemetryDelta(
        window_seconds=2.0,
        data_units_written_delta=3,
        host_write_bytes_lower_bound=3 * NVME_DATA_UNIT_BYTES,
    )
    assert delta.host_write_bytes_lower_bound == 1_536_000
    assert delta.attribution == "device-wide-not-attributable"


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

    monkeypatch.setattr(service, "collect_sample", lambda device=None: _Result())
    evidence = finish_capture(
        StorageTelemetryCapture(before=before, availability=_available(), device=None)
    )
    assert evidence.delta is not None
    assert evidence.delta.counter_wrapped is True
    assert evidence.delta.data_units_written_delta is None
    assert evidence.delta.host_write_bytes_lower_bound is None


def test_normal_window_computes_a_lower_bound(monkeypatch) -> None:
    from flashpilot.telemetry import service

    before = _sample(units=1_000, when=datetime.now(UTC))
    after = _sample(units=1_004, when=before.captured_at + timedelta(seconds=3))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None: _Result())
    evidence = finish_capture(
        StorageTelemetryCapture(before=before, availability=_available(), device=None)
    )
    assert evidence.delta is not None
    assert evidence.delta.data_units_written_delta == 4
    assert evidence.delta.host_write_bytes_lower_bound == 4 * NVME_DATA_UNIT_BYTES
    assert evidence.delta.counter_wrapped is False
    assert evidence.influences_verdict is False


def test_device_change_between_samples_is_rejected(monkeypatch) -> None:
    from flashpilot.telemetry import service

    before = _sample(device="/dev/nvme0")
    after = _sample(device="/dev/nvme1", when=before.captured_at + timedelta(seconds=1))

    class _Result:
        sample = after
        availability = _available()

    monkeypatch.setattr(service, "collect_sample", lambda device=None: _Result())
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
