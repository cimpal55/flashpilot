/* Zero-dependency tests for the verifier core: `node --test`.
 *
 * These import the exact module the browser runs — not a reimplementation —
 * so a regression in fail-closed behaviour breaks the build rather than
 * quietly shipping a verifier that passes bad evidence.
 *
 * Run: node --test report-ui/tests/hash.test.mjs
 */

import test from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";

import {
  STATUS,
  BINDING,
  validateManifest,
  verifyManifest,
  verifyManifestBinding,
  isContainedPath,
  digestsMatch,
  sha256Hex,
} from "../src/lib/hash.js";

const enc = new TextEncoder();

function bytes(text) {
  return enc.encode(text);
}

function sha(input) {
  return createHash("sha256").update(input).digest("hex");
}

/** A well-formed, internally consistent bundle: the control case. */
function goodBundle() {
  const files = {
    "result.json": bytes('{"verdict":"VERIFIED"}'),
    "logs/empty.log": bytes(""),
    "nested/model.bin": bytes("weights"),
  };
  const manifest = {
    schema_version: "evidence-manifest-v1",
    entries: Object.entries(files).map(([path, b]) => ({
      path,
      sha256: sha(b),
      size_bytes: b.length,
    })),
  };
  return { files, manifest };
}

test("intact bundle verifies", async () => {
  const { files, manifest } = goodBundle();
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.INTACT);
  assert.equal(result.rows.length, 3);
  assert.ok(result.rows.every((r) => r.status === STATUS.INTACT));
});

test("one-bit tamper is detected", async () => {
  const { files, manifest } = goodBundle();
  const result = await verifyManifest(manifest, files, new Set(["nested/model.bin"]));
  assert.equal(result.overall, STATUS.TAMPERED);
  const row = result.rows.find((r) => r.path === "nested/model.bin");
  assert.equal(row.status, STATUS.TAMPERED);
  assert.notEqual(row.actual, row.expected);
  // Only the targeted file is affected.
  assert.equal(result.rows.filter((r) => r.status === STATUS.TAMPERED).length, 1);
});

test("tampering an empty file is never silently inert", async () => {
  // A bit-flip on zero bytes is a no-op, so the empty file must be corrupted
  // some other way. This guards a real bug: it previously passed as INTACT.
  const { files, manifest } = goodBundle();
  const result = await verifyManifest(manifest, files, new Set(["logs/empty.log"]));
  assert.equal(result.overall, STATUS.TAMPERED);
  assert.equal(result.rows.find((r) => r.path === "logs/empty.log").status, STATUS.TAMPERED);
});

test("missing evidence fails closed", async () => {
  const { files, manifest } = goodBundle();
  delete files["nested/model.bin"];
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.MISSING);
  assert.equal(result.rows.find((r) => r.path === "nested/model.bin").status, STATUS.MISSING);
});

test("path traversal is void, never pass", async () => {
  const { files, manifest } = goodBundle();
  manifest.entries.push({ path: "../escape.json", sha256: "0".repeat(64), size_bytes: 0 });
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.VOID);
});

test("isContainedPath rejects every escape shape", () => {
  for (const bad of [
    "../x",
    "a/../../x",
    "/abs",
    "\\abs",
    "C:/win",
    "c:\\win",
    "a//b",
    "./a",
    "",
    null,
    undefined,
    42,
  ]) {
    assert.equal(isContainedPath(bad), false, `should reject: ${String(bad)}`);
  }
  for (const ok of ["a", "a/b", "a/b/c.json", "nested/model.bin"]) {
    assert.equal(isContainedPath(ok), true, `should accept: ${ok}`);
  }
});

test("duplicate manifest paths are rejected", async () => {
  const { files, manifest } = goodBundle();
  manifest.entries.push({ ...manifest.entries[0] });
  const structure = validateManifest(manifest);
  assert.equal(structure.ok, false);
  assert.ok(structure.problems.some((p) => p.kind === "duplicate"));

  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.VOID);
});

