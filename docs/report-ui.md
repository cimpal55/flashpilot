# Report UI

The presentation layer for FlashPilot runs: a static site that renders real
qualification artifacts and lets anyone re-verify their evidence in their own
browser.

Canonical statement it exists to deliver:

> Frameworks save checkpoints; FlashPilot proves they can safely resume — and
> issues a portable, independently re-verifiable attestation of that proof.

## Surfaces

| Surface | Route | What it does |
|---|---|---|
| Gallery | `#/` | Fleet view of every sample run; fleet counts; the FAIL/PASS hero pair |
| Compare | `#/compare` | Two runs side by side with both trajectories; any pair selectable |
| Report | `#/run/<id>` | One run in full: verdict, gate, trajectory, process reality, digests, provenance, trust boundary |
| Verifier | `#/run/<id>/verify` | Web Crypto re-hashing of every evidence file, plus three adversarial probes |
| CI | `#/run/<id>/ci` | The same evidence as a PR check: JUnit annotations, exit-code contract, merge decision |
| About | `#/about` | The boundaries the UI operates under, and the sample → source-run mapping |

## Constraints it holds

1. The UI never computes or overrides a verdict. `src/lib/bundle.js` copies
   status values; there is no branch that upgrades a status.
2. Re-verification recomputes SHA-256 over **raw evidence bytes** only. It does
   not depend on JSON canonicalisation, so it stays correct regardless of how the
   core serialises.
3. Fail closed. `verifyEntry` returns `VOID` for path escapes, `MISSING` for
   dangling references, `TAMPERED` for hash or size mismatch. `INTACT` requires
   every entry to be intact *and* the inventory to be non-empty.
4. Real data only. Every sample is a byte-identical copy of a real run, recorded
   in `samples/<id>/SOURCE.txt` and re-checkable with `tools/verify_samples.py`.
5. Fully static. No backend, no build step, no external origin except an optional
   webfont that the page renders correctly without.

## The adversarial probes

The verifier ships three controls that break the loaded bundle in memory. All
three must fail closed; they are the fastest way for a sceptic to convince
themselves the check is real.

| Probe | Mutation | Required outcome |
|---|---|---|
| Flip one bit | XORs one bit of the first evidence file | `TAMPERED`, exactly one file flagged |
| Inject `../` path | Adds a manifest entry escaping the run root | `VOID` |
| Drop a file | Leaves the manifest claim, removes the bytes | `MISSING` |

Toggling a probe off restores `INTACT`. The files under `samples/` are never
modified.

## Sample corpus

Six real runs across three adapters and all three verdict classes:

| Sample | Source run | Verdict | Why it is in the sandbox |
|---|---|---|---|
| `hf-model-only` | `runs/milestone13-hf-model-only` | FAILED | The hero scene: loads fine, provably cannot resume |
| `hf-complete` | `runs/milestone13-hf-complete` | VERIFIED | Real kill, new process, identical trajectory, attestation + 25-file manifest |
| `native-repair` | `runs/milestone13-native` | VERIFIED | 24-check gate and a persisted GPT-5.6 diagnosis filtered by the typed validator |
| `lightning-complete` | `runs/dev-lightning-complete-3` | VERIFIED | Same gate, different framework |
| `lightning-weights-only` | `runs/dev-lightning-weights-2` | FAILED | The same failure class reproduces outside Hugging Face |
| `unknown-layout` | `runs/milestone13-unknown-audit` | UNKNOWN | Proves UNKNOWN never renders as PASS |

Runs without an evidence manifest render `VOID` in the verifier. That is correct
behaviour, not a gap: there is nothing to re-verify, so no claim is made.

## Regenerating

```bash
python tools/build_samples.py --runs ../flashpilot/runs
python tools/verify_samples.py
```

`bundles.js` is committed deliberately: it is what makes the site buildless and
offline-capable.
