#!/usr/bin/env python3
"""Phase B3: build the personal-name occurrence index.

Finds title-cased name sequences (with optional honorifics), filters
non-name capitalized phrases via blocklists, and emits:
  data/json/names/<A>.json   sharded by surname initial:
      { "<surname>|<display>": {"d": display, "s": surname,
                                 "a": [[vol_idx, seq], ...]} }
  data/json/names_meta.json   vol_idx -> {vid, year}
Conservative rule: an entry is a NAME STRING, not a person. Cross-year
identity is asserted only in curated layers.

Usage: python3 pipeline/04_names.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

TITLES = r"(?:Mr|Mrs|Miss|Ms|Dr|Rabbi|Cantor|Hazzan|Judge|Rev|Prof|Sgt|Capt|Col)\.?"
CAP = r"[A-Z][a-z'’\-]+"
INITIAL = r"[A-Z]\.?"
NAME_RE = re.compile(
    rf"\b(?P<title>{TITLES}\s+)?"
    rf"(?P<first>{CAP}|{INITIAL})\s+"
    rf"(?P<mid>(?:{INITIAL}|{CAP})\s+)?"
    rf"(?P<last>{CAP})\b"
)

# Capitalized words that are never given/surnames in this corpus's context.
NOT_NAME = set("""
January February March April May June July August September October November
December Monday Tuesday Wednesday Thursday Friday Saturday Sunday
Jewish Jacksonville Center Florida Temple Synagogue Congregation Israel
Torah Talmud Shabbat Sabbath Kiddush Seder Purim Pesach Passover Sukkot
Succoth Shavuot Shovuoth Chanukah Hanukkah Rosh Hashanah Yom Kippur
Simchat Simchas Havdalah Mitzvah Mitzvahs Bar Bat Bris Kaddish Yahrzeit
Sisterhood Club School Board Committee League Auxiliary Association Fund
Society Council Youth Junior Senior Annual Meeting Officers President
Presidents Vice Secretary Treasurer Chairman Director Members Membership
New Year Happy Greetings Best Wishes Compliments Friend Friends Family
Street Avenue Boulevard Road Phone Company Bank Store Shop Inc Corp
American America United States National First Second Third Fourth Fifth
The And Our Your His Her Their This That These Those From With For
Beth Bnai Ahavath Chesed Emanu El Zion Hebrew Hadassah Israelite
Day Camp Services Service Education Library Page Table Contents
Mother Father Sister Brother Daughter Son Baby Loving Memory Honor
South North East West Main Park Riverside Springfield San Jose Crown Point
High Holy Holiday Holidays Festival Choir Orchestra Glee
Good Great Little Big Old Young Editor Staff Advertising Manager
University College Academy Preschool Kindergarten Grade Class Classes
God Lord Blessed Peace Light Life Love Hope Faith Charity
Very Truly Sincerely Yours Respectfully Cordially
Congratulations Anniversary Birthday Wedding Welcome Thank Thanks
""".split())

# Common OCR junk / stray tokens seen in sampling
NOT_NAME |= {"Ill", "Il", "Iii", "Ll", "Lll", "Yl", "Jj", "Uu"}


def shard_key(surname: str) -> str:
    c = surname[0].upper()
    return c if c.isalpha() else "_"


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    vol_meta = [{"vid": v["vid"], "year": v["year"]} for v in volumes]
    names: dict[str, dict] = {}

    for vol_idx, vol in enumerate(volumes):
        vid = vol["vid"]
        for rec in vol["page_index"]:
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            seen_on_page = set()
            for m in NAME_RE.finditer(text):
                first = m.group("first").rstrip(".")
                mid = (m.group("mid") or "").strip().rstrip(".")
                last = m.group("last")
                title = (m.group("title") or "").strip().rstrip(".")
                # filters
                if last in NOT_NAME or first in NOT_NAME or mid in NOT_NAME:
                    continue
                if len(last) < 3:
                    continue
                # single-letter first with no title and no middle: too weak
                if len(first) <= 2 and not title and not mid:
                    continue
                display = " ".join(
                    x for x in [f"{title}." if title else "", first, mid, last] if x
                ).replace("..", ".")
                key = f"{last}|{display}"
                if key in seen_on_page:
                    continue
                seen_on_page.add(key)
                ent = names.get(key)
                if ent is None:
                    ent = names[key] = {"d": display, "s": last, "a": []}
                ent["a"].append([vol_idx, seq])

    # prune singleton OCR noise: keep entries seen >=2 times OR bearing a title
    pruned = {
        k: v
        for k, v in names.items()
        if len(v["a"]) >= 2 or re.match(TITLES, v["d"])
    }

    shards: dict[str, dict] = defaultdict(dict)
    for k, v in pruned.items():
        shards[shard_key(v["s"])][k] = v

    out_dir = JSON_DIR / "names"
    out_dir.mkdir(exist_ok=True)
    total = 0
    for letter, entries in sorted(shards.items()):
        (out_dir / f"{letter}.json").write_text(
            json.dumps(entries, separators=(",", ":")), encoding="utf-8"
        )
        total += len(entries)
    (JSON_DIR / "names_meta.json").write_text(
        json.dumps(vol_meta, separators=(",", ":")), encoding="utf-8"
    )
    print(f"kept {total} name strings ({len(names)} raw) across {len(shards)} shards")
    import os
    size = sum(os.path.getsize(out_dir / f) for f in os.listdir(out_dir))
    print(f"total shard size: {size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
