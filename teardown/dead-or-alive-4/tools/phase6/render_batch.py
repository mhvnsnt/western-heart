import bpy, sys, math
from mathutils import Vector
import numpy as np
argv = sys.argv[sys.argv.index('--') + 1:]
pairs = [(argv[i], argv[i + 1]) for i in range(0, len(argv), 2)]
for glb, out in pairs:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    # world-space bbox from evaluated mesh vertices (skin-aware via depsgraph)
    dg = bpy.context.evaluated_depsgraph_get()
    mins = Vector((1e9,) * 3); maxs = Vector((-1e9,) * 3)
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ev = ob.evaluated_get(dg)
            for v in ev.data.vertices:
                w = ev.matrix_world @ v.co
                mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
    ctr = (mins + maxs) / 2; size = (maxs - mins)
    diag = float(np.linalg.norm(np.array(size))) or 1.0
    print('BBOX', glb, tuple(np.round(mins, 3)), tuple(np.round(maxs, 3)))
    cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (ctr.x, ctr.y - diag * 1.15, ctr.z + diag * 0.12)
    cam.rotation_euler = (math.radians(90 - 6), 0, 0)
    bpy.context.scene.camera = cam
    sun_data = bpy.data.lights.new('sun', 'SUN'); sun_data.energy = 3.0
    sun = bpy.data.objects.new('sun', sun_data); bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    w = bpy.context.scene.world or bpy.data.worlds.new('w'); bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            m = bpy.data.materials.new('mat'); m.use_nodes = True
            bsdf = m.node_tree.nodes['Principled BSDF']
            bsdf.inputs['Base Color'].default_value = (0.75, 0.72, 0.7, 1)
            bsdf.inputs['Roughness'].default_value = 0.85
            ob.data.materials.clear(); ob.data.materials.append(m)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 8; sc.cycles.device = 'CPU'
    sc.render.resolution_x = 448; sc.render.resolution_y = 576
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print('RENDERED', out)
