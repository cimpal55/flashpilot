"""Verify the sample corpus is internally consistent and untouched.

Two independent claims are checked, both without importing flashpilot:

1. every file listed in a sample's evidence manifest hashes to the sha256 and
   size the manifest records — i.e. the copy in ``samples/`` is byte-identical
   to what the core attested;
2. the base64 payloads embedded in ``report-ui/src/data/bundles.js`` decode to
   exactly those same bytes — i.e. what the browser hashes is what is on disk.

This is the CI counterpart to the in-browser verifier, and it fails closed.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SAMPLES = REPO / "samples"
BUNDLES_JS = REPO / "report-ui" / "src" / "data" / "bundles.js"


def load_bundles() -> list[dict]:
    text = BUNDLES_JS.read_text(encoding="utf-8")
    match = re.search(r"export const BUNDLES = (\[.*\]);\s*$", text, re.S)
    if not match:
        raise SystemExit("bundles.js does not have the expected generated shape")
    return json.loads(match.group(1))


def main() -> int:
    if not BUNDLES_JS.is_file():
        raise SystemExit("bundles.js is missing — run tools/build_samples.py first")

    bundles = {b["id"]: b for b in load_bundles()}
    failures: list[str] = []
    checked = 0

    for sample_dir in sorted(p for p in SAMPLES.iterdir() if p.is_dir()):
        sample_id = sample_dir.name
        bundle = bundles.get(sample_id)
        if bundle is None:
            failures.append(f"{sample_id}: present on disk but absent from bundles.js")
            continue

        manifest_path = sample_dir / "evidence-manifest.json"
        if not manifest_path.is_file():
            print(f"{sample_id:24s} no manifest — verifier renders VOID (expected)")
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        embedded = bundle.get("evidence_files", {})

        for entry in manifest["entries"]:
            rel = entry["path"]
            target = (sample_dir / rel).resolve()
            try:
                target.relative_to(sample_dir.resolve())
            except ValueError:
                failures.append(f"{sample_id}: manifest path escapes the sample root: {rel}")
                continue
            if not target.is_file():
                failures.append(f"{sample_id}: manifest references a missing file: {rel}")
                continue

            raw = target.read_bytes()
            checked += 1

            actual = hashlib.sha256(raw).hexdigest()
            if actual != entry["sha256"]:
                failures.append(f"{sample_id}: {rel} sha256 {actual} != manifest {entry['sha256']}")
            if entry.get("size_bytes") is not None and entry["size_bytes"] != len(raw):
                failures.append(f"{sample_id}: {rel} size {len(raw)} != manifest {entry['size_bytes']}")

            payload = embedded.get(rel)
            if payload is None:
                failures.append(f"{sample_id}: {rel} is in the manifest but not embedded in bundles.js")
            elif base64.b64decode(payload) != raw:
                failures.append(f"{sample_id}: {rel} embedded bytes differ from the file on disk")

        print(f"{sample_id:24s} {len(manifest['entries']):3d} evidence files verified")

    if failures:
        print(f"\nFAILED — {len(failures)} problem(s):", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"\nOK — {checked} evidence files match their manifests and their embedded copies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
