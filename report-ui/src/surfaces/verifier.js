/* Independent verifier — the signature surface.
 *
 * Your browser hashes the raw evidence bytes with Web Crypto and compares the
 * result to the manifest FlashPilot wrote. Nothing here trusts the attestation;
 * the attestation is the thing being checked. The adversarial probes below
 * mutate only the in-memory copy, and every one of them must fail closed. */

import { h, shortHash } from "../lib/dom.js";
import { panel, btn, verdictStamp, metric, metricGrid, banner, stateClass } from "../components/kit.js";
import { evidenceTable } from "../components/blocks.js";
import { BINDING, STATUS, verifyManifest, verifyManifestBinding } from "../lib/hash.js";
import { trustLadder } from "../components/trustladder.js";

const OVERALL_STATE = {
  [STATUS.INTACT]: "pass",
  [STATUS.TAMPERED]: "fail",
  [STATUS.MISSING]: "unknown",
  [STATUS.EXTRA]: "fail",
  [STATUS.VOID]: "void",
};

const OVERALL_COPY = {
  [STATUS.INTACT]: "Every file in the closed inventory hashes to exactly what the manifest claims.",
  [STATUS.TAMPERED]: "At least one file does not match its recorded hash. The bundle is rejected.",
  [STATUS.MISSING]: "The manifest references evidence that is not present. Fail closed — not a pass.",
  [STATUS.EXTRA]:
    "Evidence is present that the manifest does not list. A closed inventory cannot carry unlisted bytes.",
  [STATUS.VOID]: "There is nothing verifiable here, so no claim is made. Void is never a pass.",
};

export function renderVerifier(run) {
  const probes = { traversal: false, drop: false, duplicate: false, extra: false, badSha: false };
  // Paths whose in-memory copy gets a one-byte corruption. Fed by the global
  // probe button and by clicking individual evidence rows.
  const tampered = new Set();
  const firstPath = run.manifest?.entries?.[0]?.path ?? null;

  const stampSlot = h("div", {});
  const metricsSlot = h("div", {});
  const ladderSlot = h("div", {}, trustLadder(run, null, null));
  const progress = h("p", { class: "eyebrow", text: "" });

  const tableSlot = h("div", {});
  let currentTable = null;
  let flipButton = null;

  const toggleRow = (path) => {
    if (tampered.has(path)) tampered.delete(path);
    else tampered.add(path);
    rerender();
  };

  const rerender = async () => {
    const manifest = effectiveManifest(run, probes);
    const evidence = effectiveEvidence(run, probes);
    currentTable = evidenceTable(manifest, { onToggleRow: toggleRow, tampered });
    tableSlot.replaceChildren(currentTable.node);
    if (flipButton && firstPath) {
      const on = tampered.has(firstPath);
      flipButton.setAttribute("aria-pressed", String(on));
      flipButton.className = `btn ${on ? stateClass("fail") : ""}`;
    }
    await runVerification(run, manifest, evidence, tampered, currentTable, {
      stampSlot,
      metricsSlot,
      ladderSlot,
      progress,
    });
  };

  const probeButton = (label, key, description) => {
    const button = btn(label, { pressed: false });
    button.addEventListener("click", async () => {
      probes[key] = !probes[key];
      button.setAttribute("aria-pressed", String(probes[key]));
      button.className = `btn ${probes[key] ? stateClass("fail") : ""}`;
      await rerender();
    });
    button.title = description;
    return button;
  };

  flipButton = btn("Flip one bit", { pressed: false });
  flipButton.title = "Flip a single bit of the first evidence file, in memory only.";
  flipButton.addEventListener("click", () => {
    if (firstPath) toggleRow(firstPath);
  });

  const controls = h("div", { class: "row" });
  controls.append(
    flipButton,
    probeButton("Inject ../ path", "traversal", "Add a manifest entry that escapes the run root."),
    probeButton("Drop a file", "drop", "Remove the bytes for one manifest entry."),
    probeButton("Duplicate a path", "duplicate", "List the same path twice in the manifest."),
    probeButton("Add unlisted evidence", "extra", "Supply a file the manifest does not list."),
    probeButton("Corrupt a digest", "badSha", "Replace a manifest sha256 with an invalid value."),
    btn("Re-run verification", {
      primary: true,
      onClick: () => rerender(),
    }),
  );

  const view = h(
    "div",
    { class: "stack" },
    h(
      "header",
      { class: "stack-tight" },
      h("p", { class: "eyebrow", text: "independent re-verification · web crypto" }),
      h("h1", { text: "Check the proof yourself" }),
      h(
        "p",
        { class: "lede" },
        "This page does not ask you to trust FlashPilot. It recomputes SHA-256 over the raw bytes of ",
        "every file in the closed inventory, using your browser's own crypto, and compares each digest ",
        "to the manifest. Then it lets you break the bundle and watch it fail closed.",
      ),
    ),
    stampSlot,
    metricsSlot,
    panel("What was actually established", {}, ladderSlot),
    panel(
      "Adversarial probes",
      { actions: progress },
      h(
        "p",
        { class: "lede", style: "margin-bottom:var(--s-4)" },
        "Each probe mutates the in-memory copy only — the files in ",
        h("span", { class: "mono", text: `samples/${run.id}/` }),
        " are never touched. You can also click any row in the evidence table to corrupt that ",
        "specific file. A correct verifier must refuse every one of these.",
      ),
      controls,
    ),
    panel(`Evidence (${run.manifest?.entries?.length ?? 0} files)`, {}, tableSlot),
  );

  // Kick off the first pass once the surface is in the document.
  queueMicrotask(rerender);

  return view;
}

