/* CI surface — the same evidence as a pull-request check.
 *
 * The JUnit XML rendered here is the exact file the CLI wrote; it is parsed in
 * the browser, not re-derived. Exit codes come from flashpilot.ci.exits. */

import { h } from "../lib/dom.js";
import { panel, pill, banner, metric, metricGrid, stateClass, btn } from "../components/kit.js";
import { getRun, HERO_PAIR } from "../lib/bundle.js";

/** Copied from src/flashpilot/ci/exits.py — the contract CI actually branches on. */
const EXIT_CODES = {
  0: { name: "VERIFIED", state: "pass", merge: "allowed", note: "Recovery was proven end to end." },
  2: { name: "REVIEW", state: "unknown", merge: "held", note: "Evidence needs a human decision." },
  3: { name: "QUALIFICATION FAILED", state: "fail", merge: "blocked", note: "A required capability was not met." },
  4: { name: "INVALID EVIDENCE", state: "fail", merge: "blocked", note: "Evidence did not verify — never treated as a pass." },
  5: { name: "UNSUPPORTED", state: "unknown", merge: "blocked", note: "Layout or framework was not recognised." },
};

function exitCodeFor(run) {
  if (run.state === "pass") return 0;
  if (run.state === "fail") return 3;
  return 5;
}

function parseJUnit(xml) {
  if (!xml) return null;
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  if (doc.querySelector("parsererror")) return null;
  const suite = doc.querySelector("testsuite");
  if (!suite) return null;
  const properties = {};
  for (const p of suite.querySelectorAll("properties > property")) {
    properties[p.getAttribute("name")] = p.getAttribute("value");
  }
  const cases = [...suite.querySelectorAll("testcase")].map((tc) => {
    const failure = tc.querySelector("failure");
    const skipped = tc.querySelector("skipped");
    return {
      name: tc.getAttribute("name"),
      classname: tc.getAttribute("classname"),
      message: failure?.getAttribute("message") ?? null,
      detail: (failure?.textContent ?? tc.querySelector("system-out")?.textContent ?? "").trim(),
      state: failure ? "fail" : skipped ? "unknown" : "pass",
    };
  });
  return {
    name: suite.getAttribute("name"),
    tests: Number(suite.getAttribute("tests") ?? cases.length),
    failures: Number(suite.getAttribute("failures") ?? 0),
    properties,
    cases,
  };
}

export function renderCi(run) {
  const suite = parseJUnit(run.junit);
  const attSuite = parseJUnit(run.attestationJunit);
  const code = exitCodeFor(run);
  const exit = EXIT_CODES[code];

  return h(
    "div",
    { class: "stack" },
    h(
      "header",
      { class: "stack-tight" },
      h("p", { class: "eyebrow", text: "continuous integration · pull-request check" }),
      h("h1", { text: "Blocking a bad policy before an expensive run" }),
      h(
        "p",
        { class: "lede" },
        "The same typed evidence drives the local CLI and the CI check. Nothing is re-decided here: ",
        "the annotations below come from the JUnit file the run emitted.",
      ),
    ),

    banner(
      exit.state,
      h(
        "div",
        {},
        h("strong", { text: `exit ${code} · ${exit.name} — merge ${exit.merge}. ` }),
        exit.note,
      ),
    ),

    metricGrid(
      metric("Requirements", suite ? String(suite.tests) : "—"),
      metric("Failing", suite ? String(suite.failures) : "—", {
        state: suite?.failures ? "fail" : "pass",
      }),
      metric("Exit code", String(code), { state: exit.state }),
      metric("Merge", exit.merge, { state: exit.merge === "allowed" ? "pass" : "fail" }),
    ),

    mergeGate(run),

    suite
      ? panel(
          suite.name,
          { actions: propertyPills(suite.properties) },
          h("div", {}, ...suite.cases.map(annotation)),
        )
      : panel("Qualification check", {}, h("p", { class: "lede", text: "This run did not emit a JUnit report." })),

    attSuite
      ? panel(
          attSuite.name,
          { actions: propertyPills(attSuite.properties) },
          h("div", {}, ...attSuite.cases.map(annotation)),
        )
      : null,

    run.jobSummary ? panel("Job summary (as posted to the run)", {}, jobSummary(run.jobSummary)) : null,

    panel(
      "Exit-code contract",
      {},
      h(
        "div",
        {},
        ...Object.entries(EXIT_CODES).map(([value, meta]) =>
          h(
            "div",
            { class: `compare-metric ${stateClass(meta.state)}` },
            h(
              "span",
              {},
              h("span", { class: "mono", text: `exit ${value} · ${meta.name}` }),
              h("div", { class: "lede", style: "font-size:var(--step--1)", text: meta.note }),
            ),
            h("span", { class: "v", text: `merge ${meta.merge}` }),
          ),
        ),
        h(
          "p",
          { class: "lede", style: "margin-top:var(--s-4)" },
          "UNKNOWN and INVALID EVIDENCE both block. There is no exit code that turns an unproven ",
          "checkpoint into a passing check.",
        ),
      ),
    ),
  );
}

