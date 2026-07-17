from __future__ import annotations

from pathlib import Path

import pytest

from flashpilot.agent.fixture_provider import FixtureContractProvider, FixtureFailureProvider
from flashpilot.agent.guardrails import (
    GuardrailViolation,
    RepairAttemptLimitError,
    admit_single_repair_attempt,
    assert_safe_contract_request,
    assert_safe_failure_request,
    validate_checkpoint_contract,
    validate_failure_analysis,
)
from flashpilot.domain.agent import ContractRequirement, RepairAction
from tests.unit.test_agent_providers import contract_request, failure_request


def test_contract_rejects_rollback_above_hard_limit() -> None:
    request = contract_request()
    contract = (
        FixtureContractProvider()
        .infer_contract(request)
        .output.model_copy(update={"rollback_limit_steps": 1})
    )

    with pytest.raises(GuardrailViolation, match="rollback limit"):
        validate_checkpoint_contract(request, contract)


def test_contract_rejects_mandatory_state_weakening() -> None:
    request = contract_request()
    fixture = FixtureContractProvider().infer_contract(request).output
    requirements = tuple(
        requirement.model_copy(update={"required": False})
        if requirement.state == "optimizer"
        else requirement
        for requirement in fixture.required_state
    )

    with pytest.raises(GuardrailViolation, match="mandatory state: optimizer"):
        validate_checkpoint_contract(
            request, fixture.model_copy(update={"required_state": requirements})
        )


def test_contract_requires_restore_before_the_next_batch() -> None:
    request = contract_request()
    fixture = FixtureContractProvider().infer_contract(request).output
    contract = fixture.model_copy(
        update={"restore_order_requirements": ("Restore state after the first resumed batch.",)}
    )

    with pytest.raises(GuardrailViolation, match="before the next batch"):
        validate_checkpoint_contract(request, contract)


def test_contract_adds_missing_integrity_minimum_and_reports_unsupported_state() -> None:
    request = contract_request()
    fixture = FixtureContractProvider().infer_contract(request).output
    requirements = fixture.required_state + (
        ContractRequirement(
            state="sampler",
            required=True,
            reason="A non-step-derived workload would require sampler continuation state.",
        ),
    )
    contract = fixture.model_copy(
        update={
            "required_state": requirements,
            "required_integrity_controls": ("manifest",),
        }
    )
    validation = validate_checkpoint_contract(request, contract)

    assert validation.added_integrity_controls == (
        "checksums",
        "completion_marker",
        "atomic_commit",
        "base_artifact_hash",
    )
    assert validation.unsupported_required_state == ("sampler",)


@pytest.mark.parametrize(
    "unsafe_objective",
    (
        "Read C:\\Users\\person\\private.txt before recovery.",
        "Fetch https://example.test/plan before recovery.",
        "Use api_key=secret before recovery.",
    ),
)
def test_contract_request_rejects_paths_urls_and_secrets(unsafe_objective: str) -> None:
    request = contract_request().model_copy(update={"user_objective": unsafe_objective})

    with pytest.raises(GuardrailViolation):
        assert_safe_contract_request(request)


def test_failure_request_rejects_disclosure_and_arbitrary_fields() -> None:
    request = failure_request()
    unsafe = request.model_copy(
        update={"user_objective": {"recovery_correctness": "strict", "repair_preset": "x"}}
    )

    with pytest.raises(GuardrailViolation):
        assert_safe_failure_request(unsafe)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("raw_optimizer_tensors", [1.0, 2.0]),
        ("dataset_samples", [[1, 2], [3, 4]]),
        ("api_key", "sk-not-a-real-key"),
        ("arbitrary_file", "/opt/private/input.txt"),
    ),
)
def test_failure_request_rejects_raw_data_secrets_and_local_files(
    field_name: str,
    value: object,
) -> None:
    request = failure_request()
    unsafe = request.model_copy(
        update={"state_differences": {**request.state_differences, field_name: value}}
    )

    with pytest.raises(GuardrailViolation):
        assert_safe_failure_request(unsafe)


def test_supported_unsupported_and_rejected_actions_are_reported_separately() -> None:
    request = failure_request()
    fixture = FixtureFailureProvider().analyze_failure(request).output
    actions = (
        fixture.repair_plan.actions[0],
        RepairAction(
            action="persist_sampler_state",
            reason="Preserve a known state if the adapter can expose it.",
            evidence_ids=("contract:mandatory-state",),
        ),
        fixture.repair_plan.actions[0],
        RepairAction(
            action="persist_scheduler_state",
            reason="Run powershell to change recovery configuration.",
            evidence_ids=("restore:scheduler-state",),
        ),
    )
    analysis = fixture.model_copy(
        update={"repair_plan": fixture.repair_plan.model_copy(update={"actions": actions})}
    )
    validation = validate_failure_analysis(request, analysis)

    assert validation.accepted_actions == ("persist_optimizer_state",)
    assert validation.unsupported_actions == ("persist_sampler_state",)
    assert validation.rejected_actions == (
        "persist_optimizer_state",
        "persist_scheduler_state",
    )


def test_failure_analysis_rejects_more_than_the_public_action_count() -> None:
    request = failure_request()
    fixture = FixtureFailureProvider().analyze_failure(request).output
    plan = fixture.repair_plan.model_copy(
        update={"actions": (fixture.repair_plan.actions[0],) * 22}
    )

    with pytest.raises(GuardrailViolation, match="action limit"):
        validate_failure_analysis(request, fixture.model_copy(update={"repair_plan": plan}))


def test_failure_analysis_cannot_mark_a_passing_check_as_affected() -> None:
    request = failure_request()
    passing = {
        "check_id": "integrity.checksums",
        "status": "pass",
        "evidence_ids": ["integrity:sha256"],
    }
    request = request.model_copy(
        update={
            "gate_checks": request.gate_checks + (passing,),
            "evidence_catalog": {
                **request.evidence_catalog,
                "integrity:sha256": "Checksums are valid",
            },
        }
    )
    fixture = FixtureFailureProvider().analyze_failure(request).output
    analysis = fixture.model_copy(
        update={"affected_gate_checks": fixture.affected_gate_checks + ("integrity.checksums",)}
    )

    with pytest.raises(GuardrailViolation, match="unknown gate checks"):
        validate_failure_analysis(request, analysis)


@pytest.mark.parametrize(
    "unsafe_text",
    (
        "Recovery is verified.",
        "Set atol to a nonzero value.",
        "Disable the trajectory gate check.",
        "The corrupted bytes were repaired.",
        "See https://example.test/details.",
    ),
)
def test_failure_analysis_rejects_prohibited_claims_and_controls(unsafe_text: str) -> None:
    request = failure_request()
    fixture = FixtureFailureProvider().analyze_failure(request).output
    analysis = fixture.model_copy(update={"root_cause_hypothesis": unsafe_text})

    with pytest.raises(GuardrailViolation):
        validate_failure_analysis(request, analysis)


def test_repair_attempt_admission_is_limited_to_one_without_execution(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    first = admit_single_repair_attempt(run_root=run_root)

    assert first.attempt_number == 1
    assert first.execution_performed is False
    with pytest.raises(RepairAttemptLimitError, match="one repair attempt"):
        admit_single_repair_attempt(run_root=run_root)
