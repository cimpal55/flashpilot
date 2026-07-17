# FlashPilot repository guidance

Read `FLASH_PILOT_CODEX_MASTER_PLAN.md` completely before milestone work. Section
28.5 is the binding V4.1 execution override and wins over every conflicting
section.

## Scope and sequencing

- Execute exactly one Section 29 milestone at a time and stop after its
  acceptance criteria.
- P0 supports only `NativePyTorchAdapter`; do not add plugin discovery,
  framework auto-detection, or additional framework adapters.
- P0 implements only the six primary repair actions named in Section 28.5.
  Other public enum values remain known but unsupported by the native adapter.
- Do not build a generic policy engine, plugin system, repository scanner, AST
  analyzer, policy planner, numeric CrashScore, or GPT report narrator in P0.
- The primary failure fixture is a valid, checksum-valid, loadable checkpoint
  that omits training state. Binary corruption is a separate fail-closed case.
- Never send GPT-5.6 an injection label, expected diagnosis, repair preset name,
  or comments that reveal deliberately omitted state.
- Only the deterministic Recovery Gate can prove recovery. Report storage
  savings only for strategies that have passed it.

## Engineering rules

- Keep all product code, tests, documentation, reports, and console text in
  English.
- Prefer deterministic evidence, recovery correctness, safety, reproducibility,
  and honest reporting over feature count.
- P0 is Python 3.11+, PyTorch CPU-only, uses no external datasets or downloaded
  model weights, and must run with a fixed thread count and explicit seeds.
- Do not invent command or test output. Record the actual quality-gate output in
  `docs/build-log.md` after every milestone.
- Keep generated run artifacts and secrets out of Git.

## Prompt 0 commands

From the repository root with the development environment activated:

```text
ruff check .
ruff format --check .
pytest -q
```

