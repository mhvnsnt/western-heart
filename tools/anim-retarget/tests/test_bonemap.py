#!/usr/bin/env python3
"""test_bonemap.py — every WH skeleton bone must be reachable from the
Mixamo bone map (tools/anim-retarget/bone_maps/mixamo_to_wh.json).

Run: python3 tools/anim-retarget/tests/test_bonemap.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

def main():
    with open(os.path.join(REPO, "tools/auto_rig/backends/skeleton_template.json")) as f:
        tpl = json.load(f)
    wh_bones = {j["name"] for j in tpl["joints"]}
    with open(os.path.join(HERE, "..", "bone_maps", "mixamo_to_wh.json")) as f:
        bm = json.load(f)["map"]
    # reverse: WH name -> source names that map to it
    covered = {v for v in bm.values() if v}
    missing = sorted(wh_bones - covered)
    print(f"WH bones: {len(wh_bones)}, covered by bone map: {len(covered & wh_bones)}")
    if missing:
        print("MISSING:", missing)
        return 1
    print("PASS: all WH bones reachable from Mixamo map")
    return 0

if __name__ == "__main__":
    sys.exit(main())
