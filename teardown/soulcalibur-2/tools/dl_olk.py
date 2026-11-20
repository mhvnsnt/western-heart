#!/usr/bin/env python3
"""Resumable download of root.olk byte range from the SC2 Xbox ISO on GitHub release.
Refreshes the signed release-asset URL when it expires. Per owner RESUME RULE: never restart from zero."""
import os, sys, subprocess, time, urllib.request

ASSET_API = "https://api.github.com/repos/mhvnsnt/western-heart/releases/assets/637640671"
OLK_START = 682948608          # sector 333471 * 2048
OLK_END   = 1376845823         # end of ISO (size 1376845824)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "root.olk")
TOTAL = OLK_END - OLK_START + 1

def gh_token():
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

def signed_url(token):
    req = urllib.request.Request(ASSET_API, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/octet-stream"})
    # don't follow redirect; grab Location
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(NoRedir)
    try:
        opener.open(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307):
            return e.headers.get("Location")
        raise
    raise RuntimeError("no redirect from asset API")

import urllib.error

def main():
    token = gh_token()
    have = os.path.getsize(OUT) if os.path.exists(OUT) else 0
    if have >= TOTAL:
        print(f"already complete: {have} bytes", flush=True); return
    url = signed_url(token)
    url_ts = time.time()
    t0 = time.time()
    n = have
    f = open(OUT, "ab")
    try:
        while n < TOTAL:
            if time.time() - url_ts > 2400:  # refresh signed URL every 40 min
                url = signed_url(token); url_ts = time.time()
                print("refreshed signed URL", flush=True)
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "Range": f"bytes={OLK_START + n}-{OLK_END}"})
            try:
                r = urllib.request.urlopen(req, timeout=300)
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    url = signed_url(token); url_ts = time.time(); continue
                raise
            if r.status not in (200, 206):
                print(f"unexpected status {r.status}", flush=True); time.sleep(10); continue
            while n < TOTAL:
                chunk = r.read(1 << 20)
                if not chunk: break
                f.write(chunk); n += len(chunk)
                if n % (25 << 20) < (1 << 20):
                    el = time.time() - t0
                    print(f"  {n}/{TOTAL} ({100.0*n/TOTAL:.1f}%) {n/1e6/max(el,1):.1f} MB/s", flush=True)
            r.close()
    finally:
        f.close()
    final = os.path.getsize(OUT)
    print(f"done: {final}/{TOTAL} bytes", flush=True)

if __name__ == "__main__":
    main()
