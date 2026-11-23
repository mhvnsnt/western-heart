#!/usr/bin/env python3
"""Checkpoint verification: confirm batch reports are clean, then prove the
repo bytes are correct by downloading one piece over HTTPS and comparing it
against the local source range.

Usage: verify_checkpoint.py <phase> <piece-check...>
  piece-check: <raw-url> <local-file> <offset> <length>
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

WD = os.path.expanduser("~/workspace/koc2-disk-decision")


def check_reports(names):
    ok = True
    for n in names:
        p = os.path.join(WD, "batches", n + ".report.json")
        r = json.load(open(p))
        v = r.get("verify", {})
        good = v.get("missing") == [] and v.get("wrong_sha") == []
        print(f"{n}: commit={r.get('commit', '?')[:10]} "
              f"entries={len(r['entries'])} verify={'OK' if good else 'FAIL ' + str(v)}")
        ok = ok and good
    return ok


def check_piece(url, local_file, offset, length):
    print(f"downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "koc2-verify/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r:
        print(f"  HTTP {r.status} content-range={r.headers.get('Content-Range')} "
              f"accept-ranges={r.headers.get('Accept-Ranges')} "
              f"cors={r.headers.get('Access-Control-Allow-Origin')}")
        data = r.read()
    print(f"  downloaded {len(data)} bytes (expect {length})")
    h1 = hashlib.sha256(data).hexdigest()
    with open(local_file, "rb") as f:
        f.seek(offset)
        local = f.read(length)
    h2 = hashlib.sha256(local).hexdigest()
    print(f"  repo sha256:  {h1}")
    print(f"  local sha256: {h2}")
    print("  PIECE MATCH" if h1 == h2 and len(data) == length else "  PIECE MISMATCH!")
    return h1 == h2 and len(data) == length


if __name__ == "__main__":
    phase = sys.argv[1]
    batches = json.loads(sys.argv[2])  # ["B1-small", "B21", ...]
    ok = check_reports(batches)
    i = 3
    while i + 3 < len(sys.argv) + 1 and i < len(sys.argv):
        url, lf, off, ln = sys.argv[i:i + 4]
        ok = check_piece(url, lf, int(off), int(ln)) and ok
        i += 4
    print("CHECKPOINT", phase, "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
