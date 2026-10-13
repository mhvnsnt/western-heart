#!/usr/bin/env python3
"""Assemble a Tekken 3 fighter's KMD parts into a posed full-body model.

Pipeline (all USA-verified):
  motion bank -> usa_motion.sample_pose (bit-exact AnimDecodePose port)
  -> usa_tables.pose_to_slot_rotations (bit-exact PoseBuildMatrices port)
  -> local[slot] = (rot, KMD joint offset (x, y, -z))
  -> world[slot] = world[parent] . local[slot]
  -> part verts (kmd.py, local joint space) transformed by world[slot]

Part->row / part->matrix-slot tables are the documented EXE tables
(JP 0x8001A05C / 0x8001A074 -- semantic values, version-independent).
Part hierarchy (parent part + joint offset) comes from the model's own KMD.

Usage:
  python3 tools/local/pose_assemble.py <kmd> <bank> <slot> <frame> --out model.obj
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

LOCAL = Path(__file__).resolve().parent
RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(LOCAL))
sys.path.insert(0, str(RESEARCH))

import kmd  # noqa: E402
import motion  # noqa: E402
import usa_motion  # noqa: E402
import usa_tables  # noqa: E402

# Part -> KMD row (EXE 0x8001A05C) and part -> matrix slot (EXE 0x8001A074).
PART_ROW = [0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            21, 22, 23, 24]
PART_SLOT = [0, 1, 11, 12, 13, 14, 15, 16, 17, 3, 4, 5, 6, 7, 8, 9, 10, 2,
             18, 19, 20, 21]


def mat_mul(a, b):
    """4x4 multiply (row-major nested lists)."""
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)]
            for r in range(4)]


def mat_vec(m, v):
    x, y, z = v
    return (m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
            m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
            m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3])


def assemble(kmd_path: Path, bank_path: Path, slot: int, frame: int,
             exe_path: Path = usa_tables.EXE_PATH):
    """Return (obj_text, debug_info)."""
    model = kmd.parse(kmd_path.read_bytes())
    exe = exe_path.read_bytes()
    stab = usa_tables.load_tables(exe_path)
    mtab = usa_motion.UsaSplineTables(exe)

    bank_data = bank_path.read_bytes()
    bank = motion.parse_bank(bank_data)
    row_no = bank.move_index[slot]
    mrow = bank.move_row(row_no)
    anim_word = mrow[0]
    if anim_word >= motion.COMMON_FLAG:
        raise SystemExit("slot refers to divmot99 common bank -- extract it first")
    stream = motion.parse_anim(bank_data, bank.anim_offset(anim_word))
    pose_vec = usa_motion.sample_pose(stream, frame, mtab)

    slot_rots = usa_tables.pose_to_slot_rotations(pose_vec, stab)  # 18 flat 9-elem, 4.12

    # Per-part data from its KMD row.
    nparts = 18  # body parts 0..17 (18..21 are costume attachments)
    part_parent = []
    part_offset = []
    for k in range(nparts):
        row = model.rows[PART_ROW[k]]
        x, y, z = row.offset
        part_parent.append(row.parent)
        part_offset.append((x, y, -z))  # FighterSetupPart negates z

    # Slot parent = slot of parent part.
    slot_of_part = PART_SLOT[:nparts]
    part_of_slot = {}
    for k, s in enumerate(slot_of_part):
        part_of_slot[s] = k
    slot_parent = {}
    for k, s in enumerate(slot_of_part):
        p = part_parent[k]
        slot_parent[s] = slot_of_part[p] if p >= 0 else -1

    # Local matrices: rotation from the animation, translation from the model.
    local = {}
    for k, s in enumerate(slot_of_part):
        r = slot_rots[s]
        rf = [[r[3 * i + j] / 4096.0 for j in range(3)] for i in range(3)]
        tx, ty, tz = part_offset[k]
        local[s] = [rf[0] + [tx], rf[1] + [ty], rf[2] + [tz], [0, 0, 0, 1]]

    # Fighter root = translation by the pose's root channels (model space).
    root = [[1, 0, 0, pose_vec[0]], [0, 1, 0, pose_vec[1]],
            [0, 0, 1, pose_vec[2]], [0, 0, 0, 1]]

    world = {}

    def get_world(s):
        if s in world:
            return world[s]
        p = slot_parent[s]
        base = root if p < 0 else get_world(p)
        world[s] = mat_mul(base, local[s])
        return world[s]

    lines = []
    for k in range(nparts):
        s = slot_of_part[k]
        w = get_world(s)
        row = model.rows[PART_ROW[k]]
        if row.verts is None:
            continue
        lines.append(f"o part_{k}")
        for (x, y, z) in row.verts.coords:
            wx, wy, wz = mat_vec(w, (x, y, z))
            lines.append(f"v {wx:.2f} {wy:.2f} {wz:.2f}")
    info = {
        "kmd": str(kmd_path), "bank": str(bank_path), "slot": slot,
        "move_row": row_no, "frame": frame,
        "stream_frames": stream.frames,
        "pose_root": pose_vec[0:3],
    }
    return "\n".join(lines) + "\n", info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kmd", type=Path)
    ap.add_argument("bank", type=Path)
    ap.add_argument("slot", type=int, help="move-index slot (0-2 = stance moves)")
    ap.add_argument("frame", type=int, nargs="?", default=0)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--info", type=Path, default=None)
    args = ap.parse_args()
    obj, info = assemble(args.kmd, args.bank, args.slot, args.frame)
    args.out.write_text(obj)
    print("wrote", args.out, f"({obj.count(chr(10)+'v ') } verts)")
    if args.info:
        args.info.write_text(json.dumps(info, indent=1))
        print("wrote", args.info)
    print("root channels:", info["pose_root"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
