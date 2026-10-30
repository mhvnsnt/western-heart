#!/usr/bin/env python3
"""OpenGameArt (OGA) status probe + curated records for WH.

VERIFIED 2026-10-24:
  - OGA has NO public JSON search API. Appending ?format=json (or any
    similar flag) to the advanced search page returns the normal HTML
    search page (HTTP 200, text/html), not JSON. The search itself works
    in a browser: https://opengameart.org/art-search-advanced?keys=fighting
    returned "Displaying 1 - 24 of 194" on 2026-10-24.
  - Therefore this script does NOT scrape OGA and does NOT claim an API.
    It (a) probes the ?format=json URL once and reports content-type,
    and (b) prints curated records that were read from OGA detail pages
    in a browser, with per-asset attribution as shown on those pages.
    Download any asset you adopt by hand from its OGA page, under its
    own licence (licences vary per asset -- CC-BY, CC0, GPL, etc. --
    always re-check the asset page; the notes below are what the pages
    showed on 2026-10-24).
  - OGA downloads on detail pages may require a free OGA login for some
    files; that is a site login, not an API key, and this script never
    asks for it.

Usage:
  python3 opengameart.py --probe
  python3 opengameart.py --records
No credentials are read, sent, or needed.
"""
import argparse, json, urllib.request

SEARCH = ("https://opengameart.org/art-search-advanced?keys=fighting"
          "&sort_by=count&sort_order=DESC")

# Curated from OGA detail pages, read in a browser 2026-10-24. NOT API output.
RECORDS = [
    {"title": "Fighting Robot for Ultimate Smash Friends",
     "page": "https://opengameart.org/content/fighting-robot-for-ultimate-smash-friends",
     "attribution": "Stephen Challener (Redshrike), hosted by OpenGameArt.org",
     "licence_note": "Page states 'As part of CC-By, be sure to link back to OpenGameArt.org'",
     "contents": "Animated robot sprite (idle, shock, kick previews shown)",
     "wh_use": "2D fighter sprite reference / placeholder fighter art; NOT a 3D WH model."},
    {"title": "Voiceover Pack: Fighter (40+ taunts)",
     "page": "https://opengameart.org/content/voiceover-pack-fighter-40-taunts",
     "attribution": 'Credit "Kenney.nl" or "www.kenney.nl" (page says not mandatory)',
     "licence_note": "Kenney pack; re-check asset page before shipping",
     "contents": "Separate OGG files: Round 1/2/3, Fight, Flawless victory, Combo breaker, Winner, You lose, etc.",
     "wh_use": "Announcer/VO placeholder lines for fight UI (Round/Fight/Winner) -- very WH-relevant."},
    {"title": "Streets of Fight",
     "page": "https://opengameart.org/content/streets-of-fight",
     "attribution": "by ansimuz (optional, per page)",
     "licence_note": "Page: 'Feel free to use it on your own personal or commercial projects'",
     "contents": "Beat-'em-up pack: stage tileset, parallax background, foreground, props, female player (9 animations), punk enemy (4 animations); streets_of_fight_files.zip, 294.9 KB, 1098 downloads (per page)",
     "wh_use": "2D side-mode / menu background reference; NOT the 3D fighter itself."},
]


def probe():
    url = SEARCH + "&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "WH-free-pulls/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        ctype = r.headers.get("Content-Type", "")
        head = r.read(200).decode("utf-8", "replace")
    print(f"GET {url}\n-> HTTP 200, Content-Type: {ctype}")
    print(f"-> first bytes: {head[:120]!r}")
    if "json" not in ctype:
        print("CONFIRMED: no JSON API -- OGA returns HTML for ?format=json. "
              "Use the browser search + manual download; do not parse this as JSON.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--records", action="store_true")
    a = ap.parse_args()
    if a.probe:
        probe()
    if a.records:
        print(json.dumps(RECORDS, indent=2))
    if not (a.probe or a.records):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
