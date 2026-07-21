/* Composite components: the gate readout, trajectory lanes, evidence table,
 * provenance hashes and the GPT trust panel. */

import { h, shortHash, formatBytes } from "../lib/dom.js";
import { stateClass, pill, panel } from "./kit.js";
import { STATUS } from "../lib/hash.js";

const CATEGORY_TITLES = {
  checkpoint: "Checkpoint contents",
  process: "Process reality",
  trajectory: "Trajectory",
  state: "State digests",
  detection: "Layout detection",
  other: "Other requirements",
};

/** GateReadout — every requirement, grouped, with expected vs actual. */
export function gateReadout(run) {
  // Categories arrive either as slugs (`checkpoint`) or as already-readable
  // titles (`Required training state`), depending on which command wrote them.
  const groups = new Map();
  for (const check of run.gate.checks) {
    const key = check.category || "other";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(check);
  }

  const body = [...groups.entries()].map(([category, checks]) =>
    h(
      "div",
      { class: "gate-group" },
      h("div", { class: "gate-group-title", text: CATEGORY_TITLES[category.toLowerCase()] ?? category }),
      ...checks.map((check) =>
        h(
          "div",
          { class: `gate-check ${stateClass(check.state)}` },
          h("span", { class: "tick", "aria-hidden": "true" }),
          h(
            "div",
            {},
            h("span", { class: "check-label", text: check.label }),
            h("span", { class: "check-id", text: check.id }),
          ),
          h(
            "div",
            { class: "check-delta" },
            check.expected !== null
              ? h("span", { class: "expected", text: `expected ${formatCell(check.expected)}` })
              : null,
            h("span", { class: "actual", text: `${check.status.toLowerCase()} · ${formatCell(check.actual)}` }),
          ),
        ),
      ),
    ),
  );

  return h("div", { class: "gate-readout" }, ...body);
}

function formatCell(value) {
  if (value === null || value === undefined) return "—";
  const text = String(value);
  return /^[0-9a-f]{64}$/i.test(text) ? shortHash(text) : text;
}

const SVG_NS = "http://www.w3.org/2000/svg";

function svgEl(tag, attrs = {}, ...children) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== null && value !== undefined) el.setAttribute(key, String(value));
  }
  el.append(...children);
  return el;
}

/**
 * The recorded loss values as two lines. This is the plot the whole argument
 * hangs on: the resumed run either lies on the control line or it does not.
 * Values are the CLI's recorded loss_history, plotted verbatim.
 */
function lossChart(run) {
  const { control, recovery, divergenceStep } = run.trajectory;
  if (!Array.isArray(control) || control.length < 2) return null;
  const series = [control, recovery ?? []];
  const all = series.flat().filter((v) => Number.isFinite(v));
  if (all.length < 2) return null;

  const W = 640;
  const HEIGHT = 230;
  const pad = { l: 62, r: 14, t: 14, b: 30 };
  let yMin = Math.min(...all);
  let yMax = Math.max(...all);
  if (yMin === yMax) {
    yMin -= 1e-6;
    yMax += 1e-6;
  }
  const span = yMax - yMin;
  yMin -= span * 0.08;
  yMax += span * 0.08;
  const steps = control.length;
  const x = (i) => pad.l + (i / (steps - 1)) * (W - pad.l - pad.r);
  const y = (v) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * (HEIGHT - pad.t - pad.b);

  const pointsOf = (values) => values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");

  const svg = svgEl("svg", {
    viewBox: `0 0 ${W} ${HEIGHT}`,
    role: "img",
    "aria-label":
      divergenceStep === null
        ? `Loss per step: the resumed line lies exactly on the control line for all ${steps} steps.`
        : `Loss per step: the resumed line leaves the control line at step ${divergenceStep + 1}.`,
  });

  // Gridlines + y labels at min / mid / max of the plotted range.
  for (const v of [yMin + span * 0.08, (yMin + yMax) / 2, yMax - span * 0.08]) {
    svg.append(
      svgEl("line", { x1: pad.l, x2: W - pad.r, y1: y(v), y2: y(v), class: "chart-grid" }),
      svgEl("text", { x: pad.l - 8, y: y(v) + 3, class: "chart-tick", "text-anchor": "end" }, v.toFixed(4)),
    );
  }
  // x labels: step numbers.
  for (let i = 0; i < steps; i += 1) {
    svg.append(
      svgEl("text", { x: x(i), y: HEIGHT - 10, class: "chart-tick", "text-anchor": "middle" }, String(i + 1)),
    );
  }

  if (divergenceStep !== null && divergenceStep < steps) {
    svg.append(
      svgEl("line", {
        x1: x(divergenceStep),
        x2: x(divergenceStep),
        y1: pad.t,
        y2: HEIGHT - pad.b,
        class: "chart-divergence",
      }),
      svgEl(
        "text",
        {
          x: x(divergenceStep) + 6,
          y: pad.t + 12,
          class: "chart-divergence-label",
          "text-anchor": divergenceStep > steps / 2 ? "end" : "start",
          dx: divergenceStep > steps / 2 ? -12 : 0,
        },
        `diverges · step ${divergenceStep + 1}`,
      ),
    );
  }

  svg.append(svgEl("polyline", { points: pointsOf(control), class: "chart-line chart-line-control" }));
  if (recovery?.length) {
    svg.append(svgEl("polyline", { points: pointsOf(recovery), class: "chart-line chart-line-resumed" }));
  }
  for (const [values, cls] of [[control, "chart-dot-control"], [recovery ?? [], "chart-dot-resumed"]]) {
    values.forEach((v, i) => {
      const dot = svgEl("circle", { cx: x(i), cy: y(v), r: 3.2, class: `chart-dot ${cls}` });
      dot.append(svgEl("title", {}, `step ${i + 1}: ${v}`));
      svg.append(dot);
    });
  }

  return h(
    "figure",
    { class: `traj-chart ${stateClass(divergenceStep === null ? "pass" : "fail")}` },
    svg,
    h(
      "figcaption",
      { class: "chart-legend" },
      h("span", { class: "legend-item legend-control", text: "control" }),
      h("span", { class: "legend-item legend-resumed", text: "resumed" }),
      h("span", { class: "legend-note", text: "recorded loss per step, plotted verbatim" }),
    ),
  );
}

