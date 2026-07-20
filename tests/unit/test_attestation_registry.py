from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

import flashpilot.registry.service as registry_service
from flashpilot.attestation.crypto import (
    create_attestation_signature,
    generate_ed25519_signing_key,
)
from flashpilot.attestation.models import (
    ATTESTATION_SIGNATURE_PATH,
    AttestationVerificationCheck,
    AttestationVerificationResult,
    RecoveryAttestationV1,
)
from flashpilot.checkpoints.integrity import sha256_file
from flashpilot.cli import app
from flashpilot.registry import (
    AttestationRegistryArtifactV1,
    AttestationRegistryEntryV1,
    AttestationRegistryError,
    history_json,
    initialize_attestation_registry,
    register_recovery_attestation,
    verify_attestation_registry,
)
from flashpilot.registry.models import REGISTRY_PUBLIC_KEY_PATH
from flashpilot.registry.schema import registry_schema_documents


def _write_model(path: Path, model: object) -> None:
    assert hasattr(model, "model_dump")
    path.write_text(
        json.dumps(model.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _attestation(run_id: str, issued_at: datetime) -> RecoveryAttestationV1:
    digest = "1" * 64
    return RecoveryAttestationV1(
        framework_version="test",
        run_id=run_id,
        issued_at=issued_at,
        code_commit="unavailable",
        source_tree_state="unavailable",
        dependency_environment_sha256="2" * 64,
        checkpoint_path="repaired/checkpoints/checkpoint-step-000004",
        checkpoint_sha256="3" * 64,
        checkpoint_file_count=1,
        checkpoint_logical_bytes=1,
        persistence_contract_sha256="4" * 64,
        evidence_manifest_sha256="5" * 64,
        original_worker_pid=100,
        recovery_worker_pid=101,
        control_digest=digest,
        resumed_digest=digest,
        control_evaluation_digest="6" * 64,
        resumed_evaluation_digest="6" * 64,
        checks_passed=1,
        checks_total=1,
        rpo_steps=0,
        max_rpo_steps=0,
        rto_seconds=0.01,
        verified_persisted_bytes=1,
        limitations=("Synthetic registry-unit-test statement; not qualification evidence.",),
    )


def _create_source(
    root: Path,
    *,
    run_id: str,
    issued_at: datetime,
    private_key_path: Path,
    public_key_path: Path,
) -> tuple[Path, AttestationVerificationResult]:
    root.mkdir()
    attestation_path = root / "recovery.attestation.json"
    _write_model(attestation_path, _attestation(run_id, issued_at))
    signature = create_attestation_signature(
        attestation_path=attestation_path,
        private_key_path=private_key_path,
    )
    signature_path = root / ATTESTATION_SIGNATURE_PATH
    _write_model(signature_path, signature)
    verification = AttestationVerificationResult(
        attestation_sha256=sha256_file(attestation_path),
        signature_status="verified",
        signing_key_sha256=signature.public_key_sha256,
        signature_artifact_sha256=sha256_file(signature_path),
        checks=(
            AttestationVerificationCheck(
                check_id="bundle.integrity",
                detail="Synthetic source admitted by a unit-test verifier.",
            ),
            AttestationVerificationCheck(
                check_id="signature.ed25519",
                detail="Synthetic exact-byte signature passed.",
            ),
        ),
    )
    assert public_key_path.is_file()
    return attestation_path, verification


@pytest.fixture
def signed_sources(tmp_path: Path):
    generated = generate_ed25519_signing_key(tmp_path / "key")
    first = _create_source(
        tmp_path / "source-one",
        run_id="registry-run-one",
        issued_at=datetime(2026, 7, 21, 10, 0, tzinfo=UTC),
        private_key_path=generated.private_key_path,
        public_key_path=generated.public_key_path,
    )
    second = _create_source(
        tmp_path / "source-two",
        run_id="registry-run-two",
        issued_at=datetime(2026, 7, 21, 10, 0, tzinfo=UTC) + timedelta(seconds=1),
        private_key_path=generated.private_key_path,
        public_key_path=generated.public_key_path,
    )
    return generated, first, second


def _install_source_verifier(monkeypatch, results: dict[Path, AttestationVerificationResult]):
    calls: list[tuple[Path, Path | None, bool]] = []

    def verify(path: Path, *, public_key_path: Path | None, require_signed: bool):
        calls.append((path, public_key_path, require_signed))
        return results[path]

    monkeypatch.setattr(registry_service, "verify_recovery_attestation", verify)
    return calls


def test_registry_initialization_is_explicit_empty_and_non_overwriting(tmp_path: Path) -> None:
    registry_root = tmp_path / "registry"

    metadata = initialize_attestation_registry(registry_root)
    history = verify_attestation_registry(registry_root)

    assert metadata.history == "append-only-hash-chain"
    assert history.entry_count == 0
    assert history.head_entry_sha256 is None
    assert history.entries == ()
    with pytest.raises(AttestationRegistryError, match="must not already exist"):
        initialize_attestation_registry(registry_root)


def test_registry_appends_exact_artifacts_and_validates_two_entry_hash_chain(
    tmp_path: Path,
    monkeypatch,
    signed_sources,
) -> None:
    generated, first, second = signed_sources
    calls = _install_source_verifier(
        monkeypatch,
        {first[0]: first[1], second[0]: second[1]},
    )
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)

    first_entry = register_recovery_attestation(
        registry_root=registry_root,
        attestation_path=first[0],
        public_key_path=generated.public_key_path,
    )
    second_entry = register_recovery_attestation(
        registry_root=registry_root,
        attestation_path=second[0],
        public_key_path=generated.public_key_path,
    )
    history = verify_attestation_registry(registry_root)
    entry_directories = sorted((registry_root / "entries").iterdir())

    assert first_entry.sequence == 1
    assert first_entry.previous_entry_sha256 is None
    assert second_entry.sequence == 2
    assert second_entry.previous_entry_sha256 == entry_directories[0].name.split("-", 1)[1]
    assert history.entries == (first_entry, second_entry)
    assert history.head_entry_sha256 == entry_directories[1].name.split("-", 1)[1]
    assert (entry_directories[0] / "recovery.attestation.json").read_bytes() == first[
        0
    ].read_bytes()
    assert (entry_directories[0] / ATTESTATION_SIGNATURE_PATH).read_bytes() == (
        first[0].parent / ATTESTATION_SIGNATURE_PATH
    ).read_bytes()
    assert (entry_directories[0] / REGISTRY_PUBLIC_KEY_PATH).read_bytes() == (
        generated.public_key_path.read_bytes()
    )
    assert len(calls) == 4
    assert all(call[1:] == (generated.public_key_path, True) for call in calls)


def test_registry_rejects_duplicate_attestation_without_extending_history(
    tmp_path: Path,
    monkeypatch,
    signed_sources,
) -> None:
    generated, first, _ = signed_sources
    _install_source_verifier(monkeypatch, {first[0]: first[1]})
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)
    register_recovery_attestation(
        registry_root=registry_root,
        attestation_path=first[0],
        public_key_path=generated.public_key_path,
    )

    with pytest.raises(AttestationRegistryError, match="already registered"):
        register_recovery_attestation(
            registry_root=registry_root,
            attestation_path=first[0],
            public_key_path=generated.public_key_path,
        )

    assert verify_attestation_registry(registry_root).entry_count == 1


