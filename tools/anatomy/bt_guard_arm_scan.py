#!/usr/bin/env python3
"""BT-guard multi-arm derivation tool (2026-11-06).

The back-turned guard exception (owner rulings 2026-11-06) is DATA-DRIVEN:
a fighter keeps guard while back-turned only when its in-game model data
carries MORE THAN ONE ARM PAIR. This tool re-derives that roster from the
fighters' in-game GLBs, so the table checked into game/js/bt-guard.js can
be audited against the bytes at any time (test/back-turned.test.mjs runs
the same detector against the checked-in table).

Detector (identical rule in the node test):
  an ARM CHAIN ROOT is a skin joint whose name reads as a shoulder /
  upper-arm start (shoulder, upper_arm, upperarm, LeftArm/RightArm, or a
  name ending in 'arm' without 'fore'), whose PARENT joint is NOT itself
  an arm bone (arm/shoulder/elbow/wrist/hand/clavicle), and which has at
  least one hand descendant.
  Mid-chain segment bones (.001 duplicates, DEF chain segments, lace /
  sleeve helper bones under an arm) are NOT roots: their parent is an arm
  bone, so they never start a chain. A fighter is multi-arm when the
  model carries MORE THAN 2 chain roots (more than one pair).

Usage: python3 tools/anatomy/bt_guard_arm_scan.py [glb ...]
With no arguments it scans the in-game models of the owner-named fighters
plus the control model, reading only each GLB's JSON chunk (the skeleton
lives there; mesh bytes are never parsed).

Findings at derivation time (2026-11-06, game main after #1611):
  chatur  roster/rahkasa/attires/attire1/model-rigged-textured.glb
          4 chains -> QUALIFIES (primary Mixamo pair + Rigify DEF pair
          rooted independently at the rig root).
  dxmmii  roster/dxmmii/attires/attire1/model-rigged.glb,
          roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb,
          game/assets/models/dxmmii.glb: 2 chains each -> does NOT
          qualify yet; attire2/model.glb is unrigged (no skeleton).
  zen     roster/zen/attires/attire1/model-rigged.glb, oversoul,
          tentacle (tentacles are not arm chains: no shoulder/elbow/
          wrist structure), spirit (no arm chains at all): none qualify.
  Roster-wide sweep of game/assets/models/ (64 GLBs): every other model
  carries exactly one pair. The one apparent extra (zafina.glb's
  RightArm under RightShoulder) is the standard Mixamo clavicle->arm
  chain counted twice by name shape; its parent IS a shoulder bone, so
  the parent rule above excludes it — chain roots must be independent.

Findings after the owner's rigging order (2026-11-06, "We have to rig
DXMMII arms extras and zens tentacles in his tentacle forms"; method in
docs/movesets/BT-GUARD-RIGGING-2026-11-06.md):
  dxmmii  attire1: 4 chains -> QUALIFIES (a second pair — Shoulder2 /
          Arm2 / ForeArm2 / Hand2 per side, roots parented to Spine2 —
          was rigged onto the extra-arm geometry the source mesh always
          carried detached above the head; bind pose unchanged).
          patchwork-dj + game/assets twin: still 2 — their source
          holds NO extra-arm geometry (Mokujin-family bodies), so
          there is nothing to rig. attire2: no extra-arm geometry and
          unrigged.
  zen     tentacle form: 7 chains -> QUALIFIES (the five tentacle
          chains rooted outside the arms — T1/T11 hip, T2/T3 leg,
          T10 head — renamed into arm-chain form: T#_UpperArm roots,
          T#_Hand tips; names only, BIN byte-identical). attire1 /
          oversoul / spirit unchanged and still negative.
"""
import json
import struct
import sys

DEFAULT_MODELS = [
    "roster/rahkasa/attires/attire1/model-rigged-textured.glb",   # chatur (in-game)
    "roster/dxmmii/attires/attire1/model-rigged.glb",             # dxmmii slot 1
    "roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb",
    "game/assets/models/dxmmii.glb",
    "roster/zen/attires/attire1/model-rigged.glb",                # zen
    "roster/zen/oversoul/model-rigged.glb",
    "roster/zen/tentacle/model-rigged.glb",
    "roster/zen/spirit/model-rigged.glb",
    "game/assets/models/jin-body.glb",                            # control: one pair
]


def arm_chain_roots(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError(f"{path}: not a GLB")
    (clen,) = struct.unpack("<I", data[12:16])
    js = json.loads(data[20:20 + clen])
    nodes = js.get("nodes", [])
    joints = set()
    for skin in js.get("skins", []):
        joints.update(skin.get("joints", []))
    parent = {}
    for i, node in enumerate(nodes):
        for child in node.get("children", []):
            parent[child] = i

    def is_arm_word(name):
        return any(k in name for k in ("arm", "shoulder", "elbow", "wrist", "hand", "clavicle"))

    roots = []
    for j in sorted(joints):
        name = nodes[j].get("name", "")
        low = name.lower()
        is_start = (
            any(k in low for k in ("shoulder", "upper_arm", "upperarm"))
            or low in ("leftarm", "rightarm")
            or (low.endswith("arm") and "fore" not in low)
        )
        p = parent.get(j)
        parent_is_arm = p is not None and is_arm_word(nodes[p].get("name", "").lower())
        if not is_start or parent_is_arm:
            continue
        hands = 0
        stack = [j]
        while stack:
            x = stack.pop()
            if "hand" in nodes[x].get("name", "").lower():
                hands += 1
            stack.extend(nodes[x].get("children", []))
        if hands:
            roots.append(name)
    return roots


def main():
    paths = sys.argv[1:] or DEFAULT_MODELS
    for path in paths:
        roots = arm_chain_roots(path)
        verdict = "MULTI-ARM (qualifies)" if len(roots) > 2 else "one pair"
        print(f"{path}\n  chains={len(roots)} {roots} -> {verdict}")


if __name__ == "__main__":
    main()
