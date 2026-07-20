from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import torch
from pydantic import ValidationError

from flashpilot.conversion.artifacts import (
    ConversionArtifactError,
    commit_conversion_artifact,
    torch_payload_writer,
    validate_conversion_artifact,
)
from flashpilot.conversion.models import (
    ConversionArtifactManifestV1,
    ConversionComparisonPolicy,
    ConversionKind,
    ConversionRepresentation,
)
from flashpilot.conversion.schema import conversion_schema_documents
from flashpilot.conversion.service import (
    ConversionQualificationError,
    build_conversion_artifacts,
    compare_conversion_artifacts,
)
from flashpilot.conversion.workload import build_full_model_state, split_full_to_peft
from flashpilot.domain.manifests import ChecksumEntry

SHA = "a" * 64


def _entry(path: str) -> ChecksumEntry:
    return ChecksumEntry(path=path, sha256=SHA, size_bytes=1)


def test_conversion_manifest_enforces_fixed_role_and_payload_contract() -> None:
    with pytest.raises(ValidationError, match="role and representation"):
        ConversionArtifactManifestV1(
            artifact_id="source",
            role="source",
            conversion_kind=ConversionKind.FULL_TO_PEFT,
            representation=ConversionRepresentation.PEFT,
            format_version="peft-v1",
            profile="conversion",
            payloads=(_entry("adapter.pt"), _entry("base.pt")),
        )

    with pytest.raises(ValidationError, match="payload set"):
        ConversionArtifactManifestV1(
            artifact_id="source",
            role="source",
            conversion_kind=ConversionKind.FULL_TO_PEFT,
            representation=ConversionRepresentation.FULL_MODEL,
            format_version="full-model-v1",
            profile="conversion",
            payloads=(_entry("unexpected.pt"),),
        )


def test_candidate_manifest_requires_exact_source_provenance() -> None:
    with pytest.raises(ValidationError, match="bind its source"):
        ConversionArtifactManifestV1(
            artifact_id="candidate",
            role="candidate",
            conversion_kind=ConversionKind.FULL_TO_PEFT,
            representation=ConversionRepresentation.PEFT,
            format_version="peft-v1",
            profile="conversion",
            payloads=(_entry("adapter.pt"), _entry("base.pt")),
        )


def test_comparison_policy_does_not_hide_tolerance_or_weaken_exact_modes() -> None:
    with pytest.raises(ValidationError, match="explicit tolerance"):
        ConversionComparisonPolicy(mode="tolerance-bounded", atol=0.0, rtol=0.0)
    with pytest.raises(ValidationError, match="zero tolerance"):
        ConversionComparisonPolicy(mode="exact", atol=1e-12, rtol=0.0)


def test_full_to_peft_rejects_a_delta_above_the_fixed_rank() -> None:
    full = build_full_model_state()
    full["model.weight"] = full["model.weight"].clone()
    full["model.weight"][0, 0] += 1.0

    with pytest.raises(ConversionArtifactError, match="exceeds the supported PEFT rank"):
        split_full_to_peft(full)


def test_conversion_artifact_rejects_payload_tampering(tmp_path: Path) -> None:
    source, _ = build_conversion_artifacts(
        run_root=tmp_path / "run",
        kind=ConversionKind.FULL_TO_PEFT,
    )
    payload = source / "full.pt"
    with payload.open("r+b") as stream:
        stream.seek(0)
        original = stream.read(1)
        stream.seek(0)
        stream.write(bytes([original[0] ^ 1]))

    with pytest.raises(ConversionArtifactError, match="SHA-256"):
        validate_conversion_artifact(source)


def test_conversion_artifact_rejects_unmanifested_files(tmp_path: Path) -> None:
    source, _ = build_conversion_artifacts(
        run_root=tmp_path / "run",
        kind=ConversionKind.FULL_TO_PEFT,
    )
    (source / "extra.txt").write_text("unexpected\n", encoding="utf-8")

    with pytest.raises(ConversionArtifactError, match="not closed"):
        validate_conversion_artifact(source)


def test_integrity_valid_wrong_conversion_fails_semantic_checks(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    source, _ = build_conversion_artifacts(
        run_root=run_root,
        kind=ConversionKind.FULL_TO_PEFT,
    )
    source_artifact = validate_conversion_artifact(source)
    base, adapter = split_full_to_peft(build_full_model_state())
    adapter["adapter.a"] = adapter["adapter.a"] + 1.0
    bad = commit_conversion_artifact(
        run_root=run_root,
        parent_relative="bad",
        role="candidate",
        conversion_kind=ConversionKind.FULL_TO_PEFT,
        representation=ConversionRepresentation.PEFT,
        format_version="peft-v1",
        profile="conversion",
        global_step=None,
        source_artifact_sha256=source_artifact.fingerprint.sha256,
        payload_writers={
            "adapter.pt": torch_payload_writer(adapter),
            "base.pt": torch_payload_writer(base),
        },
    )

    result = compare_conversion_artifacts(
        source_path=source,
        candidate_path=bad.path,
        output_dir=tmp_path / "evidence",
    )

    assert result.passed is False
    assert "equivalence.parameters" in result.failed_check_ids
    assert "equivalence.outputs" in result.failed_check_ids
    assert result.source_unmodified is True


def test_provenance_mismatch_fails_without_normalizing_hashes(tmp_path: Path) -> None:
    run_root = tmp_path / "run"
    source, _ = build_conversion_artifacts(
        run_root=run_root,
        kind=ConversionKind.FULL_TO_PEFT,
    )
    base, adapter = split_full_to_peft(build_full_model_state())
    unbound = commit_conversion_artifact(
        run_root=run_root,
        parent_relative="unbound",
        role="candidate",
        conversion_kind=ConversionKind.FULL_TO_PEFT,
        representation=ConversionRepresentation.PEFT,
        format_version="peft-v1",
        profile="conversion",
        global_step=None,
        source_artifact_sha256="b" * 64,
        payload_writers={
            "adapter.pt": torch_payload_writer(adapter),
            "base.pt": torch_payload_writer(base),
        },
    )

    result = compare_conversion_artifacts(
        source_path=source,
        candidate_path=unbound.path,
        output_dir=tmp_path / "provenance-evidence",
    )

    assert result.passed is False
    assert result.failed_check_ids == ("provenance.source-sha256",)
    provenance = next(
        check for check in result.checks if check.check_id == "provenance.source-sha256"
    )
    assert provenance.actual == "b" * 64


def test_comparison_output_cannot_overlap_input_artifact(tmp_path: Path) -> None:
    source, candidate = build_conversion_artifacts(
        run_root=tmp_path / "run",
        kind=ConversionKind.FULL_TO_PEFT,
    )

    with pytest.raises(ConversionQualificationError, match="cannot overlap"):
        compare_conversion_artifacts(
            source_path=source,
            candidate_path=candidate,
            output_dir=source / "evidence",
        )


def test_copied_artifact_remains_valid_without_unrestricted_loading(tmp_path: Path) -> None:
    source, _ = build_conversion_artifacts(
        run_root=tmp_path / "run",
        kind=ConversionKind.FULL_TO_PEFT,
    )
    copied = tmp_path / "copied"
    shutil.copytree(source, copied)

    validated = validate_conversion_artifact(copied)
    payload = torch.load(copied / "full.pt", map_location="cpu", weights_only=True)

    assert validated.manifest.representation is ConversionRepresentation.FULL_MODEL
    assert isinstance(payload, dict)


def test_checked_in_conversion_schemas_match_strict_models() -> None:
    import json

    for filename, expected in conversion_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected
