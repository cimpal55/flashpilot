# FlashPilot

FlashPilot is a checkpoint recovery qualification and verification harness that proves whether a training checkpoint can resume correctly after a real process failure.

It complements—rather than replaces—PyTorch, Hugging Face, DeepSpeed, NeMo,
and their checkpoint implementations. P0 qualifies one controlled CPU-only
native-PyTorch workflow through real termination, new-process restore, exact
trajectory comparison, evidence-bounded GPT-5.6 diagnosis, one typed repair,
and deterministic re-verification.

## 60-second quick start

Install the prebuilt wheel in a clean Python environment:

```powershell
python -m pip install .\dist\flashpilot-0.1.0-py3-none-any.whl
flashpilot doctor
```

Exact judge command:

```powershell
flashpilot demo --provider fixture
```

No API key, network access, model download, or dataset download is required.
The command automatically creates and prints a unique `runs/repair-<uuid>`
directory, performs the complete real red-to-green workflow, and writes:

- `result.json` — authoritative typed evidence;
- `report.md` — deterministic Markdown summary;
- `report.html` — self-contained static rendering of `result.json`.

## What the demo proves

1. An uninterrupted seeded CPU control produces stable trajectory evidence.
2. A valid, checksummed, loadable checkpoint omitting training continuation
   state restores in a new process but fails the exact Recovery Gate.
3. GPT-5.6 receives only sanitized manifest, restore, failed-check, and
   trajectory evidence—not the injection label, expected diagnosis, or repair
   preset.
4. Deterministic guardrails classify the captured recommendation. Exactly six
   NativePyTorchAdapter actions can map to six explicit boolean fields;
   unsupported advice is recorded and not executed.
5. One new isolated strategy is tested through a second real termination and
   distinct recovery process. The original failed checkpoint remains unchanged.
6. Only the final deterministic Recovery Gate can print `VERIFIED`, using
   exact equality with `atol=0.0` and `rtol=0.0`.
7. Recurring logical-byte reduction is shown only after verification. The
   immutable frozen-base cost is reported separately, and the first
   adapter-aware write is not presented as savings.

## GPT-5.6 role

The judge path displays exactly:

```text
GPT source: GPT-5.6 captured-response fixture/replay
```

The checked-in fixture reproduces an independently accepted, secret-free live
GPT-5.6 structured response and retains its capture metadata. Runtime use is
explicitly labeled fixture/replay and makes no live API call. GPT recommends;
deterministic code validates, executes the fixed action mapping, and decides
recovery.

The optional `live-contract` and `live-failure` commands remain available for
explicit guarded validation with an API key. They are not used by the judge
command.

## Supported and verified environment

- Verified: Windows 11, Python 3.12.13, PyTorch CPU execution.
- Package declaration: Python 3.11 or newer. Python 3.11 has not been verified
  and is not claimed as such.
- No CUDA, external datasets, downloaded weights, server, or desktop UI.
- Payload and metadata files are fsynced and directory rename is atomic.
  Python does not expose directory fsync on Windows, so directory durability is
  explicitly best-effort there.
- The Windows directory-symlink containment test stays enabled and skips only
  when the host user lacks symlink privilege.

Run environment qualification at any time:

```powershell
flashpilot doctor
```

It reports Python, platform, CPU execution, dependency versions, fixture
availability, output writability, API-key presence without its value, and the
Windows directory-fsync limitation.

## Inspecting a completed run

```powershell
flashpilot audit --run-dir .\runs\repair-<uuid>
flashpilot verify --run-dir .\runs\repair-<uuid>
flashpilot replay --run-dir .\runs\repair-<uuid>
```

These commands are read-only. `replay` revalidates the captured structured
response without making an API call.

## Measurement limitation

Logical checkpoint bytes were measured in the controlled demo. Physical NAND
writes, write amplification, and SSD lifetime were not measured. Results apply
only to the controlled model, profile, serialization, and current environment;
they are not a general compression or hardware-lifetime claim.

## Scope limits

P0 supports only `NativePyTorchAdapter` and the six primary Section 28.5 repair
actions. It intentionally has no plugin discovery, framework auto-detection,
additional adapter, repository scanner, AST analyzer, policy planner, numeric
CrashScore, arbitrary patch executor, Docker path, Hugging Face integration, or
GPT report narrator.

## Prior art and positioning

FlashPilot does not claim checkpoint scheduling, adapter-only persistence,
compression, incremental checkpoints, atomic writes, checksums, or chaos testing
as new techniques. [docs/research.md](docs/research.md) positions the harness
against CheckFreq, Check-N-Run, ExCP, Amber, IncrCP, OPT, MegaScale,
FlashRecovery, REO, MiDAS, FDP/WARP, and ZipLLM without implementing those
systems.

## Codex contribution summary

Codex implemented the deterministic workload, integrity-valid checkpoint
strategies, real parent-controlled process termination, new-process restore,
24-check Recovery Gate, strict GPT-5.6 schemas and redaction, captured-response
replay, six-field bounded executor, immutable-history proof, second recovery
verification, Rich judge console, offline doctor, static reports, tests, and
wheel validation. GPT-5.6 supplied bounded recommendations; it did not write or
execute repair code and did not declare recovery successful.

## Development quality gates

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```
