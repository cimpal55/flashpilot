"""SHA-256 and logical-byte helpers for checkpoint artifacts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DirectoryContentFingerprint:
    sha256: str
    file_count: int
    logical_bytes: int


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def logical_directory_bytes(directory: Path) -> int:
    return sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())


def directory_content_fingerprint(directory: Path) -> DirectoryContentFingerprint:
    """Hash sorted relative file names and bytes, refusing symbolic links."""

    if not directory.is_dir() or directory.is_symlink():
        raise ValueError("directory fingerprint requires a non-symlink directory")
    digest = hashlib.sha256()
    file_count = 0
    logical_bytes = 0
    for candidate in sorted(
        directory.rglob("*"),
        key=lambda item: item.relative_to(directory).as_posix(),
    ):
        if candidate.is_symlink():
            raise ValueError("directory fingerprint refuses symbolic links")
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(directory).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with candidate.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        file_count += 1
        logical_bytes += candidate.stat().st_size
    if file_count == 0:
        raise ValueError("directory fingerprint requires at least one file")
    return DirectoryContentFingerprint(
        sha256=digest.hexdigest(),
        file_count=file_count,
        logical_bytes=logical_bytes,
    )
