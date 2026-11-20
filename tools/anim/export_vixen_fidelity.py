"""Menajerii (Vixen) fidelity rebuild export — SmutBase 6 fidelity order,
lane 6 (LAST; after Tobi #1570, Pond #1571, Chatur #1572, Ryusan #1574,
Megami #1576).

Source of truth: the recovered commission blend VixenCommission.blend
(byte-identical to the lost original; recovery WH #1575). Owner bar: the
fighter must look EXACTLY like the blend opened in Blender, with the FULL
rig from her own file, all textures, all shape keys accounted for.

Method mirrors tools/anim/export_megami_fidelity.py (same DAZ/GZM rig
family): pose_position = REST for export (the authored pose lives in the
blend; the game binds its banks at rest). Shape keys here are ALL
driver-driven; the export measures the EVALUATED value of every key on
every mesh after a depsgraph update and reports any nonzero (the authored
look is whatever those evaluate to; on Parvati all evaluated 0 = Basis).
Drivers are stripped in the export copy after capture, per the Ryusan /
Megami pattern.

Rig repairs in the export copy (bind-neutral, verified in TEST mode A/B
by diffing joint worlds REPAIR=0 vs REPAIR=1): the DAZ/GZM rig hangs the
arm assemblies off 'hip' via arm_parent.L/R and the leg assemblies off
'hip' via leg_parent.L/R, and drives them in Blender from sockets
(arm_parent COPY_TRANSFORMS armSocket, whose parent is clavicle;
leg_parent COPY_TRANSFORMS legSocket, whose parent is pelvis). glTF
carries no constraints, so without repair the bank-driven Chest would
not carry the arms and analyzeRig's chest (LCA of the arms) would
collapse onto Hips. Repairs make the exported hierarchy match the rig's
own constraint intent:
  arm_parent.L/R   -> parent armSocket.L/R   (was: hip)
  leg_parent.L/R   -> parent legSocket.L/R   (was: hip)
  upper_arm.bend.L/R -> parent upper_arm.L/R (was: arm_parent.L/R; the
                        bend/twist deformers carry the arm skin weights
                        and must ride the driven arm chain, exactly as
                        forearm.bend already rides forearm.L)
  thigh.bend.L/R   -> parent thigh.L/R       (was: leg_parent.L/R; same
                        reasoning, as shin.bend already rides shin.L)
Bone rest positions are armature-space absolute in Blender, so
reparenting changes only pose inheritance, never the bind. TEST mode
exports with REPAIR=0 and REPAIR=1 and the caller diffs joint worlds.

Game mode additionally renames 23 core bones to the engine's canonical
names (the Roger bank binds through the same canonical chain the shipped
template used: Hips/Spine/Spine1/Spine2/Chest/Neck/Head). The Chest
rename goes on DEF-chest-1: it is the lowest common ancestor of the two
arm chains once arm_parent hangs off the sockets, which is exactly the
bone analyzeRig appoints as the Chest driver.

Usage:
  blender -b VixenCommission.blend --python export_vixen_fidelity.py -- \
      MODE OUT.glb [REPAIR=0|1]
  MODE = master | game | test   (test = game pipeline to a scratch path)
Env: VIXEN_IMG_FMT (AUTO|NONE), VIXEN_MORPH (1|0)
"""
import bpy
import json
import sys
import os

argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0]
OUT = argv[1]
REPAIR = int(argv[2]) if len(argv) > 2 else 1
IMG_FMT = os.environ.get("VIXEN_IMG_FMT", "AUTO")
DO_MORPH = os.environ.get("VIXEN_MORPH", "1") == "1"

RIG = "Vixen"

