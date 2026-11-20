import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
out_dir, tag = argv[0], argv[1]
scene = bpy.context.scene
mins = Vector((1e9, 1e9, 1e9)); maxs = Vector((-1e9, -1e9, -1e9))
for ob in bpy.data.objects:
    if ob.type == 'MESH' and not ob.hide_render:
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            mins = Vector(map(min, mins, w)); maxs = Vector(map(max, maxs, w))
center = (mins + maxs) / 2; size = maxs - mins; height = max(size.z, 0.1)
cam = scene.camera
face_t = Vector((center.x, center.y, maxs.z - height * 0.14))
d = height * 0.42
loc = face_t + Vector((0, -1, 0.08)).normalized() * d
cam.location = loc
cam.rotation_euler = (face_t - loc).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = os.path.join(out_dir, f"{tag}-face-20261104.png")
bpy.ops.render.render(write_still=True)
print("FACE_DONE", scene.render.filepath, os.path.exists(scene.render.filepath))
