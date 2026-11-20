#!/usr/bin/env python3
"""Read-only test of the urr-base-1 hole semantics: stream the virtual output
disc in order (parts over copies where they overlap; holes filled per the
hypothesis under test) into a SHA-256, and compare against the author's
output_sha256. Writes NOTHING to disk — the full-disc build died on quota,
so the hash is computed from a virtual assembly instead.

Hypotheses for holes (output ranges covered by neither parts nor copies):
  B: identity — output[a:b] == source ISO bytes [a:b] (builder starts from
     the source ISO image); beyond the source size, zeros.
  A: zeros everywhere.

Copies are [src, dst, length]: source ISO bytes [src, src+length) land at
output [dst, dst+length). Parts take precedence where they overlap copies.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
CORE = ROOT / "extracted" / "core"
ISO = ROOT / "iso" / "urban-reign-usa.iso"
CHUNK = 1 << 22


def stream_hash(hypothesis):
    manifest = json.loads((CORE / "manifest.json").read_text())
    out_size = manifest["output_size"]
    target = manifest["output_sha256"]
    src_size = ISO.stat().st_size

    # segments: (start, end, kind, payload) — parts win over copies on overlap
    segs = []
    for p in manifest["parts"]:
        segs.append((p["offset"], p["offset"] + p["length"], "part", p))
    for s, d, n in manifest["copies"]:
        segs.append((d, d + n, "copy", (s, d, n)))
    segs.sort(key=lambda t: (t[0], 0 if t[2] == "part" else 1))
    # resolve overlaps: keep first (part) wins, trim the rest
    resolved = []
    for a, b, kind, pay in segs:
        a0 = a
        for ra, rb, rk, rp in resolved:
            if rb <= a0 or ra >= b:
                continue
            if ra <= a0 < rb:
                a0 = rb
            if a0 >= b:
                break
        if a0 < b:
            resolved.append((a0, b, kind, pay))
    resolved.sort()
    # build a merged event list: (start, end, kind, payload) covering parts+copies
    h = hashlib.sha256()
    pos = 0
    with open(ISO, "rb") as src:
        part_cache = {}

        def part_data(p):
            key = p["entry"]
            if key not in part_cache:
                part_cache[key] = (CORE / "parts" / Path(key).name).read_bytes()
            return part_cache[key]

        def feed_copy(s, d, a, b):
            # output [a,b) comes from source ISO [s+(a-d), s+(b-d))
            src.seek(s + (a - d))
            remaining = b - a
            while remaining > 0:
                chunk = src.read(min(remaining, CHUNK))
                if not chunk:
                    raise IOError("short ISO read")
                h.update(chunk)
                remaining -= len(chunk)

        def feed_hole(a, b):
            if hypothesis == "A":
                remaining = b - a
                zero = b"\x00" * CHUNK
                while remaining > 0:
                    h.update(zero[:min(remaining, CHUNK)])
                    remaining -= min(remaining, CHUNK)
            else:  # B: identity from source at same offset, zeros past source size
                if a < src_size:
                    take = min(b, src_size) - a
                    src.seek(a)
                    remaining = take
                    while remaining > 0:
                        chunk = src.read(min(remaining, CHUNK))
                        if not chunk:
                            raise IOError("short ISO read")
                        h.update(chunk)
                        remaining -= len(chunk)
                    a += take
                if a < b:
                    remaining = b - a
                    zero = b"\x00" * CHUNK
                    while remaining > 0:
                        h.update(zero[:min(remaining, CHUNK)])
                        remaining -= min(remaining, CHUNK)

        for a, b, kind, pay in resolved:
            if a > pos:
                feed_hole(pos, a)
            if kind == "part":
                data = part_data(pay)
                h.update(data[a - pay["offset"]:b - pay["offset"]])
            else:
                s, d, n = pay
                feed_copy(s, d, a, b)
            pos = b
            if pos % (1 << 30) < CHUNK:
                print(f"  ...{pos/1e9:.2f} GB hashed", flush=True)
        if pos < out_size:
            feed_hole(pos, out_size)
    got = h.hexdigest()
    print(f"hypothesis {hypothesis}: {got}")
    print(f"target        : {target}")
    print("MATCH:", got == target)
    return got == target


if __name__ == "__main__":
    hypo = sys.argv[1] if len(sys.argv) > 1 else "B"
    stream_hash(hypo)
