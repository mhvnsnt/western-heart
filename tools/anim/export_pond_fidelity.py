"""Pond/Tsuyu faithful GLB export from 'Tsuyu Asui IK.blend' (v1).
Follows the Tobi pattern (tools/anim/export_tobi_fidelity.py, PR #1570):
- The body mesh 'tsuyu' (67 shape keys) and the 'suit' mesh (10 shape keys)
  carry MASK modifiers, which Blender's glTF exporter cannot apply together
  with morphs, so the MASKs are baked here first: evaluate each mesh per
  shape key through the depsgraph (armature modifier kept ACTIVE, exactly
  as in the Tobi bake), rebuild one mesh whose shape keys carry the masked
  geometry.
- The blend's floor is NOT the armature origin: her boot soles sit at
  z = -0.1869 (measured over the evaluated character meshes; the footTip
  helper bones corroborate, heads at z ~ -0.11). The shipped game model
  stands with soles at y=0, so the armature object is lifted by +0.1869
  before anything is evaluated/exported, putting soles on z=0.
- Authored shape-key values in this blend are ALL zero (verified by dump),
  so the basis is the plain basis; the value-reset step is still applied
  after shape_key_add (it defaults every block to 1.0).
Usage: blender -b pond-tsuyu.blend --python export_pond_fidelity.py -- <mode> <outpath>
  mode = master (blend exactly: original bone names, every object)
       | game   (canonical core-bone renames + non-character helpers and
                 author-hidden Bulge/Penis dropped; master keeps them)
"""
import bpy, sys
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
mode, outpath = argv[0], argv[1]

arm = bpy.data.objects["tsuyu rig"]
arm.data.pose_position = 'REST'

# ---------- floor lift: soles -> z=0 (measured, see header) ----
FLOOR_LIFT = 0.1869
arm.location.z += FLOOR_LIFT
bpy.context.view_layer.update()
print("FLOOR-LIFT armature z ->", arm.location.z)

# ---------- bake MASK modifiers on a mesh, preserving shape keys ----
def bake_masked_shapekeys(obj):
    keys = [kb.name for kb in obj.data.shape_keys.key_blocks]
    authored = {kb.name: kb.value for kb in obj.data.shape_keys.key_blocks}
    print("AUTHORED KEY VALUES", obj.name, {k: v for k, v in authored.items() if v})
    # NOTE: armature modifiers stay ACTIVE (Tobi method note: the at-rest
    # armature evaluation is part of a DMX mesh's true shape).
    dg = bpy.context.evaluated_depsgraph_get()

    def evaluate(values):
        for kb in obj.data.shape_keys.key_blocks:
            kb.value = values.get(kb.name, 0.0)
        bpy.context.view_layer.update()
        ev = obj.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(ev)
        arr = np.empty(len(m.vertices) * 3)
        m.vertices.foreach_get("co", arr)
        # to world frame: the rebuilt object will sit at the origin
        mw = np.array(ev.matrix_world)
        pts = arr.reshape(-1, 3)
        pts = pts @ mw[:3, :3].T + mw[:3, 3]
        flat = pts.reshape(-1)
        m.vertices.foreach_set("co", flat)
        return m, flat

    basis_mesh, basis_arr = evaluate(dict(authored))
    positions = {keys[0]: basis_arr}
    for kname in keys[1:]:
        if authored.get(kname):
            positions[kname] = basis_arr
            print("KEY FOLDED INTO BASIS", kname)
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
    mod.object = arm
    new_obj.parent = None
    print("BAKED", obj.name, "verts", len(new_data.vertices), "keys", len(keys))
    return new_obj

for mesh_name in ("tsuyu", "suit"):
    body = bpy.data.objects[mesh_name]
    new_body = bake_masked_shapekeys(body)
    bpy.data.objects.remove(body, do_unlink=True)
    new_body.name = mesh_name

# audit: any ARMATURE modifier with no object assigned (source defect check)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for m in o.modifiers:
            if m.type == 'ARMATURE' and m.object is None:
                print("ARMATURE-NO-OBJECT", o.name, m.name)

# Game-mode core-bone renames: the runtime retargeter
# (game/js/t3anims.js canonBoneName) matches NO Blender-style names, so
# without these the model gets no bank animation at all (Tobi deviation 1).
# Pond's chain: spine is the pelvis bone (thighs/pelvis hang off it),
# spine.001/.002 the spine slerp chain, spine.003 the chest (shoulders
# hang off it), spine.004 neck, spine.005 head (Face hangs off it).
# Elbow.L/R and Knee.L/R are short in-chain helper bones; they keep their
# names and ride at rest local rotation, exactly like twist bones on
# other fighters (assets.js MB-Lab remap note).
RENAME = {
    "spine": "Hips", "spine.001": "Spine", "spine.002": "Spine1",
    "spine.003": "Chest", "spine.004": "Neck", "spine.005": "Head",
    "shoulder.L": "LeftShoulder", "upper_arm.L": "LeftArm",
    "forearm.L": "LeftForeArm", "hand.L": "LeftHand",
    "shoulder.R": "RightShoulder", "upper_arm.R": "RightArm",
    "forearm.R": "RightForeArm", "hand.R": "RightHand",
    "thigh.L": "LeftUpLeg", "shin.L": "LeftLeg", "foot.L": "LeftFoot", "toe.L": "LeftToeBase",
    "thigh.R": "RightUpLeg", "shin.R": "RightLeg", "foot.R": "RightFoot", "toe.R": "RightToeBase",
}
# Non-character helpers + author-hidden meshes (game file only; the
# master keeps every object exactly as authored). Bulge + Penis are
# hide_viewport + hide_render IN THE BLEND ITSELF (dump-verified), and
# PR #1552 already removed them on that basis (owner-approved precedent).
DROP = ["Bulge", "Penis",
        "directional", "switch", "up/down", "face_template", "mouth_template",
        "WGT-tsuyu rig_ArmIK.L", "WGT-tsuyu rig_ArmIK.R",
        "WGT-tsuyu rig_thigh.L.001", "WGT-tsuyu rig_thigh.R.001"]

if mode == "game":
    for old, new in RENAME.items():
        b = arm.data.bones.get(old)
        if b:
            b.name = new
        else:
            print("RENAME-MISS", old)
    for name in DROP:
        o = bpy.data.objects.get(name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    print("GAME-PREP done")

bpy.ops.export_scene.gltf(
    filepath=outpath,
    export_format='GLB',
    export_apply=False,         # masks already baked; armature must stay live
    export_skins=True,
    export_morph=True,
    export_morph_normal=True,
    export_animations=False,
    export_rest_position_armature=True,
    export_image_format='AUTO',
)
print("EXPORTED", mode, outpath)