test("unlisted extra evidence is rejected", async () => {
  const { files, manifest } = goodBundle();
  files["stowaway.bin"] = bytes("not in the manifest");
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.EXTRA);
  const row = result.rows.find((r) => r.path === "stowaway.bin");
  assert.equal(row.status, STATUS.EXTRA);
});

test("invalid SHA-256 in the manifest is rejected", async () => {
  const { files, manifest } = goodBundle();
  manifest.entries[0].sha256 = "nope";
  assert.equal(validateManifest(manifest).ok, false);
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.VOID);
});

test("missing or invalid size is rejected", async () => {
  for (const badSize of [undefined, null, -1, 1.5, "12"]) {
    const { files, manifest } = goodBundle();
    manifest.entries[0].size_bytes = badSize;
    assert.equal(validateManifest(manifest).ok, false, `size ${String(badSize)} should be invalid`);
    const result = await verifyManifest(manifest, files);
    assert.equal(result.overall, STATUS.VOID);
  }
});

test("a size that disagrees with the bytes is tampered", async () => {
  const { files, manifest } = goodBundle();
  manifest.entries[0].size_bytes += 1;
  const result = await verifyManifest(manifest, files);
  assert.equal(result.overall, STATUS.TAMPERED);
});

test("empty manifest is void, not a vacuous pass", async () => {
  const result = await verifyManifest({ entries: [] }, {});
  assert.equal(result.overall, STATUS.VOID);
  assert.ok(result.reason.includes("empty"));
});

test("malformed manifests are void", async () => {
  for (const bad of [null, undefined, 42, "manifest", [], {}, { entries: "no" }]) {
    const result = await verifyManifest(bad, {});
    assert.equal(result.overall, STATUS.VOID, `should be void: ${JSON.stringify(bad)}`);
  }
});

test("manifest binding matches when the manifest is the attested one", async () => {
  const raw = bytes('{"entries":[]}');
  const binding = await verifyManifestBinding(raw, { evidence_manifest_sha256: sha(raw) });
  assert.equal(binding.status, BINDING.BOUND);
  assert.equal(binding.computed, binding.expected);
});

test("manifest binding mismatch is detected", async () => {
  const raw = bytes('{"entries":[]}');
  const other = bytes('{"entries":[{"substituted":true}]}');
  const binding = await verifyManifestBinding(raw, { evidence_manifest_sha256: sha(other) });
  assert.equal(binding.status, BINDING.UNBOUND);
  assert.notEqual(binding.computed, binding.expected);
});

test("manifest binding is unavailable rather than passing when there is no digest", async () => {
  for (const att of [null, undefined, {}, { evidence_manifest_sha256: "bad" }]) {
    const binding = await verifyManifestBinding(bytes("x"), att);
    assert.equal(binding.status, BINDING.UNAVAILABLE);
  }
  const noBytes = await verifyManifestBinding(null, { evidence_manifest_sha256: sha(bytes("x")) });
  assert.equal(noBytes.status, BINDING.UNAVAILABLE);
});

test("digestsMatch is strict about type and length", () => {
  const a = sha(bytes("x"));
  assert.equal(digestsMatch(a, a), true);
  assert.equal(digestsMatch(a, a.toUpperCase()), true);
  assert.equal(digestsMatch(a, a.slice(0, 63)), false);
  assert.equal(digestsMatch(a, null), false);
  assert.equal(digestsMatch(null, null), false);
  assert.equal(digestsMatch(a, undefined), false);
});

test("sha256Hex agrees with node crypto", async () => {
  const b = bytes("frameworks save checkpoints");
  assert.equal(await sha256Hex(b), sha(b));
});

test("multiple simultaneous failures report the worst status", async () => {
  const { files, manifest } = goodBundle();
  delete files["nested/model.bin"]; // MISSING
  files["stowaway.bin"] = bytes("x"); // EXTRA
  const result = await verifyManifest(manifest, files, new Set(["result.json"])); // TAMPERED
  // TAMPERED outranks MISSING and EXTRA.
  assert.equal(result.overall, STATUS.TAMPERED);
});
