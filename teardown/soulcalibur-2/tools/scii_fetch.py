#!/usr/bin/env python3
"""Range-fetch from the Soulcalibur II PS2 ISO on GitHub Release.
Avoids downloading the full 1.38GB; pulls only needed byte ranges.
Usage: python3 scii_fetch.py <abs_offset> <length> <out_file>
"""
import sys, urllib.request

URL = "https://github.com/mhvnsnt/western-heart/releases/download/soulcalibur2-ps2-v1/Soulcalibur-II.iso"
UA = {"User-Agent": "Mozilla/5.0"}

def fetch_range(abs_off, length):
    req = urllib.request.Request(URL, headers={"Range": f"bytes={abs_off}-{abs_off+length-1}", **UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    if len(data) != length:
        raise IOError(f"short read: got {len(data)}, want {length} @{abs_off}")
    return data

if __name__ == "__main__":
    off, ln, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    data = fetch_range(off, ln)
    open(out, "wb").write(data)
    print(f"fetched {len(data)} bytes @{off} -> {out}", file=sys.stderr)
