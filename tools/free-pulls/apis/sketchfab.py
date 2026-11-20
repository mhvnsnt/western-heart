#!/usr/bin/env python3
"""Sketchfab Data API v3 client for WH -- search works unauthenticated,
downloads REQUIRE auth. Both halves verified 2026-10-24.

VERIFIED:
  - GET https://api.sketchfab.com/v3/search?type=models&downloadable=true
        &q=torso&count=2  (no auth) -> HTTP 200 with results, including
    "Marble torso from a statue of Dionysos" (uid de078950bd474c73bb6cd7e1cf31de9b,
    isDownloadable=true). Search is public.
  - GET https://api.sketchfab.com/v3/models/<uid>/download (no auth)
    -> HTTP 401 {"detail": "Authentication credentials were not provided."}
  - Download auth (per Sketchfab docs): OAuth2 user token as
    `Authorization: Bearer <token>` on the Download API, or a personal
    API token as `Authorization: Token <token>` on Data API v3.
    This script reads the token ONLY from the SKETCHFAB_API_TOKEN
    environment variable, never prints it, and never writes it to disk.
    Get a token from your Sketchfab account settings / developer pages
    (free account); download permission still depends on the creator
    allowing downloads for that model, and attribution (creator, source,
    licence) must be displayed per Sketchfab's terms.
  - Note: Sketchfab's catalogue is migrating to Fab (Epic); treat
    Sketchfab as a reference/discovery source, not a permanent pipeline
    dependency, and always keep a local copy + attribution record.

Usage:
  python3 sketchfab.py --search torso --count 3        # no auth needed
  SKETCHFAB_API_TOKEN=... python3 sketchfab.py --download <uid> --out samples/
     # ^ only with a token you set yourself; without it the script stops
     #   after search and explains the 401 instead of faking a download.
Only the Python standard library is used.
"""
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error

BASE = "https://api.sketchfab.com/v3"
UA = {"User-Agent": "WH-free-pulls/1.0"}


def get(url, token=None):
    headers = dict(UA)
    if token:
        headers["Authorization"] = f"Token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def search(query, count):
    url = (f"{BASE}/search?type=models&downloadable=true&count={count}"
           f"&q={urllib.parse.quote(query)}")
    data = get(url)
    for m in data.get("results", []):
        print(f"{m['uid']}\t{m['name']}\tdownloadable={m.get('isDownloadable')}"
              f"\tlikes={m.get('likeCount')}\tviews={m.get('viewCount')}"
              f"\t{m.get('viewerUrl')}")
    print(f"# {len(data.get('results', []))} result(s) for {query!r} (search: unauthenticated OK)")
    return data


def download(uid, outdir):
    token = os.environ.get("SKETCHFAB_API_TOKEN")
    if not token:
        print("STOP: download requires auth. Unauthenticated call returns HTTP 401 "
              "(verified 2026-10-24).", file=sys.stderr)
        print("Set SKETCHFAB_API_TOKEN in your own environment (from your Sketchfab "
              "account) and re-run. The token is never printed or stored by this script.",
              file=sys.stderr)
        return 2
    try:
        data = get(f"{BASE}/models/{uid}/download", token=token)
    except urllib.error.HTTPError as e:
        print(f"Download endpoint HTTP {e.code}: {e.read(300).decode('utf-8', 'replace')}",
              file=sys.stderr)
        return 1
    gltf = data.get("gltf") or {}
    if not gltf.get("url"):
        print(f"No glTF download in response (keys: {sorted(data)}). "
              "The creator may not allow downloads for this model.", file=sys.stderr)
        return 1
    os.makedirs(outdir, exist_ok=True)
    dest = os.path.join(outdir, f"sketchfab_{uid}.zip")
    print(f"Temporary glTF URL received (expires in {gltf.get('expires')}s per API); "
          f"downloading -> {dest}")
    req = urllib.request.Request(gltf["url"], headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        blob = r.read()
        f.write(blob)
    print(f"OK {dest} ({len(blob)} bytes; API said {gltf.get('size')})")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--download")
    ap.add_argument("--out", default="samples")
    a = ap.parse_args()
    if a.download:
        return download(a.download, a.out)
    if a.search:
        search(a.search, a.count)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
