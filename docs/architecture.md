# Architecture

The architecture is deliberately narrow:

1. `workload` owns a deterministic, CPU-only Transformer-like training system.
2. Synthetic token batches are pure functions of the global seed and global step.
3. The model has a frozen base and one trainable residual bottleneck adapter.
4. Nonzero training dropout makes RNG restoration relevant; evaluation disables dropout.
5. CI and demo profiles require no downloads or external datasets.
6. An uninterrupted control records final model, optimizer, scheduler, loss, and evaluation evidence.
7. Checkpoints use manifests, checksums, completion markers, containment, and atomic directory rename.
8. P0 exposes only `NativePyTorchAdapter` through a plain lookup function.
9. The parent kills a worker only after validating its committed checkpoint event.
10. Recovery runs in a distinct process and restores state before the next batch.
11. The deterministic Recovery Gate is the only recovery authority and compares exactly.
12. GPT-5.6 consumes only bounded capabilities or sanitized failure evidence and emits typed proposals.
13. The repair executor copies a typed strategy config and changes only six allowlisted booleans once.
14. JSON is authoritative; Markdown is deterministically rendered without a GPT narrator.
15. Logical storage impact is calculated only after repaired recovery passes.

## VNext Milestone 9 foundation

VNext adds an independent Persistence Contract beside the frozen v0.1 GPT
checkpoint-contract schema. The old schema, fixtures, demo, process protocol,
repair loop, and Recovery Gate remain unchanged.

The vNext contract separates three concerns for every state item:

```text
requirement: required | optional | ephemeral | unknown
recovery source: checkpoint | immutable reference | external durable source |
                 deterministic recompute | none
exactness: exact | tolerance bounded | non-equivalent
```

Only `exact-training-resume` and `model-only-inference` profiles exist in v0.2.
The controlled native exact-resume minimum contains nine state items: adapter,
immutable base identity, deterministic batch position, global step, optimizer,
scheduler, and Python/NumPy/Torch RNG. The model-only profile keeps adapter and
base identity required and classifies training-continuation state as ephemeral.

Contract processing is deterministic:

```text
typed proposal
-> reject malformed, contradictory, UNKNOWN, or out-of-inventory state
-> merge with the native local minimum
-> validate every required source and exactness rule
-> canonical JSON
-> SHA-256 contract identity
```

A weaker optional classification may be replaced by a required local minimum.
An internally contradictory proposal is rejected rather than normalized. An
exact-training-resume contract rejects tolerance-bounded required state. Every
required item has evidence IDs, and immutable, external-durable, or
deterministically recomputed sources require identity controls.

`migrate_native_checkpoint_contract` converts an already accepted v0.1 native
`CheckpointContract` into this model and adds the deterministic batch-position
minimum. It does not rewrite the v0.1 fixture or route, so the original judge
demo remains byte- and verdict-compatible. Public draft-2020-12 JSON Schemas are
checked in under `schemas/` and tested against generated output.

## VNext Milestone 10 static checkpoint audit

`flashpilot audit-checkpoint PATH --framework auto --profile PROFILE` performs
bounded static inspection without launching training, importing a user script,
or invoking a framework callback. Detection recognizes only native PyTorch,
the supported Hugging Face Trainer layout, or unknown. Framework-specific
metadata takes precedence over shared filenames such as `optimizer.pt`; mixed,
ambiguous, and unrecognized layouts remain `UNKNOWN`.

The audit path is deliberately separate from recovery qualification:

```text
contained non-symlink directory
-> deterministic framework detection
-> schema and lifecycle metadata
-> checksums / safe tensor metadata / weights-only payload inspection
-> profile-specific state requirements
-> PASS | WARN | FAIL | UNKNOWN
-> audit.json + report.md + junit.xml
```

Every result is typed with `static_only=true` and
`recovery_verified=false`. Static audit has no `VERIFIED` enum value and cannot
produce an attestation. `PASS` means only that the supported static contract is
satisfied; a real failure and resumed trajectory still require the Recovery
Gate in a later qualification step.

Native inspection reuses the existing strict manifest, checksum, completion,
containment, and payload-size validation. Known PyTorch payloads are opened only
with `weights_only=True`. Exact resume checks model/adapter state, immutable or
full-model identity, optimizer, scheduler, Python/NumPy/Torch RNG, global step,
deterministic batch position, and runtime metadata. Model-only inspection keeps
model/base identity required but does not require training-continuation state.

The narrow Hugging Face path reads JSON metadata with size limits, validates
safetensors headers and data offsets without materializing tensors, and applies
`weights_only=True` only to allowlisted PyTorch payload names. It never unpickles
`training_args.bin`; the supported exact-resume fixture supplies
`training_args.json`. Unknown files are reported and reduce an otherwise passing
audit to `WARN`. A supported model-only layout fails exact resume and passes the
model-only profile. JUnit contains one testcase per deterministic requirement
and one failure element per failed requirement.

