/* Independent re-verification primitives.
 *
 * Your browser hashes RAW EVIDENCE BYTES with its own Web Crypto and compares
 * the result to the manifest FlashPilot wrote. This deliberately does not
 * depend on any JSON canonicalisation, so it can be reasoned about without
 * knowing FlashPilot's serialisation rules.
 *
 * This module is environment-free on purpose: no window, no document. That is
 * what lets `node --test` exercise exactly the code the browser runs, rather
 * than a reimplementation of it.
 *
 * Everything here fails closed. There is no input for which an unverifiable
 * bundle returns a passing status. */

const HEX64 = /^[0-9a-f]{64}$/i;

/** Decode base64 to bytes. Throws on anything that is not valid base64. */
export function decodeBase64(b64) {
  const binary = atob(b64);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) out[i] = binary.charCodeAt(i);
  return out;
}

export function toHex(buffer) {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function sha256Hex(bytes) {
  if (!globalThis.crypto?.subtle) {
    throw new Error("Web Crypto unavailable — cannot re-verify, refusing to pass");
  }
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return toHex(digest);
}

/** Length-checked, case-insensitive digest comparison. */
export function digestsMatch(a, b) {
  return (
    typeof a === "string" &&
    typeof b === "string" &&
    a.length === b.length &&
    a.toLowerCase() === b.toLowerCase()
  );
}

/**
 * A manifest path is acceptable only if it is relative, free of traversal and
 * empty segments, and free of drive or UNC prefixes.
 */
export function isContainedPath(path) {
  if (typeof path !== "string" || path.length === 0) return false;
  if (path.startsWith("/") || path.startsWith("\\")) return false;
  if (/^[a-zA-Z]:/.test(path)) return false;
  const parts = path.split(/[\\/]/);
  return !parts.some((p) => p === ".." || p === "" || p === ".");
}

export const STATUS = Object.freeze({
  INTACT: "INTACT",
  TAMPERED: "TAMPERED",
  MISSING: "MISSING",
  EXTRA: "EXTRA",
  VOID: "VOID",
});

/** Severity order — the overall result is always the worst row present. */
const SEVERITY = [STATUS.INTACT, STATUS.EXTRA, STATUS.MISSING, STATUS.TAMPERED, STATUS.VOID];

function worst(statuses) {
  return statuses.reduce(
    (acc, s) => (SEVERITY.indexOf(s) > SEVERITY.indexOf(acc) ? s : acc),
    STATUS.INTACT,
  );
}

/**
 * Structural validation of the manifest itself, before a single byte is hashed.
 *
 * A manifest that is empty, malformed, self-contradictory (duplicate paths), or
 * carries an unusable digest or size is not "zero failures, therefore pass" —
 * it is unverifiable, and unverifiable is VOID.
 */
export function validateManifest(manifest) {
  const problems = [];
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    return { ok: false, problems: [{ kind: "malformed", detail: "manifest is not an object" }] };
  }
  const entries = manifest.entries;
  if (!Array.isArray(entries)) {
    return { ok: false, problems: [{ kind: "malformed", detail: "manifest has no entries array" }] };
  }
  if (entries.length === 0) {
    return {
      ok: false,
      problems: [{ kind: "empty", detail: "closed inventory is empty — nothing to verify" }],
    };
  }

  const seen = new Set();
  for (const entry of entries) {
    if (!entry || typeof entry !== "object") {
      problems.push({ kind: "malformed", detail: "entry is not an object" });
      continue;
    }
    const path = entry.path;
    if (typeof path !== "string" || path.length === 0) {
      problems.push({ kind: "malformed", detail: "entry has no path" });
      continue;
    }
    // A closed inventory that names the same file twice cannot be a closed
    // inventory: the second claim could silently shadow the first.
    if (seen.has(path)) problems.push({ kind: "duplicate", path, detail: "path listed more than once" });
    seen.add(path);

    if (!isContainedPath(path)) {
      problems.push({ kind: "traversal", path, detail: "path escapes the run root" });
    }
    if (!HEX64.test(String(entry.sha256 ?? ""))) {
      problems.push({ kind: "bad-digest", path, detail: "sha256 is not 64 hex characters" });
    }
    const size = entry.size_bytes;
    if (!Number.isInteger(size) || size < 0) {
      problems.push({ kind: "bad-size", path, detail: "size_bytes is missing or not a non-negative integer" });
    }
  }
  return { ok: problems.length === 0, problems };
}

