#!/usr/bin/env python3
"""diag_joints.py - inside/outside diagnostic for skeleton joints (Blender headless)."""
import bpy
import sys, os, json, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d
IN = opt("--in", None); REP = opt("--report", None)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"
          and any(m.type == "ARMATURE" for m in o.modifiers)]
main = max(meshes, key=lambda o: len(o.data.polygons))
deps = bpy.context.evaluated_depsgraph_get()
me = main.evaluated_get(deps).to_mesh()
bvh = BVHTree.FromPolygons([v.co for v in me.vertices],
                           [list(p.vertices) for p in me.polygons])

def norm(n):
    n = re.sub(r"^mixamorig\d*[:_]?", "", n or "", flags=re.I)
    return n.replace(".", "").replace(" ", "").lower()

def inside(p):
    # parity: cast +X far; odd hits = inside (use two-sided by casting both ways)
    hits = 0
    for d in (Vector((1, 0, 0)), Vector((-1, 0, 0))):
        o = p - d * 10.0
        h, _, _, _ = bvh.ray_cast(o, d, 20.0)
        # count intersections between o and p: walk the ray
        oo = o
        while True:
            h, _, _, _ = bvh.ray_cast(oo, d, 20.0)
            if h is None or (h - p).dot(d) > 0:
                break
            hits += 1
            oo = h + d * 1e-4
            if (oo - o).length > 20.0:
                break
    return hits

out = []
for b in arm.pose.bones:
    nn = norm(b.name)
    if not re.search(r"(arm|forearm|hand|upleg|leg|foot|shoulder)", nn):
        continue
    if re.search(r"(finger|thumb|index|middle|ring|pinky|toe)", nn):
        continue
    p = arm.matrix_world @ b.head
    loc, nrm, idx, dist = bvh.find_nearest(p)
    out.append({"bone": b.name, "head": [round(float(x), 4) for x in p],
                "closest_dist": round(float(dist), 4),
                "parity_hits": inside(p)})
    print(f"{b.name:28} dist_to_surface={dist:.4f} parity_hits={out[-1]['parity_hits']}")
main.evaluated_get(deps).to_mesh_clear()
json.dump(out, open(REP, "w"), indent=1)
