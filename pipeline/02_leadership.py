#!/usr/bin/env python3
"""Phase B1: extract clergy & lay-leadership CANDIDATES per volume, with
page citations and occurrence counts. Output is reviewed by hand/LLM before
becoming leadership.json — regex output is never published unreviewed.

Usage: python3 pipeline/02_leadership.py > data/json/leadership_candidates.json
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

NAME = r"[A-Z][A-Za-z'\-\.]+(?:\s+[A-Z][A-Za-z'\-\.]*\.?){0,3}\s+[A-Z][A-Za-z'\-]{2,}"

CLERGY_RE = re.compile(
    r"\b(Rabbi|Cantor|Hazzan|Chazzan|Reverend|Rev\.)\s+(" + NAME + r")"
)
# "<NAME>, President" / "<NAME> President" on officer pages
PRES_AFTER_RE = re.compile(
    r"(" + NAME + r")\s*[,.—-]*\s*(President|PRESIDENT)\b"
)
PRES_BEFORE_RE = re.compile(
    r"\bPresident\s*[:.—-]+\s*(" + NAME + r")"
)

# words that break a name capture (OCR noise, sentence-starts, common caps)
BAD_TOKENS = {
    "The", "And", "Our", "New", "Year", "Happy", "Center", "Jewish",
    "Jacksonville", "Congregation", "Synagogue", "Temple", "Israel",
    "Torah", "Sisterhood", "Club", "School", "Board", "Community",
    "Sabbath", "Services", "Emeritus", "Of", "In", "For", "With", "His",
    "Her", "Was", "Is", "Has", "Have", "Will", "This", "That", "Message",
    "Study", "Institute", "Association", "League", "Auxiliary", "Fund",
    "Committee", "Emanu-El", "Beth", "Bnai", "B'nai", "Ahavath", "Chesed",
}


def plausible_name(name: str) -> bool:
    parts = name.replace(".", " ").split()
    if len(parts) < 2 or len(parts) > 4:
        return False
    if any(p in BAD_TOKENS for p in parts):
        return False
    if any(len(p) == 1 for p in parts[-1:]):  # surname must be a real word
        return False
    return True


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    out = []
    for vol in volumes:
        vid = vol["vid"]
        clergy: dict[str, dict] = defaultdict(lambda: {"count": 0, "pages": []})
        presidents: dict[str, dict] = defaultdict(lambda: {"count": 0, "pages": []})
        for rec in vol["page_index"]:
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            for m in CLERGY_RE.finditer(text):
                title, name = m.group(1), m.group(2).strip(" .")
                if not plausible_name(name):
                    continue
                key = f"{'Cantor' if title in ('Hazzan', 'Chazzan') else title} {name}"
                clergy[key]["count"] += 1
                if len(clergy[key]["pages"]) < 12:
                    clergy[key]["pages"].append(seq)
            # presidents: only scan front matter + officer-looking pages
            if seq <= 40 or re.search(r"\bOFFICERS\b|Officers\b", text):
                for m in PRES_AFTER_RE.finditer(text):
                    name = m.group(1).strip(" .")
                    if plausible_name(name):
                        presidents[name]["count"] += 1
                        if len(presidents[name]["pages"]) < 8:
                            presidents[name]["pages"].append(seq)
                for m in PRES_BEFORE_RE.finditer(text):
                    name = m.group(1).strip(" .")
                    if plausible_name(name):
                        presidents[name]["count"] += 1
                        if len(presidents[name]["pages"]) < 8:
                            presidents[name]["pages"].append(seq)

        top_clergy = sorted(clergy.items(), key=lambda kv: -kv[1]["count"])[:8]
        top_pres = sorted(presidents.items(), key=lambda kv: -kv[1]["count"])[:6]
        out.append(
            {
                "vid": vid,
                "year": vol["year"],
                "clergy_candidates": [
                    {"name": k, **v} for k, v in top_clergy if v["count"] >= 2
                ],
                "president_candidates": [
                    {"name": k, **v} for k, v in top_pres
                ],
            }
        )
    (JSON_DIR / "leadership_candidates.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8"
    )
    print(f"wrote candidates for {len(out)} volumes")


if __name__ == "__main__":
    main()
