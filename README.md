# L'Dor V'Dor — A Time Machine Through Jewish Jacksonville

An interactive archive built from 87 Jacksonville Jewish Center yearbooks
(1926–2019, 17,729 pages), digitized by the University of Florida
(UFDC bibid [AA00010733](https://ufdc.ufl.edu/AA00010733/00001)).

## Run it

```bash
cd jjc-history
python3 -m http.server 8417
# open http://127.0.0.1:8417/site/
```

Serve from the **project root** (not `site/`) so page-text excerpts can load
from `data/text/`. If a page text file is missing locally, the site falls
back to fetching the same text from UFDC. Page images are hot-loaded from
UFDC's image server and every citation deep-links to the original scan.

## What's inside

| View | What it does |
|---|---|
| **Timeline** | 25 curated milestones, 1853–2021, each labeled *yearbook evidence* vs *outside research*, with citation chips |
| **Time Machine** | Pick any of the 87 years: leadership that year, section map, organizations, advertisers, page thumbnails |
| **People & Threads** | 35,616-name index (search any name/surname); 11 curated documented threads |
| **Stories** | 7 curated exhibits (the 1958 bombing, the first yearbook, the move to Mandarin…) |
| **Then & Now** | Organization/program spans 1926–2019; longest-running advertisers |
| **Mysteries & Corrections** | 10 documented contradictions and open questions — displayed, not silently fixed |
| **Search** | Full-text search over all 17,729 pages (5.7 MB sharded index, loaded on demand) |
| **✦ Surprise me** | Weighted random jump to a story, thread, year, milestone page, or vintage ad |

## Pipeline (reproducible)

Run in order; each script's docstring explains it.

```
pipeline/01_extract.py            unzip, fix encodings (UTF-16 early volumes), volumes.json
pipeline/02_leadership.py         clergy/president candidates (regex, never published raw)
pipeline/03_orgs.py               organization timelines (controlled vocabulary)
pipeline/04_names.py              name index, sharded by surname initial
pipeline/05_ads.py                advertiser directories -> business longevity
pipeline/06_sections.py           printed-page offsets + TOC section maps
pipeline/07_search.py             full-text inverted index (base36 delta postings)
pipeline/08_curate.py             the curated dataset (presidents, clergy, events,
                                  threads, stories, mysteries) — every claim cited
pipeline/09_audit_citations.py    verifies every citation points at a page containing
                                  its evidence keyword; repairs or flags
pipeline/11_president_evidence.py semantic pass: full name adjacent to a standalone
                                  'President' title (excludes Vice-President bleed and
                                  'Mrs. <husband>' convention); manual pins for pages
                                  read by hand
pipeline/10_build_site_data.py    assembles site/data/
```

The audit chain ends at **265 citations, 0 unverified**. The leadership
dataset contains 45 presidential term records: 41 marked verified and four
transparently marked `printed-list` where stronger era evidence was not found.

## Publish with GitHub Pages

This repository is ready to publish as a framework-free static site:

1. Push the repository to GitHub.
2. Open **Settings → Pages**.
3. Select **Deploy from a branch**, choose `main`, and choose `/(root)`.

The root `index.html` redirects to `site/`, and `.nojekyll` tells GitHub Pages
to serve the archive directly. The original 48 MB extraction ZIP is kept out
of Git; the extracted page text and the data required by the website are
tracked.

## Provenance rules

- Yearbook facts carry `{vid, seq}` citations → UFDC page scans.
- Outside research (Wikipedia, ISJL encyclopedia, NPS, The Jaxson) is always
  labeled and linked, never blended silently.
- Same surname ≠ same family: name threads are labeled, relationships are
  asserted only when a page states them.
- Names appear as published; street addresses and phone numbers are never
  extracted into the dataset.
- Contradictions go to Mysteries & Corrections (e.g., UFDC's catalog labels
  volume 00075 "2007-2008" but its title page reads 2016-2017; two printed
  Past-Presidents lists disagree about Robert J. Gordon and Samuel "Bud"
  Shorstein, both of whom the era's own yearbooks show as Chairmen of the
  Board).

## Data layout

```
data/text/<vid>/<seq>.txt   normalized UTF-8 page text (17,729 pages)
data/json/                  full extraction outputs + curated dataset
site/                       the website (framework-free, no build step)
site/data/                  the slim JSON bundle the site loads (11.9 MB, lazy)
```
