#!/usr/bin/env python3
"""Unit tests for tools/auto_rig/backends/retarget.py — run with pytest or plain python3."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backends"))
from retarget import canonicalize, gate_bones


def test_mixamo_passthrough():
    names = ["mixamorig_Hips_01", "mixamorig_LeftArm_09", "mixamorig_RightFoot_042",
             "mixamorig_LeftHandIndex2_017"]
    mapping, unmapped = canonicalize(names)
    assert mapping["mixamorig_Hips_01"] == "Hips", mapping
    assert mapping["mixamorig_LeftArm_09"] == "LeftArm", mapping
    assert mapping["mixamorig_RightFoot_042"] == "RightFoot", mapping
    assert mapping["mixamorig_LeftHandIndex2_017"] == "LeftHandIndex2", mapping
    assert unmapped == [], unmapped


def test_blender_conventions():
    names = ["Hips", "Spine", "thigh.L", "shin.R", "hand.L", "upperarm.R"]
    mapping, unmapped = canonicalize(names)
    assert mapping["Hips"] == "Hips"
    assert mapping["thigh.L"] == "LeftUpLeg", mapping
    assert mapping["shin.R"] == "RightLeg", mapping
    assert mapping["hand.L"] == "LeftHand", mapping
    assert mapping["upperarm.R"] == "RightArm", mapping
    assert unmapped == [], unmapped


def test_gate():
    canon = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head",
             "LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand",
             "RightShoulder", "RightArm", "RightForeArm", "RightHand",
             "LeftUpLeg", "LeftLeg", "LeftFoot",
             "RightUpLeg", "RightLeg", "RightFoot"]
    assert gate_bones(canon) == []
    missing = gate_bones(["Hips"])
    assert "Head" in missing and "LeftArm" in missing


if __name__ == "__main__":
    test_mixamo_passthrough()
    test_blender_conventions()
    test_gate()
    print("retarget tests: 3/3 pass")