Static audit exit codes are stable: `PASS=0`, `WARN/UNKNOWN=2`, `FAIL=3`, and
unsupported configuration `=5`. Code `4` remains reserved for invalid or
tampered attestation evidence in the later attestation milestone.

## VNext Milestone 11 recovery attestation

The existing native red-to-green demo now emits an unsigned
`recovery.attestation.json` only after its repaired deterministic Recovery Gate
passes. The authoritative `repair-loop-result-v1` schema and its Markdown/HTML
views remain unchanged. Attestation construction reads and revalidates those
persisted artifacts; it does not participate in recovery or set the gate
verdict.

Emission order is fail-closed:

```text
persist VERIFIED result and deterministic reports
-> validate result/report equality and exact 24/24 gate
-> write canonical native Persistence Contract
-> write dependency and source-identity environment evidence
-> fingerprint repaired checkpoint directory
-> inventory every experiment evidence file
-> write evidence-manifest.json
-> bind its SHA-256 into recovery.attestation.json
-> independently verify the complete bundle
-> write attestation.junit.xml
```

The evidence manifest records run-relative path, logical size, and SHA-256 for
every experiment evidence artifact. It excludes exactly three statement/index
artifacts: itself, the attestation, and derived attestation JUnit. This avoids a
circular hash. Verification recomputes a closed inventory, so missing, added,
renamed, symlinked, or one-byte-mutated evidence fails.

`RecoveryAttestationV1` binds the exact-resume profile, native framework and
runtime version, current commit plus explicit clean/dirty/unavailable source
state, dependency-environment identity, canonical contract identity, repaired
checkpoint directory identity, distinct worker and recovery PIDs, equal control
and resumed trainable/evaluation digests, all 24 gate checks, zero tolerances,
RPO, RTO, and the already verified recurring logical bytes. The source tree is
currently recorded honestly as dirty because the milestone changes await
independent review and commit.

`flashpilot verify-attestation recovery.attestation.json` verifies strict
schemas, manifest identity, the closed evidence inventory, dependency/source
metadata, deterministic native contract, authoritative result, exact
Markdown/HTML rendering, native checkpoint manifest/checksums/base artifact,
checkpoint directory hash, PIDs, trajectories, gate counts, RPO/RTO, and byte
metrics. Invalid or tampered evidence exits with code `4`. A successful Rich
summary and eight-check JUnit file report integrity verification.

The v1 attestation is deliberately unsigned. It provides local bundle integrity
and internal consistency, not publisher authentication, legal certification,
or third-party certification. Signing is a later roadmap item.

## VNext Milestone 12 Hugging Face qualification

The optional HF path is an explicit `HuggingFaceTrainerAdapter`, not a plugin or
auto-detected repair adapter. The included script implements one documented
callback contract with a tiny local `PreTrainedModel`, index-derived synthetic
dataset, sequential batches, CPU-only execution, full determinism, and dropout.
No model or dataset is loaded from the Hub.

The `FlashPilotTrainerCallback` runs after Trainer checkpoint save. It records a
contained checkpoint path and typed file-presence evidence, writes bounded JSON
metadata, emits one lifecycle event, and waits to be killed. Its schema cannot
carry a verdict or repair. The external parent owns the trust boundary:

```text
copy explicitly selected script into run sandbox
-> launch uninterrupted control process
-> launch checkpoint worker
-> validate checkpoint event and contained file contract
-> kill the exact recorded process
-> launch recovery in a distinct process
-> compare loss history and all final state digests at atol=0, rtol=0
-> persist VERIFIED or FAILED result and deterministic reports
-> emit unsigned attestation only after VERIFIED
```

The complete checkpoint contains model, Trainer state, optimizer, scheduler,
and Python/NumPy/Torch RNG state. Its recovery must match control loss history,
trainable state, evaluation, optimizer, scheduler, final step, and RPO exactly.
The model-only checkpoint is a valid Trainer checkpoint and loads, but omits
optimizer, scheduler, and RNG state. Continued stochastic training genuinely
diverges and the same gate fails closed. Storage bytes are recorded only for
the complete checkpoint after the gate passes.

Worker environments remove API-key variables, force the Hugging Face offline
flags, disable CUDA, and execute an argument vector with `shell=False`. This
prevents library-mediated downloads for the included example but is explicitly
not an operating-system network sandbox or a generic arbitrary-script claim.

## VNext Milestone 13 CI and developer workflow

The CI layer normalizes static-audit, native qualification, direct native crash
experiment, and HF qualification results into `CIRunEvidence`. It does not
recompute a verdict: each check status, RPO, RTO, framework, fault class, and
profile comes from the same strict result models used by local commands.

Each audit or qualification emits:

```text
junit.xml       one testcase per exact audit/gate requirement
job-summary.md  deterministic GitHub-compatible Markdown view
```

