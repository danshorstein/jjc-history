#!/usr/bin/env python3
"""Phase B5: estimate printed-page -> scan-seq offset per volume, then parse
Table of Contents pages into navigable section maps.

Output: data/json/sections.json  [{vid, year, offset, confidence, sections:[
    {title, printed_start, printed_end, seq_start, seq_end}]}]
Usage: python3 pipeline/06_sections.py
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

TOC_HDR = re.compile(r"TABLE\s+OF\s+CONTENTS", re.IGNORECASE)
TOC_ENTRY = re.compile(r"^(.{3,60}?)[ .]{1,60}(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?$")


def estimate_offset(vid: str, page_index: list[dict]) -> tuple[int | None, float]:
    """Printed page numbers usually appear as a standalone token at the very
    start or end of the OCR text. offset = seq - printed."""
    votes: Counter[int] = Counter()
    for rec in page_index:
        seq = rec["seq"]
        p = TEXT_DIR / vid / f"{seq:05d}.txt"
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8").strip()
        if not text:
            continue
        head, tail = text[:20], text[-20:]
        for zone in (head, tail):
            for tok in re.findall(r"(?<![\d/,$-])(\d{1,3})(?![\d/,%-])", zone):
                printed = int(tok)
                if 1 <= printed <= len(page_index) + 30:
                    off = seq - printed
                    if 0 <= off <= 30:
                        votes[off] += 1
    if not votes:
        return None, 0.0
    off, n = votes.most_common(1)[0]
    total = sum(votes.values())
    return off, n / total


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    out = []
    for vol in volumes:
        vid = vol["vid"]
        offset, conf = estimate_offset(vid, vol["page_index"])
        max_seq = max((r["seq"] for r in vol["page_index"]), default=0)
        sections = []
        for rec in vol["page_index"][:30]:  # TOC lives in front matter
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            if not TOC_HDR.search(text) and "Table of Contents" not in text:
                continue
            for line in text.splitlines():
                line = line.strip()
                m = TOC_ENTRY.match(line)
                if not m:
                    continue
                title = m.group(1).strip(" .").strip()
                if not re.search(r"[A-Za-z]{3}", title) or title.lower() == "page":
                    continue
                p_start = int(m.group(2))
                p_end = int(m.group(3)) if m.group(3) else p_start
                if p_end < p_start or p_start < 1:
                    continue
                entry = {
                    "title": title,
                    "printed_start": p_start,
                    "printed_end": p_end,
                    "toc_seq": seq,
                }
                if offset is not None and conf >= 0.4:
                    s0, s1 = p_start + offset, p_end + offset
                    if 1 <= s0 <= max_seq:
                        entry["seq_start"] = s0
                        entry["seq_end"] = min(s1, max_seq)
                sections.append(entry)
        # dedupe (TOC often spans 2 scanned pages / columns repeat)
        seen = set()
        uniq = []
        for s in sections:
            k = (s["title"].lower(), s["printed_start"])
            if k not in seen:
                seen.add(k)
                uniq.append(s)
        out.append(
            {
                "vid": vid,
                "year": vol["year"],
                "offset": offset,
                "offset_confidence": round(conf, 2),
                "sections": uniq,
            }
        )
    (JSON_DIR / "sections.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    with_toc = [v for v in out if v["sections"]]
    print(f"volumes with parsed TOC: {len(with_toc)}/{len(out)}")
    good_off = [v for v in out if v["offset"] is not None and v["offset_confidence"] >= 0.4]
    print(f"volumes with confident offset: {len(good_off)}")
    ex = next(v for v in out if v["vid"] == "00024")
    print(f"example 1965-66: offset={ex['offset']} conf={ex['offset_confidence']} sections={len(ex['sections'])}")
    for s in ex["sections"][:8]:
        print("   ", s["title"], s["printed_start"], "->seq", s.get("seq_start"))


if __name__ == "__main__":
    main()
