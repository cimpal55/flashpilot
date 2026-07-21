# FlashPilot

FlashPilot is a checkpoint recovery qualification and verification harness that proves whether a training checkpoint can resume correctly after a real process failure.

## Try it — no install

**[Open the FlashPilot sandbox →](https://cimpal55.github.io/flashpilot/)**

Real qualification runs in your browser. Nothing to install. Start with the pair
that carries the argument: two Hugging Face checkpoints from the same training
script, both of which load without an error — and only one of which can actually
resume the run it claims to continue.

Then re-verify the proof yourself. The page recomputes SHA-256 over the raw
evidence bytes using your browser's own Web Crypto, and lets you corrupt any file
to watch the check fail closed. It renders and re-verifies; it never computes a
verdict.

It complements—rather than replaces—PyTorch, Hugging Face, DeepSpeed, NeMo,
and their checkpoint implementations. P0 qualifies one controlled CPU-only
native-PyTorch workflow through real termination, new-process restore, exact
trajectory comparison, evidence-bounded GPT-5.6 diagnosis, one typed repair,
and deterministic re-verification.

## Three supported v0.2 paths

### 1. 60-second fixture demo

Install the release-candidate wheel in a clean Python environment and run the
short CPU profile:

```powershell
python -m pip install .\dist\flashpilot-0.2.0-py3-none-any.whl
flashpilot doctor
flashpilot demo --provider fixture --profile ci
```

The published-package form is `python -m pip install flashpilot`. Dependency
resolution may use the configured package index or local cache. After
installation, the fixture demo requires no API key, application network access,
model download, or dataset download. It writes authoritative `result.json`,
deterministic Markdown/HTML, JUnit, job summary, and a verified integrity
attestation. The attestation can subsequently receive a detached Ed25519
signature without changing the verified payload.

Use `flashpilot demo --provider fixture` for the full-size demo profile.

### 2. Static checkpoint audit

Static audit never runs a training script and never claims verified recovery:

```powershell
flashpilot audit-checkpoint .\checkpoint-1000 `
  --framework auto `
  --profile exact-training-resume `
  --output-dir .\runs\checkpoint-1000-audit
```

It emits `PASS`, `WARN`, `FAIL`, or `UNKNOWN` plus `audit.json`, `report.md`,
`junit.xml`, and `job-summary.md`. UNKNOWN never exits zero and becomes an
explicit failure under the checked-in CI policy.

### 3. Hugging Face qualification example

Install the optional dependencies and run the installed local example. No model
or dataset is downloaded:

```powershell
python -m pip install "flashpilot[hf]"
flashpilot qualify hf-trainer `
  --profile exact-training-resume `
  --fault process-kill `
  --scenario complete `
  --run-dir .\runs\hf-complete
```

From a source checkout, `--script .\examples\hf_trainer\train.py` selects the
same documented contract explicitly. Omitting `--script` selects the installed
package's offline worker entry. A base installation without the HF extra exits
`5` with actionable `pip install 'flashpilot[hf]'` guidance.

## V0.3 PyTorch Lightning qualification

The V0.3 roadmap adds one explicit, optional PyTorch Lightning
qualification adapter. It does not join the frozen native repair adapter and
does not use plugin discovery or framework auto-detection:

```powershell
python -m pip install "flashpilot[lightning]"
flashpilot qualify lightning `
  --profile exact-training-resume `
  --fault process-kill `
  --scenario complete `
  --run-dir .\runs\lightning-complete
```

The installed worker uses a tiny CPU-only `LightningModule`, deterministic
synthetic data, and real dropout. A parent process terminates the checkpoint
worker only after `Trainer.save_checkpoint` has returned and the resulting
file passes a bounded `torch.load(..., weights_only=True)` inspection. Recovery
runs in a distinct process. The `complete` scenario must pass the exact gate
before bytes or an attestation are emitted. The real Lightning
`weights_only=True` scenario remains loadable but fails exact resume because it
omits optimizer, scheduler, RNG-bridge, and loss-history state.

## V0.3 checkpoint conversion equivalence

The second V0.3 roadmap item qualifies four fixed, local CPU conversion
contracts together:

```powershell
flashpilot qualify conversions `
  --run-dir .\runs\conversion-equivalence
```

The cases are full model to PEFT-style base plus rank-2 adapter, PEFT-style
state to a merged model, two shards to one consolidated model, and legacy-v1
training state to upgraded-v2 followed by continuation in a distinct process.
Full-to-PEFT extraction and PEFT-to-merged inference use an explicit float64
`atol=1e-12`, `rtol=1e-12` policy. Shard consolidation is bit-exact, while the
version upgrade must reproduce the uninterrupted control's loss history,
trainable state, evaluation, optimizer, scheduler, and final step exactly.

Every artifact has a closed inventory, payload checksums, a manifest-bound
completion marker, source provenance, bounded safe loading, and an atomic
same-filesystem commit. A standalone comparison reuses the same typed core:

```powershell
flashpilot compare-checkpoints `
  .\runs\conversion-equivalence\cases\peft-to-merged\source `
  .\runs\conversion-equivalence\cases\peft-to-merged\candidate `
  --output-dir .\runs\conversion-comparison
```

A passing conversion result is equivalence evidence, not crash-recovery
verification. It emits neither a recovery attestation nor storage-savings
claims.

## V0.3 partial-write fuzz qualification

The third V0.3 roadmap item runs a deterministic six-case matrix for every
requested iteration:

```powershell
flashpilot fuzz-checkpoint `
  --scenario partial-write `
  --iterations 100 `
  --run-dir .\runs\partial-write-fuzz
```

Each iteration exercises truncated payload, missing shard, stale manifest,
checksum mismatch, duplicate rank, and reordered-write exposure. The first
five cases must fail validation for their exact typed reason. The reordered
case exposes a final-named directory after each of five differently ordered
writes; every incomplete observation must be rejected, and only the complete
closed inventory may pass.

The source checkpoint uses the same-filesystem temporary-directory and atomic
rename protocol. All source and candidate artifacts are fingerprinted before
and after validation. Results are deterministic for the fixed seed and contain
relative artifact paths, JSON, Markdown, JUnit, and a job summary. This is
commit-integrity evidence, not randomized crash timing or recovery proof, so it
emits no recovery attestation, byte metric, or storage-savings claim.

## V0.3 previous-valid checkpoint fallback

The fourth V0.3 roadmap item qualifies deterministic fallback after the newest
committed checkpoint becomes corrupt:

```powershell
flashpilot qualify previous-valid-fallback `
  --profile exact-training-resume `
  --scenario corrupt-newest `
  --run-dir .\runs\previous-valid-fallback
```

A dedicated CPU producer commits complete native `safe_full` checkpoints at
steps 2 and 4, emits typed evidence only after both validate, and is then
terminated by the parent. The parent corrupts only the newest model payload,
requires the exact checksum rejection, and invokes the existing latest-valid
discovery. Step 2 must be the only valid candidate and the selected checkpoint.

Recovery runs in a distinct process. The unchanged 24-check deterministic
Recovery Gate compares its step, model, optimizer, scheduler, Python/NumPy/Torch
RNG, loss trajectory, trainable state, and evaluation output to the
uninterrupted control with `atol=0.0`, `rtol=0.0`. The fixed scenario permits a
two-step RPO and fails if that limit is exceeded. Both the selected previous
checkpoint and rejected newest evidence are fingerprinted before and after
recovery. A verified fallback reports neither storage savings nor checkpoint
bytes and currently emits no recovery attestation.

## V0.3 repeated randomized fault timing

The fifth V0.3 roadmap item repeats the unchanged native `safe_full` crash and
recovery experiment at a reproducible, seeded set of completed-step boundaries:

```powershell
flashpilot qualify randomized-fault-timing `
  --profile exact-training-resume `
  --fault process-kill `
  --iterations 8 `
  --seed 20260720 `
  --run-dir .\runs\randomized-fault-timing
```

Every four-trial schedule block covers an achieved RPO of 0, 1, 2, and 3
completed steps in randomized order. Each trial uses a real parent-owned
process termination and a distinct recovery process. All 24 exact Recovery
Gate checks must pass with `atol=0.0`, `rtol=0.0`, and the achieved RPO must
remain within the fixed three-step limit. The aggregate binds its seeded
schedule and each complete trial directory by SHA-256, then revalidates the
underlying experiment evidence before reporting `VERIFIED`.

The result includes relative paths, JSON, Markdown, JUnit, and a job summary.
It does not call GPT, execute repair, emit an attestation, or calculate or
report checkpoint bytes or storage savings.

## V0.3 SARIF dashboard output

FlashPilot now writes `results.sarif` beside its typed JSON, Markdown, and
JUnit evidence for static audits; native, Hugging Face, and Lightning
qualification; conversion equivalence; partial-write fuzzing; previous-valid
fallback; and randomized fault timing. Existing completed audit and core
qualification runs can be projected again without rerunning training:

```powershell
flashpilot emit-sarif --run-dir .\runs\ci-hf
```

The SARIF 2.1.0 document is a deterministic view of existing evidence, not a
second verdict engine or a source-code scanner. Exact FlashPilot check IDs are
stable rules. `FAIL` becomes an error, `WARN` and `UNKNOWN` become warnings,
and `PASS` or `NOT_APPLICABLE` produces no dashboard alert. Every emitted
result points to the relative authoritative evidence file and carries a stable
partial fingerprint; absolute local paths are not invented.

The included GitHub Actions workflow uploads SARIF as an ordinary diagnostic
artifact under its existing `contents: read` permission. It does not request
`security-events: write` or automatically publish Code Scanning results.

## V0.4 managed-preemption certification

V0.4 adds one narrow POSIX certification path for the included offline CPU
Hugging Face Trainer workload:

```bash
flashpilot certify-preemption \
  --framework hf \
  --signal SIGTERM \
  --grace-period 300 \
  --script examples/hf_trainer/train.py \
  --run-dir runs/preemption
```

The parent waits until the worker reaches a recorded completed-step boundary,
delivers a real external `SIGTERM` with `os.kill`, and enforces the declared
grace-period deadline. The Python signal handler only records in-memory signal
state. Normal Trainer callback code creates an explicit `INCOMPLETE` marker,
requests a complete checkpoint, persists lifecycle metadata, removes and
directory-fsyncs the marker after the save, and emits commit evidence before
the worker exits cleanly.

Certification then loads that checkpoint in a distinct process and requires
all 22 deterministic checks to pass at `atol=0.0`, `rtol=0.0`. Evidence
includes checkpoint-commit and graceful-exit durations, RPO in completed steps
and synthetic-workload tokens, recovery RTO, exact trajectory digests, SARIF,
JUnit, reports, and a closed unsigned attestation. Storage bytes are emitted
only after the Gate passes.

This command requires a POSIX host. Windows execution fails closed because
Windows `TerminateProcess` is not equivalent to catchable POSIX `SIGTERM`.
The hosted Ubuntu workflow is configured to execute the real signal path. A
local or hosted run certifies only the included process/workload contract; it does not claim
that Kubernetes, Slurm, or a cloud provider control plane was exercised.

## V1.0 two-rank FSDP restart qualification

The first V1.0 qualification item exercises real PyTorch FSDP2 collectives and
Distributed Checkpoint sharding on two local CPU ranks:

```powershell
flashpilot qualify distributed-pytorch `
  --strategy fsdp `
  --backend gloo `
  --world-size 2 `
  --profile exact-training-resume `
  --run-dir .\runs\distributed-fsdp
```

The bounded harness runs separate two-rank control, checkpoint, and recovery
process groups. `torch.distributed.checkpoint` persists the FSDP model and
optimizer state; strict per-rank JSON persists scheduler, Python/NumPy/Torch
RNG, global step, and stochastic loss history. Rank 0 closes checksums and a
manifest before an atomic same-filesystem directory rename. The 24-check
Recovery Gate requires all six processes to exit cleanly and the recovered
per-rank trajectories, trainable state, evaluation, optimizer, scheduler, and
collective probe to match the uninterrupted control exactly.

This qualification is CPU-only, Gloo-only, fixed at world size 2, and restores
at the same world size. The command shown proves the clean-restart baseline;
the bounded rank-termination option is documented below. Neither surface tests
elastic resharding, CUDA/NCCL, or network filesystems. Verified bytes and the
unsigned attestation are emitted only after the deterministic Gate passes.

## V1.0 two-rank DeepSpeed ZeRO-2 restart qualification

On Linux, install the explicit optional dependency and run the fixed CPU/Gloo
contract:

```bash
python -m pip install -e ".[deepspeed]"
flashpilot qualify deepspeed \
  --zero-stage 2 \
  --backend gloo \
  --world-size 2 \
  --profile exact-training-resume \
  --run-dir runs/deepspeed-zero2
```

The harness runs two-rank control, checkpoint, and recovery groups in six
distinct processes. Both checkpoint ranks call DeepSpeed's real collective
`save_checkpoint`; the committed checkpoint requires one model/scheduler
state, exact rank 0 and 1 ZeRO optimizer shards, strict per-rank RNG/progress/
trajectory state, a tag bound to the global step, SHA-256 checksums, a
completion marker, and an atomic same-filesystem directory rename. Recovery
uses `load_checkpoint` in two new processes and must pass all 30 exact Gate
checks before bytes or an unsigned attestation are reported.

The qualified claim is intentionally limited to DeepSpeed 0.19.x, ZeRO stage
2, CPU, Gloo, world size 2, same-world-size clean restart, and the included
offline workload. Windows fails closed before workers start because the
supported qualification runtime is Linux. The clean-restart command remains
the baseline for the bounded rank-termination option below. Elastic or
universal checkpoints, ZeRO stages 1/3, CUDA/NCCL, downloaded models or
datasets, and network filesystems remain outside the qualified surface.

## V1.0 multi-rank failure qualification

The third V1.0 item adds one explicit fault to both supported two-rank
runtimes. Select either rank; run both commands to qualify the complete target
matrix:

```powershell
flashpilot qualify distributed-pytorch `
  --fault rank-termination `
  --target-rank 0 `
  --run-dir .\runs\fsdp-fault-rank-0

flashpilot qualify distributed-pytorch `
  --fault rank-termination `
  --target-rank 1 `
  --run-dir .\runs\fsdp-fault-rank-1
```

The equivalent Linux DeepSpeed commands use `flashpilot qualify deepspeed`
with the same `--fault` and `--target-rank` options. Both ranks must first load
the already committed, validated checkpoint and emit separate typed readiness
records. The parent then calls `kill()` only on its selected child process.
The peer must emit a separate typed Gloo collective-failure record; a nonzero
exit by itself is insufficient. The parent reaps the complete failed group,
launches two distinct recovery ranks from the unchanged checkpoint, and
requires exact control equivalence.

Rank failure is delivered at the committed checkpoint boundary, so the
qualified RPO is zero steps. FSDP adds 12 fault checks to its existing Gate
for 36 total; DeepSpeed adds the same checks for 42 total. The attestation
binds the target rank, both failed-group PIDs, the peer observer, and the
SHA-256 of `failure-event.json`. Clean restart remains the default. This does
not implement elastic membership, in-process process-group reinitialization,
world-size changes, scheduler retries, multi-node networking, CUDA, or NCCL.

## What the demo proves

1. An uninterrupted seeded CPU control produces stable trajectory evidence.
2. A valid, checksummed, loadable checkpoint omitting training continuation
   state restores in a new process but fails the exact Recovery Gate.
3. GPT-5.6 receives only sanitized manifest, restore, failed-check, and
   trajectory evidence—not the injection label, expected diagnosis, or repair
   preset.
4. Deterministic guardrails classify the captured recommendation. Exactly six
   NativePyTorchAdapter actions can map to six explicit boolean fields;
   unsupported advice is recorded and not executed.
5. One new isolated strategy is tested through a second real termination and
   distinct recovery process. The original failed checkpoint remains unchanged.
6. Only the final deterministic Recovery Gate can print `VERIFIED`, using
   exact equality with `atol=0.0` and `rtol=0.0`.
7. Recurring logical-byte reduction is shown only after verification. The
   immutable frozen-base cost is reported separately, and the first
   adapter-aware write is not presented as savings.

## Audience and architecture

FlashPilot is for ML engineers, researchers, and checkpoint-integration authors
who need an executable recovery qualification test. The P0 architecture is
intentionally narrow:

```text
seeded CPU control
-> atomic checkpoint commit
-> parent-owned worker termination
-> distinct-process restore
-> deterministic Recovery Gate
-> captured GPT-5.6 diagnosis replay
-> typed six-field repair
-> second termination and restore
-> final Recovery Gate
-> post-pass logical-byte comparison
```

`result.json` is the canonical machine-readable evidence. `report.md`, the
self-contained `report.html`, and the Rich console are deterministic views of
that record; there is no GPT report narrator or duplicated experiment logic.

## GPT-5.6 role

The judge path displays exactly:

```text
GPT source: GPT-5.6 captured-response fixture/replay
```

The checked-in fixture reproduces an independently accepted, secret-free live
GPT-5.6 structured response and retains its capture metadata. Runtime use is
explicitly labeled fixture/replay and makes no live API call. GPT recommends;
deterministic code validates, executes the fixed action mapping, and decides
recovery.

The optional `live-contract` and `live-failure` commands remain available for
explicit guarded validation with an API key. They are not used by the judge
command.

## Responsibility boundary

- GPT-5.6 inferred the checkpoint contract and diagnosed the observed failed
  recovery from sanitized structured evidence. It proposed typed actions only.
- Codex implemented the workload, checkpoint protocols, process orchestration,
  schemas, guardrails, bounded executor, reports, packaging, tests, and release
  documentation.
- The human fixed the scope at one native PyTorch adapter, chose the valid but
  incomplete training-state scenario, limited repair to six actions and one
  attempt, required blind diagnosis, and required proof before savings.
- Normal deterministic code validates manifests, checksums, containment,
  process evidence, exact state and trajectory equality, action capabilities,
  repair immutability, and the attempt limit.
- Only the deterministic Recovery Gate may declare `VERIFIED`. Neither GPT-5.6,
  Codex, fixture provenance, checkpoint loadability, nor report prose can do so.

## Supported and verified environment

- Verified: Windows 11, Python 3.12.13, PyTorch CPU execution.
- Package declaration: Python 3.11 or newer. Python 3.11 has not been verified
  and is not claimed as such.
- No CUDA, external datasets, downloaded weights, server, or desktop UI.
- Payload and metadata files are fsynced and directory rename is atomic.
  Python does not expose directory fsync on Windows, so directory durability is
  explicitly best-effort there.
- The Windows directory-symlink containment test stays enabled and skips only
  when the host user lacks symlink privilege.

Run environment qualification at any time:

```powershell
flashpilot doctor
```

It reports Python, platform, CPU execution, dependency versions, fixture
availability, output writability, API-key presence without its value, and the
Windows directory-fsync limitation.

## Inspecting a completed run

```powershell
flashpilot audit --run-dir .\runs\repair-<uuid>
flashpilot verify --run-dir .\runs\repair-<uuid>
flashpilot replay --run-dir .\runs\repair-<uuid>
```

These commands are read-only. `replay` revalidates the captured structured
response without making an API call.

## Measurement limitation

The independently accepted Windows/Python 3.12.13 demo-profile run measured:

| Verified quantity | Result |
| --- | ---: |
| Initial Recovery Gate | FAIL, 9 exact failed checks |
| Final Recovery Gate | VERIFIED, 24/24 checks |
| Comparison policy | `atol=0.0`, `rtol=0.0` |
| `safe_full` recurring logical bytes | 126,218 |
| Repaired recurring logical bytes | 32,743 |
| Recurring logical-byte reduction | 93,475 bytes (74.06%) |
| One-time immutable frozen base | 93,987 bytes, reported separately |

These values come from the accepted Prompt 6 run. Timing is environment- and
invocation-dependent and is retained in the build log rather than generalized.

Logical checkpoint bytes were measured in the controlled demo. Physical NAND
writes, write amplification, and SSD lifetime were not measured. Results apply
only to the controlled model, profile, serialization, and current environment;
they are not a general compression or hardware-lifetime claim.

## Scope limits

The frozen P0 repair path still supports only `NativePyTorchAdapter` and the six
primary Section 28.5 repair actions. VNext separately adds one narrow,
non-repairing `HuggingFaceTrainerAdapter` qualification for the included local
Trainer contract. It is not plugin discovery, framework auto-detection, generic
arbitrary-script compatibility, or an additional GPT repair surface.

Install and run the optional local HF qualification with:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[hf]"
.\.venv\Scripts\flashpilot.exe qualify hf-trainer --script .\examples\hf_trainer\train.py --profile exact-training-resume --fault process-kill --scenario complete --run-dir .\runs\hf-complete
```

The example constructs its tiny model and synthetic dataset locally, forces CPU
execution and offline Hugging Face environment controls, keeps dropout enabled,
kills a real checkpoint worker, and resumes in a new process. The `model-only`
scenario is loadable but intentionally fails exact training-resume qualification.

## CI and policy workflow

Every static audit and qualification writes `junit.xml` plus
`job-summary.md`. The JUnit testcase names are the exact deterministic check
IDs, so a CI failure identifies the missing or divergent requirement without
parsing console logs. Re-evaluate a completed run through the same local core:

```powershell
.\.venv\Scripts\flashpilot.exe emit-junit `
  --run-dir .\runs\hf-complete `
  --policy .\examples\ci\policy.yml
```

The YAML policy is a closed Pydantic schema: exact profile, `unknown_state=fail`,
an allowlisted process-termination fault, maximum RPO/RTO, and optional required
attestation for one run. V1.0 adds a separate closed suite policy that proves
the entire explicitly bound production matrix instead of treating one
allowlisted fault as proof that every required scenario ran:

```powershell
flashpilot generate-signing-key .\runs\qualification-signing-key
@(
  ".\runs\ci-hf",
  ".\runs\ci-distributed",
  ".\runs\ci-distributed-fault-rank-0",
  ".\runs\ci-distributed-fault-rank-1",
  ".\runs\ci-deepspeed",
  ".\runs\ci-deepspeed-fault-rank-0",
  ".\runs\ci-deepspeed-fault-rank-1",
  ".\runs\ci-preemption"
) | ForEach-Object {
  flashpilot sign-attestation "$($_)\recovery.attestation.json" `
    --private-key .\runs\qualification-signing-key\ed25519-private.pem
}
```

The checked-in production policy requires all eight runtime attestations to
verify with one explicitly trusted key:

```powershell
.\.venv\Scripts\flashpilot.exe enforce-policy `
  --policy .\examples\ci\qualification-policy.yml `
  --output-dir .\runs\ci-policy `
  --public-key .\runs\qualification-signing-key\ed25519-public.pem `
  --run hf-process-termination=.\runs\ci-hf `
  --run fsdp-checkpoint-restart=.\runs\ci-distributed `
  --run fsdp-rank-termination-0=.\runs\ci-distributed-fault-rank-0 `
  --run fsdp-rank-termination-1=.\runs\ci-distributed-fault-rank-1 `
  --run deepspeed-checkpoint-restart=.\runs\ci-deepspeed `
  --run deepspeed-rank-termination-0=.\runs\ci-deepspeed-fault-rank-0 `
  --run deepspeed-rank-termination-1=.\runs\ci-deepspeed-fault-rank-1 `
  --run hf-managed-preemption=.\runs\ci-preemption `
  --run hf-static-audit=.\runs\ci-audit