/** Build the manifest the verifier will actually check, including any probes. */
function effectiveManifest(run, probes) {
  const base = run.manifest;
  if (!base || !Array.isArray(base.entries)) return base ?? null;
  let entries = base.entries.slice();
  if (probes.drop && entries.length > 0) {
    // Keep the claim, remove the bytes: a dangling reference must never pass.
    entries = entries.map((e, i) => (i === entries.length - 1 ? { ...e, path: `${e.path}.absent` } : e));
  }
  if (probes.traversal) {
    entries = [
      ...entries,
      { path: "../outside-the-run.json", sha256: "0".repeat(64), size_bytes: 0 },
    ];
  }
  if (probes.duplicate && entries.length > 0) {
    // A closed inventory that names one file twice is self-contradictory.
    entries = [...entries, { ...entries[0] }];
  }
  if (probes.badSha && entries.length > 0) {
    entries = entries.map((e, i) => (i === 0 ? { ...e, sha256: "not-a-valid-sha256" } : e));
  }
  return { ...base, entries };
}

/** Evidence bytes as the verifier will see them, including the extras probe. */
function effectiveEvidence(run, probes) {
  if (!probes.extra) return run.evidence;
  return {
    ...run.evidence,
    "unlisted-extra-evidence.bin": new Uint8Array([0x66, 0x6c, 0x61, 0x73, 0x68]),
  };
}

async function runVerification(run, manifest, evidence, tampered, table, slots) {
  const { stampSlot, metricsSlot, ladderSlot, progress } = slots;

  if (!run.manifest) {
    stampSlot.replaceChildren(
      verdictStamp("VOID", "void", "no closed inventory to re-verify"),
      h(
        "p",
        { class: "lede", style: "margin-top:var(--s-3)" },
        "This run did not ship an evidence manifest, so there is nothing for the browser to check. ",
        "FlashPilot reports that as void rather than inventing a result.",
      ),
    );
    metricsSlot.replaceChildren();
    // An explicit unavailable binding, not null: leaving it null would render a
    // permanent "checking…" that never resolves.
    ladderSlot.replaceChildren(
      trustLadder(
        run,
        { overall: STATUS.VOID, rows: [], reason: "no closed inventory was shipped with this run" },
        {
          status: BINDING.UNAVAILABLE,
          reason: "there is no manifest to bind to an attestation",
          expected: null,
          computed: null,
        },
      ),
    );
    progress.textContent = "";
    return;
  }

  table.reset();
  progress.textContent = "hashing…";

  const mutate = tampered.size > 0 ? tampered : null;
  const started = performance.now();
  const result = await verifyManifest(manifest, evidence, mutate, (done, total, row) => {
    table.setStatus(row.path, row.status);
    progress.textContent = `hashing ${done}/${total}`;
  });
  // Bind the inventory to the attestation: matching files prove nothing if the
  // manifest itself could have been swapped.
  const binding = await verifyManifestBinding(run.manifestBytes, run.attestation);
  const elapsed = performance.now() - started;
  progress.textContent = `${manifest.entries?.length ?? 0} files · ${elapsed.toFixed(0)} ms`;

  const state = OVERALL_STATE[result.overall] ?? "void";
  const counts = tally(result.rows);

  // Tamper transition — the third and last of the permitted motions.
  stampSlot.replaceChildren(
    ...[
      verdictStamp(result.overall, state, `re-verified in your browser · ${manifest.entries?.length ?? 0} files`),
      h("p", { class: "lede", style: "margin-top:var(--s-3)", text: OVERALL_COPY[result.overall] }),
      result.problems?.length
        ? banner(
            "void",
            h(
              "div",
              {},
              h("strong", { text: "Manifest rejected before hashing · " }),
              h("span", { class: "mono", text: result.problems.map((p) => p.kind).join(", ") }),
              h("div", { text: result.problems[0].detail }),
            ),
          )
        : null,
      firstFailure(result.rows),
    ].filter(Boolean),
  );

  metricsSlot.replaceChildren(
    metricGrid(
      metric("Intact", String(counts.INTACT), { state: "pass" }),
      metric("Tampered", String(counts.TAMPERED), { state: counts.TAMPERED ? "fail" : "pass" }),
      metric("Missing", String(counts.MISSING), { state: counts.MISSING ? "unknown" : "pass" }),
      metric("Unlisted", String(counts.EXTRA), { state: counts.EXTRA ? "fail" : "pass" }),
      metric("Void", String(counts.VOID), { state: counts.VOID ? "void" : "pass" }),
    ),
  );

  ladderSlot.replaceChildren(trustLadder(run, result, binding));
}

function tally(rows) {
  const counts = { INTACT: 0, TAMPERED: 0, MISSING: 0, EXTRA: 0, VOID: 0 };
  for (const row of rows) counts[row.status] = (counts[row.status] ?? 0) + 1;
  return counts;
}

function firstFailure(rows) {
  const bad = rows.find((r) => r.status !== STATUS.INTACT);
  if (!bad) return null;
  const state = OVERALL_STATE[bad.status];
  return banner(
    state,
    h(
      "div",
      {},
      h("strong", { text: `${bad.status} · ` }),
      h("span", { class: "mono", text: bad.path }),
      bad.reason ? h("div", { class: "mono", text: bad.reason }) : null,
      bad.expected
        ? h("div", { class: "mono", text: `manifest ${shortHash(bad.expected, 12, 8)}` })
        : null,
      bad.actual
        ? h("div", { class: "mono", text: `computed ${shortHash(bad.actual, 12, 8)}` })
        : null,
    ),
  );
}
