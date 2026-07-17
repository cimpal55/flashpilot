# Engineering decisions

## D-001: Native PyTorch only in P0

P0 uses one controlled pure-PyTorch workload and will expose only
`NativePyTorchAdapter`. Multiple framework adapters, discovery, repository
scanning, and AST analysis are out of scope.

## D-002: CPU-first deterministic control

The control workload seeds Python, NumPy, and Torch; uses deterministic Torch
algorithms; fixes Torch to one CPU thread; derives each batch from the seed and
step; and evaluates on a fixed batch. Prompt 0 requires exact repeated-control
equality. The later cross-process Recovery Gate tolerance policy must be based on
empirical evidence and must never be silently relaxed.

## D-003: Training includes nonzero stochasticity

The Transformer and residual adapter contain dropout during training. Evaluation
switches the model to evaluation mode. This makes Torch RNG restoration a real
continuation requirement rather than metadata with no observable effect.

## D-004: Frozen base and trainable residual adapter

All embeddings, Transformer blocks, normalization, and output-head parameters
are frozen. Only the residual bottleneck adapter trains. This creates a future
honest comparison between full and adapter-aware checkpoints without claiming
adapter checkpointing as novel.

## D-005: Control comparison is mandatory

Loadability is not proof of correct continuation. The uninterrupted control is
the deterministic reference for final trainable state, fixed evaluation, and
continued trajectory.

## D-006: Per-invocation pytest temporary paths and no cache provider

The earlier fixed `.pytest-local/temp` and `.pytest-local/cache` design failed
when the same Windows checkout was used across host-user and sandbox security
contexts. A directory created by one principal could be visible but not
removable or writable by the other, causing `tmp_path` fixture setup to fail
before product tests ran. Moving or recreating that shared directory only
changed its current owner and did not solve the cross-context design flaw.

Pytest now uses its normal unique per-user/per-invocation operating-system
temporary directory. The default project configuration disables the cache
provider with `-p no:cacheprovider`, because pytest cache state is not required
for correctness, and contains neither `--basetemp` nor `cache_dir`. This avoids
shared repository ACL state without administrator rights, ACL rewriting,
hardcoded users, or hardcoded home-directory paths. Independent host-user
verification with isolated temporary paths passed 104 tests with the one
expected platform symlink skip; the corrected default project command is the
permanent equivalent and is verified in the build log.

## D-007: Safe full is the only Prompt 1 checkpoint strategy

`safe_full` persists the complete model, optimizer, scheduler, global step,
Python RNG, NumPy RNG, Torch RNG, immutable profile configuration, and loss
history. Direct restore loads only after manifest and SHA-256 validation and
uses `torch.load(..., weights_only=True)` for tensor-bearing payloads. The
direct-restore comparison is not a Recovery Gate verdict.

## D-008: Atomic commit and Windows durability boundary

Checkpoint payloads are written to a unique temporary sibling directory, file
contents are flushed and `fsync`ed, SHA-256 checksums and the manifest are
written, and `COMPLETE` is created before a same-filesystem directory rename.
No committed callback is invoked until the rename succeeds. Linux and other
POSIX systems attempt directory `fsync` before and after rename and fail closed
if it fails. Python does not expose usable directory `fsync` on Windows, so
payload and metadata file synchronization plus directory rename are implemented,
while directory metadata durability is explicitly reported as best-effort.

## D-009: Resolve containment before managed I/O or retention

Manifest paths must be normalized relative paths. Runtime paths are resolved
against an explicit run sandbox; traversal, absolute managed paths, containment
escapes, and symlink escapes are rejected. Retention considers only validated
direct checkpoint children, keeps the newest requested count, and separately
protects the explicitly supplied latest verified checkpoint. Prompt 1 does not
itself declare any checkpoint Recovery-Gate verified.

## D-010: Fixed native adapter boundary

P0 exposes one minimal `TrainerAdapter` implementation,
`NativePyTorchAdapter`, through `get_adapter("native-pytorch")`. The adapter
reports deterministic capabilities and save/restore summaries and partitions
the controlled model into frozen-base and trainable-adapter state. There is no
plugin discovery, entry-point loading, framework detection, external adapter
loading, command construction, or repair execution.

## D-011: Immutable base plus recurring adapter state

`safe_adapter_aware` stores the frozen non-adapter state once at the fixed,
contained `artifacts/frozen-base/base.pt` location. Its identity includes the
profile and payload SHA-256. A recurring checkpoint references that identity,
path, hash, and size and stores the adapter, optimizer, scheduler, global step,
Python/NumPy/Torch RNG, immutable profile, manifest, checksums, and completion
marker. Existing base artifacts are validated and compared tensor-for-tensor
with the current runtime before reuse; they are never replaced in place.

## D-012: Loadability and continuation correctness are separate

`missing_training_state` is intentionally a valid, checksum-valid checkpoint.
It restores the frozen base, trainable adapter, global step, profile, and loss
history, while its manifest explicitly omits optimizer, scheduler, and
Python/NumPy/Torch RNG state. Direct loading is therefore allowed. Continued
training uses the real dropout-enabled path and diverges from the uninterrupted
control, demonstrating that integrity and loadability do not prove exact
continuation. Prompt 2 does not add or simulate a Recovery Gate.

## D-013: Separate recurring structure from first-write cost

Prompt 2 reports three adapter-aware byte quantities separately: immutable base
artifact bytes, recurring checkpoint bytes, and their first-checkpoint total.
The structural comparison is `safe_full` recurring bytes minus adapter-aware
recurring bytes. It is not called a storage-savings verdict because the
deterministic Recovery Gate is not implemented yet. No padding, synthetic
baseline inflation, physical NAND estimate, or write-amplification claim is
permitted.

## D-014: Parent-owned real process termination