These files are created before a verified attestation closes its evidence
inventory. `emit-junit` verifies exact existing content for an attested run and
refuses to recreate, change, or repair missing evidence. Failed runs have no
attestation and may still retain diagnostic JUnit and summary artifacts.

`CIPolicyV1` is a closed YAML-backed model with only the exact qualification
profile, fail-closed UNKNOWN behavior, allowlisted required fault class, maximum
RPO/RTO, and attestation requirement. PyYAML `safe_load` is bounded to 64 KiB;
Pydantic rejects extra keys and every non-allowlisted value. There is no policy
expression language or code execution surface.

The stable command boundary is:

```text
0  verified qualification or passing audit
2  warning/UNKNOWN requiring review
3  failed qualification or policy
4  invalid/tampered evidence
5  unsupported configuration
```

The generic `qualify native-pytorch` command reuses the frozen native
red-to-green core; `qualify hf-trainer`, `demo`, and static audit use their same
existing services. The reusable workflow source remains under `examples/` and
is synchronized with the active `.github/workflows` qualification job.
Diagnostic artifacts use `if: always()`; attestation upload uses
`if: success()` and therefore cannot publish a failed run as verified.

The standard HF RNG pickle cannot always be read by PyTorch's default
`weights_only=True` allowlist because it contains NumPy reconstruction globals.
The callback therefore emits a strict JSON RNG metadata bridge bound to the
actual `rng_state.pth` SHA-256. Static audit verifies that hash and the three
typed RNG-presence claims without unpickling the payload or weakening the safe
loader. Fixtures without the bridge retain the previous weights-only path.

## V1.0 typed qualification-suite policy

`QualificationPolicyV1` is a closed, 64-KiB-bounded YAML schema over existing
strict audit and qualification result kinds. It is deliberately not a generic
policy engine. There are no expressions, imports, functions, commands, rule
evaluation, plugins, repository scans, path discovery, or dynamic framework
selectors. Pydantic discriminates one of seven exact requirement models:
static audit, native, Hugging Face, managed HF preemption, Lightning, FSDP, or
DeepSpeed.

The checked-in production policy contains nine unique selectors: HF process
termination; clean FSDP; FSDP rank 0 and rank 1 termination; clean DeepSpeed
ZeRO-2; DeepSpeed rank 0 and rank 1 termination; managed SIGTERM; and HF static
audit. Every run is supplied through an explicit
`requirement-id=run-directory` CLI binding. Missing evidence becomes an exact
failed requirement; duplicate or unlisted bindings are rejected. No filesystem
enumeration is used to infer a run or satisfy a selector.

`CIRunEvidence` now carries the already-validated adapter, strategy,
implementation, backend, world size, ZeRO stage, fault target, and comparison
tolerances needed for exact selector matching. This is a projection of strict
result models, not a second recovery verdict. A runtime selector also requires
the existing deterministic status to be `VERIFIED`, every underlying check to
be non-failing, `atol=0.0`, `rtol=0.0`, bounded RPO/RTO, and an integrity-verified
local attestation. Static audit requires `PASS` and forbids an attestation.
UNKNOWN always fails.

The fourth V1.0 item introduced 145 stable checks. Detached signing adds one
exact signature check to each of the eight runtime requirements, so the current
checked-in matrix evaluates 153 checks. Its aggregate `PASS` is derived from all
nine per-requirement verdicts. The command writes a
strict `policy-evaluation.json` plus JUnit, Markdown, and SARIF into a separate
closed output directory. It hashes each exact source result and the policy
source, records verified attestation hashes, refuses to write inside a bound
run, and does not mutate attested evidence. Existing malformed or tampered
evidence exits through the integrity path before policy evaluation.

The active hosted job runs this suite policy after all qualifications and the
static audit. Its always-on artifact includes the policy source, all public
policy/signature schemas, normalized evaluation, source results, JUnit,
Markdown, and SARIF. The success-only upload includes eight attestation
payloads, their detached signatures, and the run public key. It never includes
the private key. Authorization policy, organization inheritance, remote policy
retrieval, OIDC, and a registry remain out of scope.

## V1.0 detached Ed25519 attestations

Signing is a separate operation after deterministic bundle verification. It
does not alter a Recovery Gate, create a recovery verdict, repair evidence, or
rewrite `recovery.attestation.json`:

```text
verify closed recovery-attestation bundle
-> hash exact recovery.attestation.json bytes
-> sign domain || exact bytes with Ed25519
-> atomically write recovery.attestation.signature.json
-> verify with an explicitly supplied trusted public key
```

The fixed domain is `flashpilot:recovery-attestation:v1` followed by a NUL
separator. `AttestationSignatureV1` fixes the algorithm, exact-byte scope,
artifact path, artifact SHA-256, raw-public-key SHA-256, base64 encoding, and
64-byte Ed25519 signature. It has no command, executable policy, embedded key,
certificate, identity, or network field. The existing attestation payload
retains `signature_status=unsigned` to preserve its schema and byte contract;
the verifier's typed result records whether the optional detached signature
passed and binds both key and sidecar hashes.

