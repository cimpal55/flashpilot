from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_PYPROJECT = _REPOSITORY_ROOT / "pyproject.toml"
_UUID_BASETEMP = re.compile(r"flashpilot-pytest-[0-9a-f]{32}")
_PROBE_NODE = "tests/unit/test_pytest_plugin.py::test_report_basetemp_probe"


def _run_probe(*extra_args: str) -> Path:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            str(_PYPROJECT),
            "-q",
            "-s",
            *extra_args,
            _PROBE_NODE,
        ],
        cwd=_REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    match = re.search(r"^FLASHPILOT_BASETEMP=(.+)$", completed.stdout, re.MULTILINE)
    assert match is not None, completed.stdout
    return Path(match.group(1).strip())


def test_report_basetemp_probe(tmp_path_factory) -> None:
    print(f"FLASHPILOT_BASETEMP={tmp_path_factory.getbasetemp()}")


def test_independent_pytest_invocations_use_distinct_uuid_basetemps() -> None:
    first = _run_probe()
    second = _run_probe()

    expected_parent = Path(tempfile.gettempdir()).resolve()
    assert first != second
    assert first.parent == expected_parent
    assert second.parent == expected_parent
    assert _UUID_BASETEMP.fullmatch(first.name)
    assert _UUID_BASETEMP.fullmatch(second.name)
    assert not any(part.startswith("pytest-of-") for part in first.parts)
    assert not any(part.startswith("pytest-of-") for part in second.parts)


def test_explicit_basetemp_is_not_overwritten(tmp_path: Path) -> None:
    explicit = tmp_path / "caller-selected-basetemp"

    observed = _run_probe("--basetemp", str(explicit))

    assert observed == explicit.resolve()
