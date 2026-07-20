// All views: Timeline (home), Time Machine, People & Threads, Stories,
// Then & Now, Mysteries, Search.
import {
  loadVolumes, loadEvents, loadThreads, loadStories, loadMysteries,
  loadOrgs, loadAds, loadYear, loadNamesShard, loadNamesMeta,
  loadSearchShard, loadSearchMeta, volumeIndex, ufdcPageUrl, decodePostings,
} from "./data.js";
import {
  el, citeChip, chipsFor, openPageModal, thumbFigure, presenceBar, badgeFor,
} from "./ui.js";

const DECADE_NOTES = {
  1850: "Before the Center", 1880: "Before the Center",
  1900: "Founding years — B'nai Israel",
  1920: "The Conservative turn & the Center",
  1930: "Depression years", 1940: "War & renewal", 1950: "Building & belonging",
  1960: "Growth on Third & Silver", 1970: "The move to Mandarin",
  1980: "New generations", 1990: "Renewal", 2000: "A second century",
  2010: "The Galinsky era", 2020: "Legacy",
};

/* ============================= HOME / TIMELINE ============================ */
export async function viewHome(main) {
  const [events, vols] = await Promise.all([loadEvents(), loadVolumes()]);
  const hero = el("section", { class: "hero" },
    el("div", { class: "heb" }, "לדור ודור"),
    el("h1", {}, "From Generation to Generation"),
    el("p", { class: "lede" },
      "Ninety-three years of Jacksonville Jewish Center yearbooks — the people, schools, clubs, celebrations, and neighborhood businesses of a community, kept as it kept itself: one year at a time."),
    el("div", { class: "hero-stats" },
      el("div", { class: "stat" }, el("b", {}, String(vols.length)), el("span", {}, "yearbooks")),
      el("div", { class: "stat" }, el("b", {}, "17,729"), el("span", {}, "scanned pages")),
      el("div", { class: "stat" }, el("b", {}, "1926–2019"), el("span", {}, "continuous run")),
      el("div", { class: "stat" }, el("b", {}, "1901"), el("span", {}, "congregation founded"))),
    el("p", {},
      el("a", { class: "btn btn-gold", href: "#/time-machine", style: "text-decoration:none" }, "Step into a year →"), " ",
      el("a", { class: "btn", href: "#/stories", style: "text-decoration:none" }, "Read the stories")));
  main.append(hero);

  const byDecade = new Map();
  for (const e of events) {
    const d = Math.floor(e.year / 10) * 10;
    if (!byDecade.has(d)) byDecade.set(d, []);
    byDecade.get(d).push(e);
  }
  for (const [decade, evs] of [...byDecade.entries()].sort((a, b) => a[0] - b[0])) {
    const block = el("section", { class: "decade-block" },
      el("div", { class: "decade-head" },
        el("h2", {}, `${decade}s`),
        el("span", { class: "decade-note" }, DECADE_NOTES[decade] || "")));
    for (const e of evs.sort((a, b) => a.year - b.year)) {
      const item = el("article", { class: "event" },
        el("div", { class: "yr" }, String(e.year)),
        el("div", {},
          badgeFor(e.kind),
          el("h3", {}, e.title),
          el("p", {}, e.body),
          await chipsFor(e.citations, e.research)));
      block.append(item);
    }
    main.append(block);
  }
}

