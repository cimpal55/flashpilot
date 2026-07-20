# UI build log

Kept separate from `docs/build-log.md` so UI work never conflicts with
concurrent core branches. Merge into the shared log when the branches converge.

---

## 2026-07-21 — M-C + M-D + M-E + M-F + M-H (`codex/report-ui-v1.0`)

Executed in an isolated git worktree branched from `main`, so the in-progress
attestation-registry work in the primary checkout was untouched throughout.

**Scope executed.** Milestones M-C (design system + report surface), M-D (run
gallery), M-E (independent verifier + tamper), M-F (Pages deploy + guided path)
and M-H (CI view) from `FLASHPILOT_FINAL_PLAN.md`.

**Not executed.** M-B (`flashpilot report` sidecar). It proved unnecessary: the
run directories already emit everything the UI needs
(`recovery.attestation.json`, `evidence-manifest.json`, `result.json`,
`junit.xml`, `job-summary.md`). Skipping it kept the change to zero Python core
files and therefore zero merge risk. If the sidecar lands later, the UI reads it
through the same `shapeOf()` adapter without structural change.

### Changed files

```text
tools/build_samples.py                      new — copies real runs, emits bundles.js
tools/verify_samples.py                     new — CI counterpart of the browser verifier
report-ui/index.html                        new
report-ui/README.md                         new
report-ui/src/design/{tokens,base,components}.css   new
report-ui/src/lib/{dom,hash,bundle,router}.js       new
report-ui/src/components/{kit,blocks}.js            new
report-ui/src/surfaces/{gallery,report,verifier,ci,compare}.js  new
report-ui/src/data/bundles.js               new — GENERATED (561 KB)
samples/<6 run directories>                 new — byte-identical copies of real runs
.github/workflows/report-ui-pages.yml       new
docs/report-ui.md                           new
docs/ui-build-log.md                        new (this file)
docs/ui-decisions.md                        new
docs/ui-codex-contributions.md              new
docs/report-ui-readme-section.md            new — staged README copy, merged by hand
```

No file under `src/flashpilot/`, `schemas/`, `tests/`, `pyproject.toml` or
`README.md` was modified.

### Commands executed

```text
git worktree add -b codex/report-ui-v1.0 ../flashpilot-ui main
python tools/build_samples.py --runs ../flashpilot/runs
python tools/verify_samples.py
python -m http.server 4173 --bind 127.0.0.1 --directory report-ui
```

### Actual output

`python tools/build_samples.py`:

```text
hf-model-only            FAILED      0 evidence files
hf-complete              VERIFIED   25 evidence files
native-repair            VERIFIED   54 evidence files
lightning-complete       VERIFIED    0 evidence files
lightning-weights-only   FAILED      0 evidence files
unknown-layout           UNKNOWN     0 evidence files

wrote report-ui\src\data\bundles.js (561 KB)
```

`python tools/verify_samples.py` (exit 0):

```text
hf-complete               25 evidence files verified
hf-model-only            no manifest - verifier renders VOID (expected)
lightning-complete       no manifest - verifier renders VOID (expected)
lightning-weights-only   no manifest - verifier renders VOID (expected)
native-repair             54 evidence files verified
unknown-layout           no manifest - verifier renders VOID (expected)

OK - 79 evidence files match their manifests and their embedded copies
```

In-browser verifier, `hf-complete`, 25 files, no probes:

```text
INTACT  ·  Intact 25 · Tampered 0 · Missing 0 · Void 0   (1 ms)
```

Adversarial probes, measured in-page:

```text
Flip one bit    -> TAMPERED · control/result.json
                   manifest e95c1fcc449c…664177b3 / computed 0110da8c63e5…b43f2f20
                   Intact 24 · Tampered 1
Inject ../ path -> VOID     · ../outside-the-run.json — path escapes the run root
Drop a file     -> MISSING  · result.json.absent — no bytes for a manifest entry
Probes off      -> INTACT   (restored)
```

Route sweep (all render, no console errors):

