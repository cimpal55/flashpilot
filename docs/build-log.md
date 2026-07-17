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
