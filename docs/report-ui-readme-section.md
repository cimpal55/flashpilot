# Staged README section

This is the top-level `README.md` content for the report UI, staged here rather
than applied, so this branch does not conflict with concurrent core edits to
`README.md`. Paste it in at merge time and delete this file.

Insert as the **first** section after the project title.

---

## Try it — no install

**[Open the FlashPilot sandbox →](https://cimpal55.github.io/flashpilot/)**

Six real qualification runs in your browser. Nothing to install, no account.
Start with the pair that carries the whole argument: two Hugging Face
checkpoints from the same training script, both of which load without an error —
and only one of which can actually resume the run it claims to continue.

Then re-verify the proof yourself: the page recomputes SHA-256 over the raw
evidence bytes with your browser's own Web Crypto, and gives you three controls
to break the bundle and watch it fail closed.

## Or run it locally

```bash
pip install 'flashpilot[hf]'
flashpilot demo
```

## Or inspect the artifacts directly

```bash
flashpilot report ./samples/hf-model-only
```

Every sample under `samples/` is a byte-identical copy of a real run directory —
`SOURCE.txt` in each one records which. `python tools/verify_samples.py`
re-checks all 79 evidence files against their manifests.

---

## How Codex and GPT-5.6 were used

GPT-5.6 proposes contracts and diagnoses failures. **Only the deterministic gate
issues verdicts.**

That boundary is visible, not just stated. `samples/native-repair` carries a real
captured GPT-5.6 call: its root-cause hypothesis, its typed repair plan, and the
validator's per-action disposition — including one action the model proposed
that was **refused** as unsupported. The 24/24 gate that followed was computed by
FlashPilot, not by a model.

The presentation layer takes the same position: it renders and re-verifies, and
has no code path that can turn a FAILED or UNKNOWN run into a pass. See
`docs/ui-decisions.md` for how that is enforced, and `docs/ui-codex-contributions.md`
for the milestone-by-milestone trail.
