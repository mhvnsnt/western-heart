#!/usr/bin/env python3
"""Inspect a KC2FIRE.001-style archive (King of Colosseum II).

Prints: file size, header hexdump, magic-signature scan (TIM2, PSS, .mdl
hints), printable-string sample, and a first guess at table structure
(sequential u32 offset/size pairs near the header).

Usage: kc2fire_inspect.py <archive> [--strings N] [--scan]
Lane E (KoC2), 2026-11-19.
"""
import re
import struct
import sys
from pathlib import Path


def hexdump(data: bytes, base: int = 0, width: int = 16):
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{base + i:08x}  {hexs:<48}  {asc}")


def scan_magics(data: bytes):
    magics = {
        b"TIM2": "TIM2 texture",
        b"\x00\x00\x01\xba": "PSS/MPEG PS",
        b"PSMF": "PSMF video",
        b"RIFF": "RIFF/WAVE",
        b"VAGp": "VAG audio",
        b"ADPCM": "ADPCM",
        b".mdl": ".mdl string",
        b"KC2FIRE": "KC2FIRE string",
        b"SLPM-65602": "game id string",
    }
    for magic, label in magics.items():
        offs = []
        start = 0
        while True:
            j = data.find(magic, start)
            if j < 0:
                break
            offs.append(j)
            start = j + 1
            if len(offs) >= 10:
                break
        if offs:
            print(f"{label} ({magic!r}): {len(offs)}+ hits, first at "
                  + ", ".join(f"0x{o:x}" for o in offs[:10]))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    p = Path(argv[1])
    data = p.read_bytes()
    print(f"{p}  {len(data)} bytes  ({len(data) / 1024 / 1024:.1f} MiB)")
    print("\n== first 256 bytes ==")
    hexdump(data[:256])
    print("\n== u32 header words (LE) ==")
    words = struct.unpack_from("<32I", data, 0)
    print(" ".join(f"{w:08x}" for w in words[:16]))
    print(" ".join(f"{w:08x}" for w in words[16:]))
    print("\n== magic scan ==")
    scan_magics(data)
    print("\n== printable strings (>=6 chars, first 40) ==")
    strs = re.findall(rb"[ -~]{6,}", data)
    for s in strs[:40]:
        print(" ", s.decode())
    print(f"   ({len(strs)} strings total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
