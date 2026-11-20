#!/usr/bin/env python3
"""USA (SLUS_004.02) EXE tables for the Tekken 3 pose/animation pipeline.

All addresses VERIFIED 2026-10-13 by content against the USA executable
(disc/files/TEKKEN3/SLUS_004.02, load base 0x80010000, 0x800 header):

- EULER_SLOTS 0x8001A330: the 10-byte pattern [0,1,11,2,3,7,6,10,14,17]
  (documented in n0madic animation.md) is present -- SAME as Japan Rev.1.
- SIN_TABLE 0x8001E8C4: all 4096 s16 entries == round(sin(i*2pi/4096)*4096),
  0 mismatches -- SAME as Japan Rev.1.
- SQRT_TABLE 0x80098D08: 192-entry PsyQ SquareRoot0 mantissa table, exact
  analytic shape; byte-identical duplicate at 0x8004AF40. (JP: 0x800990AC)
- LIMB_BASIS 0x80096EAC: 3x3 s16, exactly orthonormal. (JP: 0x800972D0)
- SKELETON_OFFSETS 0x80096ECC: [[0,0,0],[350,0,-100],[350,0,100],[0,0,0]]
  -- matches documented JP values exactly. (JP: 0x800972F0)
- LIMB_OFFSETS 0x80096EFC: [[-140,0,0],[-140,0,0],[-160,0,100],[-160,0,-100]]
  -- matches documented JP values exactly. (JP: 0x80097320)
- SPLINE_TABLE_BASE 0x8009671C: byte-index table + 4 weight tables present
  at the JP-relative offsets (+0x200/+0x300/+0x402/+0x504). (JP: 0x80096B40)
- CHANNEL_SHIFT 0x80096C24: 49 bytes == [1]*15 + [5]*34 verified. (JP: 0x80097048)

Shift summary vs Japan Rev.1: the 0x80096xxx data region shifted -0x424
(USA = JP - 0x424); the 0x8001xxxx code region did NOT shift; the SQRT
table sits at JP-0x3A4.

NOTE: a previous handoff listed 0x80096EAC/0x80096ECC/0x80096EFC/0x8009671C
as "Japan" addresses -- they are the USA addresses (the -0x424 shift had
already been applied when written down). The Japan Rev.1 originals are in
pose.py (EULER_SLOTS 0x8001A330, LIMB_BASIS 0x800972D0, SKELETON_OFFSETS
0x800972F0, LIMB_OFFSETS 0x80097320, SPLINE_TABLE_BASE 0x80096B40,
SQRT_TABLE 0x800990AC, SIN_TABLE 0x8001E8C4).
"""

from __future__ import annotations

import sys
from pathlib import Path

RESEARCH = Path("/home/hatch/workspace/tools/tekken3remake/tools/research")
sys.path.insert(0, str(RESEARCH))
import pose  # noqa: E402

EXE_PATH = Path("/home/hatch/workspace/game-reverse-engineering/tekken3/disc/files/TEKKEN3/SLUS_004.02")

# --- verified USA addresses -------------------------------------------------
USA_SIN_TABLE = 0x8001E8C4        # == JP
USA_EULER_SLOTS = 0x8001A330      # == JP
USA_SQRT_TABLE = 0x80098D08       # JP 0x800990AC (-0x3A4); dup @ 0x8004AF40
USA_LIMB_BASIS = 0x80096EAC       # JP 0x800972D0 (-0x424)
USA_SKELETON_OFFSETS = 0x80096ECC  # JP 0x800972F0 (-0x424)
USA_LIMB_OFFSETS = 0x80096EFC     # JP 0x80097320 (-0x424)
USA_SPLINE_TABLE_BASE = 0x8009671C  # JP 0x80096B40 (-0x424)
USA_CHANNEL_SHIFT = 0x80096C24    # JP 0x80097048 (-0x424)

EULER_SLOT_VALUES = [0, 1, 11, 2, 3, 7, 6, 10, 14, 17]
SKELETON_OFFSET_VALUES = [[0, 0, 0], [350, 0, -100], [350, 0, 100], [0, 0, 0]]
LIMB_OFFSET_VALUES = [[-140, 0, 0], [-140, 0, 0], [-160, 0, 100], [-160, 0, -100]]


def apply_usa(pose_mod=pose) -> None:
    """Point pose.py's table addresses at the USA executable. Idempotent."""
    pose_mod.SQRT_TABLE = USA_SQRT_TABLE
    pose_mod.LIMB_BASIS = USA_LIMB_BASIS
    pose_mod.SKELETON_OFFSETS = USA_SKELETON_OFFSETS
    pose_mod.LIMB_OFFSETS = USA_LIMB_OFFSETS
    assert pose_mod.SIN_TABLE == USA_SIN_TABLE
    assert pose_mod.EULER_SLOTS == USA_EULER_SLOTS


def load_tables(exe_path: Path = EXE_PATH) -> pose.ExeTables:
    """ExeTables over the USA EXE, with USA addresses applied + sanity checks."""
    apply_usa()
    tab = pose.ExeTables(exe_path.read_bytes())
    assert [tab.u8(USA_EULER_SLOTS + j) for j in range(10)] == EULER_SLOT_VALUES
    assert [tab.vec3(USA_SKELETON_OFFSETS + 12 * i) for i in range(4)] == SKELETON_OFFSET_VALUES
    assert [tab.vec3(USA_LIMB_OFFSETS + 12 * i) for i in range(4)] == LIMB_OFFSET_VALUES
    return tab


def pose_to_slot_rotations(pose_vec: list[int], tab: pose.ExeTables) -> list[list[int]]:
    """PoseBuildMatrices with USA tables. Returns 18 flat 9-element rotations."""
    apply_usa()
    slots = [[4096 if r == c else 0 for r in range(3) for c in range(3)] for _ in range(18)]
    pose.pose_build_matrices(pose_vec, slots, tab)
    return slots


if __name__ == "__main__":
    tab = load_tables()
    print("USA tables OK:",
          hex(USA_SIN_TABLE), hex(USA_SQRT_TABLE), hex(USA_EULER_SLOTS),
          hex(USA_LIMB_BASIS), hex(USA_SKELETON_OFFSETS), hex(USA_LIMB_OFFSETS),
          hex(USA_SPLINE_TABLE_BASE))
