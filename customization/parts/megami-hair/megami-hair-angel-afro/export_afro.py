import bpy, os
bpy.ops.wm.open_mainfile(filepath='/home/hatch/workspace/_hair-fix-20261108/work/afro-fix-build12.blend')
def unexclude(lc):
    lc.exclude=False
    for c in lc.children: unexclude(c)
for vl in bpy.context.scene.view_layers: unexclude(vl.layer_collection)
arm=bpy.data.objects['Parvati']; afro=bpy.data.objects['AngelAfro']
used={g.name for g in afro.vertex_groups}
keep=set()
for name in used:
    b=arm.data.bones.get(name)
    while b: keep.add(b.name); b=b.parent
print('keep bones:', len(keep))
bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode='EDIT')
for eb in list(arm.data.edit_bones):
    if eb.name not in keep: arm.data.edit_bones.remove(eb)
bpy.ops.object.mode_set(mode='OBJECT')
for ob in list(bpy.data.objects):
    if ob.name not in ('Parvati','AngelAfro'): bpy.data.objects.remove(ob, do_unlink=True)
for im in list(bpy.data.images):
    if im.users==0:
        try: bpy.data.images.remove(im)
        except Exception: pass
out='/home/hatch/workspace/_hair-fix-20261108/assets/afro-v2.glb'
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_skins=True, export_apply=False, export_yup=True)
print('EXPORTED', os.path.getsize(out))
