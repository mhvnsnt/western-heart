#!/usr/bin/env python3
"""Headless Tekken 3 stage panorama extraction (geometry only).

Ports the TMD panorama parser from tekken3remake's
tools/remake_import/stage.py (which needs the full remake_import pipeline:
Disc/Output/Vram/atlas/sources) down to the geometry half, and emits one
OBJ + stage.json per fight stage (0-14, BNS TMD records 56-70).

Textures (panorama atlas, floor tiles) still require the full pipeline —
see the note at the bottom of the module docstring in stage.py.

Usage:
    python3 extract_stages.py \
        --bns <repo>/teardown/tekken3/disc/files/TEKKEN3/TEKKEN3.BNS \
        --table <repo>/teardown/tekken3/bns-table.pkl \
        --out <repo>/teardown/tekken3/stages
"""

from __future__ import annotations

import argparse
import json
import pickle
import struct
from pathlib import Path

# Stage number -> (letter, home stage of). From tekken3remake
# docs/research/code/stages.md ("Stage numbers and resources").
STAGES = [
    (0, "a", "Paul, Bryan"),
    (1, "b", "Law, Kuma, Panda"),
    (2, "c", "Yoshimitsu, Mokujin"),
    (3, "d", "Xiaoyu (costumes 0/1)"),
    (4, "e", "Hwoarang"),
    (5, "f", "Lei"),
    (6, "g", "Ogre, True Ogre"),
    (7, "n", "Xiaoyu, Jin (costumes 2/3)"),
    (8, "i", "Jin"),
    (9, "j", "Nina, Anna, Gun Jack"),
    (10, "k", "Eddy, Tiger"),
    (11, "l", "King"),
    (12, "m", "Julia, Heihachi"),
    (13, "t", "Gon"),
    (14, "u", "Doctor B."),
]

OBJECTS = 6 * 6
TABLE = 0x0C
ROW_BYTES = 0x1C
PACKET_BYTES = {0x24: 20, 0x28: 8, 0x2C: 20}
QUAD_TRIANGLES = ((0, 1, 2), (1, 3, 2))
UNTEXTURED = "untextured"


def panorama(tmd: bytes) -> tuple[int, list[tuple]]:
    """Verbatim port of tekken3remake stage.panorama (geometry half)."""
    cell = 10 * struct.unpack_from("<I", tmd, 4)[0]
    count = struct.unpack_from("<I", tmd, 8)[0]
    if count != OBJECTS:
        raise ValueError(f"expected {OBJECTS} panorama objects, found {count}")
    corners_out: list[tuple] = []
    for index in range(OBJECTS):
        vert_off, vert_count, _, _, prim_off, prim_count, _ = struct.unpack_from(
            "<7I", tmd, TABLE + ROW_BYTES * index)
        verts = [struct.unpack_from("<3h", tmd, TABLE + vert_off + 8 * i)
                 for i in range(vert_count)]
        pos = TABLE + prim_off
        for _ in range(prim_count):
            r, g, b, code = tmd[pos:pos + 4]
            if code == 0x28:
                idx = tmd[pos + 4:pos + 8]
                uvs = [(0, 0)] * 4
                key = UNTEXTURED
            else:
                u0, v0, cba = struct.unpack_from("<BBH", tmd, pos + 4)
                u1, v1, tsb = struct.unpack_from("<BBH", tmd, pos + 8)
                u2, v2, u3, v3 = tmd[pos + 12:pos + 16]
                idx = tmd[pos + 16:pos + 20] if code == 0x2C else tmd[pos + 16:pos + 19]
                uvs = [(u0, v0), (u1, v1), (u2, v2), (u3, v3)]
                key = f"{cba:04x}_{tsb:04x}"
            corners = []
            for c, vi in enumerate(idx):
                x, y, z = verts[vi]
                u, v = uvs[c]
                corners.append((key, (x, y, z), u, v, (r / 128, g / 128, b / 128)))
            for tri in ([(0, 1, 2)] if len(corners) == 3 else QUAD_TRIANGLES):
                corners_out.extend(corners[i] for i in tri)
            pos += PACKET_BYTES[code]
    return cell, corners_out


def write_obj(path: Path, corners: list[tuple]) -> tuple[int, int]:
    """OBJ with per-corner positions and UVs (0..1 across the 256px VRAM page).
    One (v, vt) pair per corner; faces reference them 1:1."""
    lines = ["# Tekken 3 stage panorama - geometry only (no texture atlas)"]
    for _, (x, y, z), _, _, _ in corners:
        lines.append(f"v {x} {y} {z}")
    for _, _, u, v, _ in corners:
        lines.append(f"vt {u / 256.0:.6f} {1.0 - v / 256.0:.6f}")
    n = len(corners)
    for i in range(0, n, 3):
        a, b, c = i + 1, i + 2, i + 3
        lines.append(f"f {a}/{a} {b}/{b} {c}/{c}")
    path.write_text("\n".join(lines) + "\n")
    return n, n // 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bns", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    table = pickle.load(open(args.table, "rb"))  # list of (id, sector, size)
    by_id = {t[0]: t for t in table}
    bns = open(args.bns, "rb")
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    total_verts = total_tris = 0
    summary = []
    for number, letter, home in STAGES:
        rec_id = 56 + number
        rid, sector, size = by_id[rec_id]
        bns.seek(sector * 2048)
        tmd = bns.read(size)
        cell, corners = panorama(tmd)
        obj_path = out_root / letter / f"stg_{letter}_panorama.obj"
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        nverts, ntris = write_obj(obj_path, corners)
        xs = [c[1][0] for c in corners]
        zs = [c[1][2] for c in corners]
        ys = [c[1][1] for c in corners]
        untextured = sum(1 for c in corners if c[0] == UNTEXTURED)
        info = {
            "stage": number,
            "letter": letter,
            "home_stage_of": home,
            "bns_tmd": rec_id,
            "bns_arc": 36 + number,
            "tmd_size": size,
            "cell": cell,
            "panorama_vertices": nverts,
            "panorama_triangles": ntris,
            "untextured_corners": untextured,
            "extent": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)],
                       "z": [min(zs), max(zs)]},
            "obj": f"stg_{letter}_panorama.obj",
            "note": "geometry only; texture keys <cba>_<tsb> per corner, "
                    "atlas needs the full tekken3remake remake_import pipeline",
        }
        (out_root / letter / "stage.json").write_text(json.dumps(info, indent=2) + "\n")
        total_verts += nverts
        total_tris += ntris
        summary.append((number, letter, nverts, ntris))
        print(f"stage {number:2d} ({letter}): {nverts:5d} verts {ntris:5d} tris -> {obj_path}")
    print(f"TOTAL: {total_verts} verts, {total_tris} tris across {len(STAGES)} stages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
