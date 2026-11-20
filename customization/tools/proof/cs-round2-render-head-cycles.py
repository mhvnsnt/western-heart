import bpy, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out_prefix = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scene = bpy.context.scene
world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.35, 0.35, 0.38, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.2

def add_sun(name, loc, energy, rot):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = energy
    o = bpy.data.objects.new(name, d); o.location = loc; o.rotation_euler = rot
    scene.collection.objects.link(o)

add_sun('key', (2, -3, 4), 3.0, (math.radians(50), 0, math.radians(30)))
add_sun('fill', (-3, -1, 2), 1.2, (math.radians(70), 0, math.radians(-40)))
add_sun('rim', (0, 3, 3), 1.5, (math.radians(60), 0, math.radians(180)))

scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.device = 'CPU'
scene.render.resolution_x = 560
scene.render.resolution_y = 560

cam_data = bpy.data.cameras.new('cam')
cam = bpy.data.objects.new('cam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

def look(loc, target, lens=70):
    cam.location = loc
    cam.data.lens = lens
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

import os
os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
look((0, -0.62, 1.63), (0, 0, 1.615))          # dead front, head height
scene.render.filepath = out_prefix + '_face.png'
bpy.ops.render.render(write_still=True)
look((0.62, 0, 1.63), (0, 0, 1.615))           # dead side (his left)
scene.render.filepath = out_prefix + '_side.png'
bpy.ops.render.render(write_still=True)
print('RENDERED', out_prefix)
