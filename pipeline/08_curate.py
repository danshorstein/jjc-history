#!/usr/bin/env python3
"""Phase B7: write the curated, citation-bearing dataset.

Everything here was verified by reading the cited pages (yearbook evidence)
or comes from labeled outside research. Yearbook citations: {vid, seq}.
Research citations: {title, url}. 'confidence' marks uncertain items.

Usage: python3 pipeline/08_curate.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "data" / "json"

# ---------------------------------------------------------------- research
RESEARCH = {
    "wikipedia": {
        "title": "Jacksonville Jewish Center — Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Jacksonville_Jewish_Center",
    },
    "isjl": {
        "title": "ISJL — Jacksonville, Florida Encyclopedia (Goldring/Woldenberg Institute of Southern Jewish Life)",
        "url": "https://www.isjl.org/florida-jacksonville-encyclopedia.html",
    },
    "nps": {
        "title": "Jacksonville Jewish Center — U.S. National Park Service",
        "url": "https://www.nps.gov/articles/000/jacksonville-jewish-center.htm",
    },
    "jaxson": {
        "title": "The Jaxson — Uncovering Jewish heritage sites in Jacksonville",
        "url": "https://www.thejaxsonmag.com/article/uncovering-jewish-heritage-sites-in-jacksonville/",
    },
    "ufdc": {
        "title": "UF Digital Collections — Jacksonville Jewish Center Yearbooks (AA00010733)",
        "url": "https://ufdc.ufl.edu/AA00010733/00001",
    },
    "jjc125": {
        "title": "JJC 125th Anniversary History Timeline (2026)",
        "note": "Institutional anniversary brochure; photographs supplied to this project on July 19, 2026.",
    },
}

# ---------------------------------------------------------------- presidents
# Sources: 1999-2000 Past Presidents list (00058 seq 51), 2018-19 list
# (00077 seq 24-25), 1998-2000 officers page (00058 seq 49), 2018-19
# executive board (00077 seq 23), plus per-era President's-Message pages.
L9900 = {"vid": "00058", "seq": 51, "note": "Past Presidents list, 1999-2000 yearbook"}
L1819A = {"vid": "00077", "seq": 24, "note": "Past Presidents list (part 1), 2018-19 yearbook"}
L1819B = {"vid": "00077", "seq": 25, "note": "Past Presidents list (part 2), 2018-19 yearbook"}

PRESIDENTS = [
    # (name, term_label, start, end, extra citations, note, confidence)
    ("Max Frank", "1901–1904", 1901, 1904, [{"vid": "00002", "seq": 28}], "Founding president. The 1926-27 yearbook reproduces the 1901 charter itself: 'until the first election under the charter, shall be Max Frank, President'.", "verified"),
    ("H. Hammerman", "1905", 1905, 1905, [], "Predates the yearbooks; as printed in later lists.", "printed-list"),
    ("Isaac Davis", "1906–1910", 1906, 1910, [{"vid": "00002", "seq": 29}], "Predates the yearbooks, but the 1926-27 volume's history essay names 'Davis, President'.", "verified"),
    ("Elias H. Pilton", "1911–1922", 1911, 1922, [{"vid": "00002", "seq": 29}], "The 1926-27 yearbook notes he served 'for nearly 20 years' as president.", "verified"),
    ("David Moscovitz", "1923–1926", 1923, 1926, [{"vid": "00002", "seq": 29}], "Named as sitting president in the first yearbook (1926-27).", "verified"),
    ("Jacob Lapinsky", "1927", 1927, 1927, [{"vid": "00002", "seq": 31}], None, "verified"),
    ("Harry Finkelstein", "1927–1929", 1927, 1929, [{"vid": "00002", "seq": 38}, {"vid": "00078", "seq": 6}], "Accepted the key at the 1928 building dedication; a 1975-76 retrospective calls him the Center's first president (i.e., first of the renamed Jacksonville Jewish Center).", "verified"),
    ("Max Rubin", "1930–1937", 1930, 1937, [{"vid": "00079", "seq": 2}], None, "verified"),
    ("David Moscovitz", "1938–1939", 1938, 1939, [{"vid": "00001", "seq": 14}], "Second service. The 1999-2000 list prints this term as 'David Moss'; the 1938-39 yearbook's president page reads DAVID MOSCOVITZ. See Mysteries.", "verified"),
    ("Abe Newman", "1940–1943", 1940, 1943, [{"vid": "00005", "seq": 5}], None, "verified"),
    ("Harry Gendzier", "1944–1946", 1944, 1946, [{"vid": "00007", "seq": 18}], None, "verified"),
    ("Joseph Hackel", "1947–1948", 1947, 1948, [{"vid": "00085", "seq": 15}], None, "verified"),
    ("Harry Leff", "1949", 1949, 1949, [{"vid": "00086", "seq": 37}], None, "verified"),
    ("Philip Selber", "1950–1951", 1950, 1951, [{"vid": "00009", "seq": 25}], "First of three separate terms.", "verified"),
    ("Philip Bork", "1952", 1952, 1952, [], "As printed in both Past-Presidents lists; his name appears on the 1953-54 Center Committee page (00012).", "printed-list"),
    ("Philip Selber", "1953–1955", 1953, 1955, [{"vid": "00012", "seq": 9}], "Second term. The 1953-54 officers block shows Selber as President with Robert J. Gordon as Vice President/Chairman.", "verified"),
    ("Ralph Mizrahi", "1956–1957", 1956, 1957, [{"vid": "00015", "seq": 14}], None, "verified"),
    ("Burton Grossman", "1958–1960", 1958, 1960, [{"vid": "00017", "seq": 19}], None, "verified"),
    ("Judge Louis Safer", "1961–1962", 1961, 1962, [{"vid": "00020", "seq": 15}], None, "verified"),
    ("Philip Selber", "1963–1965", 1963, 1965, [{"vid": "00022", "seq": 19}], "Third term. His 1963-64 message: 'When I wrote my first message as President some 12 years ago…'. The 2018-19 printed list scrambles this era (see Mysteries: Robert J. Gordon).", "verified"),
    ("Jack Becker", "1966–1967", 1966, 1967, [{"vid": "00024", "seq": 30}], None, "verified"),
    ("Nathan Freidlin", "1968–1969", 1968, 1969, [{"vid": "00027", "seq": 16}, {"vid": "00027", "seq": 34}], "Spelled FREIDLIN in the 1968-69 yearbook (signature and installation photo, March 10, 1968); later Past-Presidents lists print 'Friedlin'. His 1968-69 message notes the 'long line of distinguished Presidents… for the past 67 years' — corroborating the 1901 founding. Presidencies began in January in this era.", "verified"),
    ("Wilbur Margol", "1970–1971", 1970, 1971, [{"vid": "00029", "seq": 39}], None, "verified"),
    ("Jack Shorstein", "1972–1974", 1972, 1974, [{"vid": "00031", "seq": 31}], "The 1999-2000 list prints 1972-1973, the 2018-19 list 1972-1974; January-start terms make both readings possible. See Mysteries.", "verified"),
    ("Charles Mizrahi", "1974–1976", 1974, 1976, [{"vid": "00033", "seq": 13}], None, "verified"),
    ("Sheldon Gendzier", "1976–1978", 1976, 1978, [{"vid": "00035", "seq": 33}], None, "verified"),
    ("Lawrence DuBow", "1978–1980", 1978, 1980, [{"vid": "00037", "seq": 81}, {"vid": "00038", "seq": 228}], "Known as 'Laurie' in the yearbooks; his installation photos and signed President's Message confirm the term.", "verified"),
    ("Nathan Krestul", "1980–1982", 1980, 1982, [{"vid": "00038", "seq": 30}], "A Nathan Krestul served as assistant cantor of the Junior Congregation in 1941-42 (00005 seq 10) — probably the same person four decades earlier, not asserted.", "verified"),
    ("Sol Proctor", "1982–1984", 1982, 1984, [{"vid": "00042", "seq": 6}], None, "verified"),
    ("Dr. Joseph Honigman", "1984–1986", 1984, 1986, [{"vid": "00043", "seq": 22}], None, "verified"),
    ("Eugene Kornblum", "1986–1988", 1986, 1988, [{"vid": "00044", "seq": 39}], None, "verified"),
    ("Marsha Pollock", "1988–1990", 1988, 1990, [{"vid": "00048", "seq": 203}], "First woman in the Center's published presidential succession. Her signed President's Message appears in the 1989-90 yearbook.", "verified"),
    ("Jeffery Morris", "1990–1993", 1990, 1993, [L9900], "Missing from the OCR of the 2018-19 list; restored from the 1999-2000 list.", "verified"),
    ("Stuart Hecht", "1993–1996", 1993, 1996, [L9900], "Missing from the OCR of the 2018-19 list; restored from the 1999-2000 list.", "printed-list"),
    ("Evan Yegelwel", "1996–1998", 1996, 1998, [L9900, {"vid": "00058", "seq": 49}], "Chairman of the Board on the 1998-2000 officers page.", "verified"),
    ("Mark Shorstein", "1998–2000", 1998, 2000, [{"vid": "00058", "seq": 49}], "Named President on the 1998-2000 Center Officers page. As a teenager he was president of Jacksonville USY in 1972-73 (00032, seq 171 area) — a 26-year arc from youth leader to congregation president.", "verified"),
    ("Michael Shorstein", "2000–2002", 2000, 2002, [{"vid": "00059", "seq": 13}, L1819B], None, "verified"),
    ("Philip Bloom", "2002–2004", 2002, 2004, [{"vid": "00061", "seq": 19}, L1819B], None, "verified"),
    ("Seeman Zimmerman", "2004–2006", 2004, 2006, [{"vid": "00062", "seq": 32}, L1819B], None, "verified"),
    ("Sandy Zimmerman", "2006–2008", 2006, 2008, [{"vid": "00064", "seq": 24}, L1819B], None, "verified"),
    ("Dr. Mitchell Levine", "2008–2010", 2008, 2010, [{"vid": "00066", "seq": 25}, L1819B], None, "verified"),
    ("Michael DuBow", "2010–2013", 2010, 2013, [{"vid": "00069", "seq": 8}, L1819B], None, "verified"),
    ("Fred Pozin", "2013–2015", 2013, 2015, [{"vid": "00071", "seq": 24}, L1819B], None, "verified"),
    ("Alyse Nathans", "2015–2017", 2015, 2017, [{"vid": "00073", "seq": 21}, L1819B], None, "verified"),
    ("David Bielski", "2017–2019+", 2017, 2019, [{"vid": "00077", "seq": 23}], "Named President on the 2018-19 Executive Board page (the last yearbook in the collection).", "verified"),
]

# ---------------------------------------------------------------- clergy
CLERGY = [
    ("Rev. Benjamin Safer", "Spiritual leader, B'nai Israel", 1901, 1930,
     [{"vid": "00002", "seq": 44}],
     "Arrived c.1901-02 from Lithuania; never formally ordained, hence 'Reverend'. Also the city's first kosher butcher and mohel. Led the downtown B'nai Israel branch until 1930. (Outside research: ISJL.)",
     ["isjl"]),
    ("Rabbi Samuel Benjamin", "Rabbi", 1926, 1938,
     [{"vid": "00002", "seq": 29}, {"vid": "00078", "seq": 6}],
     "Elected April 1, 1926; a Jewish Theological Seminary graduate who brought Conservative Judaism and the synagogue-center model, leading the congregation into its 1928 Center building. End of tenure approximate (attested through the late 1930s).",
     ["isjl", "wikipedia"]),
    ("Rabbi Morris D. Margolis", "Rabbi", 1935, 1944,
     [{"vid": "00081", "seq": 4}, {"vid": "00004", "seq": 8}],
     "Attested in yearbooks from 1935-36 through 1943. Tenure bounds approximate.",
     []),
    ("Rabbi David H. Panitz", "Rabbi", 1945, 1947,
     [{"vid": "00008", "seq": 6}],
     "Attested 1945-1947. Tenure bounds approximate.",
     []),
    ("Rabbi Sanders A. Tofield", "Rabbi", 1947, 1960,
     [{"vid": "00086", "seq": 10}, {"vid": "00015", "seq": 12}],
     "Led the Center 1947 until his death in 1960; prominent in the Rabbinical Assembly; under his leadership the Center won the national Solomon Schechter Award for youth work (1952) and held Jacksonville's first Bat Mitzvah ceremonies. (Research: ISJL, NPS.)",
     ["isjl", "nps"]),
    ("Cantor Abraham Marton", "Cantor", 1946, 1980,
     [{"vid": "00084", "seq": 8}, {"vid": "00038", "seq": 12}],
     "One of the longest clergy tenures in Center history — attested continuously from 1946-47 through 1979-80, with emeritus and memorial mentions into the 2010s.",
     []),
    ("Rabbi Moshe V. Goldblum", "Rabbi", 1961, 1963,
     [{"vid": "00020", "seq": 12}],
     "Attested 1961-1963. Tenure bounds approximate.",
     []),
    ("Rabbi Arnold S. Turetsky", "Rabbi", 1963, 1967,
     [{"vid": "00023", "seq": 10}],
     "Attested 1963-1967. Tenure bounds approximate.",
     []),
    ("Rabbi Jerome Lipnick", "Rabbi", 1966, 1970,
     [{"vid": "00026", "seq": 12}],
     "Attested 1966-1970. Tenure bounds approximate.",
     []),
    ("Rabbi Dov Peretz Elkins", "Rabbi", 1971, 1973,
     [{"vid": "00030", "seq": 12}],
     "Attested 1971-1973; a prolific author within the Conservative movement.",
     []),
    ("Rabbi David Gaffney", "Rabbi", 1973, 2005,
     [{"vid": "00032", "seq": 9}, {"vid": "00058", "seq": 5}],
     "Attested from 1973-74 (already leading a Soviet-Jewry discussion for the Charles Palot Club) through the 2000s; senior rabbi for roughly three decades, later emeritus (mentions continue to 2015-16).",
     []),
    ("Rabbi Dov Kentof", "Rabbi, Director of Education & Youth", 1980, 2000,
     [{"vid": "00058", "seq": 3}],
     "The 1999-2000 yearbook is dedicated to him 'who, for 20 years, has worked tirelessly on behalf of the youth and families of our congregation' — with a commemorative section of tributes.",
     []),
    ("Cantor Joel Fox", "Cantor", 1993, 1996,
     [{"vid": "00052", "seq": 10}],
     "Attested 1993-1996. Tenure bounds approximate.",
     []),
    ("Cantor Aron Heller", "Cantor", 1999, 2002,
     [{"vid": "00058", "seq": 47}],
     "Attested 1999-2002. Tenure bounds approximate.",
     []),
    ("Rabbi Stephen Grundfast", "Rabbi", 2002, 2004,
     [{"vid": "00061", "seq": 10}],
     "Attested 2002-2004, between Rabbi Gaffney's senior tenure and Rabbi Lubliner's arrival.",
     []),
    ("Rabbi Jonathan Lubliner", "Senior Rabbi", 2004, 2019,
     [{"vid": "00063", "seq": 8}, {"vid": "00077", "seq": 5}],
     "Attested from 2004-05 through the final yearbook in the collection (2018-19); still senior rabbi today. (Research: Wikipedia.)",
     ["wikipedia"]),
    ("Cantor Yitzhak Ben-Moshe", "Cantor", 2006, 2008,
     [{"vid": "00065", "seq": 10}],
     "Attested 2006-2008. Tenure bounds approximate.",
     []),
    ("Hazzan Jesse Holzer", "Hazzan (Cantor)", 2008, 2019,
     [{"vid": "00067", "seq": 10}, {"vid": "00077", "seq": 5}],
     "Attested 2008-09 through 2018-19.",
     []),
    ("Rabbi Jesse Olitzky", "Associate Rabbi", 2011, 2014,
     [{"vid": "00070", "seq": 8}],
     "Attested 2011-2014.",
     []),
    ("Rabbi Howard Tilman", "Associate Rabbi", 2014, 2018,
     [{"vid": "00073", "seq": 9}, {"vid": "00075", "seq": 5}],
     "Attested 2014-2018.",
     []),
]

# ---------------------------------------------------------------- events
EVENTS = [
    # year, title, body, kind: yearbook|research|both, citations, research keys
    (1853, "Jacksonville's first known Jewish family arrives",
     "The Dzialynski family arrives from Prussian Poland — the city's first known Jews. By 1857 the community establishes a Jewish section in the Old City Cemetery, Florida's first permanent Jewish organization.",
     "research", [], ["isjl"]),
    (1882, "Congregation Ahavath Chesed chartered",
     "Jacksonville's first congregation (and Florida's second) is chartered; it affiliates Reform in the 1890s — prompting traditionalist families to organize on their own.",
     "research", [], ["isjl"]),
    (1901, "Hebrew Orthodox Congregation B'nai Israel incorporated",
     "Five Orthodox families, by then numbering about forty families, formally organize B'nai Israel. The charter was approved on December 5 and recorded the next day, December 6. Max Frank is named first president; the incorporators include Samuel Controvitz, E. H. Pilton, Morris Wexler, A. Hirsch, Alex Ossinsky, and Louis Rosenstein. The Center's anniversary timeline identifies many of the families as immigrants from Pušalotas, Lithuania.",
     "both", [{"vid": "00002", "seq": 28}], ["jjc125", "isjl"]),
    (1907, "A synagogue in LaVilla",
     "With membership at seventy-five, B'nai Israel begins building at Jefferson and Duval Streets in LaVilla. The 1907 building campaign and a 1909 completion/dedication describe successive stages of the same project, rather than competing dates.",
     "both", [{"vid": "00002", "seq": 28}], ["jjc125", "isjl"]),
    (1914, "The YMHA is founded",
     "The Young Men's Hebrew Association organizes in LaVilla. By 1926-27 the first yearbook is arguing forcefully that 'an adequate Y building be erected in this City.'",
     "both", [{"vid": "00002", "seq": 44}], ["isjl"]),
    (1926, "The Conservative turn — Rabbi Samuel Benjamin elected",
     "On April 1, 1926, the congregation elects Rabbi Samuel Benjamin, a Jewish Theological Seminary graduate. He brings the 'synagogue-center' vision: one roof for worship, school, gym, and social life. The religious school is reorganized in May 1926 and registers 125 pupils, running straight through the summer.",
     "yearbook", [{"vid": "00002", "seq": 30}, {"vid": "00002", "seq": 32}], ["isjl"]),
    (1927, "A new Center, and a surviving Year Book",
     "The congregation purchases land at Third and Silver Streets and adopts the Jacksonville Jewish Center identity. Its 1926-27 (5687) volume calls itself a 'first attempt to produce a Year Book.' The 125th-anniversary timeline adds an important qualification: earlier editions dating to 1902 were largely congregational directories, while it identifies 1935 as the first yearbook in the form recognized today.",
     "both", [{"vid": "00002", "seq": 5}, {"vid": "00002", "seq": 30}], ["jjc125"]),
    (1928, "Dedication at Third & Silver",
     "The new Center building in Springfield is dedicated with a full program: Rabbi Samuel Benjamin, Cantor Aaron I. Edgar, the YMHA Orchestra, greetings from every Jewish organization in town, and the presentation of the key from Lionel D. Joel to president Harry Finkelstein. The congregation formally becomes the Jacksonville Jewish Center.",
     "yearbook", [{"vid": "00078", "seq": 6}], ["wikipedia"]),
    (1931, "The missing years",
     "No yearbooks survive for 1931-1933 — the depths of the Great Depression, when Jacksonville Jewish institutions struggled (a sister congregation lost ~140 dues-paying families in 1930). Whether the books were never published or simply never digitized is an open question.",
     "both", [], ["isjl"]),
    (1938, "Ten years in the building",
     "The 1938-39 yearbook marks 'the tenth anniversary of this institution' with a banquet at the Seminole Hotel, guest speakers, and — in the same pages — anxious attention to events in Europe.",
     "yearbook", [{"vid": "00001", "seq": 44}], []),
    (1946, "River Garden Hebrew Home founded",
     "The community establishes River Garden Hebrew Home for the Aged on the St. Johns River; the Center's yearbooks report on it faithfully for the next seventy years — from an antebellum mansion housing 10 residents to a modern complex serving 175.",
     "yearbook", [{"vid": "00032", "seq": 18}], []),
    (1947, "Rabbi Sanders A. Tofield arrives",
     "A scholar prominent in the Conservative movement's Rabbinical Assembly, Tofield leads the Center until his death in 1960.",
     "both", [{"vid": "00086", "seq": 21}], ["isjl", "nps"]),
    (1948, "The first Bat Mitzvah ceremony",
     "On April 9, Bryna Lee Datz and Judy Herschaft participate in the Center's first Bat Mitzvah ceremony, held during a late Friday-evening program — an early milestone in women's participation in congregational life.",
     "research", [], ["jjc125"]),
    (1950, "The community-center building rises",
     "A new community center building (1950) and later classroom annex give the Springfield campus 19 classrooms, chapel, library, social hall, auditorium/gymnasium, banquet facility — even a bridal lounge.",
     "research", [], ["nps"]),
    (1952, "National recognition for youth work",
     "On May 19, 1952 the Center receives the National United Synagogue Solomon Schechter Award for its youth program — the rabbi's acceptance address fills the yearbook's opening pages, and a Youth Center is dedicated the same year.",
     "yearbook", [{"vid": "00087", "seq": 29}, {"vid": "00087", "seq": 52}], []),
    (1958, "Bombed on Monday — groundbreaking on Friday",
     "On April 28, 1958, dynamite set by 'unapprehended individuals' damages the synagogue; the James Weldon Johnson school is bombed the same night. Four days later, on May 2, the congregation goes ahead with groundbreaking ceremonies for its new school building, photographing the damage and the shovels side by side. 'The Council gave the community the type of leadership and solidarity needed in such a crisis… a pattern for the nation.'",
     "yearbook", [{"vid": "00017", "seq": 27}, {"vid": "00017", "seq": 131}], ["isjl", "wikipedia"]),
    (1961, "The Foundation School opens",
     "The Center opens the Foundation School with one first-grade class. In 1966 it is renamed the Solomon Schechter Day School; the 1965-66 yearbook documents the expansion through fifth grade. This corrects the archive's earlier use of the first available yearbook evidence as a founding date.",
     "both", [{"vid": "00024", "seq": 98}], ["jjc125"]),
    (1972, "Beth Shalom splits off",
     "Thirteen families leave to found Beth Shalom Congregation, seeking more egalitarian practice. Nearly forty years later, in 2011, the two congregations re-merge.",
     "research", [], ["isjl"]),
    (1972, "Rabbi David Gaffney begins a 29-year rabbinate",
     "Rabbi David Gaffney joins the Center, beginning its longest rabbinate. Across twenty-nine years, he leads an expansion of early-childhood, Hebrew high-school, day-school, youth, adult-education, and cultural offerings.",
     "research", [], ["jjc125"]),
    (1973, "Groundbreaking for the Mandarin campus",
     "On September 16, the Center breaks ground for the new synagogue complex. In 1976, a procession carries the Torah scrolls from Third and Silver to the new Mandarin home.",
     "research", [], ["jjc125"]),
    (1976, "The move to Mandarin",
     "'…whether at 3rd & Silver Streets or 10101 San Jose Blvd., it is the congregation… it is as it has always been.' After a decade of planning and a building campaign, the Center moves to its present campus at San Jose Blvd. and Crown Point Road. The old Springfield building later houses a Job Corps center (1979-2005).",
     "yearbook", [{"vid": "00034", "seq": 271}], ["wikipedia", "nps"]),
    (1978, "Rabbi Dov Kentof joins the Center",
     "Rabbi Dov Kentof is hired as Youth and Education Director. The 1999-2000 yearbook, dedicated to him, confirms two decades of service; the anniversary timeline corrects the previous 1980 arrival date.",
     "both", [{"vid": "00058", "seq": 3}], ["jjc125"]),
    (1982, "Ami Shamir's Ark is installed",
     "A major building expansion includes the installation of the Ami Shamir-designed Ark in the sanctuary.",
     "research", [], ["jjc125"]),
    (1988, "A woman leads the Center",
     "Marsha Pollock becomes the first woman in the Center's published presidential succession (1988-1990).",
     "yearbook", [{"vid": "00048", "seq": 203}], []),
    (1996, "Performing Artists Series begins",
     "Debbie Friedman inaugurates the Jacksonville Jewish Center's Performing Artists Series, beginning a decade-plus program of Jewish music, culture, and artistry.",
     "research", [], ["jjc125"]),
    (1999, "Rabbi Kentof retires; a school endowment begins",
     "Rabbi Dov Kentof retires after two decades of youth and education work. The Esther Galinsky bequest also establishes the foundation for the Galinsky Academy's educational programs.",
     "research", [], ["jjc125"]),
    (2001, "Centennial",
     "The 2001-02 yearbook celebrates 100 years: 'Jacksonville Jewish Center Centennial Celebration 1901-2001.' That June, the congregation also honors Rabbi Gaffney as he steps down after twenty-nine years and establishes the Rabbi David Gaffney Leadership in Education Award.",
     "both", [{"vid": "00060", "seq": 5}], ["jjc125"]),
    (2004, "Rabbi Jonathan Lubliner arrives",
     "Rabbi Jonathan Lubliner becomes the Center's spiritual leader, beginning a period of renewed energy, scholarship, and community engagement.",
     "research", [], ["jjc125"]),
    (2005, "The Martin J. Gottlieb Day School",
     "The day school is renamed for Martin J. Gottlieb; in 2012 the Center's schools unite under the Galinsky Academy umbrella — DuBow Preschool, Gottlieb Day School, Selevan Religious School, and Setzer Youth Education.",
     "yearbook", [{"vid": "00075", "seq": 5}], []),
    (2007, "The Center adopts egalitarian practice",
     "After a fall 2006 study process, the Board approves egalitarian practice in January. At the February 17 inaugural service, Tania Nogelwell leads Shacharit and Lois Tompkins davens Musaf and is counted in the minyan.",
     "research", [], ["jjc125"]),
    (2011, "Fire in Springfield; a family reunited",
     "Fire damages the long-vacant original building at Third & Silver (later demolished). The same year, Beth Shalom Congregation re-merges with the Center and brings a Holocaust Torah — a lasting symbol of remembrance and continuity.",
     "research", [], ["jjc125", "wikipedia", "isjl"]),
    (2017, "The Center's first female rabbi",
     "Assistant Rabbi Shira Rosenblum joins the Center as its first female rabbi.",
     "research", [], ["jjc125"]),
    (2018, "The preschool is renamed for Laurie DuBow",
     "The Center celebrates 75 years of its preschool program. Previously renamed DuBow Preschool, it is renamed Laurie Preschool in 2024 to honor Laurie DuBow, former congregation president and family patriarch.",
     "research", [], ["jjc125"]),
    (2020, "Livestream worship expands access",
     "During the COVID-19 epidemic, the Center installs a livestream system that enables members to join services and lifecycle moments from home; the system remains an accessibility and connection tool beyond the pandemic.",
     "research", [], ["jjc125"]),
    (2021, "On the National Register",
     "The Springfield Jacksonville Jewish Center site is added to the National Register of Historic Places, recognizing its significance to Jacksonville's Jewish community.",
     "research", [], ["nps", "wikipedia"]),
    (2023, "Nashuvah High Holiday service begins",
     "The Center introduces Nashuvah, an alternative High Holiday service offered during Rosh Hashanah and Yom Kippur alongside the sanctuary service.",
     "research", [], ["jjc125"]),
    (2026, "125 years",
     "On January 31, 2026, the Jacksonville Jewish Center celebrates its 125th anniversary — an occasion honoring generations of faith, resilience, learning, connection, and communal responsibility.",
     "research", [], ["jjc125"]),
]

# ---------------------------------------------------------------- threads
THREADS = [
    {
        "id": "marton",
        "title": "Cantor Abraham Marton — the voice of half a century",
        "kind": "person",
        "summary": "Attested in the yearbooks continuously from 1946-47 through 1979-80 as the Center's cantor, with emeritus and memorial mentions into the 2010s. Generations of b'nai mitzvah learned their haftarah from him.",
        "query": "Marton",
        "citations": [{"vid": "00084", "seq": 8}, {"vid": "00015", "seq": 14}, {"vid": "00038", "seq": 12}],
        "caution": None,
    },
    {
        "id": "gaffney",
        "title": "Rabbi David Gaffney — from Soviet-Jewry phone calls to emeritus",
        "kind": "person",
        "summary": "First attested in 1973-74 leading a Charles Palot Club discussion on Soviet Jewry 'topped off by a phone call to a Soviet Jew in Moscow'; senior rabbi through three decades; mentions continue past 2010.",
        "query": "Gaffney",
        "citations": [{"vid": "00032", "seq": 9}, {"vid": "00058", "seq": 5}],
        "caution": None,
    },
    {
        "id": "shorstein",
        "title": "The Shorstein name — youth president to president, and beyond",
        "kind": "surname",
        "summary": "The 1972-73 yearbook alone contains three Shorstein presidencies: Jack signing the synagogue president's message, Mark leading Jacksonville USY, and Michael leading a youth group. Mark became Center president in 1998, Michael in 2000 — and the 2018-19 board still lists three Shorsteins serving at once.",
        "query": "Shorstein",
        "citations": [{"vid": "00031", "seq": 31}, {"vid": "00032", "seq": 171}, {"vid": "00058", "seq": 49}, {"vid": "00077", "seq": 22}],
        "caution": "Shared surname does not by itself establish family relationships; the yearbook pages cited document offices held, not genealogy.",
    },
    {
        "id": "krestul",
        "title": "Nathan Krestul — junior cantor, 1941; president, 1980",
        "kind": "person-probable",
        "summary": "In 1941-42 a boy named Nathan Krestul served as assistant cantor of the Junior Congregation. In 1980-82 a Nathan Krestul served as Center president. Four decades apart, very likely the same person — marked probable, not certain.",
        "query": "Krestul",
        "citations": [{"vid": "00005", "seq": 10}, {"vid": "00077", "seq": 24}],
        "caution": "Identity across 40 years is probable but not explicitly stated in the sources.",
    },
    {
        "id": "slott",
        "title": "Blanche Slott — the artist on the cover",
        "kind": "person",
        "summary": "Encouraging the Palot Club in 1973-74; painting Rabbi Kentof's tribute portrait for the 1999-2000 cover; and honored posthumously when the 2016-17 yearbook used 'a piece of art Blanche Slott created many years ago — may her memory be for a blessing.' The Slotts were among the founding families from Pušalotas, Lithuania.",
        "query": "Slott",
        "citations": [{"vid": "00032", "seq": 9}, {"vid": "00058", "seq": 3}, {"vid": "00075", "seq": 5}],
        "caution": "The link between artist Blanche Slott and the founding Slott families is contextual (research), not stated in the yearbooks.",
    },
    {
        "id": "setzer",
        "title": "The Setzer name — from a 1958 groundbreaking shovel to a named school",
        "kind": "surname",
        "summary": "Ben Setzer broke ground for the new school building four days after the 1958 bombing. Sixty years later, 'Setzer Youth Education' is one of the Galinsky Academy's four schools, and Ben & Leonard Setzer appear across decades of officer pages.",
        "query": "Setzer",
        "citations": [{"vid": "00017", "seq": 27}, {"vid": "00058", "seq": 49}, {"vid": "00077", "seq": 5}],
        "caution": "Shared surname; family relationships not asserted.",
    },
    {
        "id": "dubow",
        "title": "The DuBow name — two presidents and a preschool",
        "kind": "surname",
        "summary": "Lawrence DuBow (president 1978-80), Michael DuBow (president 2010-13), and the DuBow Preschool carrying the name into the Galinsky Academy era.",
        "query": "DuBow",
        "citations": [{"vid": "00077", "seq": 24}, {"vid": "00069", "seq": 8}, {"vid": "00075", "seq": 5}],
        "caution": "Shared surname; family relationships not asserted.",
    },
    {
        "id": "gendzier",
        "title": "The Gendzier name — presidents a generation apart",
        "kind": "surname",
        "summary": "Harry Gendzier (president 1944-46) steered the Center through the war years; Sheldon Gendzier (president 1976-78) presided over the first years in Mandarin; Gendziers appear on boards and committee pages in nearly every decade of the collection.",
        "query": "Gendzier",
        "citations": [{"vid": "00007", "seq": 18}, {"vid": "00035", "seq": 33}],
        "caution": "Shared surname; family relationships not asserted.",
    },
    {
        "id": "pack14",
        "title": "Pack & Troop 14 — ninety years of scouting",
        "kind": "organization",
        "summary": "Boy Scout Troop/Cub Pack 14 appears in 86 of the 87 yearbooks, from 1926 to 2018 — one of the longest continuously documented programs in the collection.",
        "query": "Pack 14",
        "citations": [{"vid": "00024", "seq": 122}, {"vid": "00058", "seq": 47}],
        "caution": None,
    },
    {
        "id": "palot",
        "title": "The Charles Palot Club — a memorial that became a movement",
        "kind": "organization",
        "summary": "A USY youth club named in memory of Charles Palot, appearing in the yearbooks from 1950 through the 2010s — Jewish Jeopardy, aggression labs, interfaith-dating debates, Soviet-Jewry activism, and a phone call to Moscow.",
        "query": "Palot",
        "citations": [{"vid": "00032", "seq": 9}],
        "caution": None,
    },
    {
        "id": "kuhn",
        "title": "Kuhn Flowers — 62 years on the back pages",
        "kind": "business",
        "summary": "The longest-running advertisers are a history of Jacksonville commerce: Kuhn Flowers (1951-2013), Worman's Bakery (1941-1977), American National Bank (1946-1997), Mendelson Printing — which printed the very first yearbook in 1927 — and dozens more.",
        "query": "Kuhn Flowers",
        "citations": [{"vid": "00011", "seq": 155}, {"vid": "00072", "seq": 69}, {"vid": "00002", "seq": 47}],
        "caution": None,
    },
]

# ---------------------------------------------------------------- stories
STORIES = [
    {
        "id": "1958-bombing",
        "title": "Four Days in the Spring of 1958",
        "deck": "A dynamite blast, an unshaken congregation, and a groundbreaking that went ahead on schedule.",
        "body": [
            "On the night of April 28, 1958, dynamite exploded at the Jacksonville Jewish Center's Springfield building. The same night, a bomb went off at the James Weldon Johnson school. Threatening calls came from a group calling itself the 'Confederate Underground.' The Center's administrative director told reporters the congregation was baffled to be targeted: 'The subject [of integration] has never even come up in our congregation.'",
            "The yearbook's own account is astonishing for what it does next. It reports the bombing in one breath — 'by unapprehended individuals' — and in the next describes the groundbreaking ceremonies for the new school building held on May 2nd, four days later. The photographs sit side by side on the page: the damaged building, the crater near the entrance, a neighboring house with its windows blown out — and Mr. Ben Setzer, shovel in hand, breaking ground for classrooms.",
            "The Jewish Community Council's page that year reads: 'Faced with the bombing of the Jacksonville Jewish Center, the Council gave the community the type of leadership and solidarity needed in such a crisis. The manner in which every Jewish organization in Jacksonville supported the Council has set a pattern for the nation.'",
            "Sixty-three years later, in 2021, the building those classrooms were added to was placed on the National Register of Historic Places.",
        ],
        "citations": [{"vid": "00017", "seq": 27}, {"vid": "00017", "seq": 131}],
        "research": ["isjl", "wikipedia", "nps"],
    },
    {
        "id": "first-yearbook",
        "title": "'This First Attempt'",
        "deck": "The 1926-27 yearbook that started it all — a community arguing itself into existence.",
        "body": [
            "The first yearbook (5687 / 1926-27) is less a scrapbook than a manifesto. Its foreword announces 'this first attempt to produce a Year Book for the Jacksonville Jewish Center' and promises 'the clearest statement possible, under the circumstances, of the community's belongings.'",
            "Inside is a community taking stock: Rabbi Samuel Benjamin, elected April 1, 1926, fresh from the Jewish Theological Seminary; a religious school reorganized in May 1926 that registered 125 pupils and ran straight through the summer — 'probably the only school in the country which did'; a Girl Scout troop organized that June; and an exasperated essay demanding a proper YMHA building: 'if it cannot be erected in any other manner then let some one invent it.'",
            "The book even audits communal generosity — noting the entire community 'gave no more than $2,000' for all Jewish education, Sunday school, Yiddish school and private tutoring included — and finds 'a reinvigorated Jewish community conscious of its great responsibilities.'",
            "Two years later the congregation would dedicate its grand new building at Third & Silver and formally take the name it had already given its yearbook.",
        ],
        "citations": [{"vid": "00002", "seq": 5}, {"vid": "00002", "seq": 30}, {"vid": "00002", "seq": 32}, {"vid": "00002", "seq": 44}],
        "research": ["isjl"],
    },
    {
        "id": "school-that-grew",
        "title": "The School That Kept Growing",
        "deck": "From 125 summer pupils in 1926 to a four-school academy — one unbroken educational thread.",
        "body": [
            "In May 1926 the Center reorganized its religious school; 125 pupils registered, and it ran through the summer. In the 1950s came the Foundation School, then the Solomon Schechter Day School — by 1965-66 'a graded secular and Hebrew School, 1st through 5th grade.'",
            "The 1963-64 president's message names education as the engine of everything: 'Had our congregation been content with its educational system of ten years ago, there would today be no Foundation School, no Hebrew High School, no Ramah program, no well attended junior congregation system…'",
            "In 2005 the day school was renamed for Martin J. Gottlieb; in 2012 the Center's schools united as the Galinsky Academy — DuBow Preschool, Martin J. Gottlieb Day School, Bernard & Alice Selevan Religious School, and Setzer Youth Education. Nearly a century after those first summer sessions, the 2018-19 yearbook devotes almost forty pages to the academy's classrooms.",
        ],
        "citations": [{"vid": "00002", "seq": 32}, {"vid": "00024", "seq": 98}, {"vid": "00022", "seq": 19}, {"vid": "00077", "seq": 5}],
        "research": [],
    },
    {
        "id": "usy-to-president",
        "title": "The Youth President Who Came Back",
        "deck": "In 1973, Mark Shorstein signed the USY page as 'Pres. - Jax., USY '72-73.' In 1998 he signed the whole yearbook.",
        "body": [
            "Open the 1972-73 yearbook and count the Shorstein presidents. On the officers page of a youth group kneels 'Michael Shorstein, President.' A USY page lists 'President — Mark Shorstein.' And at the bottom of the synagogue president's message: 'Sincerely, Jack F. Shorstein, President.' Three presidencies, one surname, one book.",
            "The 1973-74 yearbook carries Mark's message to Jacksonville USY — a meditation on apathy ('there is one expression in the English language that is more obscene than any four-letter word I know: \"So what!!\"') signed 'Pres. - Jax., USY, '72-73.'",
            "Twenty-six years later, the 1998-2000 officers page reads: 'Mark Shorstein, President' — and two years after that, 'Michael Shorstein, President.' The teenagers had grown into the office their namesake signed in 1973. The yearbooks document the offices, not the family tree — but the arc from youth page to front page is all there in print.",
            "He is not alone. The same officer pages show a Nathan Krestul as president in 1980-82; a Nathan Krestul appears in 1941-42 as the twelve-ish assistant cantor of the Junior Congregation. Across the collection, the yearbooks quietly document children growing into the leaders who sign the front pages.",
        ],
        "citations": [{"vid": "00031", "seq": 8}, {"vid": "00031", "seq": 159}, {"vid": "00031", "seq": 246}, {"vid": "00032", "seq": 171}, {"vid": "00058", "seq": 49}, {"vid": "00005", "seq": 10}],
        "research": [],
    },
    {
        "id": "move-to-mandarin",
        "title": "The Long Goodbye to Third & Silver",
        "deck": "'We pivot to look ahead — to go forward into a new building.'",
        "body": [
            "For nearly fifty years the Center's address was Third & Silver Streets, Springfield: the 1928 sanctuary, the 1950 community building, the classrooms begun days after the 1958 bombing. By the 1970s the community had moved south, and the yearbooks fill with building-fund appeals: 'What is your fair share gift? … You must make a gift greater than you ever thought would be necessary.'",
            "The 1975-76 Sisterhood page captures the moment of departure: 'We look back at the spiritual home that has served us so well for so long. And then, with a sigh, we pivot to look ahead — to go forward into a new building — with plans for our growth… whether at 3rd & Silver Streets or 10101 San Jose Blvd., it is the congregation — the Sisterhood — the entire membership — it is as it has always been.'",
            "The official move came in 1976. The Springfield building became a Job Corps center for a quarter century, was damaged by fire in 2011 and largely demolished — and in 2021 was honored on the National Register of Historic Places.",
        ],
        "citations": [{"vid": "00034", "seq": 37}, {"vid": "00034", "seq": 271}],
        "research": ["wikipedia", "nps", "jaxson"],
    },
    {
        "id": "women-of-the-center",
        "title": "From the Gallery to the Presidency",
        "deck": "The evolution of women's participation, told by the yearbooks themselves.",
        "body": [
            "The 2007-08 yearbook put the whole story on its cover, in a drawing by Raymond Cohen: 'In my grandmother's day, women wore lace scarves in shul. The emancipated women of my generation went bareheaded. Now, the properly dressed Bat Mitzvah wears a kippah and talit and even wraps tefillin.'",
            "The cover essay traces the arc: a first synagogue with 'a gallery reserved for women'; mixed seating with the move to Third & Silver and the Conservative movement; women entering corporate leadership in the 1950s; Bat Mitzvah accepted alongside Bar Mitzvah; women called to the Torah by century's end. The Center's 125th-anniversary timeline dates its first Bat Mitzvah ceremony to April 9, 1948, with Bryna Lee Datz and Judy Herschaft.",
            "The yearbooks supply the punctuation: 'Bar and Bas Mitzvahs' as a section heading by 1963-64; Sisterhood pages that evolve from 'Mrs. Husband's Name' to women's own names; and in 1988, Marsha Pollock's signature at the bottom of the President's Message — the first woman in the Center's published presidential succession.",
        ],
        "citations": [{"vid": "00066", "seq": 5}, {"vid": "00022", "seq": 9}, {"vid": "00048", "seq": 203}],
        "research": ["nps", "jjc125"],
    },
    {
        "id": "moscow-call",
        "title": "A Phone Call to Moscow",
        "deck": "How world Jewry's struggles echoed through a Jacksonville youth club.",
        "body": [
            "In the 1973-74 yearbook, the Charles Palot Club — a USY youth club named for a member of the congregation — reports a season of 'Jewish Jeopardy,' a swim party, an 'Aggression Lab,' a dinner discussion on interfaith dating… and 'a discussion on Soviet Jewry led by Rabbi David Gaffney topped off by a phone call to a Soviet Jew in Moscow.'",
            "The yearbooks regularly collapse the distance between Jacksonville and the wider Jewish world. In 1963 the rabbi's annual message was written on a sweltering bus from Eilat to Mitzpeh Ramon ('I am writing and riding in a dry Negev heat'); the 1938-39 volume marks the building's tenth anniversary while tracking events in Europe; UJA and Israel Bond drives march through the decades of back pages.",
            "A youth club's long-distance phone call, preserved in a yearbook: the Cold War, the Soviet Jewry movement, and a Jacksonville teenager's Sunday evening, all on one page.",
        ],
        "citations": [{"vid": "00032", "seq": 9}, {"vid": "00022", "seq": 15}],
        "research": [],
    },
]

# ---------------------------------------------------------------- mysteries
MYSTERIES = [
    {
        "id": "gordon-presidency",
        "title": "Was Robert J. Gordon ever president?",
        "status": "resolved-probable",
        "body": "The 2018-19 Past Presidents list prints 'Robert J. Gordon* 1953-1955.' But the 1999-2000 list does not include him at all; the 1953-54 yearbook's officers block shows Philip Selber as President with Gordon as Vice President; and Gordon's own 1975-76 memorial tribute says he 'formerly served as Treasurer, Chairman of the Board, Chairman of the Building Fund' — with no mention of the presidency. Verdict: the 2018-19 entry appears to be an error (possibly a scrambled column in print or in transcription).",
        "citations": [{"vid": "00077", "seq": 24}, {"vid": "00058", "seq": 51}, {"vid": "00012", "seq": 11}, {"vid": "00034", "seq": 141}],
    },
    {
        "id": "moss-moscovitz",
        "title": "'David Moss' or David Moscovitz?",
        "status": "resolved-probable",
        "body": "For the 1938-39 presidential term, the 1999-2000 list prints '*David Moss' while the 2018-19 list prints 'David Moskovitz 1923-1926; 1938-1939.' The 1938-39 yearbook itself shows DAVID MOSCOVITZ delivering the president's message. Verdict: 'David Moss' is almost certainly a truncation of Moscovitz (whose name is also spelled Moskovitz across sources). Note there was also a distinct 'Rudy Moss' family in the congregation, so the truncation matters.",
        "citations": [{"vid": "00058", "seq": 51}, {"vid": "00077", "seq": 24}, {"vid": "00001", "seq": 14}],
    },
    {
        "id": "shorstein-term",
        "title": "Did Jack Shorstein's presidency end in 1973 or 1974?",
        "status": "open",
        "body": "The 1999-2000 list prints 'Jack Shorstein 1972-1973'; the 2018-19 list prints '1972-1974.' Both lists agree Charles Mizrahi served 1974-1976. Presidencies in this era began in January (per the 1968-69 president's message), so the discrepancy may be a counting convention — but the two printed sources genuinely disagree.",
        "citations": [{"vid": "00058", "seq": 51}, {"vid": "00077", "seq": 24}, {"vid": "00027", "seq": 16}],
    },
    {
        "id": "mislabeled-volume",
        "title": "The yearbook cataloged under the wrong decade",
        "status": "resolved",
        "body": "UFDC catalogs volume 00075 as '2007-2008' — duplicating volume 00066. Its title page reads 'Jacksonville Jewish Center Yearbook 2016-2017 5777,' and its contents (Rabbi Tilman, Galinsky Academy, Crown Point Road address) confirm the later date. This archive treats it as 2016-17, filling what would otherwise be a gap in the run.",
        "citations": [{"vid": "00075", "seq": 1}, {"vid": "00075", "seq": 5}],
    },
    {
        "id": "bud-shorstein",
        "title": "Was Samuel 'Bud' Shorstein president — or chairman?",
        "status": "resolved-probable",
        "body": "The 2018-19 Past Presidents list prints \"Samuel 'Bud' Shorstein 1978-1980.\" But the 1999-2000 list does not include him, and the 1979-80 yearbook's officers photo caption reads 'Laurie DuBow - President; Samuel (Bud) Shorstein - Chairman of the Board.' Like Robert J. Gordon, he appears to have been a Chairman of the Board whom the 2018-19 list folded into the presidential succession. (Bud Shorstein was a prominent figure statewide; his service to the Center is extensively documented — just not, apparently, as its president.)",
        "citations": [{"vid": "00077", "seq": 25}, {"vid": "00058", "seq": 51}, {"vid": "00038", "seq": 258}],
    },
    {
        "id": "missing-1931-33",
        "title": "Where are 1931, 1932, and 1933?",
        "status": "open",
        "body": "The collection runs continuously from 1926-27 to 2018-19 except for 1931-1933 — the depths of the Depression, when Jacksonville Jewish institutions were under severe financial strain. Were the yearbooks never published in those years, or published and lost? The collection itself does not say.",
        "citations": [],
    },
    {
        "id": "lavilla-date",
        "title": "1907 or 1909 for the LaVilla synagogue?",
        "status": "resolved",
        "body": "The dates describe different phases. The 1926-27 historical essay says that in 1907 the growing congregation began erecting its Jefferson & Duval synagogue; the Center's 125th-anniversary timeline says the building was completed and dedicated in 1909. The site now presents both stages rather than treating them as a contradiction.",
        "citations": [{"vid": "00002", "seq": 28}],
        "research": ["jjc125"],
    },
    {
        "id": "first-yearbook",
        "title": "What was the first Jacksonville Jewish Center yearbook?",
        "status": "open",
        "body": "The surviving 1926-27 volume calls itself the Center's 'first attempt to produce a Year Book.' The 125th-anniversary timeline says earlier editions dated to 1902 were primarily congregational directories, and identifies 1935 as the first yearbook in the form recognized today. These descriptions may use 'yearbook' differently; until the earlier editions are located, the archive treats 1926-27 as the first surviving full Year Book in its collection rather than the first publication of any kind.",
        "citations": [{"vid": "00002", "seq": 5}],
        "research": ["jjc125"],
    },
    {
        "id": "annex-date",
        "title": "When was the classroom annex built — 1957 or 1958?",
        "status": "open",
        "body": "The National Park Service article says the classroom annex was 'added 1957'; the 1958-59 yearbook photographs groundbreaking ceremonies for the 'New Classroom Building' on May 2, 1958. Possibly a planning-vs-construction distinction; the yearbook is primary evidence for the 1958 groundbreaking.",
        "citations": [{"vid": "00017", "seq": 27}],
    },
    {
        "id": "early-presidents",
        "title": "The unverifiable early presidents (1901-1922)",
        "status": "open",
        "body": "Max Frank, H. Hammerman, Isaac Davis, and Elias H. Pilton appear in the printed Past-Presidents lists, but no yearbooks exist from their era to confirm terms (the 1926-27 volume does describe Pilton as president 'for nearly 20 years'). Newspaper archives or synagogue minutes would be needed to verify dates.",
        "citations": [{"vid": "00058", "seq": 51}, {"vid": "00002", "seq": 29}],
    },
    {
        "id": "org-keyword-caveat",
        "title": "A note on organization tracking",
        "status": "methodology",
        "body": "Organization timelines on this site are built from keyword appearances in OCR text. Some names are ambiguous — 'Solomon Schechter' names both a national award the Center won in 1952 and the day school founded later; generic words like 'Basketball' or 'Library' can match incidental text. Citations link to the underlying pages so readers can judge context.",
        "citations": [{"vid": "00087", "seq": 29}],
    },
]


def main() -> None:
    NOT_IN_1819 = {"Jeffery Morris", "Stuart Hecht"}
    presidents = [
        {
            "name": n, "term": t, "start": s, "end": e,
            "citations": ([L9900] if n in NOT_IN_1819
                          else [L9900, L1819A] if s < 1980
                          else [L9900, L1819B]) + c,
            "note": note, "confidence": conf,
        }
        for (n, t, s, e, c, note, conf) in PRESIDENTS
    ]
    clergy = [
        {
            "name": n, "role": r, "from": f, "to": to,
            "citations": c, "note": note,
            "research": [RESEARCH[k] for k in rk],
        }
        for (n, r, f, to, c, note, rk) in CLERGY
    ]
    events = [
        {
            "year": y, "title": t, "body": b, "kind": k,
            "citations": c, "research": [RESEARCH[x] for x in rk],
        }
        for (y, t, b, k, c, rk) in EVENTS
    ]
    stories = [
        {**s, "research": [RESEARCH[k] for k in s["research"]]} for s in STORIES
    ]
    mysteries = [
        {**m, "research": [RESEARCH[k] for k in m.get("research", [])]}
        for m in MYSTERIES
    ]

    (JSON_DIR / "leadership.json").write_text(
        json.dumps({"presidents": presidents, "clergy": clergy}, indent=1),
        encoding="utf-8")
    (JSON_DIR / "events.json").write_text(json.dumps(events, indent=1), encoding="utf-8")
    (JSON_DIR / "threads.json").write_text(json.dumps(THREADS, indent=1), encoding="utf-8")
    (JSON_DIR / "stories.json").write_text(json.dumps(stories, indent=1), encoding="utf-8")
    (JSON_DIR / "mysteries.json").write_text(json.dumps(mysteries, indent=1), encoding="utf-8")
    (JSON_DIR / "research_sources.json").write_text(json.dumps(RESEARCH, indent=1), encoding="utf-8")
    print(f"presidents: {len(presidents)}  clergy: {len(clergy)}  events: {len(events)}")
    print(f"threads: {len(THREADS)}  stories: {len(stories)}  mysteries: {len(MYSTERIES)}")


if __name__ == "__main__":
    main()
