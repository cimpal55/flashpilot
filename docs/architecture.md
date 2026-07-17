# Architecture

The intended architecture is deliberately narrow and staged:

1. `workload` owns a deterministic, CPU-only Transformer-like training system.
2. Synthetic token batches are pure functions of the global seed and global step.
3. The model has a frozen base and one trainable residual bottleneck adapter.
4. Nonzero training dropout makes RNG restoration relevant; fixed evaluation runs with dropout disabled.
5. CI and demo profiles bound runtime and require no downloads or external datasets.
6. An uninterrupted control persists JSON-safe final-state, optimizer, scheduler, loss, and evaluation summaries.
7. The checkpoint layer validates manifests, checksums, completion markers, containment, and same-filesystem atomic directory commits.
8. A minimal `TrainerAdapter` boundary exposes only `NativePyTorchAdapter` in P0 through a plain lookup function.
9. The parent orchestrator kills a worker only after a contained, validated committed-checkpoint event and restores in a new process.
10. The deterministic Recovery Gate compares resumed evidence with the uninterrupted control and is the only recovery authority.
11. Future GPT-5.6 providers will consume bounded capability summaries or sanitized failure evidence and emit typed outputs without executing changes.
12. A future repair executor will copy a typed strategy configuration, apply only six supported field changes, and run one isolated retry.
13. Future JSON and Markdown reports will derive from deterministic results and show storage impact only after recovery passes.

## Milestone status through Prompt 3

Items 1 through 10 are implemented. A worker commits and emits a structured
event after rename; the parent validates the relative checkpoint path, kills
that recorded process, verifies termination, and starts recovery under a
different PID. The recovery worker records its immediate restored state, actual
first resumed step, and final state.

The Recovery Gate keeps 24 individual checks in `result.json`, grouped for the
console as Integrity, Required training state, Process recovery, Trajectory
correctness, and Safety and rollback. Comparison is exact with zero tolerance.
Both safe strategies pass across the process boundary. The valid incomplete
strategy loads but fails nine required-state, trajectory, and contract checks
and writes a guarded sanitized failure package. Corrupt optimizer bytes and a
missing base fail before deserialization. There is still no GPT integration,
repair execution, HTML, release packaging, plugin discovery, or additional
framework adapter.

## Three largest implementation risks

| Risk | Why it matters |
| --- | --- |
| Cross-platform process reproducibility | Exact recovery is proven on the current Windows/Python/PyTorch environment, but other supported OS and dependency versions still require validation. |
| Incomplete recovery state | A checkpoint can remain valid and loadable while omitting optimizer, scheduler, or RNG state, so later schemas and the Recovery Gate must distinguish integrity from continuation correctness. |
| Useful but non-leading GPT evidence | GPT-5.6 must diagnose from useful evidence without receiving fixture intent, while deterministic code remains the sole repair validator and recovery authority. |