/* ============================= TIME MACHINE ============================== */
export async function viewTimeMachine(main, vid) {
  const vols = await loadVolumes();
  if (!vid) vid = vols[Math.floor(Math.random() * vols.length)].vid;
  const idx = vols.findIndex(v => v.vid === vid);
  const vol = vols[idx] || vols[0];

  const ribbon = el("div", { class: "year-ribbon", role: "tablist", "aria-label": "Choose a year" });
  let lastDecade = null;
  for (const v of vols) {
    const d = v.decade;
    if (d !== lastDecade) {
      ribbon.append(el("span", { class: "decade-tick" }, `’${String(d).slice(2)}s`));
      lastDecade = d;
    }
    ribbon.append(el("button", {
      class: v.vid === vol.vid ? "active" : "",
      onclick: () => { location.hash = `#/time-machine/${v.vid}`; },
    }, v.year.replace(/(\d{4})-(\d{4})/, (m, a, b) => `${a}–${b.slice(2)}`)));
  }
  main.append(ribbon);
  const active = ribbon.querySelector("button.active");
  if (active) setTimeout(() => active.scrollIntoView({ inline: "center", block: "nearest" }), 0);

  const data = await loadYear(vol.vid);
  const head = el("div", { class: "tm-head" },
    el("h2", {}, vol.year),
    vol.hebrew_year ? el("span", { class: "heb-year" }, String(vol.hebrew_year)) : null,
    el("span", { class: "meta" }, `${vol.pages} pages · `,
      el("a", { href: vol.ufdc_url, target: "_blank", rel: "noopener" }, "read the whole book at UF ⇗")),
    el("div", { class: "tm-nav" },
      el("button", { class: "btn", onclick: () => { if (vols[idx - 1]) location.hash = `#/time-machine/${vols[idx - 1].vid}`; }, disabled: idx === 0 ? "" : null }, "← earlier"),
      el("button", { class: "btn", onclick: () => { if (vols[idx + 1]) location.hash = `#/time-machine/${vols[idx + 1].vid}`; }, disabled: idx === vols.length - 1 ? "" : null }, "later →")));
  main.append(head);

  if (vol.label_correction) {
    main.append(el("div", { class: "correction-note" },
      "⚠ Catalog note: ", vol.label_correction.note, " ",
      el("a", { href: "#/mysteries" }, "More in Mysteries & Corrections.")));
  }

  const grid = el("div", { class: "tm-grid" });
  const left = el("div", {});
  const right = el("div", {});
  grid.append(left, right);
  main.append(grid);

  // thumbnails: cover + a spread across the book
  const picks = new Set([1]);
  const secSeqs = (data.sections || []).map(s => s.seq_start).filter(Boolean);
  for (const s of secSeqs.slice(0, 6)) picks.add(s);
  for (const f of [0.25, 0.5, 0.75]) picks.add(Math.max(1, Math.round(vol.pages * f)));
  const thumbs = el("div", { class: "thumbs" });
  [...picks].sort((a, b) => a - b).slice(0, 10).forEach(seq => {
    const fig = thumbFigure(vol, seq, `p.${seq}`);
    if (fig) thumbs.append(fig);
  });
  left.append(el("div", { class: "panel" },
    el("h3", {}, "Turn the pages"),
    thumbs,
    el("p", { style: "font-size:12.5px;color:var(--ink-3);margin:10px 0 0" },
      "Click any page to read it; every page links to the original scan at the University of Florida.")));

  if (data.sections && data.sections.length) {
    const ul = el("ul", { class: "sec-list" });
    for (const s of data.sections) {
      const li = el("li", {});
      if (s.seq_start) {
        li.append(el("a", { href: "javascript:;", onclick: () => openPageModal(vol.vid, s.seq_start) }, s.title));
      } else li.append(s.title);
      li.append(" ", el("span", { class: "pg" }, `p.${s.printed_start}`));
      ul.append(li);
    }
    left.append(el("div", { class: "panel" }, el("h3", {}, "In this yearbook"), ul));
  }

  if (data.advertisers && data.advertisers.length) {
    const wrap = el("div", {});
    for (const a of data.advertisers.slice(0, 28)) {
      wrap.append(el("span", { class: "ad-item" },
        el("a", { href: "javascript:;", onclick: () => openPageModal(vol.vid, a.seq, a.name.split(",")[0]) }, a.name),
        a.vols >= 8 ? el("span", { class: "longevity" }, ` ★${a.vols} yrs of ads`) : null, " · "));
    }
    left.append(el("div", { class: "panel" },
      el("h3", {}, "Patronize our advertisers"),
      wrap,
      el("p", { style: "font-size:12.5px;color:var(--ink-3);margin:8px 0 0" },
        "★ marks businesses that advertised in eight or more yearbooks.")));
  }

  // right column: leadership, organizations
  const lead = el("div", { class: "panel" }, el("h3", {}, "Who led that year"));
  for (const p of data.presidents || []) {
    lead.append(el("div", { class: "leader-row" },
      el("span", {}, p.name), el("span", { class: "role" }, `President ${p.term}`)));
  }
  for (const c of data.clergy || []) {
    lead.append(el("div", { class: "leader-row" }, el("span", {}, c.name), el("span", { class: "role" }, c.role)));
  }
  lead.append(el("p", { style: "font-size:12px;color:var(--ink-3);margin:8px 0 0" },
    "Tenures from the verified leadership dataset — see ", el("a", { href: "#/people" }, "People & Threads"), "."));
  right.append(lead);

  if (data.organizations && data.organizations.length) {
    const wrap = el("div", { class: "chips" });
    for (const o of data.organizations) {
      wrap.append(el("button", {
        class: "chip",
        title: `${o.count} page(s) this year — click to open`,
        onclick: () => openPageModal(vol.vid, o.pages[0]),
      }, `${o.name} (${o.count})`));
    }
    right.append(el("div", { class: "panel" },
      el("h3", {}, "Life of the Center"),
      wrap,
      el("p", { style: "font-size:12px;color:var(--ink-3);margin:8px 0 0" },
        "Keyword appearances in this volume's OCR text — counts are page hits, not membership.")));
  }
}

