/* Independent re-verification primitives.
 *
 * The UI hashes RAW EVIDENCE BYTES with the browser's own Web Crypto
 * implementation and compares the result to the manifest the core wrote. It
 * deliberately does not depend on any JSON canonicalisation, so a judge can
 * reason about it without knowing FlashPilot's serialisation rules. */

/** Decode base64 to bytes. Rejects anything that is not valid base64. */
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
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return toHex(digest);
}

/** Constant-shape comparison; any non-string or length mismatch is a failure. */
export function digestsMatch(a, b) {
  return (
    typeof a === "string" &&
    typeof b === "string" &&
    a.length === b.length &&
    a.toLowerCase() === b.toLowerCase()
  );
}

/**
 * A manifest path is only acceptable if it is relative, free of traversal
 * segments, and free of drive/UNC prefixes. Anything else renders VOID.
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
  VOID: "VOID",
});

/**
 * Re-verify one manifest entry against the embedded bytes.
 * Fails closed: unknown, missing, path-escaping or mismatched -> never INTACT.
 *
 * `mutate` is a Set of paths to corrupt in memory. A non-empty file gets one
 * bit of its first byte flipped; an empty file cannot be bit-flipped, so it
 * gains a single byte instead — the size check must then catch it. Either way
 * a requested mutation is guaranteed to be detectable, never silently inert.
 */
export async function verifyEntry(entry, bytesByPath, mutate = null) {
  const path = entry?.path;
  if (!isContainedPath(path)) {
    return { path: String(path), status: STATUS.VOID, reason: "path escapes the run root" };
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
      bytes[0] = bytes[0] ^ 0x01; // flip exactly one bit of one byte
    }
  }
  let actual;
  try {
    actual = await sha256Hex(bytes);
  } catch (error) {
    return { path, status: STATUS.VOID, reason: error.message };
  }
  const expected = entry.sha256;
  const sizeOk = typeof entry.size_bytes !== "number" || entry.size_bytes === bytes.length;
  if (!digestsMatch(actual, expected) || !sizeOk) {
    return { path, status: STATUS.TAMPERED, expected, actual, size: bytes.length };
  }
  return { path, status: STATUS.INTACT, expected, actual, size: bytes.length };
}

/**
 * Re-verify a whole manifest. The overall result is INTACT only when every
 * single entry is INTACT and the manifest declared at least one entry.
 */
export async function verifyManifest(manifest, bytesByPath, mutate = null, onProgress) {
  const entries = Array.isArray(manifest?.entries) ? manifest.entries : null;
  if (!entries || entries.length === 0) {
    return { overall: STATUS.VOID, reason: "no closed inventory to check", rows: [] };
  }
  const rows = [];
  for (const entry of entries) {
    const row = await verifyEntry(entry, bytesByPath, mutate);
    rows.push(row);
    onProgress?.(rows.length, entries.length, row);
  }
  const worst = rows.some((r) => r.status === STATUS.VOID)
    ? STATUS.VOID
    : rows.some((r) => r.status === STATUS.MISSING)
      ? STATUS.MISSING
      : rows.some((r) => r.status === STATUS.TAMPERED)
        ? STATUS.TAMPERED
        : STATUS.INTACT;
  return { overall: worst, rows };
}
