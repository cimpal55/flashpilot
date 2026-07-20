# Build log

## Milestone 0 — inspect, scaffold, deterministic workload

- Date: 2026-07-17
- Objective: create the project scaffold and prove repeated uninterrupted CPU control runs match.
- Codex contributions: repository inspection, architecture and decision scaffolds, deterministic workload implementation, unit and integration tests, and quality-gate execution.
- Human decisions: Section 28.5 is binding; Prompt 0 is the only authorized milestone; the eight stated non-negotiable constraints are accepted.
- Environment observed: Windows 11, PowerShell 5.1, 12 logical processors; no system Python, Ruff, or pytest command was available at inspection time. A Codex workspace Python runtime was located for environment bootstrapping.
- Problems found: quality-gate dependencies, including PyTorch, were absent from the initially available runtime. The first sandboxed dependency install was network-blocked; the approved retry exceeded its first two-minute command timeout after installing most packages, and a second approved retry completed the editable install. The first summary-output path under `C:\tmp` was denied, so the direct control evidence was written under the ignored `runs/` sandbox instead.
- Files changed: `.gitignore`, `AGENTS.md`, `pyproject.toml`, `runs/.gitkeep`, the `src/flashpilot/workload` implementation, unit and integration tests, and the required Prompt 0 documentation scaffolds.

### Commands and actual output

```text
python -m flashpilot.workload.control --profile ci --output runs\prompt0-control.json
Exit code: 0
final_global_step: 8
device: cpu
deterministic_algorithms: true
torch_threads: 1
trainable_state.sha256: 1fc72fdf21487afe7b32da833d2300cd9a68f0c0c6f3ce1456910a5102a92997
evaluation.sha256: a42a6d25c8aaf6674130ef63439f6fd415824bd23ff9cd6a7c0ca0305be3ef9a

python -c "run the demo control twice and compare summaries"
{'match': True, 'steps': 24, 'trainable_sha256': 'a14fc50336e483a1004ed6b447c4bc590f04a59021c0244624ae10ca9e8a15cd', 'evaluation_sha256': '11a538dad7243487ea1192d395ea73544bab48505b533600571c4e94d6c4149c'}

ruff check .
All checks passed!

ruff format --check .
Initial result: 10 files would be reformatted, 1 file already formatted.

ruff format .
10 files reformatted, 1 file left unchanged

pytest -q
........                                                                 [100%]
8 passed in 7.40s
```

The required gates are rerun after documentation and audit changes; their final
output is reported in the milestone handoff.

### Final quality-gate rerun

```text
ruff check .
All checks passed!

ruff format --check .
11 files already formatted

pytest -q
........                                                                 [100%]
8 passed in 3.35s
```

- Remaining risks: cross-process reproducibility, later valid-but-incomplete checkpoint semantics, and sanitized-but-useful GPT evidence.

## Milestone 0 correction — project-local pytest paths

- Date: 2026-07-17
- Scope: Prompt 0 verification only; no Prompt 1 work.
- Independent result reported from a normal non-administrator Windows
  PowerShell session: `7 passed`, with one integration-test fixture setup error
  before the test body ran. Pytest raised `PermissionError` while accessing
  `C:\Users\cimpal55\AppData\Local\Temp\pytest-of-cimpal55` and could not write
  `C:\Programming\business\flashpilot\.pytest_cache`.
- Cause addressed: pytest was relying on host-global or previously created
  runtime directories whose ACLs can be incompatible across host and sandbox
  execution principals.
- Correction: configure `.pytest-local/temp` as pytest's base temporary path and
  `.pytest-local/cache` as its cache, and ignore all of `.pytest-local`.
- Test integrity: the integration test still uses `tmp_path`; no test was
  disabled, skipped, xfailed, or weakened, and the deterministic workload and
  exact reproducibility checks were not changed.
- Corrected quality-gate output:

  ```text
  ruff check .
  All checks passed!

  ruff format --check .
  11 files already formatted

  .\.venv\Scripts\python.exe -m pytest -q
  ........                                                                 [100%]
  8 passed in 4.28s
  ```

## Milestone 1 — safe checkpoint foundations

- Date: 2026-07-17
- Objective: implement integrity and containment models, atomic commit,
  fail-closed loading, safe retention, complete `safe_full` state, direct
  restore, metrics, and the Prompt 1 CLI surface.
- Human constraints: Section 28.5 remains binding; Prompt 1 is the only
  authorized milestone; CPU determinism and repository-local pytest paths must
  remain unchanged; Windows directory durability must be reported honestly.
- Local validation runtime: Python 3.12.13, PyTorch 2.13.0+cpu, Windows 11.
  Python 3.11 remains the compatibility target through project metadata and
  Ruff's `py311` target.
- Problem found: Windows raised `OSError: [Errno 9] Bad file descriptor` when
  payload `fsync` reopened a file read-only. Windows `_commit` requires write
  access, so payloads are reopened as non-mutating `r+b` after their writers
  close. Synchronization remains enabled.
- Symlink test: skipped on this host because non-administrator Windows denied
  symlink creation with `WinError 1314`; traversal and resolved containment tests
  passed. The symlink-escape assertion runs where the platform permits creating
  the fixture.

### Measured demo safe_full baseline

Command:

```text
.\.venv\Scripts\flashpilot.exe safe-full --profile demo --run-dir runs\prompt1-demo-safe-full-d544421
```

Actual measured result at checkpoint step 12 of 24:

```text
logical_checkpoint_bytes_written: 126170
checkpoint_duration_seconds: 0.1324288999894634
restore_duration_seconds: 0.046628499985672534
direct_restore_matches_control: true
payload_files_fsynced: true
metadata_files_fsynced: true
atomic_rename_succeeded: true
temp_directory_fsync.supported: false
parent_directory_fsync.supported: false
```

The 126,170-byte logical total was independently summed from the actual files:

```text
checksums.json      805
COMPLETE             92
manifest.json      1260
model.pt          98546
optimizer.pt       8995
rng.pt            14285
scheduler.pt       1465
state.json          722
TOTAL            126170
```

This is a complete safe-full direct-restore baseline, not a Recovery Gate
verdict or a storage-savings claim. Physical NAND writes, write amplification,
and SSD lifetime were not measured.

### Intermediate test correction output

The first expanded run exposed the Windows file-descriptor issue and reported:

```text
6 failed, 19 passed, 1 skipped, 6 errors in 2.39s
```

After the file `fsync` correction:

```text
...........................s....                                         [100%]
31 passed, 1 skipped in 3.42s
```

### Final quality-gate output

```text
ruff check .
All checks passed!

ruff format --check .
31 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
.............................s....                                       [100%]
33 passed, 1 skipped in 3.99s
```

The one skip is the explicitly platform-conditional symlink fixture described
above; no test was disabled, xfailed, or weakened.

### Prompt 1 acceptance audit

| Criterion | Status | Evidence |
| --- | --- | --- |
| Manifest, checksum, completion marker, containment models | PASS | Strict schemas and managed-path validation tests. |
| Ordered atomic commit and post-rename event | PASS | File sync, metadata order, rename-failure, and callback-order tests. |
| Loader validation and latest-valid discovery | PASS | Integrity rejection, temp exclusion, newest selection, and corrupted-newest fallback tests. |
| Safe retention | PASS | Direct-child containment and explicit verified-checkpoint protection tests. |
| Complete `safe_full` state | PASS | Model, optimizer, scheduler, step, Python/NumPy/Torch RNG, config, and metadata persisted. |
| Direct restore | PASS | Resumed CI summary exactly equals uninterrupted control; RNG streams restore exactly. |
| Negative security/integrity tests | PASS | Corruption, missing marker, traversal, outside-root containment; symlink escape runs where fixture creation is permitted. |
| Logical-byte and duration metrics | PASS | Measured demo checkpoint: 126,170 bytes; 0.1324288999894634-second commit. |
| Control and safe-full CLI | PASS | Typer runner tests plus installed demo CLI execution. |
| Required quality gates | PASS | Ruff lint, Ruff format check, and pytest output above. |

### Files changed

- `pyproject.toml`;
- `src/flashpilot/cli.py`;
- `src/flashpilot/workload/control.py`;
- `src/flashpilot/workload/trainer.py`;
- `src/flashpilot/domain/__init__.py` and `manifests.py`;
- `src/flashpilot/security/__init__.py` and `paths.py`;
- `src/flashpilot/checkpoints/__init__.py`, `atomic.py`, `integrity.py`,
  `loader.py`, `retention.py`, and `strategies.py`;
- `tests/__init__.py`, `tests/conftest.py`,
  `tests/integration/test_safe_full.py`, and the Prompt 1 unit test modules;
- `docs/architecture.md`, `docs/decisions.md`, `docs/build-log.md`,
  `docs/codex-contributions.md`, and `docs/submission-checklist.md`.

## Milestone 2 — adapter-aware and incomplete recovery fixture

- Date: 2026-07-17
- Objective: implement only the minimal native adapter boundary, immutable-base
  adapter-aware checkpoints, and the valid-but-incomplete continuation fixture.
- Human constraints: Section 28.5 remains binding; Prompt 2 is the only
  authorized milestone; Prompt 0 determinism, Prompt 1 integrity/containment,
  repository-local pytest paths, CPU-only execution, and the Windows durability
  limitation remain unchanged.
- Local validation runtime: Python 3.12.13, PyTorch 2.13.0+cpu, NumPy 2.5.1,
  Windows 11. Python 3.11 remains the project and Ruff compatibility target.
- Pytest ACL note: the first tool-side focused run could not remove an existing
  host-owned `.pytest-local/temp`. The inaccessible ignored tree could not be
  read, reset, or removed by the non-administrator account, so it was moved to
  `C:\tmp\flashpilot-pytest-local-acl-backup-20260717`. Pytest then recreated
  the exact configured repository-local paths. `tests/conftest.py` now creates
  only the ignored `.pytest-local` parent on clean checkouts; `tmp_path`, the
  integration tests, and the configured temp/cache locations are unchanged.
- Measurement correction: the first metrics command evaluated `load_succeeded`
  after the incomplete runtime had already advanced from step 12 to step 24,
  producing a false observation. A fresh run captured the loaded step before
  continuation; the corrected actual result below reports `true` and step 12.

### Measured demo-profile checkpoint structure

The corrected measurement used checkpoint step 12 of 24:

| Quantity | Actual logical bytes |
| --- | ---: |
| `safe_full` checkpoint | 126,218 |
| Frozen-base payload (`base.pt`) | 93,987 |
| Complete immutable base artifact | 94,448 |
| Recurring `safe_adapter_aware` checkpoint | 32,743 |
| First adapter-aware checkpoint including base | 127,191 |

Actual file-byte sums matched the reported logical bytes for both the
126,218-byte full checkpoint and 32,743-byte recurring adapter checkpoint. The
recurring structural reduction is 93,475 bytes (74.0583751921279%). The first
adapter-aware write is 973 bytes larger than `safe_full` because it includes the
one-time base. This is structural accounting only, not a storage-savings or
Recovery Gate verdict.

Actual timing and identity evidence from the corrected run:

```text
safe_full.commit_seconds: 0.1317292999883648
safe_full.restore_seconds: 0.042678199999500066
safe_adapter_aware.base_commit_seconds: 0.035418399987975135
safe_adapter_aware.recurring_commit_seconds: 0.08929259999422356
safe_adapter_aware.restore_seconds: 0.043570100009674206
base_sha256: 9a8da8bdc2b9e7fc6b84c04f83940db56da8fa76c1f8b3c002339eea2a3dbce5
safe_full.direct_restore_matches_control: true
safe_adapter_aware.direct_restore_matches_control: true
```

`missing_training_state` validation and loading both succeeded at global step
12. After real dropout-enabled continuation to step 24, final step still
matched, while loss suffix, trainable-state digest, evaluation digest,
optimizer digest, and scheduler digest all differed from the uninterrupted
control. Its manifest explicitly omitted optimizer, scheduler, Python RNG,
NumPy RNG, and Torch RNG state.

### Final quality-gate output

