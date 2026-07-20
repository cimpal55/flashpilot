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

## Milestone 8

Codex performed the following final-audit and submission-package work after the
human independently accepted Prompt 6 and intentionally skipped Prompt 7:

- audited the binding scope, repository status, wheel contents and hash, live
  provider settings, fixture provenance, redaction boundary, process evidence,
  gate authority, repair surface, attempt limit, checkpoint immutability,
  corruption rejection, persisted metrics, and prohibited physical claims;
- compared the accepted `result.json`, deterministic Markdown, self-contained
  HTML, Rich renderer, and README measurement vocabulary and values;
- found and corrected one release-documentation gap: `report.md` did not carry
  the mandatory logical-versus-physical measurement disclaimer;
- added a focused result-derived Markdown consistency test without changing any
  gate, tolerance, guardrail, repair action, or product test condition;
- finalized the judge-oriented README responsibility boundary, exact accepted
  metrics, installation qualification, security model, limitations, roadmap,
  repository link, and pending human license decision;
- created the under-three-minute English voiceover, complete Devpost-ready
  English copy, and a release checklist that leaves license, video, `/feedback`,
  release publication, and submission to the human;
- documented that `result.json` is canonical and that no redundant
  `report.json` should be created from the master-plan naming mismatch;
- rebuilt the prebuilt wheel after the report correction and reran the full
  clean installed judge path from outside the repository;
- recorded actual quality-gate and clean-judge outputs in the build log.

Codex did not make a live API call, implement Prompt 7, add recovery behavior,
publish a release, upload a video, submit Devpost, choose a license, or invent a
`/feedback` Session ID.

## Milestone 9

Codex performed the following VNext foundation work on the dedicated
`codex/qualification-layer-v0.2` branch:

- preserved the immutable `flashpilot-v0.1.0` tag and captured a clean baseline
  full suite and fixture demo before editing;
- added strict requirement, recovery-source, exactness, persistence-item,
  persistence-contract, and two-profile types without changing the v0.1 GPT
  schemas or captures;
- implemented fail-closed validation for UNKNOWN state, contradictory sources,
  missing evidence, missing identity controls, and non-exact state under the
  exact-training-resume profile;
- implemented deterministic local-minimum merging that can strengthen a weaker
  proposal but cannot silently repair contradictions, accept extra state, raise
  RPO, or change context;
- added native exact-resume and model-only minimum contracts and an explicit
  migration from the already accepted v0.1 native checkpoint contract;
- implemented canonical JSON and SHA-256 contract identity with stable ordering;
- generated three draft-2020-12 JSON Schema files and added a test that rejects
  checked-in schema drift;
- added focused round-trip, hashing, malformed, contradictory, UNKNOWN,
  exactness, minimum-merge, migration, model-only, and schema tests;
- updated repository guidance, architecture, decisions, contributions, and the
  build log for the vNext branch boundary.

Codex did not begin static checkpoint audit, framework detection, attestations,
Hugging Face support, JUnit output, CI workflow, packaging, signing, or any
Milestone 10+ functionality.

## Milestone 10

Codex performed the following VNext static-audit work on the existing dedicated
v0.2 branch:

- added the `audit-checkpoint` CLI with deterministic `auto`, native PyTorch,
  Hugging Face Trainer, and unknown layout outcomes;
- added strict typed audit results whose only statuses are `PASS`, `WARN`,
  `FAIL`, and `UNKNOWN`, with invariant `recovery_verified=false`;
- reused native manifest, checksum, completion, containment, immutable-base,
  and weights-only validation without running training or restoring a worker;
- implemented exact-resume and model-only state requirements, including all
  nine native Persistence Contract state IDs;
- added a narrow metadata-first Hugging Face audit for Trainer progress,
  optimizer, scheduler, RNG, weight files, checkpoint-step identity, training
  arguments, lifecycle markers, and model/base configuration identity;
- added a bounded safetensors metadata reader and refused to unpickle
  `training_args.bin` or unknown files;
- added deterministic `audit.json`, Markdown, and per-requirement JUnit output,
  plus stable status and unsupported-configuration exit codes;
- added focused fixtures for complete native, missing native training state,
  corrupted native payload, interrupted native temporary state, complete HF,
  HF model-only under both profiles, unknown layout, unsafe training arguments,
  malformed safetensors, and untrusted extra files;
