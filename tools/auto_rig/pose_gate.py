#!/usr/bin/env python3
"""tools/auto_rig/pose_gate.py — the POSE gate for per-character isolation.

A model may only be wired as a playable fighter if it can actually POSE —
statues and incomplete rigs are rejected here, not discovered in-game.

FAIL conditions (exit 1):
  1. 0 skins — unrigged static (Family E). Raw Tripo exports with 1 node,
     1 mesh, 0 skins, 0 animations cannot idle/stance/fight-animate at all.
  2. Incomplete canonical bones — required Mixamo-style bones missing.
     Uses the same REQUIRED_BONES as the playable gate (retarget.py).
     Foreign rigs (Family D) fail here unless remapped (see Vega remap).
  3. Statue-bound — skinned but effectively a statue: the skin has joints
     but the bind pose is a frozen authored pose with no animation clips
     and the skeleton cannot be driven (e.g. single-bone "rig" or all
     vertices weighted to one joint).

PASS (exit 0) means: skinned, canonically complete, poseable.

Usage:
    python3 pose_gate.py --in MODEL.glb [--json-out R.json]
Exit 0 = pass, 1 = fail. Always writes a JSON report to stdout.

Families (docs/PER-CHARACTER-ISOLATION.md):
  A — healthy canonical+Idle (pantera/steve-fox/demonio 49-bone): PASS
  B — canonical rig, no clips (rest=T-pose in game): PASS (poseable, needs bank)
  C — Lane-C 33-bone canonical, no clips: PASS (poseable, needs bank)
  D — foreign rigs: FAIL unless remapped (Vega remap in game/js/assets.js)
  E — statues (19): FAIL (0 skins)
"""

import argparse
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(__file__))
try:
    from backends.retarget import REQUIRED_BONES, canonicalize, gate_bones
except ImportError:
    # Fallback if backends not importable: inline the canonical list.
    REQUIRED_BONES = [
        "Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
        "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
        "RightShoulder", "RightArm", "RightForeArm", "RightHand",
        "LeftUpLeg", "LeftLeg", "LeftFoot",
        "RightUpLeg", "RightLeg", "RightFoot",
    ]

    def canonicalize(names):
        mapping = {}
        unmapped = []
        for n in names:
            c = n.replace("mixamorig:", "").replace("mixamorig", "")
            if c in REQUIRED_BONES:
                mapping[n] = c
            else:
                unmapped.append(n)
        return mapping, unmapped

    def gate_bones(canonical_names):
        have = set(canonical_names)
        return [b for b in REQUIRED_BONES if b not in have]


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        raise ValueError("not a GLB file")
    jlen = struct.unpack("<I", data[12:16])[0]
    js = json.loads(data[20:20 + jlen])
    return js


def skin_count(js):
    """Number of skins in the GLB."""
    return len(js.get("skins", []))


def joint_names(js):
    """Joint node names from the first skin."""
    skins = js.get("skins", [])
    if not skins:
        return []
    joints = skins[0].get("joints", [])
    nodes = js.get("nodes", [])
    return [nodes[j].get("name", "") for j in joints if j < len(nodes)]


def animation_count(js):
    """Number of embedded animation clips."""
    return len(js.get("animations", []))


def check_statue_bound(js):
    """Detect statue-bound models: skinned but unposeable.

    Heuristics:
    - Only 1 joint in the skin (single-bone "rig").
    - Skin exists but no mesh uses JOINTS_0 (skin not bound to geometry).
    Returns (is_statue_bound, reason).
    """
    skins = js.get("skins", [])
    if not skins:
        return False, ""
    joints = skins[0].get("joints", [])
    if len(joints) <= 1:
        return True, f"only {len(joints)} joint(s) in skin — cannot pose"
    # Check if any mesh primitive actually references the skin via JOINTS_0.
    has_joints_attr = False
    for mesh in js.get("meshes", []):
        for prim in mesh.get("primitives", []):
            attrs = prim.get("attributes", {})
            if "JOINTS_0" in attrs:
                has_joints_attr = True
                break
        if has_joints_attr:
            break
    if not has_joints_attr:
        return True, "skin exists but no mesh has JOINTS_0 — skin not bound"
    return False, ""


def check(path):
    report = {
        "file": path,
        "checks": {},
        "pass": False,
        "family": None,
    }
    try:
        js = read_glb(path)
    except Exception as e:
        report["checks"]["valid_glb"] = {"pass": False, "error": str(e)}
        return report

    report["checks"]["valid_glb"] = {"pass": True}

    # GATE 1: 0 skins -> FAIL (Family E statues)
    n_skins = skin_count(js)
    report["checks"]["has_skins"] = {
        "pass": n_skins > 0,
        "skins": n_skins,
    }
    if n_skins == 0:
        report["checks"]["has_skins"]["reason"] = (
            "0 skins — unrigged static (Family E). "
            "Cannot idle/stance/fight-animate. Route to auto-rig."
        )
        report["family"] = "E"
        return report

    # GATE 2: incomplete canonical bones -> FAIL
    names = joint_names(js)
    mapping, unmapped = canonicalize(names)
    missing = gate_bones(mapping.values())
    report["checks"]["canonical_bones"] = {
        "pass": len(missing) == 0,
        "have": len(mapping),
        "missing": missing,
    }
    if missing:
        report["checks"]["canonical_bones"]["reason"] = (
            f"Missing {len(missing)} required bones: {', '.join(missing)}. "
            "Foreign rig (Family D) — remap or re-rig to canonical."
        )
        report["family"] = "D"
        return report

    # GATE 3: statue-bound -> FAIL
    statue_bound, reason = check_statue_bound(js)
    report["checks"]["not_statue_bound"] = {
        "pass": not statue_bound,
        "reason": reason if statue_bound else "",
    }
    if statue_bound:
        report["family"] = "E"
        return report

    # PASS — determine family by clips
    n_anims = animation_count(js)
    report["checks"]["animations"] = {"count": n_anims}
    if n_anims > 0:
        report["family"] = "A"
    else:
        # B or C: canonical, poseable, no embedded clips (needs T3 bank)
        report["family"] = "B/C"

    report["pass"] = True
    return report


def main():
    ap = argparse.ArgumentParser(description="Pose gate: FAIL on statues/incomplete rigs.")
    ap.add_argument("--in", dest="inp", required=True, help="Input MODEL.glb")
    ap.add_argument("--json-out", default=None, help="Write JSON report to file")
    args = ap.parse_args()

    report = check(args.inp)
    out = json.dumps(report, indent=2)
    print(out)
    if args.json_out:
        with open(args.json_out, "w") as f:
            f.write(out)
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