```text
.\.venv\Scripts\ruff.exe check .
All checks passed!

.\.venv\Scripts\ruff.exe format --check .
40 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................s....                            [100%]
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
44 passed, 1 skipped in 4.71s
```

The platform-conditional symlink test remains enabled and unchanged. Windows
does not permit this non-administrator host to create its fixture. Payload and
metadata files are synchronized and the directory rename is atomic; directory
`fsync` remains unsupported through Python on Windows and is reported as
best-effort.

### Prompt 2 acceptance audit

| Criterion | Status | Evidence |
| --- | --- | --- |
| Minimal `TrainerAdapter` abstraction | PASS | Capability, summary, state partition, and strict restore methods only; no process or repair surface. |
| `NativePyTorchAdapter` only | PASS | Fixed `get_adapter("native-pytorch")`; unsupported names fail. |
| `WorkloadCapabilities` and `SaveRestoreSummary` | PASS | Strict deterministic models and exact strategy summaries. |
| Complete `safe_adapter_aware` | PASS | One immutable base plus recurring adapter, optimizer, scheduler, step, Python/NumPy/Torch RNG, manifest, checksums, and marker. |
| Valid `missing_training_state` | PASS | Checksum validation and direct loading succeed; exact omissions are explicit. |
| Direct restore for each strategy | PASS | Safe adapter-aware matches control exactly; incomplete state loads at step 12. |
| Measured byte comparison | PASS | Actual table and file-byte equality above; no padding or baseline inflation. |
| Missing-base and wrong-hash rejection | PASS | Both fail closed before base tensor deserialization. |
| Incomplete continuation divergence | PASS | Real dropout-enabled continuation differs in loss, trainable, evaluation, optimizer, and scheduler digests. |
| Established-practice positioning | PASS | `docs/research.md` explicitly disclaims invention and limits the result. |
| Required quality gates | PASS | Ruff and pytest output above. |

No Prompt 3 or later functionality was started.

## Milestone 3 — real process crash and deterministic Recovery Gate

- Date: 2026-07-17
- Objective: implement only the real worker/parent crash boundary,
  new-process restore, deterministic Recovery Gate, rollback evidence, and
  sanitized failure package required by Prompt 3.
- Binding scope: Section 28.5 remains authoritative. Prompt 0 determinism,
  Prompt 1 integrity/containment/retention, Prompt 2 strategies and byte
  measurements, one native adapter, project-local pytest paths, and the Windows
  durability limitation are preserved.
- Local runtime: Python 3.12.13, PyTorch 2.13.0+cpu, NumPy 2.5.1, Windows 11.
  Python 3.11 remains the project compatibility target.

### Windows process-launch correction

The first two real smoke attempts failed closed before an accepted crash because
the Windows console-script/venv redirector PID differed from the Python PID in
the worker event:

```text
flashpilot.orchestration.experiment.OrchestrationError:
checkpoint event PID does not match the child process
```

The parent cleaned up both processes and did not accept either event. Worker
commands now launch `sys._base_executable` directly on Windows and explicitly
provide the active venv site-packages and project source paths. The next run
recorded the same PID from `Popen` and the worker event, killed that actual
process, and passed the gate.

### Preserved demo-profile process runs

All runs used checkpoint step 12 of 24 and a hard rollback limit of zero:

| Strategy | Original PID | Checkpoint path | Termination | Exit | Recovery PID | Recovery exit | Recovery seconds | Gate | Rollback |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| `safe_full` | 6028 | `checkpoints/checkpoint-step-000012` | `TerminateProcess via subprocess.Popen.kill` | 1 | 6928 | 0 | 3.929737 | VERIFIED | 0 |
| `safe_adapter_aware` | 2124 | `checkpoints/safe-adapter-aware/checkpoint-step-000012` | `TerminateProcess via subprocess.Popen.kill` | 1 | 30804 | 0 | 3.874549 | VERIFIED | 0 |
| `missing_training_state` | 19200 | `checkpoints/missing-training-state/checkpoint-step-000012` | `TerminateProcess via subprocess.Popen.kill` | 1 | 32532 | 0 | 4.004130 | FAILED | 0 |

Both safe strategies passed every applicable gate check and exactly matched the
uninterrupted demo control after new-process continuation. The incomplete
checkpoint remained manifest-valid, checksum-valid, loadable, and able to
continue from batch step 12 to completed step 13 and final step 24. It failed
these nine checks:

```text
state.optimizer
state.scheduler
state.python_rng
state.numpy_rng
state.torch_rng
trajectory.final_trainable
trajectory.final_evaluation
trajectory.loss_history
contract.no_mandatory_omission
```

Integrity, checkpoint evaluation, process termination, distinct recovery PID,
expected next step, containment, and zero-step rollback all passed for that red
run.

### Comparison and sanitization policy

Cross-process CI and demo evidence supported exact equality. The gate uses:

```text
trainable parameters: exact SHA-256
fixed evaluation logits: exact SHA-256
optimizer state: exact SHA-256
scheduler state: exact SHA-256
Python / NumPy / Torch RNG: exact SHA-256 per state
loss history: exact float-sequence equality
atol: 0.0
rtol: 0.0
```

No nonzero tolerance was required or introduced. A real rollback negative run
completed two steps beyond its checkpoint, set a one-step hard limit, recovered
correctly, and failed only `rollback.hard_limit` with achieved rollback 2.

The failed demo wrote `agent/request.redacted.json`. Direct inspection and the
runtime/test guard reported all of the following as false:

```text
underscore failure label present: false
hyphenated failure label present: false
expected diagnosis language present: false
repair preset language present: false
injection label language present: false
absolute home path present: false
```

The package contains observed manifest, restore, gate, state-difference,
trajectory, integrity, crash, and stable evidence-ID data only. Prompt 3 does
not send it to GPT or any external service.

### Negative process evidence

- One-byte corruption of `optimizer.pt` made the new recovery worker exit 2 on
  checksum mismatch before tensor deserialization. No failure-analysis package
  or repair scenario was created.
- Removing the immutable base made adapter recovery exit 2 during base
  validation before deserialization.
- An unrelated incomplete temporary checkpoint directory remained present and
  was ignored while the committed safe-full checkpoint recovered successfully.
- A worker that exited 2 before emitting its required event was rejected with
  the actual exit code; the parent did not accept a crash event.
- The existing Windows symlink test remains enabled and conditionally skipped
  only because the non-administrator host cannot create its fixture.

### Actual test output before the documentation-only final rerun

```text
.\.venv\Scripts\python.exe -m pytest -q tests\unit\test_failure_artifact.py tests\integration\test_crash_recovery.py
................                                                         [100%]
16 passed in 48.23s

.\.venv\Scripts\python.exe -m pytest -q
........................................................s....            [100%]
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
60 passed, 1 skipped in 54.23s
```

### Prompt 3 acceptance audit

Final post-documentation quality gates:

```text
.\.venv\Scripts\ruff.exe check .
All checks passed!

.\.venv\Scripts\ruff.exe format --check .
52 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................s....            [100%]
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
60 passed, 1 skipped in 56.95s
```

| Criterion | Status | Evidence |
| --- | --- | --- |
| Worker subprocess entry point | PASS | Trusted argument-array `python -m flashpilot.orchestration.worker` checkpoint/recover modes. |
| Parent orchestrator | PASS | Starts, observes, validates, terminates, relaunches, gates, and persists results. |
| Machine-readable committed event | PASS | One strict JSON event created only after the post-rename callback. |
| Parent validation before kill | PASS | PID, contained relative path, manifest, checksum, step, and strategy checks precede `Popen.kill`. |
| Expected termination verification | PASS | Actual Windows exit 1 verified after `TerminateProcess`. |
| New-process restore | PASS | Recovery PID is recorded, distinct, and exits 0. |
| Continue to control final step | PASS | Both safe demo runs reach step 24 and exactly equal control. |
| All mandatory Recovery Gate checks | PASS | Twenty mandatory plus four explicit process checks retained individually and grouped in console output. |
| Structured evidence and redacted package | PASS | Stable evidence IDs and guarded `agent/request.redacted.json`. |
| Achieved rollback calculation | PASS | Normal demo 0; real negative observation 2 exceeds hard limit 1. |
| Initial red demo plumbing | PASS | Valid incomplete checkpoint loads, continues, and deterministically fails nine checks. |
| Corrupted optimizer fail-closed | PASS | Checksum rejection before load; no policy/repair artifact. |
| Platform support notes | PASS | Windows launcher and directory-fsync limitations explicitly recorded. |
| Required integration negatives | PASS | Corruption, incomplete temp, missing base, rollback violation, and unexpected exit covered. |
| Exact/tolerance policy | PASS | Exact cross-process equality; `atol=rtol=0`; no nonzero tolerances. |
| Prompt 4 exclusion | PASS | No GPT provider, contract inference, diagnosis, repair, HTML, or packaging. |

No Prompt 4 or later functionality was started.

## Milestone 4 — GPT-5.6 contract and blind failure analyst

- Date: 2026-07-17
- Objective: implement exactly the checkpoint-contract and blind
  failure-diagnosis roles with typed bounded repair proposals, live and fixture
  providers, deterministic guardrails, and no repair execution.
- Binding scope: Section 28.5 remains authoritative. Prompt 0 determinism,
  Prompt 1 integrity and containment, Prompt 2 strategies, Prompt 3 process
  proof and exact Recovery Gate, one native adapter, and project-local pytest
  paths remain unchanged.
- Local runtime: Python 3.12.13, OpenAI Python SDK 2.46.0, PyTorch 2.13.0+cpu,
  NumPy 2.5.1, Windows 11. Python 3.11 remains the compatibility target.
- `OPENAI_API_KEY` availability check: `false`. No live call was attempted and
  no live result is claimed. One live contract call and one live diagnosis call
  remain an explicit manual task.
- The official Docs MCP was not available in the session. The required
  `codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp`
  attempt was denied by the host, so implementation verification used the
  official OpenAI structured-output, Responses API, and GPT-5.6 model pages.
- Local SDK inspection confirmed `OpenAI().responses.parse` supports
  `text_format` and `store`. Strict-schema generation succeeded for both
  Pydantic output models (`CheckpointContract`: 1,768 JSON-schema bytes;
  `FailureAnalysis`: 2,456 JSON-schema bytes).

### Provider and fixture evidence

Both live providers call `responses.parse` with:

```text
model="gpt-5.6"
text_format=<role-specific Pydantic model>
store=False
tools omitted
```

Recording-SDK tests assert those exact arguments. The fixture providers use
the same typed interfaces and persist labels:

```text
provider: fixture
live_or_fixture: fixture
fixture_provenance: deterministic_local_fixture
model: gpt-5.6
store: false
```

The provenance is intentionally not `live_gpt_5_6_capture`: the committed
fixtures are deterministic local Prompt 4 fixtures because no API key was
available. They must be replaced or supplemented only after real live calls.

Fixture replay against the preserved Prompt 3 red artifact produced:

```text
contract required state:
  adapter, optimizer, scheduler, global_step,
  python_rng, numpy_rng, torch_rng, base_model_identity
contract integrity controls:
  manifest, checksums, completion_marker, atomic_commit, base_artifact_hash
failure confidence: high
accepted actions:
  persist_optimizer_state
  persist_scheduler_state
  persist_python_rng_state
  persist_numpy_rng_state
  persist_torch_rng_state
  restore_state_before_next_batch
rejected actions: none
unsupported actions: none
execution_performed: false
```

A separate deterministic classification probe reported:

```text
accepted: persist_optimizer_state
unsupported: persist_sampler_state
rejected: duplicate persist_optimizer_state
rejected: command-bearing persist_scheduler_state
attempt_number: 1
execution_performed: false
```

This proves known public actions remain parseable but are explicitly
unsupported when they are outside the six native capabilities. It does not
apply a repair.

### Sanitized API boundary

The recording-SDK test inspects the complete system-plus-user input supplied to
the live failure provider. Direct inspection of the preserved fixture request
reported:

