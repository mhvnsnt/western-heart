#!/usr/bin/env python3
"""Bulk-export the full WWF No Mercy AKI animation bank to NPY + manifest.

Source: WWF No Mercy (USA) (Rev-A).z64, FileTable @0x16C31D8, FirstFile 0x1BD150, 1-based file IDs (game-exact, W3c — FUN_80003ab0/FUN_80003bd0; see anim_extract.py).
Bank: file IDs 0x2DD9..0x445A (verified 2026-10-13; files before 0x2DD9 /
after 0x445A do not fit the 4+N*98 AkiAnimation layout).
  0x2DD9..0x3321 = system animations (stances, entrances, taunts, ...)
  0x3322..0x445A = move animations (AnimID = file_id - 0x3322, per
                   VPWStudio MenuItems_Moves.cs)

Output:
  <outdir>/clips/anim_XXXX.npy   per-clip int16 array, shape (nframes, 26, 3)
  <outdir>/manifest.json          joint order/kinds + per-clip metadata

NPY layout, frame = 26 joints in ORDER (see anim_extract.ORDER):
  - PivotRotation joints ("PR", 20 of them): channels = [pivot_x, rotation, pivot_z]
      [PivotX s12][Rotation u10][PivotZ s10] (W3b Finding 2); rotation unsigned, 1024 = full turn
  - OverallMovement ("OM", 1): channels = [overall_x, overall_y, overall_z]
      (12-bit X/Z signed, 8-bit Y unsigned)
  - MovementXYZ ("MV", 6): channels = [move_x, move_y, move_z] (raw u8 each)

Usage:
  extract_all_anims.py <outdir>
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from anim_extract import (FileTable, ORDER, decode_pr, decode_om,
                          FIRST_ANIM, FIRST_MOVE_ANIM)

ROM = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '..', 'WWF No Mercy (USA) (Rev-A).z64')
LAST_ANIM = 0x445A

def encode_frame(fr):
    """raw 98-byte frame -> (26,3) int16"""
    out = np.zeros((26, 3), dtype=np.int16)
    o = 0
    for i, (name, kind) in enumerate(ORDER):
        if kind == "PR":
            w = int.from_bytes(fr[o:o + 4], 'big'); o += 4
            px = w >> 20
            if px & 0x800: px -= 0x1000
            r = (w >> 10) & 0x3FF
            pz = w & 0x3FF
            if pz & 0x200: pz -= 0x400
            out[i] = (px, r, pz)
        elif kind == "OM":
            b = fr[o:o + 4]; o += 4
            ox = (b[0] << 4) | ((b[1] & 0xF0) >> 4)
            if ox & 0x800: ox -= 0x1000
            oy = ((b[1] & 0x0F) << 4) | ((b[2] & 0xF0) >> 4)
            oz = ((b[2] & 0x0F) << 8) | b[3]
            if oz & 0x800: oz -= 0x1000
            out[i] = (ox, oy, oz)
        else:
            out[i] = (fr[o], fr[o + 1], fr[o + 2]); o += 3
    assert o == 0x62
    return out

def main():
    outdir = sys.argv[1]
    clips = os.path.join(outdir, 'clips')
    os.makedirs(clips, exist_ok=True)
    data = open(ROM, 'rb').read()
    ft = FileTable(data)
    manifest = {
        "rom": "WWF No Mercy (USA) (Rev-A).z64",
        "format": "npy int16, shape (nframes, 26, 3); channels documented in FORMAT.md",
        "joints": [{"index": i, "name": n, "kind": k} for i, (n, k) in enumerate(ORDER)],
        "range": {"first": hex(FIRST_ANIM), "last": hex(LAST_ANIM)},
        "move_anim_base": hex(FIRST_MOVE_ANIM),
        "clips": [],
    }
    n_sys = n_move = 0
    for fid in range(FIRST_ANIM, LAST_ANIM + 1):
        raw, enc = ft.get(fid)
        if enc or len(raw) < 4:
            raise RuntimeError(f"file {fid:04X} unexpectedly encoded/short")
        nf = (len(raw) - 4) // 98
        arr = np.stack([encode_frame(raw[4 + f * 98:4 + (f + 1) * 98])
                        for f in range(nf)]).astype(np.int16)
        fn = f"anim_{fid:04X}.npy"
        np.save(os.path.join(clips, fn), arr)
        is_move = fid >= FIRST_MOVE_ANIM
        n_move += is_move; n_sys += (not is_move)
        manifest["clips"].append({
            "file": f"clips/{fn}", "file_id": hex(fid),
            "toki2": raw[:4].hex(), "nframes": nf,
            "kind": "move" if is_move else "system",
            "anim_id": (fid - FIRST_MOVE_ANIM) if is_move else None,
        })
    json.dump(manifest, open(os.path.join(outdir, 'manifest.json'), 'w'), indent=1)
    print(f"exported {len(manifest['clips'])} clips "
          f"({n_sys} system, {n_move} move) -> {outdir}")

if __name__ == '__main__':
    main()