```

Every requirement is a discriminated typed selector for an existing result
kind. Runtime requirements fix framework, adapter, profile, fault, exact
zero-tolerance recovery, RPO/RTO bounds, verified attestation, and a verified
detached signature. Distributed
requirements also fix strategy, implementation, Gloo world size 2, ZeRO stage
where applicable, and target rank. Missing, duplicate, unlisted, UNKNOWN,
non-exact, over-bound, unattested, malformed, or tampered evidence fails
closed. Evidence is supplied only through repeated explicit `--run` bindings;
there is no directory scan, expression, command, import, or arbitrary scripting
field.

The command writes `policy-evaluation.json`, JUnit, Markdown, and SARIF under a
separate output directory and never mutates a bound run. Exit codes remain
stable: `0=verified/pass`, `2=warning or unknown review`, `3=qualification or
enforced-policy failure`, `4=invalid/tampered evidence`, and `5=unsupported
configuration`.

V1.0 organization policy adds one deliberately narrow layer above that suite.
The central policy names the exact scenario inventory, requires signed runtime
attestations, and fixes maximum RPO/RTO bounds. A repository policy may tighten
those numeric bounds but cannot omit or add a scenario, weaken signature or
exactness requirements, or change a typed selector:

```powershell
.\.venv\Scripts\flashpilot.exe enforce-organization-policy `
  --organization-policy .\examples\ci\organization-policy.yml `
  --repository-policy .\examples\ci\qualification-policy.yml `
  --scope-id flashpilot-main `
  --output-dir .\runs\ci-organization `
  --public-key .\runs\qualification-signing-key\ed25519-public.pem `
  --run hf-process-termination=.\runs\ci-hf `
  --run fsdp-checkpoint-restart=.\runs\ci-distributed `
  --run fsdp-rank-termination-0=.\runs\ci-distributed-fault-rank-0 `
  --run fsdp-rank-termination-1=.\runs\ci-distributed-fault-rank-1 `
  --run deepspeed-checkpoint-restart=.\runs\ci-deepspeed `
  --run deepspeed-rank-termination-0=.\runs\ci-deepspeed-fault-rank-0 `
  --run deepspeed-rank-termination-1=.\runs\ci-deepspeed-fault-rank-1 `
  --run hf-managed-preemption=.\runs\ci-preemption `
  --run hf-static-audit=.\runs\ci-audit
