from __future__ import annotations

import tomllib
from pathlib import Path

from typer.testing import CliRunner

import flashpilot
import flashpilot.cli as cli
from flashpilot.adapters.huggingface import HuggingFaceDependencyError
from flashpilot.ci.exits import EXIT_UNSUPPORTED


def _pyproject() -> dict[str, object]:
    return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))


def test_release_version_and_python_target_are_synchronized() -> None:
    project = _pyproject()["project"]

    assert project["version"] == flashpilot.__version__ == "0.2.0"
    assert project["requires-python"] == ">=3.11"
    assert project["license"] == "Apache-2.0"


def test_hf_extra_declares_every_direct_runtime_dependency() -> None:
    project = _pyproject()["project"]
    hf = project["optional-dependencies"]["hf"]

    assert hf == [
        "accelerate>=1.14,<2",
        "safetensors>=0.8,<1",
        "transformers>=5.14,<6",
    ]
    assert all(
        name not in "\n".join(project["dependencies"])
        for name in ("transformers", "accelerate", "safetensors")
    )


def test_lightning_extra_is_optional_and_development_tested() -> None:
    project = _pyproject()["project"]
    optional = project["optional-dependencies"]

    assert optional["lightning"] == ["lightning>=2.6,<3"]
    assert "lightning>=2.6,<3" in optional["dev"]
    assert all("lightning" not in dependency for dependency in project["dependencies"])


def test_deepspeed_extra_is_linux_optional_and_development_tested() -> None:
    project = _pyproject()["project"]
    optional = project["optional-dependencies"]
    declaration = "deepspeed>=0.19,<0.20; platform_system != 'Windows'"

    assert optional["deepspeed"] == [declaration]
    assert declaration in optional["dev"]
    assert all("deepspeed" not in dependency for dependency in project["dependencies"])


def test_ed25519_uses_a_bounded_direct_cryptography_dependency() -> None:
    dependencies = _pyproject()["project"]["dependencies"]

    assert "cryptography>=46,<50" in dependencies
    assert all("sigstore" not in dependency for dependency in dependencies)
    assert "**/ed25519-private.pem" in Path(".gitignore").read_text(encoding="utf-8")


def test_release_data_files_cover_public_portable_artifacts() -> None:
    data_files = _pyproject()["tool"]["setuptools"]["data-files"]

    assert "schemas/ci-policy-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/attestation-signature-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/attestation-registry-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/attestation-registry-entry-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/attestation-registry-head-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/attestation-registry-history-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/attestation-registry-completion-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert "schemas/qualification-policy-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/qualification-policy-evaluation-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/organization-qualification-policy-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/organization-policy-evaluation-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/conversion-qualification-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/distributed-qualification-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/distributed-checkpoint-manifest-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/deepspeed-qualification-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/deepspeed-checkpoint-manifest-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert "schemas/storage-telemetry-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/partial-write-fuzz-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/fault-timing-trial-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/flashpilot-sarif-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/hf-preemption-certification-v1.schema.json"
        in data_files["share/flashpilot/schemas"]
    )
    assert "schemas/hf-preemption-commit-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert "schemas/hf-preemption-ready-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/multi-rank-failure-event-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert "schemas/multi-rank-fault-ready-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/multi-rank-peer-failure-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert (
        "schemas/previous-valid-fallback-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert "schemas/recovery-attestation-v1.schema.json" in data_files["share/flashpilot/schemas"]
    assert (
        "schemas/randomized-fault-timing-v1.schema.json" in data_files["share/flashpilot/schemas"]
    )
    assert data_files["share/flashpilot/examples/ci"] == [
        "examples/ci/organization-policy.yml",
        "examples/ci/policy.yml",
        "examples/ci/qualification-policy.yml",
    ]
    assert data_files["share/flashpilot/examples/hf_trainer"] == ["examples/hf_trainer/train.py"]
    assert data_files["share/flashpilot/docs"] == ["docs/release-checklist-v0.2.md"]


def test_installed_default_hf_worker_is_a_real_package_file() -> None:
    script = cli._default_hf_script()

    assert script == Path(cli.__file__).resolve().parent / "hf" / "worker.py"
    assert script.is_file()
    assert script.is_symlink() is False


def test_installed_default_lightning_worker_is_a_real_package_file() -> None:
    script = cli._default_lightning_script()

    assert script == Path(cli.__file__).resolve().parent / "lightning" / "worker.py"
    assert script.is_file()
    assert script.is_symlink() is False


def test_missing_hf_extra_has_actionable_stable_error(monkeypatch, tmp_path: Path) -> None:
    message = (
        "Hugging Face qualification requires the optional dependencies; "
        "install with `pip install 'flashpilot[hf]'`"
    )

    def missing() -> tuple[str, str]:
        raise HuggingFaceDependencyError(message)

    monkeypatch.setattr(cli, "require_huggingface_dependencies", missing)
    invocation = CliRunner().invoke(
        cli.app,
        ["qualify", "hf-trainer", "--run-dir", str(tmp_path / "hf")],
    )

    assert invocation.exit_code == EXIT_UNSUPPORTED
    assert message in invocation.output
    assert "OPENAI_API_KEY" not in invocation.output


def test_readme_exposes_release_paths_active_ci_and_limitations() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")

    for heading in (
        "### 1. 60-second fixture demo",
        "### 2. Static checkpoint audit",
        "### 3. Hugging Face qualification example",
        "## Limitations and roadmap",
    ):
        assert heading in readme
    assert "flashpilot-0.2.0-py3-none-any.whl" in readme
    assert "pip install 'flashpilot[hf]'" in readme
    assert ".github/workflows/flashpilot-qualification.yml" in readme
    assert "active pull-request and manual hosted workflow" in readme
    assert "flashpilot[lightning]" in readme


def test_release_checklist_keeps_human_release_actions_unperformed() -> None:
    checklist = Path("docs/release-checklist-v0.2.md").read_text(encoding="utf-8")

    assert "- [ ] Confirm the Apache-2.0 license metadata" in checklist
    assert "- [ ] Create an annotated `flashpilot-v0.2.0` tag" in checklist
    assert "does not authorize publication" in checklist
