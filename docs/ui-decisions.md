# UI decisions

Decisions specific to `report-ui/`. Kept separate from `docs/decisions.md` so
the UI branch never conflicts with concurrent core work; merge into the shared
file when the branches converge.

## D-UI-1 — No build step, no npm

**Decision.** The UI is plain ES modules and CSS custom properties, served as-is.

**Why.** The constraint is "builds to fully static assets". The strongest way to
satisfy an auditor is for the deployed bytes to *be* the source bytes — there is
no bundler output to reconcile against the repository. It also keeps a Python
project free of a Node toolchain, and makes the eventual wheel-vendoring step
(`src/flashpilot/report/_static/`) a plain directory copy.

**Cost.** No tree-shaking or minification. At this size (~40 KB of source) that
does not matter.

## D-UI-2 — Sample bytes embedded in a generated module, not fetched

**Decision.** `tools/build_samples.py` base64-encodes every manifest-listed
evidence file into `report-ui/src/data/bundles.js`.

**Why.** Three requirements collapse into one solution: the verifier needs the
*raw bytes* to hash; the page must work offline; and `fetch()` is blocked under
`file://`. Embedding satisfies all three with a single code path, so there is no
"works on Pages, breaks locally" class of bug.

**Guard.** `tools/verify_samples.py` proves the embedded base64 decodes to the
exact bytes on disk, and that those bytes match the manifest. CI blocks the
deploy if it does not, so the embedding can never silently drift from `samples/`.

## D-UI-3 — Hash routing

**Decision.** Routes are `#/run/<id>/verify`, not `/run/<id>/verify`.

**Why.** History routing needs a server rewrite rule, which would break both
`file://` and a bare `python -m http.server`. Hash routing makes one artifact
work in every hosting mode with no configuration.

## D-UI-4 — Raw-byte hashing, deliberately not canonical-JSON hashing

**Decision.** The verifier hashes file bytes and compares to
`evidence-manifest.json`. It does not attempt to recompute the attestation's own
digest.

**Why.** Raw-byte hashing is independent of FlashPilot's JSON canonicalisation,
so a judge can reason about the check without knowing the core's serialisation
rules — and it works today without adding an attestation-hash mirror.

**If a mirror is added later.** Document the core canonical form in this file —
stable key order, `separators=(",", ":")` — and mirror it exactly in the UI.

## D-UI-5 — Fail-closed status lattice

**Decision.** `INTACT` is reachable only when every entry is intact *and* the
inventory is non-empty. Everything else resolves to `TAMPERED`, `MISSING` or
`VOID`, and the overall result takes the worst status present.

**Why.** The failure mode that would discredit the whole tool is a bundle with no
evidence rendering as a pass. An empty inventory returning `VOID` rather than
"0 failures, therefore pass" is the specific bug this rule exists to prevent.

## D-UI-6 — A schema adapter, not a schema union

**Decision.** `shapeOf()` in `src/lib/bundle.js` maps each core result schema
(`flashpilot-hf-qualification-v1`, `repair-loop-result-v1`,
`flashpilot-static-audit-v1`, the Lightning variant) onto one view shape.

**Why.** Adding a surface must never require touching the core. The adapter
selects and renames fields; it does not derive new ones, which keeps the
"copied, never computed" rule mechanically checkable in one file.

## D-UI-7 — The GPT trust panel shows persisted output, not a claim

**Decision.** For runs that carry one, the panel renders the actual
`proposed_analysis`, the `plan_validation` dispositions (accepted / rejected /
unsupported) and the call metadata (model, schema version, request digest).

**Why.** "GPT proposed and diagnosed; it never set the verdict" is far more
convincing as an artifact a viewer can inspect — including the actions the typed
validator *refused* — than as a sentence. `native-repair` carries a real
GPT-5.6 capture, so the panel is evidence rather than assertion.

## D-UI-8 — Webfonts are progressive enhancement only

**Decision.** Google Fonts is loaded non-blockingly; `tokens.css` carries a
complete fallback stack.

**Why.** "Renders with network disabled" is an acceptance criterion. Verified:
with no font requests served, every surface still renders with correct hierarchy
and spacing. CI additionally rejects any other external origin.

## D-UI-9 — The downloadable attestation is the original bytes, cross-checked

**Decision.** `bundles.js` carries `recovery.attestation.json` as base64 of the
raw file. The report surface hashes those bytes in-browser, compares the digest
to the `attestation_sha256` the CI suite independently recorded in
`attestation.junit.xml`, and serves the same bytes for download.

**Why.** A re-serialized `JSON.stringify(attestation)` would hash differently
and quietly break the "portable, independently re-verifiable artifact" claim.
Byte-exactness also enables a real cross-check between two artifacts produced
by different code paths — measured live: browser-computed `74391573ea31…`
matches the JUnit record for `hf-complete`.

## D-UI-10 — A requested mutation must never be silently inert

**Decision.** The tamper primitive flips one bit of the first byte; for a
zero-length file (the corpus contains real 0-byte stderr logs) it appends a
single byte instead, so the size check catches it.

**Why.** The original bit-flip was a no-op on empty files: the row would claim
to be tampered while still verifying INTACT. That is exactly the class of
quiet false-pass the fail-closed rules exist to prevent — the demo's
credibility rests on every advertised mutation actually being detected.