The signature is a derived statement artifact, so new evidence manifests
exclude it alongside the manifest, attestation, and JUnit statement. Legacy
three-exclusion unsigned manifests remain valid. The verifier still recomputes
the full closed evidence inventory before checking a signature. A sidecar with
no trusted key, a supplied key with no sidecar, a wrong algorithm or key,
malformed base64, fingerprint mismatch, signature mutation, or any change to
the exact attestation bytes fails closed.

`generate-signing-key` creates a new unencrypted PKCS8 Ed25519 private key and
SPKI public key without overwrite. POSIX uses directory mode `0700` and private
file mode `0600`; Windows ACL protection is best-effort and reported. The
checked workflow uses one ephemeral run key, signs all eight runtime
attestations, evaluates the 153-check policy with its public key, deletes the
private file even on failure, and publishes only the public key on success.
That proves signature mechanics and same-run key consistency, not durable
publisher identity. OIDC identity, certificate issuance, transparency logs,
key management services, and registry publication belong to later milestones.

## Frozen v0.1 architecture

The parent process launches an incomplete-checkpoint worker, waits for and
validates its post-rename event, kills the recorded PID, and restores in a new
PID. The valid checkpoint loads, but its deterministic Recovery Gate fails nine
required-state, trajectory, and contract checks. Its sanitized evidence excludes
the injection label, strategy name, expected diagnosis, repair preset, tensors,
samples, secrets, commands, arbitrary files, and absolute local paths.

The default contract and failure fixtures reproduce the independently accepted
secret-free GPT-5.6 structured responses. Metadata sidecars retain their live
provider, model, response ID, request hash, timestamp, prompt/schema versions,
and `store=false`. Runtime use is labeled
`source=captured_live_response_replay`; no API call occurs.

The failure proposal is parsed through the same strict schema and deterministic
guardrails. `change_supported_checkpoint_strategy` remains known but
unsupported. Exactly these six actions are executable:

- `persist_optimizer_state`
- `persist_scheduler_state`
- `persist_python_rng_state`
- `persist_numpy_rng_state`
- `persist_torch_rng_state`
- `restore_state_before_next_batch`

The executor admits one attempt through exclusive file creation, copies
`CheckpointStrategyConfig`, maps those actions to
`include_optimizer`, `include_scheduler`, `include_python_rng`,
`include_numpy_rng`, `include_torch_rng`, and
`restore_before_next_batch`, and assigns a new strategy ID. There is no command,
patch, path, or model-text execution surface.

The repaired configuration runs under a new `repaired/` root using the existing
`safe_adapter_aware` contract. A second real worker is killed after its atomic
commit, a distinct process restores, and the unchanged 24-check Recovery Gate
compares with the same uninterrupted control at `atol=0.0`, `rtol=0.0`. A
whole-directory SHA-256 fingerprint proves the original failed checkpoint did
not change. Attempt two is refused.

`result.json` records the two experiments, captured and replay metadata, full
proposal, classification, explicit strategy fields, fingerprints, attempt
count, final gate, and post-pass storage comparison. `report.md` renders that
record deterministically. `audit`, `verify`, and `replay` are read-only. The
recurring repaired checkpoint is measured separately from its one-time frozen
base. No physical NAND, write-amplification, or SSD-lifetime claim is made.

## Three largest implementation risks

| Risk | Why it matters |
| --- | --- |
| Cross-platform process reproducibility | Exact recovery is proven on the current Windows/Python/PyTorch environment, but other supported OS and dependency versions still require validation. |
| Durability limits on Windows | Files are fsynced and directory rename is atomic, but Python cannot directory-fsync on Windows, so that part remains explicitly best-effort. |
| Replay applicability | The accepted GPT-5.6 diagnosis is replayed against the same typed evidence contract; new workload capabilities or failure shapes require a new guarded analysis rather than broadening this executor. |

## VNext Milestone 14 release boundary

The v0.2 wheel keeps Transformers, Accelerate, and safetensors out of the base
dependency graph. `flashpilot qualify hf-trainer` performs a safe dependency
probe before importing the HF qualification service. A base installation exits
with stable code `5` and the exact `pip install 'flashpilot[hf]'` remedy. The
`hf` extra declares all three libraries because the qualification path directly
uses each one.

The wheel packages the captured-response fixtures, public JSON Schemas, typed
CI policy, inactive GitHub Actions example, HF source example, and release
checklist under the interpreter's data prefix. The offline HF worker itself is
a normal `flashpilot.hf` package module. Omitting `--script` selects that worker;
supplying `--script` retains the explicit documented local-script contract.
Neither path adds discovery, a plugin registry, or arbitrary Trainer support.

Release validation uses two independent virtual environments outside the
FlashPilot repository. The base environment proves fixture demo, native static
audit, and actionable missing-extra behavior without any HF distribution. The
second environment installs the exact same wheel with `[hf]` and proves the
packaged default worker, exact 13-check recovery, attestation verification,
typed CI policy, and CPU static audit. Application workers remain offline; a
temporary wheelhouse is only a dependency-install transport for the clean
environment setup.

