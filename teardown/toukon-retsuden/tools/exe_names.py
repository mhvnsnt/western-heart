#!/usr/bin/env python3
"""Patch the TR1 executable's wrestler names to English.

The JP EXE holds 16 wrestler names as Shift-JIS strings at file offsets
0xD14-0xE38 (292 bytes), referenced by a pointer table at 0x5D7B0
(16 x u32, RAM addresses; file offset X maps to RAM 0x80010000+X-0x800).
Each string is NUL-terminated (00 00) and padded with zeros to a
multiple of 4 bytes total.

The US version (Power Move Pro Wrestling) uses the same layout with
short names in Title Case full-width Latin -- this patch follows that
proven approach: surname / ring name, Title Case, 00 00 terminated,
4-byte padded. The whole repacked name area must fit in the original
292 bytes (asserted), so no other data moves; only the 16 pointers
are updated. The leftover bytes at the end of the name area are filled
with full-width spaces (81 40), NOT zeros: the game scans the name area
and a zero run reads as an empty string, which freezes the title -> menu
transition (bisected 2026-11-20, tests A-I).

Usage:
  python3 exe_names.py [--exe <in>] [--out <out>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"

NAME_AREA_START = 0xD14
NAME_AREA_END = 0xE38  # title string starts here; do not cross
PTR_TABLE = 0x5D7B0
RAM_BASE = 0x80010000
FILE_BASE = 0x800

# Short (EXE text) names, Title Case like the US version's EXE.
# The full names live on the name-sheet graphic instead.
# No leading/trailing spaces: the 13-char "Thunder Lyger" only fits
# the 292-byte area without them (280 bytes used, 12 spare).
NAMES = ["Fujinami", "Chosyu", "Mutoh", "Chono", "Hashimoto", "Hase",
         "Sasaki", "Koshinaka", "Thunder Lyger", "Tenzan", "Kanemoto",
         "Norton", "Great Muta", "Warrior", "Tanaka", "Hattori"]

FW_SPACE = "\u3000"  # full-width space, Shift-JIS 81 40


def to_fw(text):
    """Convert ASCII text to full-width Latin (Title Case preserved)."""
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr(0xFF21 + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            out.append(chr(0xFF41 + ord(ch) - ord("a")))
        elif ch == " ":
            out.append(FW_SPACE)
        else:
            raise ValueError(f"unsupported char {ch!r}")
    return "".join(out)


def patch(exe: bytes) -> bytes:
    exe = bytearray(exe)
    # sanity: the original names + pointer table must be where expected
    assert exe[NAME_AREA_START:NAME_AREA_START + 2] == b"\x81\x40", \
        "name area does not start with a full-width space"
    orig_ptrs = [struct.unpack_from("<I", exe, PTR_TABLE + i * 4)[0]
                 for i in range(16)]
    assert orig_ptrs[0] == RAM_BASE + NAME_AREA_START - FILE_BASE, \
        f"pointer table moved? first ptr {orig_ptrs[0]:#x}"
    # sanity: our encoder must reproduce the US EXE's bytes exactly
    assert to_fw("Danny").encode("shift_jis") == \
        bytes.fromhex("82638281828e828e8299"), "full-width encoder wrong"
    # repack the name area
    area = bytearray()
    new_ptrs = []
    for name in NAMES:
        s = to_fw(name).encode("shift_jis")
        new_ptrs.append(RAM_BASE + NAME_AREA_START + len(area) - FILE_BASE)
        area += s + b"\x00\x00"
        while len(area) % 4:
            area += b"\x00"
    total = len(area)
    assert NAME_AREA_START + total <= NAME_AREA_END, \
        f"name area overflows by {NAME_AREA_START + total - NAME_AREA_END} bytes"
    # Fill the remainder of the original area with full-width spaces
    # (81 40), NOT zeros: the game scans the name area and a run of
    # zeros reads as an empty string, which freezes the title -> menu
    # transition (bisected 2026-11-20: tests A-I; the 12-byte zero gap
    # was the sole cause). A spaces string is harmless.
    remainder = NAME_AREA_END - NAME_AREA_START - total
    assert remainder % 2 == 0, "remainder must be even for 81 40 fill"
    exe[NAME_AREA_START:NAME_AREA_START + total] = area
    exe[NAME_AREA_START + total:NAME_AREA_END] = b"\x81\x40" * (remainder // 2)
    for i, p in enumerate(new_ptrs):
        struct.pack_into("<I", exe, PTR_TABLE + i * 4, p)
    print(f"name area: {total} bytes used of "
          f"{NAME_AREA_END - NAME_AREA_START} "
          f"({NAME_AREA_END - NAME_AREA_START - total} spare)")
    for n, p in zip(NAMES, new_ptrs):
        print(f"  {n:14s} -> {p:#010x}")
    return bytes(exe)


def main():
    src = Path(sys.argv[sys.argv.index("--exe") + 1]) \
        if "--exe" in sys.argv else WORK / "tr1-files" / "SLPS_000.84"
    dst = Path(sys.argv[sys.argv.index("--out") + 1]) \
        if "--out" in sys.argv else WORK / "SLPS_000.84.en"
    data = src.read_bytes()
    patched = patch(data)
    dst.write_bytes(patched)
    print(f"wrote {dst} ({len(patched)} bytes)")


if __name__ == "__main__":
    main()