/**
 * Re-verify one manifest entry against the supplied bytes.
 *
 * `mutate` is a Set of paths to corrupt in memory. A non-empty file gets one
 * bit of its first byte flipped; an empty file cannot be bit-flipped, so it
 * gains a byte instead and the size check catches it. Either way an advertised
 * mutation is always detectable, never silently inert.
 */
export async function verifyEntry(entry, bytesByPath, mutate = null) {
  const path = entry?.path;
  if (typeof path !== "string" || !isContainedPath(path)) {
    return { path: String(path), status: STATUS.VOID, reason: "path escapes the run root" };
  }
  if (!HEX64.test(String(entry.sha256 ?? ""))) {
    return { path, status: STATUS.VOID, reason: "manifest digest is not a valid SHA-256" };
  }
  if (!Number.isInteger(entry.size_bytes) || entry.size_bytes < 0) {
    return { path, status: STATUS.VOID, reason: "manifest size is missing or invalid" };
  }
  if (!Object.prototype.hasOwnProperty.call(bytesByPath, path)) {
    return { path, status: STATUS.MISSING, reason: "no bytes for a manifest entry" };
  }

  let bytes = bytesByPath[path];
  if (mutate?.has(path)) {
    if (bytes.length === 0) {
      bytes = new Uint8Array([0x01]);
    } else {
      bytes = bytes.slice();
      bytes[0] = bytes[0] ^ 0x01;
    }
  }

  let actual;
  try {
    actual = await sha256Hex(bytes);
  } catch (error) {
    return { path, status: STATUS.VOID, reason: error.message };
  }

  if (entry.size_bytes !== bytes.length) {
    return {
      path,
      status: STATUS.TAMPERED,
      expected: entry.sha256,
      actual,
      reason: `size ${bytes.length} does not match manifest ${entry.size_bytes}`,
    };
  }
  if (!digestsMatch(actual, entry.sha256)) {
    return { path, status: STATUS.TAMPERED, expected: entry.sha256, actual, reason: "digest mismatch" };
  }
  return { path, status: STATUS.INTACT, expected: entry.sha256, actual, size: bytes.length };
}

/**
 * Re-verify a whole manifest.
 *
 * INTACT requires: a structurally valid, non-empty manifest; every entry
 * intact; and no evidence byte present that the manifest does not list. That
 * last rule is what makes the inventory *closed* rather than merely complete.
 */
export async function verifyManifest(manifest, bytesByPath, mutate = null, onProgress = null) {
  const structure = validateManifest(manifest);
  if (!structure.ok) {
    return {
      overall: STATUS.VOID,
      rows: [],
      problems: structure.problems,
      reason: structure.problems[0].detail,
    };
  }

  const entries = manifest.entries;
  const rows = [];
  for (const entry of entries) {
    const row = await verifyEntry(entry, bytesByPath, mutate);
    rows.push(row);
    onProgress?.(rows.length, entries.length, row);
  }

  // Anything supplied but not listed is unaccounted-for evidence. Reject it:
  // a bundle that can carry unlisted bytes is not a closed inventory.
  const listed = new Set(entries.map((e) => e.path));
  for (const path of Object.keys(bytesByPath ?? {})) {
    if (!listed.has(path)) {
      rows.push({ path, status: STATUS.EXTRA, reason: "evidence present but not listed in the manifest" });
    }
  }

  return { overall: worst(rows.map((r) => r.status)), rows, problems: [] };
}

export const BINDING = Object.freeze({
  BOUND: "BOUND",
  UNBOUND: "UNBOUND",
  UNAVAILABLE: "UNAVAILABLE",
});

/**
 * Bind the inventory to the attestation.
 *
 * Re-verifying files against a manifest only proves the files match *that
 * manifest*. Hashing the manifest's own bytes and comparing to the
 * attestation's `evidence_manifest_sha256` is what proves the manifest is the
 * one the attestation was issued over — closing the substitution gap.
 */
export async function verifyManifestBinding(manifestBytes, attestation) {
  const expected = attestation?.evidence_manifest_sha256;
  if (!manifestBytes || !HEX64.test(String(expected ?? ""))) {
    return {
      status: BINDING.UNAVAILABLE,
      reason: "no attestation digest to bind the manifest to",
      expected: expected ?? null,
      computed: null,
    };
  }
  let computed;
  try {
    computed = await sha256Hex(manifestBytes);
  } catch (error) {
    return { status: BINDING.UNAVAILABLE, reason: error.message, expected, computed: null };
  }
  return {
    status: digestsMatch(computed, expected) ? BINDING.BOUND : BINDING.UNBOUND,
    expected,
    computed,
  };
}
