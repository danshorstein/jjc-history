#!/usr/bin/env python3
"""Phase E: strengthen president citations semantically.

For each verified president, scan the volumes overlapping their term for a
page where the FULL NAME appears within a small window of the word
'President' (title-adjacent scores highest). Replaces the era citations in
leadership.json with the best 1-2 evidence pages; reports anyone whose
evidence stays weak so it can be flagged honestly.

Usage: python3 pipeline/11_president_evidence.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

FIRST_NAME_ALTS = {
    "Sandy": ["Sandy", "Sanford"],
    "Seeman": ["Seeman"],
    "Jeffery": ["Jeffery", "Jeffrey"],
    "Nathan": ["Nathan"],
    "David": ["David"],
    "Mitchell": ["Mitchell", "Mitch"],
    "Lawrence": ["Lawrence", "Laurie"],
}


def normalize(t: str) -> str:
    t = re.sub(r"[¬-]\s*\n\s*", "", t)
    return re.sub(r"\s+", " ", t)


def name_variants(name: str) -> list[tuple[str, str]]:
    """-> [(first, last), ...] variants to search."""
    parts = [p for p in name.replace("Dr. ", "").replace("Judge ", "").split() if p]
    first, last = parts[0], parts[-1]
    firsts = FIRST_NAME_ALTS.get(first, [first])
    return [(f, last) for f in firsts]


def presidents_in(text: str, lo: int, hi: int) -> list[re.Match]:
    """'President' tokens that are NOT part of 'Vice(-)President' or
    'President's Wife' within the [lo:hi] slice."""
    out = []
    for m in re.finditer(r"president", text[lo:hi], re.I):
        s = lo + m.start()
        before = text[max(0, s - 10):s].lower()
        after = text[s:s + 22].lower()
        if re.search(r"vice[\s\-–.]*$", before):
            continue
        if "wife" in after:
            continue
        out.append(m)
    return out


def score_page(text: str, first: str, last: str) -> int:
    """3 = full name immediately adjacent to a standalone 'President' title;
    0 = no acceptable evidence. Officer-list bleed ('Vice President',
    'Mrs. <husband>') is excluded."""
    best = 0
    name_rx = re.compile(re.escape(first) + r"[\s.]{1,3}(?:[A-Z][\w.]{0,12}\s)?" + re.escape(last), re.I)
    for m in name_rx.finditer(text):
        s, e = m.start(), m.end()
        # exclude "Mrs. <husband's name>" convention
        if re.search(r"mrs[.\s]*$", text[max(0, s - 8):s], re.I):
            continue
        if presidents_in(text, max(0, s - 34), min(len(text), e + 34)):
            best = max(best, 3)
        elif presidents_in(text, max(0, s - 150), min(len(text), e + 150)):
            best = max(best, 1)  # same page, loose — not accepted alone
    return best


# Hand-verified evidence pages (read in full during the audit) that the
# window-scorer either misses or gets wrong (officer lists where a neighbor's
# title bleeds into the window).
MANUAL_EVIDENCE = {
    "Marsha Pollock": [("00048", 203)],   # her signed President's Message, 1989-90
    "Michael Shorstein": [("00059", 40), ("00060", 53)],  # "incoming President" + signed message
    "Max Frank": [("00002", 28)],   # 1901 charter, reproduced 1926-27: "Max Frank, President"
    "Isaac Davis": [("00002", 29)],  # history essay: "Davis, President"
    "Elias H. Pilton": [("00002", 28), ("00002", 30)],  # charter trustee; "For nearly 20 years President" caption
}
# Moscovitz's two terms: the 1926-27 history page captions him "President";
# his 1938-39 signed message page (TOC: "President's Message 12") is seq 14.
MANUAL_EVIDENCE["David Moscovitz"] = [("00002", 30), ("00001", 14)]


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    lead = json.loads((JSON_DIR / "leadership.json").read_text())
    weak = []
    for p in lead["presidents"]:
        manual = MANUAL_EVIDENCE.get(p["name"])
        if manual:
            list_cits = [c for c in p["citations"] if c.get("note")]
            p["citations"] = list_cits + [{"vid": v, "seq": s} for v, s in manual]
            p["confidence"] = "verified"
            print(f"{'MANUAL':20} {p['name']:24} {p['term']:12} -> {manual}")
            continue
        if p["confidence"] != "verified":
            continue
        y0, y1 = p["start"], p["end"]
        # yearbooks published DURING the term (year_start in [start, end-1]);
        # single-year terms also get the preceding volume (fall publication).
        lo = y0 if y1 > y0 else y0 - 1
        hi = max(y1 - 1, y0)
        vols = [v for v in volumes
                if v["year_start"] and lo <= v["year_start"] <= hi]
        best = (0, None, None)  # score, vid, seq
        for v in vols:
            vid = v["vid"]
            for rec in v["page_index"]:
                seq = rec["seq"]
                f = TEXT_DIR / vid / f"{seq:05d}.txt"
                if not f.exists():
                    continue
                text = normalize(f.read_text(encoding="utf-8"))
                for first, last in name_variants(p["name"]):
                    sc = score_page(text, first, last)
                    if sc > best[0]:
                        best = (sc, vid, seq)
                if best[0] == 3:
                    break
            if best[0] == 3:
                break
        list_cits = [c for c in p["citations"] if c.get("note")]
        if best[0] >= 3:
            p["citations"] = list_cits + [{"vid": best[1], "seq": best[2]}]
            status = "STRONG"
        else:
            # keep list citations; drop weak era page; flag
            p["citations"] = list_cits
            p["confidence"] = "printed-list"
            weak.append(p["name"])
            status = "WEAK->printed-list"
        print(f"{status:20} {p['name']:24} {p['term']:12} -> {best[1]}/{best[2] if best[2] else '-'} (score {best[0]})")

    (JSON_DIR / "leadership.json").write_text(json.dumps(lead, indent=1), encoding="utf-8")
    print(f"\nweak evidence, downgraded to printed-list: {weak or 'none'}")


if __name__ == "__main__":
    main()
