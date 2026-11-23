#!/usr/bin/env python3
"""SFxT (.bac/.bcm) parser — reverse-engineered from the real SFxT PC files.

VERIFIED against Street Fighter X Tekken PC (archive.org
street-fighter-x-tekken_202508), character RYU, 2026-11-22:

BCM (#BCM) header — DIFFERS from SSFIV AE (dantarion/bcm.py, Ono! BCMFile.cs):
  AE:  "#BCM" + FE FF + u16(40) + u16(1) + u16(1) + i32(0)
       + 4H counts @16 + 8I offsets @24
  SFxT:"#BCM" + FE FF + u16(76) + u16(0) + u16(0)
       + 4H counts @12 + 8I offsets @20
  (AE's 4-byte zero int32 at 12-15 is GONE; the counts/offsets block
  shifts 4 bytes earlier: counts 16->12, offsets 24->20.)
  counts @12 = (ChargeCount, InputMotions-1, Moves, CancelLists)
  offsets @20 = (ChargeOff, ChargeNamesOff, InputOff, InputNamesOff,
                 MoveOff, MoveNamesOff, CancelOff, CancelNamesOff)
  RYU: counts (0, 12, 92, 52); offsets (0, 0, 76, 124, 172, 540, 908, 1116).
  Every table size is an exact multiple of its count, and the layout is
  fully contiguous: header -> offset tables -> input motions (1056B each)
  -> moves (64B each) -> cancels (16B each) -> string pool.
  The 8 header offsets point at OFFSET TABLES (arrays of u32 record
  pointers), NOT directly at the records (unlike AE).

BAC (#BAC) header — DIFFERS from SSFIV AE (dantarion/bac.py, Ono! BACFile.cs):
  AE:  "#BAC" + FE FF + u16(40) + u16(1) + u16(1)
       + ScriptCount H @12, VFXScriptCount H @14, HitboxTableSize I @16
       + 5I offsets @20 (Script, VFX, ScriptName, VFXName, HitboxTable)
  SFxT:"#BAC" + FE FF + u16(32) + u16(0) + u16(0)
       + u16(1) @12, ScriptCount H @14 (=152), u32(32) @16
       + 5I offsets @20 = (36, 40, 648, 1256, 244476)
       ScriptOffsetTable @40 (152 u32, 74 nonzero), ScriptNameTable @648
       (152 u32, 74 nonzero) — nonzero indices ALIGN EXACTLY.
       @36 is the u32 just before the table (value 244476 = string pool).
       @1256 = VFX table (first u32 garbage 0x052CFFFF; entries from 1264).
       @244476 = string pool (NOT a hitbox table: ASCII 'NORMAL'...).
  Script BODY (at each @40 offset): 20 u32s forming 10 (frameOff, dataOff)
  pairs, then the frame/data blocks; the script span ends exactly at the
  next script's offset. The per-list record layout is NOT yet decoded
  (see notes in output JSON); the 20-u32 directory is preserved verbatim.

Move record (64B, SFxT) — field map derived by comparing 5LP/TC_5LP/5LPF/5LK:
  +0  H Input (button bits: 16=LP, 128=LK)
  +2  H MoveFlags (0x1010)
  +4  H PositionRestriction (2=stand, 1=fwd?)
  +6  H Restriction (0)
  +8  I Unk1 (0)
  +12 f UnkF32a (0.8, constant here)
  +16 I Unk (0)
  +20 H Unk (0)
  +22 H Unk (0)
  +24 H Unk (0)
  +26 H Unk (0)
  +28 h EXRequirement? (-1 = 0xFFFF)
  +30 H RefA (256=5LP, 500=TC_5LP, 262=5LPF, 259=5LK; TC = base+244)
  +32 H RefB (12 for punches, 15 for 5LK)
  +34 h -1
  +36 H 0
  +38 H RefC (134=5LP, 135=5LPF, 136=5LK; consecutive per move)
  +40 I 0
  +44 f UnkF32b (0.55=5LP, 1.0=5LPF, 1.05=5LK)
  +48 f UnkF32c (1.75=5LP, 1.45=5LPF, 0.6=5LK)
  +52 H 4
  +54 H 0
  +56 h -1
  +58 H 0x1400 (5120)
  +60 I 0
  RefA/RefB/RefC semantics (script vs anim vs cancel index) are UNVERIFIED
  — recorded raw, never guessed.

InputMotion record (1056B each, ~97% zeros): first u32 = 16, then 12-byte
entries; entry[1] carries direction flags (8=fwd, 4=back, 2=down) but
entry[0] does not fit the AE (Type,Buffer,Input,MoveFlags,Flags,Req) layout
(values 276/536/796). Recorded raw (first 64 bytes) + best-effort entries.

Cancel record (16B each): recorded raw hex (layout not yet decoded).
Cancel names are real ('RAPID_L', 'JUMP_9MP', 'AIR_TATUMAKI', ...).

Usage: python3 sfxt_bcm.py <file.bcm> [--out out.json]
         python3 sfxt_bcm.py --dir <dir> --out <outdir>   (all .bcm, skip .eff)
"""
import json
import os
import struct
import sys


