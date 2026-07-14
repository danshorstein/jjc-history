#!/usr/bin/env python3
"""Phase B4: parse 'Directory of Advertisers' pages into per-volume
advertiser lists; aggregate businesses recurring across decades.

Output: data/json/advertisers.json
Usage: python3 pipeline/05_ads.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

DIR_HDR = re.compile(
    r"DIRECTORY\s+OF\s+ADVERTISERS|"
    r"(?:CLASSIFIED|ALPHABETIZED)\s+DIRECTORY|"
    r"ADVERTISERS[’']?\s+(?:DIRECTORY|INDEX)",
    re.IGNORECASE,
)
NOT_AD_PAGE = re.compile(r"MEMBERSHIP\s+DIRECTORY|DIRECTORY\s+OF\s+MEMBERS", re.IGNORECASE)
# "Business Name ..... 123" possibly with dots/spaces before the number
ENTRY = re.compile(r"^([A-Za-z0-9][\w&'’.,\- ()/]+?)[ .]{1,60}(\d{1,3})$")
CATEGORY = re.compile(r"^[A-Z][A-Z &,'’\-/]{3,40}$")


def norm_name(name: str) -> str:
    n = name.strip(" .,")
    n = re.sub(r"\s+", " ", n)
    n = n.replace("’", "'")
    # canonicalize common suffix noise
    n = re.sub(r"[ ,]+(Inc|Co|Corp|Ltd)\.?$", lambda m: ", " + m.group(1) + ".", n)
    return n


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    businesses: dict[str, dict] = defaultdict(
        lambda: {"appearances": [], "categories": set()}
    )
    per_vol_counts = {}
    for vol in volumes:
        vid = vol["vid"]
        count = 0
        for rec in vol["page_index"]:
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            # must BE a directory page (header up top), not a TOC that
            # merely lists "Directory of Advertisers" as an entry
            if not DIR_HDR.search(text[:120]):
                continue
            if re.search(r"TABLE\s+OF\s+CONTENTS|Table of Contents", text):
                continue
            if NOT_AD_PAGE.search(text[:120]):
                continue
            category = ""
            for line in text.splitlines():
                line = line.strip()
                if DIR_HDR.search(line) or not line:
                    continue
                if CATEGORY.match(line) and not re.search(r"\d", line):
                    category = line.title()
                    continue
                m = ENTRY.match(line)
                if not m:
                    continue
                name = norm_name(m.group(1))
                if len(name) < 4 or name.isdigit():
                    continue
                key = re.sub(r"[^a-z0-9]", "", name.lower())[:32]
                if len(key) < 4:
                    continue
                b = businesses[key]
                b.setdefault("name", name)
                b["appearances"].append(
                    {
                        "vid": vid,
                        "year": vol["year"],
                        "year_start": vol["year_start"],
                        "seq": seq,
                        "printed_page": int(m.group(2)),
                    }
                )
                if category:
                    b["categories"].add(category)
                count += 1
        if count:
            per_vol_counts[vol["year"]] = count

    out = []
    for key, b in businesses.items():
        vols = {a["vid"] for a in b["appearances"]}
        years = sorted({a["year_start"] for a in b["appearances"] if a["year_start"]})
        out.append(
            {
                "name": b["name"],
                "key": key,
                "volumes": len(vols),
                "first_year": years[0] if years else None,
                "last_year": years[-1] if years else None,
                "categories": sorted(b["categories"]),
                "appearances": b["appearances"],
            }
        )
    out.sort(key=lambda b: -b["volumes"])
    (JSON_DIR / "advertisers.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8"
    )
    print(f"volumes with directories: {len(per_vol_counts)}")
    print(f"distinct businesses: {len(out)}")
    print("longest-running advertisers:")
    for b in out[:15]:
        print(f"  {b['name']:42} {b['volumes']:3} vols {b['first_year']}–{b['last_year']}")


if __name__ == "__main__":
    main()
