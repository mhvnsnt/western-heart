"""Tobi/Mirko faithful GLB export from mirkoIK.blend (v2).
Key step: the body mesh 'Mirko' carries 3 MASK modifiers + 55 shape keys.
Blender's glTF exporter drops the morphs when applying modifiers, so the
MASKs are baked here first: evaluate the mesh per shape key through the
depsgraph (armature modifier muted -> local bind space), rebuild one mesh
whose shape keys carry the masked geometry. Everything else exports as-is.
Usage: blender -b tobi-mirko.blend --python export_tobi.py -- <mode> <outpath> [bodytex]
"""
import bpy, sys
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
mode, outpath = argv[0], argv[1]
bodytex = argv[2] if len(argv) > 2 else None

img = bpy.data.images.get("Mirko body.png")
if img is not None and bodytex:
    img.filepath = bodytex
    img.reload()
    try:
        img.pack()
    except Exception as e:
        print("PACK-WARN", e)
    print("BODYIMG", img.size[:], "packed:", bool(img.packed_file))

arm = bpy.data.objects["Miruko Rig"]
arm.data.pose_position = 'REST'

# ---------- bake MASK modifiers on the body mesh, preserving shape keys ----
def bake_masked_shapekeys(obj):
    keys = [kb.name for kb in obj.data.shape_keys.key_blocks]
    authored = {kb.name: kb.value for kb in obj.data.shape_keys.key_blocks}
    print("AUTHORED KEY VALUES", {k: v for k, v in authored.items() if v})
    # NOTE: armature modifiers stay ACTIVE. This mesh's local frame is offset
    # from the armature frame (DMX import), so the at-rest armature evaluation
    # is part of its true shape; muting it displaced the surface ~5 cm.
    dg = bpy.context.evaluated_depsgraph_get()

    def evaluate(values):
        for kb in obj.data.shape_keys.key_blocks:
            kb.value = values.get(kb.name, 0.0)
        bpy.context.view_layer.update()
        ev = obj.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(ev)
        arr = np.empty(len(m.vertices) * 3)
        m.vertices.foreach_get("co", arr)
        # to armature/world frame: the rebuilt object will sit at the origin
        mw = np.array(ev.matrix_world)
        pts = arr.reshape(-1, 3)
        pts = pts @ mw[:3, :3].T + mw[:3, 3]
        flat = pts.reshape(-1)
        m.vertices.foreach_set("co", flat)
        # rotate normals into the same frame
        nrm = np.empty(len(m.vertices) * 3)
        m.vertices.foreach_get("normal", nrm)
        n3 = nrm.reshape(-1, 3) @ mw[:3, :3].T
        n3 /= (np.linalg.norm(n3, axis=1, keepdims=True) + 1e-12)
        # vertex normals are derived; split normals live on loops -- the
        # exporter recomputes from geometry when custom normals are absent,
        # so drop loop normals by clearing custom split normals if present
        try:
            if m.has_custom_normals:
                pass
        except Exception:
            pass
        return m, flat

    # Basis = the mesh AS AUTHORED (the blend's own active key mix, e.g.
    # suit-fit/tights-fit at 1.0) -- that mix is part of how she looks.
    basis_mesh, basis_arr = evaluate(dict(authored))
    positions = {keys[0]: basis_arr}
    for kname in keys[1:]:
        if authored.get(kname):
            # already folded into the basis; keep the target as a zero delta
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
    # shape keys onto the baked mesh
    new_data.shape_keys_create() if False else None
    sk = new_data.shape_keys
    if sk is None:
        # add basis via object-level op fallback below
        pass
    new_obj = bpy.data.objects.new(obj.name, new_data)
    bpy.context.collection.objects.link(new_obj)
    # shape keys must be added through the object API
    new_obj.shape_key_add(name=keys[0], from_mix=False)
    for kname in keys[1:]:
        kb = new_obj.shape_key_add(name=kname, from_mix=False)
        co = np.empty(len(kb.data) * 3)
        kb.data.foreach_get("co", co)
        assert len(co) == len(positions[kname]), (kname, len(co), len(positions[kname]))
        kb.data.foreach_set("co", positions[kname])
    # shape_key_add leaves every block at value 1.0 -- restore authored values
    # (otherwise all morphs apply at once and the surface bulges)
    for kb in new_obj.data.shape_keys.key_blocks:
        kb.value = authored.get(kb.name, 0.0)
    # armature modifier; the rebuilt object sits at the origin in armature
    # frame (its evaluated world positions were baked into the geometry)
    mod = new_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm
    new_obj.parent = None
    print("BAKE-MW", [ [round(x,4) for x in row] for row in np.array(obj.matrix_world) ])
    # materials: evaluated mesh already carries the slots
    print("BAKED", obj.name, "verts", len(new_data.vertices), "keys", len(keys))
    return new_obj

