"""The bounded Prompt 5 red-to-green reliability loop."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from flashpilot.agent.fixture_provider import FixtureFailureProvider
from flashpilot.agent.service import analyze_recovery_failure
from flashpilot.checkpoints.integrity import logical_directory_bytes
from flashpilot.checkpoints.strategies import run_safe_full_baseline
from flashpilot.domain.agent import AgentCallMetadata
from flashpilot.domain.manifests import CheckpointManifest
from flashpilot.domain.recovery import SanitizedFailureArtifact
from flashpilot.domain.repair import (
    DirectoryFingerprint,
    RepairLoopResult,
    StorageComparison,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.orchestration.experiment import run_crash_recovery_experiment
from flashpilot.presentation.html_report import render_repair_html
from flashpilot.repair.executor import execute_bounded_repair
from flashpilot.security.paths import PathSandbox
from flashpilot.workload.profiles import get_profile

_REPAIRED_CONFIG_PATH = "strategy/repaired-strategy.json"
_INTENTIONAL_FAILURE_NOTICE = (
    "The failure is intentional and deterministic, but GPT-5.6 does not receive the "
    "injection label. It receives only the sanitized checkpoint manifest, restore behavior, "
    "failed Recovery Gate checks, and trajectory evidence."
)


def fingerprint_directory(path: Path) -> DirectoryFingerprint:
    """Hash relative file names and bytes so any historical mutation is detected."""

    digest = hashlib.sha256()
    file_count = 0
    logical_bytes = 0
    for candidate in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
        if candidate.is_symlink():
            raise ValueError("checkpoint fingerprint refuses symbolic links")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(path).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with candidate.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        file_count += 1
        logical_bytes += candidate.stat().st_size
    if file_count == 0:
        raise ValueError("checkpoint fingerprint requires at least one file")
    return DirectoryFingerprint(
        sha256=digest.hexdigest(),
        file_count=file_count,
        logical_bytes=logical_bytes,
    )


def _storage_comparison(
    *,
    profile_name: str,
    checkpoint_step: int,
    run_root: Path,
    repaired_checkpoint_path: Path,
    repaired_base_bytes: int,
) -> StorageComparison:
    baseline = run_safe_full_baseline(
        profile_name=profile_name,
        run_root=run_root / "measurements" / "safe-full",
        checkpoint_step=checkpoint_step,
    )
    if not baseline.direct_restore_matches_control:
        raise RuntimeError("safe_full measurement failed its unchanged direct-restore baseline")
    repaired_bytes = logical_directory_bytes(repaired_checkpoint_path)
    reduction = baseline.logical_checkpoint_bytes_written - repaired_bytes
    if reduction <= 0:
        raise RuntimeError("repaired recurring checkpoint has no structural byte reduction")
    comparison = StorageComparison(
        profile=profile_name,
        checkpoint_step=checkpoint_step,
        safe_full_bytes=baseline.logical_checkpoint_bytes_written,
        repaired_recurring_bytes=repaired_bytes,
        repaired_one_time_base_bytes=repaired_base_bytes,
        structural_reduction_bytes=reduction,
        structural_reduction_percent=(
            reduction / baseline.logical_checkpoint_bytes_written * 100.0
        ),
        limitations=(
            "The repaired recurring total excludes the immutable base artifact stored once per run.",
            "Logical file bytes are measured; physical NAND writes and write amplification are not.",
            "The safe_full source is the unchanged direct-restore measurement implementation.",
        ),
    )
    write_json_artifact(
        run_root=run_root,
        relative_path="measurements/storage-comparison.json",
        value=comparison,
    )
    return comparison


def render_repair_report(result: RepairLoopResult) -> str:
    """Render a deterministic Markdown report without a GPT narrator."""

    proposed = tuple(action.action for action in result.proposed_analysis.repair_plan.actions)
    config = result.repair_execution.repaired_config
    lines = [
        "# FlashPilot bounded repair report",
        "",
        _INTENTIONAL_FAILURE_NOTICE,
        "",
        f"Final verdict: **{result.final_verdict}**",
        "",
        "Only the deterministic Recovery Gate sets this verdict; the replayed GPT-5.6 response "
        "does not declare recovery.",
        "",
        "## Initial failure",
        "",
        f"- Worker PID: {result.initial_failure.crash.worker_pid}",
        f"- Recovery PID: {result.initial_failure.recovery.worker_pid}",
        f"- Gate passed: {result.initial_failure.gate.passed}",
        f"- Failed checks: {', '.join(result.initial_failure.gate.failed_check_ids)}",
        "",
        "## Bounded repair",
        "",
        "- Provider mode: fixture replay of an accepted secret-free GPT-5.6 structured response",
        f"- Captured response ID: {result.captured_live_failure_metadata.response_id}",
        f"- Proposed actions: {', '.join(proposed)}",
        f"- Applied actions: {', '.join(result.repair_execution.applied_actions)}",
        f"- Unsupported actions: {', '.join(result.plan_validation.unsupported_actions) or 'none'}",
        f"- Rejected actions: {', '.join(result.plan_validation.rejected_actions) or 'none'}",
        f"- Repair attempts: {result.repair_attempt_count}",
        f"- New strategy ID: {config.strategy_id}",
        f"- include_optimizer: {config.include_optimizer}",
        f"- include_scheduler: {config.include_scheduler}",
        f"- include_python_rng: {config.include_python_rng}",
        f"- include_numpy_rng: {config.include_numpy_rng}",
        f"- include_torch_rng: {config.include_torch_rng}",
        f"- restore_before_next_batch: {config.restore_before_next_batch}",
        "",
        "## Repaired verification",
        "",
        f"- Worker PID: {result.repaired_run.crash.worker_pid}",
        f"- Recovery PID: {result.repaired_run.recovery.worker_pid}",
        f"- Gate passed: {result.repaired_run.gate.passed}",
        f"- Exact atol/rtol: {result.repaired_run.gate.comparison_policy.atol}/"
        f"{result.repaired_run.gate.comparison_policy.rtol}",
        f"- Original failed checkpoint unmodified: {result.original_checkpoint_unmodified}",
    ]
    if result.storage_comparison is not None:
        storage = result.storage_comparison
        lines.extend(
            (
                "",
                "## Post-verification storage measurement",
                "",
                f"- safe_full recurring logical bytes: {storage.safe_full_bytes}",
                f"- repaired recurring logical bytes: {storage.repaired_recurring_bytes}",
                f"- one-time frozen base bytes: {storage.repaired_one_time_base_bytes}",
                f"- structural reduction: {storage.structural_reduction_bytes} bytes "
                f"({storage.structural_reduction_percent:.2f}%)",
            )
        )
    else:
        lines.extend(
            (
                "",
                "No storage reduction is reported because repaired recovery did not pass.",
            )
        )
    lines.extend(
        (
            "",
            "## Measurement limitation",
            "",
            "Logical checkpoint bytes were measured in the controlled demo. Physical NAND "
            "writes, write amplification, and SSD lifetime were not measured.",
        )
    )
    return "\n".join(lines) + "\n"


def run_bounded_repair_loop(
    *,
    profile_name: str,
    run_root: Path,
    checkpoint_step: int | None = None,
    timeout_seconds: float = 60.0,
) -> RepairLoopResult:
    """Execute one initial failure, one repair attempt, and one repaired verification."""

    profile = get_profile(profile_name)
    selected_step = checkpoint_step if checkpoint_step is not None else profile.steps // 2
    if run_root.exists() and any(run_root.iterdir()):
        raise FileExistsError("Prompt 5 requires a clean run directory")
    sandbox = PathSandbox.create(run_root.resolve())

    initial_root = sandbox.resolve_relative("initial")
    initial = run_crash_recovery_experiment(
        profile_name=profile.name,
        strategy="missing_training_state",
        run_root=initial_root,
        checkpoint_step=selected_step,
        hard_rollback_limit_steps=0,
        timeout_seconds=timeout_seconds,
    )
    if initial.gate.passed or initial.failure_artifact_path is None:
        raise RuntimeError("the deterministic initial incomplete-checkpoint run did not fail")
    original_checkpoint = initial_root / initial.crash.checkpoint_path
    original_before = fingerprint_directory(original_checkpoint)

    request_path = initial_root / initial.failure_artifact_path
    request = SanitizedFailureArtifact.model_validate_json(request_path.read_text(encoding="utf-8"))
    write_json_artifact(
        run_root=sandbox.root,
        relative_path="agent/request.redacted.json",
        value=request,
    )
    provider = FixtureFailureProvider()
    captured_metadata = provider.captured_live_metadata
    if captured_metadata is None:
        raise RuntimeError("the failure fixture lacks accepted live GPT-5.6 capture metadata")
    proposed_analysis, validation = analyze_recovery_failure(
        provider=provider,
        request=request,
        run_root=sandbox.root,
    )
    write_json_artifact(
        run_root=sandbox.root,
        relative_path="agent/failure/captured-live-metadata.json",
        value=captured_metadata,
    )
    replay_metadata = AgentCallMetadata.model_validate_json(
        sandbox.resolve_relative("agent/failure/metadata.json", must_exist=True).read_text(
            encoding="utf-8"
        )
    )

    execution = execute_bounded_repair(validation=validation, run_root=sandbox.root)
    repaired_root = sandbox.resolve_relative("repaired")
    write_json_artifact(
        run_root=repaired_root,
        relative_path=_REPAIRED_CONFIG_PATH,
        value=execution.repaired_config,
    )
    repaired = run_crash_recovery_experiment(
        profile_name=profile.name,
        strategy="safe_adapter_aware",
        run_root=repaired_root,
        checkpoint_step=selected_step,
        hard_rollback_limit_steps=0,
        strategy_config_path=_REPAIRED_CONFIG_PATH,
        timeout_seconds=timeout_seconds,
    )
    original_after = fingerprint_directory(original_checkpoint)
    unchanged = original_before == original_after
    if not unchanged:
        raise RuntimeError("the original failed checkpoint changed during bounded repair")

    storage: StorageComparison | None = None
    if repaired.gate.passed:
        repaired_manifest = repaired_root / repaired.crash.checkpoint_path / "manifest.json"
        manifest = CheckpointManifest.model_validate_json(
            repaired_manifest.read_text(encoding="utf-8")
        )
        if manifest.base_artifact is None:
            raise RuntimeError("repaired adapter-aware checkpoint lacks its immutable base")
        storage = _storage_comparison(
            profile_name=profile.name,
            checkpoint_step=selected_step,
            run_root=sandbox.root,
            repaired_checkpoint_path=repaired_root / repaired.crash.checkpoint_path,
            repaired_base_bytes=manifest.base_artifact.size_bytes,
        )

    result = RepairLoopResult(
        run_id=sandbox.root.name,
        created_at=datetime.now(UTC),
        profile=profile.name,
        initial_failure=initial,
        captured_live_failure_metadata=captured_metadata,
        replay_call_metadata=replay_metadata,
        proposed_analysis=proposed_analysis,
        plan_validation=validation,
        repair_execution=execution,
        repaired_run=repaired,
        original_checkpoint_before=original_before,
        original_checkpoint_after=original_after,
        original_checkpoint_unmodified=unchanged,
        final_verdict="VERIFIED" if repaired.gate.passed else "FAILED",
        fallback_status=(
            "not_required" if repaired.gate.passed else "documented_not_invoked_after_failure"
        ),
        storage_comparison=storage,
        limitations=(
            "No live API call occurs; the diagnosis is an accepted GPT-5.6 capture replay.",
            "A failed repaired gate stops closed without another diagnosis or repair attempt.",
            "safe_full remains the documented complete-state fallback and is not auto-executed.",
            "Windows directory fsync remains best-effort because Python does not expose it.",
        ),
    )
    write_json_artifact(run_root=sandbox.root, relative_path=result.result_path, value=result)
    persisted_result = RepairLoopResult.model_validate_json(
        sandbox.resolve_relative(result.result_path, must_exist=True).read_text(encoding="utf-8")
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path=result.report_path,
        text=render_repair_report(persisted_result),
    )
    write_text_artifact(
        run_root=sandbox.root,
        relative_path=result.html_report_path,
        text=render_repair_html(persisted_result),
    )
    return result
