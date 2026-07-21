/* Run gallery — the judge sandbox. Every card is a real run, copied verbatim
 * from the core's output directories. */

import { h } from "../lib/dom.js";
import { RUNS, HERO_PAIR, getRun } from "../lib/bundle.js";
import { panel, pill, stateClass, btn, metricGrid, metric } from "../components/kit.js";


function runCard(run) {
  return h(
    "a",
    { class: `run-card ${stateClass(run.state)}`, href: `#/run/${run.id}` },
    h(
      "div",
      { class: "row", style: "justify-content:space-between;align-items:baseline" },
      h("span", { class: "card-verdict", text: run.verdict }),
      pill(run.kind, "neutral"),
    ),
    h("h3", { text: run.title }),
    h("p", { class: "card-sub", text: run.subtitle }),
    h(
      "div",
      { class: "card-meta" },
      pill(run.framework, "data"),
      run.gate.total
        ? pill(`${run.gate.passedCount}/${run.gate.total} checks`, run.state)
        : null,
      run.attestation ? pill("attested", "pass") : pill("no attestation", "unknown"),
    ),
  );
}

export function renderGallery() {
  const verified = RUNS.filter((r) => r.state === "pass").length;
  const failed = RUNS.filter((r) => r.state === "fail").length;
  const unknown = RUNS.filter((r) => r.state === "unknown").length;

  const [failId, passId] = HERO_PAIR;
  const failRun = getRun(failId);
  const passRun = getRun(passId);

  return h(
    "div",
    { class: "stack" },
    h(
      "header",
      { class: "stack-tight" },
      h("p", { class: "eyebrow", text: "pre-flight qualification · run gallery" }),
      h("h1", { text: "Frameworks save checkpoints. This proves they can resume." }),
      h(
        "p",
        { class: "lede" },
        "Every run below was produced by the FlashPilot CLI on real code, with a real process kill ",
        "and a real resume in a new process. This page renders those artifacts and re-verifies their ",
        "hashes in your browser. It never computes a verdict of its own.",
      ),
      h(
        "div",
        { class: "row", style: "margin-top:var(--s-4)" },
        btn("Start the proof", { href: "#/compare", primary: true }),
        btn("Explore all runs", { href: "#all-runs" }),
      ),
    ),

    metricGrid(
      metric("Runs in sandbox", String(RUNS.length)),
      metric("Verified", String(verified), { state: "pass" }),
      metric("Failed", String(failed), { state: "fail" }),
      metric("Unknown", String(unknown), { state: "unknown", note: "never rendered as pass" }),
    ),

    failRun && passRun
      ? panel(
          "The scene worth two minutes",
          {
            actions: btn("Open side by side", { href: "#/compare", primary: true }),
            raised: true,
          },
          h(
            "p",
            { class: "lede" },
            "Two Hugging Face checkpoints from the same training script. Both load without an error. ",
            "One resumes the same run; the other silently does not.",
          ),
          h(
            "div",
            { class: "compare", style: "margin-top:var(--s-4)" },
            heroColumn(failRun),
            heroColumn(passRun),
          ),
        )
      : null,

    h(
      "div",
      { id: "all-runs" },
      panel("All runs", {}, h("div", { class: "card-grid" }, ...RUNS.map(runCard))),
    ),
  );
}

function heroColumn(run) {
  return h(
    "a",
    {
      class: `compare-col ${stateClass(run.state)}`,
      href: `#/run/${run.id}`,
      style: "text-decoration:none;color:inherit;display:block",
    },
    h("div", { class: "card-verdict", text: run.verdict }),
    h("h3", { text: run.title, style: "margin-top:var(--s-2)" }),
    h("p", { class: "card-sub", text: run.subtitle, style: "margin:var(--s-2) 0 var(--s-3)" }),
    h(
      "div",
      { class: "compare-metric" },
      h("span", { text: "Requirements met" }),
      h("span", { class: "v", text: `${run.gate.passedCount}/${run.gate.total}` }),
    ),
    h(
      "div",
      { class: "compare-metric" },
      h("span", { text: "Trajectory" }),
      h("span", {
        class: "v",
        text:
          run.trajectory.divergenceStep === null
            ? "identical"
            : `diverges at step ${run.trajectory.divergenceStep + 1}`,
      }),
    ),
    h(
      "div",
      { class: "compare-metric" },
      h("span", { text: "Attestation" }),
      h("span", { class: "v", text: run.attestation ? "issued" : "withheld" }),
    ),
  );
}
