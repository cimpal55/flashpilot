# FlashPilot report UI

A static presentation and **independent re-verification** surface for FlashPilot
runs. It renders real qualification artifacts and re-hashes their evidence in
the browser. It never computes, softens, or overrides a verdict.

## Run it

```bash
python -m http.server --directory report-ui 4173
# open http://127.0.0.1:4173
```

There is no build step and no `node_modules`. What you see in this directory is
exactly what gets deployed — plain ES modules and CSS custom properties.

## What it is allowed to do

| | |
|---|---|
| Verdicts | copied verbatim from the CLI's typed output; the UI has no code path that can turn FAILED or UNKNOWN into a pass |
| Re-verification | SHA-256 over **raw evidence bytes** via the browser's Web Crypto, compared to the manifest the core wrote |
| Failure mode | fails closed — unknown, missing, path-escaping and hash-mismatched evidence all render as not-a-pass |
| Network | none. Sample bytes are embedded; webfonts are optional progressive enhancement with a full fallback stack |
| Backend | none. Hash routing means the same files work from `file://`, a local server, and GitHub Pages |

Raw-byte hashing is deliberately independent of FlashPilot's JSON
canonicalisation, so the check can be reasoned about without knowing the core's
serialisation rules.

## Layout

```text
index.html
src/design/      tokens.css · base.css · components.css   (single source of truth)
src/lib/         hash.js (Web Crypto + fail-closed rules) · bundle.js · router.js · dom.js
src/components/  kit.js (primitives) · blocks.js (gate, lanes, evidence, provenance, trust)
src/surfaces/    gallery · report · verifier · ci · compare
src/data/        bundles.js — GENERATED, do not hand-edit
```

## Regenerating the sample data

`src/data/bundles.js` is generated from the real run directories of the core
repository. It is committed so the site needs no build:

```bash
python tools/build_samples.py --runs ../flashpilot/runs   # copy runs + emit bundles.js
python tools/verify_samples.py                            # prove the copy is byte-identical
```

`verify_samples.py` is the CI counterpart of the in-browser verifier: it
recomputes every manifest hash on disk *and* checks that the base64 embedded in
`bundles.js` decodes to those same bytes. CI refuses to deploy if it fails.

## Design system

Avionics go/no-go instrument readout: the verdict is the hero, everything else
grounds in hashes and evidence. Colour only ever encodes pass / fail / unknown /
provenance — never decoration. Motion is limited to exactly three orchestrated
moments (verdict stamp lock-in, metric count-up, tamper transition), all of them
disabled under `prefers-reduced-motion`.

Tokens live in `src/design/tokens.css`. No surface hard-codes a colour.
