#!/usr/bin/env python3
"""Tekken 5 (PS2) ISO survey — stdlib-only disc-layout + format fingerprinting.

Usage:
  t5_survey.py <iso_dir> --out survey.json
  t5_survey.py --exe SLUS_210.59 --strings-out dw_strings.txt

Does NOT modify anything. Outputs:
  - file inventory: path, size, extension
  - magic-byte table (first 16 bytes hex + ascii)
  - entropy of first 256KB per file (flags packed/encrypted)
  - known-format hits: PSS/MPEG, TIM2, VAGp, ELF, PS-ADPCM containers
  - keyword scan of the main executable for Devil Within / stage / roster names
"""
import json
import math
import os
import re
import struct
import sys
from collections import Counter

KNOWN = {
    b"\x7fELF": "ELF (executable/object)",
    b"TIM2": "TIM2 (PS2 texture)",
    b"VAGp": "VAGp (PS2 ADPCM audio)",
    b"\x00\x00\x01\xBA": "MPEG program stream (PSS movie?)",
    b"MThd": "MIDI",
    b"pDAT": "pDAT container",
    b"IECS": "IECS (Sony container)",
    b"\x10\x00\x00\x00": None,  # too generic, skip
}

DEVIL_WITHIN_KEYWORDS = [
    b"DEVIL WITHIN", b"Devil Within", b"devil within",
    b"JACK", b"OGRE", b"Ogre", b"TRUE OGRE",
    b"G CORP", b"G Corp", b"GCorp",
    b"HEIHACHI", b"KAZUYA", b"JUN",
    b"STAGE 1", b"STAGE 2", b"STAGE 3", b"STAGE 4", b"STAGE 5",
    b"FORCE", b"GEM", b"DEVIL GENE", b"Devil Gene",
    b"SOUL SPHERE", b"Soul Sphere",
]


def entropy(data):
    if not data:
        return 0.0
    c = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def magic_name(head):
    for magic, name in KNOWN.items():
        if head.startswith(magic):
            return name
    return None


def scan_exe(path, out):
    with open(path, "rb") as f:
        data = f.read()
    strings = re.findall(rb"[ -~]{6,}", data)
    hits = {}
    for kw in DEVIL_WITHIN_KEYWORDS:
        matches = sorted({s.decode("ascii", "replace")
                          for s in strings if kw.lower() in s.lower()})
        if matches:
            hits[kw.decode()] = matches[:40]
    # path-like strings: reveal the disc layout the executable expects
    pathlike = sorted({s.decode("ascii", "replace") for s in strings
                       if (b"/" in s or b"\\" in s or b".DAT" in s.upper()
                           or b".BIN" in s.upper())
                       and len(s) < 120})[:200]
    report = {
        "exe": path,
        "size": len(data),
        "total_printable_strings": len(strings),
        "devil_within_hits": hits,
        "path_like_strings": pathlike,
        "exe_entropy_head": round(entropy(data[:262144]), 3),
    }
    # stage-like identifiers: look for "STG" / "stg" prefixed tokens
    stg = sorted({s.decode("ascii", "replace") for s in strings
                  if re.match(rb"(?i)^(stg|stage|bg)[_a-z0-9]{0,12}$", s)})
    report["stage_like_tokens"] = stg[:80]
    if out:
        with open(out, "w") as f:
            json.dump(report, f, indent=1)
    print(f"exe {os.path.basename(path)}: {len(data)} bytes, "
          f"{len(strings)} strings, {len(hits)} DW keyword groups hit")
    for k, v in hits.items():
        print(f"  {k}: {len(v)} e.g. {v[:5]}")
    return report


def survey_dir(root, out):
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root)
            try:
                size = os.path.getsize(p)
                with open(p, "rb") as f:
                    head = f.read(16)
                    sample = f.read(262128)
                rows.append({
                    "path": rel, "size": size,
                    "ext": os.path.splitext(fn)[1].lower(),
                    "magic_hex": head.hex(),
                    "magic_ascii": "".join(chr(b) if 32 <= b < 127 else "."
                                           for b in head),
                    "format": magic_name(head),
                    "entropy": round(entropy(head + sample), 3),
                })
            except OSError as e:
                rows.append({"path": rel, "error": str(e)})
    rows.sort(key=lambda r: r.get("size", 0), reverse=True)
    ext_hist = Counter(r.get("ext", "") for r in rows)
    total = sum(r.get("size", 0) for r in rows)
    report = {"root": root, "files": len(rows), "bytes": total,
              "ext_histogram": dict(ext_hist), "inventory": rows}
    if out:
        with open(out, "w") as f:
            json.dump(report, f, indent=1)
    print(f"{len(rows)} files, {total/1e9:.2f} GB")
    print("extensions:", dict(ext_hist.most_common(15)))
    for r in rows[:25]:
        print(f"  {r['size']:>12}  {r.get('format') or r['magic_ascii'][:16]:32s}  {r['path']}")
    return report


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--exe", action="store_true")
    ap.add_argument("--strings-out")
    a = ap.parse_args()
    if a.exe:
        scan_exe(a.target, a.strings_out)
    else:
        survey_dir(a.target, a.out)
