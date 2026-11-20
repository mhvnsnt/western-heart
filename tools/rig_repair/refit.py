#!/usr/bin/env python3
"""refit.py - skeleton refit (the missing core step), headless Blender.

No free tool refits an EXISTING skeleton in place (every auto-rigger builds a
new skeleton, breaking clip compatibility). This implements the
vendor-documented "volume mode" algorithm from Voxel Heat Diffuse Skinning as
headless Blender Python:

  for each limb bone joint: ray-cast through the mesh along several axes,
  take entry/exit points, move the joint to the SHORTEST chord's midpoint
  (the volume center).

Mitigations (per spec):
  * cast along several axes; axes that miss the mesh are skipped, not guessed;
  * displacement clamped to --max-disp (default 0.10 m);
  * joints with no valid chord, or displacement > --outlier-disp (default
    0.06 m), are logged as outliers in the JSON report and still applied
    (clamped) -- nothing is silently skipped.

After repositioning, the GLB is exported from Blender, which RECOMPUTES the
inverse bind matrices from the new rest pose. The joint NAMES and HIERARCHY
are unchanged, so every existing animation clip (local rotations) keeps
playing -- the deformation just follows bones that now sit inside the mesh
volume instead of ~5 cm outside it.

usage (inside Blender):
  blender --background --factory-startup --disable-autoexec --python-exit-code 1 \\
      --python refit.py -- --in MODEL.glb --out MODEL_refit.glb
      --report refit.json [--joints arm,forearm,hand,upleg,leg,foot,shoulder]
      [--max-disp 0.10] [--outlier-disp 0.06]

Inputs are never modified; --out must be a new path.
"""
import bpy
import sys, os, json, re
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# ---------------------------------------------------------------- args
argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d):
    return argv[argv.index(k) + 1] if k in argv else d

IN = opt("--in", None); OUT = opt("--out", None); REP = opt("--report", None)
JOINTS = [j.strip().lower() for j in opt("--joints", "shoulder,arm,forearm,hand,upleg,leg,foot").split(",")]
MAX_DISP = float(opt("--max-disp", "0.10"))
OUTLIER_DISP = float(opt("--outlier-disp", "0.06"))
RAY_DIST = float(opt("--ray-dist", "2.0"))
assert IN and OUT and REP, "--in/--out/--report required"
assert not os.path.exists(OUT), f"refusing to overwrite {OUT}"

AXES = [(1, 0, 0), (0, 1, 0), (0, 0, 1),
        (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1), (1, 1, -1)]
AXES = [Vector(a).normalized() for a in AXES]

def norm(n):
    n = re.sub(r"^mixamorig\d*[:_]?", "", n or "", flags=re.I)
    return n.replace(".", "").replace(" ", "").lower()

# ------------------------------------------------------------ import
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
assert arm, "no armature found in " + IN
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"
          and any(m.type == "ARMATURE" for m in o.modifiers)]
if not meshes:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
assert meshes, "no meshes found in " + IN
print("refit: armature", arm.name, "| meshes",
      [(m.name, len(m.data.polygons)) for m in meshes], file=sys.stderr)

# evaluated meshes -> ONE combined BVH in world space.
# (Do NOT fit against the largest mesh only: on multi-mesh models the largest
# mesh can be an accessory -- e.g. Pantera's gloves -- which corrupts the
# refit. Merge-audit fix 2026-10-15.)
deps = bpy.context.evaluated_depsgraph_get()
ev = arm.evaluated_get(deps)  # noqa: F841 (keeps depsgraph honest)
all_verts, all_polys = [], []
for mo in meshes:
    mev = mo.evaluated_get(deps).to_mesh()
    mw = mo.matrix_world
    base = len(all_verts)
    all_verts.extend([mw @ v.co for v in mev.vertices])
    all_polys.extend([[vi + base for vi in p.vertices] for p in mev.polygons])
    mo.evaluated_get(deps).to_mesh_clear()
bvh = BVHTree.FromPolygons(all_verts, all_polys)

def want(bone_name):
    nn = norm(bone_name)
    # match whole-word-ish: e.g. "arm" matches "leftarm" but not "forearm"
    for j in JOINTS:
        if re.search(rf"(^|_|\.){re.escape(j)}($|_|\.)", nn):
            return True
        # also match side-prefixed: leftarm / arm_l / l_arm
        if nn in (f"left{j}", f"right{j}", f"{j}_l", f"{j}_r", f"l_{j}", f"r_{j}"):
            return True
    return False

