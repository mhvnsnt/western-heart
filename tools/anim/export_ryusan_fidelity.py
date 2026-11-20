"""Ryusan/Mina Ashido faithful GLB export from 'Mina Ashido rigify.blend'.
Follows the Tobi (#1570) / Pond (#1571) / Chatur (#1572) pattern, adapted:

- The skinning rig is the 'Mina Ashido' armature (520 bones, 169 deform:
  Rigify DEF- body + a GZM-style face rig). Every character mesh's
  ARMATURE modifier points at it. The 65-bone 'backup-metarig' armature
  skins NOTHING (no modifier references it) -- it is not the skinning
  rig (the Chatur RahkasaRIG_Deform lesson).
- Character meshes: Mina (20,719v, 63 key blocks = basis 'base' + 62
  keys, ARMATURE + MASK('SuitHide', inverted)), boots, Fur (hide_render
  only -- visible as the blend opens), Hair, Horns (1 key), jacket,
  suit (1 key), Penis (author-hidden, 7 keys, master only).
  Total non-basis shape keys in the blend: 62 + 1 + 1 + 7 = 71.
- Mina's shape keys are DRIVEN (31 driver fcurves from the face-rig
  bones) and her one authored nonzero key (NipplesFlat 1.0) is driven
  too. The drivers are a Blender-side control rig with no glTF
  representation, so the export copy strips them AFTER capturing the
  authored (rest-evaluated) values; the blend keeps them untouched.
- Mina's MASK and suit's authored mix (suit 'nipples flat' 1.0) are
  baked through the depsgraph per shape key with the armature ACTIVE
  (Tobi method): basis = evaluated(authored mix); a key authored
  nonzero folds into the basis (its target equals the basis); every
  other key's target = evaluated(authored + that key at 1.0).
- FLOOR LIFT: the evaluated character soles sit at z = -0.0473 in the
  blend; the armature object is lifted +0.0473 so soles export at
  y = 0 (Pond method). Scale is applied AFTER export by
  tools/anim/scale_glb.mjs to the shipped model's 1.992 m total
  height (blend character 6.3670 -> x0.312836).
- REST export: both armatures' pose bones are all at rest already
  (0 nonzero, dump-verified); pose_position is set to REST anyway.

Usage: blender -b ryusan-mina.blend --python export_ryusan_fidelity.py -- <mode> <outpath>
  mode = master (blend as authored: original names, all objects/bones)
       | game   (FULL 520-bone rig, canonical core renames,
                 Penis/templates/widgets/backup-metarig dropped)
       | test   (like game but no renames/drops)

NOTE on the skin: a deform-bones-only export was measured and REJECTED
for this rig. Rigify parents its DEF- bones to ORG- control bones, and
Blender's deform-only path re-roots every ORG-parented deform bone at
the skin root -- arms and legs end up disconnected from the spine, and
the engine's rig analysis (t3anims.js analyzeRig: chest = lowest
common ancestor of the two arms) then refuses the bank outright
('lacks core humanoid bones', play-probe all-TPOSE). The full-rig
export keeps the authored hierarchy exactly, as Pond (224 bones) and
Tobi (254 bones) shipped; all 169 deform bones ride in it.
"""
import bpy, sys, os
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
mode, outpath = argv[0], argv[1]

rig = bpy.data.objects["Mina Ashido"]
rig.data.pose_position = 'REST'
meta = bpy.data.objects.get("backup-metarig")
if meta:
    meta.data.pose_position = 'REST'
bpy.context.view_layer.update()

print("EXPORTER deform-only param (export_def_bones):",
      'export_def_bones' in bpy.ops.export_scene.gltf.get_rna_type().properties)

# ---------- floor lift: soles -> z=0 (measured, see header) ----------
FLOOR_LIFT = 0.0473
rig.location.z += FLOOR_LIFT
bpy.context.view_layer.update()
print("FLOOR-LIFT armature z ->", rig.location.z)

# ---------- capture authored key values, then strip shape-key drivers --
def authored_values(obj):
    if not obj.data.shape_keys:
        return {}
    return {kb.name: kb.value for kb in obj.data.shape_keys.key_blocks}

AUTHORED = {}
for name in ("Mina", "suit", "Horns", "Penis"):
    o = bpy.data.objects.get(name)
    if o:
        AUTHORED[name] = authored_values(o)
        print("AUTHORED", name, {k: v for k, v in AUTHORED[name].items() if v})

for name in ("Mina", "suit", "Horns", "Penis"):
    o = bpy.data.objects.get(name)
    if not o or not o.data.shape_keys:
        continue
    sk = o.data.shape_keys
    if sk.animation_data and sk.animation_data.drivers:
        paths = [(d.data_path, d.array_index) for d in sk.animation_data.drivers]
        for path, idx in paths:
            try:
                sk.driver_remove(path, idx)
            except Exception as e:
                print("DRIVER-REMOVE-FAIL", name, path, idx, e)
        left = len(sk.animation_data.drivers) if sk.animation_data else 0
        print("DRIVERS STRIPPED", name, len(paths), "remaining", left)

