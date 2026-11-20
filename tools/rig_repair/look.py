#!/usr/bin/env python3
"""look.py - quick front-view render of a GLB with armature overlay (Blender headless)."""
import bpy
from mathutils import Vector
import sys, os
argv = sys.argv[sys.argv.index("--") + 1:]
def opt(k, d): return argv[argv.index(k) + 1] if k in argv else d
IN = opt("--in", None); OUT = opt("--out", "/tmp/look.png")
RES = int(opt("--res", "640"))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
# bounds
mn = [1e9]*3; mx = [-1e9]*3
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
cx, cy = (mn[0]+mx[0])/2, (mn[2]+mx[2])/2
H = mx[1]-mn[1]
if arm:
    arm.show_in_front = True
    arm.data.display_type = "STICK"
# camera on +X looking at character (character faces +X per gate)
cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam)
bpy.context.scene.collection.objects.link(co)
co.location = (cx + H*1.9, (mn[1]+mx[1])/2, cy)
co.rotation_euler = (1.5708, 0, 1.5708)
bpy.context.scene.camera = co
cam.lens = 35
# sun light
sun = bpy.data.lights.new("s", "SUN"); so = bpy.data.objects.new("s", sun)
bpy.context.scene.collection.objects.link(so); sun.energy = 3
so.rotation_euler = (0.6, 0.3, 1.2)
bpy.context.scene.render.engine = "BLENDER_EEVEE"
bpy.context.scene.render.resolution_x = RES
bpy.context.scene.render.resolution_y = RES
bpy.context.scene.render.film_transparent = False
bpy.context.scene.world = bpy.data.worlds.new("w")
bpy.context.scene.world.use_nodes = False
bpy.context.scene.world.color = (1, 1, 1)
bpy.context.scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("wrote", OUT)
