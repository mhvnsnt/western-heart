#!/usr/bin/env python3
"""VPW2 params (30-byte) unpacker.

Layout reverse-engineered from the params unpack helper at ROM 0x800051CC
(main segment): it calls the MSB-first bit-reader (0x80004F64) 44 times
with fixed widths and stores each value into a 60-byte temp buffer.

Field list (call order; widths in bits; temp offset + store width):
  call 1:  3 bits, discarded (read and thrown away)
  calls 2..27: 4,3,4,4,3,3,3,5,4,4,4,4,4,4,4,4,4,4,4,3,5,3,3,4,3,3
               -> temp[0..25] as bytes
  call 28: 9 bits -> temp[26] as byte (low 8 bits stored; see note)
  call 29: 4 bits -> temp[28..29] as u16
  call 30: 4 bits -> temp[30] as byte
  call 31: 9 bits -> temp[31] as byte (low 8 bits stored; see note)
  call 32: 4 bits -> temp[32..33] as u16
  calls 33..37: 3,3,4,4,3 -> temp[34..38] as bytes
  call 38: 12 bits -> temp[39] as byte (low 8 bits stored; see note)
  calls 39..41: 12 bits each -> temp[40..41], [42..43], [44..45] as u16
  call 42: 32 bits -> temp[46..47] as u16 (low 16 bits stored; see note)
  call 43: 1 bit -> temp[48..51] as u32
  call 44: 1 bit -> temp[52..55] as u32 (also re-stored as u16 at 56..57)
Total: 229 bits of 240 (11 bits padding).

NOTE on truncated stores: the helper stores 9/12/32-bit reads with sb/sh,
keeping only the low 8/16 bits. Empirically (all 98 params files) the
discarded high bits are ALWAYS ZERO, so no information is lost — the
fields are effectively 8/16-bit values read with a wider window. Verified
in `check_truncation()`.
"""
import json
import struct
from pathlib import Path

# (width_bits, temp_offset, store) — store: 'b'=byte, 'h'=u16, 'w'=u32, None=discard
FIELDS = [
    (3, None, None),
    (4, 0, "b"), (3, 1, "b"), (4, 2, "b"), (4, 3, "b"), (3, 4, "b"),
    (3, 5, "b"), (3, 6, "b"), (5, 7, "b"), (4, 8, "b"), (4, 9, "b"),
    (4, 10, "b"), (4, 11, "b"), (4, 12, "b"), (4, 13, "b"), (4, 14, "b"),
    (4, 15, "b"), (4, 16, "b"), (4, 17, "b"), (4, 18, "b"), (3, 19, "b"),
    (5, 20, "b"), (3, 21, "b"), (3, 22, "b"), (4, 23, "b"), (3, 24, "b"),
    (3, 25, "b"), (9, 26, "b"), (4, 28, "h"), (4, 30, "b"), (9, 31, "b"),
    (4, 32, "h"), (3, 34, "b"), (3, 35, "b"), (4, 36, "b"), (4, 37, "b"),
    (3, 38, "b"), (12, 39, "b"), (12, 40, "h"), (12, 42, "h"), (12, 44, "h"),
    (32, 46, "h"), (1, 48, "w"), (1, 52, "w"),
]


class BitReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, n):
        v = 0
        for _ in range(n):
            byte = self.data[self.pos >> 3]
            bit = (byte >> (7 - (self.pos & 7))) & 1
            v = (v << 1) | bit
            self.pos += 1
        return v


def unpack_params(data):
    """Unpack a 30-byte params file -> (temp buffer 60 bytes, raw field values)."""
    assert len(data) == 30, len(data)
    br = BitReader(data)
    temp = bytearray(60)
    raw = []
    for width, off, store in FIELDS:
        v = br.read(width)
        raw.append(v)
        if off is None:
            continue
        if store == "b":
            temp[off] = v & 0xFF
        elif store == "h":
            struct.pack_into(">H", temp, off, v & 0xFFFF)
        elif store == "w":
            struct.pack_into(">I", temp, off, v & 0xFFFFFFFF)
    # call 44's value is also stored as u16 at temp[56]
    struct.pack_into(">H", temp, 56, raw[-1] & 0xFFFF)
    assert br.pos == 229, br.pos
    # padding bits must be zero
    assert br.read(11) == 0, "nonzero padding bits"
    return bytes(temp), raw


def check_truncation(raw_dir, manifest):
    """Verify the discarded high bits of the wide reads are always zero."""
    wide = {27: 8, 30: 8, 37: 8, 41: 16}  # field idx -> kept bits
    bad = 0
    n = 0
    for p in manifest["pairs"]:
        if p["kind"] != "params":
            continue
        data = (raw_dir / f"{p['file_id']}.bin").read_bytes()
        _temp, raw = unpack_params(data)
        n += 1
        for idx, kept in wide.items():
            if raw[idx] >> kept:
                bad += 1
                print(f"  TRUNCATION LOSS {p['file_id']} field {idx}: "
                      f"{raw[idx]} (kept {kept} bits)")
    print(f"truncation check: {n} params files, {bad} losses")
    return bad == 0


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from vpw2_moveset import MOVESET_DIR, RAW_DIR
    man = json.loads((MOVESET_DIR / "params_moveset_manifest.json").read_text())
    ok = check_truncation(RAW_DIR, man)
    print("truncation OK" if ok else "TRUNCATION LOSSES FOUND")
