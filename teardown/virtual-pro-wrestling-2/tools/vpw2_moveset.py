#!/usr/bin/env python3
"""VPW2 bit-packed moveset/params decoder.

Reverse-engineered from the VPW2 ROM code (main segment):
- Encoder 0x80005578, decoder 0x8000632C, bit-writer 0x80004D60,
  bit-reader 0x80004F64, style table @ ROM 0x3E524 (3 pointers).
- Bit order: MSB-first within each byte; first bit read = MSB of value.
- Per movegroup record (10 bytes: u16 move_id + 4x u16 menu items):
  read (maxbits+5) bits, where maxbits = max(bitpacking_main[item])
  over the record's nonzero menu items.
  value layout (high -> low): flags(3) | slot(2) | mod_index(maxbits).
  - slot selects which of the record's 4 menu items applies.
  - mod_index indexes MasterMoveMods[item] -> u16 "mod value" (multiple of 10).
  - flags -> bytes 2,3,4 of the decoded 6-byte move record.
- Decoded output: 292 x 6-byte records indexed by move_id:
  {u16 mod_value, u8 flag2, u8 flag3, u8 flag4, u8 pad?}.
- File = bitstream padded with zero bits to a whole byte, sometimes +1
  trailing 0x00 byte (combo 180B, most shoot 126B).

Tables (in-repo under teardown/virtual-pro-wrestling-2/moveset/):
  bitpacking_main.bin, bitpacking_movegroup_{wrestling,combo,shoot}.bin,
  master_movemods.bin, master_movemod_pointers.bin,
  master_movemods_first_entries.bin
"""

import json
import os
import struct
from pathlib import Path

# Resolve the VPW2 teardown tree: VPW2_DIR env var, else the repo layout
# (this script lives in teardown/virtual-pro-wrestling-2/tools/).
def _find_root():
    env = os.environ.get("VPW2_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "moveset" / "bitpacking_main.bin").exists():
            return parent
    return here.parent.parent  # best effort; load_tables will fail loudly


ROOT = _find_root()
MOVESET_DIR = ROOT / "moveset"
RAW_DIR = ROOT / "raw"

N_MOVES = 292  # decoder zeroes 0x124 records

STYLES = ("wrestling", "combo", "shoot")


def load_tables(d=MOVESET_DIR):
    main = struct.unpack(">134H", (d / "bitpacking_main.bin").read_bytes())
    groups = {}
    for style in STYLES:
        data = (d / f"bitpacking_movegroup_{style}.bin").read_bytes()
        recs = [
            struct.unpack(">5H", data[i * 10 : (i + 1) * 10])
            for i in range(len(data) // 10)
        ]
        groups[style] = [r for r in recs if r[0] != 0xFFFF]
    mm = (d / "master_movemods.bin").read_bytes()
    u16 = struct.unpack(f">{len(mm)//2}H", mm)
    mods = []
    cur = []
    for v in u16:
        if v == 0xFFFF:
            mods.append(cur)
            cur = []
        else:
            cur.append(v)
    if cur:
        mods.append(cur)
    fe = struct.unpack(
        ">133H", (d / "master_movemods_first_entries.bin").read_bytes()
    )
    return main, groups, mods, fe


class BitReader:
    """MSB-first bit reader matching ROM 0x80004F64."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0  # bit position

    def read(self, n: int) -> int:
        v = 0
        for _ in range(n):
            byte = self.data[self.pos >> 3]
            bit = (byte >> (7 - (self.pos & 7))) & 1
            v = (v << 1) | bit
            self.pos += 1
        return v

    def bits_left(self) -> int:
        return len(self.data) * 8 - self.pos


def style_for_length(nbytes: int) -> str:
    """Style from moveset file length (edit-mode files confirm the map)."""
    if nbytes == 176:
        return "wrestling"
    if nbytes == 180:
        return "combo"
    if nbytes in (125, 126):
        return "shoot"
    raise ValueError(f"unknown moveset length {nbytes}")


def decode_moveset(data: bytes, tables=None):
    """Decode one moveset file.

    Returns dict with style, per-move records, bit accounting, validity.
    """
    main, groups, mods, _fe = tables or load_tables()
    style = style_for_length(len(data))
    recs = groups[style]
    br = BitReader(data)
    moves = {}  # move_id -> record
    invalid = []
    for rec in recs:
        move_id, items = rec[0], rec[1:]
        nz = [i for i in items if i != 0]
        maxbits = max(main[i] for i in nz) if nz else 0
        nbits = maxbits + 5
        v = br.read(nbits)
        mod_index = v & ((1 << maxbits) - 1) if maxbits else 0
        slot = (v >> maxbits) & 3
        flags = (v >> (maxbits + 2)) & 7
        item = items[slot]
        grp = mods[item] if item < len(mods) else []
        if mod_index >= len(grp):
            invalid.append((move_id, item, mod_index, len(grp)))
            mod_value = None
        else:
            mod_value = grp[mod_index]
        moves[move_id] = {
            "move_id": move_id,
            "menu_item": item,
            "slot": slot,
            "mod_index": mod_index,
            "mod_value": mod_value,
            "flags": flags,
            "flag2": flags & 1,
            "flag3": (flags >> 1) & 1,
            "flag4": (flags >> 2) & 1,
            "maxbits": maxbits,
        }
    # trailing bits must be zero padding
    tail = br.read(br.bits_left()) if br.bits_left() else 0
    return {
        "style": style,
        "moves": moves,
        "bits_used": br.pos - br.bits_left() if False else None,
        "total_bits": sum(
            (max(main[i] for i in r[1:] if i != 0) + 5) for r in recs
        ),
        "file_bits": len(data) * 8,
        "trailing_bits": br.bits_left(),
        "trailing_value": tail,
        "invalid": invalid,
    }


def main():
    import sys

    tables = load_tables()
    man = json.loads((MOVESET_DIR / "params_moveset_manifest.json").read_text())
    n_ok = n_bad = 0
    bad_files = []
    for p in man["pairs"]:
        if p["kind"] != "moveset":
            continue
        data = (RAW_DIR / f"{p['file_id']}.bin").read_bytes()
        res = decode_moveset(data, tables)
        n_moves = len(res["moves"])
        n_set = sum(
            1 for m in res["moves"].values() if m["mod_value"] not in (None, 0)
        )
        ok = not res["invalid"] and res["trailing_value"] == 0
        if ok:
            n_ok += 1
        else:
            n_bad += 1
            bad_files.append(
                (p["file_id"], p["wrestler_id4"], res["style"],
                 len(res["invalid"]), res["trailing_value"])
            )
        if "--verbose" in sys.argv:
            print(
                f"{p['file_id']} id4={p['wrestler_id4']} {res['style']:9s} "
                f"moves={n_moves} set={n_set} bits={res['total_bits']}/{res['file_bits']} "
                f"invalid={len(res['invalid'])} tail={res['trailing_value']}"
            )
    print(f"valid: {n_ok}/98, bad: {n_bad}")
    for b in bad_files[:20]:
        print("  BAD:", b)


if __name__ == "__main__":
    main()
