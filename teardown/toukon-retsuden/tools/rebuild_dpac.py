#!/usr/bin/env python3
"""Rebuild DTPAC.PAC with the English PAC_GAME_MES + US TIM_END.

DPAC layout (verified):
  0x000 header: "DPAC", ver 0x100, count, table_size (count*32),
                data_size (file_size - 0x2000); rest zeros to 0x800
  0x800 entry table: count x 32 bytes (16-byte SJIS name, u32 size,
                u32 start_sector, u32 sector_count, u32 0)
  0x2000 data area: entries in table order, contiguous, each padded
                with zeros to a whole 2048-byte sector

CRITICAL (learned 2026-11-20): the game loads SOME entries by HARDCODED
sector number, not via the DPAC table (the title->menu transition hung
when entries after PAC_GAME_MES shifted down 5 sectors). So this rebuild
PRESERVES every entry's original start sector: the new PAC_GAME_MES
(13,848 B) is zero-padded to its original 12 sectors (24,576 B), and
the file keeps its original size. Only the bytes inside the two
replaced entries' original sector ranges change.

Replacements: PAC_GAME_MES -> the rebuilt English one (padded);
TIM_END -> the US "The End" TIM (same size, no pad needed).

Usage:
  python3 rebuild_dpac.py [--in <pac>] [--out <pac>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"

SECTOR = 0x800
HEADER_SIZE = 0x800

REPLACEMENTS = {
    "PAC_GAME_MES": WORK / "PAC_GAME_MES.en.bin",
    "TIM_END": WORK / "us-pac-tim" / "TIM_END.bin",
    # US staff credits (English) — same size/VRAM as JP, drop-in (M2, 2026-11-20)
    "TIM_STAFF": WORK / "us-pac-tim" / "TIM_STAFF.bin",
    "TIM_STAFF2": WORK / "us-pac-tim" / "TIM_STAFF2.bin",
    "TIM_STAFF3": WORK / "us-pac-tim" / "TIM_STAFF3.bin",
    "TIM_STAFF4": WORK / "us-pac-tim" / "TIM_STAFF4.bin",
    # EN menu atlas (slot 202) + US T3 staff lines (slot 204) (M2, 2026-11-20)
    "PAC_WRES": WORK / "PAC_WRES.en.bin",
}


def rebuild(orig: bytes, skip=frozenset()) -> bytes:
    assert orig[:4] == b"DPAC"
    _ver, count, table_size, _total = struct.unpack_from("<IIII", orig, 4)
    assert table_size == count * 32
    out = bytearray(orig)  # start from the original, patch in place
    for i in range(count):
        off = HEADER_SIZE + i * 32
        raw = orig[off:off + 32]
        name = raw[:16].rstrip(b" \x00").decode("shift_jis")
        size, start_sector, nsec, _d = struct.unpack_from("<IIII", raw, 16)
        if name not in REPLACEMENTS or name in skip:
            continue
        new_blob = REPLACEMENTS[name].read_bytes()
        capacity = nsec * SECTOR
        assert len(new_blob) <= capacity, f"{name}: {len(new_blob)} > {capacity}"
        dest = start_sector * SECTOR
        # zero the whole original sector range, then write the new blob
        out[dest:dest + capacity] = b"\x00" * capacity
        out[dest:dest + len(new_blob)] = new_blob
        # update the table size field (sector + count UNCHANGED)
        struct.pack_into("<I", out, off + 16, len(new_blob))
        print(f"{name}: {size} -> {len(new_blob)} bytes "
              f"(sector {start_sector}, {nsec} sectors, padded to {capacity})")
    print(f"new DTPAC.PAC: {len(out)} bytes ({len(out) // SECTOR} sectors, "
          f"same as original {len(orig)})")
    return bytes(out)


def main():
    args = sys.argv[1:]
    inp = WORK / "tr1-files" / "TOK" / "DTPAC.PAC"
    outp = WORK / "DTPAC.en.PAC"
    if "--in" in args:
        inp = Path(args[args.index("--in") + 1])
    if "--out" in args:
        outp = Path(args[args.index("--out") + 1])
    skip = frozenset(args[args.index("--skip") + 1].split(",")
                     ) if "--skip" in args else frozenset()
    orig = inp.read_bytes()
    new = rebuild(orig, skip)
    outp.write_bytes(new)
    # verify: only the two replaced entries' ranges differ
    diff_ranges = []
    i = 0
    while i < len(orig):
        if orig[i] != new[i]:
            j = i
            while j < len(orig) and orig[j] != new[j]:
                j += 1
            diff_ranges.append((i, j))
            i = j
        else:
            i += 1
    print(f"diff ranges vs original: {len(diff_ranges)}")
    for s, e in diff_ranges[:10]:
        print(f"  {s:#x}-{e:#x} ({e - s} bytes)")
    print(f"wrote {outp}")


if __name__ == "__main__":
    main()