## V0.3 PyTorch Lightning qualification adapter

The Lightning path is an explicit qualification-only adapter. It is not
registered with `NativePyTorchAdapter`, exposes no repair actions, performs no
plugin discovery, and does not claim arbitrary `LightningModule`
compatibility. `flashpilot qualify lightning` copies one selected Python entry
point into an isolated run root and launches three CPU subprocesses with
argument arrays and `shell=False`:

```text
uninterrupted control
-> Lightning Trainer.save_checkpoint
-> parent validates contained, bounded, weights-only-loadable checkpoint
-> parent kills checkpoint worker
-> distinct recovery worker
-> exact 14-check gate
-> JUnit/job summary
-> verified-only attestation and persisted-byte count
```

The included module uses actual dropout. Its full checkpoint contains
Lightning model, loop, optimizer, and scheduler state plus an explicit
JSON-safe Python/NumPy/Torch RNG and loss-history bridge. RNG restoration is
deferred until the first resumed batch boundary so new-process data-loader
initialization cannot consume the restored dropout stream. The
`weights-only=True` scenario uses Lightning's real serialization mode: model
loading succeeds, loop metadata may remain, but optimizer, scheduler, RNG, and
history are absent. Continued training then diverges naturally and the gate
fails closed. No verified attestation or storage metric is emitted.

## V0.3 checkpoint conversion equivalence

Conversion qualification is a fixed four-case subsystem, not a format plugin
or arbitrary checkpoint converter. Each case commits an immutable source and
candidate directory with a strict typed manifest, closed payload inventory,
SHA-256 checksums, and a completion marker bound to the manifest hash. Payloads
are limited to 64 MiB and Torch data is loaded only after integrity validation
with `weights_only=True`.

```text
fixed deterministic source
-> checksummed atomic source commit
-> fixed conversion
-> candidate manifest binds source directory SHA-256
-> checksummed atomic candidate commit
-> semantic equivalence comparison
-> source and candidate re-fingerprinting
-> JSON + Markdown + JUnit evidence
```

The model cases cover controlled full-to-PEFT rank-2 extraction,
PEFT-to-merged inference, and sharded-to-consolidated state. Float64 PEFT
factorization and merge use the declared `1e-12` absolute and relative
tolerance; consolidation requires exact parameter and output equality. The
version-upgrade case translates all model, optimizer, scheduler, RNG,
trajectory, and step state into the v2 layout, then resumes in a distinct
subprocess and compares exact continuation evidence to a fresh uninterrupted
control.

The public `compare-checkpoints` command consumes only these typed artifact
pairs and reuses the same comparator. It does not scan repositories, detect
frameworks, mutate either input, repair checkpoints, issue a Recovery Gate
verdict, calculate byte savings, or emit an attestation.

## V0.3 partial-write and incomplete-commit fuzzing

`fuzz-checkpoint --scenario partial-write` owns a fixed two-rank binary fixture
with no external inputs. Its strict manifest binds iteration, checkpoint ID,
world size, unique ranks, paths, sizes, and SHA-256 values. A completion marker
binds the exact manifest hash, while a separate checksum document must agree
with every manifest shard. Validation also requires a closed five-file
inventory and refuses symbolic links or payloads above 1 MiB.

Each deterministic iteration first creates a valid source through payload and
metadata fsync, temporary-directory fsync where supported, same-filesystem
directory rename, and parent-directory fsync where supported. Windows directory
fsync remains best-effort. Five isolated copies are then faulted independently:

```text
truncated shard     -> payload-size-mismatch
removed shard       -> payload-missing
changed manifest    -> completion-mismatch
changed checksums   -> checksum-manifest-mismatch
duplicate rank      -> manifest-invalid
```

The sixth case creates a final-named directory prematurely and rotates a fixed
five-file write order by iteration. Validation observes the directory after
every write. The four incomplete states must be rejected; the fifth state must
be accepted only when the full committed inventory is present. This is a
deterministic commit-state matrix, not the later randomized process-timing
milestone.

Case evidence stores only relative paths, stable rejection enums, validation
counts, and before/after directory fingerprints. The aggregate verdict derives
from the complete six-case-per-iteration matrix and zero premature acceptances.
It does not select an older checkpoint, resume training, invoke GPT, report
bytes, or emit a recovery attestation.

## V0.3 previous-valid checkpoint fallback

Fallback qualification reuses the production native `safe_full` writer,
fail-closed checkpoint validator, latest-valid discovery, recovery subprocess,
and 24-check Recovery Gate. It adds orchestration and typed evidence but no new
checkpoint format or alternate recovery verdict.