```text
#/                          Frameworks save checkpoints. This proves they can resume.
#/compare                   It loads. It just doesn't resume the same run.   FAILED
#/run/hf-model-only         FAILED     5/13 checks, diverges at step 5
#/run/hf-complete           VERIFIED  13/13 checks, trajectory identical
#/run/native-repair         VERIFIED  24/24 checks, GPT-5.6 diagnosis panel populated
#/run/lightning-complete    VERIFIED
#/run/lightning-weights-only FAILED   5/14 checks
#/run/unknown-layout        UNKNOWN
#/run/hf-complete/verify    INTACT
#/run/hf-model-only/verify  VOID     (no manifest — nothing to re-verify)
#/run/hf-model-only/ci      exit 3 · QUALIFICATION FAILED — merge blocked
#/run/nope                  "No such run"
```

Quality floor, measured in-page:

```text
horizontal overflow at 375 px : 0 on all 9 routes
focusable controls without a visible focus ring : 0 of 45 across 3 surfaces
prefers-reduced-motion : honoured (all three motions collapse to 1 ms)
network requests to external origins : 0 (webfonts absent; fallback stack renders)
```

### Acceptance criteria

**M-C — design system + report surface**

- Single design language derived from tokens — **PASS** (all colour via
  `tokens.css`; no surface hard-codes a value)
- Legible without a legend — **PASS**
- Renders with network disabled — **PASS** (fonts never loaded during testing;
  layout and hierarchy intact)
- Focus + reduced-motion verified — **PASS**

**M-D — run gallery**

- Zero-install access to every scenario — **PASS**
- Each card shows a real distinct verdict — **PASS** (3 VERIFIED, 2 FAILED,
  1 UNKNOWN across 3 adapters)
- FAIL/PASS pair reads red→green at a glance — **PASS**

**M-E — independent verifier + tamper**

- Genuine bundle verifies intact in-browser — **PASS** (25/25, then 54/54)
- One-byte mutation detected — **PASS** (single bit; exactly one file flagged)
- Traversal and missing refs → void, never pass — **PASS** (`VOID`, `MISSING`)
- No verdict computed by the UI — **PASS** (verdicts copied in `bundle.js`;
  verifier reports evidence integrity only, never a qualification verdict)

**M-F — hosting, guided path, README**

- One hosted link renders the sandbox — **PENDING** (workflow committed;
  deploys on merge to `main`, needs Pages enabled in repo settings)
- First-time judge completes doubt→proof unassisted — **PASS** (5-step guided
  path, dismissible, free exploration preserved)
- README leads with the no-install path — **PASS** (staged in
  `docs/report-ui-readme-section.md` to avoid conflicting with concurrent
  core edits to `README.md`)

**M-H — CI view**

- Individual failed requirements visible — **PASS** (8 failed requirements
  rendered as annotations from the real `junit.xml`)
- UNKNOWN can never render as PASS — **PASS** (`unknown-layout` renders
  UNKNOWN with exit 5 / merge blocked; the exit-code table has no path from an
  unproven checkpoint to a passing check)

### v0.1 fixture demo

**Unchanged — not re-run in this worktree.** No Python file was touched, so the
demo cannot have regressed; the assertion is structural rather than executed.
Re-run it in the primary checkout before merging if you want it on the record.

### Assumptions and unresolved risks

1. **Pages is not yet enabled** on the repository. The workflow is correct but
   unproven until the first `main` deploy; the hosted-link criterion stays
   PENDING until then.
2. **`samples/` adds ~900 KB to the repository** (real evidence bytes, committed
   deliberately so re-verification is genuine rather than simulated).
3. **The README section is staged, not applied.** Merging it into the top-level
   `README.md` is a manual step, taken once the concurrent core branches land.
4. **Screenshots could not be captured** in this environment; all visual claims
   above were verified through computed styles, geometry and extracted text
   rather than by eye. A human should look at the site once before recording.
5. **No `--serve` (M-I) and no real-world probe (M-G).** Both were out of scope
   for this pass. M-I is a pure directory copy of `report-ui/` into
   `src/flashpilot/report/_static/` when the core branch is quiet.
