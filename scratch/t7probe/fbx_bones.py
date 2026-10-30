import bpy, json, sys, math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=sys.argv[sys.argv.index('--')+1], automatic_bone_orientation=False)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
out = {'armature': arm.name, 'matrix_world': [list(r) for r in arm.matrix_world], 'bones': []}
for b in arm.data.bones:
    ml = b.matrix_local
    out['bones'].append({'name': b.name, 'parent': b.parent.name if b.parent else None,
        'head': list(b.head_local), 'tail': list(b.tail_local),
        'matrix_local': [list(r) for r in ml]})
json.dump(out, open(sys.argv[sys.argv.index('--')+2], 'w'), indent=1)
print('BONES', len(out['bones']))
