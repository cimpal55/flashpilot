/* Hash router. Hash routing (not history routing) is what lets the same build
 * work unchanged from `python -m http.server` and from GitHub Pages without any
 * server-side rewrite rules or a per-route 404 fallback.
 *
 * It does NOT make the page work from file:// — ES modules are fetched under
 * CORS and a file:// origin is opaque, so any static server is required. */

const listeners = new Set();

export function parseRoute(hash = window.location.hash) {
  const clean = String(hash || "").replace(/^#\/?/, "");
  const [pathPart, queryPart] = clean.split("?");
  const segments = pathPart.split("/").filter(Boolean);
  const params = new URLSearchParams(queryPart ?? "");
  if (segments.length === 0) return { name: "gallery", params };
  if (segments[0] === "run" && segments[1]) {
    return {
      name: "run",
      runId: decodeURIComponent(segments[1]),
      tab: segments[2] ?? "report",
      params,
    };
  }
  if (segments[0] === "compare") return { name: "compare", params };
  if (segments[0] === "about") return { name: "about", params };
  return { name: "gallery", params };
}

export function onRoute(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function go(path) {
  if (window.location.hash === path) emit();
  else window.location.hash = path;
}

function emit() {
  const route = parseRoute();
  for (const fn of listeners) fn(route);
}

export function startRouter() {
  window.addEventListener("hashchange", emit);
  emit();
}

export function href(route) {
  return `#/${route}`;
}
