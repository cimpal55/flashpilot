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
