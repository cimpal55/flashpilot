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

## D-006: Project-local pytest runtime paths

Pytest uses `.pytest-local/temp` for temporary fixtures and
`.pytest-local/cache` for its cache. Keeping both paths under the repository
isolates tests from host-global temporary directories and cache directories that
may carry incompatible ACLs when the same checkout is used from a normal Windows
PowerShell session and a sandboxed development process. The entire generated
directory is ignored by Git; tests continue to use `tmp_path` normally.
The test configuration creates only the ignored `.pytest-local` parent during
pytest startup because pytest does not create the parent of `--basetemp` on a
clean checkout. The configured temp and cache paths themselves are unchanged.

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
