/* Side-by-side compare — the FAIL/PASS pair read as red → green at a glance. */

import { h, shortHash } from "../lib/dom.js";
import { panel, pill, verdictStamp, stateClass, btn } from "../components/kit.js";
import { trajectoryLanes } from "../components/blocks.js";
import { getRun, HERO_PAIR, RUNS } from "../lib/bundle.js";

export function renderCompare(params) {
  const leftId = params?.get("a") ?? HERO_PAIR[0];
  const rightId = params?.get("b") ?? HERO_PAIR[1];
  const left = getRun(leftId) ?? getRun(HERO_PAIR[0]);
  const right = getRun(rightId) ?? getRun(HERO_PAIR[1]);

  return h(
    "div",
    { class: "stack" },
    h(
      "header",
      { class: "stack-tight" },
      h("p", { class: "eyebrow", text: "side by side · same script, same gate" }),
      h("h1", { text: "It loads. It just doesn't resume the same run." }),
      h(
        "p",
        { class: "lede" },
        "Both checkpoints open without an error and both resume to the same global step. Only one of ",
        "them reproduces the run it claims to continue.",
      ),
      h("div", { class: "row" }, picker("a", left, right), picker("b", right, left)),
    ),
    h("div", { class: "compare" }, column(left), column(right)),
    panel(
      "Trajectories",
      {},
      h(
        "div",
        { class: "grid-2" },
        h("div", {}, h("h3", { text: left.title, style: "font-size:var(--step-1)" }), trajectoryLanes(left)),
        h("div", {}, h("h3", { text: right.title, style: "font-size:var(--step-1)" }), trajectoryLanes(right)),
      ),
    ),
  );
}

function picker(key, selected, other) {
  const select = h("select", {
    class: "btn",
    "aria-label": key === "a" ? "left run" : "right run",
    onChange: (event) => {
      const a = key === "a" ? event.target.value : other.id;
      const b = key === "a" ? other.id : event.target.value;
      window.location.hash = `#/compare?a=${a}&b=${b}`;
    },
  });
  for (const run of RUNS) {
    const option = h("option", { value: run.id, text: `${run.verdict} · ${run.title}` });
    if (run.id === selected.id) option.selected = true;
    select.append(option);
  }
  return select;
}

function column(run) {
  const rows = [
    ["Verdict", run.verdict],
    ["Requirements met", `${run.gate.passedCount}/${run.gate.total}`],
    ["Checkpoint loaded", run.rawResult.model_checkpoint_load_succeeded === false ? "no" : "yes"],
    ["Global step reached", stepText(run)],
    [
      "Trajectory",
      run.trajectory.divergenceStep === null ? "identical to control" : `diverges at step ${run.trajectory.divergenceStep + 1}`,
    ],
    ["Trainable digest", digestText(run)],
    ["Attestation", run.attestation ? "issued" : "withheld"],
  ];

  return h(
    "div",
    { class: `compare-col ${stateClass(run.state)}` },
    verdictStamp(run.verdict, run.state, run.framework),
    h("h3", { text: run.title, style: "margin:var(--s-3) 0 var(--s-2)" }),
    h("div", { class: "row", style: "margin-bottom:var(--s-3)" }, pill(run.scenario ?? run.kind, "neutral"), pill(run.profile, "data")),
    ...rows.map(([label, value]) =>
      h("div", { class: "compare-metric" }, h("span", { text: label }), h("span", { class: "v", text: value })),
    ),
    h(
      "div",
      { class: "row", style: "margin-top:var(--s-4)" },
      btn("Full report", { href: `#/run/${run.id}` }),
      btn("Verify", { href: `#/run/${run.id}/verify` }),
    ),
  );
}

function stepText(run) {
  const { controlStep, recoveryStep } = run.trajectory;
  if (controlStep === null && recoveryStep === null) return "—";
  return `${recoveryStep ?? "—"} of ${controlStep ?? "—"}`;
}

function digestText(run) {
  const d = run.digests.find((x) => x.label === "Trainable state");
  if (!d) return "—";
  return d.match ? `identical · ${shortHash(d.control, 8, 6)}` : `${shortHash(d.control, 6, 4)} ≠ ${shortHash(d.recovery, 6, 4)}`;
}
