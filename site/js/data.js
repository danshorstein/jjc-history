// Data layer: fetch + cache the JSON bundle and page text.
const cache = new Map();

async function getJSON(path) {
  if (cache.has(path)) return cache.get(path);
  const p = fetch(path, { cache: "no-cache" }).then(r => {
    if (!r.ok) throw new Error(`${r.status} ${path}`);
    return r.json();
  });
  cache.set(path, p);
  return p;
}

export const loadVolumes = () => getJSON("data/volumes.json");
export const loadEvents = () => getJSON("data/events.json");
export const loadLeadership = () => getJSON("data/leadership.json");
export const loadThreads = () => getJSON("data/threads.json");
export const loadStories = () => getJSON("data/stories.json");
export const loadMysteries = () => getJSON("data/mysteries.json");
export const loadOrgs = () => getJSON("data/orgs.json");
export const loadAds = () => getJSON("data/ads.json");
export const loadYear = vid => getJSON(`data/years/${vid}.json`);
export const loadNamesShard = letter => getJSON(`data/names/${letter}.json`);
export const loadNamesMeta = () => getJSON("data/names_meta.json");
export const loadSearchShard = c => getJSON(`data/search/${c}.json`);
export const loadSearchMeta = () => getJSON("data/search_meta.json");

let volsByVid = null;
export async function volumeIndex() {
  if (!volsByVid) {
    const vols = await loadVolumes();
    volsByVid = new Map(vols.map(v => [v.vid, v]));
  }
  return volsByVid;
}

const BIB = "AA00010733";
const IMG_BASE = `https://ufdcimages.uflib.ufl.edu/AA/00/01/07/33`;

export function ufdcPageUrl(vid, seq) {
  return `https://ufdc.ufl.edu/${BIB}/${vid}/${seq}`;
}
export function thumbUrl(vol, seq) {
  const pid = vol.page_ids[String(seq)];
  return pid ? `${IMG_BASE}/${vol.vid}/${pid}thm.jpg` : null;
}
export function imageUrl(vol, seq) {
  const pid = vol.page_ids[String(seq)];
  return pid ? `${IMG_BASE}/${vol.vid}/${pid}.jpg` : null;
}

// Page text: local corpus first (served alongside the site when run from the
// project root), falling back to the UFDC text file itself.
export async function pageText(vid, seq) {
  const key = `pt:${vid}:${seq}`;
  if (cache.has(key)) return cache.get(key);
  const p = (async () => {
    const local = `../data/text/${vid}/${String(seq).padStart(5, "0")}.txt`;
    try {
      const r = await fetch(local);
      if (r.ok) return r.text();
    } catch (e) { /* fall through */ }
    const vols = await volumeIndex();
    const vol = vols.get(vid);
    const pid = vol && vol.page_ids[String(seq)];
    if (pid) {
      const r = await fetch(`${IMG_BASE}/${vid}/${pid}.txt`);
      if (r.ok) return r.text();
    }
    return "(page text unavailable)";
  })();
  cache.set(key, p);
  return p;
}

// base36 delta-decoding for search postings
export function decodePostings(str) {
  const out = [];
  let acc = 0;
  for (const part of str.split(",")) {
    acc += parseInt(part, 36);
    out.push(acc);
  }
  return out;
}
