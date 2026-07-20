// Shared UI components: citation chips, research chips, the page modal.
import { volumeIndex, ufdcPageUrl, imageUrl, thumbUrl, pageText } from "./data.js";

export const el = (tag, attrs = {}, ...children) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) n.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined) continue;
    n.append(c.nodeType ? c : document.createTextNode(c));
  }
  return n;
};

export function esc(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

// ---- citation chip: "1958-59 · p.27" -> page modal
export async function citeChip(cit, highlight) {
  const vols = await volumeIndex();
  const vol = vols.get(cit.vid);
  const year = vol ? vol.year : cit.vid;
  const chip = el("button", {
    class: "chip chip-cite",
    title: `Open yearbook page (scan ${cit.seq})`,
    onclick: () => openPageModal(cit.vid, cit.seq, highlight),
  }, `${year} · p.${cit.seq}`);
  if (cit.unverified) chip.title += " — citation could not be auto-verified";
  return chip;
}

export function researchChip(src) {
  const label = src.title.split("—")[0].trim();
  if (!src.url) {
    return el("span", { class: "chip chip-research", title: src.note || src.title }, label);
  }
  return el("a", {
    class: "chip chip-research", href: src.url, target: "_blank",
    rel: "noopener", title: src.title,
  }, label);
}

export async function chipsFor(citations = [], research = [], highlight) {
  const wrap = el("div", { class: "chips" });
  for (const c of citations) wrap.append(await citeChip(c, highlight));
  for (const r of research) wrap.append(researchChip(r));
  return wrap;
}

// ---- page modal
const backdrop = document.getElementById("modal-backdrop");
const modalBody = document.getElementById("modal-body");
document.getElementById("modal-close").addEventListener("click", closeModal);
backdrop.addEventListener("click", e => { if (e.target === backdrop) closeModal(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

export function closeModal() {
  backdrop.hidden = true;
  modalBody.innerHTML = "";
  document.body.style.overflow = "";
}

export async function openPageModal(vid, seq, highlight) {
  const vols = await volumeIndex();
  const vol = vols.get(vid);
  if (!vol) return;
  backdrop.hidden = false;
  document.body.style.overflow = "hidden";
  modalBody.innerHTML = "";
  const img = imageUrl(vol, seq);
  const view = el("div", { class: "page-view" });
  if (img) {
    view.append(el("a", { href: ufdcPageUrl(vid, seq), target: "_blank", rel: "noopener", title: "Open the scan at UF Digital Collections" },
      el("img", { src: img, alt: `Scanned page ${seq} of the ${vol.year} yearbook`, loading: "lazy" })));
  }
  const right = el("div", {},
    el("h3", {}, `${vol.year} Yearbook`),
    el("div", { class: "src" },
      `Scan page ${seq} of ${vol.pages} · `,
      el("a", { href: ufdcPageUrl(vid, seq), target: "_blank", rel: "noopener" }, "View original at UF Digital Collections ⇗")),
    el("div", { class: "page-text", id: "modal-page-text" }, "Loading page text…"));
  view.append(right);
  modalBody.append(view);

  const raw = await pageText(vid, seq);
  const box = document.getElementById("modal-page-text");
  if (!box) return;
  if (highlight) {
    const rx = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    box.innerHTML = esc(raw).replace(rx, "<mark>$1</mark>");
    const m = box.querySelector("mark");
    if (m) m.scrollIntoView({ block: "center" });
  } else {
    box.textContent = raw;
  }
}

// ---- thumbnails strip
export function thumbFigure(vol, seq, caption) {
  const t = thumbUrl(vol, seq);
  if (!t) return null;
  return el("figure", { onclick: () => openPageModal(vol.vid, seq) },
    el("img", { src: t, alt: caption || `Page ${seq}`, loading: "lazy" }),
    el("figcaption", {}, caption || `p.${seq}`));
}

// ---- decade presence bar (1920s..2010s)
export function presenceBar(yearsOn) {
  const decades = [];
  for (let d = 1920; d <= 2010; d += 10) decades.push(d);
  const on = new Set(yearsOn.map(y => Math.floor(y / 10) * 10));
  const bar = el("div", { class: "presence-bar", role: "img",
    "aria-label": `Appears in decades: ${[...on].sort().join(", ")}` });
  for (const d of decades) bar.append(el("span", { class: on.has(d) ? "on" : "" }));
  const scale = el("div", { class: "presence-scale" }, el("span", {}, "1920s"), el("span", {}, "2010s"));
  return el("div", {}, bar, scale);
}

export const badgeFor = kind => {
  const map = {
    yearbook: ["badge badge-yearbook", "From the yearbooks"],
    research: ["badge badge-research", "Outside research"],
    both: ["badge badge-both", "Yearbooks + research"],
  };
  const [cls, label] = map[kind] || map.yearbook;
  return el("span", { class: cls }, label);
};
