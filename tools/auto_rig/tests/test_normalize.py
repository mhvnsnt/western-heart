#!/usr/bin/env python3
"""Unit tests for backends/normalize.py — needs the test GLB from the e2e run."""

import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backends"))
from normalize import normalize  # noqa: E402

TEST_IN = "/home/hatch/workspace/auto-rig-work/test/humanoid.glb"


def positions(path):
    import json
    d = open(path, "rb").read()
    jl = struct.unpack("<I", d[12:16])[0]
    js = json.loads(d[20:20 + jl])
    boff = 20 + jl
    blen = struct.unpack("<I", d[boff:boff + 4])[0]
    bdat = d[boff + 8:boff + 8 + blen]
    prim = js["meshes"][0]["primitives"][0]
    a = js["accessors"][prim["attributes"]["POSITION"]]
    bv = js["bufferViews"][a["bufferView"]]
    off = (bv.get("byteOffset") or 0) + (a.get("byteOffset") or 0)
    return (np.frombuffer(bdat, dtype=np.float32, count=a["count"] * 3,
                          offset=off).reshape(-1, 3), js)


def test_normalize():
    out = "/tmp/test_norm.glb"
    info = normalize(TEST_IN, out, height=1.8)
    pos, js = positions(out)
    # feet on ground, height matched
    assert abs(pos[:, 1].min()) < 1e-4, pos[:, 1].min()
    assert abs((pos[:, 1].max() - pos[:, 1].min()) - 1.8) < 1e-3
    # still centered under the skeleton (x symmetric about 0)
    assert abs(pos[:, 0].min() + pos[:, 0].max()) < 1e-3, \
        (pos[:, 0].min(), pos[:, 0].max())
    # node transforms baked to identity
    for n in js["nodes"]:
        assert (n.get("translation") or [0, 0, 0]) == [0, 0, 0]
        assert (n.get("scale") or [1, 1, 1]) == [1, 1, 1]
        assert n.get("matrix") is None
    # input untouched
    ipos, _ = positions(TEST_IN)
    assert abs((ipos[:, 1].max() - ipos[:, 1].min())
               - info["height_in"]) < 1e-3
    os.remove(out)


if __name__ == "__main__":
    if not os.path.exists(TEST_IN):
        print("SKIP: test GLB not present (run the Blender e2e first)")
        sys.exit(0)
    test_normalize()
    print("normalize tests: pass")
