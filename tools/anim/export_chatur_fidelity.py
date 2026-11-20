"""Chatur/Rahkasa faithful GLB export from 'RahkasaV1.1.blend'.
Follows the Tobi (#1570) / Pond (#1571) pattern, adapted to this blend:

- The character meshes (RahkasaBody 29,489v / 99 key blocks, RahkasaHair
  10,185v) are skinned to RahkasaRIG (983 bones, 263 deform). The blend
  also carries RahkasaRIG_Deform (133 bones) — a SEPARATE single-armed
  skeleton whose arm bones sit at averaged positions between the RIG's
  two arm chains; no mesh references it as a modifier target, so it is
  NOT the skinning rig and is never exported as one.
- FOUR ARMS: the RIG's deform set carries two full arm chains per side
  (DEF-upper_arm.L/.001 + DEF-forearm.L/.001 + DEF-hand.L at shoulder
  height, and DEF-upper_arm.L.002/.003 + DEF-forearm.L.002/.003 +
  DEF-hand.L.001 at waist height, with .001-suffixed palm/finger sets).
  The game export keeps the full 263-bone deform set (export_deform_
  bones_only), so both chains survive.
- The body carries an AUTHORED shape-key mix (13 keys nonzero:
  HipsThiccness 1.0, BreastsLarge 2.5, No Nipples 1.0, ...). If the
  exporter writes glTF mesh.weights (test mode checks), the mix rides
  as default morph weights and nothing is folded. Otherwise the mix is
  folded into the basis via a depsgraph bake (Tobi method) so the
  exported model renders as the blend opens.
- No MASK modifiers exist on either character mesh, so no mask bake.
- REST export: RahkasaRIG carries an authored flex pose (61 pose
  bones); pose_position is set to REST for both armatures (Pond/Tobi
  precedent — the pose lives in the blend, the bind is the export).

Usage: blender -b chatur-rahkasa.blend --python export_chatur_fidelity.py -- <mode> <outpath>
  mode = master (blend as authored: original names, all objects/bones)
       | game   (deform-bones-only skin, canonical core renames,
                 scene/widget/prop objects dropped)
       | test   (like game but no renames/drops except deform-only)
"""
import bpy, sys, json
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
mode, outpath = argv[0], argv[1]

rig = bpy.data.objects["RahkasaRIG"]
rig.data.pose_position = 'REST'
dfm = bpy.data.objects.get("RahkasaRIG_Deform")
if dfm:
    dfm.data.pose_position = 'REST'
bpy.context.view_layer.update()

print("EXPORTER deform-only param (export_def_bones):",
      'export_def_bones' in bpy.ops.export_scene.gltf.get_rna_type().properties)

# ---------- authored shape-key mix on the body ----------
body = bpy.data.objects["RahkasaBody"]
authored = {}
if body.data.shape_keys:
    authored = {kb.name: kb.value for kb in body.data.shape_keys.key_blocks}
    print("AUTHORED MIX (nonzero):", {k: v for k, v in authored.items() if v})

# ---------- material node audit (why did the Nipples pair drop?) ----------
mat = bpy.data.materials.get("Rahkasa_Body")
if mat and mat.use_nodes:
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            links = [l.to_node.name + "." + l.to_socket.name for out in n.outputs for l in out.links]
            print("BODYMAT TEX", n.image.name if n.image else None, "-> linked to:", links)

# ---------- reparent body -> RAHKASA_RIG in EVERY mode ----------
# The body is object-parented to RahkasaRIG_Deform, and the glTF
# exporter skins an object to its PARENT armature when parented --
# the test export put the body on the 134-joint Deform skin and would
# have amputated the waist arm pair + face weights (the modifier, and
# the vertex groups, belong to RahkasaRIG). Both armatures share the
# same object transform, so the reparent is visually a no-op.
if body.parent is not rig:
    before = np.array(body.matrix_world)
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    after = np.array(body.matrix_world)
    print("BODY REPARENT (pre-fold) max world delta:", float(np.abs(before - after).max()))