/* ============================= PEOPLE & THREADS ========================== */
export async function viewPeople(main, query) {
  const threads = await loadThreads();
  main.append(el("h1", { class: "section-title" }, "People & Threads"),
    el("p", { class: "section-deck" },
      "Follow a name through ninety years of yearbooks. Name strings are shown exactly as printed; people who share a surname are a thread, not a family tree — relationships are only asserted where a page says so."));

  const input = el("input", {
    type: "search", placeholder: "Type a name or surname — try “Shorstein”, “Marton”, “Safer”…",
    value: query || "", "aria-label": "Search names",
  });
  const results = el("div", {});
  const doSearch = async () => {
    const q = input.value.trim();
    location.hash = q ? `#/people/${encodeURIComponent(q)}` : "#/people";
    results.innerHTML = "";
    if (q.length < 2) return;
    results.append(el("div", { class: "loading" }, "Searching the name index…"));
    try {
      const meta = await loadNamesMeta();
      const letter = q[0].toUpperCase();
      // if querying by surname, the shard is the surname initial; also try
      // the last word's initial for "First Last" queries
      const words = q.split(/\s+/);
      const letters = new Set([letter, words[words.length - 1][0].toUpperCase()]);
      const shards = await Promise.all([...letters].map(l => loadNamesShard(l).catch(() => ({}))));
      const ql = q.toLowerCase();
      const matches = [];
      for (const shard of shards) {
        for (const [key, entry] of Object.entries(shard)) {
          if (entry.d.toLowerCase().includes(ql) || entry.s.toLowerCase() === ql) {
            matches.push(entry);
          }
        }
      }
      results.innerHTML = "";
      if (!matches.length) {
        results.append(el("p", { class: "empty" },
          "No name strings matched. OCR spellings vary — try a shorter fragment or a different spelling."));
        return;
      }
      // group by surname
      const bySurname = new Map();
      for (const m of matches) {
        if (!bySurname.has(m.s)) bySurname.set(m.s, []);
        bySurname.get(m.s).push(m);
      }
      for (const [surname, entries] of [...bySurname.entries()].sort((a, b) => b[1].length - a[1].length).slice(0, 12)) {
        const group = el("div", { class: "name-group" },
          el("h3", {}, `${surname} `, el("small", { style: "color:var(--ink-3);font-weight:400" },
            `${entries.length} name string${entries.length > 1 ? "s" : ""} — same surname ≠ same family`)));
        const list = el("div", { class: "name-list" });
        for (const e of entries.sort((a, b) => b.a.length - a.a.length).slice(0, 40)) {
          list.append(el("button", { class: "name-pill", onclick: () => showNameDetail(e, meta, results) },
            e.d, " ", el("span", { class: "ct" }, `×${e.a.length}`)));
        }
        group.append(list);
        results.append(group);
      }
    } catch (err) {
      results.innerHTML = "";
      results.append(el("p", { class: "empty" }, `Search failed: ${err.message}`));
    }
  };
  input.addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
  main.append(el("div", { class: "search-row" }, input,
    el("button", { class: "btn btn-gold", onclick: doSearch }, "Search names")));
  main.append(results);
  if (query) doSearch();

  main.append(el("hr", { class: "rule" }),
    el("h2", { class: "section-title", style: "font-size:24px" }, "Curated threads"),
    el("p", { class: "section-deck" }, "Documented arcs across the collection — every claim cited to its page."));
  const cards = el("div", { class: "cards" });
  for (const t of threads) {
    const card = el("article", { class: "card" },
      el("h3", {}, t.title),
      el("p", {}, t.summary),
      await chipsFor(t.citations, [], t.query.split(" ")[0]),
      t.caution ? el("p", { style: "font-size:12.5px;color:var(--gold);margin-top:10px" }, "⚖ " + t.caution) : null,
      el("p", { style: "margin-top:10px" }, el("a", { href: `#/people/${encodeURIComponent(t.query)}`,
        onclick: () => setTimeout(() => window.scrollTo(0, 0), 0) }, `Follow “${t.query}” in the index →`)));
    cards.append(card);
  }
  main.append(cards);
}

