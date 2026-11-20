#!/usr/bin/env python3
"""sjis_strings.py — scan a file for runs of Shift-JIS text (and ASCII).

Usage:
  python3 sjis_strings.py <file> [--min N] [--ascii] [--json out.json]
Prints: offset, length, text (Shift-JIS decoded).
"""
import argparse
import json
import sys


def is_sjis_lead(b):
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC


def is_sjis_trail(b):
    return 0x40 <= b <= 0x7E or 0x80 <= b <= 0xFC


def scan(data, min_len=4, want_ascii=True):
    """Yield (offset, text) for runs of decodable Shift-JIS / ASCII."""
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        if b < 0x20 and b not in (0x0A, 0x0D, 0x09):
            i += 1
            continue
        # try to extend a run starting at i
        j = i
        buf = bytearray()
        while j < n:
            c = data[j]
            if is_sjis_lead(c) and j + 1 < n and is_sjis_trail(data[j + 1]):
                buf += data[j:j + 2]
                j += 2
            elif 0x20 <= c < 0x7F:
                buf.append(c)
                j += 1
            elif c in (0x0A, 0x0D):
                buf.append(c)
                j += 1
            elif 0xA1 <= c <= 0xDF:  # half-width katakana
                buf.append(c)
                j += 1
            else:
                break
        if len(buf) >= min_len:
            try:
                text = bytes(buf).decode("shift_jis")
            except UnicodeDecodeError:
                text = None
            if text is not None:
                # keep runs that contain at least one non-space char
                # and (for ASCII-only runs) look like words, not noise
                stripped = text.strip()
                if stripped:
                    if want_ascii or any(ord(ch) > 0x7E for ch in text):
                        yield i, text.replace("\n", "\\n").replace("\r", "")
        i = j if j > i else i + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--no-ascii", action="store_true")
    ap.add_argument("--json")
    args = ap.parse_args()
    data = open(args.file, "rb").read()
    results = [{"offset": off, "text": t} for off, t in scan(data, args.min, not args.no_ascii)]
    if args.json:
        json.dump(results, open(args.json, "w"), ensure_ascii=False, indent=1)
        print(f"{len(results)} strings -> {args.json}")
    else:
        for r in results:
            print(f"{r['offset']:>10}  {r['text']}")


if __name__ == "__main__":
    main()
