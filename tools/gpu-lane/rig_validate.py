#!/usr/bin/env python3
"""Shared rig validation for GPU batch jobs (Python mirror of
game/js/rig-compat.js matching, exact by construction: patterns
come from rig-patterns.json, which gen_rig_patterns.py generates
FROM rig-compat.js — never a hand-copied second list).
Normalization mirrors the JS: lowercase, strip non-alphanumerics,
then substring match. Used by rig-batch-job.py and
creation-batch-job.py.
"""
import json
import struct

CORE_ROLES = ["hips", "spine", "chest", "neck", "head",
              "shoulderL", "elbowL", "wristL", "shoulderR", "elbowR", "wristR",
              "hipL", "kneeL", "ankleL", "hipR", "kneeR", "ankleR"]


def norm(s):
    return "".join(c for c in str(s).lower() if c.isalnum())


def glb_node_names(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"glTF":
        raise ValueError(f"not a GLB file: {path}")
    clen = struct.unpack("<I", data[12:16])[0]
    chunk = json.loads(data[20:20 + clen])
    return [n.get("name") for n in chunk.get("nodes", []) if n.get("name")]


def map_roles(node_names, patterns):
    normalized = [norm(n) for n in node_names]
    out = {}
    for role, pat in patterns.items():
        p = norm(pat)
        for orig, n in zip(node_names, normalized):
            if p and p in n:
                out[role] = orig
                break
    return out