```text
producer process trains to step 2
-> atomic safe_full commit and validation
-> same producer trains to step 4
-> second atomic safe_full commit and validation
-> parent receives the typed two-checkpoint event
-> parent terminates the producer
-> parent corrupts only step-4 model.pt and fsyncs the mutation
-> exact checksum rejection
-> discovery returns only step 2 and selects it
-> distinct recovery process resumes step 2 through step 8
-> unchanged 24-check exact Recovery Gate with RPO 2/2
```

The event records both checkpoint snapshots and RNG digests before termination.
For gate evaluation, the selected step-2 event remains bound to the original
producer PID and its last completed step 4. Therefore achieved rollback is
computed as `4 - 2 = 2`, rather than being hidden by rewriting the crash point.

Selection adds seven checks for producer termination, corruption, exact
rejection, valid-candidate inventory, selected path, previous-checkpoint
immutability, and preservation of the rejected newest artifact. The Gate then
proves exact continued training. The workflow does not delete or repair the
corrupt checkpoint, call GPT, select across arbitrary repositories, emit a
storage metric, or run the later randomized-timing matrix.

## V0.3 repeated randomized fault timing

This qualification layer composes the existing native crash experiment rather
than introducing a second checkpoint writer, recovery worker, or Gate. A local
`random.Random` instance produces an RPO-stratified schedule from a recorded
63-bit seed. Each four-entry block contains one boundary for every allowed RPO
value, 0 through 3, and chooses a checkpoint step that keeps the completed
fault boundary within the eight-step CI workload.

```text
seed + iteration count
-> deterministic RPO-stratified schedule and SHA-256
-> N isolated safe_full native experiment directories
-> parent-owned termination after the scheduled completed step
-> distinct recovery process per trial
-> unchanged 24-check exact Recovery Gate per trial
-> closed aggregate with per-trial result and directory SHA-256
-> deterministic Markdown + JUnit + job summary
```

The aggregate verifier regenerates the schedule from the seed, resolves only
contained relative paths, fingerprints every trial directory, hashes every
underlying `result.json`, and compares process, timing, RPO, Gate, profile,
strategy, and exactness evidence to the strict aggregate. It rejects symlinks,
missing artifacts, mutation, schedule substitution, relaxed tolerances, or an
unexpected recovery attestation.

Randomization is limited to completed training-step boundaries. The design
does not claim mid-instruction, filesystem-controller, network-filesystem, or
distributed timing coverage. It calls no GPT provider, executes no repair,
emits no attestation, and never computes a storage byte or savings result.

## V0.3 SARIF evidence projection

SARIF output is downstream of the existing typed result models. It cannot
change a qualification, audit, policy, or Recovery Gate verdict.

```text
strict typed FlashPilot evidence
-> deterministic check-to-rule projection
-> suppress PASS and NOT_APPLICABLE alerts
-> emit FAIL as error; WARN and UNKNOWN as warning
-> bind each alert to a relative evidence artifact and stable fingerprint
-> validate the strict FlashPilot SARIF subset
-> write results.sarif beside the authoritative evidence
```

The projection uses SARIF 2.1.0 and the official OASIS Errata 01 schema URI.
Its strict Pydantic subset closes unknown properties and requires one run,
unique exact rule IDs, correct rule-index references, relative evidence
locations, and one deterministic partial fingerprint per non-passing result.
The checked JSON Schema is packaged with the application.

Core native, Hugging Face, and Lightning evidence uses the same CI-normalized
renderer as static audit. Conversion, fuzz, fallback, and randomized-timing
results use narrow typed adapters over their existing checks; no generic
scanner, plugin, policy planner, or numeric severity model is introduced.
When a verified attestation already closes a run inventory, re-emission may
verify the existing SARIF bytes but may not add a missing file.

The GitHub Actions workflow retains `contents: read` and uploads
`results.sarif` as an ordinary always-on diagnostic artifact. Publishing to a
repository's Code Scanning service is deliberately left to an explicitly
authorized workflow with the appropriate repository permissions.

## V0.4 managed-preemption certification

The V0.4 path is an explicit extension of the narrow Hugging Face adapter, not
a scheduler integration or a generic signal framework.

```text
full uninterrupted CPU control
-> preemption worker reaches fixed completed step and emits ready evidence
-> parent delivers external POSIX SIGTERM and starts grace deadline
-> minimal Python handler records only in-memory receipt state
-> Trainer callback writes preemption/INCOMPLETE and requests a full save
-> Trainer completes model + trainer + optimizer + scheduler + RNG state
-> callback persists lifecycle metadata, removes marker, fsyncs directory
-> worker emits commit evidence and exits 0 before grace deadline
-> parent validates streamed/persisted evidence and closed checkpoint inventory
-> distinct recovery process resumes to the fixed final step
-> 22-check zero-tolerance Gate measures step/token RPO and exact trajectory
-> result-derived reports, CI/SARIF, and verified-only unsigned attestation
```

