/* Primitive components. Every surface composes these — that identity is what
 * makes the gallery, the report, the verifier and the CI view read as one
 * instrument rather than four pages. */

import { h, countUp } from "../lib/dom.js";

const STATE_CLASS = {
  pass: "state-pass",
  fail: "state-fail",
  unknown: "state-unknown",
  void: "state-void",
};

export function stateClass(state) {
  return STATE_CLASS[state] ?? STATE_CLASS.unknown;
}

export function panel(title, { actions = null, raised = false, extraClass = "" } = {}, ...body) {
  const head = title
    ? h(
        "div",
        { class: "panel-head" },
        h("h2", { text: title }),
        actions,
      )
    : null;
  return h(
    "section",
    { class: `panel ${raised ? "panel-raised" : ""} ${extraClass}` },
    head,
    ...body,
  );
}

export function pill(label, state = "neutral") {
  if (state === "neutral") return h("span", { class: "pill pill-neutral", text: label });
  if (state === "data") return h("span", { class: "pill pill-data", text: label });
  return h("span", { class: `pill ${stateClass(state)}`, text: label });
}

/**
 * The shared taxonomy. Each pill means one thing everywhere it appears, so a
 * judge learns the vocabulary once on the gallery and reuses it on every surface.
 */
export const TAXONOMY = {
  REQUIRED: ["REQUIRED", "unknown"],
  EPHEMERAL: ["EPHEMERAL", "neutral"],
  EXACT: ["EXACT", "data"],
  RESOLVED: ["RESOLVED", "pass"],
  "NO SOURCE": ["NO SOURCE", "fail"],
  UNKNOWN: ["UNKNOWN", "unknown"],
};

export function taxonomyPill(name) {
  const entry = TAXONOMY[name];
  return entry ? pill(entry[0], entry[1]) : pill(name, "neutral");
}

export function verdictStamp(verdict, state, scope) {
  return h(
    "div",
    { class: `verdict-stamp ${stateClass(state)}`, role: "status" },
    h("span", { class: "verdict-word", text: String(verdict).toUpperCase() }),
    scope ? h("span", { class: "verdict-scope", text: scope }) : null,
  );
}

export function verdictChip(run) {
  if (!run) {
    return h(
      "span",
      { class: "verdict-chip state-void" },
      h("span", { class: "dot" }),
      h("span", { class: "chip-label", text: "no run selected" }),
    );
  }
  return h(
    "a",
    { class: `verdict-chip ${stateClass(run.state)}`, href: `#/run/${run.id}` },
    h("span", { class: "dot" }),
    h("strong", { text: run.verdict }),
    h("span", { class: "chip-label", text: run.id }),
  );
}

export function metric(label, value, { note = null, state = null, animate = null } = {}) {
  const valueEl = h("div", { class: "metric-value", text: animate ? "0" : value });
  if (state) valueEl.style.setProperty("--metric-color", `var(--state)`);
  const node = h(
    "div",
    { class: `metric ${state ? stateClass(state) : ""}` },
    h("div", { class: "metric-label", text: label }),
    valueEl,
    note ? h("div", { class: "metric-note", text: note }) : null,
  );
  if (animate) {
    // Metric count-up — the second of the three permitted motions.
    requestAnimationFrame(() => countUp(valueEl, animate.value, animate));
  }
  return node;
}

export function metricGrid(...metrics) {
  return h("div", { class: "metric-grid" }, ...metrics);
}

export function banner(state, ...content) {
  return h("div", { class: `banner ${stateClass(state)}` }, ...content);
}

export function btn(label, { href = null, onClick = null, pressed = null, primary = false } = {}) {
  const props = {
    class: `btn ${primary ? "btn-primary" : ""}`,
  };
  if (pressed !== null) props["aria-pressed"] = String(pressed);
  if (href) return h("a", { ...props, href }, label);
  return h("button", { ...props, type: "button", onClick }, label);
}

export function emptyState(message) {
  return h("p", { class: "lede", text: message });
}
