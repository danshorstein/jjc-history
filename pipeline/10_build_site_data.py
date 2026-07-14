#!/usr/bin/env python3
"""Phase B9: assemble the JSON bundle the website consumes.

Outputs into site/data/:
  volumes.json      slim volume index (page ids only; URLs derived client-side)
  years/<vid>.json  per-volume Time Machine payload
  ads.json          businesses appearing in >= 4 volumes
  orgs.json         organization timelines (trimmed pages)
  leadership.json, events.json, threads.json, stories.json,
  mysteries.json, research_sources.json   (copied)
  names/<A>.json, names_meta.json         (copied)
  search/<c>.json, search_meta.json       (copied)

Usage: python3 pipeline/10_build_site_data.py
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "data" / "json"
SITE_DATA = ROOT / "site" / "data"


def main() -> None:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / "years").mkdir(exist_ok=True)

    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    leadership = json.loads((JSON_DIR / "leadership.json").read_text())
    orgs = json.loads((JSON_DIR / "organizations.json").read_text())
    ads = json.loads((JSON_DIR / "advertisers.json").read_text())
    sections = {s["vid"]: s for s in json.loads((JSON_DIR / "sections.json").read_text())}

    # ---- slim volume index
    slim = []
    for v in volumes:
        slim.append(
            {
                "vid": v["vid"],
                "year": v["year"],
                "year_start": v["year_start"],
                "year_end": v["year_end"],
                "decade": v["decade"],
                "hebrew_year": v["hebrew_year"],
                "pages": v["pages"],
                "ufdc_url": v["ufdc_url"],
                "page_ids": {str(p["seq"]): p["page_id"] for p in v["page_index"]},
                **({"label_correction": v["label_correction"]} if "label_correction" in v else {}),
            }
        )
    (SITE_DATA / "volumes.json").write_text(
        json.dumps(slim, separators=(",", ":")), encoding="utf-8"
    )

    # ---- per-volume payloads
    ads_by_vid: dict[str, list] = {}
    for b in ads:
        for a in b["appearances"]:
            ads_by_vid.setdefault(a["vid"], []).append(
                {"name": b["name"], "seq": a["seq"], "vols": b["volumes"]}
            )
    orgs_by_vid: dict[str, list] = {}
    for o in orgs:
        for a in o["appearances"]:
            orgs_by_vid.setdefault(a["vid"], []).append(
                {"name": o["name"], "pages": a["pages"][:6], "count": a["count"]}
            )

    for v in volumes:
        vid = v["vid"]
        y0, y1 = v["year_start"], v["year_end"]
        pres = [
            {"name": p["name"], "term": p["term"], "note": p.get("note"),
             "confidence": p["confidence"]}
            for p in leadership["presidents"]
            if y0 and not (p["end"] < y0 or p["start"] > (y1 or y0))
        ]
        clergy = [
            {"name": c["name"], "role": c["role"]}
            for c in leadership["clergy"]
            if y0 and not (c["to"] < y0 or c["from"] > (y1 or y0))
        ]
        vol_ads = sorted(ads_by_vid.get(vid, []), key=lambda a: -a["vols"])
        secs = sections.get(vid, {}).get("sections", [])
        payload = {
            "vid": vid,
            "year": v["year"],
            "hebrew_year": v["hebrew_year"],
            "pages": v["pages"],
            "ufdc_url": v["ufdc_url"],
            "presidents": pres,
            "clergy": clergy,
            "organizations": sorted(
                orgs_by_vid.get(vid, []), key=lambda o: -o["count"]
            )[:24],
            "advertisers": vol_ads[:40],
            "sections": [
                {k: s[k] for k in ("title", "printed_start", "seq_start") if k in s}
                for s in secs[:60]
            ],
        }
        (SITE_DATA / "years" / f"{vid}.json").write_text(
            json.dumps(payload, separators=(",", ":")), encoding="utf-8"
        )

    # ---- trimmed cross-volume files
    ads_slim = [
        {
            "name": b["name"],
            "volumes": b["volumes"],
            "first_year": b["first_year"],
            "last_year": b["last_year"],
            "categories": b["categories"][:3],
            "appearances": [
                {"vid": a["vid"], "year": a["year"], "seq": a["seq"]}
                for a in b["appearances"][:60]
            ],
        }
        for b in ads
        if b["volumes"] >= 4 and b["first_year"]
    ]
    (SITE_DATA / "ads.json").write_text(
        json.dumps(ads_slim, separators=(",", ":")), encoding="utf-8"
    )

    orgs_slim = [
        {
            "name": o["name"],
            "appearances": [
                {"vid": a["vid"], "year": a["year"], "year_start": a["year_start"],
                 "count": a["count"], "pages": a["pages"][:4]}
                for a in o["appearances"]
            ],
        }
        for o in orgs
    ]
    (SITE_DATA / "orgs.json").write_text(
        json.dumps(orgs_slim, separators=(",", ":")), encoding="utf-8"
    )

    for name in ("leadership", "events", "threads", "stories", "mysteries",
                 "research_sources", "names_meta", "search_meta"):
        shutil.copy(JSON_DIR / f"{name}.json", SITE_DATA / f"{name}.json")
    for sub in ("names", "search"):
        dst = SITE_DATA / sub
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(JSON_DIR / sub, dst)

    total = sum(f.stat().st_size for f in SITE_DATA.rglob("*") if f.is_file())
    print(f"site/data ready: {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
