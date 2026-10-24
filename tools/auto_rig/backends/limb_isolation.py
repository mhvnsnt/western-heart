#!/usr/bin/env python3
"""limb_isolation.py — remove cross-limb skin weight bleed from an auto-rigged GLB (2026-10-23, Claude session).

Owner 2026-10-23: "for most fighters the pose looks really good but in like the arms and hands area starts to get a
little wonky ... I need to get deeper rigging and deeper accuracy". Viewed on Skull's re-rig (Bryan heavy, high kick):
the inner thighs stretch into a web of trouser between the legs — vertices of one leg carry weight from the other leg
(bone heat / k-NN diffuse across the crotch gap; the same happens hand↔thigh in an A-pose and arm↔arm never should).

Rule (hierarchy-based, nothing authored):
  every joint is classed by the limb chain it hangs under — left leg (under the left thigh joint), right leg, left arm
  (under the left shoulder/upper arm), right arm — or core (hips, spine, neck, head, tail, everything else).
  For each vertex, the class of its dominant joint decides which influences it may keep:
    leg vertex  -> drops every influence from the other leg and from both arms
    arm vertex  -> drops every influence from the other arm and from both legs
    core vertex -> unchanged (hips and torso legitimately blend both legs / both arms)
  The kept weights are renormalized; a vertex never loses its dominant joint.

Usage (plain glTF: decode meshopt first with tools/anim/gltf_codec.mjs):
    python3 tools/auto_rig/backends/limb_isolation.py --in rigged.glb [--dry-run]
Writes in place (same layout, only JOINTS_0/WEIGHTS_0 values change) and prints per-class counts.
"""
import argparse
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import anim_check as ac  # noqa: E402
from smooth_weights import write_vert_weights  # noqa: E402

# Limb chain roots, matched on joint names (canonical WH/Mixamo/GameRig/Blender spellings).
ROOTS = {
    "L_leg": re.compile(r"^(mixamorig:)?(Left(Up)?Leg|LeftThigh|thigh[._]L|Thigh_L|L_?Thigh|DEF-thigh\.L)$", re.I),
    "R_leg": re.compile(r"^(mixamorig:)?(Right(Up)?Leg|RightThigh|thigh[._]R|Thigh_R|R_?Thigh|DEF-thigh\.R)$", re.I),
    "L_arm": re.compile(r"^(mixamorig:)?(LeftShoulder|LeftArm|LeftUpperArm|shoulder[._]L|upper_arm[._]L|Clavicle_L|DEF-shoulder\.L)$", re.I),
    "R_arm": re.compile(r"^(mixamorig:)?(RightShoulder|RightArm|RightUpperArm|shoulder[._]R|upper_arm[._]R|Clavicle_R|DEF-shoulder\.R)$", re.I),
}
DROP = {
    "L_leg": {"R_leg", "L_arm", "R_arm"},
    "R_leg": {"L_leg", "L_arm", "R_arm"},
    "L_arm": {"R_arm", "L_leg", "R_leg"},
    "R_arm": {"L_arm", "L_leg", "R_leg"},
}


def classify_joints(model):
    """joint index (position in skin.joints) -> class. The first ancestor matching a chain root decides."""
    nodes = model.nodes
    parent = {}
    for i, nd in enumerate(nodes):
        for c in nd.get("children", []):
            parent[c] = i
    out = []
    for nidx in model.joint_nodes:
        cls, n = "core", nidx
        while n is not None:
            name = nodes[n].get("name", "")
            hit = next((k for k, rx in ROOTS.items() if rx.match(name)), None)
            if hit:
                cls = hit
                break
            n = parent.get(n)
        out.append(cls)
    return out


def isolate(path, dry_run=False):
    model = ac.AnimModel(path)
    cls = classify_joints(model)
    counts = {k: 0 for k in ROOTS}
    if not any(c != "core" for c in cls):
        print("no limb chain roots matched; nothing to do (joint names:", [model.nodes[j].get("name") for j in model.joint_nodes][:12], ")")
        return {}
    print("joint classes:", {k: sum(1 for c in cls if c == k) for k in ("core", *ROOTS)})
    total_changed = 0
    for pi, prim in enumerate(model.prims):
        J = np.asarray(prim["joints"]).astype(int)
        W = np.asarray(prim["weights"], dtype=float)
        jcls = np.array(cls, dtype=object)[J]
        dom = np.argmax(W, axis=1)
        dom_cls = jcls[np.arange(len(J)), dom]
        updates = {}
        for v in np.nonzero(dom_cls != "core")[0]:
            dc = dom_cls[v]
            w = W[v].copy()
            bad = np.array([c in DROP[dc] for c in jcls[v]]) & (w > 0)
            if not bad.any():
                continue
            w[bad] = 0.0
            s = w.sum()
            if s <= 0:
                continue
            w /= s
            updates[int(v)] = (J[v].tolist(), w.tolist())
            counts[dc] += 1
        total_changed += len(updates)
        if updates and not dry_run:
            write_vert_weights(path, model, pi, updates)
    print("vertices cleaned per dominant limb:", counts, "total", total_changed, "(dry run)" if dry_run else "")
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    isolate(a.inp, a.dry_run)


if __name__ == "__main__":
    main()