- preserved the UUID pytest basetemp plugin, v0.1 Recovery Gate, fixture demo,
  repair boundary, and captured agent fixtures unchanged.

Codex did not begin recovery attestation, attestation verification, full HF
qualification, a Trainer adapter/callback, script execution, process killing,
new repairs, CI policy, packaging, signing, or any Milestone 11+ functionality.

## Milestone 11

Codex performed the following recovery-attestation work on the existing v0.2
branch:

- added strict `RecoveryAttestationV1`, evidence-manifest, dependency
  environment, and verification-result models plus generated public schemas;
- emitted an attestation from the existing native demo only after the unchanged
  repaired Recovery Gate persisted a 24/24 exact VERIFIED result;
- retained the existing result, Markdown, HTML, gate, repair, storage, and agent
  schemas unchanged and treated them as input evidence;
- added a closed evidence inventory with run-relative path, size, and SHA-256 for
  every experiment artifact and fixed circular-statement exclusions;
- bound native exact Persistence Contract, repaired checkpoint directory,
  immutable base, dependency environment, Git commit, honest source-tree state,
  process IDs, trajectory digests, gate counts, RPO/RTO, and verified bytes;
- added deterministic validation of native checkpoint manifests, payload
  checksums, completion, base identity, reports, result metrics, and contract;
- added `verify-attestation` with Rich success output and stable invalid/tampered
  exit code `4`;
- added deterministic eight-check attestation JUnit output;
- added focused tests for verified emission, failed-gate refusal, deterministic
  verification, one-byte evidence mutation, missing evidence, checkpoint
  mutation, refreshed external hashes versus native checksums, report mismatch,
  contract mismatch, metric mismatch, path traversal, CLI exits, Rich wording,
  and generated schema drift;
- stated prominently that v1 is unsigned integrity evidence and not publisher
  authentication or certification.

Codex did not add cryptographic signing, a registry, OIDC provenance, a
HuggingFaceTrainerAdapter, a callback, HF training execution, a generic qualify
command, CI policy, release packaging, or any Milestone 12+ functionality.

## Milestone 12

Codex performed the following Hugging Face Trainer qualification work on the
existing dedicated v0.2 branch:

- added an `hf` optional dependency group for bounded Transformers 5 and
  Accelerate 1 versions;
- added one explicit `HuggingFaceTrainerAdapter` without altering the frozen P0
  native registry, plugin discovery, entry points, auto-detection, or repairs;
- added a verdict-free `FlashPilotTrainerCallback` that emits only contained
  post-save checkpoint lifecycle evidence;
- added a local tiny `PreTrainedModel`, deterministic synthetic dataset,
  sequential CPU training, dropout, and exact fixed evaluation with no Hub
  model or dataset downloads;
- added an external launcher that copies the selected script into the run
  sandbox, strips API keys, forces offline controls, uses `shell=False`, kills
  the exact checkpoint process, and resumes in a distinct process;
- added an exact 13-check HF Recovery Gate covering required files, real
  termination, distinct recovery, final step, full loss trajectory, and
  trainable/evaluation/optimizer/scheduler state digests;
- proved the complete Trainer checkpoint resumes exactly and reports logical
  bytes only after VERIFIED;
- proved a valid loadable Trainer model-only checkpoint omits optimizer,
  scheduler, and RNG state and genuinely diverges through the real
  dropout-enabled continuation path;
- extended the unsigned attestation format through an explicit Transformers
  branch with a separate deterministic HF persistence contract, environment
  identity, closed evidence inventory, safetensors loading, state-file checks,
  and exact result/report verification;
- added the `qualify hf-trainer` CLI and focused unit/integration coverage while
  retaining the existing native fixture demo and Recovery Gate behavior.

Codex did not begin CI workflow work, global JUnit policy, stable qualification
exit-code policy, packaging, release automation, signing, generic Trainer-script
compatibility, another adapter, or any Milestone 13+ functionality.

## Milestone 13

Codex performed the following CI and developer-workflow work on the existing
dedicated v0.2 branch:

- added the closed `CIPolicyV1` schema and bounded safe YAML loader for exact
  profile, fail-closed UNKNOWN, allowlisted process termination, RPO/RTO, and
  attestation requirements without arbitrary scripting;