RENAMES = {
    "hip": "Hips",
    "DEF-spine": "Spine",
    "DEF-spine-1": "Spine1",
    "DEF-chest": "Spine2",
    "DEF-chest-1": "Chest",
    "neck": "Neck",
    "head": "Head",
    "clavicle.L": "LeftShoulder", "clavicle.R": "RightShoulder",
    "upper_arm.L": "LeftArm", "upper_arm.R": "RightArm",
    "forearm.L": "LeftForeArm", "forearm.R": "RightForeArm",
    "hand.L": "LeftHand", "hand.R": "RightHand",
    "thigh.L": "LeftUpLeg", "thigh.R": "RightUpLeg",
    "shin.L": "LeftLeg", "shin.R": "RightLeg",
    "foot.L": "LeftFoot", "foot.R": "RightFoot",
    "toe.L": "LeftToeBase", "toe.R": "RightToeBase",
}

REPARENTS = {
    "arm_parent.L": "armSocket.L",
    "arm_parent.R": "armSocket.R",
    "leg_parent.L": "legSocket.L",
    "leg_parent.R": "legSocket.R",
    "upper_arm.bend.L": "upper_arm.L",
    "upper_arm.bend.R": "upper_arm.R",
    "thigh.bend.L": "thigh.L",
    "thigh.bend.R": "thigh.R",
}

# Game-file drops: 0-poly GZM rig widgets + the hide_render floor plane.
GAME_DROP_PREFIX = "GZM_"
GAME_DROP_EXACT = {"Plane"}

# Author-hidden wardrobe: the blend's ONLY view layer excludes the
# collections Public Hair, Lingerie 1, Lingerie 2, Lingerie 3 and BDSM
# (plus the Hidden collection of GZM widgets) from viewport AND render —
# the author's alternate garments, toggled off in the saved file. Opened
# and rendered as saved, she wears only the 'Original' collection outfit
# (Arms, Necklace, Suit, Boots) + Hair + the Vixen Mesh body. Shipping
# the excluded pieces would stack five outfits on her at once. Per the
# Pond #1552 / Megami #1576 author-hidden precedent they leave the GAME
# file and stay in the MASTER. (Verified by direct view-layer inspection
# of the source: layer_collection.exclude flags in the lane inspect JSON.)
GAME_DROP_EXACT |= {
    "Full", "Triangle", "Stripe",                       # Public Hair
    "Bra", "Pantie", "Stocking (2)", "Heels",           # Lingerie 1
    "Body Suit", "High Heels",                          # Lingerie 2
    "Belt", "Bra (2)", "Pantie 3", "Stocking",          # Lingerie 3
    "Glove R", "Glove L", "Choker", "Heel L", "Heel R",  # Lingerie 3
    "BDSM harness", "BDSM harness neck ring",           # BDSM
    "BDSM Thigh Harness", "Gloves",                     # BDSM
}

report = {"mode": MODE, "repair": REPAIR}

rig = bpy.data.objects[RIG]
assert rig and rig.type == "ARMATURE", "armature not found"

# ---------------------------------------------------------------- floor
# Evaluated per-mesh z-minimum at REST with the armature ACTIVE (Pond /
# Megami method). The character's floor is her footwear/body sole,
# measured over the authored-look (game-kept) meshes only; excluded
# garments (heels etc.) never float her feet.
rig.data.pose_position = "REST"
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="OBJECT")
dg = bpy.context.evaluated_depsgraph_get()
sole = None
per_mesh_min = {}
import array
for ob in bpy.context.scene.objects:
    if ob.type != "MESH" or ob.hide_render:
        continue
    if ob.name.startswith(GAME_DROP_PREFIX) or ob.name in GAME_DROP_EXACT:
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    if len(me.vertices) == 0:
        ev.to_mesh_clear()
        continue
    zs = array.array("f", [0.0]) * (3 * len(me.vertices))
    me.vertices.foreach_get("co", zs)
    zmin = min(zs[2::3])
    per_mesh_min[ob.name] = round(zmin, 4)
    ev.to_mesh_clear()
    sole = zmin if sole is None else min(sole, zmin)