def cstr(data, off):
    if off <= 0 or off >= len(data):
        return ""
    end = data.find(b"\x00", off)
    if end < 0:
        end = len(data)
    try:
        return data[off:end].decode("ascii")
    except UnicodeDecodeError:
        return data[off:end].decode("ascii", "replace")


def parse_bcm(path):
    data = open(path, "rb").read()
    if data[:4] != b"#BCM":
        raise ValueError("not #BCM: %s" % path)
    endian = "<"  # SFxT PC is little-endian (FE FF)
    counts = struct.unpack(endian + "4H", data[12:20])
    offsets = struct.unpack(endian + "8I", data[20:52])
    charge_count, input_count_m1, move_count, cancel_count = counts
    (charge_off, charge_names_off, input_off, input_names_off,
     move_off, move_names_off, cancel_off, cancel_names_off) = offsets
    result = {
        "file": os.path.basename(path),
        "format": "sfxt-bcm",
        "header_u16_at_6": struct.unpack(endian + "H", data[6:8])[0],
        "counts": {"charges": charge_count,
                   "input_motions_incl_none": input_count_m1 + 1,
                   "moves": move_count, "cancel_lists": cancel_count},
        "offsets": {"charges": charge_off, "charge_names": charge_names_off,
                    "inputs": input_off, "input_names": input_names_off,
                    "moves": move_off, "move_names": move_names_off,
                    "cancels": cancel_off, "cancel_names": cancel_names_off},
        "input_motions": [], "moves": [], "cancel_lists": [],
    }
    input_tbl = struct.unpack(endian + "%dI" % input_count_m1,
                              data[input_off:input_off + 4 * input_count_m1])
    input_name_tbl = struct.unpack(
        endian + "%dI" % input_count_m1,
        data[input_names_off:input_names_off + 4 * input_count_m1])
    for i, (off, noff) in enumerate(zip(input_tbl, input_name_tbl)):
        rec = data[off:off + 1056]
        first_u32, = struct.unpack(endian + "I", rec[0:4])
        entries = []
        for e in range(min(first_u32, 16)):
            base = 4 + e * 12
            if base + 12 > len(rec):
                break
            entries.append(list(struct.unpack(endian + "6H", rec[base:base + 12])))
        result["input_motions"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "first_u32": first_u32,
            "entries_best_effort_6H": entries,
            "raw_first_64_hex": rec[:64].hex(),
        })
    move_tbl = struct.unpack(endian + "%dI" % move_count,
                             data[move_off:move_off + 4 * move_count])
    move_name_tbl = struct.unpack(endian + "%dI" % move_count,
                                  data[move_names_off:move_names_off + 4 * move_count])
    for i, (off, noff) in enumerate(zip(move_tbl, move_name_tbl)):
        rec = data[off:off + 64]
        h = struct.unpack(endian + "32H", rec)
        f12, = struct.unpack(endian + "f", rec[12:16])
        f44, = struct.unpack(endian + "f", rec[44:48])
        f48, = struct.unpack(endian + "f", rec[48:52])
        result["moves"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "input_bits": h[0], "move_flags": h[1],
            "position_restriction": h[2], "restriction": h[3],
            "unk_u32_at_8": struct.unpack(endian + "I", rec[8:12])[0],
            "unk_f32_at_12": f12,
            "unk_h_at_28": h[14], "ref_a_h_at_30": h[15],
            "ref_b_h_at_32": h[16], "unk_h_at_34": h[17],
            "ref_c_h_at_38": h[19],
            "unk_f32_at_44": f44, "unk_f32_at_48": f48,
            "unk_h_at_52": h[26], "unk_h_at_58": h[29],
            "raw_hex": rec.hex(),
        })
    cancel_tbl = struct.unpack(endian + "%dI" % cancel_count,
                               data[cancel_off:cancel_off + 4 * cancel_count])
    cancel_name_tbl = struct.unpack(
        endian + "%dI" % cancel_count,
        data[cancel_names_off:cancel_names_off + 4 * cancel_count])
    for i, (off, noff) in enumerate(zip(cancel_tbl, cancel_name_tbl)):
        rec = data[off:off + 16] if off else b""
        result["cancel_lists"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "raw_hex": rec.hex(),
        })
    return result


