#!/usr/bin/env python3
"""proof.py - before/after stress-pose proof renders (headless Blender).

Renders the model at 4 stress poses (arms raised, crucifix, finger guns,
mid-walk) by posing the armature directly, plus the rest pose. Used for
own-eyes verification per the media proof standard: open every render,
SHA-256 everything, never report "verified" without looking.

usage (inside Blender):
  blender --background ... --python proof.py -- --in MODEL.glb --outdir DIR
      --tag TAG [--res 640]

Poses are defined as bone euler rotations (degrees, XYZ) applied to the
armature in pose mode. The character faces +X (Stick-Up convention); the
camera looks from +X.
"""
import bpy
from mathutils import Vector, Euler
import sys, os, json, hashlib

argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d
IN = opt("--in", None); OUTDIR = opt("--outdir", None); TAG = opt("--tag", "proof")
RES = int(opt("--res", "640"))
assert IN and OUTDIR, "--in/--outdir required"
os.makedirs(OUTDIR, exist_ok=True)

# Poses are given in glTF space (Y-up, character faces +X) and converted to
# Blender space (Z-up) below. AIM points the bone's Y axis at the target dir.
def G2B(v):
    x, y, z = v
    return (x, -z, y)  # glTF Y-up -> Blender Z-up (matches the importer)

POSES = {
    "rest": {},
    "arms_raised": {"aim": {"leftarm": (0, 0.92, 0.39), "rightarm": (0, 0.92, -0.39),
                            "leftforearm": (0, 0.98, 0.2), "rightforearm": (0, 0.98, -0.2)}},
    "crucifix": {"aim": {"leftarm": (0, 0.05, 1), "rightarm": (0, 0.05, -1)}},
    "finger_guns": {"aim": {"rightarm": (1, 0.05, -0.15), "rightforearm": (1, 0, -0.1),
                            "righthand": (1, 0, -0.1)}},
    "walk": {"aim": {"leftupleg": (0.42, -0.9, 0), "rightupleg": (-0.42, -0.9, 0),
                     "leftleg": (0.2, -0.97, 0), "rightleg": (-0.3, -0.95, 0),
                     "leftarm": (-0.2, -0.97, 0), "rightarm": (0.2, -0.97, 0)}},
}

def norm(n):
    import re
    n = re.sub(r"^mixamorig\d*[:_]?", "", n or "", flags=re.I)
    return n.replace(".", "").replace(" ", "").lower()

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
mn = [1e9]*3; mx = [-1e9]*3
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
# Blender space: X = facing, Y = lateral, Z = up
H = mx[2]-mn[2]; cx, cy, cz = (mn[0]+mx[0])/2, (mn[1]+mx[1])/2, (mn[2]+mx[2])/2

# camera at +X looking back down -X, up = +Z
cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam)
bpy.context.scene.collection.objects.link(co)
co.location = (cx + H*1.7, cy, cz)
direction = Vector((cx, cy, cz)) - co.location
co.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = co; cam.lens = 40
sun = bpy.data.lights.new("s", "SUN"); so = bpy.data.objects.new("s", sun)
bpy.context.scene.collection.objects.link(so); sun.energy = 2.5
so.rotation_euler = (0.6, 0.3, 1.2)
fill = bpy.data.lights.new("f", "SUN"); fo = bpy.data.objects.new("f", fill)
bpy.context.scene.collection.objects.link(fo); fill.energy = 0.8
fo.rotation_euler = (0.6, 0.3, -1.2)
bpy.context.scene.render.engine = "BLENDER_EEVEE"
bpy.context.scene.render.resolution_x = RES
bpy.context.scene.render.resolution_y = RES
bpy.context.scene.world = bpy.data.worlds.new("w")
bpy.context.scene.world.use_nodes = False
bpy.context.scene.world.color = (1, 1, 1)

bones = {norm(b.name): b.name for b in arm.pose.bones} if arm else {}

# rest bone directions in armature (Blender) space, from EDIT bones
# (arm.data.bones head/tail are not populated by the glTF importer)
_rest_dir = {}
if arm:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for eb in arm.data.edit_bones:
        _rest_dir[norm(eb.name)] = ((eb.tail - eb.head).normalized(),
                                    eb.matrix.to_quaternion())
    bpy.ops.object.mode_set(mode="OBJECT")

def aim_bone(key, target_gltf):
    """Point the bone's Y axis at target_dir (given in glTF space)."""
    bone_name = bones[key]
    pb = arm.pose.bones[bone_name]
    rest_y, q_rest = _rest_dir[key]
    target = Vector(G2B(target_gltf)).normalized()
    q_align = rest_y.rotation_difference(target)
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = q_rest.inverted() @ q_align @ q_rest

# clay material override (proof renders show deformation, not textures)
clay = bpy.data.materials.new("clay")
clay.use_nodes = True
bsdf = clay.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.72, 0.72, 0.75, 1)
for o in meshes:
    o.data.materials.clear()
    o.data.materials.append(clay)

results = []
for pname, pose in POSES.items():
    if arm:
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="POSE")
        for b in arm.pose.bones:
            b.rotation_mode = "XYZ"
            b.rotation_euler = (0, 0, 0)
        for key, target in pose.get("aim", {}).items():
            if key in bones and key in _rest_dir:
                aim_bone(key, target)
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.update()
    out = os.path.join(OUTDIR, f"{TAG}_{pname}.png")
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()
    results.append({"pose": pname, "file": out, "sha256": h})
    print(f"proof: {pname} -> {out} sha256:{h[:16]}...")
json.dump(results, open(os.path.join(OUTDIR, f"{TAG}_manifest.json"), "w"), indent=1)