/** TrajectoryLanes — control above, recovery below, divergence made visible. */
export function trajectoryLanes(run) {
  const { control, recovery, divergenceStep } = run.trajectory;
  if (!Array.isArray(control) || control.length === 0) {
    return h("p", { class: "lede", text: "This run did not record a step-by-step loss trajectory." });
  }
  const length = Math.max(control.length, recovery?.length ?? 0);

  const laneFor = (name, series) =>
    h(
      "div",
      { class: "lane" },
      h("span", { class: "lane-name", text: name }),
      h(
        "div",
        { class: "lane-track" },
        ...Array.from({ length }, (_, i) => {
          const value = series?.[i];
          const missing = value === undefined;
          const same = !missing && control[i] === recovery?.[i];
          const state = missing ? "unknown" : same ? "pass" : "fail";
          return h("span", {
            class: `lane-cell ${stateClass(state)}`,
            dataset: { missing: String(missing) },
            title: missing ? `step ${i + 1}: not reached` : `step ${i + 1}: ${value}`,
          });
        }),
      ),
    );

  const divergence =
    divergenceStep === null
      ? h(
          "div",
          { class: `lane-divergence ${stateClass("pass")}` },
          h("strong", { text: "No divergence. " }),
          "The resumed run reproduced the control trajectory step for step.",
        )
      : h(
          "div",
          { class: `lane-divergence ${stateClass("fail")}` },
          h("strong", { text: `Diverges at step ${divergenceStep + 1}. ` }),
          divergenceLine(control, recovery, divergenceStep),
        );

  return h(
    "div",
    {},
    lossChart(run),
    h("div", { class: "lanes" }, laneFor("control", control), laneFor("resumed", recovery ?? [])),
    h(
      "div",
      { class: "lane-axis", style: "margin-left:104px" },
      ...Array.from({ length }, (_, i) => h("span", { text: String(i + 1) })),
    ),
    divergence,
  );
}

function divergenceLine(control, recovery, step) {
  const a = control[step];
  const b = recovery?.[step];
  if (b === undefined) {
    return `The resumed run stopped after ${recovery?.length ?? 0} of ${control.length} steps.`;
  }
  return h(
    "span",
    { class: "mono" },
    `control ${a} · resumed ${b}`,
  );
}

/** EvidenceRow table with a live re-verification status column.
 *
 * When `onToggleRow` is provided, each row is a button that toggles an
 * in-memory single-byte corruption of that specific file — the judge picks
 * the target instead of trusting a canned demo. */
