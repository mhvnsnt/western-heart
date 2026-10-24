#!/usr/bin/env python3
"""tools/auto_rig/backends/retarget.py — bone-name canonicalization + retarget.

Two operations, kept separate on purpose:

1. canonicalize(names) — rename bones to the WH Mixamo-style canonical set.
   This is the PR #264 default: it preserves the native skeleton structure
   and only fixes names. Structure-preserving = no clobber.

2. geometric_retarget(...) — full geometric retarget of a source skeleton
   onto the WH template (position-based). Fallback for skeletons whose
   proportions don't match the canonical set at all.

The canonical set (Mixamo-style, per MODEL-STATUS.md):
  Hips, Spine, Spine1, Spine2, Neck, Head,
  LeftShoulder, LeftArm, LeftForeArm, LeftHand, RightShoulder, ...,
  LeftUpLeg, LeftLeg, LeftFoot, LeftToeBase, RightUpLeg, ...,
  plus LeftHandThumb1..3, LeftHandIndex1..3, LeftHandMiddle1..3,
  LeftHandRing1..3, LeftHandPinky1..3 (and Right side).
"""

import re

# ---------------------------------------------------------------- canonical
# Maps common foreign naming conventions onto the canonical set.
# Each entry: canonical name -> list of regexes (first match wins).
NAME_TABLE = {
    "Hips": [r"^hips$", r"^pelvis$", r"^root$", r"^mixamorig_hips(_\d+)?$"],
    "Spine": [r"^spine$", r"^spine1$", r"^mixamorig_spine(_\d+)?$"],
    "Spine1": [r"^spine2$", r"^chest$", r"^mixamorig_spine1(_\d+)?$"],
    "Spine2": [r"^spine3$", r"^upperchest$", r"^mixamorig_spine2(_\d+)?$"],
    "Neck": [r"^neck$", r"^mixamorig_neck(_\d+)?$"],
    "Head": [r"^head$", r"^mixamorig_head(_\d+)?$"],
}

_LIMB = {
    # canonical base -> (left regexes, right regexes)
    "Shoulder": ([r"l[_ ]?shoulder", r"shoulder\.?l", r"mixamorig_leftshoulder"],
                 [r"r[_ ]?shoulder", r"shoulder\.?r", r"mixamorig_rightshoulder"]),
    "Arm": ([r"l[_ ]?(upperarm|arm)(?!.*fore)", r"upperarm\.?l", r"mixamorig_leftarm_"],
            [r"r[_ ]?(upperarm|arm)(?!.*fore)", r"upperarm\.?r", r"mixamorig_rightarm_"]),
    "ForeArm": ([r"l[_ ]?forearm", r"forearm\.?l", r"mixamorig_leftforearm_"],
                [r"r[_ ]?forearm", r"forearm\.?r", r"mixamorig_rightforearm_"]),
    "Hand": ([r"l[_ ]?hand$", r"hand\.?l", r"mixamorig_lefthand_"],
             [r"r[_ ]?hand$", r"hand\.?r", r"mixamorig_righthand_"]),
    "UpLeg": ([r"l[_ ]?(thigh|upleg)", r"thigh\.?l", r"mixamorig_leftupleg_"],
              [r"r[_ ]?(thigh|upleg)", r"thigh\.?r", r"mixamorig_rightupleg_"]),
    "Leg": ([r"l[_ ]?(shin|leg|calf)", r"shin\.?l", r"mixamorig_leftleg_"],
            [r"r[_ ]?(shin|leg|calf)", r"shin\.?r", r"mixamorig_rightleg_"]),
    "Foot": ([r"l[_ ]?foot", r"foot\.?l", r"mixamorig_leftfoot_"],
             [r"r[_ ]?foot", r"foot\.?r", r"mixamorig_rightfoot_"]),
    "ToeBase": ([r"l[_ ]?toe", r"toe\.?l", r"mixamorig_lefttoebase_"],
                [r"r[_ ]?toe", r"toe\.?r", r"mixamorig_righttoebase_"]),
}

_FINGERS = ["Thumb", "Index", "Middle", "Ring", "Pinky"]


def _build_table():
    table = []  # (compiled regex, canonical name)
    for canon, patterns in NAME_TABLE.items():
        for p in patterns:
            table.append((re.compile(p, re.IGNORECASE), canon))
    for base, (lpats, rpats) in _LIMB.items():
        for p in lpats:
            table.append((re.compile(p, re.IGNORECASE), "Left" + base))
        for p in rpats:
            table.append((re.compile(p, re.IGNORECASE), "Right" + base))
    for finger in _FINGERS:
        for i in (1, 2, 3):
            table.append((re.compile(r"l[_ ]?%s%d" % (finger.lower(), i), re.IGNORECASE),
                          "LeftHand%s%d" % (finger, i)))
            table.append((re.compile(r"%s\.?l\.?%d" % (finger.lower(), i), re.IGNORECASE),
                          "LeftHand%s%d" % (finger, i)))
            table.append((re.compile(r"mixamorig_left\w*%s_?0*%d" % (finger.lower(), i), re.IGNORECASE),
                          "LeftHand%s%d" % (finger, i)))
            table.append((re.compile(r"r[_ ]?%s%d" % (finger.lower(), i), re.IGNORECASE),
                          "RightHand%s%d" % (finger, i)))
            table.append((re.compile(r"%s\.?r\.?%d" % (finger.lower(), i), re.IGNORECASE),
                          "RightHand%s%d" % (finger, i)))
            table.append((re.compile(r"mixamorig_right\w*%s_?0*%d" % (finger.lower(), i), re.IGNORECASE),
                          "RightHand%s%d" % (finger, i)))
    return table


_TABLE = _build_table()

REQUIRED_BONES = [
    "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
    "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
    "RightShoulder", "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot",
    "RightUpLeg", "RightLeg", "RightFoot",
]


def canonicalize(bone_names):
    """Map an iterable of bone names onto the canonical set.

    Returns (mapping, unmapped): mapping is {original: canonical},
    unmapped is the list of names no pattern matched. Names that already
    match the canonical set pass through unchanged.
    """
    canonical_set = set(REQUIRED_BONES)
    for base in _LIMB:
        canonical_set.add("Left" + base)
        canonical_set.add("Right" + base)
    mapping, unmapped = {}, []
    for name in bone_names:
        if name in canonical_set or re.fullmatch(r"(Left|Right)Hand(Thumb|Index|Middle|Ring|Pinky)[123]", name or ""):
            mapping[name] = name
            continue
        hit = None
        for rx, canon in _TABLE:
            if rx.search(name or ""):
                hit = canon
                break
        if hit:
            mapping[name] = hit
        else:
            unmapped.append(name)
    return mapping, unmapped


def gate_bones(canonical_names):
    """Check the canonical name set against the playable-gate bone list."""
    have = set(canonical_names)
    missing = [b for b in REQUIRED_BONES if b not in have]
    return missing
