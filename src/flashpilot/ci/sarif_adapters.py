"""Typed SARIF projections for V0.3 qualification result families."""

from __future__ import annotations

from flashpilot.ci.models import CICheck, CICheckStatus
from flashpilot.ci.sarif import render_sarif_checks
from flashpilot.conversion.models import (
    ConversionCaseResult,
    ConversionQualificationResult,
)
from flashpilot.fallback.models import PreviousValidFallbackResult
from flashpilot.fault_timing.models import RandomizedFaultTimingResult
from flashpilot.fuzzing.models import FuzzScenario, PartialWriteFuzzResult


def _binary_status(passed: bool) -> CICheckStatus:
    return CICheckStatus.PASS if passed else CICheckStatus.FAIL


def render_conversion_case_sarif(result: ConversionCaseResult) -> str:
    checks = tuple(
        CICheck(
            check_id=check.check_id,
            status=_binary_status(check.status == "pass"),
            summary=check.summary,
            expected=check.expected,
            actual=check.actual,
        )
        for check in result.checks
    )
    return render_sarif_checks(
        kind="conversion-comparison",
        framework="native-pytorch",
        checks=checks,
        source_uri="comparison.json",
    )


def render_conversion_qualification_sarif(result: ConversionQualificationResult) -> str:
    checks = tuple(
        CICheck(
            check_id=f"{case.conversion_kind.value}.{check.check_id}",
            status=_binary_status(check.status == "pass"),
            summary=check.summary,
            expected=check.expected,
            actual=check.actual,
        )
        for case in result.cases
        for check in case.checks
    )
    return render_sarif_checks(
        kind="conversion-qualification",
        framework="native-pytorch",
        checks=checks,
        source_uri="result.json",
    )


def render_fuzz_sarif(result: PartialWriteFuzzResult) -> str:
    checks = []
    for scenario in FuzzScenario:
        cases = tuple(case for case in result.cases if case.scenario is scenario)
        passed = sum(case.passed for case in cases)
        premature = sum(case.premature_acceptances for case in cases)
        checks.append(
            CICheck(
                check_id=f"fuzz.{scenario.value}",
                status=_binary_status(passed == len(cases) and premature == 0),
                summary=f"All {scenario.value} cases satisfy their deterministic contract.",
                expected=f"{len(cases)}/{len(cases)} passed; premature_acceptances=0",
                actual=f"{passed}/{len(cases)} passed; premature_acceptances={premature}",
            )
        )
    return render_sarif_checks(
        kind="partial-write-fuzz",
        framework="native-pytorch",
        checks=tuple(checks),
        source_uri="result.json",
    )


def render_fallback_sarif(result: PreviousValidFallbackResult) -> str:
    selection = tuple(
        CICheck(
            check_id=f"selection.{check.check_id}",
            status=_binary_status(check.status == "pass"),
            summary=check.summary,
            expected=check.expected,
            actual=check.actual,
        )
        for check in result.selection_checks
    )
    gate = tuple(
        CICheck(
            check_id=f"gate.{check.check_id}",
            status=(
                CICheckStatus.FAIL
                if check.status == "fail"
                else CICheckStatus.NOT_APPLICABLE
                if check.status == "not_applicable"
                else CICheckStatus.PASS
            ),
            summary=check.label,
            expected=check.expected,
            actual=check.actual,
        )
        for check in result.gate.checks
    )
    return render_sarif_checks(
        kind="previous-valid-fallback",
        framework="native-pytorch",
        checks=selection + gate,
        source_uri="result.json",
    )


def render_randomized_timing_sarif(result: RandomizedFaultTimingResult) -> str:
    checks = tuple(
        CICheck(
            check_id=f"trial.{trial.schedule.iteration:04d}",
            status=_binary_status(trial.passed),
            summary="Scheduled process termination satisfies exact recovery requirements.",
            expected=(
                f"gate={trial.gate_checks_total}/{trial.gate_checks_total}; "
                f"rpo<={trial.max_rpo_steps}; exact_control_match=true"
            ),
            actual=(
                f"gate={trial.gate_checks_passed}/{trial.gate_checks_total}; "
                f"rpo={trial.achieved_rpo_steps}; "
                f"exact_control_match={str(trial.exact_control_match).lower()}; "
                f"failed_checks={trial.failed_gate_check_ids}"
            ),
        )
        for trial in result.trials
    )
    return render_sarif_checks(
        kind="randomized-fault-timing",
        framework="native-pytorch",
        checks=checks,
        source_uri="result.json",
    )
