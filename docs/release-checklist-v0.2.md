# FlashPilot v0.2 release checklist

This checklist prepares release artifacts; it does not authorize publication,
tag creation, or signing.

## Source and scope

- [ ] Independent review confirms Milestones 9–14 and the complete VNext
  requirement audit.
- [ ] Frozen tag `flashpilot-v0.1.0` still resolves to its original target.
- [ ] Release commit contains only reviewed v0.2 changes.
- [ ] No V0.3+, hosted service, signing, registry, distributed, CUDA, or extra
  adapter work is included.
- [ ] Apache-2.0 metadata and the checked-in `LICENSE` are reviewed together.

## Versions and schemas

- [ ] `pyproject.toml` and `flashpilot.__version__` both equal `0.2.0`.
- [ ] Python requirement remains `>=3.11`.
- [ ] Base dependencies and the `hf` extra match the reviewed bounds.
- [ ] Contract, policy, evidence-manifest, and attestation schemas match their
  deterministic generators.

## Quality and security

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```

- [ ] Full tests pass with only documented platform-conditional skips.
- [ ] Fixture demo retains the exact native 24/24 Recovery Gate.
- [ ] HF complete qualification passes and model-only qualification fails.
- [ ] Failed runs have no verified attestation.
- [ ] UNKNOWN never exits zero.
- [ ] Generated output is scanned for API-key sentinels and secret-bearing SDK
  objects.

## Build and distribution inspection

```powershell
.\.venv\Scripts\python.exe -m build
.\.venv\Scripts\python.exe -m twine check .\dist\flashpilot-0.2.0*
```

- [ ] Wheel and source distribution are both present with recorded SHA-256.
- [ ] Wheel metadata reports version `0.2.0`, `Requires-Python >=3.11`, base
  dependencies, and `Provides-Extra: hf`.
- [ ] Wheel contains all FlashPilot modules, captured fixtures, public schemas,
  policy/workflow examples, HF example, README metadata, and this checklist.
- [ ] Wheel/sdist contain no runs, caches, `.env`, API keys, or compiled Python
  artifacts.

## Two clean installations outside the repository

- [ ] Fresh base environment installs the wheel without Transformers,
  Accelerate, or safetensors.
- [ ] Base `flashpilot doctor` passes.
- [ ] Base fixture demo verifies 24/24 without an API call.
- [ ] Base static native audit passes on CPU.
- [ ] Base HF command exits `5` with the exact actionable
  `pip install 'flashpilot[hf]'` guidance.
- [ ] Separate fresh environment installs the wheel with `[hf]`.
- [ ] Installed default HF example qualifies exactly with distinct PIDs and no
  model/dataset download.
- [ ] Installed attestation verification and typed CI policy pass.
- [ ] Both output trees are secret-sentinel free.

## Human release actions

- [ ] Confirm the Apache-2.0 license metadata and copyright notice.
- [ ] Review release notes and measured limitations.
- [ ] Commit with the reviewed release message.
- [ ] Create an annotated `flashpilot-v0.2.0` tag only after independent review.
- [ ] Publish only the exact reviewed artifact hashes; do not rebuild between
  review and upload.
- [ ] Do not claim legal certification, publisher authentication, physical NAND
  savings, arbitrary Trainer compatibility, or hosted-service availability.
