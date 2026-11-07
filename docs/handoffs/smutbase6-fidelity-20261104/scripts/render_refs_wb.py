import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out_dir, tag = argv[0], argv[1]
os.makedirs(out_dir, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'TEXTURE'
try:
    scene.eevee.taa_render_samples = 16
except Exception:
    pass
scene.render.resolution_x = 512
scene.render.resolution_y = 768
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("W") if not scene.world else scene.world
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# bounds of render-visible meshes
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
found = False
for ob in bpy.data.objects:
    if ob.type == 'MESH' and not ob.hide_render:
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w)); found = True
if not found:
    print("NO_VISIBLE_MESH"); sys.exit(0)
center = (mins + maxs) / 2
size = maxs - mins
height = max(size.z, 0.1)
print("BBOX", list(mins), list(maxs))

# sun light
ld = bpy.data.lights.new("sun", 'SUN'); ld.energy = 3.0
lo = bpy.data.objects.new("sun", ld); scene.collection.objects.link(lo)
lo.rotation_euler = (math.radians(50), 0, math.radians(30))

cam_data = bpy.data.cameras.new("cam"); cam_data.clip_end = 1000
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam)
scene.camera = cam
dist = height * 1.9

def shot(name, direction, target, d):
    cam.location = target + direction * d
    # look at target
    dirv = target - cam.location
    cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = os.path.join(out_dir, f"{tag}-{name}-20261104.png")
    bpy.ops.render.render(write_still=True)
    print("SHOT", scene.render.filepath)

front = Vector((0, -1, 0.08)); three = Vector((0.75, -0.75, 0.15))
shot("front", front.normalized(), center, dist)
shot("q34", three.normalized(), center, dist)
# face close-up: target top of bbox
face_t = Vector((center.x, center.y, maxs.z - height * 0.14))
shot("face", front.normalized(), face_t, height * 0.42)
print("RENDERS_DONE")