function mergeGate(current) {
  const [failId, passId] = HERO_PAIR;
  const failRun = getRun(failId);
  const passRun = getRun(passId);
  if (!failRun || !passRun) return null;

  const column = (run) => {
    const code = exitCodeFor(run);
    const exit = EXIT_CODES[code];
    return h(
      "div",
      { class: `compare-col ${stateClass(run.state)}` },
      h("div", { class: "row", style: "justify-content:space-between" }, h("strong", { text: run.verdict }), pill(`exit ${code}`, run.state)),
      h("h3", { text: run.title, style: "margin-top:var(--s-2)" }),
      h(
        "div",
        { class: "compare-metric" },
        h("span", { text: "Persistence policy" }),
        h("span", { class: "v", text: run.scenario ?? "—" }),
      ),
      h(
        "div",
        { class: "compare-metric" },
        h("span", { text: "Failing requirements" }),
        h("span", { class: "v", text: String(run.gate.failedCount) }),
      ),
      h(
        "div",
        { class: "compare-metric" },
        h("span", { text: "Merge" }),
        h("span", { class: "v", text: exit.merge }),
      ),
      run.id === current.id ? null : btn("Open this check", { href: `#/run/${run.id}/ci` }),
    );
  };

  return panel(
    "The policy regression, as CI sees it",
    {},
    h(
      "p",
      { class: "lede", style: "margin-bottom:var(--s-4)" },
      "Same training script, same gate, one difference: what the checkpoint callback persists. ",
      "Dropping optimizer, scheduler and RNG state still produces a checkpoint that loads — and a ",
      "check that blocks the merge.",
    ),
    h("div", { class: "compare" }, column(passRun), column(failRun)),
  );
}

function propertyPills(properties) {
  return h(
    "div",
    { class: "row" },
    ...Object.entries(properties)
      .slice(0, 4)
      .map(([k, v]) => pill(`${k}=${v}`, "neutral")),
  );
}

function annotation(tc) {
  return h(
    "div",
    { class: `gate-check ${stateClass(tc.state)}` },
    h("span", { class: "tick", "aria-hidden": "true" }),
    h(
      "div",
      {},
      h("span", { class: "check-label", text: tc.message ?? tc.name }),
      h("span", { class: "check-id", text: `${tc.classname} · ${tc.name}` }),
    ),
    h("div", { class: "check-delta" }, h("span", { class: "actual", text: tc.detail || tc.state })),
  );
}

/** The job summary is markdown the core wrote; render its structure, not HTML. */
function jobSummary(markdown) {
  const lines = markdown.split(/\r?\n/);
  const nodes = [];
  for (const line of lines) {
    if (!line.trim()) continue;
    if (line.startsWith("## ")) nodes.push(h("h3", { text: line.slice(3), style: "margin-top:var(--s-4)" }));
    else if (line.startsWith("# ")) nodes.push(h("h3", { text: line.slice(2) }));
    else if (line.startsWith("- ")) nodes.push(h("div", { class: "mono", style: "color:var(--ink-muted)", text: line.slice(2).replace(/[`*]/g, "") }));
    else nodes.push(h("p", { class: "lede", text: line.replace(/[`*]/g, "") }));
  }
  return h("div", { class: "stack-tight" }, ...nodes);
}
