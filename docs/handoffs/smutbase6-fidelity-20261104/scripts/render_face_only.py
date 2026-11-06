import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out_path = argv[0]

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.render.resolution_x = 512
scene.render.resolution_y = 640
if not scene.world:
    scene.world = bpy.data.worlds.new("W")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.28, 1)

# bbox over non-GZM visible meshes only (character geometry)
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
for ob in bpy.data.objects:
    if ob.type == 'MESH' and not ob.hide_render and not ob.name.startswith("GZM"):
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
center = (mins + maxs) / 2
size = maxs - mins
height = max(size.z, 0.1)
print("CHAR_BBOX", list(mins), list(maxs))

ld = bpy.data.lights.new("sun", 'SUN'); ld.energy = 3.0
lo = bpy.data.objects.new("sun", ld); scene.collection.objects.link(lo)
lo.rotation_euler = (math.radians(50), 0, math.radians(30))

cam_data = bpy.data.cameras.new("cam"); cam_data.clip_end = 1000
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam)
scene.camera = cam

face_t = Vector((center.x, center.y, maxs.z - height * 0.10))
front = Vector((0, -1, 0.05)).normalized()
cam.location = face_t + front * (height * 0.34)
dirv = face_t - cam.location
cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("FACE_SHOT", out_path)