export function evidenceTable(manifest, { onToggleRow = null, tampered = null } = {}) {
  const entries = Array.isArray(manifest?.entries) ? manifest.entries : [];
  const statusCells = new Map();

  const head = h(
    "div",
    { class: "evidence-row is-head" },
    h("span", { text: onToggleRow ? "path (click a row to tamper it)" : "path" }),
    h("span", { text: "sha-256 (manifest)" }),
    h("span", { class: "size", text: "size" }),
    h("span", { class: "status", text: "re-verify" }),
  );

  const rows = entries.map((entry) => {
    const status = h("span", { class: "status state-void", text: "pending" });
    statusCells.set(entry.path, status);
    const cells = [
      h("span", { class: "path", text: entry.path }),
      h("span", { class: "sha", title: entry.sha256, text: shortHash(entry.sha256, 12, 8) }),
      h("span", { class: "size", text: formatBytes(entry.size_bytes) }),
      status,
    ];
    if (!onToggleRow) return h("div", { class: "evidence-row" }, ...cells);
    return h(
      "button",
      {
        type: "button",
        class: "evidence-row evidence-row-btn",
        "aria-pressed": String(Boolean(tampered?.has(entry.path))),
        title: "Toggle a one-byte in-memory corruption of this file",
        onClick: () => onToggleRow(entry.path),
      },
      ...cells,
    );
  });

  const node = h(
    "div",
    { class: "evidence-scroll" },
    h("div", { class: "evidence-table" }, head, ...rows),
  );

  const statusState = {
    [STATUS.INTACT]: "pass",
    [STATUS.TAMPERED]: "fail",
    [STATUS.MISSING]: "unknown",
    [STATUS.VOID]: "void",
  };

  return {
    node,
    count: entries.length,
    setStatus(path, status) {
      const cell = statusCells.get(path);
      if (!cell) return;
      cell.className = `status ${stateClass(statusState[status] ?? "void")}`;
      cell.textContent = status.toLowerCase();
    },
    reset() {
      for (const cell of statusCells.values()) {
        cell.className = "status state-void";
        cell.textContent = "pending";
      }
    },
  };
}

/** ProvenanceHashes — where the artifact came from and what binds it. */
export function provenanceHashes(run) {
  const a = run.attestation;
  if (!a) {
    return h(
      "p",
      { class: "lede" },
      "No attestation was issued for this run. FlashPilot only issues one when the ",
      "recovery gate passes, so its absence is itself a signal.",
    );
  }
  const rows = [
    ["Attestation schema", a.schema_version],
    ["Run id", a.run_id],
    ["Issued at", a.issued_at],
    ["Code commit", a.code_commit],
    ["Source tree", a.source_tree_state],
    ["Signature", a.signature_status],
    ["Checkpoint sha-256", a.checkpoint_sha256],
    ["Evidence manifest sha-256", a.evidence_manifest_sha256],
    ["Persistence contract sha-256", a.persistence_contract_sha256],
    ["Environment sha-256", a.dependency_environment_sha256],
  ].filter(([, v]) => v !== undefined && v !== null);

  const digestMatch = a.control_digest && a.control_digest === a.resumed_digest;

  return h(
    "dl",
    { class: "hash-list" },
    ...rows.map(([label, value]) =>
      h(
        "div",
        { class: "hash-item" },
        h("dt", { text: label }),
        h("dd", { title: String(value), text: displayValue(value) }),
      ),
    ),
    h(
      "div",
      { class: "hash-item" },
      h("dt", { text: "Control vs resumed digest" }),
      h("dd", {
        class: digestMatch ? "match" : "differ",
        text: digestMatch
          ? `identical · ${shortHash(a.control_digest, 12, 8)}`
          : `${shortHash(a.control_digest, 8, 6)} ≠ ${shortHash(a.resumed_digest, 8, 6)}`,
      }),
    ),
  );
}

function displayValue(value) {
  const text = String(value);
  return /^[0-9a-f]{64}$/i.test(text) ? shortHash(text, 16, 10) : text;
}