body = bpy.data.objects["Mirko"]
new_body = bake_masked_shapekeys(body)
bpy.data.objects.remove(body, do_unlink=True)
new_body.name = "Mirko"

# audit: any ARMATURE modifier with no object assigned (source defect check)
for o in bpy.data.objects:
    if o.type == 'MESH':
        for m in o.modifiers:
            if m.type == 'ARMATURE' and m.object is None:
                print("ARMATURE-NO-OBJECT", o.name, m.name)

RENAME = {
    "hips": "Hips", "spine": "Spine", "spine2": "Spine2", "chest": "Chest", "neck": "Neck",
    "shoulder.L": "LeftShoulder", "upper_arm.L": "LeftArm", "forearm.L": "LeftForeArm", "hand.L": "LeftHand",
    "thigh.L": "LeftUpLeg", "shin.L": "LeftLeg", "foot.L": "LeftFoot", "toe.L": "LeftToeBase",
    "shoulder.R": "RightShoulder", "upper_arm.R": "RightArm", "forearm.R": "RightForeArm", "hand.R": "RightHand",
    "thigh.R": "RightUpLeg", "shin.R": "RightLeg", "foot.R": "RightFoot", "toe.R": "RightToeBase",
}
DROP = ["Bulge", "Penis", "directional", "switch", "up/down", "face_template", "mouth_template"]

if mode == "game":
    for old, new in RENAME.items():
        b = arm.data.bones.get(old)
        if b:
            b.name = new
        else:
            print("RENAME-MISS", old)
    # SOURCE-DEFECT REPAIR (game build only; master keeps the file as authored):
    # the tail's ARMATURE modifier has object=None in the source blend, so the
    # tail can never deform; its weights exist (AC_tail_A + an orphan SFM group
    # 'ValveBiped.Bip01_Pelvis'). Assign the rig and map the orphan group to
    # Hips (the same bone in this rig) so the tail follows the body.
    # NECK-FLUFF MATERIAL (game build only): the blend assigns the neck-fluff
    # mesh NO material (source trait; master keeps it as authored), so in the
    # blend it renders as plain white fluff. The game's material gate blocks
    # any model with an untextured prim. The old shipped conversion put it on
    # the Body texture, which renders the collar skin-toned -- visibly wrong
    # vs the blend. Game-only fix: an authored flat warm-white matching the
    # blend's own rendered collar (passes the gate's authoredFlat test).
    fw = bpy.data.objects.get("neck fluff")
    if fw:
        print("NECKFLUFF slots:", [m.name if m else None for m in fw.data.materials])
        if not any(fw.data.materials):
            nf = bpy.data.materials.new("NeckFluff")
            nf.use_nodes = True
            nf.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.90, 0.88, 0.84, 1.0)
            fw.data.materials.clear()
            fw.data.materials.append(nf)
            print("NECKFLUFF-REPAIR authored flat warm-white assigned (game-only)")
    tail = bpy.data.objects.get("tail")
    if tail:
        for m in tail.modifiers:
            if m.type == 'ARMATURE' and m.object is None:
                m.object = arm
                print("TAIL-REPAIR assigned armature object")
        vg = tail.vertex_groups.get("ValveBiped.Bip01_Pelvis")
        if vg:
            vg.name = "Hips"
            print("TAIL-REPAIR orphan group -> Hips")
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
