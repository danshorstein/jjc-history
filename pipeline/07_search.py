#!/usr/bin/env python3
"""Phase B6: build a sharded inverted index for client-side full-text search.

Pages get global ids (volume order, then seq). Tokens (lowercased, 3-24
chars, containing a letter) map to delta-encoded base36 posting lists at
page granularity. Sharded by first character for on-demand loading.

Output: data/json/search/<c>.json  {token: "b36,b36,..."} (deltas)
        data/json/search_meta.json  page id -> [vid, seq] table (compact)
Usage: python3 pipeline/07_search.py
"""
import json
import re
import string
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

TOKEN = re.compile(r"[a-z0-9'’\-]{3,24}")
STOP = set("""
the and for with that this from was were are you your our his her their has
have had not but all any can will one two three which when where what who
whom been being does did than then them they there here how its it's also
into out over under more most other some such only own same too very just
each few both during before after above below between because while about
against again further once
""".split())

B36 = string.digits + string.ascii_lowercase


def b36(n: int) -> str:
    if n == 0:
        return "0"
    s = []
    while n:
        n, r = divmod(n, 36)
        s.append(B36[r])
    return "".join(reversed(s))


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    page_table = []
    postings: dict[str, list[int]] = defaultdict(list)
    pid = 0
    for vol in volumes:
        vid = vol["vid"]
        for rec in vol["page_index"]:
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            page_table.append([vid, seq])
            if p.exists():
                text = p.read_text(encoding="utf-8").lower().replace("’", "'")
                toks = set(TOKEN.findall(text))
                for t in toks:
                    t = t.strip("'-")
                    if len(t) < 3 or t in STOP or t.isdigit():
                        continue
                    lst = postings[t]
                    if not lst or lst[-1] != pid:
                        lst.append(pid)
            pid += 1

    shards: dict[str, dict[str, str]] = defaultdict(dict)
    for tok, pids in postings.items():
        if len(pids) < 2 and len(tok) > 18:
            continue  # long singleton OCR garbage
        deltas = [pids[0]] + [b - a for a, b in zip(pids, pids[1:])]
        shards[tok[0] if tok[0].isalpha() else "_"][tok] = ",".join(
            b36(d) for d in deltas
        )

    out_dir = JSON_DIR / "search"
    out_dir.mkdir(exist_ok=True)
    total_bytes = 0
    for c, entries in sorted(shards.items()):
        f = out_dir / f"{c}.json"
        f.write_text(json.dumps(entries, separators=(",", ":")), encoding="utf-8")
        total_bytes += f.stat().st_size
    (JSON_DIR / "search_meta.json").write_text(
        json.dumps(page_table, separators=(",", ":")), encoding="utf-8"
    )
    print(f"pages: {pid}  tokens: {len(postings)}  shards: {len(shards)}")
    print(f"index size: {total_bytes/1e6:.1f} MB; meta: {(JSON_DIR/'search_meta.json').stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