async function showNameDetail(entry, meta, container) {
  const vols = await volumeIndex();
  const old = container.querySelector(".name-detail");
  if (old) old.remove();
  const yearsOn = entry.a.map(([vi]) => {
    const y = (meta[vi].year.match(/\d{4}/) || [null])[0];
    return y ? +y : null;
  }).filter(Boolean);
  const detail = el("div", { class: "panel name-detail" },
    el("h3", {}, `${entry.d} — every appearance`),
    presenceBar(yearsOn));
  const seen = new Set();
  for (const [vi, seq] of entry.a) {
    const m = meta[vi];
    const key = `${m.vid}:${seq}`;
    if (seen.has(key)) continue;
    seen.add(key);
    detail.append(el("div", { class: "appearance-row" },
      el("span", { class: "yr" }, m.year),
      el("span", {}, `scan page ${seq}`),
      el("span", {},
        el("button", { class: "chip chip-cite", onclick: () => openPageModal(m.vid, seq, entry.s) }, "read page"),
        " ",
        el("a", { class: "chip", href: ufdcPageUrl(m.vid, seq), target: "_blank", rel: "noopener" }, "scan ⇗"))));
  }
  detail.append(el("p", { style: "font-size:12.5px;color:var(--ink-3);margin-top:10px" },
    "Appearances are exact-string matches in the OCR text. The same person may appear under other spellings; different people may share a name."));
  container.prepend(detail);
  detail.scrollIntoView({ behavior: "smooth", block: "start" });
}

/* ============================= STORIES =================================== */
export async function viewStories(main, id) {
  const stories = await loadStories();
  if (id) {
    const s = stories.find(x => x.id === id);
    if (!s) { main.append(el("p", {}, "Story not found.")); return; }
    const page = el("article", { class: "story-page" },
      el("p", {}, el("a", { href: "#/stories" }, "← All stories")),
      el("h1", { class: "section-title" }, s.title),
      el("p", { class: "deck" }, s.deck));
    s.body.forEach((para, i) => {
      page.append(el("p", { class: "body-para" + (i === 0 ? " drop" : "") }, para));
    });
    const ev = el("div", { class: "evidence-box" }, el("h4", {}, "Evidence"));
    ev.append(await chipsFor(s.citations, s.research));
    ev.append(el("p", { style: "font-size:12.5px;color:var(--ink-3);margin:8px 0 0" },
      "Blue chips open the cited yearbook pages; gold dashed chips are outside research."));
    page.append(ev);
    main.append(page);
    return;
  }
  main.append(el("h1", { class: "section-title" }, "Stories from the Archive"),
    el("p", { class: "section-deck" },
      "Curated exhibits — patterns nobody would see reading one yearbook at a time. Every claim links to its page."));
  const cards = el("div", { class: "cards" });
  for (const s of stories) {
    cards.append(el("article", { class: "card card-click", onclick: () => { location.hash = `#/story/${s.id}`; } },
      el("h3", {}, s.title),
      el("p", {}, s.deck),
      el("p", { style: "color:var(--blue);font-size:14px" }, "Read the story →")));
  }
  main.append(cards);
}

/* ============================= THEN & NOW ================================ */
const SPAN_MIN = 1926, SPAN_MAX = 2019;
function spanBar(first, last, gold) {
  const track = el("div", { class: "span-track", role: "img",
    "aria-label": `${first} to ${last}` });
  const l = ((first - SPAN_MIN) / (SPAN_MAX - SPAN_MIN)) * 100;
  const r = ((last - SPAN_MIN) / (SPAN_MAX - SPAN_MIN)) * 100;
  track.append(el("i", { class: gold ? "gold" : "", style: `left:${l}%; width:${Math.max(r - l, 1)}%` }));
  return track;
}