report["per_mesh_zmin"] = per_mesh_min
report["sole_z"] = sole
lift = -sole
print("FLOOR sole_z", sole, "lift", lift)

# Apply the lift to every root object so the whole scene (and the
# armature-parented meshes riding it) moves together. Placement only.
for ob in bpy.context.scene.objects:
    if ob.parent is None:
        ob.location.z += lift
report["floor_lift"] = lift

# ------------------------------------------------------- evaluated keys
# ONE depsgraph update already happened above via evaluated_get; read the
# evaluated values off EVERY evaluated mesh that carries shape keys.
key_report = {}
nonzero_total = {}
for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    if not ob.data.shape_keys:
        continue
    ev_ob = ob.evaluated_get(dg)
    sk = ev_ob.data.shape_keys
    evals = {kb.name: kb.value for kb in sk.key_blocks}
    nz = {k: v for k, v in evals.items() if abs(v) > 1e-6 and k != "Basis"}
    key_report[ob.name] = {"blocks": len(evals), "nonzero": nz}
    if nz:
        nonzero_total[ob.name] = nz
report["shape_keys_evaluated"] = key_report
report["shape_keys_nonzero_evaluated"] = nonzero_total
print("EVALKEYS meshes", len(key_report), "meshes-with-nonzero", len(nonzero_total))
for k, v in nonzero_total.items():
    print("  NONZERO", k, v)

# Strip shape-key drivers in the export copy (values already captured;
# per the measurements above this changes nothing they evaluate to —
# Ryusan / Megami pattern).
stripped = 0
for mesh in bpy.data.meshes:
    if mesh.shape_keys and mesh.shape_keys.animation_data:
        for drv in list(mesh.shape_keys.animation_data.drivers):
            mesh.shape_keys.animation_data.drivers.remove(drv)
            stripped += 1
report["drivers_stripped"] = stripped

# ------------------------------------------------- dead armature modifiers
# Source defect (also on Parvati / Ryusan): ARMATURE modifiers whose
# object is None do nothing in Blender. Remove the dead entries in the
# export copy so the exporter sees the one live modifier.
dead_removed = {}
for ob in bpy.context.scene.objects:
    if ob.type != "MESH":
        continue
    for mod in list(ob.modifiers):
        if mod.type == "ARMATURE" and mod.object is None:
            ob.modifiers.remove(mod)
            dead_removed[ob.name] = dead_removed.get(ob.name, 0) + 1
report["dead_armature_modifiers_removed"] = dead_removed
print("DEADMODS", dead_removed)

# ------------------------------------------------------------ rig repairs
if REPAIR:
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = rig.data.edit_bones
    for child, parent in REPARENTS.items():
        eb[child].parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    report["reparents"] = REPARENTS
    print("REPARENTS applied", REPARENTS)

# ---------------------------------------------------------------- drops
if MODE in ("game", "test"):
    dropped = []
    for ob in list(bpy.context.scene.objects):
        if ob.type == "MESH" and (ob.name.startswith(GAME_DROP_PREFIX)
                                  or ob.name in GAME_DROP_EXACT):
            dropped.append(ob.name)
            bpy.data.objects.remove(ob, do_unlink=True)
    report["dropped_objects"] = dropped
    print("DROPPED", len(dropped))

# -------------------------------------------------------------- renames
if MODE in ("game", "test"):
    for old, new in RENAMES.items():
        rig.data.bones[old].name = new
    report["renames"] = RENAMES
    print("RENAMES applied", len(RENAMES))

# ---------------------------------------------------------------- export
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    export_apply=False,
    export_skins=True,
    export_morph=DO_MORPH,
    export_morph_normal=True,
    export_animations=False,
    export_rest_position_armature=True,
    export_image_format=IMG_FMT,
    export_leaf_bone=False,
)
report["out"] = OUT
json.dump(report, open(OUT + ".report.json", "w"), indent=1)
print("EXPORT_DONE", MODE, OUT)