# ---------- optional fold of the authored mix into the basis ----------
# REQUIRED for the final exports: the test export proved the exporter
# writes glTF mesh.weights as all-zero, so without the fold the game
# would render the raw Basis shape instead of the authored look.
import os
if os.environ.get("CHATUR_FOLD") == "1":
    keys = [kb.name for kb in body.data.shape_keys.key_blocks]
    dg = bpy.context.evaluated_depsgraph_get()
    rig_inv = np.linalg.inv(np.array(rig.matrix_world))

    def evaluate(values):
        for kb in body.data.shape_keys.key_blocks:
            kb.value = values.get(kb.name, 0.0)
        bpy.context.view_layer.update()
        ev = body.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(ev)
        arr = np.empty(len(m.vertices) * 3)
        m.vertices.foreach_get("co", arr)
        mw = np.array(ev.matrix_world)
        pts = arr.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        # world -> RIG space (the rebuilt object is parented to the rig)
        pts = pts @ rig_inv[:3, :3].T + rig_inv[:3, 3]
        bpy.data.meshes.remove(m)
        return pts.reshape(-1)

    basis_arr = evaluate(dict(authored))
    positions = {keys[0]: basis_arr}
    for kname in keys[1:]:
        if authored.get(kname):
            positions[kname] = basis_arr
            print("KEY FOLDED INTO BASIS", kname)
            continue
        mix = dict(authored); mix[kname] = 1.0
        positions[kname] = evaluate(mix)
    counts = {len(v) // 3 for v in positions.values()}
    assert len(counts) == 1, f"vertex count varies across keys: {counts}"
    # rebuild: clone the body data so groups/materials/uv survive, swap positions
    new_data = body.data.copy()
    new_data.name = body.data.name
    flat = positions[keys[0]]
    new_data.vertices.foreach_set("co", flat)
    if new_data.shape_keys:
        for kb in new_data.shape_keys.key_blocks:
            kb.data.foreach_set("co", positions[kb.name])
            kb.value = authored.get(kb.name, 0.0)
    new_obj = bpy.data.objects.new(body.name, new_data)
    bpy.context.collection.objects.link(new_obj)
    new_obj.parent = rig
    mod = new_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = rig
    bpy.data.objects.remove(body, do_unlink=True)
    body = new_obj
    print("FOLD-BAKED body verts", len(new_data.vertices), "keys", len(keys))

# ---------- game-mode prep ----------
# Canonical core renames (Tobi/Pond deviation 1): the runtime retargeter
# (game/js/t3anims.js canonBoneName) matches no Blender-style names; the
# T3 stance gate needs Hips/RightArm/Head. The waist arm pair has NO
# canonical names in the engine — it keeps its source names and holds
# rest (Chatur is pose-only; no bank exists for True Ogre).
RENAME = {
    "DEF-spine": "Hips", "DEF-spine.001": "Spine", "DEF-spine.002": "Spine1",
    "DEF-spine.003": "Chest", "DEF-neck": "Neck", "DEF-head": "Head",
    "DEF-shoulder.L": "LeftShoulder", "DEF-upper_arm.L": "LeftArm",
    "DEF-forearm.L": "LeftForeArm", "DEF-hand.L": "LeftHand",
    "DEF-shoulder.R": "RightShoulder", "DEF-upper_arm.R": "RightArm",
    "DEF-forearm.R": "RightForeArm", "DEF-hand.R": "RightHand",
    "DEF-thigh.L": "LeftUpLeg", "DEF-shin.L": "LeftLeg",
    "DEF-foot.L": "LeftFoot", "DEF-toe.L": "LeftToeBase",
    "DEF-thigh.R": "RightUpLeg", "DEF-shin.R": "RightLeg",
    "DEF-foot.R": "RightFoot", "DEF-toe.R": "RightToeBase",
}
# Scene dressing, control-rig widgets and the unskinned spare-parts
# sheet (game file only; the master keeps every object as authored).
DROP_EXACT = ["Floor", "godrays", "NSFWNipples", "RahkasaRIG_Deform"]

if mode == "game":
    for old, new in RENAME.items():
        b = rig.data.bones.get(old)
        if b:
            b.name = new
        else:
            print("RENAME-MISS", old)
    # reparent the body from RahkasaRIG_Deform to RahkasaRIG, world kept
    if body.parent is not rig:
        before = np.array(body.matrix_world)
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        after = np.array(body.matrix_world)
        print("BODY REPARENT max world delta:", float(np.abs(before - after).max()))
    for name in DROP_EXACT:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.data.objects):
        if o.name.startswith("WGT-"):
            bpy.data.objects.remove(o, do_unlink=True)
    # the body was parented to the dropped Deform armature: reparent to rig
    if body.parent is None:
        body.parent = rig
    hair = bpy.data.objects.get("RahkasaHair")
    print("GAME-PREP done; body parent:", body.parent.name if body.parent else None,
          "| hair parent:", hair.parent.name if hair and hair.parent else None)

kwargs = dict(
    filepath=outpath,
    export_format='GLB',
    export_apply=False,
    export_skins=True,
    export_morph=True,
    export_morph_normal=True,
    export_animations=False,
    export_rest_position_armature=True,
    export_image_format='AUTO',
)
if mode in ("game", "test"):
    kwargs["export_def_bones"] = True
if mode in ("game", "test", "master"):
    kwargs["export_leaf_bone"] = False
bpy.ops.export_scene.gltf(**kwargs)
print("EXPORTED", mode, outpath)
