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
  Prompt 0 development environment; checkpoint durability behavior remains
  unimplemented and unverified.
