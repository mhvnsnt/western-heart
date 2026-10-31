"""Unit tests for tools/auto_rig/anim_check.py — run with pytest or plain python3.

Builds minimal synthetic GLBs in-memory (pure python) covering each failure
mode the validator exists to catch:
  clean rigid anim          -> PASS
  child-joint scale keys    -> bone-length VARIANCE flag
  constant joint scale      -> bone REST-DEVIATION flag
  joint translation teleport -> vertex TEARING flag
  channel on a deco node    -> WRONG-NODE flag
"""

import json
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import anim_check  # noqa: E402


def _acc(arrays, types, comp=5126):
    """Pack float arrays into (buffer_bytes, accessor dicts)."""
    buf = b""
    views, accs = [], []
    for arr, typ in zip(arrays, types):
        a = np.asarray(arr, dtype=np.float32)
        pad = (-len(buf)) % 4
        buf += b"\x00" * pad
        views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": a.nbytes})
        buf += a.tobytes()
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[typ]
        acc = {"bufferView": len(views) - 1, "componentType": comp, "count": a.size // n,
               "type": typ}
        if typ == "SCALAR":
            acc["min"], acc["max"] = [float(a.min())], [float(a.max())]
        accs.append(acc)
    return buf, views, accs


def make_glb(anim_channels):
    """3-joint chain Root->Child->GrandChild + deco node; 6 verts, 2 tris.

    anim_channels: list of (node, path, times, values) LINEAR channels.
    Returns path to a temp .glb.
    """
    pos = [[-0.1, 0.05, 0], [0.1, 0.05, 0], [-0.1, 0.95, 0], [0.1, 0.95, 0],
           [-0.1, 1.45, 0], [0.1, 1.45, 0]]
    joints = [[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0],
              [2, 0, 0, 0], [2, 0, 0, 0]]
    weights = [[1, 0, 0, 0]] * 6
    idx = [0, 1, 2, 2, 1, 3, 2, 3, 4, 4, 3, 5]
    ibm = []
    for t in ([0, 0, 0], [0, -1, 0], [0, -1.5, 0]):
        m = np.eye(4)
        m[:3, 3] = t
        ibm.append(m.T.flatten())  # column-major
    arrays = [pos, joints, weights, np.array(ibm, dtype=np.float32)]
    types = ["VEC3", "VEC4", "VEC4", "MAT4"]
    buf, views, accs = _acc(arrays, types)
    # JOINTS_0 must be unsigned short, not float: repack that accessor
    jbuf = np.asarray(joints, dtype=np.uint16).tobytes()
    pad = (-len(buf)) % 4
    buf += b"\x00" * pad
    views[1] = {"buffer": 0, "byteOffset": len(buf), "byteLength": len(jbuf)}
    buf += jbuf
    accs[1] = {"bufferView": 1, "componentType": 5123, "count": 6, "type": "VEC4"}
    ibuf = np.asarray(idx, dtype=np.uint16).tobytes()
    pad = (-len(buf)) % 4
    buf += b"\x00" * pad
    views.append({"buffer": 0, "byteOffset": len(buf), "byteLength": len(ibuf)})
    buf += ibuf
    accs.append({"bufferView": len(views) - 1, "componentType": 5123,
                 "count": len(idx), "type": "SCALAR"})

    samplers, channels = [], []
    for node, path, times, values in anim_channels:
        new_accs = []
        for arr, typ in ((times, "SCALAR"),
                         (values, "VEC3" if path != "rotation" else "VEC4")):
            abuf, aviews, aaccs = _acc([arr], [typ])
            off = len(buf)
            buf += abuf
            base_v = len(views)
            for v in aviews:
                v = dict(v)
                v["byteOffset"] += off
                views.append(v)
            for acc in aaccs:
                acc = dict(acc)
                acc["bufferView"] += base_v
                accs.append(acc)
                new_accs.append(len(accs) - 1)
        samplers.append({"input": new_accs[0], "output": new_accs[1],
                         "interpolation": "LINEAR"})
        channels.append({"sampler": len(samplers) - 1,
                         "target": {"node": node, "path": path}})

    gltf = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0, 3]}],
        "nodes": [
            {"name": "Root", "children": [1], "translation": [0, 0, 0]},
            {"name": "Child", "children": [2], "translation": [0, 1, 0]},
            {"name": "GrandChild", "translation": [0, 0.5, 0]},
            {"name": "Deco"},
        ],
        "meshes": [{"primitives": [{
            "attributes": {"POSITION": 0, "JOINTS_0": 1, "WEIGHTS_0": 2},
            "indices": 4}]}],
        "skins": [{"joints": [0, 1, 2], "inverseBindMatrices": 3}],
        "animations": [{"name": "Test", "samplers": samplers,
                        "channels": channels}],
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": views,
        "accessors": accs,
    }
    js = json.dumps(gltf).encode()
    js += b" " * ((-len(js)) % 4)
    buf += b"\x00" * ((-len(buf)) % 4)
    glb = b"glTF" + struct.pack("<II", 2, 12 + 8 + len(js) + 8 + len(buf))
    glb += struct.pack("<I", len(js)) + b"JSON" + js
    glb += struct.pack("<I", len(buf)) + b"BIN\x00" + buf
    fd, path = tempfile.mkstemp(suffix=".glb")
    with os.fdopen(fd, "wb") as f:
        f.write(glb)
    return path


