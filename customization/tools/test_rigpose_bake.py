#!/usr/bin/env python3
"""test_rigpose_bake.py — round-trip contract for the Rig & Pose bake stage.

Builds a tiny synthetic skinned GLB, then proves:
  1. a no-`rig` bake leaves skeleton, weights and IBMs untouched;
  2. edit -> save -> reload -> bake is deterministic (byte-identical);
  3. a rest offset changes the skeleton's zero-pose while IBMs stay
     consistent with the new rests (mesh unmoved in world space);
  4. remove_bones drops the joint and renormalizes weights;
  5. a weight "set" stroke fully binds verts near its center.
Run: python3 customization/tools/test_rigpose_bake.py
"""
import json, os, struct, sys, tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "tools", "rig-pose-studio"))
import rigpose_bake as rb
import glb_inspect as gi

def make_fixture(path):
    # 3-bone chain Root->Hips->Spine along +Y; one 6-vert strip skinned to it.
    nodes = [
        {"name": "Root", "children": [1]},
        {"name": "Hips", "translation": [0, 1.0, 0], "children": [2]},
        {"name": "Spine", "translation": [0, 0.5, 0]},
        {"name": "Body", "mesh": 0, "skin": 0},
    ]
    pos = np.array([[0, 0.9, 0], [0.1, 0.9, 0], [0, 1.1, 0],
                    [0.1, 1.1, 0], [0, 1.6, 0], [0.1, 1.6, 0]], dtype=np.float64)
    joints = np.array([[1, 0, 0, 0], [1, 0, 0, 0], [1, 2, 0, 0],
                       [1, 2, 0, 0], [2, 0, 0, 0], [2, 0, 0, 0]], dtype=np.uint16)
    weights = np.array([[1, 0, 0, 0], [1, 0, 0, 0], [0.5, 0.5, 0, 0],
                        [0.5, 0.5, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]], dtype=np.float64)
    idx = np.array([0, 1, 2, 2, 1, 3, 2, 3, 4, 4, 3, 5], dtype=np.uint16)
    js = {"asset": {"version": "2.0", "generator": "rigpose-test"},
          "scene": 0, "scenes": [{"nodes": [0, 3]}], "nodes": nodes,
          "meshes": [{"name": "BodyMesh", "primitives": [{"attributes": {}, "indices": 0}]}],
          "skins": [{"joints": [0, 1, 2], "skeleton": 0}],
          "buffers": [{"byteLength": 0}], "bufferViews": [], "accessors": []}
    buf = bytearray()
    def add(arr, typ, comp="f"):
        return rb.append_acc(js, buf, arr, typ, comp)
    world = rb.world_mats(js)
    ibms = np.array([np.linalg.inv(world[j]).T.reshape(-1) for j in [0, 1, 2]])
    js["skins"][0]["inverseBindMatrices"] = add(ibms, "MAT4")
    prim = js["meshes"][0]["primitives"][0]
    prim["indices"] = add(idx, "SCALAR", "u")
    prim["attributes"]["POSITION"] = add(pos, "VEC3")
    prim["attributes"]["JOINTS_0"] = add(joints, "VEC4", "u")
    prim["attributes"]["WEIGHTS_0"] = add(weights, "VEC4")
    js["buffers"][0]["byteLength"] = len(buf)
    rb.save_glb(path, js, buf)

def load(p):
    return rb.load_glb(p)

