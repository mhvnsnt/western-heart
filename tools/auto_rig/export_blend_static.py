"""tools/auto_rig/export_blend_static.py — export an artist .blend character as a TEXTURED static GLB for the auto-rig.

Why (2026-10-24): the SmutBase GLBs (roster/<x>/attires/attire1/model.glb) were exported without their images and
with every mesh on one or two materials ("boots"/"eyes", "Body"/"belt"), so the material gate quarantines them and
they never reach a fight. Their source .blend files are in the repo (roster/<x>/intake/) with the real materials and
textures. This re-exports the character from that source; tools/auto_rig/rig_tripo_static.py then rigs it.

What it does:
- relinks image files that moved, by basename, from --tex-dir (e.g. "Mirko body.png" -> intake/.../textures/);
- puts every armature in REST pose;
- keeps only visible MESH objects parented to (or deformed by) an armature: the character. Hidden alternates,
  rig widgets (WGT-*), floors, lights and helper meshes are not exported;
- bakes each kept object (modifiers applied in rest pose: armature = identity, the artist's MASK modifiers applied)
  and its world transform into a fresh unparented mesh with an identity transform, so no per-node scale reaches the
  auto-rig;
- exports glTF (+Y up) with materials and embedded images, no skin, no animation, no morphs.

The .blend files are saved by Blender 4.5/5.x (header "BLENDER17-01", zstd): Blender 4.0.2 cannot read them; run
this with Blender 5.0.1 (download.blender.org, sha256 8019580e...0b09 for blender-5.0.1-linux-x64.tar.xz).

    blender5 -b --factory-startup roster/miruko/intake/miruko\\ IK/mirkoIK.blend \\
        --python tools/auto_rig/export_blend_static.py -- --out /tmp/mirko_static.glb --tex-dir roster/miruko/intake
"""
import os
import sys

import bpy

argv = sys.argv[sys.argv.index('--') + 1:]
out = argv[argv.index('--out') + 1]
tex_dir = argv[argv.index('--tex-dir') + 1] if '--tex-dir' in argv else None

idx = {}
if tex_dir:
    for r, _, fs in os.walk(tex_dir):
        for f in fs:
            idx.setdefault(f.lower(), os.path.join(r, f))
for im in bpy.data.images:
    if im.source != 'FILE' or im.packed_file:
        continue
    p = bpy.path.abspath(im.filepath)
    if not os.path.exists(p):
        alt = idx.get(os.path.basename(p).lower())
        print('RELINK', im.name, '->', alt)
        if alt:
            im.filepath = alt
            im.reload()

for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        o.data.pose_position = 'REST'

keep = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    arm = (o.parent and o.parent.type == 'ARMATURE') or any(m.type == 'ARMATURE' and m.object for m in o.modifiers)
    hidden = o.hide_render or o.hide_get() or o.hide_viewport
    if arm and not hidden:
        keep.append(o)

assign_missing = argv[argv.index('--assign-missing') + 1] if '--assign-missing' in argv else None
dg = bpy.context.evaluated_depsgraph_get()
coll = bpy.data.collections.new('wh_export')
bpy.context.scene.collection.children.link(coll)
baked = []
for o in keep:
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    me.transform(o.matrix_world)
    # The auto-rig joins every mesh into one object: a join keeps UVs only for layers whose NAME matches the active
    # object's, so a mesh whose UV layer is named differently (Rahkasa's hair, converted from a curve) lost its UVs
    # and the exporter dropped its texture. One UV layer per mesh, named "UVMap".
    if me.uv_layers:
        act = me.uv_layers.active or me.uv_layers[0]
        for uv in [u for u in me.uv_layers if u != act]:
            me.uv_layers.remove(uv)
        me.uv_layers[0].name = 'UVMap'
    # A mesh the artist left without any material renders Blender's grey default; --assign-missing gives it one of
    # the character's own materials instead (logged).
    if assign_missing and not len(me.materials):
        mat = bpy.data.materials.get(assign_missing)
        if mat:
            me.materials.append(mat)
            print('ASSIGN', o.name, '->', assign_missing)
    name = o.name
    o.name = name + '__src'  # free the name so the exported mesh keeps the artist's object name (no ".001")
    nb = bpy.data.objects.new(name, me)
    coll.objects.link(nb)
    baked.append(nb)
for o in bpy.data.objects:
    try:
        o.select_set(False)
    except RuntimeError:  # objects outside the view layer
        pass
for o in baked:
    o.select_set(True)
print('KEEP', [o.name for o in baked])
bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_apply=True, export_skins=False,
                          export_animations=False, export_morph=False, export_yup=True, export_materials='EXPORT')
print('WROTE', out, os.path.getsize(out))