The in-progress marker is intentionally outside the checkpoint directory at
`preemption/INCOMPLETE`. A forced kill during the callback path leaves it for
fail-closed diagnosis; a verified run requires it to be absent after worker
exit. Marker absence alone is insufficient: full state presence, a directly
loadable checkpoint, new-process resume, exact loss/state/evaluation digests,
commit-before-exit ordering, clean exit, and the grace deadline are separate
Gate checks.

The parent, not the worker, owns signal delivery and measures elapsed grace
time with a monotonic clock. Evidence timestamps additionally bind ready,
send, receipt, commit, and exit order. RPO is the difference between the
recorded completed step and committed checkpoint step; the included workload
also reports tokens as `batch_size * sequence_length * RPO steps`. Recovery RTO
retains the existing definition: recovery-process start through completion.

Windows fails closed before creating a run directory. Its process termination
API cannot substitute for a catchable POSIX `SIGTERM`. The Ubuntu workflow and
POSIX-only integration test are configured to exercise the real signal path.
This local harness models the process-level contract used by interruptible environments but does
not invoke Kubernetes, Slurm, RunPod, Vast, or another provider control plane.

## V1.0 item 1: bounded distributed PyTorch qualification

`qualify distributed-pytorch` owns a fixed six-process lifecycle: two control
ranks, two checkpoint ranks, and two recovery ranks. Each phase initializes a
fresh Gloo process group through a UUID-named file-store rendezvous under the
run directory. The included model is wrapped with PyTorch FSDP2
`fully_shard`; this is not DDP labeled as FSDP.

PyTorch Distributed Checkpoint collectively saves and loads model and
optimizer shards. Each rank separately records scheduler, Python/NumPy/Torch
RNG, progress, and loss history in strict JSON. Rank 0 fsyncs every payload,
writes a closed checksum document, strict manifest, and completion marker,
then atomically renames the temporary directory. Directory fsync remains an
explicit best-effort limitation on Windows.

The result is authoritative only when all 24 distributed Recovery Gate checks
pass. The Gate requires exact rank topology and process separation, integrity
closure, complete state, exact control prefix, all-rank load, final progress,
per-rank stochastic trajectory, full trainable/evaluation/optimizer/scheduler
digests, and a collective all-gather probe. Only then are logical checkpoint
bytes and an unsigned closed attestation emitted.

The qualified surface is intentionally fixed to CPU, Gloo, FSDP2, world size
2, same-world-size restart, and the included workload. Multi-rank failure
injection, elastic resharding, CUDA/NCCL, DeepSpeed, and network filesystems are
separate work.

## V1.0 item 2: bounded DeepSpeed ZeRO-2 qualification

`qualify deepspeed` owns the same six-process lifecycle but uses a distinct,
strict DeepSpeed evidence model. The only supported topology is Linux, CPU,
Gloo, world size 2, ZeRO stage 2, DeepSpeed 0.19.x, same-world-size restart,
and the included deterministic workload. Unsupported operating systems,
versions, stages, backends, world sizes, or profiles fail before worker launch.

```text
two-rank uninterrupted control
-> two new ranks train to the fixed checkpoint step
-> both ranks call DeepSpeedEngine.save_checkpoint with one exact tag
-> rank 0 fsyncs and hashes the closed payload set
-> rank 0 writes checksums + manifest + COMPLETE
-> atomic same-filesystem directory rename
-> parent validates without deserializing .pt payloads
-> two new ranks call DeepSpeedEngine.load_checkpoint
-> strict namespaced client state and per-rank RNG state restored
-> continuation to final step
-> 30-check exact Recovery Gate
-> result-derived CI/SARIF/reports and verified-only unsigned attestation
```

The checkpoint layout is closed to `latest`, `zero_to_fp32.py`, one tagged
model/scheduler state, exact rank 0 and 1 ZeRO optimizer shards, and exact rank
0 and 1 JSON state. FlashPilot checks every size and SHA-256 plus the tag,
manifest, completion marker, containment, and directory layout before allowing
DeepSpeed to deserialize its own checkpoint. DeepSpeed must restore engine
progress, optimizer, and scheduler; FlashPilot restores only rank-local
Python/NumPy/Torch RNG after verifying the scheduler state already matches.

The Gate compares each rank's stochastic loss history, trainable state,
evaluation, ZeRO optimizer partition, scheduler, final progress, and collective
probe to the uninterrupted control with `atol=0.0`, `rtol=0.0`. Logical bytes
and the unsigned attestation remain unavailable until every check passes.

This item proves the clean same-world-size checkpoint baseline. The next
section adds bounded targeted-rank failure without expanding to universal or
elastic checkpoints, ZeRO stages 1/3, CUDA/NCCL, or network filesystems.

## V1.0 item 3: targeted multi-rank process termination

Both FSDP and DeepSpeed reuse their strict clean checkpoint and exact recovery
paths. `fault=rank-termination` inserts one additional two-rank group between
checkpoint validation and final recovery:

