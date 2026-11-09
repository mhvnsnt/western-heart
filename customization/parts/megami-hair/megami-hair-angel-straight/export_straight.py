import bpy, os
bpy.ops.wm.open_mainfile(filepath='/home/hatch/workspace/_hair-fix-20261108/work/straight-build5.blend')
def unexclude(lc):
    lc.exclude=False
    for c in lc.children: unexclude(c)
for vl in bpy.context.scene.view_layers: unexclude(vl.layer_collection)
arm=bpy.data.objects['Parvati']
for im in bpy.data.images:
    if max(im.size)>1024 if im.size[0] else False:
        try: im.scale(1024,1024)
        except Exception: pass
meshes=[bpy.data.objects['AngelStraight'], bpy.data.objects['AngelHeadband']]
used=set()
for ob in meshes:
    for g in ob.vertex_groups: used.add(g.name)
keep=set()
for name in used:
    b=arm.data.bones.get(name)
    while b: keep.add(b.name); b=b.parent
print('keep bones:', len(keep))
bpy.context.view_layer.objects.active=arm; arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for eb in list(arm.data.edit_bones):
    if eb.name not in keep: arm.data.edit_bones.remove(eb)
bpy.ops.object.mode_set(mode='OBJECT'); arm.select_set(False)
for ob in bpy.data.objects: ob.hide_viewport = ob not in meshes and ob is not arm
bpy.ops.object.select_all(action='DESELECT')
for ob in meshes: ob.select_set(True)
arm.select_set(True); bpy.context.view_layer.objects.active=arm
OUT='/home/hatch/workspace/_hair-fix-20261108/work/straight-raw.glb'
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_skins=True, export_apply=False, export_yup=True)
print('EXPORTED', os.path.getsize(OUT))
