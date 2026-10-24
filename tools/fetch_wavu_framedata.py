#!/usr/bin/env python3
"""Fetch public Tekken 8 frame data from wavu.wiki (CC0) Cargo API.

Restored from e03195de (the original was lost in the cd3bf38 wipe) and extended:
  * also pulls `notes`, `alias`, `alt`, `reach`, `tracksLeft`, `tracksRight` (stance
    transitions, alternate inputs and properties live in `notes`)
  * --out lets the full fetch go to its own folder so the Oct 14 baseline files in
    docs/t7t8-reference/frame-data/ stay byte-identical

Usage:
  python3 tools/fetch_wavu_framedata.py King "Devil Jin" ...                # baseline schema
  python3 tools/fetch_wavu_framedata.py --full --out docs/t7t8-reference/frame-data-t8-full --all
"""
import argparse, datetime, json, pathlib, time, urllib.parse, urllib.request

REPO = pathlib.Path(__file__).resolve().parents[1]
BASE_F = "id,name,input,parent,target,damage,startup,recv,tot,crush,block,hit,ch"
FULL_F = BASE_F + ",alias,alt,reach,tracksLeft,tracksRight,notes"
# Every T8 character with a movelist on wavu.wiki (checked 2026-10-21 against the Cargo table).
ALL_T8 = ["Alisa", "Anna", "Armor King", "Asuka", "Azucena", "Bob", "Bryan", "Claudio", "Clive",
          "Devil Jin", "Dragunov", "Eddy", "Fahkumram", "Feng", "Heihachi", "Hwoarang", "Jack-8",
          "Jin", "Jun", "Kazuya", "King", "Kuma", "Kunimitsu", "Lars", "Law", "Lee", "Leo", "Leroy",
          "Lidia", "Lili", "Nina", "Panda", "Paul", "Raven", "Reina", "Shaheen", "Steve", "Victor",
          "Xiaoyu", "Yoshimitsu", "Zafina"]


def q(body, off, fields):
    p = {"action": "cargoquery", "tables": "Move", "fields": fields, "where": f"id LIKE '{body}-%'",
         "limit": "500", "offset": str(off), "format": "json"}
    r = urllib.request.Request("https://wavu.wiki/w/api.php?" + urllib.parse.urlencode(p),
                               headers={"User-Agent": "WH-reference/1.0"})
    return [x["title"] for x in json.load(urllib.request.urlopen(r, timeout=60)).get("cargoquery", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bodies", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--full", action="store_true", help="also fetch notes/alias/alt/reach/tracking")
    ap.add_argument("--out", default="docs/t7t8-reference/frame-data")
    a = ap.parse_args()
    out = REPO / a.out
    out.mkdir(parents=True, exist_ok=True)
    fields = FULL_F if a.full else BASE_F
    for body in (ALL_T8 if a.all else a.bodies):
        rows, off = [], 0
        while True:
            b = q(body, off, fields)
            rows += b
            off += 500
            if len(b) < 500:
                break
            time.sleep(1)
        rows = [r for r in rows if r["id"].startswith(body + "-")]
        doc = {"source": "https://wavu.wiki/t/" + body.replace(" ", "_") + "_movelist", "license": "CC0-1.0 (wavu.wiki)",
               "game": "Tekken 8", "body": body, "moves": rows}
        if a.full:
            doc["fetched"] = datetime.date.today().isoformat()
            doc["fields"] = fields
        (out / f"{body.lower().replace(' ', '_')}.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        print(body, len(rows))
        time.sleep(1)


if __name__ == "__main__":
    main()
