# Devpost submission copy

## Title

FlashPilot

## Tagline

Reduce checkpoint writes only when recovery is proven.

## Category answer

**Developer Tools.** FlashPilot is a checkpoint recovery qualification and
verification harness for PyTorch training. It deliberately terminates a real
training process, restores in a new process, and verifies continuation against an
uninterrupted control. GPT-5.6 infers the checkpoint contract and diagnoses an
observed recovery failure from sanitized structured evidence. Deterministic code
filters its typed repair proposal, permits one bounded repair, reruns the crash
test, and reports logical storage reduction only after the Recovery Gate passes.

## Short description

FlashPilot proves whether a loadable AI checkpoint can resume correctly, uses
GPT-5.6 to diagnose failed recovery and propose bounded repairs, and measures
logical checkpoint reduction only after deterministic re-verification.

## Problem

A checkpoint may exist, pass checksums, load successfully, and restore model
weights while still being unsafe for continued training. Missing optimizer,
scheduler, or random-number-generator state can silently alter the optimization
trajectory after a crash. File integrity alone does not prove resumability.

## Solution

FlashPilot treats recovery as an observable system property. It runs a seeded
uninterrupted control, atomically commits a valid but incomplete checkpoint,
terminates the worker, restores in a distinct process, and compares the resumed
trajectory with the control. A failed gate produces bounded redacted evidence
for GPT-5.6. After deterministic action filtering, FlashPilot applies one typed
repair in a new isolated run and repeats the real crash and restore. Only the
second deterministic Recovery Gate may declare the repair verified.

## How GPT-5.6 was used

GPT-5.6 has two structured, non-decorative roles. First, it infers a checkpoint
contract from the human objective, native workload capabilities, and save/restore
summary. Second, it diagnoses the observed failed Recovery Gate and proposes
evidence-linked repair actions. The live providers use the official Responses
API structured parser with `model="gpt-5.6"`, Pydantic schemas, `store=false`, and
no tools. The judge path clearly replays independently accepted secret-free live
captures; no API key or application network access is required. GPT cannot
execute commands, change tolerances, repair corrupted bytes, or declare success.

## How Codex was used

Codex implemented and debugged the deterministic CPU workload, native adapter,
atomic checkpoint protocol, manifest and checksum validation, real subprocess
termination, new-process restore, 24-check Recovery Gate, redaction boundary,
strict GPT schemas, allowlisted six-field executor, immutable-history proof,
reports, Rich console, doctor command, tests, Windows pytest isolation, wheel,
clean-install validation, and submission documentation. The human chose the
narrow P0 scope, primary valid-incomplete failure, blind GPT boundary, exact
comparison policy, one-attempt limit, six repair actions, and proof-before-savings
rule.

## Technical implementation

- Python 3.11+ package with PyTorch CPU, Pydantic, Typer, Rich, and the OpenAI SDK.
- Tiny Transformer-like workload with a frozen base, trainable residual adapter,
  nonzero dropout, seeded stochastic state, and step-derived synthetic batches.
- Temporary-sibling writes, file fsync, SHA-256 manifests, completion marker,
  atomic directory rename, containment checks, and immutable base identity.
- Parent-owned real worker termination after validated commit and recovery in a
  distinct process.
- Exact Recovery Gate comparing integrity, required training state, process
  recovery, rollback, final trainable state, evaluation, and loss trajectory.
- Strict typed GPT identifiers and action enum; only six native actions map to a
  six-boolean copied strategy configuration, once.
- Canonical `result.json` with deterministic Markdown, self-contained HTML, and
  Rich views; audit, verify, and offline replay commands.

## Measured result

On the independently accepted Windows 11, Python 3.12.13 demo-profile run, the
initial valid incomplete checkpoint failed 9 exact Recovery Gate checks. After
one bounded repair and a second real crash/restore, all 24 checks passed with
`atol=0.0` and `rtol=0.0`. The safe-full recurring checkpoint measured 126,218
logical bytes; the repaired recurring adapter-aware checkpoint measured 32,743,
a reduction of 93,475 bytes, or 74.06%. The immutable frozen base measured
93,987 bytes and is reported separately as a one-time cost. Internal workflow
runtime was 16.75 seconds and total installed-command runtime was 20.41 seconds
for that accepted invocation; timing is environment-specific.

## Differentiation and prior art

FlashPilot does not claim adapter-only persistence, checkpoint scheduling,
compression, incremental checkpointing, atomic writes, checksums, or chaos
testing as new. Its contribution is the integrated developer workflow: contract
inference, real cross-process crash and restore, comparison with a control,
evidence-bounded GPT diagnosis, typed repair, mandatory re-verification, and
post-proof measurement. It is a qualification harness, not a replacement for
PyTorch, Hugging Face, DeepSpeed, NeMo, or their serializers.

## Limitations

The verified submission supports one controlled CPU-only
`NativePyTorchAdapter` workload on Windows 11 and Python 3.12.13. Python 3.11 is
the compatibility target but was not locally verified. Windows directory fsync
is unavailable through Python and remains best-effort. There is no arbitrary
repository execution, CUDA, distributed training, additional framework adapter,
plugin discovery, policy planner, or autonomous patching. Fixture replay applies
to its captured schema and failure shape. Fresh dependency installation may need
the configured package index or cache. Physical NAND writes, write amplification,
and SSD lifetime were not measured.

## Future roadmap

Future work can qualify additional adapters and operating systems, add
distributed and partial-write crash scenarios, validate previous-checkpoint
fallback, exercise broader model topologies, and add continuous integration.
Each addition must retain strict containment, typed repair, immutable history,
and the rule that only a passing deterministic Recovery Gate authorizes storage
claims.