class _Args:
    bone_var, tear_m, tear_k, edge_max, root_max, max_frames = \
        0.02, 0.35, 8.0, 2.5, 1.0, 120


def run(path):
    m = anim_check.AnimModel(path)
    return anim_check.check_animation(m, m.js["animations"][0], _Args())


def test_clean_passes():
    # small rigid rotation on Child + gentle root bob: no stretch, no tearing
    p = make_glb([
        (1, "rotation", [0, 0.5, 1.0],
         [[0, 0, 0, 1], [0, 0, 0.0436, 0.999], [0, 0, 0, 1]]),
        (0, "translation", [0, 0.5, 1.0],
         [[0, 0, 0], [0, 0.01, 0], [0, 0, 0]]),
    ])
    r = run(p)
    assert r["pass"], r["failures"]
    assert not r["bones_flagged"] and not r["tearing"]["spikes"]


def test_bone_variance_flagged():
    p = make_glb([(1, "scale", [0, 0.5, 1.0],
                   [[1, 1, 1], [1, 1.5, 1], [1, 1, 1]])])
    r = run(p)
    assert not r["pass"]
    assert any(b["bone"] == "Child->GrandChild" for b in r["bones_flagged"]), r


def test_rest_deviation_flagged():
    p = make_glb([(1, "scale", [0, 1.0], [[1, 1.4, 1], [1, 1.4, 1]])])
    r = run(p)
    assert not r["pass"]
    assert any(b["bone"] == "Child->GrandChild"
               for b in r["bones_rest_deviant"]), r


def test_tearing_flagged():
    p = make_glb([(1, "translation", [0, 0.5, 1.0],
                   [[0, 1, 0], [0, 3.0, 0], [0, 1, 0]])])
    r = run(p)
    assert not r["pass"]
    assert r["tearing"]["spikes"], r["tearing"]
    # spikes name the vertex's OWN joints (only Child/GrandChild-weighted verts move), never skin slot 0
    assert all(s["joints"] and set(s["joints"]) <= {"Child", "GrandChild"}
               for s in r["tearing"]["spikes"]), r["tearing"]["spikes"]


def test_wrong_node_flagged():
    p = make_glb([(3, "translation", [0, 1.0], [[0, 0, 0], [5, 0, 0]])])
    r = run(p)
    assert not r["pass"]
    assert "Deco" in r["channels_on_non_joint_nodes"], r


def test_root_offset_flagged():
    # root baked 5 m away from bind (scene placement baked into the clip)
    p = make_glb([(0, "translation", [0, 1.0], [[5, 0, 0], [5, 0.2, 0]])])
    r = run(p)
    assert not r["pass"]
    assert r["root_max_dev_m"] > 4.9, r["root_max_dev_m"]
    assert any("root joint" in f for f in r["failures"]), r["failures"]


def test_cli_exit_codes(tmp_path=None):
    good = make_glb([(0, "translation", [0, 1.0], [[0, 0, 0], [0, 0.02, 0]])])
    bad = make_glb([(1, "scale", [0, 0.5, 1.0],
                     [[1, 1, 1], [1, 2.0, 1], [1, 1, 1]])])
    here = os.path.dirname(os.path.abspath(__file__))
    exe = os.path.join(here, "..", "anim_check.py")
    for path, want in ((good, 0), (bad, 1)):
        rc = subprocess.run([sys.executable, exe, "--in", path, "--quiet"]
                            ).returncode
        assert rc == want, (path, rc, want)


if __name__ == "__main__":
    test_clean_passes()
    test_bone_variance_flagged()
    test_rest_deviation_flagged()
    test_tearing_flagged()
    test_wrong_node_flagged()
    test_root_offset_flagged()
    test_cli_exit_codes()
    print("anim_check tests: 7/7 pass")