```

The command re-runs the existing repository suite verifier; it does not trust
an independently supplied PASS document. Its terminal
`organization-policy-evaluation.json` embeds and SHA-256 binds that complete
repository evaluation, along with both policy-source hashes, the explicit
scope label, every organization check, and the derived aggregate verdict.
The layer remains closed data: there are no expressions, scripts, policy
plugins, repository scans, remote policy retrieval, inheritance trees,
exceptions, or waivers. The scope label is operator-provided context, not an
authenticated repository identity.

[.github/workflows/flashpilot-qualification.yml](.github/workflows/flashpilot-qualification.yml)
is the active pull-request and manual hosted workflow, sourced from
[examples/github-actions/flashpilot-qualification.yml](examples/github-actions/flashpilot-qualification.yml).
It publishes diagnostics on failure and uploads attestation payloads, detached
signatures, the ephemeral run public key, both policy sources, the terminal
organization-policy evaluation, and GitHub OIDC provenance only after
qualification and both typed policy layers succeed. The private key is created
under runner temporary storage, removed
with `if: always()`, and never uploaded. Its quality matrix runs Python 3.11
and 3.12; on Linux, the development extra installs Lightning and DeepSpeed so
the full suite exercises both optional qualification paths on both
interpreters.

The workflow uses `actions/attest@v4` to create SLSA provenance for the exact
`runs/ci-organization/organization-policy-evaluation.json` bytes. That terminal
evaluation embeds and hash-binds the repository policy evaluation, which binds
the production policy hash plus every runtime result, recovery attestation,
detached signature, and trusted-key fingerprint. The workflow immediately
verifies the saved Sigstore bundle with the GitHub CLI while requiring the
exact repository, signer-workflow path, workflow digest, source digest, source
ref, GitHub OIDC issuer, and a GitHub-hosted runner. A consumer can repeat the
core offline-bundle check after downloading the success artifact:

```powershell
gh attestation verify .\runs\ci-organization\organization-policy-evaluation.json `
  --bundle .\runs\ci-provenance\github-oidc-provenance.sigstore.json `
  --repo cimpal55/flashpilot `
  --signer-workflow cimpal55/flashpilot/.github/workflows/flashpilot-qualification.yml `
  --predicate-type https://slsa.dev/provenance/v1 `
  --cert-oidc-issuer https://token.actions.githubusercontent.com `
  --deny-self-hosted-runners
