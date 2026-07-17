# Codex contributions

## Milestone 0

Codex performed the following concrete work under human-approved scope:

- read and reconciled the complete V4 plan with the binding V4.1 override;
- inspected the initially empty repository and local command availability;
- designed the narrow Prompt 0 architecture and recorded the three largest risks;
- created the Python `src` layout, test layout, configuration, and documentation scaffolds;
- implemented immutable CI and demo workload profiles;
- implemented deterministic step-derived synthetic next-token batches;
- implemented the tiny Transformer-like frozen base and trainable residual adapter;
- implemented dropout-active training and fixed dropout-disabled evaluation;
- implemented AdamW training, a linear learning-rate scheduler, and control-run summaries;
- implemented deterministic digests for trainable, optimizer, scheduler, and evaluation state;
- added unit tests and an integration test for exact repeated-control equality;
- ran and recorded the required quality gates with actual output.

Codex did not implement checkpoints, GPT providers, repair execution, process
killing, a Recovery Gate, HTML, packaging, or any later milestone feature.

## Milestone 1

Codex performed the following concrete work under the binding Prompt 1 scope:

- refactored the deterministic loop into reusable runtime, train, and summary
  primitives while retaining Prompt 0 control semantics;
- added strict Pydantic schemas for the safe-full manifest, checksum document,
  completion marker, profile snapshot, and checkpoint state;
- implemented normalized path models plus resolved run-root containment and
  symlink-escape rejection;
- implemented payload and metadata file flushing, file `fsync`, checksum
  generation, temp-directory commit, same-filesystem rename, and post-rename
  commit callback ordering;
- implemented an explicit Windows best-effort directory-sync result rather than
  claiming unavailable durability guarantees;
- implemented fail-closed loader validation, corruption rejection,
  incomplete-temp exclusion, and latest-valid discovery with fallback;
- implemented containment-safe retention that separately preserves an explicit
  latest verified checkpoint;
- implemented `safe_full` serialization and direct restoration of model,
  optimizer, scheduler, step, Python/NumPy/Torch RNG, profile, and loss history;
- implemented measured logical checkpoint bytes, checkpoint duration, and
  restore duration;
- added `flashpilot control` and `flashpilot safe-full` CLI commands;
- added unit and integration coverage for integrity, containment, atomic commit,
  restore equality, RNG restoration, retention, metrics, and CLI behavior;
- diagnosed and corrected Windows `fsync` behavior, where `_commit` requires a
  descriptor opened with write access even when no bytes are modified.

Codex did not implement Prompt 2 adapter abstractions or adapter-aware state,
GPT providers, process termination, a Recovery Gate, repair logic, HTML,
packaging/release artifacts, plugin discovery, or additional frameworks.

## Milestone 2

Codex performed the following concrete work under the binding Prompt 2 scope:

- added a deliberately minimal `TrainerAdapter` abstraction and the only P0
  implementation, `NativePyTorchAdapter`, with a fixed plain lookup function;
- added strict `WorkloadCapabilities` and `SaveRestoreSummary` models without
  plugin discovery, command builders, framework detection, or repair methods;
- partitioned native model state into the immutable frozen base and trainable
  residual adapter with strict key validation on restore;
- implemented atomic one-time frozen-base persistence with payload and metadata
  file synchronization, same-filesystem rename, fixed contained paths, identity,
  SHA-256, size, completion marker, and tensor-for-tensor reuse validation;
- implemented `safe_adapter_aware` recurring checkpoints containing adapter,
  optimizer, scheduler, step, Python/NumPy/Torch RNG, profile, base reference,
  manifest, checksums, and completion marker;
- implemented `missing_training_state` as a valid, loadable checkpoint whose
  manifest explicitly declares the omitted optimizer, scheduler, and RNG state;
- implemented direct restore for both strategies, validating checkpoint and base
  integrity before deserializing tensors with `weights_only=True`;
- added tests proving exact adapter-aware continuation, one-time base reuse,
  immutable-base enforcement, structural byte reduction, missing/wrong-base
  rejection, and real dropout-path divergence after incomplete-state loading;
- measured demo-profile full, base, recurring adapter, first-write, restore, and
  divergence evidence without adding padding or claiming storage savings.

Codex did not implement GPT integration or disclosure labels, subprocess
workers or termination, a Recovery Gate, bounded repair, HTML, packaging,
Docker, Hugging Face support, plugin discovery, or any additional adapter.

## Milestone 3

Codex performed the following concrete work under the binding Prompt 3 scope:

- added strict structured models for checkpoint events, runtime observations,
  process metadata, comparison policy, individual gate checks, experiment
  results, and sanitized failure artifacts;
- implemented a real checkpoint worker subprocess that trains, commits through
  the existing atomic strategies, captures hash-only observations after rename,
  emits one machine-readable event, and waits for parent-owned termination;
- implemented parent-side event parsing, PID verification, run-sandbox path
  resolution, checkpoint validation before termination, forceful process kill,
  expected exit-code verification, and orphan cleanup on protocol errors;
- diagnosed Windows venv-launcher PID indirection and switched workers to the
  actual base Python executable with explicitly supplied venv/project paths;
- implemented a separate recovery worker process that validates and restores
  the checkpoint, records immediate state and RNG digests, executes the actual
  next batch, continues to the final step, and writes a contained result;
- implemented all 20 mandatory Recovery Gate checks plus explicit original PID,
  termination, distinct recovery PID, and recovery exit checks;
- implemented exact SHA-256 and loss-sequence comparisons with zero numerical
  tolerance, plus observed rollback and hard-limit enforcement;
- grouped console checks into the five binding categories while retaining all
  individual checks and stable evidence IDs in `result.json`;
- implemented a runtime-guarded `agent/request.redacted.json` package without
  raw tensors, home paths, strategy fields/directories, failure-label spellings,
  diagnosis expectations, or repair preset language;
- added real-process coverage for both safe strategies, the loadable incomplete
  strategy, optimizer corruption, missing base, incomplete temp directory,
  two-step rollback violation, and unexpected worker exit;
- ran and preserved demo-profile process artifacts for all three strategies and
  recorded the actual PIDs, exit codes, rollback, and gate outcomes.

Codex did not implement GPT-5.6 providers, contract inference, failure analysis,
repair schemas or execution, a second repaired crash, HTML, packaging, Docker,
Hugging Face support, plugin discovery, or another framework adapter.
