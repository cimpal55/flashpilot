"""Fixed four-case checkpoint conversion and equivalence qualification."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import torch
from pydantic import ValidationError

from flashpilot.checkpoints.integrity import directory_content_fingerprint
from flashpilot.conversion.artifacts import (
    ConversionArtifactCommit,
    ConversionArtifactError,
    ValidatedConversionArtifact,
    commit_conversion_artifact,
    json_payload_writer,
    safe_load_torch_payload,
    torch_payload_writer,
    validate_conversion_artifact,
)
from flashpilot.conversion.models import (
    ConversionCaseResult,
    ConversionCheck,
    ConversionComparisonPolicy,
    ConversionKind,
    ConversionQualificationResult,
    ConversionRepresentation,
    UpgradedTrainingStateV2,
    VersionResumeEvidenceV1,
)
from flashpilot.conversion.reporting import (
    render_case_junit,
    render_case_markdown,
    render_job_summary,
    render_qualification_junit,
    render_qualification_markdown,
)
from flashpilot.conversion.workload import (
    MERGE_ATOL,
    MERGE_RTOL,
    VERSION_CHECKPOINT_STEP,
    build_full_model_state,
    canonical_legacy_digest,
    canonical_upgraded_digest,
    evaluate_full_state,
    evaluate_merged_state,
    evaluate_peft_state,
    exact_tensor_mapping_equal,
    full_effective_state,
    legacy_training_checkpoint,
    load_full_payload,
    load_json_index,
    maximum_absolute_difference,
    merge_peft_state,
    reconstruct_full_state,
    shard_full_state,
    split_full_to_peft,
    validate_legacy_training_checkpoint,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact


class ConversionQualificationError(RuntimeError):
    """Conversion qualification cannot produce trustworthy evidence."""


_FORMATS = {
    ConversionRepresentation.FULL_MODEL: "full-model-v1",
    ConversionRepresentation.PEFT: "peft-v1",
    ConversionRepresentation.MERGED_MODEL: "merged-model-v1",
    ConversionRepresentation.SHARDED: "sharded-v1",
    ConversionRepresentation.CONSOLIDATED: "consolidated-v1",
    ConversionRepresentation.LEGACY_V1: "training-checkpoint-v1",
    ConversionRepresentation.UPGRADED_V2: "training-checkpoint-v2",
}


def _check(
    check_id: str,
    passed: bool,
    summary: str,
    expected: str,
    actual: str,
) -> ConversionCheck:
    return ConversionCheck(
        check_id=check_id,
        status="pass" if passed else "fail",
        summary=summary,
        expected=expected,
        actual=actual,
    )


def _commit(
    *,
    run_root: Path,
    kind: ConversionKind,
    role: str,
    representation: ConversionRepresentation,
    source_sha256: str | None,
    payload_writers,
    global_step: int | None = None,
) -> ConversionArtifactCommit:
    return commit_conversion_artifact(
        run_root=run_root,
        parent_relative=f"cases/{kind.value}",
        role=role,
        conversion_kind=kind,
        representation=representation,
        format_version=_FORMATS[representation],
        profile="ci" if kind is ConversionKind.VERSION_UPGRADE_RESUME else "conversion",
        global_step=global_step,
        source_artifact_sha256=source_sha256,
        payload_writers=payload_writers,
    )


def _build_full_to_peft(run_root: Path) -> tuple[Path, Path]:
    kind = ConversionKind.FULL_TO_PEFT
    source = _commit(
        run_root=run_root,
        kind=kind,
        role="source",
        representation=ConversionRepresentation.FULL_MODEL,
        source_sha256=None,
        payload_writers={"full.pt": torch_payload_writer(build_full_model_state())},
    )
    full = load_full_payload(validate_conversion_artifact(source.path), "full.pt")
    base, adapter = split_full_to_peft(full)
    candidate = _commit(
        run_root=run_root,
        kind=kind,
        role="candidate",
        representation=ConversionRepresentation.PEFT,
        source_sha256=source.fingerprint.sha256,
        payload_writers={
            "adapter.pt": torch_payload_writer(adapter),
            "base.pt": torch_payload_writer(base),
        },
    )
    return source.path, candidate.path


def _build_peft_to_merged(run_root: Path) -> tuple[Path, Path]:
    kind = ConversionKind.PEFT_TO_MERGED
    full = build_full_model_state()
    base, adapter = split_full_to_peft(full)
    source = _commit(
        run_root=run_root,
        kind=kind,
        role="source",
        representation=ConversionRepresentation.PEFT,
        source_sha256=None,
        payload_writers={
            "adapter.pt": torch_payload_writer(adapter),
            "base.pt": torch_payload_writer(base),
        },
    )
    merged = merge_peft_state(base, adapter)
    candidate = _commit(
        run_root=run_root,
        kind=kind,
        role="candidate",
        representation=ConversionRepresentation.MERGED_MODEL,
        source_sha256=source.fingerprint.sha256,
        payload_writers={"merged.pt": torch_payload_writer(merged)},
    )
    return source.path, candidate.path


def _build_sharded_to_consolidated(run_root: Path) -> tuple[Path, Path]:
    kind = ConversionKind.SHARDED_TO_CONSOLIDATED
    full = full_effective_state(build_full_model_state())
    shard_zero, shard_one = shard_full_state(full)
    index = {key: "shard-000.pt" if key in shard_zero else "shard-001.pt" for key in sorted(full)}
    source = _commit(
        run_root=run_root,
        kind=kind,
        role="source",
        representation=ConversionRepresentation.SHARDED,
        source_sha256=None,
        payload_writers={
            "index.json": json_payload_writer(index),
            "shard-000.pt": torch_payload_writer(shard_zero),
            "shard-001.pt": torch_payload_writer(shard_one),
        },
    )
    candidate = _commit(
        run_root=run_root,
        kind=kind,
        role="candidate",
        representation=ConversionRepresentation.CONSOLIDATED,
        source_sha256=source.fingerprint.sha256,
        payload_writers={"model.pt": torch_payload_writer(full)},
    )
    return source.path, candidate.path


def _build_version_upgrade_resume(run_root: Path) -> tuple[Path, Path]:
    kind = ConversionKind.VERSION_UPGRADE_RESUME
    legacy = legacy_training_checkpoint()
    source = _commit(
        run_root=run_root,
        kind=kind,
        role="source",
        representation=ConversionRepresentation.LEGACY_V1,
        source_sha256=None,
        global_step=VERSION_CHECKPOINT_STEP,
        payload_writers={"checkpoint.pt": torch_payload_writer(legacy)},
    )
    loaded = validate_legacy_training_checkpoint(
        safe_load_torch_payload(validate_conversion_artifact(source.path), "checkpoint.pt")
    )
    state = UpgradedTrainingStateV2(
        global_step=int(loaded["completed_step"]),
        loss_history=tuple(float(loss) for loss in loaded["losses"]),
    )
    candidate = _commit(
        run_root=run_root,
        kind=kind,
        role="candidate",
        representation=ConversionRepresentation.UPGRADED_V2,
        source_sha256=source.fingerprint.sha256,
        global_step=state.global_step,
        payload_writers={
            "model.pt": torch_payload_writer(loaded["model_state"]),
            "optimizer.pt": torch_payload_writer(loaded["optimizer_state"]),
            "rng.pt": torch_payload_writer(loaded["random_state"]),
            "scheduler.pt": torch_payload_writer(loaded["scheduler_state"]),
            "state.json": json_payload_writer(state.model_dump(mode="json")),
        },
    )
    return source.path, candidate.path


def build_conversion_artifacts(
    *,
    run_root: Path,
    kind: ConversionKind,
) -> tuple[Path, Path]:
    """Build one fixed source/candidate pair for qualification tests and demos."""

    builders = {
        ConversionKind.FULL_TO_PEFT: _build_full_to_peft,
        ConversionKind.PEFT_TO_MERGED: _build_peft_to_merged,
        ConversionKind.SHARDED_TO_CONSOLIDATED: _build_sharded_to_consolidated,
        ConversionKind.VERSION_UPGRADE_RESUME: _build_version_upgrade_resume,
    }
    return builders[kind](run_root)


def _load_peft(artifact: ValidatedConversionArtifact) -> tuple[dict, dict]:
    return (
        load_full_payload(artifact, "base.pt"),
        load_full_payload(artifact, "adapter.pt"),
    )


def _load_sharded(artifact: ValidatedConversionArtifact) -> dict[str, torch.Tensor]:
    index = load_json_index(artifact.path / "index.json")
    shards = {name: load_full_payload(artifact, name) for name in {"shard-000.pt", "shard-001.pt"}}
    expected_by_shard = {
        shard: {key for key, selected in index.items() if selected == shard} for shard in shards
    }
    if any(set(shards[shard]) != expected_by_shard[shard] for shard in shards):
        raise ConversionArtifactError("shard index and shard contents disagree")
    consolidated = {}
    for key, shard in sorted(index.items()):
        if key in consolidated:
            raise ConversionArtifactError("shard index contains duplicate parameter keys")
        consolidated[key] = shards[shard][key]
    return consolidated


def _model_checks(
    source: ValidatedConversionArtifact,
    candidate: ValidatedConversionArtifact,
) -> tuple[list[ConversionCheck], ConversionComparisonPolicy, float]:
    kind = source.manifest.conversion_kind
    if kind is ConversionKind.FULL_TO_PEFT:
        source_state = load_full_payload(source, "full.pt")
        base, adapter = _load_peft(candidate)
        source_dense = full_effective_state(source_state)
        candidate_dense = merge_peft_state(base, adapter)
        source_output = evaluate_merged_state(source_dense)
        candidate_output = evaluate_peft_state(base, adapter)
        state_equal = set(source_dense) == set(candidate_dense) and all(
            torch.allclose(
                source_dense[key],
                candidate_dense[key],
                atol=MERGE_ATOL,
                rtol=MERGE_RTOL,
            )
            for key in source_dense
        )
        output_equal = torch.allclose(
            source_output,
            candidate_output,
            atol=MERGE_ATOL,
            rtol=MERGE_RTOL,
        )
        difference = maximum_absolute_difference(source_output, candidate_output)
        checks = [
            _check(
                "equivalence.parameters",
                state_equal,
                "Full and reconstructed PEFT parameters satisfy the fixed tolerance.",
                f"atol={MERGE_ATOL}, rtol={MERGE_RTOL}",
                "within tolerance" if state_equal else "outside tolerance",
            ),
            _check(
                "equivalence.outputs",
                output_equal,
                "Full and PEFT outputs satisfy the fixed tolerance.",
                f"atol={MERGE_ATOL}, rtol={MERGE_RTOL}",
                f"max_abs_diff={difference}",
            ),
        ]
        return (
            checks,
            ConversionComparisonPolicy(
                mode="tolerance-bounded",
                atol=MERGE_ATOL,
                rtol=MERGE_RTOL,
            ),
            difference,
        )
    if kind is ConversionKind.PEFT_TO_MERGED:
        base, adapter = _load_peft(source)
        merged = load_full_payload(candidate, "merged.pt")
        expected_merged = merge_peft_state(base, adapter)
        state_equal = exact_tensor_mapping_equal(expected_merged, merged)
        source_output = evaluate_full_state(reconstruct_full_state(base, adapter))
        candidate_output = evaluate_merged_state(merged)
        difference = maximum_absolute_difference(source_output, candidate_output)
        output_equal = torch.allclose(
            source_output,
            candidate_output,
            atol=MERGE_ATOL,
            rtol=MERGE_RTOL,
        )
        checks = [
            _check(
                "conversion.merged-weight",
                state_equal,
                "Merged weight equals the deterministic PEFT merge.",
                "exact merged parameter equality",
                "exact" if state_equal else "different",
            ),
            _check(
                "equivalence.outputs",
                output_equal,
                "PEFT and merged inference outputs satisfy the fixed tolerance.",
                f"atol={MERGE_ATOL}, rtol={MERGE_RTOL}",
                f"max_abs_diff={difference}",
            ),
        ]
        return (
            checks,
            ConversionComparisonPolicy(
                mode="tolerance-bounded",
                atol=MERGE_ATOL,
                rtol=MERGE_RTOL,
            ),
            difference,
        )
    if kind is ConversionKind.SHARDED_TO_CONSOLIDATED:
        source_state = _load_sharded(source)
        candidate_state = load_full_payload(candidate, "model.pt")
        source_output = evaluate_merged_state(source_state)
        candidate_output = evaluate_merged_state(candidate_state)
        state_equal = exact_tensor_mapping_equal(source_state, candidate_state)
        output_equal = torch.equal(source_output, candidate_output)
        difference = maximum_absolute_difference(source_output, candidate_output)
        checks = [
            _check(
                "equivalence.parameters",
                state_equal,
                "Sharded and consolidated parameters are exactly equal.",
                "exact tensor equality",
                "exact" if state_equal else "different",
            ),
            _check(
                "equivalence.outputs",
                output_equal,
                "Sharded and consolidated outputs are exactly equal.",
                "exact tensor equality",
                "exact" if output_equal else f"max_abs_diff={difference}",
            ),
        ]
        return checks, ConversionComparisonPolicy(mode="exact", atol=0.0, rtol=0.0), difference
    raise ConversionQualificationError("model checks called for a training-version conversion")


def _version_checks(
    source: ValidatedConversionArtifact,
    candidate: ValidatedConversionArtifact,
    output_dir: Path,
) -> tuple[list[ConversionCheck], ConversionComparisonPolicy, float, int]:
    legacy = validate_legacy_training_checkpoint(safe_load_torch_payload(source, "checkpoint.pt"))
    legacy_digest = canonical_legacy_digest(legacy)
    upgraded_digest = canonical_upgraded_digest(candidate)
    state_equal = legacy_digest == upgraded_digest
    environment = os.environ.copy()
    for key in tuple(environment):
        normalized = key.upper()
        if normalized == "OPENAI_API_KEY" or normalized.endswith("_API_KEY"):
            environment.pop(key)
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "PYTHONHASHSEED": "20260720",
            "PYTHONUNBUFFERED": "1",
        }
    )
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "flashpilot.conversion.worker",
            "--artifact",
            str(candidate.path),
            "--output-root",
            str(output_dir),
        ],
        cwd=output_dir,
        env=environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
        timeout=120,
        check=False,
    )
    write_text_artifact(
        run_root=output_dir,
        relative_path="version-resume.stdout.log",
        text=process.stdout,
    )
    write_text_artifact(
        run_root=output_dir,
        relative_path="version-resume.stderr.log",
        text=process.stderr,
    )
    if process.returncode != 0:
        raise ConversionQualificationError(
            f"version resume worker failed with exit code {process.returncode}"
        )
    try:
        resumed = VersionResumeEvidenceV1.model_validate_json(
            (output_dir / "version-resume.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValidationError, ValueError) as error:
        raise ConversionQualificationError("version resume worker evidence is invalid") from error
    checks = [
        _check(
            "equivalence.converted-state",
            state_equal,
            "Legacy and upgraded pre-resume training state digests are exact.",
            legacy_digest,
            upgraded_digest,
        ),
        _check(
            "continuation.global-step",
            resumed.resumed_global_step == resumed.control_global_step,
            "Upgraded resume reaches the control global step.",
            str(resumed.control_global_step),
            str(resumed.resumed_global_step),
        ),
        _check(
            "continuation.loss-history",
            resumed.resumed_loss_history == resumed.control_loss_history,
            "Upgraded resume loss history exactly matches control.",
            "exact control history",
            (
                "exact"
                if resumed.resumed_loss_history == resumed.control_loss_history
                else "different"
            ),
        ),
        _check(
            "continuation.trainable-state",
            resumed.resumed_trainable_sha256 == resumed.control_trainable_sha256,
            "Upgraded resume trainable state exactly matches control.",
            resumed.control_trainable_sha256,
            resumed.resumed_trainable_sha256,
        ),
        _check(
            "continuation.evaluation",
            resumed.resumed_evaluation_sha256 == resumed.control_evaluation_sha256,
            "Upgraded resume evaluation exactly matches control.",
            resumed.control_evaluation_sha256,
            resumed.resumed_evaluation_sha256,
        ),
        _check(
            "continuation.optimizer",
            resumed.resumed_optimizer_sha256 == resumed.control_optimizer_sha256,
            "Upgraded resume optimizer exactly matches control.",
            resumed.control_optimizer_sha256,
            resumed.resumed_optimizer_sha256,
        ),
        _check(
            "continuation.scheduler",
            resumed.resumed_scheduler_sha256 == resumed.control_scheduler_sha256,
            "Upgraded resume scheduler exactly matches control.",
            resumed.control_scheduler_sha256,
            resumed.resumed_scheduler_sha256,
        ),
        _check(
            "process.distinct-resume",
            resumed.worker_pid != os.getpid(),
            "Version-upgrade continuation ran in a distinct process.",
            f"PID different from {os.getpid()}",
            str(resumed.worker_pid),
        ),
    ]
    difference = (
        max(
            abs(left - right)
            for left, right in zip(
                resumed.control_loss_history,
                resumed.resumed_loss_history,
                strict=True,
            )
        )
        if len(resumed.control_loss_history) == len(resumed.resumed_loss_history)
        else 1.0
    )
    return (
        checks,
        ConversionComparisonPolicy(mode="exact-training-resume", atol=0.0, rtol=0.0),
        difference,
        resumed.worker_pid,
    )


def _prepare_output(output_dir: Path, source: Path, candidate: Path) -> Path:
    lexical = output_dir.absolute()
    for input_path in (source.resolve(strict=True), candidate.resolve(strict=True)):
        try:
            resolved_output = lexical.resolve(strict=False)
        except OSError as error:
            raise ConversionQualificationError("comparison output cannot be resolved") from error
        if resolved_output == input_path or resolved_output.is_relative_to(input_path):
            raise ConversionQualificationError("comparison output cannot overlap an input artifact")
    if lexical.exists() and (not lexical.is_dir() or any(lexical.iterdir())):
        raise ConversionQualificationError("comparison output must be a new or empty directory")
    lexical.mkdir(parents=True, exist_ok=True)
    return lexical.resolve(strict=True)


def compare_conversion_artifacts(
    *,
    source_path: Path,
    candidate_path: Path,
    output_dir: Path,
) -> ConversionCaseResult:
    """Compare one fixed conversion pair and persist deterministic evidence."""

    source = validate_conversion_artifact(source_path)
    candidate = validate_conversion_artifact(candidate_path)
    if source.manifest.role != "source" or candidate.manifest.role != "candidate":
        raise ConversionQualificationError("conversion pair roles are invalid")
    if source.manifest.conversion_kind is not candidate.manifest.conversion_kind:
        raise ConversionQualificationError("conversion pair kinds do not match")
    output = _prepare_output(output_dir, source.path, candidate.path)
    kind = source.manifest.conversion_kind
    provenance_matches = candidate.manifest.source_artifact_sha256 == source.fingerprint.sha256
    checks = [
        _check(
            "artifact.source-valid",
            True,
            "Source artifact passed closed-inventory validation.",
            "valid",
            "valid",
        ),
        _check(
            "artifact.candidate-valid",
            True,
            "Candidate artifact passed closed-inventory validation.",
            "valid",
            "valid",
        ),
        _check(
            "provenance.source-sha256",
            provenance_matches,
            "Candidate provenance binds the exact source directory.",
            source.fingerprint.sha256,
            candidate.manifest.source_artifact_sha256 or "missing",
        ),
    ]
    if kind is ConversionKind.VERSION_UPGRADE_RESUME:
        semantic_checks, policy, difference, resume_worker_pid = _version_checks(
            source,
            candidate,
            output,
        )
    else:
        semantic_checks, policy, difference = _model_checks(source, candidate)
        resume_worker_pid = None
    checks.extend(semantic_checks)
    source_after = directory_content_fingerprint(source.path)
    source_unmodified = source_after.sha256 == source.fingerprint.sha256
    checks.append(
        _check(
            "immutability.source",
            source_unmodified,
            "Comparison did not mutate the source artifact.",
            source.fingerprint.sha256,
            source_after.sha256,
        )
    )
    candidate_after = directory_content_fingerprint(candidate.path)
    candidate_unmodified = candidate_after.sha256 == candidate.fingerprint.sha256
    checks.append(
        _check(
            "immutability.candidate",
            candidate_unmodified,
            "Comparison did not mutate the candidate artifact.",
            candidate.fingerprint.sha256,
            candidate_after.sha256,
        )
    )
    failed = tuple(check.check_id for check in checks if check.status == "fail")
    result = ConversionCaseResult(
        conversion_kind=kind,
        source_representation=source.manifest.representation,
        candidate_representation=candidate.manifest.representation,
        source_artifact_sha256=source.fingerprint.sha256,
        source_artifact_sha256_after=source_after.sha256,
        candidate_artifact_sha256=candidate.fingerprint.sha256,
        candidate_artifact_sha256_after=candidate_after.sha256,
        comparison_policy=policy,
        checks=tuple(checks),
        failed_check_ids=failed,
        passed=not failed,
        maximum_absolute_difference=difference,
        source_unmodified=source_unmodified,
        candidate_unmodified=candidate_unmodified,
        comparison_process_pid=os.getpid(),
        resume_worker_pid=resume_worker_pid,
        resume_in_distinct_process=(
            resume_worker_pid is not None and resume_worker_pid != os.getpid()
        ),
    )
    write_json_artifact(run_root=output, relative_path="comparison.json", value=result)
    write_text_artifact(
        run_root=output,
        relative_path="report.md",
        text=render_case_markdown(result),
    )
    write_text_artifact(
        run_root=output,
        relative_path="junit.xml",
        text=render_case_junit(result),
    )
    return result


def run_conversion_qualification(*, run_root: Path) -> ConversionQualificationResult:
    """Build and compare all four plan-defined conversion cases."""

    if run_root.exists() and (not run_root.is_dir() or any(run_root.iterdir())):
        raise ConversionQualificationError(
            "conversion qualification requires a new or empty run directory"
        )
    run_root.mkdir(parents=True, exist_ok=True)
    results = []
    try:
        for kind in ConversionKind:
            source, candidate = build_conversion_artifacts(run_root=run_root, kind=kind)
            results.append(
                compare_conversion_artifacts(
                    source_path=source,
                    candidate_path=candidate,
                    output_dir=run_root / "cases" / kind.value / "evidence",
                )
            )
    except (ConversionArtifactError, OSError, RuntimeError, ValueError) as error:
        raise ConversionQualificationError("conversion qualification failed closed") from error
    failed = tuple(case.conversion_kind for case in results if not case.passed)
    result = ConversionQualificationResult(
        cases=tuple(results),
        failed_cases=failed,
        passed=not failed,
        verdict="PASS" if not failed else "FAILED",
        limitations=(
            "Conversion qualification uses fixed local CPU fixtures, not arbitrary repositories.",
            "PEFT extraction and merge use an explicit float64 tolerance; other cases are exact.",
            "No crash Recovery Gate ran, so this result cannot claim verified recovery.",
            "Artifact byte counts and storage savings are intentionally not reported.",
        ),
    )
    write_json_artifact(run_root=run_root, relative_path=result.result_path, value=result)
    write_text_artifact(
        run_root=run_root,
        relative_path=result.report_path,
        text=render_qualification_markdown(result),
    )
    write_text_artifact(
        run_root=run_root,
        relative_path=result.junit_path,
        text=render_qualification_junit(result),
    )
    write_text_artifact(
        run_root=run_root,
        relative_path=result.job_summary_path,
        text=render_job_summary(result),
    )
    return result


def load_conversion_result(path: Path) -> ConversionQualificationResult:
    try:
        return ConversionQualificationResult.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise ConversionQualificationError("conversion qualification result is invalid") from error