```

Add `--signer-digest`, `--source-digest`, and `--source-ref` with the expected
workflow commit, source commit, and Git ref to reproduce the workflow's full
identity constraint. GitHub provenance authenticates who produced the fixed
organization-policy-evaluation artifact; it cannot create or upgrade a
FlashPilot recovery verdict.

## Optional local attestation history

V1.0 can preserve verified signed recovery statements in an explicitly chosen
local append-only registry. Registration first verifies the complete source
bundle with the existing deterministic verifier and an explicitly trusted
Ed25519 public key. It then copies only the exact attestation, detached
signature, and public key into a content-addressed entry:

```powershell
flashpilot attestation-registry init .\runs\attestation-registry

flashpilot attestation-registry add `
  .\runs\ci-hf\recovery.attestation.json `
  --registry-root .\runs\attestation-registry `
  --public-key .\runs\qualification-signing-key\ed25519-public.pem

flashpilot attestation-registry verify .\runs\attestation-registry
flashpilot attestation-registry history .\runs\attestation-registry
```

Each entry has a strict manifest, fixed three-file artifact inventory,
completion marker, sequential predecessor hash, and directory name bound to
the exact manifest SHA-256. A strict atomically replaced `HEAD` binds the
expected count and newest entry, including suffix-deletion detection. Files and
metadata are fsynced before atomic same-filesystem replacement; directory fsync
remains explicitly best-effort on Windows. Reads validate the complete bounded
history and every stored signature before returning JSON. Duplicate attestations, gaps,
unexpected files, symbolic links, interrupted temporary entries, retained
writer locks, hash changes, or malformed statements fail closed.

