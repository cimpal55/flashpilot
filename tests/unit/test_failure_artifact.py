import pytest

from flashpilot.verification.failure_artifact import (
    FORBIDDEN_FAILURE_PAYLOAD_TERMS,
    assert_sanitized_failure_payload,
)


@pytest.mark.parametrize("forbidden", FORBIDDEN_FAILURE_PAYLOAD_TERMS)
def test_failure_payload_guard_rejects_every_forbidden_term(forbidden: str) -> None:
    with pytest.raises(ValueError, match="forbidden terms"):
        assert_sanitized_failure_payload(f'{{"unsafe": "{forbidden}"}}')


def test_failure_payload_guard_accepts_observed_gate_evidence() -> None:
    assert_sanitized_failure_payload(
        '{"failed_check": "optimizer state did not restore", "checksum_valid": true}'
    )
