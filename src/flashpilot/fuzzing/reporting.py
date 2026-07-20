"""Deterministic Markdown and JUnit views of typed fuzz evidence."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from flashpilot.fuzzing.models import PartialWriteFuzzResult


def render_fuzz_markdown(result: PartialWriteFuzzResult) -> str:
    rows = []
    for scenario in dict.fromkeys(case.scenario for case in result.cases):
        cases = [case for case in result.cases if case.scenario is scenario]
        passed = sum(case.passed for case in cases)
        premature = sum(case.premature_acceptances for case in cases)
        rows.append(
            f"| `{scenario.value}` | {len(cases)} | {passed} | "
            f"{len(cases) - passed} | {premature} |"
        )
    return (
        "# Partial-write and incomplete-commit fuzz qualification\n\n"
        f"- Verdict: **{result.verdict}**\n"
        f"- Deterministic iterations: `{result.iterations}`\n"
        f"- Cases: `{result.total_cases}`\n"
        f"- Premature acceptances: `{result.premature_acceptances}`\n"
        f"- Schedule SHA-256: `{result.schedule_sha256}`\n"
        "- Recovery verified: `false`\n"
        "- Attestation emitted: `false`\n"
        "- Storage savings reported: `false`\n\n"
        "| Fault scenario | Cases | Passed | Failed | Premature acceptances |\n"
        "| --- | ---: | ---: | ---: | ---: |\n"
        + "\n".join(rows)
        + "\n\n## Limitations\n\n"
        + "\n".join(f"- {limitation}" for limitation in result.limitations)
        + "\n"
    )


def render_fuzz_junit(result: PartialWriteFuzzResult) -> str:
    suite = Element(
        "testsuite",
        name="flashpilot.partial-write-fuzz",
        tests=str(result.total_cases),
        failures=str(result.failed_cases),
        errors="0",
        skipped="0",
    )
    for case_result in result.cases:
        case = SubElement(
            suite,
            "testcase",
            classname=f"flashpilot.fuzz.{case_result.scenario.value}",
            name=f"iteration-{case_result.iteration:04d}",
        )
        if not case_result.passed:
            failure = SubElement(
                case,
                "failure",
                message="checkpoint fault did not fail closed as expected",
                type="fuzz-qualification",
            )
            failure.text = (
                f"expected={case_result.expected_rejection_reason}; "
                f"observed={[reason.value for reason in case_result.observed_rejection_reasons]}; "
                f"premature_acceptances={case_result.premature_acceptances}; "
                f"final_valid={case_result.final_valid}"
            )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(suite, encoding="unicode", short_empty_elements=True)
        + "\n"
    )


def render_fuzz_job_summary(result: PartialWriteFuzzResult) -> str:
    return (
        "# FlashPilot partial-write fuzz qualification\n\n"
        f"**Verdict: {result.verdict}**\n\n"
        f"{result.passed_cases}/{result.total_cases} deterministic cases passed; "
        f"premature acceptances: {result.premature_acceptances}.\n\n"
        "This is commit-integrity evidence, not a Recovery Gate verdict.\n"
    )
