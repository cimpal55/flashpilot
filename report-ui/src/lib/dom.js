/* Minimal DOM helper. No framework, no build step: the UI ships as the exact
 * files in this directory, which keeps "static assets only" literally true. */

export function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props ?? {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") el.className = value;
    else if (key === "text") el.textContent = value;
    else if (key === "dataset") Object.assign(el.dataset, value);
    else if (key.startsWith("on") && typeof value === "function") {
      el.addEventListener(key.slice(2).toLowerCase(), value);
    } else el.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

/** Truncate a hex digest for display without ever hiding a mismatch. */
export function shortHash(hex, head = 10, tail = 6) {
  if (typeof hex !== "string" || hex.length <= head + tail + 1) return hex ?? "—";
  return `${hex.slice(0, head)}…${hex.slice(-tail)}`;
}

export function formatBytes(n) {
  if (typeof n !== "number" || !Number.isFinite(n)) return "—";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB`;
}

/** Count-up on a numeric readout — one of the three permitted motions. */
export function countUp(el, value, { decimals = 0, suffix = "" } = {}) {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const final = `${value.toFixed(decimals)}${suffix}`;
  if (reduced || !Number.isFinite(value)) {
    el.textContent = final;
    return;
  }
  const duration = 520;
  const start = performance.now();
  const tick = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = `${(value * eased).toFixed(decimals)}${suffix}`;
    if (t < 1) requestAnimationFrame(tick);
    else el.textContent = final;
  };
  requestAnimationFrame(tick);
}
