"""Distinct-process worker for version-upgrade continuation equivalence."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from flashpilot.conversion.artifacts import validate_conversion_artifact
from flashpilot.conversion.models import (
    ConversionKind,
    ConversionRepresentation,
    VersionResumeEvidenceV1,
)
from flashpilot.conversion.workload import resume_upgraded_to_control
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot version-upgrade resume worker")
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser


def main() -> None:
    args = _parser().parse_args()
    artifact = validate_conversion_artifact(args.artifact)
    if (
        artifact.manifest.conversion_kind is not ConversionKind.VERSION_UPGRADE_RESUME
        or artifact.manifest.representation is not ConversionRepresentation.UPGRADED_V2
    ):
        raise ValueError("resume worker accepts only an upgraded-v2 candidate")
    output_root = PathSandbox.create(args.output_root).root
    control, resumed = resume_upgraded_to_control(artifact)
    evidence = VersionResumeEvidenceV1(
        worker_pid=os.getpid(),
        control_global_step=control.final_global_step,
        resumed_global_step=resumed.final_global_step,
        control_loss_history=control.loss_history,
        resumed_loss_history=resumed.loss_history,
        control_trainable_sha256=control.trainable_state.sha256,
        resumed_trainable_sha256=resumed.trainable_state.sha256,
        control_evaluation_sha256=control.evaluation.sha256,
        resumed_evaluation_sha256=resumed.evaluation.sha256,
        control_optimizer_sha256=control.optimizer.sha256,
        resumed_optimizer_sha256=resumed.optimizer.sha256,
        control_scheduler_sha256=control.scheduler.sha256,
        resumed_scheduler_sha256=resumed.scheduler.sha256,
    )
    write_json_artifact(
        run_root=output_root,
        relative_path="version-resume.json",
        value=evidence,
    )


if __name__ == "__main__":
    main()
