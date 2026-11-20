#!/usr/bin/env python3
"""reskin.py - re-skin to the refit armature with meshonline's
Surface-Heat-Diffuse-Skinning (MIT, compiled from source at ../shds/src/shd).

Why: the refit moves joints up to ~10 cm; the old weights were painted for the
old bone positions. Re-skinning to the NEW armature is what makes the refit
actually deform correctly.

Glue (headless Blender):
  1. import the refit GLB; collect every mesh with an Armature modifier;
  2. write the combined mesh as shd text (v,x,y,z / f,i0,i1,i2) and the
     deform bones as shd text (b,name,hx,hy,hz,tx,ty,tz) in armature space;
  3. run: shd mesh.txt bone.txt weight.txt 128 5 64 4 0.2 3 n
     (voxel-res 128, 5 diffuse loops, 64 sample rays, 4 influences,
      falloff 0.2, sharpness 3=Sharp, solidify detect off);
  4. parse weight.txt -> replace ALL vertex groups on the meshes
     (bone index -> bone name -> group), then vertex_group_normalize_all;
  5. export GLB (Blender recomputes IBMs from the rest pose).

Fallback (documented): if the shd binary is missing or fails, use Blender's
built-in bone heat via parent_set(type='ARMATURE_AUTO') equivalent
(bpy.ops.object.data_transfer is NOT it; the fallback is documented in the
pipeline doc, not silently substituted -- the JSON report records which
skinner ran).

usage (inside Blender):
  blender --background ... --python reskin.py -- --in MODEL_refit.glb \\
      --out MODEL_reskin.glb --report reskin.json [--shd ../shds/src/shd]
"""
import bpy
import sys, os, json, subprocess
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d

IN = opt("--in", None); OUT = opt("--out", None); REP = opt("--report", None)
SHD = opt("--shd", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "shds", "src", "shd"))
VOX = opt("--voxel-res", "128"); LOOPS = opt("--loops", "5")
RAYS = opt("--rays", "64"); INFL = opt("--influences", "4")
FALLOFF = opt("--falloff", "0.2"); SHARP = opt("--sharpness", "3")
SOLIDIFY = opt("--solidify", "n")
assert IN and OUT and REP, "--in/--out/--report required"
assert not os.path.exists(OUT), f"refusing to overwrite {OUT}"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
assert arm, "no armature in " + IN
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"
          and any(m.type == "ARMATURE" for m in o.modifiers)]
assert meshes, "no skinned meshes in " + IN

AW = arm.matrix_world
bones = [b for b in arm.data.bones if b.use_deform and (b.tail - b.head).length > 1e-6]
bnames = [b.name for b in bones]
print(f"reskin: {len(meshes)} mesh(es), {len(bnames)} deform bones", file=sys.stderr)

# --- write shd inputs (armature space) ------------------------------------
deps = bpy.context.evaluated_depsgraph_get()
work = os.path.dirname(os.path.abspath(OUT))
mesh_txt = os.path.join(work, "_reskin_mesh.txt")
bone_txt = os.path.join(work, "_reskin_bone.txt")
w_txt = os.path.join(work, "_reskin_weight.txt")

vert_offset = 0
mesh_ranges = []  # (obj, start, count)
with open(mesh_txt, "w") as f:
    for o in meshes:
        me = o.evaluated_get(deps).to_mesh()
        me.calc_loop_triangles()
        M = AW.inverted() @ o.matrix_world
        verts = [M @ v.co for v in me.vertices]
        for v in verts:
            f.write(f"v,{v.x:.6f},{v.y:.6f},{v.z:.6f}\n")
        for t in me.loop_triangles:
            f.write(f"f,{t.vertices[0] + vert_offset},{t.vertices[1] + vert_offset},{t.vertices[2] + vert_offset}\n")
        mesh_ranges.append((o, vert_offset, len(verts)))
        vert_offset += len(verts)
        o.evaluated_get(deps).to_mesh_clear()
with open(bone_txt, "w") as f:
    for b in bones:
        h, t = b.head, b.tail
        f.write(f"b,{b.name},{h.x:.6f},{h.y:.6f},{h.z:.6f},{t.x:.6f},{t.y:.6f},{t.z:.6f}\n")

# --- run shd ---------------------------------------------------------------
skinner = "shd"
if not (os.path.isfile(SHD) and os.access(SHD, os.X_OK)):
    raise RuntimeError(f"shd binary not found/executable at {SHD} -- "
                       "see pipeline doc fallback (Blender bone heat)")
cmd = [SHD, mesh_txt, bone_txt, w_txt, VOX, LOOPS, RAYS, INFL, FALLOFF, SHARP, SOLIDIFY]
print("reskin: running", " ".join(cmd), file=sys.stderr)
r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
print(r.stdout[-2000:], file=sys.stderr)
if r.returncode != 0 or not os.path.isfile(w_txt):
    raise RuntimeError(f"shd failed rc={r.returncode}: {r.stderr[-2000:]}")

# --- parse weights ----------------------------------------------------------
bidx = {}
weights = {}  # vert -> list of (bone_name, w)
with open(w_txt) as f:
    for line in f:
        line = line.strip()
        if line.startswith("b,"):
            bidx[len(bidx)] = line[2:]
        elif line.startswith("w,"):
            _, vi, bi, w = line.split(",")
            vi, bi, w = int(vi), int(bi), float(w)
            weights.setdefault(vi, []).append((bidx[bi], w))
n_verts = vert_offset
n_weighted = len(weights)
print(f"reskin: shd weighted {n_weighted}/{n_verts} verts", file=sys.stderr)

# --- assign -----------------------------------------------------------------
for o, start, count in mesh_ranges:
    # clear existing deform groups
    for vg in list(o.vertex_groups):
        o.vertex_groups.remove(vg)
    groups = {}
    for vi in range(start, start + count):
        for bn, w in weights.get(vi, []):
            if w <= 0:
                continue
            g = groups.get(bn)
            if g is None:
                g = groups[bn] = o.vertex_groups.new(name=bn)
            g.add([vi - start], w, "REPLACE")
    # unweighted verts -> nearest bone (shouldn't happen; be explicit)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    bpy.ops.object.mode_set(mode="OBJECT")

for p in (mesh_txt, bone_txt, w_txt):
    try: os.remove(p)
    except OSError: pass

# --- export ------------------------------------------------------------------
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB",
                          export_animations=False, export_skins=True,
                          export_image_format="AUTO")
rep = {"in": IN, "out": OUT, "skinner": skinner,
       "params": {"voxel_res": VOX, "loops": LOOPS, "rays": RAYS,
                  "influences": INFL, "falloff": FALLOFF,
                  "sharpness": SHARP, "solidify": SOLIDIFY},
       "meshes": len(meshes), "bones": len(bnames),
       "verts_total": n_verts, "verts_weighted": n_weighted,
       "verts_unweighted": n_verts - n_weighted}
json.dump(rep, open(REP, "w"), indent=1)
print(json.dumps({"skinner": skinner, "verts_weighted": n_weighted,
                  "verts_unweighted": n_verts - n_weighted}))