- added canonical public exit constants `0`, `2`, `3`, `4`, and `5` and applied
  them across static audit, native/HF qualification, evidence verification, and
  unsupported configurations;
- normalized audit, native repair-loop, direct native crash, and HF results into
  shared typed CI evidence without parsing logs or creating another verdict;
- added deterministic qualification `junit.xml` with exact gate check IDs and
  expected/actual failures, plus `job-summary.md` for every audit and
  qualification;
- added `emit-junit --run-dir --policy`, which reuses local result models,
  verifies attested CI files byte-for-byte, reports exact policy failures, and
  refuses invalid or missing attested evidence;
- added the generic `qualify native-pytorch` command as a thin entry point over
  the preserved native red-to-green core;
- added a non-installed GitHub Actions example that runs HF qualification,
  static audit, policy enforcement, GitHub job summary, always-on diagnostics,
  and success-only attestation upload;
- added a hash-bound strict HF RNG metadata bridge so real standard Trainer RNG
  checkpoints pass safe static audit without unrestricted pickle loading;
- added focused tests for safe policy parsing, schema drift, weak/unknown policy
  rejection, stable exits, exact JUnit failure IDs, Markdown summaries,
  pass/fail policy behavior, no mutation of attested bundles, workflow upload
  conditions, real HF audit compatibility, and RNG hash mismatch.

Codex did not begin clean wheel/source installation, version bumping, release
checklists, publishing, signing, another adapter, active hosted workflow, or any
Milestone 14+ functionality.

## Milestone 14

Codex performed the following v0.2 packaging work on the existing dedicated
qualification branch:

- synchronized package and runtime versions at `0.2.0`, declared Python
  `>=3.11`, Apache-2.0, project URLs, classifiers, and release metadata;
- kept the base dependencies HF-free and declared Transformers, Accelerate,
  and safetensors only through the bounded `hf` optional group;
- made the installed offline HF worker the default `qualify hf-trainer` entry
  while retaining the explicit script contract and stable actionable exit `5`
  when extras are absent;
- packaged fixtures, public schemas, policy/workflow examples, the HF source
  example, and the release checklist into both distribution formats;
- added focused packaging tests covering version/license synchronization,
  dependency separation, installed resources, the default worker, README
  paths, and missing-extra behavior;
- built and inspected the wheel and source distribution with `build` and
  `twine`, then recorded their exact sizes and SHA-256 digests;
- installed the wheel into two fresh environments outside the FlashPilot
  repository and proved the base fixture/native path separately from the
  complete installed HF path;
- scanned clean-run outputs and both release archives for the injected secret
  sentinels and credential-shaped values, with zero matches;
- documented the exact supported paths, limitations, Windows validation
  boundaries, release architecture, decisions, and human checklist.

Codex did not publish a package, create a tag or commit, enable a hosted
workflow, add signing, begin a V0.3 roadmap item, broaden Trainer compatibility,
add an adapter, or change the frozen native repair surface.

## V0.3 roadmap item 1 - PyTorch Lightning adapter

Codex implemented only the first V0.3 roadmap item:

- added an explicit optional `PyTorchLightningAdapter` with fixed capabilities,
  bounded safe checkpoint inspection, and no repair or discovery surface;
- added an installed CPU-only Lightning worker and source example using
  deterministic synthetic inputs and real dropout;
- added parent-controlled process termination after a committed, safely
  loadable checkpoint and recovery in a distinct process;
- added a strict 14-check exact-resume gate covering checkpoint state,
  termination, process identity, progress, loss history, model/evaluation,
  optimizer, and scheduler digests;
- demonstrated that a complete checkpoint resumes exactly and that a real
  `weights_only=True` checkpoint loads but diverges without artificial output
  manipulation;
- extended the existing JUnit, job-summary, persistence-contract, attestation,
  and offline verification surfaces to verified Lightning evidence;
- added focused adapter, dependency, CLI, full qualification, negative-path,
  CI, and attestation tests.

Codex did not begin conversion equivalence, partial-write fuzzing,
previous-valid fallback, randomized fault timing, SARIF, distributed training,
CUDA, plugin discovery, or another framework adapter.

## V0.3 roadmap item 2 - checkpoint conversion equivalence

Codex implemented only the second V0.3 roadmap item:

- added four explicit typed conversion contracts: full-to-PEFT,
  PEFT-to-merged, sharded-to-consolidated, and version-upgrade-resume;