export async function viewThenNow(main) {
  const [orgs, ads] = await Promise.all([loadOrgs(), loadAds()]);
  main.append(el("h1", { class: "section-title" }, "Then & Now"),
    el("p", { class: "section-deck" },
      "What lasted, what faded, what returned. Spans show the first to last yearbook in which each organization or advertiser appears — click a row to open its earliest page."));

  main.append(el("h2", { style: "font-size:22px;margin:26px 0 6px" }, "Organizations & programs"),
    el("div", { class: "spans-head" }, el("span", {}),
      el("div", { class: "span-axis" }, el("span", {}, "1926"), el("span", {}, "1950"), el("span", {}, "1975"), el("span", {}, "2000"), el("span", {}, "2019"))));
  const orgWrap = el("div", {});
  const orgRows = orgs
    .map(o => {
      const ys = o.appearances.map(a => a.year_start).filter(Boolean);
      return ys.length >= 2 ? { o, first: Math.min(...ys), last: Math.max(...ys), n: o.appearances.length } : null;
    })
    .filter(Boolean)
    .sort((a, b) => (b.last - b.first) - (a.last - a.first));
  for (const { o, first, last, n } of orgRows) {
    const firstApp = o.appearances[0];
    const row = el("div", { class: "span-row", style: "cursor:pointer",
      title: `${o.name}: ${first}–${last} (${n} yearbooks) — click to open its earliest page`,
      onclick: () => openPageModal(firstApp.vid, firstApp.pages[0]) },
      el("span", { class: "lbl" }, `${o.name} · ${n}`),
      spanBar(first, last, true));
    orgWrap.append(row);
  }
  main.append(orgWrap);
  main.append(el("p", { style: "font-size:12.5px;color:var(--ink-3)" },
    "Counts are yearbooks in which the name appears (OCR keyword matches — see the methodology note in Mysteries)."));

  main.append(el("hr", { class: "rule" }),
    el("h2", { style: "font-size:22px;margin:6px 0 6px" }, "The businesses that kept the lights on"),
    el("p", { class: "section-deck" },
      "Advertisers from the yearbooks' classified directories, ranked by how many yearbooks they appeared in."));
  const adWrap = el("div", {});
  for (const b of ads.filter(b => b.volumes >= 10).slice(0, 40)) {
    const firstApp = b.appearances[0];
    adWrap.append(el("div", { class: "span-row", style: "cursor:pointer",
      title: `${b.name}: ads ${b.first_year}–${b.last_year} (${b.volumes} yearbooks)`,
      onclick: () => openPageModal(firstApp.vid, firstApp.seq, b.name.split(",")[0].split(" ")[0]) },
      el("span", { class: "lbl" }, `${b.name} · ${b.volumes}`),
      spanBar(b.first_year, b.last_year, false)));
  }
  main.append(adWrap);
}

/* ============================= MYSTERIES ================================= */
export async function viewMysteries(main) {
  const mysteries = await loadMysteries();
  main.append(el("h1", { class: "section-title" }, "Mysteries & Corrections"),
    el("p", { class: "section-deck" },
      "Where the record disagrees with itself — printed lists that conflict, catalog errors, missing years, and the honest limits of OCR. Contradictions are displayed, not silently fixed."));
  const cards = el("div", { class: "cards" });
  for (const m of mysteries) {
    const badge = m.status.startsWith("resolved")
      ? el("span", { class: "badge badge-resolved" }, m.status === "resolved" ? "resolved" : "resolved (probable)")
      : el("span", { class: "badge badge-open" }, m.status === "methodology" ? "methodology" : "open question");
    cards.append(el("article", { class: "card mystery" },
      badge,
      el("h3", {}, m.title),
      el("p", {}, m.body),
      await chipsFor(m.citations || [], m.research || [])));
  }
  main.append(cards);
}

