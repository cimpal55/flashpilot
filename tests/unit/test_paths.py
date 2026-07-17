from pathlib import Path

import pytest

from flashpilot.security.paths import PathContainmentError, PathSandbox


def test_sandbox_resolves_managed_child(tmp_path: Path) -> None:
    sandbox = PathSandbox.create(tmp_path / "run")

    resolved = sandbox.resolve_relative("checkpoints/model.pt")

    assert resolved == sandbox.root / "checkpoints" / "model.pt"


def test_sandbox_rejects_traversal_and_absolute_paths(tmp_path: Path) -> None:
    sandbox = PathSandbox.create(tmp_path / "run")

    with pytest.raises(ValueError):
        sandbox.resolve_relative("../outside")
    with pytest.raises(PathContainmentError):
        sandbox.require_contained(tmp_path / "outside")


def test_sandbox_rejects_symlink_escape_where_supported(tmp_path: Path) -> None:
    sandbox = PathSandbox.create(tmp_path / "run")
    outside = tmp_path / "outside"
    outside.mkdir()
    link = sandbox.root / "escape"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlinks are unavailable: {error}")

    with pytest.raises(PathContainmentError):
        sandbox.resolve_relative("escape/payload.pt")
