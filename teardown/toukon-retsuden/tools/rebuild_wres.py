#!/usr/bin/env python3
"""Rebuild PAC_WRES with the English T1 menu atlas (slot 202), the
English T2 results/messages atlas (slot 203), and the US English T3
staff-lines atlas (slot 204).

PAC_WRES layout (verified 2026-11-20):
  table_ptr = 0x29EEC, data_base = 0x2A2EC, 256 slots x 4 bytes.
  Slot s: offset = data_base + u16(table + s*4 + 8)*4,
          size   = u16(table + s*4 + 10)*4.
  Slots are packed contiguously, so a replacement MUST be exactly the
  original size (BPE dummy-block padding) or all later slots shift.

Replacements:
  slot 202 (T1, 7,388 B): EN atlas TIM, BPE-compressed to exactly 7,388 B.
  slot 203 (T2, 2,684 B): EN T2 TIM (US base + "IWGP CHAMPIONS"),
                          BPE-compressed to exactly 2,684 B.
  slot 204 (T3, 4,644 B): US slot 204 blob, padded to exactly 4,644 B
                          (US blob is smaller; zero-pad after the section
                          — the BPE header declares its own size).

Usage:
  python3 rebuild_wres.py [--in <pac_wres.bin>] [--out <pac_wres.en.bin>]
"""
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"
sys.path.insert(0, str(HERE))

from bpe_compress import compress_section_exact  # noqa: E402
from bpe import decompress_section  # noqa: E402

TABLE_PTR = 0x29EEC
DATA_BASE = 0x2A2EC


def container_layout(data):
    """Compute (table_ptr, data_base) from a PAC_WRES container's header."""
    v = struct.unpack_from("<I", data, 0x814)[0]
    table_ptr = 0x880 + v
    return table_ptr, table_ptr + 0x400


def slot_info(data, slot):
    table_ptr, data_base = container_layout(data)
    off_u = struct.unpack_from("<H", data, table_ptr + slot * 4 + 8)[0]
    sz_u = struct.unpack_from("<H", data, table_ptr + slot * 4 + 10)[0]
    return data_base + off_u * 4, sz_u * 4


def us_slot(data, slot):
    """Extract a slot blob from the US PAC_WRES (own table layout)."""
    off, size = slot_info(data, slot)
    return data[off:off + size]


def main():
    args = sys.argv[1:]
    inp = WORK / "pac_wres.jp.bin"
    outp = WORK / "PAC_WRES.en.bin"
    if "--in" in args:
        inp = Path(args[args.index("--in") + 1])
    if "--out" in args:
        outp = Path(args[args.index("--out") + 1])
    data = bytearray(inp.read_bytes())
    print(f"PAC_WRES: {len(data)} bytes")

    # --- slot 202: EN atlas, exact-size BPE ---
    off202, size202 = slot_info(data, 202)
    print(f"slot 202: offset {off202:#x}, size {size202}")
    en_tim = (WORK / "en-atlas.tim").read_bytes()
    comp202 = compress_section_exact(en_tim, size202)
    assert len(comp202) == size202, f"202: {len(comp202)} != {size202}"
    dec = decompress_section(comp202)
    assert dec == en_tim, "202 roundtrip FAILED"
    print(f"slot 202: EN atlas compressed to exactly {len(comp202)} B, "
          f"roundtrip OK")
    data[off202:off202 + size202] = comp202

    # --- slot 203: EN T2, exact-size BPE ---
    off203, size203 = slot_info(data, 203)
    print(f"slot 203: offset {off203:#x}, size {size203}")
    en_t2 = (WORK / "en-t2.tim").read_bytes()
    comp203 = compress_section_exact(en_t2, size203)
    assert len(comp203) == size203, f"203: {len(comp203)} != {size203}"
    dec203 = decompress_section(comp203)
    assert dec203 == en_t2, "203 roundtrip FAILED"
    print(f"slot 203: EN T2 compressed to exactly {len(comp203)} B, "
          f"roundtrip OK")
    data[off203:off203 + size203] = comp203

    # --- slot 204: US T3, padded to exact size ---
    off204, size204 = slot_info(data, 204)
    print(f"slot 204: offset {off204:#x}, size {size204}")
    us_data = (WORK / "us-pac_wres.bin").read_bytes()
    us204 = us_slot(us_data, 204)
    print(f"US slot 204: {len(us204)} B (JP: {size204} B)")
    assert len(us204) <= size204, "US slot 204 LARGER than JP — needs rebuild"
    padded204 = us204 + b"\x00" * (size204 - len(us204))
    data[off204:off204 + size204] = padded204
    print(f"slot 204: US T3 written, padded with {size204 - len(us204)} "
          f"zero bytes")

    outp.write_bytes(bytes(data))
    print(f"wrote {outp} ({len(data)} bytes, same size as original)")

    # Verify: only slots 202 + 204 differ.
    orig = inp.read_bytes()
    new = bytes(data)
    diffs = []
    i = 0
    while i < len(orig):
        if orig[i] != new[i]:
            j = i
            while j < len(orig) and orig[j] != new[j]:
                j += 1
            diffs.append((i, j))
            i = j
        else:
            i += 1
    print(f"diff ranges: {len(diffs)}")
    for s, e in diffs:
        print(f"  {s:#x}-{e:#x} ({e - s} B)")


if __name__ == "__main__":
    main()
