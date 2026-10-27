#!/usr/bin/env python3
"""Poly Haven API client for Western Heart (WH).

VERIFIED 2026-10-24 (live calls, no auth, no key):
  - Correct host is https://api.polyhaven.com  (NOT api.polyhaven.org:
    that host returned HTTP 522 on 2026-10-24).
  - GET /assets?type=textures|hdris|models  -> JSON dict keyed by asset id.
  - GET /categories/{type}                 -> JSON dict of category counts.
  - GET /files/{asset_id}                  -> JSON of download URLs by map /
    resolution / format, hosted on dl.polyhaven.org.
  - No account, no key, no rate limit published on the API responses.
  - License: CC0 (Poly Haven states all assets are CC0; verify per asset
    on its polyhaven.com page before shipping).

Usage:
  python3 polyhaven.py --list --type textures --limit 5
  python3 polyhaven.py --search sand --type textures
  python3 polyhaven.py --download sand_01 --map Diffuse --res 1k --format jpg --out samples/
Only the Python standard library is used. No credentials are read or sent.
"""
import argparse, json, os, sys, urllib.request, urllib.error

BASE = "https://api.polyhaven.com"
UA = {"User-Agent": "WH-free-pulls/1.0"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def list_assets(asset_type, limit):
    data = get_json(f"{BASE}/assets?type={asset_type}")
    items = sorted(data.items(), key=lambda kv: kv[1].get("download_count", 0), reverse=True)
    for asset_id, meta in items[:limit]:
        print(f"{asset_id}\t{meta.get('name')}\t{','.join(meta.get('categories', []))}"
              f"\tdownloads={meta.get('download_count')}")
    print(f"# total {asset_type}: {len(data)} (showing {min(limit, len(data))})")


def search(query, asset_type):
    data = get_json(f"{BASE}/assets?type={asset_type}")
    q = query.lower()
    hits = [(k, v) for k, v in data.items()
            if q in k.lower() or q in v.get("name", "").lower()
            or q in " ".join(v.get("categories", [])).lower()
            or q in " ".join(v.get("tags", [])).lower()]
    for asset_id, meta in hits[:50]:
        print(f"{asset_id}\t{meta.get('name')}\t{','.join(meta.get('categories', []))}")
    print(f"# {len(hits)} hit(s) for {query!r} in {asset_type}")


def download(asset_id, map_name, res, fmt, outdir):
    files = get_json(f"{BASE}/files/{asset_id}")
    # Texture maps are keyed e.g. Diffuse/nor_dx/rough; HDRIs/models differ.
    if map_name not in files:
        print(f"ERROR: map {map_name!r} not in {asset_id}; available: {sorted(files)}",
              file=sys.stderr)
        return 1
    try:
        entry = files[map_name][res][fmt]
    except KeyError:
        print(f"ERROR: no {res}/{fmt} for map {map_name}; available resolutions: "
              f"{sorted(files[map_name])}", file=sys.stderr)
        return 1
    os.makedirs(outdir, exist_ok=True)
    url, size = entry["url"], entry.get("size")
    fname = os.path.basename(url)
    dest = os.path.join(outdir, fname)
    print(f"Downloading {url} ({size} bytes, per API) -> {dest}")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        data = r.read()
        f.write(data)
    print(f"OK {dest} ({len(data)} bytes on disk; API said {size})")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--search")
    ap.add_argument("--type", default="textures", choices=["textures", "hdris", "models", "all"])
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--download")
    ap.add_argument("--map", default="Diffuse")
    ap.add_argument("--res", default="1k")
    ap.add_argument("--format", default="jpg")
    ap.add_argument("--out", default="samples")
    a = ap.parse_args()
    if a.download:
        return download(a.download, a.map, a.res, a.format, a.out)
    if a.search:
        search(a.search, a.type)
    elif a.list:
        list_assets(a.type, a.limit)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
