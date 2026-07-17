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
