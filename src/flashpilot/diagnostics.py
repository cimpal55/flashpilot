"""Offline environment qualification for the installed judge path."""

from __future__ import annotations

import os
import platform
import sys
import uuid
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal

import torch

from flashpilot.agent.fixture_provider import (
    DEFAULT_CONTRACT_CAPTURE_METADATA,
    DEFAULT_CONTRACT_FIXTURE,
    DEFAULT_FAILURE_CAPTURE_METADATA,
    DEFAULT_FAILURE_FIXTURE,
)

DoctorStatus = Literal["PASS", "FAIL", "INFO", "LIMITATION"]
_REQUIRED_DISTRIBUTIONS = ("numpy", "openai", "pydantic", "rich", "torch", "typer")


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    status: DoctorStatus
    detail: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class DoctorResult:
    checks: tuple[DoctorCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.status != "FAIL" for check in self.checks if check.required)


def _dependency_check() -> DoctorCheck:
    installed: list[str] = []
    missing: list[str] = []
    for distribution in _REQUIRED_DISTRIBUTIONS:
        try:
            installed.append(f"{distribution}={version(distribution)}")
        except PackageNotFoundError:
            missing.append(distribution)
    if missing:
        return DoctorCheck(
            name="Required dependencies",
            status="FAIL",
            detail=f"Missing: {', '.join(missing)}",
        )
    return DoctorCheck(
        name="Required dependencies",
        status="PASS",
        detail=", ".join(installed),
    )


def _fixture_check() -> DoctorCheck:
    paths = (
        DEFAULT_CONTRACT_FIXTURE,
        DEFAULT_CONTRACT_CAPTURE_METADATA,
        DEFAULT_FAILURE_FIXTURE,
        DEFAULT_FAILURE_CAPTURE_METADATA,
    )
    missing = tuple(path for path in paths if not path.is_file())
    return DoctorCheck(
        name="Captured-response fixtures",
        status="FAIL" if missing else "PASS",
        detail=(
            f"Missing: {', '.join(str(path) for path in missing)}"
            if missing
            else f"Available at {DEFAULT_FAILURE_FIXTURE.parent}"
        ),
    )


def _writable_output_check(output_dir: Path) -> DoctorCheck:
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        probe = output_dir / f".flashpilot-doctor-{uuid.uuid4().hex}"
        try:
            with probe.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write("flashpilot doctor write probe\n")
                stream.flush()
                os.fsync(stream.fileno())
        finally:
            if probe.exists():
                probe.unlink()
    except OSError as error:
        return DoctorCheck(
            name="Writable output location",
            status="FAIL",
            detail=f"{output_dir.resolve()}: {type(error).__name__}: {error}",
        )
    return DoctorCheck(
        name="Writable output location",
        status="PASS",
        detail=str(output_dir.resolve()),
    )


def run_doctor(*, output_dir: Path) -> DoctorResult:
    """Check the offline CPU judge prerequisites without exposing secrets."""

    python_ok = sys.version_info >= (3, 11)
    try:
        cpu_device = torch.ones(1, device="cpu").device.type
        cpu_ok = cpu_device == "cpu"
        cpu_detail = f"Torch CPU tensor execution available ({torch.get_num_threads()} threads)"
    except RuntimeError as error:
        cpu_ok = False
        cpu_detail = f"Torch CPU execution failed: {error}"
    api_key_present = bool(os.environ.get("OPENAI_API_KEY"))
    if os.name == "nt":
        directory_sync = DoctorCheck(
            name="Directory fsync",
            status="LIMITATION",
            detail=(
                "Windows: Python does not expose directory fsync; payload and metadata file "
                "fsync plus atomic directory rename remain enforced."
            ),
            required=False,
        )
    else:
        directory_sync = DoctorCheck(
            name="Directory fsync",
            status="PASS",
            detail="Supported POSIX directory fsync path is active.",
        )
    return DoctorResult(
        checks=(
            DoctorCheck(
                name="Python version",
                status="PASS" if python_ok else "FAIL",
                detail=(
                    f"{platform.python_version()} (package requires >=3.11; verified release "
                    "environment: Python 3.12.13)"
                ),
            ),
            DoctorCheck(
                name="OS / platform",
                status="INFO",
                detail=platform.platform(),
                required=False,
            ),
            DoctorCheck(
                name="CPU execution",
                status="PASS" if cpu_ok else "FAIL",
                detail=cpu_detail,
            ),
            _dependency_check(),
            _fixture_check(),
            _writable_output_check(output_dir),
            DoctorCheck(
                name="OPENAI_API_KEY",
                status="INFO",
                detail=(
                    "Present (value hidden; not used by fixture demo)"
                    if api_key_present
                    else "Not present (not required by fixture demo)"
                ),
                required=False,
            ),
            directory_sync,
        )
    )
