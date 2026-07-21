/* CI surface — the same evidence as a pull-request check.
 *
 * Hard rule for this surface: every value shown must have been RECORDED by the
 * core. The UI does not derive exit codes, does not decide merges, and does not
 * infer a policy verdict. Where the core recorded nothing, this page says so
 * rather than computing a plausible-looking substitute.
 *
 * The JUnit XML is the exact file the CLI wrote, parsed in the browser. */

import { h } from "../lib/dom.js";
import { panel, pill, banner, metric, metricGrid, stateClass } from "../components/kit.js";

/** Documented in src/flashpilot/ci/exits.py. Shown as a reference table only —
 *  this page never selects a code on a run's behalf. */
const EXIT_CODES = [
  [0, "VERIFIED", "pass", "Recovery was proven end to end."],
  [2, "REVIEW", "unknown", "Evidence needs a human decision."],
  [3, "QUALIFICATION FAILED", "fail", "A required capability was not met."],
  [4, "INVALID EVIDENCE", "fail", "Evidence did not verify — never treated as a pass."],
  [5, "UNSUPPORTED", "unknown", "Layout or framework was not recognised."],
];

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

  return h(
    "div",
    { class: "stack" },
    h(
      "header",
      { class: "stack-tight" },
      h("p", { class: "eyebrow", text: "continuous integration · recorded evidence" }),
      h("h1", { text: "The same evidence, as a pull-request check" }),
      h(
        "p",
        { class: "lede" },
        "The same typed evidence drives the local CLI and the CI check. Nothing is re-decided here: ",
        "every value below was written by the run that produced it.",
      ),
    ),

    verdictBanner(run),
    suiteMetrics(run, suite),
    policyPanel(run),

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

    run.jobSummary ? panel("Job summary (as written by the run)", {}, jobSummary(run.jobSummary)) : null,

    panel(
      "Exit-code contract",
      {},
      h(
        "p",
        { class: "lede", style: "margin-bottom:var(--s-4)" },
        "The codes FlashPilot's CI entrypoints return, from ",
        h("span", { class: "mono", text: "src/flashpilot/ci/exits.py" }),
        ". This is reference documentation — this page does not assign a code to any run.",
      ),
      ...EXIT_CODES.map(([value, name, state, note]) =>
        h(
          "div",
          { class: `compare-metric ${stateClass(state)}` },
          h(
            "span",
            {},
            h("span", { class: "mono", text: `exit ${value} · ${name}` }),
            h("div", { class: "lede", style: "font-size:var(--step--1)", text: note }),
          ),
          h("span", { class: "v", text: state === "pass" ? "merge allowed" : "merge blocked" }),
        ),
      ),
      h(
        "p",
        { class: "lede", style: "margin-top:var(--s-4)" },
        "UNKNOWN and INVALID EVIDENCE both block. There is no code that turns an unproven ",
        "checkpoint into a passing check.",
      ),
    ),
  );
}

/** The gate verdict, copied. No exit code is inferred from it. */
function verdictBanner(run) {
  const copy =
    run.state === "pass"
      ? "The recovery gate passed. Every requirement below was met."
      : run.state === "fail"
        ? "The recovery gate failed. The failing requirements are listed below."
        : "The gate did not reach a verdict. UNKNOWN is never rendered as a pass.";
  return banner(
    run.state,
    h(
      "div",
      {},
      h("strong", { text: `Recovery gate: ${run.verdict}. ` }),
      copy,
    ),
  );
}

function suiteMetrics(run, suite) {
  return metricGrid(
    metric("Requirements", suite ? String(suite.tests) : String(run.gate.total || "—")),
    metric("Failing", suite ? String(suite.failures) : String(run.gate.failedCount), {
      state: (suite ? suite.failures : run.gate.failedCount) ? "fail" : "pass",
    }),
    metric("Gate verdict", run.verdict, { state: run.state }),
    metric("Attestation", run.attestation ? "issued" : "withheld", {
      state: run.attestation ? "pass" : "unknown",
    }),
  );
}

/**
 * Organization-policy evaluation.
 *
 * Rendered only from a recorded `organization-policy-evaluation.json`. When the
 * run carries none, this states that plainly. An absent policy evaluation is
 * not a passing one, and it is not something this page may reconstruct.
 */
function policyPanel(run) {
  const evaluation = run.policyEvaluation;

  if (!evaluation) {
    return panel(
      "Organization policy",
      { actions: pill("not evaluated", "unknown") },
      h(
        "p",
        { class: "lede" },
        "This run carries no organization-policy evaluation, so none is shown. The policy verdict, ",
        "its exit code, and the resulting merge decision are produced by ",
        h("span", { class: "mono", text: "flashpilot enforce-organization-policy" }),
        " and are only displayed here when that command has actually written them into the run.",
      ),
      h(
        "p",
        { class: "lede", style: "margin-top:var(--s-3)" },
        "The checkpoint-content difference between the samples in this sandbox is a difference in ",
        "what each callback persists — not an organization-policy change, and it is not presented as one.",
      ),
    );
  }

  // Every field below is copied verbatim from the recorded evaluation. Where
  // the core recorded nothing, this reports that rather than deriving a value:
  // a page that computes its own merge decision is deciding policy.
  const passed = evaluation.passed === true;
  const state = passed ? "pass" : "fail";
  const requirements = Array.isArray(evaluation.requirements) ? evaluation.requirements : [];
  const recordedExit = Number.isInteger(evaluation.exit_code) ? String(evaluation.exit_code) : null;
  const recordedMerge =
    evaluation.merge_decision === "allowed" || evaluation.merge_decision === "blocked"
      ? evaluation.merge_decision
      : null;

  return panel(
    "Organization policy",
    { actions: pill(passed ? "PASS" : "FAIL", state) },
    metricGrid(
      metric("Policy verdict", passed ? "PASS" : "FAIL", { state }),
      metric("Exit code", recordedExit ?? "not recorded", {
        state: recordedExit ? state : "unknown",
      }),
      metric("Requirements", `${requirements.filter((r) => r.passed).length}/${requirements.length}`, {
        state,
      }),
      metric("Merge", recordedMerge ?? "not recorded", {
        state: recordedMerge ? state : "unknown",
        note: recordedMerge ? null : "recorded merge decision unavailable",
      }),
    ),
    h(
      "div",
      { style: "margin-top:var(--s-4)" },
      h("div", { class: "gate-group-title", text: `${evaluation.organization_id ?? "organization"} · ${evaluation.policy_id ?? "policy"}` }),
      ...requirements.map((req) =>
        h(
          "div",
          { class: `compare-metric ${stateClass(req.passed ? "pass" : "fail")}` },
          h(
            "span",
            {},
            h("span", { class: "mono", text: req.requirement_id ?? "requirement" }),
            req.summary
              ? h("div", { class: "lede", style: "font-size:var(--step--1)", text: req.summary })
              : null,
          ),
          h("span", { class: "v", text: req.passed ? "PASS" : "FAIL" }),
        ),
      ),
    ),
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
    else if (line.startsWith("- "))
      nodes.push(h("div", { class: "mono", style: "color:var(--ink-muted)", text: line.slice(2).replace(/[`*]/g, "") }));
    else nodes.push(h("p", { class: "lede", text: line.replace(/[`*]/g, "") }));
  }
  return h("div", { class: "stack-tight" }, ...nodes);
}