```text
missing_training_state: False
missing-training-state: False
inject_failure: False
failure_injection: False
expected_diagnosis: False
repair_preset: False
```

Additional guards reject absolute local paths, URLs, secret-like values, API
key fields, command and patch text, raw tensor/weight fields, dataset/sample
fields, and raw numeric arrays. Model-output validation rejects tolerance
changes, disabled checks, recovery-verification claims, corruption-repair
claims, unknown evidence, duplicates, and unsafe action text.

### Pytest ACL observation

The first focused run reached 28 passing tests but four `tmp_path` fixture
setups failed because an existing ignored `.pytest-local` tree had ACLs from a
different execution principal. The source resolved exactly to the configured
repository path. A sandboxed move was denied; an approved host move preserved
it at:

```text
C:\tmp\flashpilot-pytest-local-acl-backup-prompt4-20260717
```

Pytest recreated the unchanged `.pytest-local/temp` and `.pytest-local/cache`
paths under the current account. No test, fixture, or pytest configuration was
disabled or weakened.

### Actual test output

Focused provider and guardrail run after the ACL correction:

```text
.\.venv\Scripts\python.exe -m pytest -q tests\unit\test_agent_providers.py tests\unit\test_agent_guardrails.py
................................                                         [100%]
32 passed in 1.34s
```

Expanded Prompt 4 and affected-boundary run:

```text
.\.venv\Scripts\python.exe -m pytest -q tests\unit\test_agent_providers.py tests\unit\test_agent_guardrails.py tests\unit\test_failure_artifact.py tests\unit\test_adapters.py
.........................................................                [100%]
57 passed in 1.38s
```

Final quality gates:

```text
.\.venv\Scripts\ruff.exe check .
All checks passed!

.\.venv\Scripts\ruff.exe format --check .
62 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 68%]
............................s....                                        [100%]
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
104 passed, 1 skipped in 53.45s
```

The platform-conditional Windows symlink test remains enabled and unchanged.

### Prompt 4 acceptance audit

| Criterion | Status | Evidence |
| --- | --- | --- |
| Exactly two GPT-5.6 roles | PASS | Contract inference and blind failure analysis only. |
| Official SDK and Responses API | PASS | `responses.parse` is used by both live providers. |
| Exact model and storage policy | PASS | `model="gpt-5.6"`, `store=False`, asserted by recording SDK tests. |
| Structured outputs | PASS | Strict Pydantic contract and analysis schemas; local strict-schema conversion succeeds. |
| Live and labeled fixture providers | PASS | Two live and two deterministic-local fixture providers share typed protocols. |
| Native capability scope | PASS | Exactly the six Section 28.5 actions are advertised. |
| Known unsupported action reporting | PASS | Public enum remains complete; non-native actions receive `unsupported`. |
| Sanitized failure boundary | PASS | Complete mocked API input and persisted request pass all forbidden-string guards. |
| No commands, patches, paths, URLs, secrets, raw data, or tolerance changes | PASS | Input/output guards and negative tests cover each category. |
| GPT cannot declare or perform recovery | PASS | No tools or executor; verification and corruption-repair claims are rejected. |
| Deterministic contract validation | PASS | Rollback, mandatory state, integrity minimum, and capability gaps are enforced. |
| Deterministic repair-plan validation | PASS | Allowlist, native capability, evidence, duplicate/conflict, and safety decisions are recorded. |
| One-attempt limit | PASS | Exclusive attempt-one admission rejects a second admission and records no execution. |
| Secret-free metadata persistence | PASS | Request hash, provider, model, versions, timestamp, source, response ID, and `store` are persisted. |
| Live validation | OUTSTANDING | `OPENAI_API_KEY` was unavailable; no live output was invented. |
| Prompt 5 exclusion | PASS | No repair execution, repaired strategy, second crash, or red-to-green orchestration. |

No Prompt 5 or later functionality was started.

## Post-Prompt 4 pytest cross-context ACL correction

- Date: 2026-07-17
- Scope: pytest infrastructure only; Prompt 5 remains unstarted.
- Independent host-user verification using a unique `%TEMP%` basetemp and a
  disabled cache provider passed the full suite twice with 104 passed and the
  one expected Windows symlink skip. The focused agent suite passed 40 tests.
- Root cause: fixed `.pytest-local/temp` and `.pytest-local/cache` directories
  were shared by normal host-user and sandbox security contexts. Whichever
  principal created or recreated the directories could leave ACLs that blocked
  the other principal before `tmp_path` fixture setup. Product test bodies were
  not responsible for those failures.
- Failed approach: keeping fixed repository-local temp/cache paths and moving
  or recreating their shared parent only transferred the immediate ownership
  problem. It did not provide cross-security-context isolation.
- Permanent correction: remove `--basetemp=.pytest-local/temp`, remove
  `cache_dir=.pytest-local/cache`, remove the pytest startup hook that created
  `.pytest-local`, allow pytest to use its normal unique per-user/per-invocation
  operating-system temporary directory, and disable cacheprovider with
  `-p no:cacheprovider` because cache state is not required for correctness.
- No product test, skip condition, xfail, tolerance, or Recovery Gate check was
  changed.

