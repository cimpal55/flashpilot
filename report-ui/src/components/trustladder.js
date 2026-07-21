/* The trust ladder.
 *
 * Five distinct claims that are routinely conflated into one word ("verified").
 * Each rung states who established it and, crucially, what was NOT checked.
 *
 * The hard rule: a rung may only report a positive result for work that
 * actually happened in this page or was actually recorded by the core. This
 * page verifies content integrity. It does not verify signatures and it does
 * not verify publisher identity — so those rungs say so plainly rather than
 * borrowing credibility from the rungs above them. */

import { h } from "../lib/dom.js";
import { stateClass } from "./kit.js";
import { STATUS, BINDING } from "../lib/hash.js";

const RUNGS = [
  {
    id: "gate",
    label: "Recovery Gate",
    question: "Did the checkpoint actually resume the same run?",
    by: "computed by the FlashPilot CLI — copied here, never recomputed",
  },
  {
    id: "inventory",
    label: "Evidence inventory",
    question: "Do the bytes match the hashes the manifest records?",
    by: "recomputed in your browser with Web Crypto",
  },
  {
    id: "binding",
    label: "Manifest binding",
    question: "Is this the manifest the attestation was issued over?",
    by: "manifest bytes hashed here, compared to evidence_manifest_sha256",
  },
  {
    id: "signature",
    label: "Attestation signature",
    question: "Is the attestation cryptographically signed?",
    by: "read from the attestation — this page performs no signature check",
  },
  {
    id: "provenance",
    label: "Publisher provenance",
    question: "Who issued it, and can that be proven?",
    by: "not established — integrity is not publisher authentication",
  },
];

/**
 * @param run            the view model
 * @param inventory      result of verifyManifest, or null before the first pass
 * @param binding        result of verifyManifestBinding, or null
 */
export function trustLadder(run, inventory, binding) {
  const rows = RUNGS.map((rung) => {
    const { state, value, note } = assess(rung.id, run, inventory, binding);
    return h(
      "div",
      { class: `ladder-rung ${stateClass(state)}` },
      h("span", { class: "rung-tick", "aria-hidden": "true" }),
      h(
        "div",
        { class: "rung-body" },
        h(
          "div",
          { class: "rung-head" },
          h("span", { class: "rung-label", text: rung.label }),
          h("span", { class: "rung-value", text: value }),
        ),
        h("p", { class: "rung-question", text: rung.question }),
        h("p", { class: "rung-by", text: note ?? rung.by }),
      ),
    );
  });

  return h(
    "div",
    { class: "trust-ladder" },
    h(
      "p",
      { class: "lede", style: "margin-bottom:var(--s-4)" },
      "“Verified” is five separate claims. They are not interchangeable, so they are ",
      "reported separately — including the two this page does not check.",
    ),
    ...rows,
  );
}

function assess(id, run, inventory, binding) {
  if (id === "gate") {
    if (run.state === "pass") {
      return { state: "pass", value: run.verdict, note: "computed by the FlashPilot CLI — copied here, never recomputed" };
    }
    if (run.state === "fail") {
      return { state: "fail", value: run.verdict, note: "computed by the FlashPilot CLI — copied here, never recomputed" };
    }
    return { state: "unknown", value: run.verdict, note: "the core did not reach a verdict; this page will not invent one" };
  }

  if (id === "inventory") {
    if (!inventory) return { state: "void", value: "checking…", note: "hashing raw evidence bytes" };
    if (inventory.overall === STATUS.INTACT) {
      const n = inventory.rows.length;
      return { state: "pass", value: "INTACT", note: `${n} files recomputed here and matched, with no unlisted extras` };
    }
    return {
      state: inventory.overall === STATUS.VOID ? "void" : "fail",
      value: inventory.overall,
      note: inventory.reason ?? "at least one file did not match the closed inventory",
    };
  }

  if (id === "binding") {
    if (!binding) return { state: "void", value: "checking…", note: "hashing the manifest's own bytes" };
    if (binding.status === BINDING.BOUND) {
      return { state: "pass", value: "BOUND", note: "the manifest hashes to the digest recorded in the attestation" };
    }
    if (binding.status === BINDING.UNBOUND) {
      return { state: "fail", value: "UNBOUND", note: "the manifest does NOT hash to the attestation's digest — substitution detected" };
    }
    return { state: "void", value: "NOT AVAILABLE", note: binding.reason ?? "no attestation digest to bind against" };
  }

  if (id === "signature") {
    if (!run.attestation) {
      return { state: "void", value: "NOT PRESENT", note: "no attestation was issued for this run" };
    }
    // A detached Ed25519 signature is a separate artifact, so the attestation
    // payload legitimately still reads "unsigned": signing must not alter the
    // bytes that were verified. Presence of the artifact is what to report —
    // and only as recorded, because this page runs no signature check.
    if (run.signature) {
      return {
        state: "unknown",
        value: "RECORDED, NOT CHECKED",
        note: "a detached Ed25519 signature artifact is present; this page does not verify signatures, and no OIDC identity is checked here",
      };
    }
    return {
      state: "unknown",
      value: "UNSIGNED",
      note: "no detached signature artifact accompanies this attestation; this page performs no signature check either way",
    };
  }

  // provenance
  return {
    state: "unknown",
    value: "NOT ESTABLISHED",
    note: "content integrity does not identify a publisher; no OIDC or identity claim is checked here",
  };
}
