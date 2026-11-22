#!/usr/bin/env python3
"""Rebuild PAC_GAME_MES with the English banners + name sheet.

Reads the original JP PAC_GAME_MES and replaces 14 of its 19 BPE
sections IN PLACE with English content (12 US banner TIMs, the new
English name sheet, the new "Ring Out!" banner), keeping 5 sections
byte-identical (color tile, VS, digits x2, big digits x2).

CRITICAL (learned 2026-11-20, test N): the game reads PAC_GAME_MES
sections by HARDCODED file offsets, NOT via the WRES section table --
repacking the sections (even swapping in a genuine Yuke's-encoded US
section) freezes the game at the title screen. So each replacement is
written at its ORIGINAL offset and zero-padded to the ORIGINAL table
size; the table, the data total (0x884), and the file size (0x0C) stay
byte-identical to the original. Every replacement compresses smaller
than the original section, so all of them fit (asserted).

Slot map (JP slot -> content):
   0 color tile        keep JP      16 NO TIME LIMIT  US "NO LIMIT"
   1 name sheet        NEW English  17 WIN BY DQ      US "Disqualif.!"
   2 VS                keep JP      18 digits         keep JP
  10 WINNER            US "Winner"  19 TITLE WON      US "and new champ"
  11 TIME-UP DRAW      US "Time's   20 TITLE DEFENDED US "and still ch"
  12 GIVE UP           US "Opponent 21 CHAMPION       US "The Winner"
  13 REFEREE STOP      US "Referee  22 FINAL MATCH    US "Final Match!"
  14 RING OUT          NEW Ring Out 23 OFFICIAL DEC.  US "by split dec"
  15 DOUBLE RING OUT   US "Double   30 big digits     keep JP
                          Ring Out!" 31 big digits     keep JP

Usage:
  python3 rebuild_gamemes.py [--in <pac>] [--out <pac>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"
sys.path.insert(0, str(HERE))
from bpe import decompress_section
from bpe_compress import compress_section_exact

DATA_START = 0xC80
TABLE_OFF = 0x888
TOTAL_OFF = 0x884

# JP slot -> (original BPE section index, replacement TIM or None=keep)
# Original section order in the file: bpe00..bpe18 map to slots
# 0,1,2,10,11,12,13,14,15,16,17,18,19,20,21,22,23,30,31.
SLOT_TO_BPE = {0: 0, 1: 1, 2: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 7,
               15: 8, 16: 9, 17: 10, 18: 11, 19: 12, 20: 13, 21: 14,
               22: 15, 23: 16, 30: 17, 31: 18}

REPLACEMENTS = {
    1: WORK / "new-namesheet.tim",
    10: WORK / "us-bigmes-tim" / "big10_0x9f00.bin",    # Winner
    11: WORK / "us-bigmes-tim" / "big02_0x2d00.bin",    # Time's up!
    12: WORK / "us-bigmes-tim" / "big03_0x3d40.bin",    # Opponent gives up!
    13: WORK / "us-bigmes-tim" / "big08_0x8680.bin",    # Referee stops match!
    14: WORK / "new-ringout.tim",                        # Ring Out!
    15: WORK / "us-bigmes-tim" / "big07_0x7640.bin",    # Double Ring Out!
    16: WORK / "us-gamemes-dec" / "bpe02_0x17b4.bin",   # NO LIMIT
    17: WORK / "us-bigmes-tim" / "big04_0x4d80.bin",    # Disqualification!
    19: WORK / "us-bigmes-tim" / "big01_0x1cc0.bin",    # and new champion
    20: WORK / "us-bigmes-tim" / "big00_0xc80.bin",     # and still champion
    21: WORK / "us-bigmes-tim" / "big11_0xa040.bin",    # The Winner
    22: WORK / "us-bigmes-tim" / "big05_0x5dc0.bin",    # Final Match!
    23: WORK / "us-bigmes-tim" / "big09_0x96c0.bin",    # by split decision
}


def read_table(data):
    """Return {slot: (offset, size)} from the section table."""
    table = {}
    for slot in range(32):
        off4, size4 = struct.unpack_from("<HH", data, TABLE_OFF + slot * 4)
        if size4:
            table[slot] = (DATA_START + off4 * 4, size4 * 4)
    return table


def transplant_jp_header(jp_tim: bytes, us_tim: bytes) -> bytes:
    """Build an English banner TIM on the JP TIM's header + palette.

    The US (Power Move) banner TIMs use a DIFFERENT CLUT VRAM location
    (240, 480-491) and a different palette (white/black/red/gray) than
    the JP banners (CLUT at (736, 256), 16-color gradient palette).
    The JP game draws banners from the JP CLUT location; a US TIM used
    as-is uploads its palette to the wrong VRAM and the game hangs at
    the title->menu transition (bisected 2026-11-20, tests AO/AP/AR).

    Fix: keep the JP TIM's full 0x34-byte header (magic, flags, CLUT
    coords, CLUT data) + image header, but use the US pixel data with
    indices remapped to the JP palette:
      US 0 (white text) -> JP 1 (white, 0x7FFF)
      US 1 (black bg)   -> JP 0 (black, 0x0000)
      US 2 (red accent) -> JP 2 (set to pure red 0x001F)
      US 3-15 (unused)  -> unchanged (JP gradient entries)
    The JP CLUT entry 2 is overwritten with pure red so the US red
    accent renders correctly. Pixel data starts at offset 0x40 in
    both TIMs (12-byte TIM header + 44-byte CLUT section + 12-byte
    image header = 68 bytes; verified for all banner TIMs).
    """
    assert len(jp_tim) == len(us_tim), "TIM sizes must match"
    assert jp_tim[:4] == b"\x10\x00\x00\x00", "not a TIM"
    assert us_tim[:4] == b"\x10\x00\x00\x00", "not a TIM"
    out = bytearray(jp_tim[:0x40])
    # JP CLUT entry 2 (offset 0x14 + 2*2 = 0x18) -> pure red 0x001F.
    out[0x18:0x1A] = b"\x1f\x00"
    # Remap US pixels: swap nibbles 0<->1, keep 2-15.
    # Nibble swap table: 0->1, 1->0, others identity.
    remap = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    px = us_tim[0x40:]
    new_px = bytearray(len(px))
    for i, b in enumerate(px):
        new_px[i] = (remap[b & 0x0F]) | (remap[(b >> 4) & 0x0F] << 4)
    out += new_px
    assert len(out) == len(jp_tim)
    return bytes(out)


def rebuild(orig: bytes) -> bytes:
    table = read_table(orig)
    assert set(table) == set(SLOT_TO_BPE), \
        f"table slots {sorted(table)} != expected {sorted(SLOT_TO_BPE)}"
    # IN-PLACE replacement: each new section goes at its original offset,
    # padded to EXACTLY the original section's total length. The header
    # (incl. the table), the data total, and the file size are NEVER
    # touched. Exact length is REQUIRED: the game reads BPE sections
    # SEQUENTIALLY, advancing by each section's csize -- a section even
    # 1 byte longer or shorter desyncs every following section and hangs
    # the game (bisected 2026-11-20, tests W2/Z/AA/AB/AC/AD).
    out = bytearray(orig)
    for slot in sorted(table):
        off, size = table[slot]
        if slot not in REPLACEMENTS:
            print(f"slot {slot:2d}: keep JP ({size}B)")
            continue
        tim = REPLACEMENTS[slot].read_bytes()
        # US-sourced TIMs (big-mes banners + NO LIMIT) need the JP
        # header + palette transplanted (see transplant_jp_header).
        # The name sheet (slot 1) and Ring Out banner (slot 14) were
        # built on JP headers already and are used as-is.
        if slot not in (1, 14):
            orig_csize_pre = struct.unpack_from("<I", orig, off + 8)[0]
            jp_tim = decompress_section(
                orig[off:off + 16 + orig_csize_pre])
            tim = transplant_jp_header(jp_tim, tim)
        # Original section total length = 16-byte header + csize.
        orig_csize = struct.unpack_from("<I", orig, off + 8)[0]
        orig_total = 16 + orig_csize
        sec = compress_section_exact(tim, orig_total)
        # verify the replacement decompresses to the same TIM size
        # as the original section (same VRAM layout)
        orig_ds = struct.unpack_from("<I", orig, off + 12)[0]
        assert len(tim) == orig_ds, \
            (f"slot {slot}: replacement TIM {len(tim)}B != "
             f"original {orig_ds}B")
        assert len(sec) == orig_total, \
            (f"slot {slot}: compressed {len(sec)}B != original "
             f"{orig_total}B -- exact length required")
        out[off:off + size] = b"\x00" * size
        out[off:off + len(sec)] = sec
        print(f"slot {slot:2d}: NEW {REPLACEMENTS[slot].name} "
              f"{len(tim)} -> {len(sec)}B (exact, was {orig_total}B)")
    assert bytes(out[:DATA_START]) == orig[:DATA_START], \
        "header changed -- in-place rebuild must not touch it"
    assert len(out) == len(orig), "file size changed"
    print(f"new PAC_GAME_MES: {len(out)} bytes (same as original)")
    return bytes(out)


def main():
    src = Path(sys.argv[sys.argv.index("--in") + 1]) \
        if "--in" in sys.argv else WORK / "pac-entries" / "PAC_GAME_MES.bin"
    dst = Path(sys.argv[sys.argv.index("--out") + 1]) \
        if "--out" in sys.argv else WORK / "PAC_GAME_MES.en.bin"
    data = src.read_bytes()
    new = rebuild(data)
    dst.write_bytes(new)
    print(f"wrote {dst} ({len(new)} bytes)")


if __name__ == "__main__":
    main()
