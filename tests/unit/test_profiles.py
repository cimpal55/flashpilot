import pytest

from flashpilot.workload.profiles import CI_PROFILE, DEMO_PROFILE, get_profile


def test_ci_and_demo_profiles_are_bounded_and_use_dropout() -> None:
    assert get_profile("ci") is CI_PROFILE
    assert get_profile("demo") is DEMO_PROFILE
    assert 0 < CI_PROFILE.steps < DEMO_PROFILE.steps <= 40
    assert CI_PROFILE.dropout > 0
    assert DEMO_PROFILE.dropout > 0


def test_unknown_profile_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown profile"):
        get_profile("unknown")