Final default-command output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
62 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 68%]
............................s....                                        [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
104 passed, 1 skipped in 55.04s
```

Focused agent output using the requested PowerShell continuation syntax:

```text
.\.venv\Scripts\python.exe -m pytest `
  .\tests\unit\test_agent_providers.py `
  .\tests\unit\test_agent_guardrails.py `
  -q
........................................                                 [100%]
40 passed in 1.31s
```

The final output contains no ACL failure and no unknown `cache_dir` option
warning. Prompt 5 was not started.

## Prompt 4 live-validation entry point

- Date: 2026-07-17
- Scope: the outstanding live-validation path only; Prompt 5 remains
  unstarted.
- Existing inspection result: the OpenAI contract and failure providers,
  strict Pydantic schemas, Responses API structured parsing, `gpt-5.6`,
  `store=False`, no-tools behavior, and deterministic guardrails already
  existed. There was no supported live CLI entry point.
- Added `live-contract` and `live-failure` commands. Each command admits one
  live provider call and requires a new role-specific output directory. The
  failure command has no input-file option and reads only
  `runs/manual-prompt3-incomplete/agent/request.redacted.json`.
- Live metadata now requires a nonempty response ID and records
  `source=captured_live_response`. Fixture metadata remains explicitly
  labeled and cannot validate as captured live output.
- The preserved failure request passed the existing sanitizer unchanged. Its
  canonical redacted-request SHA-256 is
  `eaa6f7818ecdaf482525081514dccfbfe748ae79b0d17c1a719a5e60bfc5ba2e`.
- `OPENAI_API_KEY` availability was `false` in the validation environment. No
  live call was attempted, no live response or response ID is claimed, and no
  model output was invented or edited.

Exact live commands from the repository root, after setting the API key in the
process environment without printing it:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli live-contract `
  --run-dir .\runs\manual-prompt4-live-contract

.\.venv\Scripts\python.exe -m flashpilot.cli live-failure `
  --run-dir .\runs\manual-prompt4-live-failure
```

Actual focused entry-point, provider, and guardrail output:

```text
.\.venv\Scripts\python.exe -m pytest .\tests\unit\test_agent_providers.py .\tests\unit\test_agent_guardrails.py .\tests\unit\test_live_cli.py -q
...........................................                              [100%]
43 passed in 1.73s
```

Final quality-gate output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
63 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 66%]
...............................s....                                     [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
107 passed, 1 skipped in 62.75s (0:01:02)
```

The live commands do not execute a repair or launch another crash. Prompt 5
was not started.

## Prompt 4 strict-ID, rejection-audit, and pytest-isolation correction

- Date: 2026-07-17
- Scope: Prompt 4 corrections only. No live API call was made during this
  correction and Prompt 5 remains unstarted.

### Independent live results carried into the correction

The independently captured checkpoint-contract call was accepted with:

```text
provider=openai
model=gpt-5.6
source=captured_live_response
store=false
response_id=<nonempty>
```

All deterministic contract guardrails passed. The first live
failure-analysis call reached GPT-5.6 and produced a parsed response, but the
model combined a Gate check ID and evidence ID in values such as:

```text
state.optimizer [restore:optimizer-state]
```

The exact deterministic rejection category was:

```text
failure analysis references unknown gate checks
```

The valid Gate ID is `state.optimizer`; `restore:optimizer-state` is a separate
evidence ID. The guardrail correctly failed closed. The pre-correction service
validated before writing artifacts, so that rejected response was not
persisted. One failure-analysis retry is required after this correction:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli live-failure --run-dir .\runs\manual-prompt4-live-failure-retry
```

This retry was documented but not executed by Codex.

### Corrections

- Failure-analysis schema v2 uses exact `Literal` values for all 24 supported
  Recovery Gate check IDs and all 24 supported evidence IDs. Gate IDs,
  confirming evidence IDs, and per-action evidence IDs remain separate fields.
- Failure prompt v2 requires exact identifiers copied from failed
  `gate_checks` and `evidence_catalog` and forbids concatenating, annotating,
  wrapping, splitting, trimming, or rewriting them.
- There is no normalization or repair path. The malformed combined identifier
  fails Pydantic validation, and a constructed malformed provider result still
  fails the deterministic unknown-check guard.
- Deterministically rejected parsed output is preserved unchanged at
  `agent/failure/response.parsed.rejected.json`, with the redacted request,
  `metadata.json`, and `validation.rejected.json` written before the guardrail
  exception is re-raised. Metadata includes `validation_status=rejected`.
- No action capability, allowlist, tolerance, Recovery Gate check, redaction
  boundary, test skip, or xfail was changed.

### Both Windows ACL collision mechanisms

1. Fixed repository-local `.pytest-local/temp` and `.pytest-local/cache`
   directories collided when host-user and sandbox principals shared the
   checkout.
2. Pytest's normal `%TEMP%/pytest-of-<username>` parent also collided because
   the predictable parent was shared across those security contexts.

The project now explicitly loads `flashpilot.pytest_plugin`, which assigns a
fresh `flashpilot-pytest-<uuid4 hex>` direct child of
`tempfile.gettempdir()` before `TempPathFactory` is initialized. It preserves a
caller-supplied `--basetemp`; the cache provider remains disabled. No username,
home path, fixed repository path, PID-only identifier, administrator access,
`icacls`, or `takeown` is used.

Actual default-command output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
65 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 62%]
...................................s.......                              [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314]
114 passed, 1 skipped in 58.61s
```

The default run's platform-skip path used the UUID root
`flashpilot-pytest-a04093977927411cb2bebf5030b9b48b`. A direct default-config
probe produced a separate UUID root and passed:

```text
FLASHPILOT_BASETEMP=<system temp>\flashpilot-pytest-bb10f4f059b1423cba93e49a5b2c833a
1 passed in 0.02s
```

Focused agent and live-CLI output:

```text
.\.venv\Scripts\python.exe -m pytest .\tests\unit\test_agent_providers.py .\tests\unit\test_agent_guardrails.py .\tests\unit\test_live_cli.py -q
...............................................                          [100%]
47 passed in 1.28s
```

Focused pytest-plugin output:

```text
.\.venv\Scripts\python.exe -m pytest .\tests\unit\test_pytest_plugin.py -q
...                                                                      [100%]
3 passed in 8.20s
```

No live API call, repair, second crash, or Prompt 5 functionality was executed
or added.

## Prompt 5 bounded repair and second verification

- Date: 2026-07-17
- Scope: Prompt 5 only; Prompt 6 was not started.
- Target: Python 3.11+ compatibility; local validation used Python 3.12.13 on
  Windows.
- Provider mode: fixture replay of the independently accepted, secret-free
  GPT-5.6 structured response. No live API call was made.

### Implementation evidence

The checked-in contract and failure fixtures now match the independently
accepted live structured outputs. Their sidecars preserve the accepted live
metadata, including response IDs. Runtime replay metadata remains separately
labeled `provider=fixture`, `live_or_fixture=fixture`, and
`source=captured_live_response_replay`.

The bounded executor copied a strict `CheckpointStrategyConfig`, admitted
attempt one, assigned `native-repaired-complete-v1`, and set exactly:

```text
include_optimizer=true
include_scheduler=true
include_python_rng=true
include_numpy_rng=true
include_torch_rng=true
restore_before_next_batch=true
```

It applied only:

```text
persist_optimizer_state
persist_scheduler_state
persist_python_rng_state
persist_numpy_rng_state
persist_torch_rng_state
restore_state_before_next_batch
```

`change_supported_checkpoint_strategy` remained recorded as unsupported and
was not executed. Rejected actions were empty. A second repair admission was
refused in both unit and end-to-end integration coverage.

The captured live request hash and fresh replay request hash differ because a
real rerun has different process IDs and the current native capability summary
advertises the six supported actions. Both hashes are recorded separately. No
claim is made that the current request bytes were sent to GPT-5.6; the accepted
response is a semantic structured replay that passed all current deterministic
guardrails before the executor admitted it.

### Focused tests

```text
.\.venv\Scripts\python.exe -m pytest tests\unit\test_agent_providers.py tests\unit\test_agent_guardrails.py tests\unit\test_repair_executor.py -q
.................................................                        [100%]
49 passed in 1.65s

.\.venv\Scripts\python.exe -m pytest tests\integration\test_repair_loop.py -q
.....                                                                    [100%]
5 passed in 20.30s
```

### Clean demo-profile fixture replay

Command:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile demo --run-dir .\runs\manual-prompt5-fixture-20260717
```

Actual output:

```text
The failure is intentional and deterministic, but GPT-5.6 does not receive the injection label. It receives only the sanitized checkpoint manifest, restore behavior, failed Recovery Gate checks, and trajectory evidence.
Initial worker PID: 12360
Initial recovery PID: 13356
Initial failed checks: state.optimizer, state.scheduler, state.python_rng, state.numpy_rng, state.torch_rng, trajectory.final_trainable, trajectory.final_evaluation, trajectory.loss_history, contract.no_mandatory_omission
Applied actions: persist_optimizer_state, persist_scheduler_state, persist_python_rng_state, persist_numpy_rng_state, persist_torch_rng_state, restore_state_before_next_batch
Unsupported actions: change_supported_checkpoint_strategy
Repaired strategy ID: native-repaired-complete-v1
Second worker PID: 42748
Second recovery PID: 8556
Final Recovery Gate: VERIFIED
Result: C:\Programming\business\flashpilot\runs\manual-prompt5-fixture-20260717\result.json
Report: C:\Programming\business\flashpilot\runs\manual-prompt5-fixture-20260717\report.md
```

The initial gate failed exactly the nine checks shown above. The final gate
passed with no failed checks, and the comparison policy remained `atol=0.0`,
`rtol=0.0`. The initial checkpoint fingerprint before and after repair was:

```text
c78f9fcd39a57960268cd354521dddf3751f974b974791adefd5a143dfe696ce
```

Therefore the historical failed checkpoint was not modified. Repair attempt
count was exactly one. The captured failure response ID was
`resp_0d7e808cd722f97f016a5a90f0300481908d22e7befa15e3fe`.

Only after the final gate passed, the unchanged measurement paths reported:

```text
safe_full logical checkpoint bytes: 126218
repaired recurring logical checkpoint bytes: 32743
one-time immutable base bytes: 93987
structural recurring-byte reduction: 93475 bytes (74.0583751921279%)
```

This is a same-profile, same-step logical checkpoint-directory comparison. The
repaired recurring number excludes the immutable base stored once. It is not a
physical NAND-write, write-amplification, or SSD-lifetime measurement.

Read-only artifact commands also passed:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli audit --run-dir .\runs\manual-prompt5-fixture-20260717
Fixture replay source: captured_live_response_replay
Captured response ID: resp_0d7e808cd722f97f016a5a90f0300481908d22e7befa15e3fe
Repair attempts: 1
Original checkpoint unmodified: True
Final Recovery Gate: VERIFIED

.\.venv\Scripts\python.exe -m flashpilot.cli verify --run-dir .\runs\manual-prompt5-fixture-20260717
VERIFIED by the persisted deterministic Recovery Gate (atol=0.0, rtol=0.0).

.\.venv\Scripts\python.exe -m flashpilot.cli replay --run-dir .\runs\manual-prompt5-fixture-20260717
Captured GPT-5.6 structured response replay matched; no API call was made.
```

### Final quality gates

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
71 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 58%]
.........................................s..........                     [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Клиент не обладает требуемыми правами: 'C:\Users\cimpal55\AppData\Local\Temp\flashpilot-pytest-4e08ea4efdea49a08a636ecab2305a76\test_sandbox_rejects_symlink_e0\outside' -> 'C:\Users\cimpal55\AppData\Local\Temp\flashpilot-pytest-4e08ea4efdea49a08a636ecab2305a76\test_sandbox_rejects_symlink_e0\run\escape'
123 passed, 1 skipped in 74.98s (0:01:14)
```

The skip is the unchanged platform-conditional Windows directory-symlink test.
Pytest used its unique UUID temp root and had no ACL or cache warning. Windows
payload and metadata file fsync and atomic directory rename remain enforced;
directory fsync remains explicitly best-effort.

## Prompt 6 judge experience and wheel qualification

- Date: 2026-07-18
- Scope: Prompt 6 only. Prompt 7 and Prompt 8 were not started.
- Verified environment: Windows 11, Python 3.12.13, PyTorch 2.13.0 CPU.
- Primary command: `flashpilot demo --provider fixture`.
- No live API call was made.

### Product path

The installed command now prints a unique full-UUID run path before execution
and renders these result-derived Rich stages:

```text
Uninterrupted control                              PASS
Initial checkpoint                                 PASS
First real process termination                    PASS
Initial Recovery Gate                             FAIL
GPT-5.6 captured-response fixture/replay diagnosis GPT RECOMMENDATION
Deterministic bounded repair                       GUARDRAIL ACCEPTED
Second real process termination                   PASS
Final Recovery Gate                               VERIFIED
Verified storage comparison                       VERIFIED
```

The decision table marks `change_supported_checkpoint_strategy` UNSUPPORTED and
the exact six native actions GUARDRAIL ACCEPTED. The storage headline is emitted
only after the final gate passes. `report.html` is self-contained, has no
external asset, and is rendered from the persisted `result.json`.

### Wheel build

Command:

```text
.\.venv\Scripts\python.exe -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

Actual final output:

```text
Processing c:\programming\business\flashpilot
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: flashpilot
  Building wheel for flashpilot (pyproject.toml): started
  Building wheel for flashpilot (pyproject.toml): finished with status 'done'
  Created wheel for flashpilot: filename=flashpilot-0.1.0-py3-none-any.whl size=85846 sha256=d8462a963f005096756fcaca8832319abb8cdbbbf9b784d18bb9c3175c6e3bfd
Successfully built flashpilot
```

Wheel evidence:

```text
path: C:\Programming\business\flashpilot\dist\flashpilot-0.1.0-py3-none-any.whl
size: 85846 bytes
SHA-256: D8462A963F005096756FCACA8832319ABB8CDBBBF9B784D18BB9C3175C6E3BFD
```

Wheel inspection confirmed that all product modules and these four installed
data files are present:

```text
share/flashpilot/fixtures/contract_fixture.json
share/flashpilot/fixtures/contract_fixture.metadata.json
share/flashpilot/fixtures/failure_analysis_fixture.json
share/flashpilot/fixtures/failure_analysis_fixture.metadata.json
```

### Fresh clean installation

The final environment was newly created as a standard virtual environment; it
did not use `--system-site-packages`:

```text
.\.venv\Scripts\python.exe -m venv C:\tmp\flashpilot-prompt6-clean-final-20260718
C:\tmp\flashpilot-prompt6-clean-final-20260718\Scripts\python.exe -m pip install .\dist\flashpilot-0.1.0-py3-none-any.whl
```

Actual installation conclusion:

```text
Processing c:\programming\business\flashpilot\dist\flashpilot-0.1.0-py3-none-any.whl
Installing collected packages: mpmath, typing-extensions, sympy, sniffio, shellingham, setuptools, pygments, numpy, networkx, mdurl, MarkupSafe, jiter, idna, h11, fsspec, filelock, distro, colorama, certifi, annotated-types, annotated-doc, typing-inspection, tqdm, pydantic-core, markdown-it-py, jinja2, httpcore, anyio, torch, rich, pydantic, httpx, typer, openai, flashpilot
Successfully installed MarkupSafe-3.0.3 annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.14.2 certifi-2026.6.17 colorama-0.4.6 distro-1.9.0 filelock-3.31.0 flashpilot-0.1.0 fsspec-2026.6.0 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.18 jinja2-3.1.6 jiter-0.16.0 markdown-it-py-4.2.0 mdurl-0.1.2 mpmath-1.3.0 networkx-3.6.1 numpy-2.5.1 openai-2.46.0 pydantic-2.13.4 pydantic-core-2.46.4 pygments-2.20.0 rich-14.3.4 setuptools-83.0.0 shellingham-1.5.4 sniffio-1.3.1 sympy-1.14.0 torch-2.13.0 tqdm-4.69.0 typer-0.27.0 typing-extensions-4.16.0 typing-inspection-0.4.2
```

Dependency installation used the configured pip package source/cache. The
installed application commands below made no API call, package-index request,
model download, or dataset download.

Clean environment metadata:

```text
Python 3.12.13
Name: flashpilot
Version: 0.1.0
Summary: Checkpoint recovery qualification and verification harness
Location: C:\tmp\flashpilot-prompt6-clean-final-20260718\Lib\site-packages
Requires: numpy, openai, pydantic, rich, torch, typer
```

### Installed doctor outside the repository

Working directory:

```text
C:\tmp\flashpilot-prompt6-work-final-20260718
```

Judge command and actual outcome:

```text
flashpilot doctor

Python version             PASS        3.12.13
OS / platform              INFO        Windows-11-10.0.26200-SP0
CPU execution              PASS        Torch CPU tensor execution available
Required dependencies      PASS        numpy, openai, pydantic, rich, torch, typer
Captured-response fixtures PASS        installed wheel data available
Writable output location   PASS        outside-repository runs directory
OPENAI_API_KEY             INFO        Not present (not required by fixture demo)
Directory fsync            LIMITATION  unavailable through Python on Windows
Doctor verdict             PASS
```

The doctor printed only API-key presence and never a value.

### Installed primary demo outside the repository

Exact judge command:

```text
flashpilot demo --provider fixture
```

Actual final outcome:

```text
Generated run path: C:\tmp\flashpilot-prompt6-work-final-20260718\runs\repair-42b022b330a148a8ae77e01edbcd4a2d
GPT source: GPT-5.6 captured-response fixture/replay
Initial checkpoint: step 12; worker PID 26504; recovery PID 17312
Initial Recovery Gate: FAIL (9 exact failures)
change_supported_checkpoint_strategy: UNSUPPORTED
Six native repair actions: GUARDRAIL ACCEPTED
Repaired run: worker PID 21380; recovery PID 22676
Final Recovery Gate: VERIFIED (24/24, atol=0.0, rtol=0.0)
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base cost: 93987
recurring logical-byte reduction: 93475 bytes (74.06%)
Internal workflow runtime: 16.75 seconds
Total installed-command runtime: 20.41 seconds
```

Visible disclaimer:

```text
Logical checkpoint bytes were measured in the controlled demo. Physical NAND writes, write amplification, and SSD lifetime were not measured.
```

Generated top-level artifacts:

```text
result.json
report.md
report.html
agent/
initial/
repaired/
measurements/
```

The subtrees retain redacted agent evidence, repair admission/execution,
immutable base artifacts, both committed checkpoints, worker logs and recovery
results, safe-full measurement payloads, and storage comparison evidence.

Installed read-only commands also passed against that run:

```text
flashpilot audit --run-dir .\runs\repair-42b022b330a148a8ae77e01edbcd4a2d
Final Recovery Gate: VERIFIED
flashpilot verify --run-dir .\runs\repair-42b022b330a148a8ae77e01edbcd4a2d
VERIFIED by the persisted deterministic Recovery Gate (atol=0.0, rtol=0.0).
flashpilot replay --run-dir .\runs\repair-42b022b330a148a8ae77e01edbcd4a2d
Captured GPT-5.6 structured response replay matched; no API call was made.
```

A recursive artifact scan found no `OPENAI_API_KEY` or `sk-...` material.
`report.html` was 8316 bytes and contained no HTTP/HTTPS external reference.

### Installed-wheel defect found and corrected

The first clean-wheel run completed the recovery workflow and generated its
artifacts, but Rich failed while rendering a decorative Unicode arrow through a
CP1251 Windows console. The arrow was removed, the tables were narrowed for an
80-column console, focused tests passed, the wheel was rebuilt, and the entire
fresh-install/outside-repository path above then passed. No recovery or gate
logic was involved in that presentation-only failure.

### Final quality gates

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
76 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 56%]
.............................................s..........                 [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Клиент не обладает требуемыми правами
127 passed, 1 skipped in 86.77s (0:01:26)
```

The skip is the unchanged Windows platform-conditional directory-symlink test.
Pytest used a unique UUID basetemp with no ACL or cache warning. No test,
tolerance, guardrail, repair limit, redaction boundary, or Recovery Gate check
was weakened.

## Prompt 8 final audit and submission package

- Date: 2026-07-18
- Scope: Prompt 8 only. Optional Prompt 7 was intentionally skipped.
- Environment: Windows 11, repository Python 3.12.13, clean-wheel Python 3.12.13.
- Live API calls: none.

### Audit findings and correction

The repository began clean at committed Prompt 6 revision `ad0bf86`. The audit
confirmed the accepted GPT-5.6 contract and failure captures were unchanged,
the live providers still use `responses.parse`, `model="gpt-5.6"`, Pydantic
structured output, `store=False`, and no tools, and the judge path remained a
clearly labeled captured-response fixture replay.

The audit found one release-documentation gap: `report.md` did not include the
mandatory logical-versus-physical measurement disclaimer already present in the
Rich and HTML presentations. The deterministic Markdown renderer now labels the
safe-full value as recurring logical bytes and always includes:

```text
Logical checkpoint bytes were measured in the controlled demo. Physical NAND writes, write amplification, and SSD lifetime were not measured.
```

A focused assertion now proves Markdown contains all four result-derived byte
values and the exact disclaimer. No checkpoint, process, agent, repair, gate,
tolerance, containment, redaction, skip, or xfail behavior changed.

Focused correction verification:

```text
.\.venv\Scripts\python.exe -m pytest tests\integration\test_repair_loop.py -q
......                                                                   [100%]
6 passed in 23.84s
```

Prompt 8 also finalized the README, a 372-word English voiceover, Devpost-ready
English copy, the submission checklist, the release checklist, the canonical
`result.json` clarification, engineering decisions, and concrete Codex
contributions. No redundant `report.json` was created.

### Final wheel

Because the Markdown renderer is packaged code, the wheel was rebuilt with:

```text
.\.venv\Scripts\python.exe -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

Actual build conclusion:

```text
Created wheel for flashpilot: filename=flashpilot-0.1.0-py3-none-any.whl size=85926 sha256=95450c4e0d67f533f5543ad8a1363135aa188761f77f3644beeaa905ad497502
Successfully built flashpilot
```

Final artifact:

```text
path: C:\Programming\business\flashpilot\dist\flashpilot-0.1.0-py3-none-any.whl
size: 85926 bytes
SHA-256: 95450C4E0D67F533F5543AD8A1363135AA188761F77F3644BEEAA905AD497502
```

The previously accepted Prompt 6 wheel was preserved outside the repository at
`C:\tmp\flashpilot-0.1.0-prompt6-accepted-D8462A963F005096.whl`; it is not a
submission artifact.

### Fresh clean installation

A new standard virtual environment was created without
`--system-site-packages`:

```text
.\.venv\Scripts\python.exe -m venv C:\tmp\flashpilot-prompt8-clean-final-20260718
C:\tmp\flashpilot-prompt8-clean-final-20260718\Scripts\python.exe -m pip install .\dist\flashpilot-0.1.0-py3-none-any.whl
```

Installation completed successfully using cached dependency distributions and
installed `flashpilot-0.1.0` with the declared dependency set. This is not an
offline dependency-installation claim. The application commands below made no
API or network call.

### Final clean installed judge path

Working directory:

```text
C:\tmp\flashpilot-prompt8-work-final-20260718
```

Doctor command and result:

```text
flashpilot doctor
Python version             PASS        3.12.13
OS / platform              INFO        Windows-11-10.0.26200-SP0
CPU execution              PASS        Torch CPU tensor execution available
Required dependencies      PASS        numpy, openai, pydantic, rich, torch, typer
Captured-response fixtures PASS        installed wheel data available
Writable output location   PASS        outside-repository runs directory
OPENAI_API_KEY             INFO        Not present (not required by fixture demo)
Directory fsync            LIMITATION  unavailable through Python on Windows
Doctor verdict             PASS
```

Exact judge command:

```text
flashpilot demo --provider fixture
```

Actual clean installed outcome:

```text
Generated run path: C:\tmp\flashpilot-prompt8-work-final-20260718\runs\repair-f2a124b0a506422cad054c6d1c10c685
GPT source: GPT-5.6 captured-response fixture/replay
Initial checkpoint: step 12; worker PID 28068; recovery PID 21260
Initial Recovery Gate: FAIL (9 exact failures)
change_supported_checkpoint_strategy: UNSUPPORTED
Six native repair actions: GUARDRAIL ACCEPTED
Repaired run: worker PID 24044; recovery PID 25644
Final Recovery Gate: VERIFIED (24/24, atol=0.0, rtol=0.0)
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base cost: 93987
recurring logical-byte reduction: 93475 bytes (74.06%)
Internal workflow runtime: 16.92 seconds
Total installed-command runtime: 20.7 seconds
```

The byte results exactly match the independently accepted Prompt 6 submission
measurements. The new timing is retained as an audit-run observation and does
not replace the accepted 16.75-second workflow and 20.41-second command timing
used in the Devpost copy.

Installed read-only commands:

```text
flashpilot audit --run-dir .\runs\repair-f2a124b0a506422cad054c6d1c10c685
Fixture replay source: captured_live_response_replay
Repair attempts: 1
Original checkpoint unmodified: True
Final Recovery Gate: VERIFIED

flashpilot verify --run-dir .\runs\repair-f2a124b0a506422cad054c6d1c10c685
VERIFIED by the persisted deterministic Recovery Gate (atol=0.0, rtol=0.0).

flashpilot replay --run-dir .\runs\repair-f2a124b0a506422cad054c6d1c10c685
Captured GPT-5.6 structured response replay matched; no API call was made.
```

An artifact consistency check confirmed initial termination and distinct restore
PID, exactly one repair, historical checkpoint immutability, second termination
and distinct restore PID, 24 passing final checks, zero tolerance, storage
reporting after the pass, exact metric agreement across JSON/Markdown/HTML/
README, the disclaimer in both reports, no external HTTP reference in HTML, and
zero API-key or secret-pattern matches.

The prior-art table was also rechecked against its linked primary papers or
official conference pages. CheckFreq, Check-N-Run, ExCP, Amber, IncrCP, OPT,
MegaScale, FlashRecovery, REO, MIDAS, FDP/WARP, and ZipLLM remain positioned as
adjacent systems rather than implemented FlashPilot features. The OPT paper
directly supports the documented 992-A100, at-least-35-manual-restart, and
estimated-70-plus-automatic-restart framing.

### Final quality gates

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
76 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 56%]
.............................................s..........                 [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
127 passed, 1 skipped in 74.10s (0:01:14)
```

The one skip is the unchanged Windows platform-conditional symlink-privilege
test. Pytest used a unique UUID basetemp and emitted no ACL or cache warning.

### Final scope status

Prompt 8 acceptance criteria pass. Prompt 7 remains skipped. No stretch feature,
additional adapter, new recovery functionality, desktop UI, Docker, Hugging
Face, CUDA, policy planner, chaos scenario, or live API call was added. External
license selection, `/feedback`, video recording/upload, optional GitHub Release,
and Devpost submission remain manual human tasks.

## Milestone 9 — VNext persistence contract foundation

- Date: 2026-07-20
- Branch: `codex/qualification-layer-v0.2`
- Scope: Milestone 9 only. Milestone 10 was not started.
- Starting revision: `97267a3` on `main`.
- Frozen annotated release tag: `flashpilot-v0.1.0` tag object `19b19d0`,
  targeting commit `ad0bf86`; unchanged.

### Baseline before VNext changes

Commands:

```text
git switch -c codex/qualification-layer-v0.2
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile demo --run-dir .\runs\milestone9-baseline-v01
```

Actual baseline quality output:

```text
All checks passed!
76 files already formatted
127 passed, 1 skipped in 84.30s (0:01:24)
```

The one skip was the unchanged Windows directory-symlink privilege condition.
The baseline fixture demo reported:

```text
Initial Recovery Gate: FAIL — 9 exact failures
Final Recovery Gate: VERIFIED — 24/24
atol=0.0, rtol=0.0
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base bytes: 93987
recurring reduction: 93475 bytes (74.06%)
repair attempts: 1
original failed checkpoint unmodified: true
```

### Implementation

Milestone 9 added a new `flashpilot.contracts` package without changing the
frozen v0.1 agent, checkpoint, process, repair, gate, or report code.

The public model includes:

```text
RequirementClass: required, optional, ephemeral, unknown
RecoverySource: checkpoint, immutable_reference, external_durable_source,
                deterministic_recompute, none
RecoveryExactness: exact, tolerance_bounded, non_equivalent
QualificationProfile: exact-training-resume, model-only-inference
PersistenceItem
PersistenceContract
```

Deterministic validation rejects UNKNOWN state, state outside the local
inventory, required state without a source or evidence, a non-equivalent
required item, tolerance-bounded required state under exact training resume,
and an immutable/external/recomputed source without identity controls.

The merger can add or strengthen a deterministic minimum but rejects malformed
or contradictory proposals, context changes, RPO weakening, and unknown state.
The native exact profile contains nine items. The model-only profile retains
adapter and immutable base identity as required and marks training continuation
state ephemeral. The accepted v0.1 native `CheckpointContract` migrates through
an explicit adapter-specific function after the old guardrails pass; no fixture
or v0.1 artifact is rewritten.

Canonical JSON uses sorted keys, fixed separators, UTF-8, and normalized item
ordering before SHA-256. Measured deterministic identities:

```text
exact native minimum: 760789d83b39b7e8943254158cbf6202bca2e87790cd560f06a4202c51ff3295
migrated accepted v0.1 contract: e28d5f74b11f6c7beda69dd3e7c8009803bb73aac8db847c2641cbd1cddf7e59
model-only native minimum: 53ec8e96cce0bf28d1a86c424c84ccc353b8abb244582968dee3a57acb7e8a22
```

Schema generation command:

```text
.\.venv\Scripts\python.exe -c "from pathlib import Path; from flashpilot.contracts.schema import write_schema_files; print(*(str(path) for path in write_schema_files(Path('schemas'))), sep='\n')"
```

Generated draft-2020-12 schemas:

```text
persistence-contract-v1.schema.json    3525 bytes
persistence-item-v1.schema.json        1767 bytes
qualification-profile-v1.schema.json    272 bytes
```

The unit suite reads these files and compares their parsed documents with fresh
generator output, so schema drift fails tests.

### Focused tests

Command and actual output:

```text
.\.venv\Scripts\python.exe -m pytest tests\unit\test_persistence_contracts.py -q
.............                                                            [100%]
13 passed in 1.21s
```

Coverage includes exact and model-only native contracts, round-trip stability,
canonical hash stability under input reordering, UNKNOWN state, missing source,
missing immutable identity controls, tolerance-bounded exact state, duplicate
state IDs, deterministic-minimum strengthening, unknown inventory state,
contradiction rejection, accepted v0.1 migration, and checked-in schema drift.

### Final quality gates

Commands and actual output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
83 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 51%]
.............................................s.......................    [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
140 passed, 1 skipped in 78.87s (0:01:18)
```

Pytest used the unique UUID basetemp and emitted no ACL or cache warning. No
test, tolerance, gate check, repair limit, redaction boundary, or fixture was
weakened.

### Post-change v0.1 fixture regression

Command:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile demo --run-dir .\runs\milestone9-post-v01
```

Actual output retained:

```text
Initial checkpoint: step 12; worker PID 11360; recovery PID 18012
Initial Recovery Gate: FAIL — 9 exact failures
Repaired worker PID 20396; recovery PID 21616
Final Recovery Gate: VERIFIED — 24/24
atol=0.0, rtol=0.0
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base bytes: 93987
recurring reduction: 93475 bytes (74.06%)
```

A direct comparison of pre- and post-change result projections returned:

```text
InvariantProjectionMatch: True
InitialFailures: 9
FinalChecks: 24
FinalVerdict: VERIFIED
RepairAttempts: 1
OriginalCheckpointUnmodified: True
```

The projection includes schema/verdict fields, failed-check IDs, all final gate
checks, tolerance policy, control and resumed trainable/evaluation digests,
applied and unsupported actions, attempt count, immutability, and every storage
comparison value. PIDs and timestamps are intentionally not compared.

### Acceptance status and remaining risks

All Milestone 9 acceptance criteria pass. The contract foundation is currently
used through deterministic builders and the explicit accepted-v0.1 migration;
it does not yet drive static audit, attestation, or a new qualification command.
Those are later milestones. The JSON Schemas are checked in but are not packaged
as wheel data until release packaging is addressed. Only the controlled native
workload is migrated; no Hugging Face adapter or framework detector exists.

After the evidence wording was clarified to distinguish the annotated release
tag object from its target commit, the final documentation-only confirmation
again passed: Ruff check passed, all 83 Python files were formatted, and pytest
reported `140 passed, 1 skipped in 78.59s (0:01:18)`.

## Milestone 10 - static checkpoint audit

- Date: 2026-07-20
- Branch: `codex/qualification-layer-v0.2`
- Scope: Milestone 10 only. Milestone 11 was not started.
- Frozen v0.1 tag and target: unchanged.

### Implementation and trust boundary

Milestone 10 added:

```text
flashpilot audit-checkpoint PATH --framework auto --profile PROFILE
```

The command performs no training run, worker launch, restore, script import, or
user-code execution. It recognizes only `native-pytorch`,
`huggingface-trainer`, or `unknown`. Results use only `PASS`, `WARN`, `FAIL`, or
`UNKNOWN`; the typed result always records `static_only=true` and
`recovery_verified=false`. Static audit cannot issue `VERIFIED` or create a
recovery attestation.

Native inspection reuses existing containment, manifest, checksum, completion,
payload-size, immutable-base, and weights-only validation. Exact resume audits
all nine native Persistence Contract state IDs. The narrow Hugging Face path
uses bounded JSON, validates safetensors headers and offsets without tensor
materialization, and opens only allowlisted PyTorch payloads with
`weights_only=True`. It does not unpickle `training_args.bin` or unknown files.

Outputs are deterministic `audit.json`, `report.md`, and `junit.xml`. JUnit has
one testcase per check and a failure element for every failed requirement.
Stable exits are `PASS=0`, `WARN/UNKNOWN=2`, `FAIL=3`, and unsupported or unsafe
configuration `=5`.

### Development finding

The first focused run exposed that native and Hugging Face layouts share names
such as `optimizer.pt` and `scheduler.pt`:

```text
F.F..............                                                        [100%]
2 failed, 15 passed in 3.69s
```

Both failures were detector ambiguity, not audit-check failures. Detection was
corrected to prioritize framework-specific metadata and to treat shared
training payload names as insufficient framework evidence. The final focused
suite also proves that `optimizer.pt` alone remains `UNKNOWN`.

### Focused verification

Commands and actual output:

```text
.\.venv\Scripts\python.exe -m ruff format src\flashpilot\audit tests\unit\test_static_audit.py
1 file reformatted, 8 files left unchanged

.\.venv\Scripts\python.exe -m ruff check src\flashpilot\audit src\flashpilot\cli.py tests\unit\test_static_audit.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\unit\test_static_audit.py -q
..................                                                       [100%]
18 passed in 5.12s
```

The focused fixtures cover complete native PASS, valid native missing training
state FAIL, native checksum corruption FAIL, interrupted native temporary state
FAIL, supported HF exact-resume PASS, HF model-only exact FAIL and model-only
PASS, unknown layout, shared-name ambiguity, untrusted extra files, refusal to
unpickle binary training arguments, invalid safetensors offsets, output
containment, per-requirement JUnit, and stable exits.

### Manual default-shape native audit

A native checkpoint source was created once for manual inspection:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli safe-full --profile ci --run-dir .\runs\milestone10-native-source
```

It committed at step 4, reported 44,998 logical bytes, and matched the control
after direct restore. The final static command was then run without training:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli audit-checkpoint .\runs\milestone10-native-source\checkpoints\checkpoint-step-000004 --framework auto --profile exact-training-resume --output-dir .\runs\milestone10-native-audit-final
```

Actual command output:

```text
PASS
Static audit only; recovery_verified=false.
Framework: native-pytorch
Audit JSON: C:\Programming\business\flashpilot\runs\milestone10-native-audit-final\audit.json
Markdown report: C:\Programming\business\flashpilot\runs\milestone10-native-audit-final\report.md
JUnit XML: C:\Programming\business\flashpilot\runs\milestone10-native-audit-final\junit.xml
```

The parsed audit contained 17/17 PASS checks including
`state.batch-position`. JUnit reported 17 tests, zero failures, zero errors, and
zero skipped. The result retained `static_only=true` and
`recovery_verified=false`. Both source and output run directories are ignored
by Git.

### Final quality gates

Commands and actual output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
92 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 45%]
.............................................s.......................... [ 90%]
...............                                                          [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
158 passed, 1 skipped in 84.83s (0:01:24)
```

The unchanged Windows platform-conditional symlink test is the only skip.
Pytest used its unique UUID basetemp and emitted no ACL or cache warning.

### Frozen v0.1 regression

Command:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile demo --run-dir .\runs\milestone10-v01-regression
```

Actual invariant result:

```text
Initial Recovery Gate: FAIL - 9 exact failures
Final Recovery Gate: VERIFIED - 24/24
atol=0.0, rtol=0.0
repair attempts: 1
original failed checkpoint unmodified: true
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base bytes: 93987
recurring reduction: 93475 bytes (74.06%)
storage reported only after recovery passed: true
```

The run used worker/recovery PIDs `13560/30036` for the initial failure and
`24496/18792` for the repaired experiment. Total console runtime was 20.88
seconds. Generated artifacts are ignored by Git.

### Acceptance and remaining risks

All Milestone 10 acceptance criteria pass. A static audit can prove only that a
known on-disk layout satisfies the supported static requirements; it cannot
prove resumed trajectory. Hugging Face support is deliberately qualified to the
documented metadata bridge and safe file forms. Typical checkpoints that expose
resume-relevant arguments only through `training_args.bin` fail exact static
qualification rather than being unpickled. Recovery attestation, attestation
verification, a Trainer adapter, script execution, real HF qualification, and
Milestone 11+ work remain unimplemented.

## Milestone 11 - recovery attestation v1

- Date: 2026-07-20
- Branch: `codex/qualification-layer-v0.2`
- Scope: Milestone 11 only. Milestone 12 was not started.
- Frozen v0.1 tag and target: unchanged.

### Implementation

The existing native red-to-green run now emits these additional files only
after the repaired deterministic Recovery Gate passes:

```text
persistence-contract.json
environment.json
evidence-manifest.json
recovery.attestation.json
attestation.junit.xml
```

The original `result.json`, `report.md`, `report.html`, Recovery Gate, repair
loop, and storage models remain unchanged. `RecoveryAttestationV1` records the
exact profile, native framework/runtime, commit and clean/dirty source state,
dependency-environment hash, contract hash, repaired checkpoint-directory hash,
distinct process IDs, equal control/resumed digests, 24/24 gate, zero
tolerances, RPO/RTO, verified recurring bytes, evidence-manifest hash, and
`signature_status=unsigned`.

The evidence manifest contains path, size, and SHA-256 for every experiment
artifact. Exactly three index/statement files are excluded to avoid circular
hashes: the manifest itself, the attestation, and derived attestation JUnit.
Verification recomputes the closed inventory and rejects missing, extra,
mutated, path-escaping, or symlinked evidence.

The verifier also checks the dependency/source record, deterministic native
contract, authoritative result, exact Markdown and HTML rendering, repaired
checkpoint directory identity, native manifest and payload checksums, immutable
base identity, worker/recovery PIDs, trajectory digests, gate count and policy,
RPO/RTO, and verified bytes. `verify-attestation` exits `4` for invalid or
tampered evidence. No signing or publisher-authentication claim is made.

Generated schemas:

```text
evidence-manifest-v1.schema.json       1533 bytes
recovery-attestation-v1.schema.json    6261 bytes
```

The recovery-attestation schema was regenerated after source provenance was
bound into environment evidence, and both final files pass schema-drift tests.

### Development findings

The first attestation-enabled repair-loop test run failed closed because
installed package metadata represented Torch as `2.13.0`, while the actual
runtime build identity was `2.13.0+cpu`:

```text
6 errors in 26.21s
AttestationVerificationError: framework version differs from dependency evidence
```

The environment record was corrected to use `torch.__version__`, preserving the
strict equality check. A later review also bound the Git commit and explicit
`clean`, `dirty`, or `unavailable` source-tree state into the hashed environment
record. The current manual artifact correctly reports the old HEAD plus
`source_tree_state=dirty`; it does not pretend uncommitted milestone code is the
tagged source.

### Focused verification

Commands and final actual output:

```text
.\.venv\Scripts\python.exe -m ruff format src\flashpilot\attestation\verifier.py tests\integration\test_repair_loop.py
2 files left unchanged

.\.venv\Scripts\python.exe -m ruff check src\flashpilot\attestation tests\integration\test_repair_loop.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\integration\test_repair_loop.py -q
....................                                                     [100%]
20 passed in 20.75s
```

Focused tests cover verified emission, exact persisted fields, closed inventory,
deterministic repeat verification, failed-gate refusal, one-byte evidence
mutation, missing evidence, checkpoint mutation, refreshed statement hashes
versus native payload checksums, report mismatch, contract mismatch, metric
mismatch, path traversal, valid/invalid CLI exits, Rich unsigned wording,
eight-check JUnit, and checked-in schema drift.

### Manual native demo and attestation

Commands:

```text
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile demo --run-dir .\runs\milestone11-demo
.\.venv\Scripts\python.exe -m flashpilot.cli verify-attestation .\runs\milestone11-demo\recovery.attestation.json
```

The native core remained unchanged:

```text
Initial Recovery Gate: FAIL - 9 exact failures
Final Recovery Gate: VERIFIED - 24/24
atol=0.0, rtol=0.0
repair attempts: 1
original failed checkpoint unmodified: true
safe_full recurring logical bytes: 126218
repaired recurring logical bytes: 32743
one-time frozen-base bytes: 93987
recurring reduction: 93475 bytes (74.06%)
```

Actual attestation summary:

```text
verdict: verified
qualification profile: exact-training-resume
framework: native-pytorch 2.13.0+cpu
code commit: 97267a3515c9b9add31a63487149d5757a758f0d
source tree: dirty
original/recovery PIDs: 16840 / 13376
Recovery Gate: 24/24
atol/rtol: 0.0 / 0.0
RPO/max RPO: 0 / 0 steps
RTO: 3.975041 seconds
verified persisted bytes: 32743
checkpoint files: 8
checkpoint logical bytes: 32743
checkpoint SHA-256: b3c1b410a0a478173004618565c0c3c8e42f62e20c6850fd901afe122d5e791a
contract SHA-256: 760789d83b39b7e8943254158cbf6202bca2e87790cd560f06a4202c51ff3295
evidence manifest SHA-256: bb36e8727f48c4a9b9217d8cce8831632254cc3d2c6111185b60f04a4fcdd385
evidence entries: 52
signature: unsigned
JUnit: 8 tests, 0 failures
```

Actual verification output ended with:

```text
Attestation SHA-256: f79bf9b04061ea46ec4454559873ef22ea118de884c9727109ff6d3e1a54a105
Unsigned integrity verification passed; no publisher signature was checked.
```

The manual run directory is ignored by Git.

### Final quality gates

Commands and actual output:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
99 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 41%]
...........................................................s............ [ 83%]
.............................                                            [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
172 passed, 1 skipped in 77.74s (0:01:17)
```

The one skip is the unchanged Windows directory-symlink privilege test. Pytest
used a unique UUID basetemp and emitted no ACL or cache warning.

### Acceptance and remaining risks

All Milestone 11 acceptance criteria pass. Verification provides strong local
integrity and internal consistency but not publisher authentication: an actor
who can replace the entire unsigned bundle can recompute it. Cryptographic
signing remains explicitly deferred. The attestation currently covers the
native red-to-green demo; Hugging Face full qualification and its attestation
remain Milestone 12 work. The source tree remains uncommitted and is recorded as
dirty rather than misrepresented as clean release code.

## VNext Milestone 12 - Hugging Face Trainer recovery qualification

Date: 2026-07-20. Scope stopped before Milestone 13.

### Dependency and implementation boundary

The new optional group is:

```toml
hf = [
    "accelerate>=1.14,<2",
    "transformers>=5.14,<6",
]
```

The first sandboxed editable install could not reach the package index because
network access was restricted. The approved retry completed successfully:

```text
.\.venv\Scripts\python.exe -m pip install --no-build-isolation -e ".[hf]"
Successfully installed accelerate-1.14.0 flashpilot-0.1.0 huggingface_hub-1.24.0
safetensors-0.8.0 tokenizers-0.22.2 transformers-5.14.1
```

No model weights or datasets were downloaded. The example creates a tiny model,
config, and deterministic synthetic dataset locally. All workers ran CPU-only
with one Torch thread, offline environment flags, explicit seeds, sequential
samples, and dropout enabled.

The first parent-harness prototype exposed a Windows venv launcher PID mismatch:
the launcher PID differed from the worker event PID. Reusing the existing
Windows base-executable pattern alone then lacked venv imports. The final path
uses the base executable for exact PID ownership and an explicit bounded
`PYTHONPATH` containing repository source plus current venv site-packages. API
key variables are removed from the child environment. Successful runs record
exact event/process PID equality.

### Focused tests

```text
.\.venv\Scripts\python.exe -m pytest tests\unit\test_hf_adapter.py -q
........                                                                 [100%]
8 passed in 0.39s

.\.venv\Scripts\python.exe -m pytest tests\integration\test_hf_qualification.py -q
...                                                                      [100%]
3 passed in 48.66s
```

The tests cover the narrow capability and argument contracts, callback schema,
exact persistence inventory, both real three-process protocols, offline worker
evidence, checkpoint measurement, and complete attestation verification.

### Manual complete HF qualification

```text
.\.venv\Scripts\flashpilot.exe qualify hf-trainer --script .\examples\hf_trainer\train.py --profile exact-training-resume --fault process-kill --scenario complete --run-dir .\runs\milestone12-hf-complete

VERIFIED
Processes: control=18724, terminated=25068, recovery=28236
Result: C:\Programming\business\flashpilot\runs\milestone12-hf-complete\result.json
Markdown report: C:\Programming\business\flashpilot\runs\milestone12-hf-complete\report.md
HTML report: C:\Programming\business\flashpilot\runs\milestone12-hf-complete\report.html
Recovery attestation: C:\Programming\business\flashpilot\runs\milestone12-hf-complete\recovery.attestation.json
```

Measured evidence:

```text
checkpoint step / final step: 4 / 8
verified checkpoint logical bytes: 41635
control duration: 11.890736 seconds
checkpoint/termination duration: 8.419455 seconds
recovery duration: 10.323756 seconds
Recovery Gate: 13/13
atol / rtol: 0.0 / 0.0
RPO / max RPO: 0 / 0
loss history: exact match
trainable state: exact SHA-256 match
fixed evaluation: exact SHA-256 match
optimizer: exact SHA-256 match
scheduler: exact SHA-256 match
```

The checkpoint contains `model.safetensors`, `trainer_state.json`,
`optimizer.pt`, `scheduler.pt`, and `rng_state.pth` plus bounded metadata.
Persisted bytes were assigned only after the gate passed.

```text
.\.venv\Scripts\flashpilot.exe verify-attestation .\runs\milestone12-hf-complete\recovery.attestation.json
Framework: transformers 5.14.1
Recovery processes: 25068 -> 28236
Recovery Gate: 13/13
Exact policy: atol=0.0, rtol=0.0
RPO / RTO: 0 steps / 10.324s
Persisted bytes: 41,635
Signature: unsigned (integrity only; no publisher authentication)
Attestation SHA-256: a8cbd09982f3eefa811308d830ade38472f61dff5e3618bd4d3aa19ae696f2ef
Unsigned integrity verification passed; no publisher signature was checked.
```

### Manual model-only negative qualification

```text
.\.venv\Scripts\flashpilot.exe qualify hf-trainer --script .\examples\hf_trainer\train.py --profile exact-training-resume --fault process-kill --scenario model-only --run-dir .\runs\milestone12-hf-model-only

FAILED
Processes: control=364, terminated=12420, recovery=19792
model_checkpoint_load_succeeded=true
model_only_diverged=true
```

Failed gate IDs:

```text
checkpoint.optimizer
checkpoint.scheduler
checkpoint.rng
trajectory.loss-history
state.trainable
state.evaluation
state.optimizer
state.scheduler
```

The model and Trainer metadata remained valid and loadable. Optimizer,
scheduler, and RNG files were genuinely absent through Trainer's
`save_only_model` behavior. Real dropout-enabled continuation diverged without
output manipulation. No storage metric or attestation was emitted.

### Existing native regression

```text
.\.venv\Scripts\python.exe -m flashpilot.cli demo --provider fixture --profile ci --run-dir .\runs\milestone12-native-regression
Initial Recovery Gate: FAIL - 9 exact failures
Final Recovery Gate: VERIFIED - 24/24
atol=0.0, rtol=0.0
RPO: 0
original failed checkpoint unmodified: true
```

The P0 NativePyTorchAdapter and six-action repair boundary remain unchanged.

### Final quality gates

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
112 files already formatted

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 39%]
......................................................................s. [ 78%]
........................................                                 [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
183 passed, 1 skipped in 133.36s (0:02:13)
```

Pytest used a unique UUID basetemp. The skip is the unchanged Windows
directory-symlink privilege check.

### Acceptance and unresolved risks

All Milestone 12 criteria pass: complete HF recovery is exact and VERIFIED;
model-only is valid/loadable and FAILED for exact resume; every run uses three
distinct PIDs with real termination; no network or download is needed; the
native demo remains green; and Ruff/pytest pass.

Validation used Windows, Python 3.12.13, Transformers 5.14.1, Accelerate 1.14.0,
and Torch 2.13.0+cpu. Python 3.11 and other hosts remain unverified locally.
Offline flags are not an OS network sandbox. The adapter qualifies only the
included callback contract, not arbitrary Trainer scripts. Windows directory
fsync remains best-effort and attestations remain unsigned. CI workflow,
every-command JUnit, stable global exit policy, and packaging are Milestone 13+
and were not started.

## VNext Milestone 13 - CI and developer workflow

Date: 2026-07-20. Scope stopped before Milestone 14.

### Implemented boundary

Milestone 13 adds the opt-in workflow example at
`examples/github-actions/flashpilot-qualification.yml`; it is intentionally not
installed under `.github/workflows`. The workflow installs `.[hf]`, runs the
real HF qualification, statically audits its committed checkpoint, enforces the
same typed policy used locally, appends `job-summary.md` to
`GITHUB_STEP_SUMMARY`, uploads diagnostics with `if: always()`, and uploads
`recovery.attestation.json` only with `if: success()`.

The checked-in `examples/ci/policy.yml` validates against
`schemas/ci-policy-v1.schema.json`. Its only fields are the exact profile,
`unknown_state=fail`, canonical process-termination fault, maximum RPO/RTO, and
attestation requirement. Loading uses bounded `yaml.safe_load`; extra keys,
arbitrary expressions, weak UNKNOWN settings, and unallowlisted faults fail.

Every completed audit and qualification now contains `junit.xml` and
`job-summary.md`. Passing attested runs write both before evidence-manifest
closure. Later `emit-junit` verifies byte equality, refuses to recreate missing
attested evidence, and independently verifies an existing attestation. Failed
runs keep diagnostic CI artifacts and never receive an attestation.

### Safe real-HF audit compatibility finding

The first audit of the real Milestone 13 complete Trainer checkpoint failed:

```text
FAIL
state.python_rng: rng_state.pth failed weights-only loading
state.numpy_rng: rng_state.pth failed weights-only loading
state.torch_rng: rng_state.pth failed weights-only loading
captured_exit=3
```

PyTorch reported that the standard Transformers RNG pickle contains
`numpy._core.multiarray._reconstruct`, which is outside the default
weights-only allowlist. FlashPilot did not fall back to unrestricted pickle or
weaken the audit. The supported callback now emits strict
`flashpilot-hf-rng-metadata-v1` JSON bound to the exact `rng_state.pth` SHA-256
and three literal RNG presence claims. Static audit validates this bridge and
hash without loading the pickle. A focused copied-checkpoint test flips one RNG
byte and proves all three RNG requirements fail.

The corrected real checkpoint audit command and output were:

```text
.\.venv\Scripts\flashpilot.exe audit-checkpoint .\runs\milestone13-hf-qualified\crash\checkpoints\checkpoint-4 --framework auto --profile exact-training-resume --output-dir .\runs\milestone13-qualified-audit
PASS
Static audit only; recovery_verified=false.
Framework: huggingface-trainer
Audit JSON: C:\Programming\business\flashpilot\runs\milestone13-qualified-audit\audit.json
Markdown report: C:\Programming\business\flashpilot\runs\milestone13-qualified-audit\report.md
JUnit XML: C:\Programming\business\flashpilot\runs\milestone13-qualified-audit\junit.xml
Job summary: C:\Programming\business\flashpilot\runs\milestone13-qualified-audit\job-summary.md
captured_exit=0
```

### Generic native qualification

```text
.\.venv\Scripts\flashpilot.exe qualify native-pytorch --profile exact-training-resume --fault process-kill --workload ci --run-dir .\runs\milestone13-native
VERIFIED
Processes: terminated=27632, recovery=31396
Result: C:\Programming\business\flashpilot\runs\milestone13-native\result.json
JUnit XML: C:\Programming\business\flashpilot\runs\milestone13-native\junit.xml
Job summary: C:\Programming\business\flashpilot\runs\milestone13-native\job-summary.md
Recovery attestation: C:\Programming\business\flashpilot\runs\milestone13-native\recovery.attestation.json
captured_exit=0
```

The command is a thin entry point over the preserved fixture replay, bounded
repair, second process termination, exact 24-check Recovery Gate, and unsigned
attestation core. It adds no new native repair behavior.

### Real HF verified CI path

```text
.\.venv\Scripts\flashpilot.exe qualify hf-trainer --script .\examples\hf_trainer\train.py --profile exact-training-resume --fault process-kill --scenario complete --run-dir .\runs\milestone13-hf-qualified
VERIFIED
Processes: control=16608, terminated=29488, recovery=23100
JUnit XML: C:\Programming\business\flashpilot\runs\milestone13-hf-qualified\junit.xml
Job summary: C:\Programming\business\flashpilot\runs\milestone13-hf-qualified\job-summary.md
Recovery attestation: C:\Programming\business\flashpilot\runs\milestone13-hf-qualified\recovery.attestation.json
captured_exit=0
```

Measured evidence:

```text
Recovery Gate: 13/13
JUnit: 13 tests, 0 failures
control / terminated / recovery PIDs: 16608 / 29488 / 23100
RPO: 0 steps
RTO: 6.536153 seconds
verified checkpoint logical bytes: 41947
RNG bridge present: true
evidence manifest entries: 26
```

The byte increase from the historical Milestone 12 run is the real strict JSON
RNG metadata bridge; it is measured rather than hidden or presented as savings.

Policy enforcement and attestation verification:

```text
.\.venv\Scripts\flashpilot.exe emit-junit --run-dir .\runs\milestone13-hf-qualified --policy .\examples\ci\policy.yml
VERIFIED
Policy: PASS
captured_exit=0

.\.venv\Scripts\flashpilot.exe verify-attestation .\runs\milestone13-hf-qualified\recovery.attestation.json
Framework: transformers 5.14.1
Recovery processes: 29488 -> 23100
Recovery Gate: 13/13
RPO / RTO: 0 steps / 6.536s
Persisted bytes: 41,947
Attestation SHA-256: 638b2166f139ac8a3bc336b426e2ffadf521e5dcedac37e6dadc463ded91db82
captured_exit=0
```

### Failed HF CI path and exact requirements

```text
.\.venv\Scripts\flashpilot.exe qualify hf-trainer --script .\examples\hf_trainer\train.py --profile exact-training-resume --fault process-kill --scenario model-only --run-dir .\runs\milestone13-hf-model-only
FAILED
Processes: control=21448, terminated=29604, recovery=28232
JUnit XML: C:\Programming\business\flashpilot\runs\milestone13-hf-model-only\junit.xml
Job summary: C:\Programming\business\flashpilot\runs\milestone13-hf-model-only\job-summary.md
captured_exit=3
```

The JUnit suite contains 13 tests and 8 failures named exactly:

```text
checkpoint.optimizer
checkpoint.scheduler
checkpoint.rng
trajectory.loss-history
state.trainable
state.evaluation
state.optimizer
state.scheduler
```

No attestation exists for this run. Typed policy enforcement remains failed:

```text
FAILED
Policy: FAIL
FAILED REQUIREMENT policy.qualification-verdict: Qualification must have a deterministic VERIFIED verdict.
captured_exit=3
```

### Stable exit-code matrix

Actual normal PowerShell process exits:

```text
0 = verified/pass
  complete native qualification: 0
  complete HF qualification: 0
  complete HF static audit: 0
  typed policy plus verified attestation: 0

2 = warning/UNKNOWN review
  unknown empty checkpoint audit: UNKNOWN, captured_exit=2

3 = qualification or enforced-policy failure
  model-only HF exact qualification: captured_exit=3
  UNKNOWN with unknown_state=fail: captured_exit=3
  FAILED REQUIREMENT policy.unknown-state

4 = invalid/tampered evidence
  emit-junit on a run without result evidence: captured_exit=4
  INVALID OR TAMPERED CI EVIDENCE: run directory lacks a safe result.json or audit.json

5 = unsupported configuration
  HF qualification with unsupported profile: captured_exit=5
```

UNKNOWN never produced exit zero. With the checked-in policy it becomes an
explicit policy failure rather than PASS.

### Focused verification

Final focused command and actual output:

```text
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ci.py tests\unit\test_static_audit.py tests\integration\test_repair_loop.py tests\integration\test_hf_qualification.py -q
............................................................             [100%]
60 passed in 72.80s (0:01:12)
```

Additional post-review focused evidence:

```text
.\.venv\Scripts\python.exe -m pytest tests\unit\test_ci.py tests\integration\test_repair_loop.py -q
.....................................                                    [100%]
37 passed in 25.77s
```

### Final quality gates

```text
.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 35%]
........................................................................ [ 70%]
..................s.........................................             [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
203 passed, 1 skipped in 144.55s (0:02:24)
```

The single skip is the unchanged non-administrator Windows directory-symlink
test. Pytest used a unique UUID basetemp with no ACL or cache warning. Final Ruff
outputs after this documentation update were:

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
120 files already formatted
```

### Acceptance and unresolved risks

All Milestone 13 acceptance criteria pass. CI failures name exact audit/gate or
policy IDs; UNKNOWN cannot become PASS; the example uploads attestations only
after success; local and example-CI commands share typed services; and full
pytest passes. The workflow is an opt-in example rather than an active hosted
service.

Current validation remains Windows/Python 3.12.13. The example targets Python
3.11 but has not run in hosted GitHub Actions. Windows directory fsync remains
best-effort, offline flags are not an OS network sandbox, and attestations remain
unsigned. PyYAML becomes a core dependency so policy loading works without HF
extras; clean base/HF wheel installation and dependency verification are
Milestone 14 and were not started.

## 2026-07-20 — VNext Milestone 14: v0.2 release packaging

Milestone 14 was executed alone. Version metadata is `0.2.0`, Python support is
declared as `>=3.11`, the checked-in Apache-2.0 license is expressed through
PEP 639 metadata, and the frozen `flashpilot-v0.1.0` tag still resolves to
`ad0bf8641132125038da7ca17903e4627b9af36d`.

### Build and archive inspection

The release tools were installed at the declared bounds. The first unprivileged
install attempt was blocked by sandbox network policy; the approved retry
installed `build 1.5.0` and `twine 6.2.0`. The actual build and validation were:

```text
.\.venv\Scripts\python.exe -m build --no-isolation
Successfully built flashpilot-0.2.0.tar.gz and flashpilot-0.2.0-py3-none-any.whl

.\.venv\Scripts\python.exe -m twine check .\dist\flashpilot-0.2.0-py3-none-any.whl .\dist\flashpilot-0.2.0.tar.gz
Checking .\dist\flashpilot-0.2.0-py3-none-any.whl: PASSED
Checking .\dist\flashpilot-0.2.0.tar.gz: PASSED
```

Final artifacts:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `flashpilot-0.2.0-py3-none-any.whl` | 168,532 | `676c1a6110f041b5b84aaa178d3d641a94051ec4ea4ab3c0590b4b8e64bf020b` |
| `flashpilot-0.2.0.tar.gz` | 129,810 | `cb5383a502558cd441fe6e27893d264c8f77b18a122972977de3bd792cab8a15` |

Programmatic inspection found 111 wheel members and 142 source-distribution
members. It confirmed name/version, `Requires-Python >=3.11`,
`License-Expression: Apache-2.0`, `Provides-Extra: dev, hf`, all three HF
requirements, every required module/fixture/schema/example/checklist, and zero
run, cache, `.env`, or compiled-Python members.

### Clean installations outside the repository

A network-enabled dependency download created a neutral wheelhouse. Both
authoritative installations then resolved the FlashPilot wheel offline from
that wheelhouse. The long clean-environment root is outside this repository and
was temporarily mapped to `R:` only for installation because Windows long-path
support is disabled on this host.

Base installation evidence:

```text
python=3.12.13
flashpilot=0.2.0
transformers_present=False
accelerate_present=False
safetensors_present=False
torch=2.13.0

flashpilot doctor --output-dir <outside-repository>/base-run/doctor-output
Doctor verdict: PASS

flashpilot demo --provider fixture --profile ci --run-dir <outside-repository>/base-run/fixture-demo-canonical
Initial Recovery Gate: FAIL, 9 exact failures
Final Recovery Gate: VERIFIED, 24/24
safe_full recurring logical bytes: 44,998
repaired recurring logical bytes: 27,681
one-time immutable base: 18,475
demo_exit=0

flashpilot audit-checkpoint <safe_full-checkpoint> --framework auto --profile exact-training-resume --output-dir <outside-repository>/base-run/native-safe-full-audit
PASS
Static audit only; recovery_verified=false.
Framework: native-pytorch
audit_exit=0

flashpilot qualify hf-trainer --run-dir <outside-repository>/base-run/hf-extra-missing
Hugging Face qualification requires the optional dependencies; install with `pip install 'flashpilot[hf]'`
hf_missing_exit=5
```

HF-extra installation evidence:

```text
python=3.12.13
flashpilot=0.2.0
transformers=5.14.1
accelerate=1.14.0
safetensors=0.8.0
torch=2.13.0

flashpilot qualify hf-trainer --profile exact-training-resume --fault process-kill --scenario complete --run-dir <outside-repository>/hf-run/complete-default-worker
VERIFIED
Processes: control=6300, terminated=3640, recovery=16756
Recovery Gate: 13/13
RPO / RTO: 0 steps / 7.224s
verified checkpoint logical bytes: 42,010
hf_qualification_exit=0

flashpilot verify-attestation <outside-repository>/hf-run/complete-default-worker/recovery.attestation.json
Attestation SHA-256: f9a2670d52ee81272639065c1e87d010644beed0ab72083090481d17bc654509
Unsigned integrity verification passed; no publisher signature was checked.

flashpilot emit-junit --run-dir <outside-repository>/hf-run/complete-default-worker --policy <installed-data>/examples/ci/policy.yml
VERIFIED
Policy: PASS

flashpilot audit-checkpoint <outside-repository>/hf-run/complete-default-worker/crash/checkpoints/checkpoint-4 --framework auto --profile exact-training-resume --output-dir <outside-repository>/hf-run/static-audit
PASS
Static audit only; recovery_verified=false.
Framework: huggingface-trainer
hf_audit_exit=0
```

No `--script` argument was used for the accepted HF qualification; the worker
came from the installed wheel. The worker recorded offline controls, used CPU,
and downloaded no model or dataset. Scans across both authoritative output
trees and both distribution archives reported:

```text
output_secret_matches=0
distribution_secret_matches=0
```

### Windows validation findings

Three failed setup attempts were retained as diagnostic facts and not counted
as acceptance evidence:

- `C:\tmp` environments created under the approved network security context
  inherited ACLs that denied writes from the normal validation context;
- installing PyTorch under the first long external path exceeded the host's
  disabled Windows long-path boundary;
- a completed fixture run using the `R:` alias failed attestation verification
  closed because the alias and canonical path were different containment
  identities.

The successful environments use the external artifact workspace, a short drive
mapping for package installation, and canonical paths for every run artifact.
No ACL was modified and no containment rule was weakened. A static audit of an
adapter-aware checkpoint without its sibling immutable base correctly returned
FAIL; the authoritative CPU static-audit acceptance used the self-contained
safe_full checkpoint and returned PASS.

### Focused and full quality gates

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m ruff format --check .
121 files already formatted

.\.venv\Scripts\python.exe -m pytest tests\unit\test_packaging.py tests\unit\test_doctor.py tests\unit\test_hf_adapter.py tests\integration\test_hf_qualification.py -q
........................                                                 [100%]
24 passed in 50.35s

.\.venv\Scripts\python.exe -m pytest -q
........................................................................ [ 34%]
........................................................................ [ 68%]
.........................s.........................................      [100%]
=========================== short test summary info ===========================
SKIPPED [1] tests\unit\test_paths.py:33: directory symlinks are unavailable: [WinError 1314] Client lacks the required directory-symlink privilege
210 passed, 1 skipped in 138.51s (0:02:18)
```

The single skip is the unchanged Windows directory-symlink privilege test. The
default pytest command retained its unique UUID basetemp and disabled cache.

### Acceptance and unresolved risks

All Milestone 14 acceptance criteria pass: the native installation works with
no HF distributions; the HF command fails actionably when its extra is absent;
the separate HF-extra install qualifies its packaged example; native and HF
static audits pass on CPU; output and archive secret scans are empty; and the
full Ruff/pytest gates pass.

Validation remains Windows/Python 3.12.13; Python 3.11 is the declared target
but was unavailable locally. Windows directory fsync remains best-effort,
offline environment flags are not an OS network sandbox, the attestation is
unsigned, dependency installation requires a package index or prepared local
wheelhouse, and public release/tagging remains a human action. No V0.3 roadmap
work was started.