def parse_bac_tables(path):
    """Header + script tables only (script bodies not yet decoded)."""
    data = open(path, "rb").read()
    if data[:4] != b"#BAC":
        raise ValueError("not #BAC: %s" % path)
    endian = "<"
    script_count, = struct.unpack(endian + "H", data[14:16])
    u32_at_16, = struct.unpack(endian + "I", data[16:20])
    offsets = struct.unpack(endian + "5I", data[20:40])
    off_tbl = struct.unpack(endian + "%dI" % script_count,
                            data[offsets[1]:offsets[1] + 4 * script_count])
    name_tbl = struct.unpack(endian + "%dI" % script_count,
                             data[offsets[2]:offsets[2] + 4 * script_count])
    scripts = []
    for i, (off, noff) in enumerate(zip(off_tbl, name_tbl)):
        entry = {"index": i, "name": cstr(data, noff) if noff else "",
                 "offset": off}
        if off:
            directory = struct.unpack(endian + "20I", data[off:off + 80])
            # script span ends at the next nonzero offset
            nxt = [o for o in off_tbl[i + 1:] if o]
            end = min(nxt) if nxt else len(data)
            entry["span_bytes"] = end - off
            entry["directory_20u32"] = list(directory)
        scripts.append(entry)
    return {
        "file": os.path.basename(path),
        "format": "sfxt-bac-tables",
        "header_u16_at_6": struct.unpack(endian + "H", data[6:8])[0],
        "u16_at_12": struct.unpack(endian + "H", data[12:14])[0],
        "script_count": script_count,
        "u32_at_16": u32_at_16,
        "offsets": {"field_20": offsets[0], "script_table": offsets[1],
                    "script_name_table": offsets[2],
                    "vfx_table": offsets[3], "string_pool": offsets[4]},
        "scripts": scripts,
        "note": "script bodies NOT decoded: 20-u32 directory preserved "
                "verbatim; per-list record layout is an open RE task.",
    }


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    outdir = None
    indir = None
    if "--out" in argv:
        outdir = argv[argv.index("--out") + 1]
    if "--dir" in argv:
        indir = argv[argv.index("--dir") + 1]
    if indir:
        os.makedirs(outdir, exist_ok=True)
        n_ok = n_fail = n_skip = 0
        for root, _dirs, files in os.walk(indir):
            for fn in sorted(files):
                low = fn.lower()
                if low.endswith(".eff.bac") or low.endswith(".eff.bcm"):
                    n_skip += 1
                    continue
                if low.endswith(".bcm"):
                    parse, suffix = parse_bcm, ".sfxt-bcm.json"
                elif low.endswith(".bac"):
                    parse, suffix = parse_bac_tables, ".sfxt-bac.json"
                else:
                    continue
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, indir)
                try:
                    res = parse(path)
                except Exception as exc:  # noqa: BLE001 - report and continue
                    print("FAIL %s: %s" % (rel, exc))
                    n_fail += 1
                    continue
                outp = os.path.join(outdir, rel.rsplit(".", 1)[0] + suffix)
                os.makedirs(os.path.dirname(outp), exist_ok=True)
                with open(outp, "w") as fh:
                    json.dump(res, fh, indent=1)
                n_ok += 1
        print("sfxt: ok=%d fail=%d skipped_eff=%d" % (n_ok, n_fail, n_skip))
        return 0
    if not args:
        print(__doc__)
        return 2
    if args[0].lower().endswith(".bac"):
        res = parse_bac_tables(args[0])
    else:
        res = parse_bcm(args[0])
    if outdir:
        with open(outdir, "w") as fh:
            json.dump(res, fh, indent=1)
    else:
        print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
