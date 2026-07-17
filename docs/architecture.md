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
9. A future parent orchestrator will kill a worker only after a validated committed-checkpoint event and restore in a new process.
10. A future deterministic Recovery Gate will compare resumed evidence with the uninterrupted control and be the only recovery authority.
11. Future GPT-5.6 providers will consume bounded capability summaries or sanitized failure evidence and emit typed outputs without executing changes.
12. A future repair executor will copy a typed strategy configuration, apply only six supported field changes, and run one isolated retry.
13. Future JSON and Markdown reports will derive from deterministic results and show storage impact only after recovery passes.

## Milestone status through Prompt 2

Items 1 through 8 are implemented. `safe_full` remains the complete-state
baseline. `safe_adapter_aware` references one immutable hash-identified frozen
base and stores complete recurring adapter training state.
`missing_training_state` is checksum-valid and loadable but intentionally omits
optimizer, scheduler, and relevant RNG state; continued dropout-enabled
training diverges from the control. There is still no crash orchestration,
Recovery Gate, GPT integration, repair execution, HTML, release packaging,
plugin discovery, or additional framework adapter.

## Three largest implementation risks

| Risk | Why it matters |
| --- | --- |
| Cross-process reproducibility | Exact results must survive true process boundaries and supported OS and PyTorch versions, not only repeated calls in one interpreter. |
| Incomplete recovery state | A checkpoint can remain valid and loadable while omitting optimizer, scheduler, or RNG state, so later schemas and the Recovery Gate must distinguish integrity from continuation correctness. |
| Useful but non-leading GPT evidence | GPT-5.6 must diagnose from useful evidence without receiving fixture intent, while deterministic code remains the sole repair validator and recovery authority. |