# ---------- bake a mesh through the depsgraph, preserving shape keys ---
def bake_shapekeys(obj):
    keys = [kb.name for kb in obj.data.shape_keys.key_blocks]
    authored = AUTHORED[obj.name]
    dg = bpy.context.evaluated_depsgraph_get()

    def evaluate(values):
        for kb in obj.data.shape_keys.key_blocks:
            kb.value = values.get(kb.name, 0.0)
        bpy.context.view_layer.update()
        ev = obj.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(ev)
        arr = np.empty(len(m.vertices) * 3)
        m.vertices.foreach_get("co", arr)
        mw = np.array(ev.matrix_world)
        pts = arr.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        return m, pts.reshape(-1)

    basis_mesh, basis_arr = evaluate(dict(authored))
    positions = {keys[0]: basis_arr}
    for kname in keys[1:]:
        if abs(authored.get(kname, 0.0)) > 1e-4:
            positions[kname] = basis_arr
            print("KEY FOLDED INTO BASIS", obj.name, kname)
            continue
        mix = dict(authored); mix[kname] = 1.0
        m, arr = evaluate(mix)
        positions[kname] = arr
        bpy.data.meshes.remove(m)
    counts = {len(v) // 3 for v in positions.values()}
    assert len(counts) == 1, f"vertex count varies across keys: {counts}"
    new_data = basis_mesh
    new_data.name = obj.data.name
    new_obj = bpy.data.objects.new(obj.name, new_data)
    bpy.context.collection.objects.link(new_obj)
    new_obj.shape_key_add(name=keys[0], from_mix=False)
    for kname in keys[1:]:
        kb = new_obj.shape_key_add(name=kname, from_mix=False)
        co = np.empty(len(kb.data) * 3)
        kb.data.foreach_get("co", co)
        assert len(co) == len(positions[kname]), (kname, len(co), len(positions[kname]))
        kb.data.foreach_set("co", positions[kname])
    # shape_key_add leaves every block at value 1.0 -- restore authored values
    for kb in new_obj.data.shape_keys.key_blocks:
        kb.value = authored.get(kb.name, 0.0)
    mod = new_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = rig
    new_obj.parent = None
    print("BAKED", obj.name, "verts", len(new_data.vertices), "keys", len(keys),
          "vgroups", len(new_obj.vertex_groups))
    return new_obj

for mesh_name in ("Mina", "suit"):
    old = bpy.data.objects[mesh_name]
    new = bake_shapekeys(old)
    bpy.data.objects.remove(old, do_unlink=True)
    new.name = mesh_name

# audit: any ARMATURE modifier with no object assigned (source defect check)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for m in o.modifiers:
            if m.type == 'ARMATURE' and m.object is None:
                print("ARMATURE-NO-OBJECT", o.name, m.name)

# ---------- game-mode prep ----------
# Canonical core renames (Tobi/Pond/Chatur deviation 1): the runtime
# retargeter (game/js/t3anims.js canonBoneName) matches no Blender-style
# names. Rigify chain: DEF-spine is the pelvis root (DEF-pelvis.L/R hang
# off it), .001/.002 the spine slerp, .003 the chest (shoulders hang in
# its span), .004 a short neck-slerp helper (keeps its name, rides at
# rest like Pond's Elbow/Knee helpers), .005 the neck, .006 the head
# (the whole face rig hangs off it). Segment bones (.001 on arms/legs)
# keep their names and ride at rest.
RENAME = {
    "DEF-spine": "Hips", "DEF-spine.001": "Spine", "DEF-spine.002": "Spine1",
    "DEF-spine.003": "Chest", "DEF-spine.005": "Neck", "DEF-spine.006": "Head",
    "DEF-shoulder.L": "LeftShoulder", "DEF-upper_arm.L": "LeftArm",
    "DEF-forearm.L": "LeftForeArm", "DEF-hand.L": "LeftHand",
    "DEF-shoulder.R": "RightShoulder", "DEF-upper_arm.R": "RightArm",
    "DEF-forearm.R": "RightForeArm", "DEF-hand.R": "RightHand",
    "DEF-thigh.L": "LeftUpLeg", "DEF-shin.L": "LeftLeg",
    "DEF-foot.L": "LeftFoot", "DEF-toe.L": "LeftToeBase",
    "DEF-thigh.R": "RightUpLeg", "DEF-shin.R": "RightLeg",
    "DEF-foot.R": "RightFoot", "DEF-toe.R": "RightToeBase",
}
# Author-hidden Penis (hide_viewport + hide_render in the blend; Pond
# #1552 precedent), non-character template helpers, the non-skinning
# backup metarig and the zero-polygon WGT widgets -- game file only;
# the master keeps every object as authored.
DROP_EXACT = ["Penis", "directional", "switch", "up/down",
              "face_template", "mouth_template", "backup-metarig"]

if mode == "game":
    for old, new in RENAME.items():
        b = rig.data.bones.get(old)
        if b:
            b.name = new
        else:
            print("RENAME-MISS", old)
    for name in DROP_EXACT:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.data.objects):
        if o.name.startswith("WGT"):
            bpy.data.objects.remove(o, do_unlink=True)
    print("GAME-PREP done")

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
kwargs["export_leaf_bone"] = False
bpy.ops.export_scene.gltf(**kwargs)
print("EXPORTED", mode, outpath)
