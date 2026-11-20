import bpy, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=argv[0])
dg = bpy.context.evaluated_depsgraph_get()
bpy.context.view_layer.update()
for o in bpy.context.scene.objects:
    if o.type != 'MESH':
        continue
    ev = o.evaluated_get(dg)
    vs = [ev.matrix_world @ v.co for v in ev.data.vertices]
    if not vs:
        continue
    xs = [v.x for v in vs]; ys = [v.y for v in vs]; zs = [v.z for v in vs]
    print('PROBE %s n=%d x[%.3f,%.3f] y[%.3f,%.3f] z[%.3f,%.3f] parent=%s ptype=%s mods=%s' % (
        o.name[:44], len(vs), min(xs), max(xs), min(ys), max(ys), min(zs), max(zs),
        o.parent.name if o.parent else '-', o.parent_type,
        [m.type for m in o.modifiers]))
print('PROBE DONE')
