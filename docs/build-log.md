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
