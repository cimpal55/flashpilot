"""Resolved containment checks for all FlashPilot-managed checkpoint paths."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from flashpilot.domain.manifests import validate_managed_relative_path


class PathContainmentError(ValueError):
    """Raised when a managed path escapes its declared sandbox."""


@dataclass(frozen=True, slots=True)
class PathSandbox:
    """A resolved root used to contain all managed reads and writes."""

    root: Path

    @classmethod
    def create(cls, root: Path) -> PathSandbox:
        root.mkdir(parents=True, exist_ok=True)
        if not root.is_dir():
            raise PathContainmentError("sandbox root must be a directory")
        return cls(root=root.resolve(strict=True))

    def resolve_relative(
        self,
        relative_path: str,
        *,
        must_exist: bool = False,
        reject_symlinks: bool = True,
    ) -> Path:
        normalized = validate_managed_relative_path(relative_path)
        return self.require_contained(
            self.root.joinpath(*normalized.split("/")),
            must_exist=must_exist,
            reject_symlinks=reject_symlinks,
        )

    def require_contained(
        self,
        candidate: Path,
        *,
        must_exist: bool = False,
        reject_symlinks: bool = True,
    ) -> Path:
        lexical = candidate if candidate.is_absolute() else self.root / candidate
        try:
            resolved = lexical.resolve(strict=must_exist)
        except OSError as error:
            raise PathContainmentError(f"managed path cannot be resolved: {candidate}") from error

        if not resolved.is_relative_to(self.root):
            raise PathContainmentError(f"managed path escapes sandbox: {candidate}")
        if reject_symlinks:
            self._reject_existing_symlink_components(lexical)
        if must_exist and not resolved.exists():
            raise PathContainmentError(f"managed path does not exist: {candidate}")
        return resolved

    def _reject_existing_symlink_components(self, candidate: Path) -> None:
        current = candidate
        while current != self.root:
            if current.exists() and current.is_symlink():
                raise PathContainmentError(f"managed path contains a symlink: {candidate}")
            parent = current.parent
            if parent == current:
                raise PathContainmentError(f"managed path is not rooted in sandbox: {candidate}")
            current = parent
