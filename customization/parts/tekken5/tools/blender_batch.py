"""Blender (in-session) batch: OBJ+MTL -> GLB, one factory reset per job.
Jobs file: JSON list of {obj, glb}. Prints BATCHDONE/ BATCHFAIL per job."""
import bpy, sys, json, time
from collections import defaultdict

jobs = json.load(open(sys.argv[sys.argv.index('--') + 1]))
for job in jobs:
    t = time.time()
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.obj_import(filepath=job['obj'])
        for mat in bpy.data.materials:
            if not mat.use_nodes: continue
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    node.image.colorspace_settings.name = 'sRGB'
                    try: node.extension = 'REPEAT'
                    except Exception: pass
        groups = defaultdict(list)
        for o in list(bpy.data.objects):
            if o.type == 'MESH':
                key = o.data.materials[0].name if o.data.materials else 'none'
                groups[key].append(o)
        for key, objs in groups.items():
            bpy.ops.object.select_all(action='DESELECT')
            for o in objs: o.select_set(True)
            bpy.context.view_layer.objects.active = objs[0]
            if len(objs) > 1: bpy.ops.object.join()
            bpy.context.view_layer.objects.active.name = 'mat_' + key
        bpy.ops.export_scene.gltf(filepath=job['glb'], export_format='GLB', export_apply=True)
        print('BATCHDONE', job['glb'], round(time.time() - t, 1), flush=True)
    except Exception as e:
        print('BATCHFAIL', job['glb'], repr(e), flush=True)
