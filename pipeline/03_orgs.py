#!/usr/bin/env python3
"""Phase B2: track organizations/programs across all volumes using a
controlled vocabulary (regex variants -> canonical name). Emits per-volume
appearances with page citations: data/json/organizations.json

Usage: python3 pipeline/03_orgs.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

# canonical org/program -> regex (case-insensitive where safe)
ORGS: dict[str, str] = {
    "Sisterhood": r"\bSisterhood\b",
    "Men's Club": r"\bMen[’']?s\s+Club\b",
    "Junior Congregation": r"\bJunior\s+(?:Congregation|Synagogue)\b",
    "USY (United Synagogue Youth)": r"\bUnited\s+Synagogue\s+Youth\b|\bUSY\b",
    "Kadima": r"\bKadima\b",
    "Center Youth League": r"\bCenter\s+Youth\s+League\b",
    "Charles Palot Club": r"\bCharles\s+Palot\b",
    "ATID": r"\bATID\b",
    "AZA (Aleph Zadik Aleph)": r"\bAleph\s+Zadik\s+Aleph\b|\bAZA\b",
    "BBG (B'nai B'rith Girls)": r"\bB[’']?nai\s+B[’']?rith\s+Girls\b|\bBBG\b",
    "B'nai B'rith": r"\bB[’']?nai\s+B[’']?rith\b",
    "Hadassah": r"\bHadassah\b",
    "Hannah Senesch Group": r"\bHann?ah\s+Senes[ch]+\b",
    "Boy Scouts": r"\bBoy\s+Scouts?\b|\bScout\s+Troop\b|\bCub\s+(?:Pack|Scouts)\b",
    "Girl Scouts / Brownies": r"\bGirl\s+Scouts?\b|\bBrownies\b",
    "Foundation School": r"\bFoundation\s+School\b",
    "Religious School": r"\bReligious\s+School\b|\bSunday\s+School\b|\bHebrew\s+School\b",
    "Solomon Schechter Day School": r"\bSolomon\s+Schechter\b",
    "Martin J. Gottlieb Day School": r"\bGottlieb\s+Day\s+School\b",
    "DuBow Preschool": r"\bDuBow\s+Preschool\b",
    "Bernard & Alice Selevan Religious School": r"\bSelevan\s+Religious\s+School\b",
    "Galinsky Academy": r"\bGalinsky\s+Academy\b",
    "Setzer Youth Education": r"\bSetzer\s+Youth\b",
    "Camp Ramah": r"\bCamp\s+Ramah\b|\bRamah\b",
    "Day Camp": r"\bDay\s+Camp\b",
    "Choir / Glee Club": r"\bChoir\b|\bGlee\s+Club\b",
    "Center Players / Dramatics": r"\bCenter\s+Players\b|\bDramatic\s+(?:Club|Society)\b",
    "Young Men's Hebrew Association (YMHA)": r"\bY\.?\s?M\.?\s?H\.?\s?A\.?\b|\bYoung\s+Men[’']?s\s+Hebrew\b",
    "Knights and Dames": r"\bKnights\s+and\s+Dames\b",
    "Amity Club": r"\bAmity\s+Club\b",
    "Major's Pre-Teens": r"\bMajor[’']?s\s+Pre-?Teens\b",
    "Hebrew Sheltering Aid Society": r"\bHebrew\s+Sheltering\b",
    "Jewish Community Council": r"\bJewish\s+Community\s+Council\b",
    "Jewish Family (and Children's) Services": r"\bJewish\s+Family\s+(?:and|&)?\s*(?:Children[’']?s)?\s*Servic",
    "River Garden Hebrew Home": r"\bRiver\s+Garden\b",
    "Daughters of Israel": r"\bDaughters\s+of\s+Israel\b",
    "Hebra Kadisha / Cemetery": r"\bHe[bv]ra\s+Kad+isha\b|\bCemetery\s+Committee\b|\bCenter\s+Cemeteries\b",
    "Adult Education / Institute of Jewish Studies": r"\bAdult\s+Education\b|\bInstitute\s+of\s+Jewish\s+Studies\b",
    "Library": r"\bCenter\s+Library\b|\bLibrary\s+Committee\b",
    "Gift Shop": r"\bGift\s+Shop\b",
    "Golden Age Club": r"\bGolden\s+Age\b",
    "Couples Club / Parents Association": r"\bCouples\s+Club\b|\bParents\s+Association\b",
    "Hazak": r"\bHazak\b",
    "Hesed Committee": r"\bHesed\b",
    "Social Action / Social Justice": r"\bSocial\s+Action\b|\bSocial\s+Justice\b",
    "JJC Futures": r"\bJJC\s+Futures\b",
    "SoShul Network": r"\bSoShul\b",
    "Bowling League": r"\bBowling\s+League\b",
    "Basketball": r"\bBasketball\b",
    "Softball": r"\bSoftball\b",
    "Boy/Cub Pack 14": r"\bPack\s+14\b|\bTroop\s+14\b",
}

COMPILED = {k: re.compile(v, re.IGNORECASE if k not in ("ATID",) else 0) for k, v in ORGS.items()}


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())
    orgs_out: dict[str, dict] = {
        k: {"name": k, "appearances": []} for k in ORGS
    }
    for vol in volumes:
        vid = vol["vid"]
        per_org_pages: dict[str, list[int]] = {k: [] for k in ORGS}
        for rec in vol["page_index"]:
            seq = rec["seq"]
            p = TEXT_DIR / vid / f"{seq:05d}.txt"
            if not p.exists():
                continue
            text = p.read_text(encoding="utf-8")
            for key, rx in COMPILED.items():
                if rx.search(text):
                    per_org_pages[key].append(seq)
        for key, pages in per_org_pages.items():
            if pages:
                orgs_out[key]["appearances"].append(
                    {
                        "vid": vid,
                        "year": vol["year"],
                        "year_start": vol["year_start"],
                        "count": len(pages),
                        "pages": pages[:20],
                    }
                )

    result = sorted(orgs_out.values(), key=lambda o: -len(o["appearances"]))
    (JSON_DIR / "organizations.json").write_text(
        json.dumps(result, indent=1), encoding="utf-8"
    )
    for o in result:
        yrs = [a["year_start"] for a in o["appearances"] if a["year_start"]]
        if yrs:
            print(f"{o['name']:45} {len(o['appearances']):3} vols  {min(yrs)}–{max(yrs)}")


if __name__ == "__main__":
    main()
