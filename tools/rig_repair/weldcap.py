#!/usr/bin/env python3
"""weldcap.py - weld/cap verification stage (headless Blender + numpy assert).

LESSONS (measured 2026-10-15, do not "optimize"):
  - bmesh.ops.remove_doubles, even at 1e-6, CREATED 19 boundary holes on a
    watertight mesh (merging exact-duplicate verts that were load-bearing).
  - bmesh sees UV-seam splits as boundary edges; "capping" them manufactures
    holes (measured: 19).
  - A pure Blender import->export roundtrip preserves 0 boundary edges.
So this stage does NOT mutate topology. It recalculates normals and then
HARD-ASSERTS (numpy, welded by position so UV seams don't count):
    boundary_edges_holes == 0   (the 266-open-edge incident is impossible by
                                 assertion -- the stage FAILS loudly)
    nonmanifold_edges <= input count
If holes exist, the stage fails for manual review; blind auto-capping is
deferred until a model with real cut holes needs it (the bmesh UV-seam trap
above is why).

usage (inside Blender):
  blender --background ... --python weldcap.py -- --in MODEL.glb
      --out MODEL_weld.glb --report weldcap.json
"""
import bpy
import sys, os, json

argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d
IN = opt("--in", None); OUT = opt("--out", None); REP = opt("--report", None)
assert IN and OUT and REP, "--in/--out/--report required"
assert not os.path.exists(OUT), f"refusing to overwrite {OUT}"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert meshes, "no meshes in " + IN

import bmesh
report = {"in": IN, "out": OUT, "meshes": []}
for o in meshes:
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.update_edit_mesh(o.data)
    bpy.ops.object.mode_set(mode="OBJECT")
    report["meshes"].append({"name": o.name})

bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB",
                          export_animations=False, export_skins=True,
                          export_image_format="AUTO")

# hard assert: numpy edge count on position-welded topology
import struct as _struct
import numpy as _np
def _edge_counts(path):
    b = open(path, "rb").read()
    L = _struct.unpack("<I", b[12:16])[0]
    jj = json.loads(b[20:20 + L])
    o = 20 + L
    bins = []
    while o + 8 <= len(b):
        cl, ct = _struct.unpack("<II", b[o:o + 8])
        if ct == 0x004E4942:
            bins.append(b[o + 8:o + 8 + cl])
        o += 8 + cl
    def _acc(i, n=1, dt=None):
        a = jj["accessors"][i]; bv = jj["bufferViews"][a["bufferView"]]
        if dt is None:
            dt = _np.dtype({5121: _np.uint8, 5123: _np.uint16, 5125: _np.uint32}[a["componentType"]])
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        return _np.frombuffer(bins[bv.get("buffer", 0)], dt, count=a["count"] * n, offset=off)
    holes = nm = 0
    for m in jj["meshes"]:
        for pr in m["primitives"]:
            at = pr["attributes"]
            P = _acc(at["POSITION"], 3, _np.dtype(_np.float32)).reshape(-1, 3).astype(_np.float64)
            _, wid = _np.unique(_np.round(P / 1e-6).astype(_np.int64), axis=0, return_inverse=True)
            F = wid[_acc(pr["indices"]).reshape(-1, 3)]
            e = _np.sort(_np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1)
            e = e[e[:, 0] != e[:, 1]]
            _, cnt = _np.unique(e, axis=0, return_counts=True)
            holes += int((cnt == 1).sum()); nm += int((cnt > 2).sum())
    return holes, nm
d_in, d_out = _edge_counts(IN), _edge_counts(OUT)
report["detect_in"] = {"boundary_edges_holes": d_in[0], "nonmanifold_edges": d_in[1]}
report["detect_out"] = {"boundary_edges_holes": d_out[0], "nonmanifold_edges": d_out[1]}
report["assert"] = {"open_edges_zero": d_out[0] == 0,
                    "nonmanifold_not_increased": d_out[1] <= d_in[1]}
json.dump(report, open(REP, "w"), indent=1)
print(json.dumps(report["assert"]))
if not report["assert"]["open_edges_zero"]:
    raise RuntimeError(f"WELDCAP ASSERT FAILED: {d_out[0]} open edges in {OUT} -- manual review required")
if not report["assert"]["nonmanifold_not_increased"]:
    raise RuntimeError(f"WELDCAP ASSERT FAILED: non-manifold increased {d_in[1]} -> {d_out[1]}")
print("weldcap: asserts passed")
