"""Uninterrupted deterministic control-run implementation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flashpilot.workload.profiles import get_profile
from flashpilot.workload.state import ControlRunSummary
from flashpilot.workload.trainer import (
    build_model,
    configure_determinism,
    create_training_runtime,
    summarize_runtime,
    train_until,
)

__all__ = ["build_model", "configure_determinism", "run_control"]


def run_control(
    profile_name: str = "ci",
    *,
    output_path: Path | None = None,
) -> ControlRunSummary:
    """Run training without interruption and return its observable reference state."""

    profile = get_profile(profile_name)
    runtime = create_training_runtime(profile)
    train_until(runtime, profile.steps)
    summary = summarize_runtime(runtime)
    if output_path is not None:
        summary.write_json(output_path)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the FlashPilot uninterrupted control workload."
    )
    parser.add_argument("--profile", choices=("ci", "demo"), default="ci")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    summary = run_control(arguments.profile, output_path=arguments.output)
    sys.stdout.write(summary.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
