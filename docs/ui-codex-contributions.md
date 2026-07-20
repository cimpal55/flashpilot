# UI contributions trail

Companion to `docs/codex-contributions.md`, kept separate so the UI branch does
not conflict with concurrent core work. Merge into the shared file when the
branches converge.

---

## Milestones M-C → M-F, M-H — report UI (`codex/report-ui-v1.0`, 2026-07-21)

**Kickoff.** The UI subset of `FLASHPILOT_FINAL_PLAN.md`, executed under the
plan's binding constraints, with one added constraint from the operator: produce
no merge conflict with the in-flight attestation-registry work.

### One decision the agent made well

Reading the run directories before writing any code, rather than implementing
milestone M-B first as the plan's ordering implied. The artifacts already
contained everything the UI needed — `recovery.attestation.json`,
`evidence-manifest.json` with per-file sha256 and size, `result.json`,
`junit.xml`, `job-summary.md`. That single observation removed the sidecar
command from the critical path and reduced the change to **zero Python core
files**, which is what made the isolation constraint achievable rather than
merely attempted.

The second good call followed from the first: because the evidence files are
small (64 KB and 266 KB per manifest), the raw bytes could be committed and
embedded. The in-browser verification is therefore genuine — the browser hashes
real safetensors, real optimizer state, real logs — rather than a simulation
over fixtures written to make the check pass.

### One place a human overrode it

The operator rejected the agent's implied default of working in the existing
checkout and directed an isolated copy instead. The agent proposed a git
worktree over a plain folder copy; the operator chose it, which preserved shared
git history and reduced the eventual merge to an ordinary pull request. The
operator also scoped the work to UI milestones only — the agent would otherwise
have implemented M-B and touched `cli.py` and `pyproject.toml`, the two files
the concurrent branch was already modifying.

A second override was structural: the plan says to update `docs/build-log.md`,
`docs/decisions.md` and `docs/codex-contributions.md` at every milestone. The
operator directed separate `ui-*` files instead, trading a manual merge later
for zero conflicts now.

### Where GPT-5.6 runs inside the product

The UI does not call a model. It *renders* the model's persisted output, which
is the point of the trust panel.

`samples/native-repair` carries a real captured GPT-5.6 call:

- `proposed_analysis` — root-cause hypothesis, confidence `high`, nine affected
  gate checks, and a typed repair plan;
- `plan_validation.decisions` — the typed validator's disposition per proposed
  action, including one the model proposed that was **refused**
  (`change_supported_checkpoint_strategy` → `unsupported`);
- `captured_live_failure_metadata` — provider, model `gpt-5.6`, prompt version,
  output schema `failure-analysis-v2`, request digest, `validation_status:
  accepted`.

The panel shows the refusal alongside the acceptances deliberately. "GPT
proposed and diagnosed; it never set the verdict" is a claim; a rejected action
sitting next to a deterministic 24/24 gate is evidence. The same sentence appears
in the product, this file, and the video narration, in the same words.

### Verification the agent performed on itself

Every claim in `docs/ui-build-log.md` was measured in a live browser rather than
asserted: the tamper probe output, the 0-overflow figure at 375 px, the
zero-focus-ring-failures count, and the route sweep are all extracted readings.
Where verification was not possible — screenshots would not capture in this
environment — the build log says so instead of implying a visual review happened.
