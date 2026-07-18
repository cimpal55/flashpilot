# FlashPilot

FlashPilot is a CPU-only checkpoint-reliability demonstration for one native
PyTorch workload. It creates a valid but incomplete checkpoint, terminates a
real worker, observes deterministic recovery failure, replays an accepted
secret-free GPT-5.6 diagnosis, applies one bounded typed repair, repeats the
real crash/restore, and lets only the Recovery Gate declare success.

Prompt 5 is the current implemented milestone. P0 supports only
`NativePyTorchAdapter` and exactly six repair actions. It has no plugin system,
additional framework adapter, policy planner, HTML report, package artifact,
Docker image, or GPT report narrator.

## Development commands

Use Python 3.11 or newer with the development dependencies installed, then run:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```

The current Windows validation environment uses Python 3.12.13. Pytest disables
its cache and uses a fresh UUID directory directly under the system temporary
directory, avoiding cross-security-context ACL collisions.

## Bounded fixture demo

Choose a clean run directory:

```powershell
.\.venv\Scripts\python.exe -m flashpilot.cli demo `
  --provider fixture `
  --profile demo `
  --run-dir .\runs\manual-prompt5
```

The default fixture is an explicitly labeled replay of an independently
accepted GPT-5.6 structured response. It makes no API call. Inspect the durable
artifacts without rerunning the crash:

```powershell
.\.venv\Scripts\python.exe -m flashpilot.cli audit --run-dir .\runs\manual-prompt5
.\.venv\Scripts\python.exe -m flashpilot.cli verify --run-dir .\runs\manual-prompt5
.\.venv\Scripts\python.exe -m flashpilot.cli replay --run-dir .\runs\manual-prompt5
```

`result.json` is authoritative and `report.md` is rendered deterministically.
Storage comparison is emitted only after the repaired Recovery Gate passes and
reports logical recurring bytes separately from the one-time immutable base.
No physical NAND-write, write-amplification, or SSD-lifetime claim is made.

## Safety and platform limits

- GPT-5.6 does not receive the failure-injection label, expected diagnosis,
  repair preset, tensors, samples, secrets, arbitrary files, or absolute local
  paths.
- Model output cannot execute code, commands, patches, or paths. It is parsed
  and classified before six fixed action-to-boolean mappings are considered.
- Exactly one repair attempt is admitted. A failed repaired gate stops closed.
- Checkpoint payload and metadata files are fsynced and directory rename is
  atomic. Python does not expose directory fsync on Windows, so directory
  durability there remains explicitly best-effort.
- The Windows directory-symlink containment test remains enabled and skips only
  when the host user lacks symlink privilege.
