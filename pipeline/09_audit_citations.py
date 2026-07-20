#!/usr/bin/env python3
"""Phase B8 / E: verify every curated citation against the cited page text.

For each {vid, seq} citation, check the page contains the expected keyword.
If not, scan the volume for the best matching page and repair the citation
(logged); if no page matches, mark the citation {"unverified": true}.

Usage: python3 pipeline/09_audit_citations.py [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"
DRY = "--dry-run" in sys.argv

_page_cache: dict[tuple[str, int], str] = {}


def normalize(text: str) -> str:
    """Undo OCR line-break hyphenation ('Founda¬\ntion', 'Founda-\ntion')
    and collapse whitespace so keyword checks match running prose."""
    text = re.sub(r"[¬-]\s*\n\s*", "", text)
    return re.sub(r"\s+", " ", text)


def page_text(vid: str, seq: int) -> str:
    key = (vid, seq)
    if key not in _page_cache:
        p = TEXT_DIR / vid / f"{seq:05d}.txt"
        raw = p.read_text(encoding="utf-8") if p.exists() else ""
        _page_cache[key] = normalize(raw)
    return _page_cache[key]


def vol_seqs(vid: str) -> list[int]:
    d = TEXT_DIR / vid
    if not d.exists():
        return []
    return sorted(
        int(f.stem) for f in d.glob("[0-9]*.txt") if f.stem.isdigit()
    )


def find_best(vid: str, kws: list[str], support: list[str]) -> int | None:
    """Best page in volume: must contain all kws; prefer pages that also
    contain a support keyword, then earliest."""
    candidates = []
    for seq in vol_seqs(vid):
        text = page_text(vid, seq).lower()
        if all(k.lower() in text for k in kws):
            bonus = any(s.lower() in text for s in support)
            candidates.append((not bonus, seq))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]


REPORT = {"ok": 0, "repaired": 0, "unverified": 0}
LOG: list[str] = []


def check(cit: dict, kws: list, support: list[str], label: str) -> None:
    """kws: list of keywords (all must match) OR list of lists (any
    alternative set may match)."""
    if "vid" not in cit:
        return
    alts = kws if kws and isinstance(kws[0], list) else [kws]
    vid, seq = cit["vid"], cit["seq"]
    text = page_text(vid, seq).lower()
    if text and any(all(k.lower() in text for k in alt) for alt in alts):
        REPORT["ok"] += 1
        cit.pop("unverified", None)
        return
    for alt in alts:
        best = find_best(vid, alt, support)
        if best is not None:
            LOG.append(f"REPAIR {label}: {vid}/{seq} -> {best} (kw={alt})")
            cit["seq"] = best
            cit.pop("unverified", None)
            REPORT["repaired"] += 1
            return
    LOG.append(f"UNVERIFIED {label}: {vid}/{seq} (kw={kws})")
    cit["unverified"] = True
    REPORT["unverified"] += 1


def surname(name: str) -> str:
    return name.replace("*", "").split()[-1]


def main() -> None:
    # leadership
    lead = json.loads((JSON_DIR / "leadership.json").read_text())
    for p in lead["presidents"]:
        sn = surname(p["name"])
        for cit in p["citations"]:
            if cit.get("note", "").startswith("Past Presidents"):
                check(cit, [[sn], ["president"]], [], f"pres-list {p['name']}")
            else:
                check(cit, [[sn]], ["president"], f"president {p['name']}")
    for c in lead["clergy"]:
        for cit in c["citations"]:
            check(cit, [surname(c["name"])], ["rabbi", "cantor", "hazzan", "rev"], f"clergy {c['name']}")

    # events: per-event keyword to verify
    EV_KW = {
        1901: [["1901"]], 1914: [["Y. M. H. A."], ["Y"]],
        1926: [["elected rabbi"], ["1926"]], 1927: [["Year Book"], ["1926"]],
        1928: [["Dedication"]], 1938: [["tenth anniversary"], ["anniversary"]],
        1946: [["River Garden"], ["1946"]], 1947: [["Tofield"]],
        1952: [["Schechter"]], 1958: [["bombing"]],
        1957: [["Schechter Day School"], ["Foundation School"]],
        1961: [["Foundation School"]], 1976: [["pivot"], ["San Jose"]],
        1980: [["Kentof"]], 1988: [["Pollock"]], 2001: [["Centennial"]],
        2005: [["Galinsky"]],
    }
    events = json.loads((JSON_DIR / "events.json").read_text())
    for e in events:
        kws = EV_KW.get(e["year"])
        if not kws:
            continue
        for cit in e["citations"]:
            check(cit, kws, [], f"event {e['year']} {e['title'][:30]}")

    # threads: query keyword (kuhn thread cites Mendelson too)
    TH_KW = {"kuhn": [["Kuhn"], ["Kuhn"], ["Mendelson"]]}
    threads = json.loads((JSON_DIR / "threads.json").read_text())
    for t in threads:
        kw_lists = TH_KW.get(t["id"])
        for i, cit in enumerate(t["citations"]):
            kws = kw_lists[i] if kw_lists and i < len(kw_lists) else [t["query"].split()[0]]
            check(cit, kws, [], f"thread {t['id']}")

    # stories: id -> per-citation keyword lists (parallel to citations order)
    ST_KW = {
        "1958-bombing": [["bombing"], ["bombing"]],
        "first-yearbook": [["Year Book"], ["Benjamin"], ["1926"], ["Y"]],
        "school-that-grew": [["1926"], ["Schechter"], [["Foundation School"], ["Ramah"]], ["Galinsky"]],
        "usy-to-president": [["Shorstein"], ["Shorstein"], ["Shorstein"], ["Shorstein"], ["Shorstein"], ["Krestul"]],
        "move-to-mandarin": [["fair share"], ["pivot"]],
        "women-of-the-center": [["kippah"], ["Bas Mitzvah"], ["Pollock"]],
        "moscow-call": [["Moscow"], ["Negev"]],
    }
    stories = json.loads((JSON_DIR / "stories.json").read_text())
    for s in stories:
        kw_lists = ST_KW.get(s["id"], [])
        for i, cit in enumerate(s["citations"]):
            kws = kw_lists[i] if i < len(kw_lists) else None
            if kws:
                check(cit, kws, [], f"story {s['id']}[{i}]")

    # mysteries
    MY_KW = {
        "gordon-presidency": [["Gordon"], ["Past Presidents"], ["Selber"], ["loved and respected"]],
        "moss-moscovitz": [["Moss"], ["Mosk"], ["Moscovitz"]],
        "shorstein-term": [["Shorstein"], ["Shorstein"], ["President"]],
        "bud-shorstein": [["Shorstein"], ["Past Presidents"], ["Bud"]],
        "mislabeled-volume": [["2016"], ["Crown Point"]],
        "annex-date": [["bombing"]],
        "early-presidents": [["1901"], ["Pilton"]],
        "org-keyword-caveat": [["Schechter"]],
    }
    mysteries = json.loads((JSON_DIR / "mysteries.json").read_text())
    for m in mysteries:
        kw_lists = MY_KW.get(m["id"], [])
        for i, cit in enumerate(m["citations"]):
            kws = kw_lists[i] if i < len(kw_lists) else None
            if kws:
                check(cit, kws, [], f"mystery {m['id']}[{i}]")

    for line in LOG:
        print(line)
    print(f"\nok={REPORT['ok']} repaired={REPORT['repaired']} unverified={REPORT['unverified']}")

    if not DRY:
        (JSON_DIR / "leadership.json").write_text(json.dumps(lead, indent=1), encoding="utf-8")
        (JSON_DIR / "events.json").write_text(json.dumps(events, indent=1), encoding="utf-8")
        (JSON_DIR / "threads.json").write_text(json.dumps(threads, indent=1), encoding="utf-8")
        (JSON_DIR / "stories.json").write_text(json.dumps(stories, indent=1), encoding="utf-8")
        (JSON_DIR / "mysteries.json").write_text(json.dumps(mysteries, indent=1), encoding="utf-8")
        print("files updated")


if __name__ == "__main__":
    main()