/** GptTrustPanel — stated identically in the product, the README and the video. */
export function trustPanel(run = null) {
  const gpt = run?.gpt ?? null;
  return panel(
    "Where the model is, and is not",
    { extraClass: "trust-panel" },
    h(
      "p",
      { class: "lede" },
      "GPT-5.6 proposes contracts and diagnoses failures. Only the deterministic gate issues verdicts.",
    ),
    h(
      "div",
      { class: "trust-flow", style: "margin-top:var(--s-4)" },
      h("span", { class: "trust-step", text: "GPT-5.6 proposes a persistence contract" }),
      h("span", { class: "trust-arrow", text: "→" }),
      h("span", { class: "trust-step", text: "GPT-5.6 diagnoses the failure" }),
      h("span", { class: "trust-arrow", text: "→" }),
      h("span", { class: "trust-step is-gate", text: "deterministic gate issues the verdict" }),
    ),
    gpt ? gptEvidence(gpt) : null,
    h(
      "p",
      { class: "lede", style: "margin-top:var(--s-4)" },
      gpt
        ? "The model's output above is the persisted artifact, shown verbatim. It was filtered by a typed validator before anything ran, and it did not set the verdict."
        : "Nothing on this page is generated by a model. Every value shown is copied from the typed artifacts the CLI wrote, and the hash column is recomputed by your own browser.",
    ),
  );
}

/** The repair run persisted its actual model call — show it rather than describe it. */
function gptEvidence(gpt) {
  const analysis = gpt.analysis ?? {};
  const decisions = gpt.validation?.decisions ?? [];
  const applied = gpt.execution?.applied_actions ?? [];
  const meta = gpt.metadata ?? {};

  const dispositionState = (d) =>
    d === "accepted" ? "pass" : d === "rejected" ? "fail" : "unknown";

  return h(
    "div",
    { style: "margin-top:var(--s-5)" },
    analysis.root_cause_hypothesis
      ? h(
          "div",
          { class: "banner state-unknown", style: "margin-bottom:var(--s-4)" },
          h(
            "div",
            {},
            h("strong", { text: "Model diagnosis · " }),
            pill(`confidence ${analysis.confidence ?? "—"}`, "unknown"),
            h("p", { style: "margin-top:var(--s-2)", text: analysis.root_cause_hypothesis }),
          ),
        )
      : null,

    decisions.length
      ? h(
          "div",
          {},
          h("div", { class: "gate-group-title", text: "Proposed actions, as filtered by the typed validator" }),
          ...decisions.map((d) =>
            h(
              "div",
              { class: `compare-metric ${stateClass(dispositionState(d.disposition))}` },
              h(
                "span",
                {},
                h("span", { class: "mono", text: d.action }),
                h("div", { class: "lede", style: "font-size:var(--step--1)", text: d.reason ?? "" }),
              ),
              h("span", { class: "v", text: d.disposition }),
            ),
          ),
        )
      : null,

    applied.length
      ? h(
          "p",
          { class: "lede mono", style: "margin-top:var(--s-4)" },
          `executed: ${applied.join(", ")}`,
        )
      : null,

    h(
      "div",
      { class: "row", style: "margin-top:var(--s-4)" },
      meta.model ? pill(`model ${meta.model}`, "data") : null,
      meta.output_schema_version ? pill(meta.output_schema_version, "neutral") : null,
      meta.validation_status ? pill(meta.validation_status, "pass") : null,
      meta.request_sha256 ? pill(`request ${shortHash(meta.request_sha256, 8, 4)}`, "neutral") : null,
      meta.source ? pill(meta.source, "neutral") : null,
    ),
  );
}

/** Process reality: real termination and a genuinely distinct resume process. */
export function processReadout(run) {
  const p = run.processes;
  if (!p.control && !p.recovery) return null;
  const row = (label, proc) => {
    if (!proc) return null;
    const exit = proc.exit_code ?? proc.termination_exit_code;
    const verified = proc.exit_verified ?? proc.termination_verified;
    return h(
      "div",
      { class: "compare-metric" },
      h("span", { text: label }),
      h("span", {
        class: "v mono",
        text: [
          proc.worker_pid !== undefined ? `pid ${proc.worker_pid}` : null,
          exit !== undefined ? `exit ${exit}` : null,
          verified ? "verified" : null,
        ]
          .filter(Boolean)
          .join(" · "),
      }),
    );
  };
  return h(
    "div",
    { class: stateClass(run.state) },
    row("Control process", p.control),
    row("Killed process", p.crash),
    row("Recovery process", p.recovery),
    p.faultScenario
      ? h(
          "div",
          { class: "compare-metric" },
          h("span", { text: "Fault scenario" }),
          h("span", { class: "v mono", text: p.faultScenario }),
        )
      : null,
  );
}

export { pill };
