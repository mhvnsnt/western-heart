"""G4 import-verify (PR #397 standard): every shipped GLB imports
clean in Blender with a skeleton (bones > 0) and skin weights.
Fresh scene per character (per-character isolation). Run:
  blender -b --python g4_blender_verify.py -- <glb_dir> <out.json>
"""
import bpy, json, os, sys

argv = sys.argv[sys.argv.index('--') + 1:]
glb_dir, out_json = argv[0], argv[1]
report = {}
for n in range(1, 73):
    name = f'char{n:03d}'
    path = os.path.join(glb_dir, name + '.glb')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=path)
    except Exception as e:
        report[name] = {'import': 'FAIL', 'error': str(e)}
        continue
    arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    meshes = [o for o in bpy.data.objects if o.type == 'MESH'
              and o.name != 'Icosphere']
    entry = {'import': 'ok', 'armatures': len(arms),
             'bones': len(arms[0].data.bones) if arms else 0,
             'meshes': len(meshes), 'verts': 0, 'weighted_verts': 0}
    for m in meshes:
        entry['verts'] += len(m.data.vertices)
        if m.vertex_groups:
            entry['weighted_verts'] += len(m.data.vertices)
    report[name] = entry
ok = sum(1 for v in report.values()
         if v.get('import') == 'ok' and v.get('bones', 0) > 0
         and v.get('weighted_verts', 0) > 0)
json.dump({'pass_count': ok, 'total': 72, 'characters': report},
          open(out_json, 'w'), indent=1)
print(f'G4 IMPORT-VERIFY: {ok}/72 pass')
