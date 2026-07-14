#!/usr/bin/env python3
"""Cross-check the 2018-19 Past Presidents master list (vid 00077 seq 24-25,
OCR column-scrambled) against each era's own yearbook: does the claimed
president's surname appear near 'President' in the front matter of the
volumes covering the term?

Usage: python3 pipeline/verify_presidents.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "data" / "text"
JSON_DIR = ROOT / "data" / "json"

# name, term(s) as printed; scrambled entries carry a '?'
MASTER = [
    ("Max Frank", [(1901, 1904)]),
    ("H. Hammerman", [(1905, 1905)]),
    ("Isaac Davis", [(1906, 1910)]),
    ("Elias H. Pilton", [(1911, 1922)]),
    ("David Moskovitz", [(1923, 1926), (1938, 1939)]),
    ("Jacob Lapinsky", [(1927, 1927)]),
    ("Harry Finkelstein", [(1927, 1929)]),
    ("Max Rubin", [(1930, 1937)]),
    ("Abe Newman", [(1940, 1943)]),
    ("Harry Gendzier", [(1944, 1946)]),
    ("Joseph Hackel", [(1947, 1948)]),
    ("Harry Leff", [(1949, 1949)]),
    ("Philip Selber", [(1950, 1951), (1953, 1955)]),
    ("Philip Bork", [(1952, 1952)]),
    ("Ralph Mizrahi", [(1956, 1957)]),
    ("Burton Grossman", [(1958, 1960)]),
    ("Louis Safer", [(1961, 1962)]),
    ("Robert J. Gordon", [(1963, 1965)]),  # printed dates scrambled; testing 1963-65
    ("Jack Becker", [(1966, 1967)]),
    ("Nathan Friedlin", [(1968, 1969)]),
    ("Wilbur Margol", [(1970, 1971)]),
    ("Jack Shorstein", [(1972, 1974)]),
    ("Charles Mizrahi", [(1974, 1976)]),
    ("Sheldon Gendzier", [(1976, 1978)]),
    ("Lawrence DuBow", [(1978, 1980)]),  # scrambled cluster
    ("Samuel Shorstein", [(1978, 1980)]),  # scrambled cluster ("Bud")
    ("Nathan Krestul", [(1980, 1982)]),
    ("Sol Proctor", [(1982, 1984)]),
    ("Joseph Honigman", [(1984, 1986)]),
    ("Eugene Kornblum", [(1986, 1988)]),
    ("Marsha Pollock", [(1988, 1990)]),
    ("Michael Shorstein", [(2000, 2002)]),
    ("Philip Bloom", [(2002, 2004)]),
    ("Seeman Zimmerman", [(2004, 2006)]),
    ("Sandy Zimmerman", [(2006, 2008)]),
    ("Mitchell Levine", [(2008, 2010)]),
    ("Michael DuBow", [(2010, 2013)]),
    ("Fred Pozin", [(2013, 2015)]),
    ("Alyse Nathans", [(2015, 2017)]),
    ("David Bielski", [(2017, 2019)]),
]


def main() -> None:
    volumes = json.loads((JSON_DIR / "volumes.json").read_text())

    def vols_in(term):
        y0, y1 = term
        return [
            v for v in volumes
            if v["year_start"] and not (v["year_end"] < y0 or v["year_start"] > y1)
        ]

    results = []
    for name, terms in MASTER:
        surname = name.split()[-1]
        firstname = name.split()[0].rstrip(".")
        hits = []
        for term in terms:
            for v in vols_in(term):
                vid = v["vid"]
                for rec in v["page_index"][:45]:
                    seq = rec["seq"]
                    p = TEXT_DIR / vid / f"{seq:05d}.txt"
                    if not p.exists():
                        continue
                    text = p.read_text(encoding="utf-8")
                    if surname not in text:
                        continue
                    # surname within 250 chars of 'President'
                    for m in re.finditer(re.escape(surname), text):
                        lo = max(0, m.start() - 250)
                        window = text[lo : m.start() + 250]
                        if re.search(r"[Pp]resident", window) and not re.search(
                            r"[Vv]ice[- ]?[Pp]res", window[max(0, len(window)//2 - 60):len(window)//2 + 60]
                        ):
                            hits.append({"vid": vid, "year": v["year"], "seq": seq})
                            break
                    else:
                        continue
                    break
        status = "CONFIRMED" if hits else ("NO-VOLUMES" if not any(vols_in(t) for t in terms) else "UNCONFIRMED")
        results.append({"name": name, "terms": terms, "status": status, "evidence": hits[:4]})
        ev = f" e.g. {hits[0]['year']} seq{hits[0]['seq']}" if hits else ""
        print(f"{status:12} {name:24} {terms}{ev}")

    (JSON_DIR / "presidents_verification.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