- added checksummed, closed-inventory, bounded, atomically committed source and
  candidate artifacts whose provenance binds the exact source directory hash;
- added deterministic dense-to-rank-2 extraction, PEFT merge, shard
  consolidation, and complete training-state schema upgrade paths;
- added exact or explicitly tolerance-bounded parameter/output comparisons,
  plus distinct-process exact continuation checks for upgraded training state;
- added `flashpilot qualify conversions` and a narrow
  `flashpilot compare-checkpoints` command backed by the same typed comparator;
- added JSON Schemas, Markdown/JUnit output, tamper/provenance/semantic-failure
  tests, and before/after immutability evidence.

Codex did not claim recovery verification or storage savings and did not emit a
recovery attestation. Partial-write fuzzing, previous-valid fallback,
randomized fault timing, SARIF, distributed/CUDA training, discovery, and
additional adapters were not started.

## V0.3 roadmap item 3 - partial-write fuzz matrix

Codex implemented only the third V0.3 roadmap item:

- added the candidate `flashpilot fuzz-checkpoint --scenario partial-write
  --iterations 100` interface with bounded deterministic iterations;
- added a strict two-rank fuzz artifact, manifest-bound completion marker,
  checksum cross-check, closed inventory, containment, size limit, and atomic
  source commit;
- added six cases per iteration for truncation, missing shard, stale manifest,
  checksum mismatch, duplicate rank, and prematurely exposed reordered writes;
- required exact typed rejection reasons for corrupt cases and zero acceptance
  across every incomplete reordered-write observation;
- added source/candidate immutability hashes, deterministic schedule hashing,
  JSON Schemas, Markdown, JUnit, and job-summary evidence;
- added focused schema, validator, repeatability, redaction, CLI, bounded-input,
  and full-matrix tests.

Codex did not begin previous-valid fallback, randomized fault timing, SARIF,
distributed/CUDA qualification, discovery, or another adapter. The fuzz result
does not claim recovery verification, report bytes or savings, or emit an
attestation.

## V0.3 roadmap item 4 - previous-valid checkpoint fallback

Codex implemented only the fourth V0.3 roadmap item:

- added a fixed native producer that commits valid `safe_full` checkpoints at
  steps 2 and 4 in one process and emits a strict two-checkpoint event;
- added parent-owned termination after both checkpoints validate, followed by
  durable corruption of only the newest model payload;
- required exact checksum rejection, a `(2,)` valid-candidate inventory, and
  exact selection of the immediate predecessor;
- reused the existing distinct recovery worker and unchanged 24-check exact
  Recovery Gate with an honest two-step achieved and maximum RPO;
- added seven typed selection checks and before/after fingerprints preserving
  both the previous checkpoint and rejected newest evidence;
- added `qualify previous-valid-fallback`, strict JSON Schemas, Markdown,
  JUnit, job-summary output, packaging coverage, and focused process,
  redaction, containment, schema, and unsupported-mode tests.

Codex did not begin randomized fault timing, SARIF, distributed/CUDA
qualification, discovery, or another adapter. It did not repair or delete the
corrupt checkpoint, call GPT, report bytes or storage savings, or emit an
attestation.

## V0.3 roadmap item 5 - repeated randomized fault timing

Codex implemented only the fifth V0.3 roadmap item:

- added a strict seeded schedule whose four-trial blocks each cover RPO 0, 1,
  2, and 3 at valid completed-step boundaries;
- composed the existing real native `safe_full` process-kill experiment and
  unchanged 24-check exact Recovery Gate for every isolated trial;
- required a distinct recovery process, verified producer termination, exact
  continuation, and the fixed three-step maximum RPO in every trial;
- bound the aggregate to its regenerated schedule, every complete trial
  directory fingerprint, and every underlying experiment-result SHA-256;
- added `qualify randomized-fault-timing`, strict JSON Schemas, Markdown,
  per-trial JUnit, job-summary output, packaging coverage, and focused
  reproducibility, boundary, containment, redaction, process, and tamper tests;
- performed an authoritative eight-trial local run covering eight unique
  checkpoint/RPO timing pairs with all trials verified.

Codex did not begin SARIF, distributed/CUDA qualification, discovery, or
another adapter. The implementation made no GPT call, executed no repair,
reported no checkpoint bytes or storage savings, and emitted no attestation.