This is an optional single-host evidence archive, not a remote publication
service or a second recovery oracle. Stored entries preserve the exact signed
statement but not the source checkpoint/evidence bundle, so later history
verification proves signature and chain integrity, not a fresh Recovery Gate
run. Trust in the registry root and admission key remains an operator concern;
there is no deletion, pruning, revocation, key rotation, network API, database,
or hosted registry. Organization-policy enforcement is a separate explicit
suite operation and neither discovers nor trusts compact registry history.

## Security model

FlashPilot accepts no arbitrary commands or source patches. Managed writes are
contained under the selected run root; traversal and supported symlink escapes
fail closed. Checkpoints require completion, manifest, checksum, base-identity,
and containment validation before loading. GPT receives bounded redacted JSON,
never raw tensors, dataset samples, secrets, arbitrary files, absolute local
paths, the injection label, expected diagnosis, or a repair preset. API keys are
read only from the environment and are never printed or persisted.

Detached signatures cover the domain-separated exact bytes of
`recovery.attestation.json`. Verification fails closed unless the caller
supplies the expected Ed25519 public key; the sidecar does not embed or choose
its own trust root. The local key generator refuses overwrites and does not
print private-key bytes. POSIX private files are created with mode `0600`;
Windows file ACL protection is explicitly best-effort. Keep production private
keys outside the repository and establish public-key trust out of band.

