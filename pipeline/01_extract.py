#!/usr/bin/env python3
"""Phase A: unzip the UFDC yearbook archive, normalize encodings to UTF-8,
and build data/json/volumes.json with per-page UFDC deep links.

Usage: python3 pipeline/01_extract.py
"""
import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT / "Jacksonville_Jewish_Center_Yearbooks_TXT.zip"
PREFIX = "Jacksonville_Jewish_Center_Yearbooks_TXT/"
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"
BIBID = "AA00010733"


def decode_page(raw: bytes) -> str:
    """Decode page bytes: UTF-16 (BOM) or UTF-8, falling back to latin-1."""
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")
    # Some files are UTF-16 without BOM: every other byte NUL.
    if text.count("\x00") > len(text) // 4:
        for enc in ("utf-16-le", "utf-16-be"):
            try:
                alt = raw.decode(enc)
                if alt.count("\x00") < 2:
                    return alt
            except UnicodeDecodeError:
                pass
    return text


def clean_text(text: str) -> str:
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_years(label: str) -> tuple[int | None, int | None]:
    m = re.match(r"^(\d{4})(?:-(\d{4}))?$", label.strip())
    if not m:
        return None, None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    return start, end


def detect_hebrew_year(vol_dir: Path, page_records: list[dict]) -> int | None:
    """Scan the first pages of a volume for a Hebrew year like 5699."""
    for rec in page_records[:10]:
        p = vol_dir / f"{rec['seq']:05d}.txt"
        if not p.exists():
            continue
        m = re.search(r"\b(5[67]\d\d)\b", p.read_text(encoding="utf-8"))
        if m:
            return int(m.group(1))
    return None


def main() -> None:
    zf = zipfile.ZipFile(ZIP_PATH)
    manifest = json.loads(zf.read(PREFIX + "manifest.json"))
    overrides = json.loads((ROOT / "pipeline" / "overrides.json").read_text())
    year_overrides = overrides["year_overrides"]
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    # page file entries from the manifest: vid, position, relative_path, url
    pages_by_vid: dict[str, list[dict]] = {}
    for f in manifest["files"]:
        pages_by_vid.setdefault(f["vid"], []).append(f)

    volumes_out = []
    encodings = {"utf-16": 0, "utf-8": 0}
    for vol in manifest["volumes"]:
        vid = vol["vid"]
        files = sorted(pages_by_vid.get(vid, []), key=lambda f: f["position"])
        vol_dir = TEXT_DIR / vid
        vol_dir.mkdir(exist_ok=True)
        page_records = []
        combined_parts = []
        for f in files:
            rel = f["relative_path"]
            # pages/<seq>__<ufdc-page-id>.txt ; skip the combined-PDF text dump
            m = re.search(r"pages/(\d+)__(.+)\.txt$", rel)
            if not m:
                continue
            seq, page_id = m.group(1), m.group(2)
            if "pdf" in page_id.lower() or "xml" in page_id.lower():
                continue  # whole-book PDF text / METS xml, not a page scan
            raw = zf.read(PREFIX + rel)
            if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
                encodings["utf-16"] += 1
            else:
                encodings["utf-8"] += 1
            text = clean_text(decode_page(raw))
            out = vol_dir / f"{seq}.txt"
            out.write_text(text + "\n", encoding="utf-8")
            page_records.append(
                {
                    "seq": int(seq),
                    "page_id": page_id,
                    "chars": len(text),
                    # UFDC page viewer: https://ufdc.ufl.edu/AA00010733/<vid>/<seq>
                    "ufdc_url": f"https://ufdc.ufl.edu/{BIBID}/{vid}/{int(seq)}",
                    "image_url": f"https://ufdcimages.uflib.ufl.edu/AA/00/01/07/33/{vid}/{page_id}.jpg",
                    "thumb_url": f"https://ufdcimages.uflib.ufl.edu/AA/00/01/07/33/{vid}/{page_id}thm.jpg",
                }
            )
            combined_parts.append(f"===== PAGE {int(seq)} =====\n{text}\n")
        (vol_dir / "combined.txt").write_text("".join(combined_parts), encoding="utf-8")

        ov = year_overrides.get(vid)
        year_label = ov["year"] if ov else vol["label"]
        y_start, y_end = parse_years(year_label)
        record = {
            "vid": vid,
            "year": year_label,
            "year_start": y_start,
            "year_end": y_end,
            "decade": (y_start // 10 * 10) if y_start else None,
            "hebrew_year": detect_hebrew_year(vol_dir, page_records),
            "label_original": vol["label"],
            "title": vol["title"],
            "pages": len(page_records),
            "ufdc_url": vol["ufdc_url"],
            "page_index": page_records,
        }
        if ov:
            record["label_correction"] = {
                "note": ov["note"],
                "evidence_seq": ov["evidence_seq"],
            }
        volumes_out.append(record)

    volumes_out.sort(key=lambda v: (v["year_start"] or 0, v["vid"]))

    (JSON_DIR / "volumes.json").write_text(
        json.dumps(volumes_out, indent=1), encoding="utf-8"
    )
    total_pages = sum(v["pages"] for v in volumes_out)
    print(f"volumes: {len(volumes_out)}  pages: {total_pages}")
    print(f"encodings seen: {encodings}")


if __name__ == "__main__":
    main()