```text
validated committed checkpoint
-> two fault ranks load the exact checkpoint
-> each atomically writes typed ready evidence
-> both repeatedly enter a Gloo monitored collective
-> parent kills exactly target rank 0 or rank 1 through its Popen handle
-> peer writes a separate typed collective-failure event
-> parent confirms/reaps the entire failed group
-> fresh two-rank recovery group loads the unchanged checkpoint
-> original exact Recovery Gate + 12 fault checks
-> verified-only metrics and unsigned attestation
```

The parent never accepts a requested PID or command from evidence. Paths are
fixed run-relative values and go through the existing sandbox. The target's
nonzero exit cannot prove peer impact: `failure-event.json` is constructed
only after the other rank's independently persisted evidence validates its
framework, PID, rank roles, checkpoint step, and observation ordering. Every
control, checkpoint, fault, and recovery PID must be distinct.

The fault occurs only after all ranks have restored the durable checkpoint and
before another optimizer step, yielding an exact zero-step RPO claim. Recovery
always uses a newly launched group at the same world size. No attempt is made
to reinitialize a damaged process group in-process, shrink or grow membership,
invoke TorchElastic or a scheduler, or qualify multi-node/CUDA/NCCL behavior.

## V1.0 item 6: GitHub OIDC provenance

OIDC provenance is a downstream hosted-CI trust layer over the existing local
evidence chain:

```text
eight deterministic Recovery Gates
-> eight exact-byte Ed25519 signatures under one ephemeral public key
-> nine-requirement / 153-check closed suite policy
-> policy-evaluation.json with source, attestation, signature, key, and policy hashes
-> 71-check exact organization baseline over the reverified repository suite
-> organization-policy-evaluation.json embedding and binding the suite evaluation
-> actions/attest@v4 GitHub OIDC + Sigstore SLSA provenance
-> gh attestation verify with repository/workflow/commit/ref/issuer/runner constraints
-> success-only evidence upload
```

The qualification job is the only component granted `id-token: write` and
`attestations: write`. It attests one explicit file rather than discovering
repository artifacts. The Sigstore bundle and JSON verification output are
persisted only alongside the successful signed suite. The always-on diagnostic
upload remains separate, and the quality matrix remains read-only.

No application component requests an OIDC token or parses a secret-bearing
runner credential. FlashPilot does not implement Fulcio, Rekor, certificate
path validation, registry publication, history queries, or a second policy
language. GitHub provenance can authenticate the terminal deterministic
artifact but cannot convert UNKNOWN, FAILED, unsigned, or policy-rejected
evidence into VERIFIED.

## V1.0 item 8: organization qualification policy

The organization layer is a strict downstream composition of the existing
repository suite evaluator:

```text
closed organization baseline YAML
+ closed repository suite-policy YAML
+ explicit requirement-id=run-directory bindings
+ explicit trusted Ed25519 public key
-> re-run existing repository suite verification
-> compare exact typed selector inventory
-> require equal-or-tighter RPO/RTO bounds
-> require exact recovery and signed runtime evidence
-> embed and hash-bind repository policy evaluation
-> organization-policy-evaluation.json
-> JUnit + Markdown + SARIF
```

`organization_policy_models.py` defines only fixed data shapes;
`organization_policy.py` performs safe loading, exact selector matching,
repository re-verification, deterministic evaluation, and closed-root writes;
`organization_policy_reporters.py` projects the authoritative model; and
`organization_policy_schema.py` generates the two public schemas.

The command never scans a repository or evidence parent, loads remote policy,
executes policy text, or evaluates a user expression. One invocation binds one
explicit scope label and one explicit repository policy. The label is not an
authenticated repository identity. The policy cannot alter an existing Gate,
tolerance, attestation, signature, or result, and it cannot issue a recovery
attestation. It reports organization-policy PASS only when both the central
baseline checks and the complete reverified repository suite pass.

The hosted workflow uses the organization evaluation as its terminal GitHub
OIDC provenance subject. The embedded repository evaluation retains the full
hash chain to source results and signed recovery attestations. The optional
local attestation registry is not an input to organization enforcement because
its compact entries intentionally omit the source evidence needed for a fresh
suite verification.
## Storage telemetry collectors

`src/flashpilot/telemetry/` sits outside the verdict path entirely. It has no
import from, and no caller inside, the Recovery Gate, the attestation builder,
or the policy engines.

Collection is strictly read-only. Each collector runs a fixed argument array —
never a shell string and never an interpolated one — under a ten-second timeout
and a 256 KiB output cap, and never escalates privileges. Linux reads
`nvme smart-log --output-format=json`; Windows reads storage reliability
counters through a fixed non-interactive PowerShell expression. Any failure
mode — missing tool, unsupported platform, insufficient rights, non-zero exit,
unparsable output, unrecognised counters — resolves to an explicit
"unavailable" artifact rather than a partial reading.

The artifact is written as `storage-telemetry.json` beside a run's other
outputs. It is deliberately not part of the verdict-bearing evidence inventory.