Hosted qualification additionally uses GitHub's OIDC-backed Sigstore flow for
the terminal organization-policy evaluation. Only job-scoped `id-token: write` and
`attestations: write` are added to the qualification job; the repository and
quality-job default remains `contents: read`. The saved bundle and local
verification result contain no private key or repository secret. This
provenance layer is downstream of deterministic policy and Recovery Gate
results and cannot change them.

The optional local registry is disabled unless its commands are invoked. It
uses one exclusive writer lock, caps history at 10,000 entries, binds the
newest committed entry through `HEAD`, refuses stale locks rather than guessing
whether they are safe to remove, and never reads a private key. Registry entry
and head commits are atomic on one filesystem. A process death can leave an
entry/head mismatch, temporary file/directory, or lock; any such condition
intentionally blocks subsequent reads and writes until an operator inspects the
local path.

## Prior art and positioning

FlashPilot does not claim checkpoint scheduling, adapter-only persistence,
compression, incremental checkpoints, atomic writes, checksums, or chaos testing
as new techniques. [docs/research.md](docs/research.md) positions the harness
against CheckFreq, Check-N-Run, ExCP, Amber, IncrCP, OPT, MegaScale,
FlashRecovery, REO, MiDAS, FDP/WARP, and ZipLLM without implementing those
systems.