def inside_mesh(p):
    """3-axis ray-parity vote: odd hits before p along the ray = inside."""
    votes = 0
    for ax in AXES[:3]:
        wa = (arm.matrix_world.to_3x3() @ ax).normalized()
        hits = 0
        oo = p - wa * RAY_DIST
        while True:
            h, _, _, _ = bvh.ray_cast(oo, wa, RAY_DIST * 2)
            if h is None or (h - p).dot(wa) > 1e-6:
                break
            hits += 1
            oo = h + wa * 1e-4
        if hits % 2 == 1:
            votes += 1
    return votes >= 2


def volume_center_inside(p):
    """Shortest chord's midpoint (valid only when p is inside the mesh)."""
    cands = []
    for ax in AXES:
        wa = (arm.matrix_world.to_3x3() @ ax).normalized()
        h1, _, _, _ = bvh.ray_cast(p, wa, RAY_DIST)
        h2, _, _, _ = bvh.ray_cast(p, -wa, RAY_DIST)
        if h1 is None or h2 is None:
            continue
        length = (h1 - h2).length
        if length < 1e-6:
            continue
        cands.append((length, (h1 + h2) / 2))
    if not cands:
        return None, 0
    length, mid = min(cands, key=lambda c: c[0])
    return mid, length


def volume_center_outside(p):
    """Joint is outside the mesh: nearest surface point, then half the local
    inward thickness = the volume center of the limb at that point."""
    c, n, _, _ = bvh.find_nearest(p)
    inward = (-n).normalized()
    h, _, _, _ = bvh.ray_cast(c + inward * 1e-3, inward, RAY_DIST)
    if h is None:
        return c, 0.0  # fallback: the surface itself
    return (c + h) / 2, (h - c).length


def move_joint(eb, new_p_world):
    """Move a joint (bone head). For connected bones the joint IS the parent's
    tail -- move that so the child follows instead of breaking the chain."""
    inv = arm.matrix_world.inverted()
    if eb.use_connect and eb.parent:
        eb.parent.tail = inv @ new_p_world
    else:
        eb.head = inv @ new_p_world


report = {"in": IN, "out": OUT, "armature": arm.name, "meshes": [m.name for m in meshes],
          "max_disp": MAX_DISP, "joints": []}
moved, outliers = 0, 0

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
try:
    for eb in arm.data.edit_bones:
        if not want(eb.name):
            continue
        p = arm.matrix_world @ eb.head
        jr = {"bone": eb.name,
              "old_head": [round(float(x), 5) for x in p]}
        if inside_mesh(p):
            mid, length = volume_center_inside(p)
            jr["inside"] = True
            jr["chord_len"] = round(float(length), 5)
        else:
            mid, length = volume_center_outside(p)
            jr["inside"] = False
            jr["thickness"] = round(float(length), 5)
        disp = mid - p
        dl = disp.length
        clamped = False
        if dl > MAX_DISP:
            disp = disp.normalized() * MAX_DISP
            dl = MAX_DISP
            clamped = True
        new_p = p + disp
        move_joint(eb, new_p)
        moved += 1
        jr["status"] = "moved" + (" (clamped)" if clamped else "")
        jr["new_head"] = [round(float(x), 5) for x in new_p]
        jr["displacement"] = round(float(dl), 5)
        if dl > OUTLIER_DISP or not jr["inside"]:
            jr["outlier"] = True
            outliers += 1
        report["joints"].append(jr)
finally:
    bpy.ops.object.mode_set(mode="OBJECT")

# (combined BVH meshes were cleared per-mesh above; nothing left to clear)

report["moved"] = moved
report["outliers"] = outliers
report["total_candidates"] = len(report["joints"])

# ------------------------------------------------------------ export
# Blender's glTF exporter recomputes inverseBindMatrices from the new rest
# pose -- this is what keeps existing local-rotation clips playing.
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB",
                          export_animations=False, export_skins=True,
                          export_image_format="AUTO")
json.dump(report, open(REP, "w"), indent=1)
print(json.dumps({"moved": moved, "outliers": outliers,
                  "candidates": len(report["joints"])}))
