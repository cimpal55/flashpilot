"""Parent-owned orchestration for one targeted rank termination."""

from __future__ import annotations

import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from flashpilot.multirank.models import (
    MultiRankAdapter,
    MultiRankFailureEvent,
    MultiRankFaultProcessEvidence,
    MultiRankFaultReadyEvidence,
    MultiRankFramework,
    MultiRankImplementation,
    MultiRankPeerFailureEvidence,
    MultiRankStrategy,
)
from flashpilot.orchestration.artifacts import write_json_artifact, write_text_artifact
from flashpilot.security.paths import PathSandbox


class MultiRankFailureError(RuntimeError):
    """The target rank failure did not produce trustworthy group evidence."""


def _load_ready(root: Path, relative: str) -> MultiRankFaultReadyEvidence:
    try:
        path = PathSandbox.create(root).resolve_relative(relative, must_exist=True)
        return MultiRankFaultReadyEvidence.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise MultiRankFailureError(f"invalid rank-ready evidence: {relative}") from error


def _load_peer_failure(root: Path, relative: str) -> MultiRankPeerFailureEvidence:
    try:
        path = PathSandbox.create(root).resolve_relative(relative, must_exist=True)
        return MultiRankPeerFailureEvidence.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        raise MultiRankFailureError(f"invalid peer-failure evidence: {relative}") from error