/* ============================= SEARCH ==================================== */
export async function viewSearch(main, query) {
  main.append(el("h1", { class: "section-title" }, "Search the Archive"),
    el("p", { class: "section-deck" },
      "Full-text search across all 17,729 pages. Results open the page text with your terms highlighted, and link to the original scans."));
  const input = el("input", { type: "search", value: query || "",
    placeholder: "Try “confirmation class”, “Purim”, “basketball champions”, a business, a street…",
    "aria-label": "Search text" });
  const results = el("div", {});
  const doSearch = async () => {
    const q = input.value.trim();
    location.hash = q ? `#/search/${encodeURIComponent(q)}` : "#/search";
    results.innerHTML = "";
    const tokens = q.toLowerCase().replace(/’/g, "'").match(/[a-z0-9'\-]{3,24}/g) || [];
    if (!tokens.length) return;
    results.append(el("div", { class: "loading" }, "Searching…"));
    try {
      const meta = await loadSearchMeta();
      const postingSets = [];
      for (const t of tokens.slice(0, 5)) {
        const shard = await loadSearchShard(t[0].match(/[a-z]/) ? t[0] : "_").catch(() => ({}));
        const enc = shard[t];
        postingSets.push(enc ? new Set(decodePostings(enc)) : new Set());
      }
      let hits = [...postingSets[0]];
      for (const s of postingSets.slice(1)) hits = hits.filter(p => s.has(p));
      results.innerHTML = "";
      if (!hits.length) {
        results.append(el("p", { class: "empty" }, "No pages matched all terms. OCR spellings vary — try fewer or shorter terms."));
        return;
      }
      const vols = await volumeIndex();
      const byVol = new Map();
      for (const pid of hits) {
        const [vid, seq] = meta[pid];
        if (!byVol.has(vid)) byVol.set(vid, []);
        byVol.get(vid).push(seq);
      }
      results.append(el("p", { style: "color:var(--ink-2)" },
        `${hits.length} page${hits.length > 1 ? "s" : ""} across ${byVol.size} yearbook${byVol.size > 1 ? "s" : ""}.`));
      for (const [vid, seqs] of [...byVol.entries()].sort()) {
        const vol = vols.get(vid);
        const box = el("div", { class: "result-vol" },
          el("h3", {}, vol ? vol.year : vid));
        const chipsWrap = el("div", { class: "chips" });
        for (const seq of seqs.sort((a, b) => a - b).slice(0, 30)) {
          chipsWrap.append(el("button", { class: "chip chip-cite",
            onclick: () => openPageModal(vid, seq, tokens[0]) }, `p.${seq}`));
        }
        if (seqs.length > 30) chipsWrap.append(el("span", { class: "chip chip-demo" }, `+${seqs.length - 30} more`));
        box.append(chipsWrap);
        results.append(box);
      }
    } catch (err) {
      results.innerHTML = "";
      results.append(el("p", { class: "empty" }, `Search failed: ${err.message}`));
    }
  };
  input.addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
  main.append(el("div", { class: "search-row" }, input,
    el("button", { class: "btn btn-gold", onclick: doSearch }, "Search")));
  main.append(results);
  if (query) doSearch();
}

/* ============================= SURPRISE ME =============================== */
export async function surpriseMe() {
  const [stories, threads, events, ads, vols] = await Promise.all([
    loadStories(), loadThreads(), loadEvents(), loadAds(), loadVolumes()]);
  const pool = [];
  for (const s of stories) pool.push({ w: 3, go: () => { location.hash = `#/story/${s.id}`; } });
  for (const t of threads) pool.push({ w: 2, go: () => { location.hash = `#/people/${encodeURIComponent(t.query)}`; } });
  for (const e of events.filter(e => e.citations.length)) {
    pool.push({ w: 1, go: async () => {
      location.hash = "#/";
      const c = e.citations[0];
      setTimeout(() => openPageModal(c.vid, c.seq), 300);
    } });
  }
  const oldAds = ads.filter(b => b.volumes >= 15);
  for (const b of oldAds.slice(0, 10)) {
    pool.push({ w: 1, go: () => {
      const a = b.appearances[Math.floor(Math.random() * b.appearances.length)];
      openPageModal(a.vid, a.seq, b.name.split(",")[0].split(" ")[0]);
    } });
  }
  pool.push({ w: 4, go: () => {
    const v = vols[Math.floor(Math.random() * vols.length)];
    location.hash = `#/time-machine/${v.vid}`;
  } });
  const total = pool.reduce((s, p) => s + p.w, 0);
  let r = Math.random() * total;
  for (const p of pool) { r -= p.w; if (r <= 0) { p.go(); return; } }
}
