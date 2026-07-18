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

The wheel contains FlashPilot and its captured-response fixtures, but it is not
a fully self-contained dependency bundle. A fresh `pip install` may use the
configured package index or local cache to resolve declared dependencies.

Exact judge command:

```powershell
flashpilot demo --provider fixture
```

After installation, no API key, network access, model download, or dataset
download is required by the application demo. The command automatically creates
and prints a unique `runs/repair-<uuid>`
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

## Audience and architecture

FlashPilot is for ML engineers, researchers, and checkpoint-integration authors
who need an executable recovery qualification test. The P0 architecture is
intentionally narrow:

```text
seeded CPU control
-> atomic checkpoint commit
-> parent-owned worker termination
-> distinct-process restore
-> deterministic Recovery Gate
-> captured GPT-5.6 diagnosis replay
-> typed six-field repair
-> second termination and restore
-> final Recovery Gate
-> post-pass logical-byte comparison
```

`result.json` is the canonical machine-readable evidence. `report.md`, the
self-contained `report.html`, and the Rich console are deterministic views of
that record; there is no GPT report narrator or duplicated experiment logic.

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

## Responsibility boundary

- GPT-5.6 inferred the checkpoint contract and diagnosed the observed failed
  recovery from sanitized structured evidence. It proposed typed actions only.
- Codex implemented the workload, checkpoint protocols, process orchestration,
  schemas, guardrails, bounded executor, reports, packaging, tests, and release
  documentation.
- The human fixed the scope at one native PyTorch adapter, chose the valid but
  incomplete training-state scenario, limited repair to six actions and one
  attempt, required blind diagnosis, and required proof before savings.
- Normal deterministic code validates manifests, checksums, containment,
  process evidence, exact state and trajectory equality, action capabilities,
  repair immutability, and the attempt limit.
- Only the deterministic Recovery Gate may declare `VERIFIED`. Neither GPT-5.6,
  Codex, fixture provenance, checkpoint loadability, nor report prose can do so.

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

The independently accepted Windows/Python 3.12.13 demo-profile run measured:

| Verified quantity | Result |
| --- | ---: |
| Initial Recovery Gate | FAIL, 9 exact failed checks |
| Final Recovery Gate | VERIFIED, 24/24 checks |
| Comparison policy | `atol=0.0`, `rtol=0.0` |
| `safe_full` recurring logical bytes | 126,218 |
| Repaired recurring logical bytes | 32,743 |
| Recurring logical-byte reduction | 93,475 bytes (74.06%) |
| One-time immutable frozen base | 93,987 bytes, reported separately |

These values come from the accepted Prompt 6 run. Timing is environment- and
invocation-dependent and is retained in the build log rather than generalized.

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

## Security model

FlashPilot accepts no arbitrary commands or source patches. Managed writes are
contained under the selected run root; traversal and supported symlink escapes
fail closed. Checkpoints require completion, manifest, checksum, base-identity,
and containment validation before loading. GPT receives bounded redacted JSON,
never raw tensors, dataset samples, secrets, arbitrary files, absolute local
paths, the injection label, expected diagnosis, or a repair preset. API keys are
read only from the environment and are never printed or persisted.

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

## Limitations and roadmap

The verified scope is one controlled CPU-only `NativePyTorchAdapter` workload on
Windows 11 with Python 3.12.13. Python 3.11 compatibility is targeted but not
locally verified. Windows directory fsync is unavailable through Python and is
best-effort. The project does not qualify arbitrary repositories, distributed
training, CUDA, Hugging Face, DeepSpeed, NeMo, TensorFlow, or JAX. Fixture replay
is tied to the captured schema and evidence contract; novel failures require a
new guarded live analysis. Physical storage effects are not measured.

Future work may add separately qualified adapters, distributed and partial-write
scenarios, previous-valid fallback, broader platform validation, and CI. Those
items remain roadmap only and are not part of the submission proof.

## Repository and license

Repository: <https://github.com/cimpal55/flashpilot>

No license file is currently committed. Selecting and adding the intended
license remains a human release decision and is listed in the release checklist.

## Development quality gates

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```
