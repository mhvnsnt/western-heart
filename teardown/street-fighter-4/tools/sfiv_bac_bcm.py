#!/usr/bin/env python3
"""Vanilla SFIV (.bac/.bcm) parser — reverse-engineered from the real files.

Vanilla SFIV (Build 3584) stores character data in *.cmn.emz (zlib raw-deflate
after a 16-byte header; see kaggle-sfiv-v2). The decompressed payload is one
#EMB container; #BAC/#BCM are carved out of it (see extract_sfiv_v2.py).

VERIFIED against carved RYU/AGL (2026-11-22):

BAC (#BAC) header — DIFFERS from SSFIV AE (dantarion/bac.py) AND from SFxT:
  AE:  "#BAC" + FE FF + u16(40) + u16(1) + u16(1)
       + ScriptCount H @12, VFXScriptCount H @14, HitboxTableSize I @16
       + 5I offsets @20
  SFIV:"#BAC" + FE FF + u16(24) + u16(tableCount) + u16(field10)
       + u32 scriptOffTbl @12 + u32 scriptNameTbl @16 + u32 thirdTbl @20
       + 4x u32(0) @24..40 + 6 floats @40...
  RYU: tableCount=687, field10=132, scriptOffTbl=696, scriptNameTbl=3444,
  thirdTbl=6192. Both tables have 687 entries; 196 nonzero, and the nonzero
  indices ALIGN EXACTLY. First scripts: STAND @6720, CROUCH @7024, ...
  Third table @6192: 63 entries, targets spaced 768 B (VFX scripts?).
  field10 (132) is NOT the nonzero count (196) — meaning unknown.
  Script BODY: header (first,last,iasa,total HHHH) + 12 zero bytes + X u16
  + numLists u16, then numLists x 12-byte directory entries in VANILLA order:
  (frameOff u32, type u16, count u16, dataOff u32) — AE has
  (type, count, frameOff, dataOff). Types match AE's enum exactly
  (1=ANIMATION, 2=TRANSITION, 3=STATE, 4=SPEED, 6=HURTBOX, 7=PHYSICS,
  10=INVINC) and appear in ascending order. The frameOff/dataOff BASE is
  NOT yet resolved (script-relative, +24-relative, and directory-end-relative
  all fail to yield sane frames+data); the header fields + directory are
  preserved verbatim and the body decode is an open RE task (same class as
  the SFxT script body). 5LP: first=9 last=12 iasa=26 total=32 (header reads
  sane at delta 0).

BCM (#BCM) header — DIFFERS from AE and SFxT:
  AE:  "#BCM" + FE FF + u16(40) + u16(1) + u16(1) + i32(0)
       + 4H counts @16 + 8I offsets @24
  SFIV:"#BCM" + FE FF + u16(48) + u16(0) + 4H counts @10 + 7I offsets @20
  counts @10 = (InputMotions-1, Moves, CancelLists, 0)
  offsets @20 = (ChargeOff=0, InputOff, InputNamesOff, MoveOff,
                 MoveNamesOff, CancelOff, CancelNamesOff)
  RYU: counts (7, 65, 15, 0); offsets (0, 48, 1420, 1448, 6388, 6648, 6768).
  bytes 6-7 (48) = InputOff (first table), like SFxT's 76.
  InputMotion records: 196 B each (count I + 16 x 12 B entries — same size
  as AE; the first u32 reads 0xC0000, entry layout UNVERIFIED; recorded raw).
  Move records: 76 B each. MoveOff..MoveNamesOff = 65 x 76 B exactly.
  Cancel records: 8 B each (raw).
  Input bits use the AE layout (util.py): LP=0x40, MP=0x80, HP=0x100,
  LK=0x200, MK=0x400, HK=0x800; down=0x04, back=0x08, fwd=0x10, up=0x02.
  (Verified: 2LP=0x44=LP+down, 6MP=0x90=MP+fwd, THROW=LP+LK.)
  Move record fields (verified by comparing 5LP/5MP/5HP/5LK/5MK/5HK/2LP/6MP):
  +0 H input_bits, +2 H move_flags (0x1010 normals, 0x1411 crouch,
  0x1412 command normals, 0x5010-ish specials), +4 H position_restriction
  (2=stand, 1=forward, 0=any), +6 H unk (3), +8 I 0, +12 f 1.2,
  +24 h -1, +26 h -1, +28 H ref_a (256=5LP, 257=5MP, ... — SAME values as
  SFxT ref_a for the same moves), +30 H 0, +32 H button_index
  (1,2,4,8,16,32 = LP,MP,HP,LK,MK,HK), +34 H (64 or 0). Rest recorded raw.

Usage: python3 sfiv_bac_bcm.py --dir <carved-dir> --out <outdir>
       python3 sfiv_bac_bcm.py <file.bac|file.bcm> [--out out.json]
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
    endian = "<"
    counts = struct.unpack(endian + "4H", data[10:18])
    offsets = struct.unpack(endian + "7I", data[20:48])
    input_count_m1, move_count, cancel_count, _zero = counts
    (charge_off, input_off, input_names_off, move_off, move_names_off,
     cancel_off, cancel_names_off) = offsets
    result = {
        "file": os.path.basename(path),
        "format": "sfiv-bcm",
        "header_u16_at_6": struct.unpack(endian + "H", data[6:8])[0],
        "counts": {"input_motions_incl_none": input_count_m1 + 1,
                   "moves": move_count, "cancel_lists": cancel_count,
                   "fourth_count": _zero},
        "offsets": {"charges": charge_off, "inputs": input_off,
                    "input_names": input_names_off, "moves": move_off,
                    "move_names": move_names_off, "cancels": cancel_off,
                    "cancel_names": cancel_names_off},
        "input_motions": [], "moves": [], "cancel_lists": [],
    }
    input_tbl = None  # motions are records, not an offset table
    input_name_tbl = struct.unpack(
        endian + "%dI" % input_count_m1,
        data[input_names_off:input_names_off + 4 * input_count_m1])
    for i, noff in enumerate(input_name_tbl):
        off = input_off + i * 196
        rec = data[off:off + 196]
        first_u32, = struct.unpack(endian + "I", rec[0:4])
        result["input_motions"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "first_u32": first_u32,
            "raw_first_64_hex": rec[:64].hex(),
        })
    move_name_tbl = struct.unpack(endian + "%dI" % move_count,
                                  data[move_names_off:move_names_off + 4 * move_count])
    for i, noff in enumerate(move_name_tbl):
        off = move_off + i * 76
        rec = data[off:off + 76]
        h = struct.unpack(endian + "38H", rec)
        f12, = struct.unpack(endian + "f", rec[12:16])
        result["moves"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "input_bits": h[0], "move_flags": h[1],
            "position_restriction": h[2], "unk_h_at_6": h[3],
            "unk_f32_at_12": f12,
            "unk_h_at_24": h[12], "unk_h_at_26": h[13],
            "ref_a_h_at_28": h[14], "unk_h_at_30": h[15],
            "button_index_h_at_32": h[16], "unk_h_at_34": h[17],
            "raw_hex": rec.hex(),
        })
    cancel_name_tbl = struct.unpack(
        endian + "%dI" % cancel_count,
        data[cancel_names_off:cancel_names_off + 4 * cancel_count])
    for i, noff in enumerate(cancel_name_tbl):
        off = cancel_off + i * 8
        rec = data[off:off + 8]
        result["cancel_lists"].append({
            "index": i, "name": cstr(data, noff), "offset": off,
            "raw_hex": rec.hex(),
        })
    return result


def parse_bac_tables(path):
    """Header + script tables + per-script header/directory (bodies not decoded)."""
    data = open(path, "rb").read()
    if data[:4] != b"#BAC":
        raise ValueError("not #BAC: %s" % path)
    endian = "<"
    table_count, field10 = struct.unpack(endian + "2H", data[8:12])
    script_off_tbl, script_name_tbl, third_tbl = struct.unpack(
        endian + "3I", data[12:24])
    off_tbl = struct.unpack(endian + "%dI" % table_count,
                            data[script_off_tbl:script_off_tbl + 4 * table_count])
    name_tbl = struct.unpack(endian + "%dI" % table_count,
                             data[script_name_tbl:script_name_tbl + 4 * table_count])
    scripts = []
    for i, (off, noff) in enumerate(zip(off_tbl, name_tbl)):
        entry = {"index": i, "name": cstr(data, noff) if noff else "",
                 "offset": off}
        if off:
            fh, lh, iasa, tot = struct.unpack(endian + "4H", data[off:off + 8])
            x_field, num_lists = struct.unpack(endian + "2H", data[off + 20:off + 24])
            directory = []
            for e in range(num_lists):
                fo, t, c, do = struct.unpack(
                    endian + "IHHI", data[off + 24 + e * 12:off + 36 + e * 12])
                directory.append({"frame_off": fo, "type": t,
                                  "count": c, "data_off": do})
            nxt = [o for o in off_tbl[i + 1:] if o]
            end = min(nxt) if nxt else len(data)
            entry["first_hit"] = fh
            entry["last_hit"] = lh
            entry["iasa"] = iasa
            entry["total"] = tot
            entry["x_field"] = x_field
            entry["num_lists"] = num_lists
            entry["span_bytes"] = end - off
            entry["directory"] = directory
        scripts.append(entry)
    # Third table: count entries until the run breaks (values stop increasing).
    third = []
    base = third_tbl
    prev = -1
    while base + 4 <= len(data) and len(third) < 512:
        (v,) = struct.unpack(endian + "I", data[base:base + 4])
        if v == 0 or v <= prev:
            break
        third.append(v)
        prev = v
        base += 4
    return {
        "file": os.path.basename(path),
        "format": "sfiv-bac-tables",
        "header_u16_at_6": struct.unpack(endian + "H", data[6:8])[0],
        "table_count": table_count,
        "field10": field10,
        "offsets": {"script_table": script_off_tbl,
                    "script_name_table": script_name_tbl,
                    "third_table": third_tbl},
        "third_table_entries": len(third),
        "third_table_first": third[0] if third else None,
        "third_table_last": third[-1] if third else None,
        "scripts": scripts,
        "note": "script bodies NOT decoded: header fields + directory "
                "(frameOff, type, count, dataOff) preserved verbatim; the "
                "frameOff/dataOff base is an open RE task.",
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
        n_ok = n_fail = 0
        for root, _dirs, files in os.walk(indir):
            for fn in sorted(files):
                low = fn.lower()
                if low.endswith(".bac"):
                    parse, suffix = parse_bac_tables, ".sfiv-bac.json"
                elif low.endswith(".bcm"):
                    parse, suffix = parse_bcm, ".sfiv-bcm.json"
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
        print("sfiv: ok=%d fail=%d" % (n_ok, n_fail))
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
