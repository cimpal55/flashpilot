# Architecture

The architecture is deliberately narrow:

1. `workload` owns a deterministic, CPU-only Transformer-like training system.
2. Synthetic token batches are pure functions of the global seed and global step.
3. The model has a frozen base and one trainable residual bottleneck adapter.
4. Nonzero training dropout makes RNG restoration relevant; evaluation disables dropout.
5. CI and demo profiles require no downloads or external datasets.
6. An uninterrupted control records final model, optimizer, scheduler, loss, and evaluation evidence.
7. Checkpoints use manifests, checksums, completion markers, containment, and atomic directory rename.
8. P0 exposes only `NativePyTorchAdapter` through a plain lookup function.
9. The parent kills a worker only after validating its committed checkpoint event.
10. Recovery runs in a distinct process and restores state before the next batch.
11. The deterministic Recovery Gate is the only recovery authority and compares exactly.
12. GPT-5.6 consumes only bounded capabilities or sanitized failure evidence and emits typed proposals.
13. The repair executor copies a typed strategy config and changes only six allowlisted booleans once.
14. JSON is authoritative; Markdown is deterministically rendered without a GPT narrator.
15. Logical storage impact is calculated only after repaired recovery passes.

## Milestone status through Prompt 5

The parent process launches an incomplete-checkpoint worker, waits for and
validates its post-rename event, kills the recorded PID, and restores in a new
PID. The valid checkpoint loads, but its deterministic Recovery Gate fails nine
required-state, trajectory, and contract checks. Its sanitized evidence excludes
the injection label, strategy name, expected diagnosis, repair preset, tensors,
samples, secrets, commands, arbitrary files, and absolute local paths.

The default contract and failure fixtures reproduce the independently accepted
secret-free GPT-5.6 structured responses. Metadata sidecars retain their live
provider, model, response ID, request hash, timestamp, prompt/schema versions,
and `store=false`. Runtime use is labeled
`source=captured_live_response_replay`; no API call occurs.

The failure proposal is parsed through the same strict schema and deterministic
guardrails. `change_supported_checkpoint_strategy` remains known but
unsupported. Exactly these six actions are executable:

- `persist_optimizer_state`
- `persist_scheduler_state`
- `persist_python_rng_state`
- `persist_numpy_rng_state`
- `persist_torch_rng_state`
- `restore_state_before_next_batch`

The executor admits one attempt through exclusive file creation, copies
`CheckpointStrategyConfig`, maps those actions to
`include_optimizer`, `include_scheduler`, `include_python_rng`,
`include_numpy_rng`, `include_torch_rng`, and
`restore_before_next_batch`, and assigns a new strategy ID. There is no command,
patch, path, or model-text execution surface.

The repaired configuration runs under a new `repaired/` root using the existing
`safe_adapter_aware` contract. A second real worker is killed after its atomic
commit, a distinct process restores, and the unchanged 24-check Recovery Gate
compares with the same uninterrupted control at `atol=0.0`, `rtol=0.0`. A
whole-directory SHA-256 fingerprint proves the original failed checkpoint did
not change. Attempt two is refused.

`result.json` records the two experiments, captured and replay metadata, full
proposal, classification, explicit strategy fields, fingerprints, attempt
count, final gate, and post-pass storage comparison. `report.md` renders that
record deterministically. `audit`, `verify`, and `replay` are read-only. The
recurring repaired checkpoint is measured separately from its one-time frozen
base. No physical NAND, write-amplification, or SSD-lifetime claim is made.

## Three largest implementation risks

| Risk | Why it matters |
| --- | --- |
| Cross-platform process reproducibility | Exact recovery is proven on the current Windows/Python/PyTorch environment, but other supported OS and dependency versions still require validation. |
| Durability limits on Windows | Files are fsynced and directory rename is atomic, but Python cannot directory-fsync on Windows, so that part remains explicitly best-effort. |
| Replay applicability | The accepted GPT-5.6 diagnosis is replayed against the same typed evidence contract; new workload capabilities or failure shapes require a new guarded analysis rather than broadening this executor. |
