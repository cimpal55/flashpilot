"""Deterministic six-case partial-write and incomplete-commit fuzz matrix."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
from pathlib import Path

import torch

from flashpilot.checkpoints.integrity import directory_content_fingerprint, sha256_file
from flashpilot.fuzzing.artifacts import (
    FUZZ_PAYLOAD_PATHS,
    FuzzArtifactError,
    build_fuzz_documents,
    commit_fuzz_artifact,
    serialize_model,
    validate_fuzz_artifact,
)
from flashpilot.fuzzing.models import (
    FuzzCaseResult,
    FuzzRejectionReason,
    FuzzScenario,
    PartialWriteFuzzResult,
)
from flashpilot.fuzzing.reporting import (
    render_fuzz_job_summary,
    render_fuzz_junit,
    render_fuzz_markdown,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.security.paths import PathSandbox

FUZZ_SEED = 20_260_720
MAX_FUZZ_ITERATIONS = 1000

_EXPECTED_REJECTIONS = {
    FuzzScenario.TRUNCATED_PAYLOAD: FuzzRejectionReason.PAYLOAD_SIZE_MISMATCH,
    FuzzScenario.MISSING_SHARD: FuzzRejectionReason.PAYLOAD_MISSING,
    FuzzScenario.STALE_MANIFEST: FuzzRejectionReason.COMPLETION_MISMATCH,
    FuzzScenario.CHECKSUM_MISMATCH: FuzzRejectionReason.CHECKSUM_MANIFEST_MISMATCH,
    FuzzScenario.DUPLICATE_RANK: FuzzRejectionReason.MANIFEST_INVALID,
}


class PartialWriteFuzzError(RuntimeError):
    """The deterministic fuzz qualification could not produce valid evidence."""


def _payloads(iteration: int) -> dict[str, bytes]:
    payloads = {}
    for rank, relative in enumerate(FUZZ_PAYLOAD_PATHS):
        stream = io.BytesIO()
        torch.save(
            {
                "rank": rank,
                "tensor": torch.arange(32, dtype=torch.float64).reshape(4, 8)
                + FUZZ_SEED
                + iteration * 100
                + rank,
            },
            stream,
        )
        payloads[relative] = stream.getvalue()
    return payloads


def _write_json_bytes(path: Path, value: dict[str, object]) -> None:
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode("utf-8"))


def _mutate_negative_case(path: Path, scenario: FuzzScenario) -> None:
    if scenario is FuzzScenario.TRUNCATED_PAYLOAD:
        payload = path / "rank-001.pt"
        content = payload.read_bytes()
        payload.write_bytes(content[: len(content) // 2])
        return
    if scenario is FuzzScenario.MISSING_SHARD:
        (path / "rank-001.pt").unlink()
        return
    if scenario is FuzzScenario.STALE_MANIFEST:
        manifest_path = path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["global_step"] += 1
        _write_json_bytes(manifest_path, manifest)
        return
    if scenario is FuzzScenario.CHECKSUM_MISMATCH:
        checksums_path = path / "checksums.json"
        checksums = json.loads(checksums_path.read_text(encoding="utf-8"))
        checksums["files"][0]["sha256"] = "0" * 64
        _write_json_bytes(checksums_path, checksums)
        return
    if scenario is FuzzScenario.DUPLICATE_RANK:
        manifest_path = path / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["shards"][1]["rank"] = 0
        _write_json_bytes(manifest_path, manifest)
        completion_path = path / "COMPLETE"
        completion = json.loads(completion_path.read_text(encoding="utf-8"))
        completion["manifest_sha256"] = sha256_file(manifest_path)
        _write_json_bytes(completion_path, completion)
        return
    raise ValueError(f"unsupported negative fuzz scenario: {scenario.value}")


def _negative_case(
    *,
    run_root: Path,
    iteration: int,
    scenario: FuzzScenario,
    source: Path,
    source_sha256: str,
) -> FuzzCaseResult:
    relative = f"cases/iteration-{iteration:04d}/{scenario.value}/artifact"
    candidate = PathSandbox.create(run_root).resolve_relative(relative)
    candidate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, candidate)
    _mutate_negative_case(candidate, scenario)
    candidate_before = directory_content_fingerprint(candidate)
    observed = []
    final_valid = False
    try:
        validate_fuzz_artifact(candidate)
        final_valid = True
    except FuzzArtifactError as error:
        observed.append(error.reason)
    candidate_after = directory_content_fingerprint(candidate)
    source_after = directory_content_fingerprint(source)
    expected = _EXPECTED_REJECTIONS[scenario]
    passed = (
        observed == [expected]
        and not final_valid
        and source_sha256 == source_after.sha256
        and candidate_before.sha256 == candidate_after.sha256
    )
    result = FuzzCaseResult(
        iteration=iteration,
        scenario=scenario,
        artifact_path=relative,
        expected_rejection_reason=expected,
        observed_rejection_reasons=tuple(observed),
        validation_attempts=1,
        premature_acceptances=0,
        final_valid=final_valid,
        source_sha256_before=source_sha256,
        source_sha256_after=source_after.sha256,
        source_unmodified=source_sha256 == source_after.sha256,
        candidate_sha256_before_validation=candidate_before.sha256,
        candidate_sha256_after_validation=candidate_after.sha256,
        candidate_unmodified_by_validation=candidate_before.sha256 == candidate_after.sha256,
        passed=passed,
    )
    return result


def _ordered_files(iteration: int, payloads: dict[str, bytes]) -> tuple[tuple[str, bytes], ...]:
    checksums, manifest, completion = build_fuzz_documents(
        iteration=iteration,
        payloads=payloads,
    )
    files = (
        ("COMPLETE", serialize_model(completion)),
        ("rank-001.pt", payloads["rank-001.pt"]),
        ("manifest.json", serialize_model(manifest)),
        ("rank-000.pt", payloads["rank-000.pt"]),
        ("checksums.json", serialize_model(checksums)),
    )
    offset = (iteration - 1) % len(files)
    return files[offset:] + files[:offset]


def _reordered_case(
    *,
    run_root: Path,
    iteration: int,
    payloads: dict[str, bytes],
    source: Path,
    source_sha256: str,
) -> tuple[FuzzCaseResult, tuple[str, ...]]:
    scenario = FuzzScenario.REORDERED_WRITES
    relative = f"cases/iteration-{iteration:04d}/{scenario.value}/artifact"
    candidate = PathSandbox.create(run_root).resolve_relative(relative)
    candidate.mkdir(parents=True)
    observed = []
    premature_acceptances = 0
    final_valid = False
    ordered = _ordered_files(iteration, payloads)
    for index, (name, content) in enumerate(ordered):
        (candidate / name).write_bytes(content)
        try:
            validate_fuzz_artifact(candidate)
            if index != len(ordered) - 1:
                premature_acceptances += 1
            else:
                final_valid = True
        except FuzzArtifactError as error:
            observed.append(error.reason)
    candidate_before = directory_content_fingerprint(candidate)
    try:
        validate_fuzz_artifact(candidate)
    except FuzzArtifactError:
        final_valid = False
    candidate_after = directory_content_fingerprint(candidate)
    source_after = directory_content_fingerprint(source)
    passed = (
        len(observed) == len(ordered) - 1
        and premature_acceptances == 0
        and final_valid
        and source_sha256 == source_after.sha256
        and candidate_before.sha256 == candidate_after.sha256
    )
    result = FuzzCaseResult(
        iteration=iteration,
        scenario=scenario,
        artifact_path=relative,
        expected_rejection_reason=None,
        observed_rejection_reasons=tuple(observed),
        validation_attempts=len(ordered),
        premature_acceptances=premature_acceptances,
        final_valid=final_valid,
        source_sha256_before=source_sha256,
        source_sha256_after=source_after.sha256,
        source_unmodified=source_sha256 == source_after.sha256,
        candidate_sha256_before_validation=candidate_before.sha256,
        candidate_sha256_after_validation=candidate_after.sha256,
        candidate_unmodified_by_validation=candidate_before.sha256 == candidate_after.sha256,
        passed=passed,
    )
    return result, tuple(name for name, _ in ordered)


def _schedule_hash(schedule: list[dict[str, object]]) -> str:
    canonical = json.dumps(schedule, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def run_partial_write_fuzz(
    *,
    run_root: Path,
    iterations: int = 100,
) -> PartialWriteFuzzResult:
    """Run the complete deterministic six-case matrix for every iteration."""

    if not 1 <= iterations <= MAX_FUZZ_ITERATIONS:
        raise ValueError(f"iterations must be between 1 and {MAX_FUZZ_ITERATIONS}")
    if run_root.exists() and (not run_root.is_dir() or any(run_root.iterdir())):
        raise PartialWriteFuzzError("fuzz qualification requires a new or empty run directory")
    run_root.mkdir(parents=True, exist_ok=True)
    cases = []
    schedule: list[dict[str, object]] = []
    try:
        for iteration in range(1, iterations + 1):
            payloads = _payloads(iteration)
            source = commit_fuzz_artifact(
                run_root=run_root,
                iteration=iteration,
                payloads=payloads,
            )
            for scenario in FuzzScenario:
                if scenario is FuzzScenario.REORDERED_WRITES:
                    case, write_order = _reordered_case(
                        run_root=run_root,
                        iteration=iteration,
                        payloads=payloads,
                        source=source.path,
                        source_sha256=source.fingerprint.sha256,
                    )
                else:
                    case = _negative_case(
                        run_root=run_root,
                        iteration=iteration,
                        scenario=scenario,
                        source=source.path,
                        source_sha256=source.fingerprint.sha256,
                    )
                    write_order = ()
                cases.append(case)
                schedule.append(
                    {
                        "iteration": iteration,
                        "scenario": scenario.value,
                        "write_order": write_order,
                    }
                )
    except (FuzzArtifactError, OSError, RuntimeError, ValueError) as error:
        raise PartialWriteFuzzError("partial-write fuzz qualification failed closed") from error
    passed_cases = sum(case.passed for case in cases)
    failed_cases = len(cases) - passed_cases
    premature = sum(case.premature_acceptances for case in cases)
    result = PartialWriteFuzzResult(
        iterations=iterations,
        cases=tuple(cases),
        total_cases=len(cases),
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        premature_acceptances=premature,
        schedule_sha256=_schedule_hash(schedule),
        passed=failed_cases == 0 and premature == 0,
        verdict="PASS" if failed_cases == 0 and premature == 0 else "FAILED",
        limitations=(
            "This deterministic local matrix exercises one fixed two-rank artifact protocol.",
            "It does not test randomized process timing, distributed storage, or network filesystems.",
            "No training crash Recovery Gate ran, so recovery is not verified.",
            "Artifact bytes and storage savings are intentionally not reported.",
        ),
    )
    write_json_artifact(run_root=run_root, relative_path=result.result_path, value=result)
    write_text_artifact(
        run_root=run_root,
        relative_path=result.report_path,
        text=render_fuzz_markdown(result),
    )
    write_text_artifact(
        run_root=run_root,
        relative_path=result.junit_path,
        text=render_fuzz_junit(result),
    )
    write_text_artifact(
        run_root=run_root,
        relative_path=result.job_summary_path,
        text=render_fuzz_job_summary(result),
    )
    from flashpilot.ci.sarif_adapters import render_fuzz_sarif

    write_text_artifact(
        run_root=run_root,
        relative_path=result.sarif_path,
        text=render_fuzz_sarif(result),
    )
    return result
