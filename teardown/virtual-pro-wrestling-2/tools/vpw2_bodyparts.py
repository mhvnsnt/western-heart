#!/usr/bin/env python3
"""VPW2 body-part selection resolver (Task 2 — CRACKED 2026-11-19).

The per-wrestler body-part selection table lives in the ROM main segment:

* Body sets: ROM 0x435AC — six 72-byte entries, each a 19-model body set
  (17 consecutive file IDs + 2 trailing IDs = 19 consecutive models).
  Entry layout: 5 torso models + 7 left-limb + 7 right-limb models.
  The 7 per-side slots are the AKI limb joints: thigh, shin, foot,
  upper arm, forearm, hand, fingers (order within the 7 is provisional
  except hand/fingers — see SLOT_LABELS).
* Pointer table: ROM 0x438D0 — 27 u32 entries, indexed by BodyType (0-8):
  slots 0-8 point at the body-set entries (full), slots 9-17 at the
  second halves, slots 18-26 at nine 36-byte attire entries (ROM 0x4375C,
  which reference texture/small files, not geometry).
* BodyType -> body set (verified geometrically: torso bulk increases
  monotonically thin -> standard -> stocky -> huge -> super-heavy, and
  the giant set is tall-narrow):
      BT 0,1 (thin) -> group 0x98B
      BT 2,3 (standard) -> group 0x978
      BT 4,5 (stocky) -> group 0x965
      BT 6 (huge) -> group 0x93F
      BT 7 (super-heavy) -> group 0x952
      BT 8 (giant) -> group 0x92C
* Head triple: face/neck/head models are a 5x12x2 grid starting at
  file 0x15D5 (stride 3 per triple):
      k = body_idx*60 + shape_idx*12 + hair_idx
      face = 0x15D5 + 3k, neck = face+1, head = face+2
  body_idx: 0 if BodyType in {7,8} else 1.
  shape_idx from head_shape: Tall(4)->0, Round(2)->1, Standard(0)->2,
  Triangular(3)->3, Slender(1)->4.
  hair_idx from hair_type (value+1 = hair number N): N==1 -> 1,
  N==4 -> 2, N in {5,6,14} -> 3, N==7 -> 4, N==9 -> 5, N==12 -> 6,
  N==13 -> 10, N==15 -> 11, else 0 ("most").
  Fitted on all 23 Hidden-25 head triples, 0 mismatches.

Open: the attire-variant geometry (19-groups 6+, file IDs 0x99E-0xE4F)
is selected by RingAttire/UpperAttire through tables not yet located;
the base body above is the default (no-attire) body. The 14 models at
0x91E-0x92B (before group 0) are unassigned. Hand/glove variants
(0x19FA+, tables at ROM 0x4120C/0x4123C) are selected by the Gloves
field — not yet mapped.
"""
import json
import struct
from pathlib import Path

BODY_SETS = {
    0: 0x98B, 1: 0x98B,  # thin / thin-muscular
    2: 0x978, 3: 0x978,  # standard-muscular / standard
    4: 0x965, 5: 0x965,  # (4 unused in shipped costumes) / stocky
    6: 0x93F,            # huge
    7: 0x952,            # super-heavy
    8: 0x92C,            # giant
}

# Slot labels within a 19-model body set. Torso slots 0-4 attach to the
# pelvis/lower-ab/upper-body/neck joints (exact order provisional);
# limb slots are the 7 per-side AKI joints. Hand/fingers are confident
# (hand slot geometry matches the standalone hand models; fingers is
# the smallest mesh). Left = first 7 (higher model-space X).
SLOT_LABELS = [
    "torso_0", "torso_1", "torso_2", "torso_3", "torso_4",
    "leg_L_0", "leg_L_1", "leg_L_2", "hand_L", "fingers_L",
    "leg_L_5", "leg_L_6",
    "leg_R_0", "leg_R_1", "leg_R_2", "hand_R", "fingers_R",
    "leg_R_5", "leg_R_6",
]
# Provisional per-side mapping by size (group-1 geometry):
#   slot 0 (14,42,15): upper arm or shin; slot 1 (17,49,23): thigh;
#   slot 2 (15,17,30): foot (long in Z = forward); slot 5 (8,30,12):
#   forearm (thin); slot 6 (11,39,15): upper arm or shin.
LIMB_GUESS = ["upper_arm_or_shin", "thigh?", "foot?",
              "hand", "fingers", "forearm?", "upper_arm_or_shin"]

SHAPE_IDX = {4: 0, 2: 1, 0: 2, 3: 3, 1: 4}  # head_shape -> shape_idx


def hair_idx(hair_type):
    n = hair_type + 1
    if n == 1:
        return 1
    if n == 4:
        return 2
    if n in (5, 6, 14):
        return 3
    if n == 7:
        return 4
    if n == 9:
        return 5
    if n == 12:
        return 6
    if n == 13:
        return 10
    if n == 15:
        return 11
    return 0


def body_models(body_type):
    """19 base-body model file IDs for a BodyType (0-8)."""
    base = BODY_SETS[body_type]
    return [base + i for i in range(19)]


def head_triple(body_type, head_shape, hair_type):
    """(face, neck, head) file IDs."""
    body_idx = 0 if body_type in (7, 8) else 1
    k = body_idx * 60 + SHAPE_IDX[head_shape] * 12 + hair_idx(hair_type)
    face = 0x15D5 + 3 * k
    return face, face + 1, face + 2


def read_tables(rom_path):
    """Read the body-set + pointer tables straight from the ROM."""
    rom = Path(rom_path).read_bytes()
    sets = []
    for e in range(6):
        off = 0x435AC + e * 0x48
        vals = struct.unpack_from(">36H", rom, off)
        run = list(vals[:17])
        tail = [vals[19], vals[20]]
        assert vals[17] == 0 and vals[18] == 0
        assert tail == [run[0] - 1, run[0] - 2]
        assert all(v == 0 for v in vals[21:])
        sets.append(run[0] - 2)  # group base
    ptrs = struct.unpack_from(">27I", rom, 0x438D0)
    return sets, [p - 0x7FFFF400 for p in ptrs]


if __name__ == "__main__":
    import glob
    rom = glob.glob("/home/hatch/workspace/grok-declined-items/lane-jp-sourcing/vpw2-rom/*.z64")[0]
    sets, ptrs = read_tables(rom)
    print("body-set group bases from ROM:", [hex(s) for s in sets])
    print("pointer table targets:", [hex(p) for p in ptrs])
    # verify against BODY_SETS
    expect = [0x98B, 0x978, 0x965, 0x93F, 0x952, 0x92C]
    assert sets == expect, (sets, expect)
    print("BODY_SETS verified against ROM table")