def test_registry_head_detects_newest_suffix_deletion(
    tmp_path: Path,
    monkeypatch,
    signed_sources,
) -> None:
    generated, first, second = signed_sources
    _install_source_verifier(
        monkeypatch,
        {first[0]: first[1], second[0]: second[1]},
    )
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)
    for source in (first, second):
        register_recovery_attestation(
            registry_root=registry_root,
            attestation_path=source[0],
            public_key_path=generated.public_key_path,
        )
    newest = sorted((registry_root / "entries").iterdir())[-1]
    shutil.rmtree(newest)

    with pytest.raises(AttestationRegistryError, match="HEAD does not match"):
        verify_attestation_registry(registry_root)


def test_registry_fails_closed_on_artifact_mutation(
    tmp_path: Path,
    monkeypatch,
    signed_sources,
) -> None:
    generated, first, _ = signed_sources
    _install_source_verifier(monkeypatch, {first[0]: first[1]})
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)
    register_recovery_attestation(
        registry_root=registry_root,
        attestation_path=first[0],
        public_key_path=generated.public_key_path,
    )
    entry_directory = next((registry_root / "entries").iterdir())
    with (entry_directory / "recovery.attestation.json").open("ab") as stream:
        stream.write(b" ")

    with pytest.raises(AttestationRegistryError, match="size or SHA-256"):
        verify_attestation_registry(registry_root)