def run_targeted_rank_termination(
    *,
    run_root: Path,
    commands: tuple[tuple[str, ...], tuple[str, ...]],
    environments: tuple[dict[str, str], dict[str, str]],
    ready_paths: tuple[str, str],
    peer_failure_paths: tuple[str, str],
    log_stem: str,
    framework: MultiRankFramework,
    adapter: MultiRankAdapter,
    strategy: MultiRankStrategy,
    implementation: MultiRankImplementation,
    zero_stage: int | None,
    checkpoint_path: str,
    checkpoint_id: str,
    checkpoint_tag: str | None,
    checkpoint_step: int,
    target_rank: int,
    timeout_seconds: float,
) -> MultiRankFailureEvent:
    """Kill one ready rank and require typed peer collective-failure evidence."""

    if target_rank not in (0, 1):
        raise ValueError("target rank must be 0 or 1")
    if timeout_seconds <= 0:
        raise ValueError("fault timeout must be positive")
    root = PathSandbox.create(run_root).root
    processes: list[subprocess.Popen[str]] = []
    starts: list[datetime] = []
    captured = False

    def capture() -> None:
        nonlocal captured
        if captured:
            return
        for rank, process in enumerate(processes):
            stdout, stderr = process.communicate(timeout=10)
            write_text_artifact(
                run_root=root,
                relative_path=f"logs/{log_stem}.rank-{rank:03d}.stdout.log",
                text=stdout,
            )
            write_text_artifact(
                run_root=root,
                relative_path=f"logs/{log_stem}.rank-{rank:03d}.stderr.log",
                text=stderr,
            )
        captured = True

    try:
        for rank in range(2):
            starts.append(datetime.now(UTC))
            processes.append(
                subprocess.Popen(
                    commands[rank],
                    cwd=root,
                    env=environments[rank],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    shell=False,
                )
            )

        startup_deadline = time.monotonic() + timeout_seconds
        ready: dict[int, MultiRankFaultReadyEvidence] = {}
        while len(ready) != 2 and time.monotonic() < startup_deadline:
            for rank, relative in enumerate(ready_paths):
                if rank not in ready and (root / relative).is_file():
                    ready[rank] = _load_ready(root, relative)
            if any(process.poll() is not None for process in processes):
                break
            time.sleep(0.02)
        if len(ready) != 2:
            raise MultiRankFailureError("rank group did not become ready for termination")
        ordered_ready = tuple(ready[rank] for rank in range(2))
        for rank, evidence in enumerate(ordered_ready):
            if (
                evidence.rank != rank
                or evidence.worker_pid != processes[rank].pid
                or evidence.framework != framework
                or evidence.adapter != adapter
                or evidence.strategy != strategy
                or evidence.implementation != implementation
                or evidence.zero_stage != zero_stage
                or str(evidence.checkpoint_path) != checkpoint_path
                or evidence.checkpoint_id != checkpoint_id
                or evidence.checkpoint_tag != checkpoint_tag
                or evidence.checkpoint_step != checkpoint_step
            ):
                raise MultiRankFailureError("rank-ready identity differs from the launched fault")
        if any(process.poll() is not None for process in processes):
            raise MultiRankFailureError("rank exited before parent-owned fault delivery")
        if any((root / relative).exists() for relative in peer_failure_paths):
            raise MultiRankFailureError("peer-failure evidence predates parent fault delivery")

        delivered_at = datetime.now(UTC)
        processes[target_rank].kill()
        peer_rank = 1 - target_rank
        peer_failure: MultiRankPeerFailureEvidence | None = None
        propagation_deadline = time.monotonic() + min(timeout_seconds, 30.0)
        while time.monotonic() < propagation_deadline:
            relative = peer_failure_paths[peer_rank]
            if (root / relative).is_file():
                peer_failure = _load_peer_failure(root, relative)
                break
            if processes[peer_rank].poll() is not None:
                break
            time.sleep(0.02)
        if peer_failure is None:
            raise MultiRankFailureError(
                "surviving rank did not persist collective-failure evidence"
            )
        if (root / peer_failure_paths[target_rank]).exists():
            raise MultiRankFailureError("terminated rank emitted contradictory peer evidence")
        if (
            peer_failure.framework != framework
            or peer_failure.target_rank != target_rank
            or peer_failure.observer_rank != peer_rank
            or peer_failure.observer_pid != processes[peer_rank].pid
            or peer_failure.checkpoint_step != checkpoint_step
        ):
            raise MultiRankFailureError("peer-failure identity differs from the launched fault")

        cleanup_forced = [False, False]
        cleanup_deadline = time.monotonic() + min(timeout_seconds, 10.0)
        while (
            any(process.poll() is None for process in processes)
            and time.monotonic() < cleanup_deadline
        ):
            time.sleep(0.02)
        for rank, process in enumerate(processes):
            if process.poll() is None:
                process.kill()
                cleanup_forced[rank] = True
        for process in processes:
            process.wait(timeout=10)
        completed_at = datetime.now(UTC)
        capture()
        if processes[target_rank].returncode == 0 or processes[peer_rank].returncode == 0:
            raise MultiRankFailureError("failed rank group reported an unexpected clean exit")

        process_evidence = tuple(
            MultiRankFaultProcessEvidence(
                rank=rank,
                worker_pid=process.pid,
                started_at=starts[rank],
                ready_at=ordered_ready[rank].ready_at,
                completed_at=completed_at,
                exit_code=process.returncode,
                externally_terminated=rank == target_rank,
                collective_failure_observed=rank == peer_rank,
                cleanup_forced=cleanup_forced[rank],
            )
            for rank, process in enumerate(processes)
        )
        event = MultiRankFailureEvent(
            framework=framework,
            adapter=adapter,
            strategy=strategy,
            implementation=implementation,
            zero_stage=zero_stage,
            target_rank=target_rank,
            checkpoint_path=checkpoint_path,
            checkpoint_id=checkpoint_id,
            checkpoint_tag=checkpoint_tag,
            checkpoint_step=checkpoint_step,
            ready_evidence=ordered_ready,
            peer_failure=peer_failure,
            rank_processes=process_evidence,
            delivered_at=delivered_at,
            emitted_at=datetime.now(UTC),
        )
        write_json_artifact(run_root=root, relative_path="failure-event.json", value=event)
        return event
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
        for process in processes:
            if process.poll() is None:
                process.wait(timeout=10)
        if processes and not captured:
            capture()
