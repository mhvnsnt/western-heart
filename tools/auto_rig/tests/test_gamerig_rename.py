#!/usr/bin/env python3
"""Unit tests for the GameRig backend's pure-python joint renaming.

The DEF-bone -> WH canonical rename is what makes a GameRig export
pass validate.py's bone gate, and it runs on the exported GLB's JSON
chunk (no Blender needed), so it is testable with plain python3:

    python3 -m pytest tools/auto_rig/tests/test_gamerig_rename.py
    # or
    python3 tools/auto_rig/tests/test_gamerig_rename.py
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backends"))

import gamerig_backend as g  # noqa: E402


def test_core_spine_chain():
    assert g.def_to_canonical("DEF-spine") == "Hips"
    assert g.def_to_canonical("DEF-spine.001") == "Spine"
    assert g.def_to_canonical("DEF-spine.003") == "Spine2"
    assert g.def_to_canonical("DEF-spine.004") == "Neck"
    assert g.def_to_canonical("DEF-spine.005") == "Head"
    assert g.def_to_canonical("DEF-spine.006") == "HeadTop"


def test_limbs_and_leaf_segments():
    assert g.def_to_canonical("DEF-upper_arm.L") == "LeftArm"
    assert g.def_to_canonical("DEF-upper_arm.L.001") == "LeftArm.001"
    assert g.def_to_canonical("DEF-forearm.R") == "RightForeArm"
    assert g.def_to_canonical("DEF-thigh.L") == "LeftUpLeg"
    assert g.def_to_canonical("DEF-shin.R.001") == "RightLeg.001"
    assert g.def_to_canonical("DEF-toe.L") == "LeftToeBase"


def test_fingers_and_palms():
    assert g.def_to_canonical("DEF-thumb.01.L") == "LeftHandThumb1"
    assert g.def_to_canonical("DEF-f_index.02.R") == "RightHandIndex2"
    assert g.def_to_canonical("DEF-f_pinky.03.L") == "LeftHandPinky3"
    assert g.def_to_canonical("DEF-palm.04.R") == "RightHandPalm4"


def test_unknown_names_lose_only_def_prefix():
    # documented fallback: unmapped DEF bones keep their name minus
    # the DEF- prefix; names without the prefix pass through untouched
    assert g.def_to_canonical("DEF-some_future_bone") == "some_future_bone"
    assert g.def_to_canonical("Hips") == "Hips"


def _tiny_glb(joint_names):
    """Build a minimal GLB whose skin lists the given joint node names."""
    import json as _json
    nodes = [{"name": n} for n in joint_names]
    js = {"asset": {"version": "2.0"}, "nodes": nodes,
          "skins": [{"joints": list(range(len(joint_names)))}],
          "scene": 0, "scenes": [{"nodes": []}]}
    payload = _json.dumps(js).encode()
    payload += b" " * (-len(payload) % 4)
    total = 12 + 8 + len(payload)
    return (b"glTF" + struct.pack("<I", 2) + struct.pack("<I", total) +
            struct.pack("<I", len(payload)) + b"JSON" + payload)


def test_glb_joint_rename_roundtrip(tmp_path=None):
    src = _tiny_glb(["DEF-spine", "DEF-upper_arm.L", "DEF-f_middle.03.R",
                     "DEF-pelvis.L", "CustomBone"])
    if tmp_path is None:
        import tempfile
        tmp_path = tempfile.mkdtemp()
    inp = os.path.join(str(tmp_path), "in.glb")
    outp = os.path.join(str(tmp_path), "out.glb")
    with open(inp, "wb") as f:
        f.write(src)
    with open(outp, "wb") as f:
        f.write(src)
    mapping = g.rename_glb_joints(outp)  # renames in place
    assert mapping["DEF-spine"] == "Hips"
    assert mapping["DEF-upper_arm.L"] == "LeftArm"
    assert "CustomBone" not in mapping
    names = g.joint_names_of_glb(outp)
    assert names == ["Hips", "LeftArm", "RightHandMiddle3", "LeftPelvis",
                     "CustomBone"]


if __name__ == "__main__":
    test_core_spine_chain()
    test_limbs_and_leaf_segments()
    test_fingers_and_palms()
    test_unknown_names_lose_only_def_prefix()
    test_glb_joint_rename_roundtrip()
    print("test_gamerig_rename: all tests passed")