## Codex contribution summary

Codex implemented the deterministic workload, integrity-valid checkpoint
strategies, real parent-controlled process termination, new-process restore,
24-check Recovery Gate, strict GPT-5.6 schemas and redaction, captured-response
replay, six-field bounded executor, immutable-history proof, second recovery
verification, Rich judge console, offline doctor, static reports, tests, and
wheel validation. GPT-5.6 supplied bounded recommendations; it did not write or
execute repair code and did not declare recovery successful.

## Limitations and roadmap

The locally verified scope is the controlled CPU-only native workload plus the
included local Hugging Face Trainer, PyTorch Lightning, and FSDP examples on
Windows 11 with Python 3.12.13. DeepSpeed and managed-preemption qualification
require a Linux/POSIX host and cannot be certified by this Windows host.
Python 3.11 compatibility is targeted but not locally verified.
Windows directory fsync is
unavailable through Python and is best-effort. The project does not qualify
arbitrary repositories, Trainer scripts, or LightningModules, arbitrary
distributed training, CUDA, NeMo, TensorFlow, or JAX. Fixture replay is tied to the captured
schema and evidence contract; novel failures require a new guarded live
analysis. Physical storage effects are not measured.

Future work may add elastic membership, multi-node/CUDA fault scenarios, and
broader platform validation. The implemented organization policy is local,
explicit, and exact-inventory only; remote distribution, authenticated scope
identity, inheritance trees, waivers, exceptions, and a hosted policy service
remain unimplemented.

## Repository and license

Repository: <https://github.com/cimpal55/flashpilot>

No license file is currently committed. Selecting and adding the intended
license remains a human release decision and is listed in the release checklist.

## Development quality gates

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
```
