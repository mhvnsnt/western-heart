import bpy, sys, math
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:]
glb, out = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
# frame all objects
import numpy as np
mins=Vector((1e9,)*3); maxs=Vector((-1e9,)*3)
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':
        for c in ob.bound_box:
            w=ob.matrix_world @ Vector(c)
            mins=Vector(map(min, mins, w)); maxs=Vector(map(max, maxs, w))
ctr=(mins+maxs)/2; size=(maxs-mins)
print('BBOX', tuple(np.round(mins,3)), tuple(np.round(maxs,3)), 'size', tuple(np.round(size,3)))
diag=float(np.linalg.norm(np.array(size)))
# camera: front = looking from -Y toward +Y (character faces +Z-up in gltf Y-up after import: blender Z up)
cam_data=bpy.data.cameras.new('cam'); cam=bpy.data.objects.new('cam', cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location=(ctr.x, ctr.y - diag*1.15, ctr.z + diag*0.12)
cam.rotation_euler=(math.radians(90-6), 0, 0)
bpy.context.scene.camera=cam
sun_data=bpy.data.lights.new('sun','SUN'); sun_data.energy=3.0
sun=bpy.data.objects.new('sun', sun_data); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(50), 0, math.radians(30))
w=bpy.context.scene.world or bpy.data.worlds.new('w'); bpy.context.scene.world=w
w.use_nodes=True
w.node_tree.nodes['Background'].inputs[0].default_value=(0.25,0.25,0.28,1)
w.node_tree.nodes['Background'].inputs[1].default_value=1.0
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.cycles.device='CPU'
sc.render.resolution_x=448; sc.render.resolution_y=576
sc.render.filepath=out
bpy.ops.render.render(write_still=True)
print('RENDERED', out)