The checkpoint worker is a real Python subprocess that remains alive after it
emits one structured `checkpoint_committed` event. The event is constructed
only after the atomic commit callback has observed the final renamed directory.
The parent requires the event PID to match the launched Python process, resolves
the event's relative checkpoint path inside the run sandbox, and validates the
checkpoint before calling `subprocess.Popen.kill`. It records and verifies the
exit code, then launches recovery through a new process and rejects PID reuse.

On Windows, venv and console-script redirector executables may introduce a
launcher PID distinct from the actual Python PID. Prompt 3 therefore launches
`sys._base_executable` directly and supplies the active venv site-packages and
project source paths through a trusted child environment. The observed Windows
termination primitive is `TerminateProcess` through `Popen.kill`; the demo exit
code was 1. POSIX uses the active Python executable and expects `SIGKILL`.

## D-015: Exact cross-process comparison, with zero tolerance

The Recovery Gate uses exact equality only. Trainable state, evaluation logits,
optimizer state, scheduler state, and each RNG state use exact SHA-256 digest
equality. The loss history uses exact float-sequence equality. Both CI tests and
the demo profile passed across killed and newly launched processes for
`safe_full` and `safe_adapter_aware`, so no nonzero tolerance was empirically
needed. The recorded policy is `atol=0.0`, `rtol=0.0`; any difference fails.
GPT, fixtures, CLI options, and future repair code may not change this policy.

## D-016: Rollback is an observed process quantity

Achieved rollback is `last_completed_step - committed_checkpoint_step`. The
normal deterministic crash event is emitted immediately after commit, yielding
zero rollback. A real-process negative test allows the worker to complete two
additional steps after the committed snapshot and before emitting the event;
with a one-step hard limit, the gate observes two rollback steps and fails only
`rollback.hard_limit`. Rollback is not inferred from checkpoint interval alone.

## D-017: Redacted failure artifact boundary

A failed gate writes `agent/request.redacted.json` containing bounded
capabilities, a local minimum checkpoint contract, sanitized manifest fields,
restore observations, individual gate checks, state/trajectory differences,
relative crash metadata, and stable evidence IDs. It excludes raw tensors,
absolute home paths, the strategy field, strategy-bearing checkpoint directory,
failure label spellings, expected diagnosis, repair preset language, and
comments about deliberate omission. A runtime guard and tests enforce this
before the artifact is persisted. Prompt 3 does not send the artifact anywhere.

## D-018: Binary corruption is fail-closed

Changing one byte of `optimizer.pt` causes the recovery worker to exit during
SHA-256 validation before tensor deserialization. No Recovery Gate result,
failure-analysis request, policy diagnosis, or repair scenario is generated for
that invalid checkpoint. A missing external base fails at the equivalent
pre-deserialization validation boundary.

## D-019: Exactly two bounded GPT-5.6 roles

Prompt 4 exposes only checkpoint-contract inference and blind recovery-failure
analysis. Both live providers use the official OpenAI Python SDK,
`responses.parse`, `model="gpt-5.6"`, Pydantic structured outputs, and
`store=False`; neither call supplies tools. Fixture providers implement the
same typed protocols and are labeled `fixture` with provenance
`deterministic_local_fixture`. That provenance is deliberately distinct from a
captured live response because `OPENAI_API_KEY` was unavailable during local
validation. Live validation remains a manual task rather than a fabricated
claim.

## D-020: The sanitized artifact is the complete diagnosis boundary

The live failure provider accepts only `SanitizedFailureArtifact`, reuses the
Prompt 3 forbidden-disclosure guard, and additionally rejects absolute local
paths, URLs, secret-like data, command or patch text, prohibited raw-data
fields, and raw numeric arrays. The API request contains only a fixed system
prompt and canonical JSON from that typed artifact. No tools, arbitrary files,
raw tensors, dataset samples, or API credentials are available to the model.

## D-021: Model output proposes; deterministic code classifies

The public schema retains all 21 known repair actions. The active native
adapter advertises only the six binding P0 capabilities. Deterministic
post-parse validation classifies supported evidence-linked actions as accepted,
known non-native actions as unsupported, and duplicates, unsafe content, or
unrecognized evidence as rejected. It also rejects tolerance changes, disabled
checks, recovery-verification claims, and claims that corrupted bytes were
repaired. Prompt 4 persists the proposal and classification but has no repair
executor, repaired strategy, or second crash.

## D-022: One-attempt state is admission-only in Prompt 4

An exclusive contained admission record can reserve repair attempt number one
and rejects a second reservation for the same run. The record explicitly says
`execution_performed=false`. This proves the hard one-attempt bound without
prematurely implementing Prompt 5 repair execution.

## Binding decisions for later milestones

- The primary failure will be a valid, loadable checkpoint that intentionally
  omits optimizer, scheduler, and relevant RNG state. Corrupted bytes must be
  rejected, never narrated as repaired.
- P0 repair execution will implement only the six actions in Section 28.5 by
  copying a typed checkpoint-strategy configuration and changing explicit
  boolean fields. Exactly one repair iteration is allowed.
- GPT-5.6 will not receive a failure-injection label, expected diagnosis, repair
  preset name, or comments revealing deliberately omitted state.
- The deterministic Recovery Gate alone proves recovery. Deterministic selection
  follows correctness and rollback constraints before storage metrics.
- Numeric CrashScore, arbitrary patches, generic policy planning, and GPT report
  narration are omitted.
- Physical NAND writes, write amplification, and SSD lifetime are not measured.
  Reducing logical writes may reduce overhead, but no physical-lifetime claim is
  permitted.
- Linux is the intended strongest atomic-commit target. Windows is the current
  development environment; file synchronization and rename are tested, but
  directory `fsync` remains unavailable and durability is therefore best-effort.
