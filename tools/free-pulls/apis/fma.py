#!/usr/bin/env python3
"""Free Music Archive (FMA) status probe + manual curation helper for WH.

VERIFIED 2026-10-24 -- THE FMA API IS SHUT DOWN, AND THERE IS NO KEY
PATH. Do not let any older write-up mislead you:
  - GET https://freemusicarchive.org/api/get/tracks.json?limit=1
    -> HTTP 404 on 2026-10-24.
  - FMA's own app-developer page (https://freemusicarchive.org/app-developers/)
    states: "Free Music Archive used to have an API ... we unfortunately
    had to shut down our API." There is no api_key signup for it any more.
  - FMA rules that DO still apply (same page): NO hotlinking (host any
    FMA track you use on your own server, under its CC licence), and do
    NOT forward user search queries to FMA's search engine / scrape its
    HTML without explicit FMA approval.

So this script does NOT scrape FMA and does NOT fake API results. It:
  1. probes the old endpoint and reports the honest result, and
  2. prints a small CURATED candidate list that was found by reading
     FMA's public genre/track pages in a browser (not via any API),
     clearly labelled as manual curation, with licence notes to re-check
     on the track page before use. Download any track you adopt by hand
     from its FMA page, host it yourself, credit the artist, and obey
     the licence (several below are CC BY-NC-SA -- NonCommercial, so
     they are reference/temp-track candidates, NOT cleared for a
     commercial release without checking the licence).

Usage:
  python3 fma.py --probe
  python3 fma.py --candidates
  python3 fma.py --template out.json   # blank metadata record to fill in by hand
No credentials are read, sent, or needed. There is no FMA_API_KEY.
"""
import argparse, json, urllib.request, urllib.error

OLD_ENDPOINT = "https://freemusicarchive.org/api/get/tracks.json?limit=1"

# Manual curation from FMA public pages, read 2026-10-24. NOT API output.
CANDIDATES = [
    {"title": "Cowboy Surfer", "artist": "The Vivisectors",
     "album": "Happy Halloween", "genres": "Rock, Surf, Halloween",
     "duration": "03:42", "licence": "CC BY-NC-SA (per FMA track page)",
     "page": "https://freemusicarchive.org/music/The_Vivisectors/Happy_Halloween/The_Vivisectors_-_08_-_Cowboy_Surfer/",
     "wh_use": "Spooky/surf fight vibe; reference track. NC licence: check before any commercial use."},
    {"title": "Duane Stomp", "artist": "The Vivisectors",
     "album": "Happy Halloween", "genres": "Rock, Surf, Halloween",
     "duration": "02:39", "licence": "CC BY-NC-SA (per FMA track page)",
     "page": "https://freemusicarchive.org/music/The_Vivisectors/Happy_Halloween/The_Vivisectors_-_06_-_Duane_Stomp/",
     "wh_use": "Surf-rock fight energy; reference track."},
    {"title": "Halloween Surf Rock With Theramin", "artist": "Greg Kirkelie",
     "album": "Halloween Music", "genres": "20th Century Classical, Halloween, Holiday",
     "duration": "02:10", "licence": "RE-CHECK on FMA track page before use",
     "page": "https://freemusicarchive.org/genre/Halloween",
     "wh_use": "Spooky + surf + theremin; closest single-track match to the Cape Jones vibe."},
    {"title": "Ghost Surf Rock", "artist": "Loyalty Freak Music",
     "album": "WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !!",
     "genres": "Ambient, Halloween, Holiday, Instrumental",
     "duration": "04:07", "licence": "RE-CHECK on FMA track page before use",
     "page": "https://freemusicarchive.org/genre/Halloween",
     "wh_use": "Already the Cape Jones theme per WH direction; listed here only as the FMA record."},
]


def probe():
    req = urllib.request.Request(OLD_ENDPOINT, headers={"User-Agent": "WH-free-pulls/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"UNEXPECTED: old FMA API returned HTTP {r.status}; re-verify before trusting it.")
    except urllib.error.HTTPError as e:
        print(f"CONFIRMED: old FMA API -> HTTP {e.code} ({OLD_ENDPOINT})")
        print("FMA API is shut down (see https://freemusicarchive.org/app-developers/).")
        print("No key, no env var, no signup path restores it. Use --candidates for manual curation.")
    except Exception as e:
        print(f"Probe failed with {type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--template")
    a = ap.parse_args()
    if a.probe:
        probe()
    if a.candidates:
        print(json.dumps(CANDIDATES, indent=2))
    if a.template:
        template = {"title": "", "artist": "", "album": "", "fma_page": "",
                    "licence_as_shown_on_page": "", "downloaded_file": "",
                    "self_hosted_path": "", "credit_line": "",
                    "notes": "Download by hand from the FMA page; host on WH's own server; never hotlink."}
        with open(a.template, "w") as f:
            json.dump(template, f, indent=2)
        print(f"Wrote template {a.template}")
    if not (a.probe or a.candidates or a.template):
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
