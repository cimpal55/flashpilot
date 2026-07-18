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

## Milestone 4

Codex performed the following concrete work under the binding Prompt 4 scope:

- verified the installed official OpenAI SDK's current `responses.parse`
  signature and `store` support against official developer documentation;
- added strict checkpoint-contract, failure-analysis, repair-plan, action,
  validation, provider-metadata, and one-attempt admission schemas;
- retained the complete public repair-action enum while advertising only the
  six Section 28.5 actions from `NativePyTorchAdapter`;
- implemented live contract and failure providers using the Responses API,
  `model="gpt-5.6"`, Pydantic structured parsing, `store=False`, and no tools;
- implemented contract and failure fixture/replay providers with explicit
  deterministic-local provenance because no API key was available;
- added fixed prompts that deny command execution, patching, tolerance changes,
  check disabling, recovery-verification claims, and repair application;
- extended the Prompt 3 sanitized boundary to cover every newly specified
  forbidden label spelling plus local paths, URLs, secret-like data, command or
  patch text, raw-data fields, and numeric arrays;
- implemented deterministic contract minimums, rollback enforcement,
  unsupported-state reporting, evidence validation, duplicate/conflict checks,
  and accepted/rejected/unsupported repair-action classification;
- persisted redacted requests, parsed responses, validation results, prompt and
  schema versions, provider labels, model alias, timestamps, response IDs, and
  request hashes without persisting credentials;
- added an exclusive attempt-one admission record that performs no repair and
  rejects a second admission;
- added recording-SDK mocks, structured fixture tests, invalid-output tests,
  disclosure tests, guardrail tests, capability tests, and at-most-once tests.

Codex did not implement repair execution, a repaired strategy, a second crash,
Prompt 5 orchestration, policy planning, report narration, HTML, packaging,
Docker, Hugging Face support, plugins, or another adapter.

## Milestone 5

Codex performed the following concrete work under the binding Prompt 5 scope:

- replaced the two default local-answer fixtures with the independently
  accepted secret-free GPT-5.6 structured responses and preserved their live
  metadata in explicit sidecars;
- added a strict six-boolean `CheckpointStrategyConfig` and a fixed typed
  action-to-field mapping with no command, patch, path, or model-text execution
  surface;
- implemented one exclusive repair attempt that copies the incomplete config,
  applies exactly the six NativePyTorchAdapter actions, assigns a new strategy
  ID, and records accepted, unsupported, rejected, and applied actions;
- kept `change_supported_checkpoint_strategy` recorded as unsupported while
  reusing the existing supported adapter-aware checkpoint contract;
- connected the initial real crash, failed gate, captured-response replay,
  deterministic validation, bounded repair, second real crash, new-process
  restore, and final exact Recovery Gate in isolated run directories;
- added whole-directory before/after checkpoint fingerprints proving that the
  historical failed checkpoint is not modified;
- added post-verification logical-byte comparison that separates recurring
  repaired bytes from the one-time immutable base and makes no physical-write
  claim;
- added authoritative `result.json`, deterministic `report.md`, the fixture
  `demo` path, and read-only `audit`, `verify`, and `replay` commands;
- added unit and integration tests for the six field changes, unsupported
  strategy action, one-attempt limit, second-attempt refusal, original
  checkpoint immutability, real second-process recovery, exact trajectory, and
  artifact/CLI replay behavior.

Codex did not make a live API call or implement Prompt 6 work, HTML, packaging,
Docker, Hugging Face support, plugin discovery, a policy planner, numeric
CrashScore, a GPT report narrator, another adapter, or weakened gate behavior.

## Milestone 6

Codex performed the following concrete work under the binding Prompt 6 scope:

- converted the primary fixture demo into a staged Rich console experience
  rendered from the verified Prompt 5 result, with distinct GPT recommendation
  and deterministic guardrail decisions;
- kept the savings headline behind the final Recovery Gate and displayed
  recurring full/repaired logical bytes and one-time base cost separately;
- added an offline `flashpilot doctor` covering Python, platform, CPU,
  dependencies, fixture data, output writability, hidden API-key presence, and
  the Windows directory-fsync limitation;
- added a self-contained static `report.html` rendered only from persisted
  `result.json`, with no server, external asset, or GPT narrator;
- made captured fixture data wheel-safe through installed data files while
  retaining source-tree fixture/replay behavior and provenance;
- added unique full-UUID default run directories and printed the resolved path
  before the experiment starts;
- preserved `audit`, `verify`, `replay`, `live-contract`, and `live-failure`;
- rewrote the README beginning around the value proposition, 60-second judge
  path, proof, GPT-5.6 role, verified environment, limits, positioning, prior
  art, and Codex contribution;
- built and retained a pure-Python wheel, installed it with dependencies into a
  fresh standard virtual environment, and ran `doctor` and the full primary
  demo from outside the repository;
- diagnosed and removed one CP1251-incompatible decorative console character
  found only in the first installed-wheel judge run, then rebuilt and repeated
  the entire clean-install verification successfully;
- added focused tests for doctor secrecy and prerequisites, unique default run
  paths, every visible judge stage and status, storage wording, HTML
  self-containment, and artifact generation.

Codex did not make a live GPT-5.6 call or add Prompt 7/8 work, a desktop UI,
Hugging Face, CUDA, Docker, another adapter, plugin discovery, repository
scanning, a policy planner, numeric CrashScore, or new recovery research.
