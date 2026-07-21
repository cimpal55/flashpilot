/* Report surface — one run rendered in full: verdict, gate, trajectory,
 * process reality, metrics, provenance and the trust boundary. */

import { h, shortHash } from "../lib/dom.js";
import { panel, pill, verdictStamp, metric, metricGrid, taxonomyPill, btn, stateClass } from "../components/kit.js";
import { gateReadout, trajectoryLanes, provenanceHashes, trustPanel, processReadout } from "../components/blocks.js";
import { sha256Hex } from "../lib/hash.js";

export function renderReport(run) {
  return h(
    "div",
    { class: "stack" },
    headline(run),
    verdictSummary(run),
    whyItFailed(run),
    run.staticOnly ? staticOnlyBanner() : null,
    panel(
      "Recovery gate",
      {
        actions: h(
          "div",
          { class: "row" },
          pill(`${run.gate.passedCount} pass`, "pass"),
          run.gate.failedCount ? pill(`${run.gate.failedCount} fail`, "fail") : null,
          run.gate.unknownCount ? pill(`${run.gate.unknownCount} unknown`, "unknown") : null,
        ),
      },
      h(
        "p",
        { class: "lede", style: "margin-bottom:var(--s-4)" },
        "Every requirement below is copied from the CLI result. Tolerances are exact: ",
        h("span", { class: "mono", text: `atol=${run.gate.atol ?? "—"} rtol=${run.gate.rtol ?? "—"}` }),
        ".",
      ),
      gateReadout(run),
    ),
    h(
      "div",
      { class: "grid-2" },
      panel("Trajectory", {}, trajectoryLanes(run)),
      panel("Process reality", {}, processReadout(run) ?? h("p", { class: "lede", text: "Static audit only — no processes were run." })),
    ),
    run.digests.length ? panel("State digests", {}, digestTable(run)) : null,
    panel("Contract taxonomy", {}, taxonomyLegend(run)),
    panel("Provenance", {}, provenanceHashes(run)),
    portableArtifact(run),
    trustPanel(run),
    run.limitations.length ? panel("Stated limitations", {}, limitationList(run)) : null,
  );
}

function headline(run) {
  return h(
    "header",
    { class: "stack-tight" },
    h("p", { class: "eyebrow", text: `${run.framework} · ${run.profile}` }),
    h("h1", { text: run.title }),
    h("p", { class: "lede", text: run.subtitle }),
    h(
      "div",
      { class: "row" },
      pill(run.adapter, "data"),
      run.scenario ? pill(run.scenario, "neutral") : null,
      run.runId ? pill(`run ${/^[0-9a-f]{16,}$/i.test(run.runId) ? run.runId.slice(0, 8) : run.runId}`, "neutral") : null,
      pill(`samples/${run.id}`, "neutral"),
    ),
  );
}

function verdictSummary(run) {
  const rpo = run.gate.rpo;
  const rto = run.attestation?.rto_seconds;
  return h(
    "div",
    { class: "grid-2", style: "align-items:start" },
    h(
      "div",
      { class: "stack-tight" },
      verdictStamp(run.verdict, run.state, `${run.profile} · ${run.framework}`),
      h(
        "p",
        { class: "lede" },
        run.state === "pass"
          ? "The checkpoint was killed for real, resumed in a new process, and reproduced the control run exactly."
          : run.state === "fail"
            ? "The checkpoint loaded without error. It did not reproduce the control run — so it cannot resume it."
            : "The layout was not recognised. FlashPilot refuses to guess, and UNKNOWN never renders as a pass.",
      ),
    ),
    metricGrid(
      metric("Requirements met", `${run.gate.passedCount}/${run.gate.total}`, {
        state: run.gate.failedCount ? "fail" : "pass",
      }),
      metric("RPO", rpo === null ? "—" : `${rpo} steps`, {
        note: run.gate.maxRpo === null ? null : `budget ${run.gate.maxRpo}`,
        state: rpo === null ? "unknown" : rpo <= (run.gate.maxRpo ?? rpo) ? "pass" : "fail",
      }),
      metric("RTO", rto ? "0" : "—", {
        state: "pass",
        animate: rto ? { value: rto, decimals: 2, suffix: " s" } : null,
      }),
      metric("Attestation", run.attestation ? "issued" : "withheld", {
        state: run.attestation ? "pass" : "unknown",
      }),
    ),
  );
}

/** The attestation as a file you can take, not just a screen you can read.
 *
 * The bytes shown, hashed and downloaded here are the exact bytes of
 * recovery.attestation.json — never a re-serialisation, which would hash
 * differently and quietly break the portability claim. */