def main():
    tmp = tempfile.mkdtemp()
    base = os.path.join(tmp, "base.glb")
    make_fixture(base)
    cust = {"version": 1, "app": "wh-creation-suite", "fighter": "test",
            "attire": "attire1", "base_glb": "base.glb", "out_glb": "out.glb"}
    cj = os.path.join(tmp, "customization.json")

    # 1) no-rig bake is a no-op for skeleton + weights + IBMs
    json.dump(cust, open(cj, "w"))
    out0 = os.path.join(tmp, "out0.glb")
    rb.bake(base, json.load(open(cj)), out0)
    j0, b0 = load(base); j1, b1 = load(out0)
    for i, n in enumerate(j0["nodes"]):
        assert n.get("translation") == j1["nodes"][i].get("translation"), f"node {i} moved"
    wa = rb.read_acc(j0, bytearray(b0), j0["meshes"][0]["primitives"][0]["attributes"]["WEIGHTS_0"])
    wb = rb.read_acc(j1, bytearray(b1), j1["meshes"][0]["primitives"][0]["attributes"]["WEIGHTS_0"])
    assert np.allclose(wa, wb), "weights changed on no-op bake"
    ia = rb.read_acc(j0, bytearray(b0), j0["skins"][0]["inverseBindMatrices"])
    ib = rb.read_acc(j1, bytearray(b1), j1["skins"][0]["inverseBindMatrices"])
    assert np.allclose(ia, ib, atol=1e-5), "IBMs changed on no-op bake"
    print("PASS 1 no-rig bake is a skeleton/weights/IBM no-op")

    # 2) determinism with a full rig section
    cust["rig"] = {
        "bones": {"Spine": {"offset": {"rot_deg": [15, 0, 0]}}},
        "add_bones": [{"name": "Tail", "parent": "Hips", "head": [0, -0.1, -0.2], "tail": [0, -0.2, -0.6]}],
        "weights": [{"bone": "Spine", "center": [0.05, 1.55, 0], "radius": 0.3, "strength": 1.0, "mode": "add"}],
        "visibility": {"BodyMesh": True},
        "pose": {"Hips": {"rot_deg": [0, 10, 0]}},
    }
    json.dump(cust, open(cj, "w"))
    saved = json.load(open(cj))
    o1, o2 = os.path.join(tmp, "o1.glb"), os.path.join(tmp, "o2.glb")
    rb.bake(base, saved, o1); rb.bake(base, saved, o2)
    assert open(o1, "rb").read() == open(o2, "rb").read(), "bake not deterministic"
    print("PASS 2 edit->save->reload->bake is byte-identical")

    # 3) IBMs consistent with edited rests (IBM @ world_rest == I)
    jj, bb = load(o1)
    world = rb.world_mats(jj)
    ibm = rb.read_acc(jj, bytearray(bb), jj["skins"][0]["inverseBindMatrices"])
    for k, jn in enumerate(jj["skins"][0]["joints"]):
        m = ibm[k].reshape(4, 4).T @ world[jn]
        assert np.allclose(m, np.eye(4), atol=1e-4), f"IBM inconsistent for joint {k}"
    names = [jj["nodes"][j].get("name") for j in jj["skins"][0]["joints"]]
    assert "Tail" in names, "added bone missing from skin"
    print("PASS 3 IBMs consistent after rest edits; added bone in skin:", names)

    # 4) remove_bones renormalizes
    cust["rig"] = {"remove_bones": ["Spine"]}
    json.dump(cust, open(cj, "w"))
    o3 = os.path.join(tmp, "o3.glb")
    rb.bake(base, json.load(open(cj)), o3)
    j3, b3 = load(o3)
    assert len(j3["skins"][0]["joints"]) == 2, "joint not removed"
    w3 = rb.read_acc(j3, bytearray(b3), j3["meshes"][0]["primitives"][0]["attributes"]["WEIGHTS_0"])
    assert np.allclose(w3.sum(axis=1), 1.0, atol=1e-5), "weights not renormalized"
    print("PASS 4 remove_bones drops joint, weights renormalize")

    # 5) weight set stroke binds fully near center
    cust["rig"] = {"weights": [{"bone": "Root", "center": [0.0, 0.9, 0.0],
                                 "radius": 0.05, "strength": 1.0, "mode": "set"}]}
    json.dump(cust, open(cj, "w"))
    o4 = os.path.join(tmp, "o4.glb")
    rb.bake(base, json.load(open(cj)), o4)
    j4, b4 = load(o4)
    prim = j4["meshes"][0]["primitives"][0]
    jj4 = rb.read_acc(j4, bytearray(b4), prim["attributes"]["JOINTS_0"])
    w4 = rb.read_acc(j4, bytearray(b4), prim["attributes"]["WEIGHTS_0"])
    v0 = {int(jj4[0, c]): w4[0, c] for c in range(4) if w4[0, c] > 0}
    assert v0.get(0, 0) > 0.99, f"vert0 not bound to Root: {v0}"
    print("PASS 5 weight set stroke binds verts at center to target bone")
    # 6) frame op moves scene roots (intake frame correction)
    cust["rig"] = {"frame": {"translate": [0, 0.5, 0]}}
    json.dump(cust, open(cj, "w"))
    o5 = os.path.join(tmp, "o5.glb")
    rb.bake(base, json.load(open(cj)), o5)
    j5, _b5 = load(o5)
    assert abs(j5["nodes"][0].get("translation", [0, 0, 0])[1] - 0.5) < 1e-9, "frame translate not applied to scene root"
    w5 = rb.world_mats(j5)
    hips_i = [i for i, n in enumerate(j5["nodes"]) if n.get("name") == "Hips"][0]
    assert abs(w5[hips_i][1, 3] - 1.5) < 1e-6, f"hips world wrong after frame: {w5[hips_i][:3, 3]}"
    print("PASS 6 frame translate re-frames scene roots + skeleton together")
    print("ALL RIGPOSE BAKE TESTS PASS")

if __name__ == "__main__":
    main()