@pytest.mark.parametrize("unexpected_name", ["unexpected.txt", ".tmp-interrupted"])
def test_registry_fails_closed_on_unknown_or_incomplete_entries(
    tmp_path: Path,
    unexpected_name: str,
) -> None:
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)
    path = registry_root / "entries" / unexpected_name
    if unexpected_name.startswith(".tmp"):
        path.mkdir()
    else:
        path.write_text("unexpected", encoding="utf-8")

    with pytest.raises(AttestationRegistryError, match="incomplete|non-symlink"):
        verify_attestation_registry(registry_root)


def test_registry_lock_fails_reads_closed_and_is_never_bypassed(tmp_path: Path) -> None:
    registry_root = tmp_path / "registry"
    initialize_attestation_registry(registry_root)
    (registry_root / registry_service.REGISTRY_LOCK_PATH).write_text("writer", encoding="utf-8")

    with pytest.raises(AttestationRegistryError, match="locked"):
        verify_attestation_registry(registry_root)


def test_registry_models_reject_noncanonical_inventory_and_missing_signature_check() -> None:
    artifact = AttestationRegistryArtifactV1(
        path="recovery.attestation.json",
        size_bytes=1,
        sha256="a" * 64,
    )

    with pytest.raises(ValidationError, match="fixed artifact inventory"):
        AttestationRegistryEntryV1(
            sequence=1,
            attestation_sha256="a" * 64,
            signature_artifact_sha256="b" * 64,
            signing_key_sha256="c" * 64,
            qualification_profile="exact-training-resume",
            framework="native-pytorch",
            adapter="native-pytorch",
            fault_scenario="process_termination",
            run_id="run",
            issued_at=datetime.now(UTC),
            verification_check_ids=("bundle.integrity",),
            artifacts=(artifact, artifact, artifact),
        )


def test_checked_in_registry_schemas_match_generator() -> None:
    for filename, expected in registry_schema_documents().items():
        actual = json.loads((Path("schemas") / filename).read_text(encoding="utf-8"))
        assert actual == expected


def test_registry_cli_initializes_verifies_and_prints_validated_history(tmp_path: Path) -> None:
    registry_root = tmp_path / "registry"
    runner = CliRunner()

    initialized = runner.invoke(app, ["attestation-registry", "init", str(registry_root)])
    verified = runner.invoke(app, ["attestation-registry", "verify", str(registry_root)])
    history = runner.invoke(app, ["attestation-registry", "history", str(registry_root)])

    assert initialized.exit_code == 0, initialized.output
    assert "ATTESTATION REGISTRY INITIALIZED" in initialized.output
    assert verified.exit_code == 0, verified.output
    assert "Entries: 0" in verified.output
    assert history.exit_code == 0, history.output
    assert json.loads(history.output) == json.loads(
        history_json(verify_attestation_registry(registry_root))
    )