function portableArtifact(run) {
  if (!run.attestationBytes) return null;

  const bytes = run.attestationBytes;
  const computedCell = h("dd", { text: "computing…" });
  const crossCheckCell = h("dd", { text: "—" });

  // The CI suite independently recorded the attestation's hash; extract it
  // from the JUnit file so the browser's result can be checked against it.
  const recorded =
    run.attestationJunit?.match(/"attestation_sha256"\s+value="([0-9a-f]{64})"/)?.[1] ?? null;

  queueMicrotask(async () => {
    try {
      const digest = await sha256Hex(bytes);
      computedCell.textContent = digest;
      if (!recorded) {
        crossCheckCell.textContent = "not recorded by this run's CI suite";
      } else if (digest === recorded) {
        crossCheckCell.className = "match";
        crossCheckCell.textContent = `matches attestation.junit.xml · ${shortHash(recorded, 12, 8)}`;
      } else {
        crossCheckCell.className = "differ";
        crossCheckCell.textContent = `DOES NOT MATCH attestation.junit.xml · ${shortHash(recorded, 12, 8)}`;
      }
    } catch (error) {
      computedCell.textContent = `unavailable — ${error.message}`;
    }
  });

  const download = btn("Download attestation.json", { primary: true });
  download.addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([bytes], { type: "application/json" }));
    const link = h("a", { href: url, download: "recovery.attestation.json" });
    link.click();
    URL.revokeObjectURL(url);
  });

  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    text = null;
  }

  return panel(
    "Portable artifact",
    { actions: download },
    h(
      "p",
      { class: "lede", style: "margin-bottom:var(--s-4)" },
      "The attestation is a file, not a page. Take it, mail it, commit it — anyone can re-verify ",
      "it without FlashPilot installed. The hash below is computed by your browser over the exact ",
      "bytes you would download.",
    ),
    h(
      "dl",
      { class: "hash-list" },
      h(
        "div",
        { class: "hash-item" },
        h("dt", { text: "SHA-256 (computed here)" }),
        computedCell,
      ),
      h(
        "div",
        { class: "hash-item" },
        h("dt", { text: "Independent record" }),
        crossCheckCell,
      ),
      h(
        "div",
        { class: "hash-item" },
        h("dt", { text: "Size" }),
        h("dd", { text: `${bytes.length} bytes` }),
      ),
    ),
    text
      ? h(
          "details",
          { class: "artifact-details" },
          h("summary", { text: "Show the raw bytes (as text)" }),
          h("pre", { class: "artifact-raw mono", text: text }),
        )
      : null,
  );
}

/**
 * "Why it failed", derived deterministically from the first three failed gate
 * checks in the order the core recorded them. No ranking heuristic, no
 * generated prose, no model: the same run always yields the same summary.
 */
function whyItFailed(run) {
  if (run.state !== "fail") return null;
  const failed = run.gate.checks.filter((c) => c.state === "fail");
  if (failed.length === 0) return null;
  const shown = failed.slice(0, 3);
  const rest = failed.length - shown.length;

  return panel(
    "Why it failed",
    { actions: pill(`${failed.length} failing`, "fail") },
    h(
      "p",
      { class: "lede", style: "margin-bottom:var(--s-4)" },
      "The first ",
      String(shown.length),
      " failed requirements, in the order the gate recorded them.",
    ),
    ...shown.map((check) =>
      h(
        "div",
        { class: `compare-metric ${stateClass("fail")}` },
        h(
          "span",
          {},
          h("span", { text: check.label }),
          h("div", { class: "check-id mono", text: check.id }),
        ),
        h("span", {
          class: "v",
          title: `expected ${check.expected}\nactual ${check.actual}`,
          text: `expected ${abbreviate(check.expected)} · got ${abbreviate(check.actual)}`,
        }),
      ),
    ),
    rest > 0
      ? h("p", { class: "lede", style: "margin-top:var(--s-3)", text: `${rest} further requirement${rest === 1 ? "" : "s"} also failed — see the full gate readout below.` })
      : null,
  );
}

function abbreviate(value) {
  if (value === null || value === undefined) return "—";
  const text = String(value);
  if (/^[0-9a-f]{64}$/i.test(text)) return shortHash(text, 8, 4);
  return text.length > 40 ? `${text.slice(0, 38)}…` : text;
}

function staticOnlyBanner() {
  return h(
    "div",
    { class: "banner state-unknown" },
    h("div", {}, h("strong", { text: "Static audit only. " }), "No recovery was executed for this checkpoint, so no claim about resuming it is made."),
  );
}

function digestTable(run) {
  return h(
    "div",
    {},
    ...run.digests.map((d) =>
      h(
        "div",
        { class: `compare-metric ${d.match ? "state-pass" : "state-fail"}` },
        h("span", { text: d.label }),
        h("span", {
          class: "v",
          title: `control ${d.control}\nresumed ${d.recovery}`,
          text: d.match
            ? `identical · ${shortHash(d.control, 10, 6)}`
            : `${shortHash(d.control, 8, 4)} ≠ ${shortHash(d.recovery, 8, 4)}`,
        }),
      ),
    ),
  );
}

function taxonomyLegend(run) {
  const items = Array.isArray(run.contract?.items) ? run.contract.items : [];
  if (items.length === 0) {
    return h(
      "div",
      { class: "row" },
      ...["REQUIRED", "EPHEMERAL", "EXACT", "RESOLVED", "NO SOURCE", "UNKNOWN"].map(taxonomyPill),
      h(
        "p",
        { class: "lede", style: "width:100%;margin-top:var(--s-3)" },
        "This vocabulary is shared by every surface. It comes from the persistence contract; ",
        "this run did not ship one, so no per-item classification is shown.",
      ),
    );
  }
  return h(
    "div",
    {},
    ...items.slice(0, 40).map((item) =>
      h(
        "div",
        { class: "compare-metric" },
        h("span", { class: "mono", text: item.key ?? item.name ?? "item" }),
        h(
          "span",
          { class: "row", style: "justify-content:flex-end" },
          taxonomyPill(String(item.classification ?? item.kind ?? "UNKNOWN").toUpperCase()),
        ),
      ),
    ),
  );
}

function limitationList(run) {
  return h(
    "ul",
    { class: "lede", style: "margin:0;padding-left:1.1rem" },
    ...run.limitations.map((l) => h("li", { text: l })),
  );
}
