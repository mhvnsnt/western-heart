#!/usr/bin/env python3
"""ambientCG API v3 client for Western Heart (WH).

VERIFIED 2026-10-24 (live calls, no auth, no key):
  - GET https://ambientcg.com/api/v3/assets?type=material&limit=2
    -> 200, {"totalResults": 2037, "assets": [{"id": "Fabric086"}, ...]}.
    Without include=downloads only ids are returned.
  - Add &include=downloads,maps,thumbnails,url to get download zips, e.g.
    Fabric086 1K-JPG -> https://ambientcg.com/get?file=Fabric086_1K-JPG.zip
    (7,733,757 bytes per API; verified by downloading it).
  - GET with a bogus id (Rock047A) -> 200 with totalResults 0, assets [].
    Ids are case-sensitive in practice; use ids returned by search.
  - License: CC0. No account required to download. Docs:
    https://docs.ambientcg.com/api/v3/assets/ (v2 still works but v3 is
    the documented current API; v2 full_json/downloads_csv also exist).
  - No published hard rate limit was observed; be polite (1 request at a
    time, small limits).

Usage:
  python3 ambientcg.py --search rock --limit 3
  python3 ambientcg.py --id Fabric086
  python3 ambientcg.py --download Fabric086 --variant 1K-JPG --out samples/
Only the Python standard library is used. No credentials are read or sent.
"""
import argparse, json, os, sys, urllib.parse, urllib.request

BASE = "https://ambientcg.com/api/v3/assets"
UA = {"User-Agent": "WH-free-pulls/1.0"}


def get(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    # One retry on a dropped connection (seen once 2026-10-24); a second
    # failure propagates as an error rather than a faked result.
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            if attempt == 2:
                raise
            print("# (retrying after a dropped connection...)", file=sys.stderr)


def search(query, limit, asset_type="material"):
    data = get({"q": query, "type": asset_type, "limit": limit, "include": "downloads"})
    print(f"# totalResults: {data.get('totalResults')}")
    for a in data.get("assets", []):
        variants = [d["attributes"] for d in a.get("downloads", [])]
        print(f"{a['id']}\t1K-JPG={'1K-JPG' in variants}\tvariants={len(variants)}")
    return data


def show(asset_id):
    data = get({"id": asset_id, "include": "downloads,maps,thumbnails,url"})
    for a in data.get("assets", []):
        print(f"id: {a['id']}\nmaps: {a.get('maps')}\nurl: {a.get('url')}")
        for d in a.get("downloads", []):
            print(f"  {d['attributes']}\t{d['size']} bytes\t{d['url']}")
    if not data.get("assets"):
        print(f"No asset with id {asset_id!r} (check spelling/case; search first).")
    return data


def download(asset_id, variant, outdir):
    data = get({"id": asset_id, "include": "downloads"})
    for a in data.get("assets", []):
        for d in a.get("downloads", []):
            if d["attributes"] == variant:
                os.makedirs(outdir, exist_ok=True)
                dest = os.path.join(outdir, os.path.basename(d["url"].split("file=")[-1]))
                print(f"Downloading {d['url']} ({d['size']} bytes, per API) -> {dest}")
                req = urllib.request.Request(d["url"], headers=UA)
                with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
                    blob = r.read()
                    f.write(blob)
                print(f"OK {dest} ({len(blob)} bytes on disk; API said {d['size']})")
                return 0
    print(f"ERROR: variant {variant!r} not found for {asset_id!r}; run --id first.",
          file=sys.stderr)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    ap.add_argument("--id")
    ap.add_argument("--download")
    ap.add_argument("--variant", default="1K-JPG")
    ap.add_argument("--type", default="material")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--out", default="samples")
    a = ap.parse_args()
    if a.download:
        return download(a.download, a.variant, a.out)
    if a.id:
        show(a.id)
    elif a.search:
        search(a.search, a.limit, a.type)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
