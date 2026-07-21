"""Build the report-UI sample corpus from real FlashPilot run directories.

This script copies a curated set of *real* runs into ``samples/`` and emits
``report-ui/src/data/bundles.js`` — a static ES module carrying the same bytes
so the UI works from ``file://`` and from GitHub Pages with no server.

It imports nothing from ``flashpilot`` and never recomputes a verdict: every
status value is copied verbatim from the artifacts the core already produced.
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SAMPLES = REPO / "samples"
BUNDLE_OUT = REPO / "report-ui" / "src" / "data" / "bundles.js"


@dataclass(frozen=True)
class Sample:
    """A curated real run promoted into the sandbox."""

    sample_id: str
    source: str
    title: str
    subtitle: str
    kind: str  # qualification | repair | audit
    copy: tuple[str, ...] = field(default=())
    # Optional run-relative directory holding a real organization-policy
    # evaluation produced by `flashpilot enforce-organization-policy`. Never a
    # hand-written file: the UI only renders what the CLI actually wrote.
    policy_source: str | None = None


SAMPLES_SPEC: tuple[Sample, ...] = (
    Sample(
        sample_id="hf-model-only",
        source="final-hf-model-only",
        title="Hugging Face — model-only checkpoint",
        subtitle="Loads without error. Provably cannot resume the same run.",
        kind="qualification",
        copy=("result.json", "junit.xml", "job-summary.md", "report.md"),
        policy_source="final-policy/fail",
    ),
    Sample(
        sample_id="hf-complete",
        source="final-hf-complete",
        title="Hugging Face — complete checkpoint",
        subtitle="Real kill, new process, identical trajectory, signed attestation issued.",
        kind="qualification",
        copy=(
            "result.json",
            "junit.xml",
            "attestation.junit.xml",
            "job-summary.md",
            "report.md",
            "recovery.attestation.json",
            "recovery.attestation.signature.json",
            "evidence-manifest.json",
            "persistence-contract.json",
            "environment.json",
        ),
        policy_source="final-policy/pass",
    ),
    Sample(
        sample_id="native-repair",
        source="milestone13-native",
        title="Native PyTorch — repair loop",
        subtitle="Contract violation detected, repaired, then re-qualified end to end.",
        kind="repair",
        copy=(
            "result.json",
            "junit.xml",
            "attestation.junit.xml",
            "job-summary.md",
            "report.md",
            "recovery.attestation.json",
            "evidence-manifest.json",
            "persistence-contract.json",
            "environment.json",
        ),
    ),
    Sample(
        sample_id="lightning-complete",
        source="dev-lightning-complete-3",
        title="PyTorch Lightning — complete checkpoint",
        subtitle="Same gate, different framework: VERIFIED.",
        kind="qualification",
        copy=("result.json", "junit.xml", "report.md"),
    ),
    Sample(
        sample_id="lightning-weights-only",
        source="dev-lightning-weights-2",
        title="PyTorch Lightning — weights-only checkpoint",
        subtitle="The same failure class reproduces outside Hugging Face.",
        kind="qualification",
        copy=("result.json", "junit.xml", "report.md"),
    ),
    Sample(
        sample_id="unknown-layout",
        source="milestone13-unknown-audit",
        title="Unrecognised checkpoint layout",
        subtitle="Not trusted, not guessed. UNKNOWN is never rendered as PASS.",
        kind="audit",
        copy=("audit.json", "junit.xml", "job-summary.md", "report.md"),
    ),
)

# Evidence payloads are only embedded for files the manifest itself lists, so the
# UI can never verify a file the core did not put under the closed inventory.
MAX_EMBEDDED_BYTES = 4 * 1024 * 1024


def read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def verdict_of(kind: str, result: dict | None) -> str:
    """Copy the verdict. Never derive one."""
    if result is None:
        return "UNKNOWN"
    for key in ("final_verdict", "verdict", "status"):
        value = result.get(key)
        if isinstance(value, str) and value:
            return value.upper()
    return "UNKNOWN"


def collect_evidence(run_dir: Path, manifest: dict | None) -> tuple[dict, list[str]]:
    """Base64 the exact bytes the manifest claims. Missing files stay missing."""
    if not manifest:
        return {}, []
    files: dict[str, str] = {}
    missing: list[str] = []
    total = 0
    for entry in manifest.get("entries", []):
        rel = entry["path"]
        target = (run_dir / rel).resolve()
        try:
            target.relative_to(run_dir.resolve())
        except ValueError:
            missing.append(rel)
            continue
        if not target.is_file():
            missing.append(rel)
            continue
        raw = target.read_bytes()
        total += len(raw)
        if total > MAX_EMBEDDED_BYTES:
            raise SystemExit(f"evidence payload exceeds {MAX_EMBEDDED_BYTES} bytes at {rel}")
        files[rel] = base64.b64encode(raw).decode("ascii")
    return files, missing


def copy_sample(spec: Sample, runs_root: Path) -> Path:
    src = runs_root / spec.source
    if not src.is_dir():
        raise SystemExit(f"missing source run: {src}")
    dest = SAMPLES / spec.sample_id
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    for name in spec.copy:
        origin = src / name
        if origin.is_file():
            shutil.copy2(origin, dest / name)

    manifest = read_json(dest / "evidence-manifest.json")
    if manifest:
        for entry in manifest.get("entries", []):
            rel = entry["path"]
            origin = (src / rel).resolve()
            try:
                origin.relative_to(src.resolve())
            except ValueError:
                continue
            if not origin.is_file():
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origin, target)

    # newline="\n" everywhere: samples/ and bundles.js are marked -text in
    # .gitattributes, so a platform-dependent line ending would make
    # regeneration produce a spurious diff on Linux CI.
    if spec.policy_source is not None:
        policy_root = (runs_root / spec.policy_source).resolve()
        if not policy_root.is_dir():
            raise SystemExit(f"missing policy evaluation directory: {policy_root}")
        for name, target_name in (
            ("organization-policy-evaluation.json", "organization-policy-evaluation.json"),
            ("junit.xml", "organization-policy.junit.xml"),
        ):
            origin = policy_root / name
            if origin.is_file():
                shutil.copy2(origin, dest / target_name)

    (dest / "SOURCE.txt").write_text(
        f"Copied verbatim from runs/{spec.source} of the FlashPilot core repository.\n"
        + (
            f"Organization-policy evaluation copied from runs/{spec.policy_source},\n"
            "produced by `flashpilot enforce-organization-policy`.\n"
            if spec.policy_source
            else ""
        )
        + "No value in this directory was edited, regenerated, or synthesised.\n",
        encoding="utf-8",
        newline="\n",
    )
    return dest


def build_bundle(spec: Sample, dest: Path) -> dict:
    result = read_json(dest / "result.json")
    audit = read_json(dest / "audit.json")
    core = result if result is not None else audit
    manifest = read_json(dest / "evidence-manifest.json")
    files, missing = collect_evidence(dest, manifest)

    # The attestation is also carried as raw bytes so the UI can offer a
    # byte-exact download and hash it in-browser; a re-serialized JSON copy
    # would hash differently and defeat the point.
    att_path = dest / "recovery.attestation.json"
    attestation_raw = (
        base64.b64encode(att_path.read_bytes()).decode("ascii") if att_path.is_file() else None
    )

    # The manifest's own bytes, so the browser can bind the inventory to the
    # attestation's evidence_manifest_sha256 rather than trusting that they
    # refer to the same manifest.
    man_path = dest / "evidence-manifest.json"
    manifest_raw = (
        base64.b64encode(man_path.read_bytes()).decode("ascii") if man_path.is_file() else None
    )

    return {
        "id": spec.sample_id,
        "title": spec.title,
        "subtitle": spec.subtitle,
        "kind": spec.kind,
        "source_run": spec.source,
        "verdict": verdict_of(spec.kind, core),
        "result": core,
        "attestation": read_json(dest / "recovery.attestation.json"),
        "attestation_raw": attestation_raw,
        # Presence only. The UI reports that a detached signature exists; it
        # never claims to have verified one.
        "signature": read_json(dest / "recovery.attestation.signature.json"),
        "manifest_raw": manifest_raw,
        "manifest": manifest,
        "contract": read_json(dest / "persistence-contract.json"),
        "environment": read_json(dest / "environment.json"),
        # Organization-policy evaluations are consumed only if the core actually
        # emitted them into the run directory. Nothing here synthesises a policy
        # verdict, an exit code, or a merge decision.
        "policy_evaluation": read_json(dest / "organization-policy-evaluation.json"),
        "policy_junit": read_text(dest / "organization-policy.junit.xml"),
        "junit": read_text(dest / "junit.xml"),
        "attestation_junit": read_text(dest / "attestation.junit.xml"),
        "job_summary": read_text(dest / "job-summary.md"),
        "evidence_files": files,
        "evidence_missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        default=str(REPO.parent / "flashpilot" / "runs"),
        help="directory holding the real FlashPilot run outputs",
    )
    args = parser.parse_args()
    runs_root = Path(args.runs).resolve()

    SAMPLES.mkdir(exist_ok=True)
    bundles = []
    for spec in SAMPLES_SPEC:
        dest = copy_sample(spec, runs_root)
        bundle = build_bundle(spec, dest)
        bundles.append(bundle)
        print(
            f"{spec.sample_id:24s} {bundle['verdict']:9s} "
            f"{len(bundle['evidence_files']):3d} evidence files"
        )

    BUNDLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(bundles, indent=1, sort_keys=True, ensure_ascii=False)
    BUNDLE_OUT.write_text(
        "// GENERATED FILE — do not edit by hand.\n"
        "// Produced by tools/build_samples.py from the real run directories in\n"
        "// samples/. Every value here is copied; none is computed by the UI.\n"
        f"export const BUNDLES = {payload};\n",
        encoding="utf-8",
        newline="\n",
    )
    size_kb = round(BUNDLE_OUT.stat().st_size / 1024)
    print(f"\nwrote {BUNDLE_OUT.relative_to(REPO)} ({size_kb} KB)")


if __name__ == "__main__":
    main()
