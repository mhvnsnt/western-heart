"""ZUI rework stage 1: import, hide hair, robe/pants tints, T-pose, preview render."""
import bpy, sys, math, re
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath="/home/hatch/workspace/zui_base_v1.glb")
sc = bpy.context.scene

# 1. hide hair (bald monk)
for o in sc.objects:
    if "Hair" in o.name and o.type == "MESH":
        o.hide_viewport = True
        o.hide_render = True
        print("hidden:", o.name)

# 2. robe rework: saffron shirt (crest print removed), indigo pants
def solid_fill(img_name, rgb):
    img = bpy.data.images.get(img_name)
    if not img:
        print("IMG MISSING:", img_name); return
    px = [c for _ in range(img.size[0] * img.size[1]) for c in (rgb[0], rgb[1], rgb[2], 1.0)]
    img.pixels = px
    img.update()
    print("tinted:", img_name, rgb)

solid_fill("Shirt", (0.93, 0.50, 0.10))   # saffron robe
solid_fill("Lower", (0.20, 0.14, 0.45))   # indigo pants

# 3. T-pose via skeleton (same logic as tpose_render.py)
for o in sc.objects:
    if o.animation_data: o.animation_data_clear()
arms = [o for o in sc.objects if o.type == "ARMATURE"]
def side_of(n):
    n2 = n.lower()
    if re.search(r'(^|[^a-z])(l|left)([^a-z]|$)|left|_l$|\.l$|^l_|l_|lft', n2) and not re.search(r'right|_r$|\.r$|^r_', n2): return 1
    if re.search(r'(^|[^a-z])(r|right)([^a-z]|$)|right|_r$|\.r$|^r_|r_|rgt', n2): return -1
    return 0
for arm in arms:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    order = sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive))
    for pb in order:
        n = pb.name.lower()
        if not re.fullmatch(r'(l|r)_(upperarm|lowerarm|hand)|(left|right)(arm|forearm|hand)|(mixamorig:)?(left|right)(arm|forearm|hand)|(upperarm|lowerarm|forearm|hand)[._](l|r)|bip01_[lr]_(upperarm|forearm|hand)', n): continue
        if side_of(pb.name) == 0: continue
        bpy.context.view_layer.update()
        mw = arm.matrix_world @ pb.matrix
        head = mw.translation
        kids = [k for k in pb.children if re.search(r'arm|hand', k.name, re.I) and not re.search(r'twt|twist|mus|drv|adr|pmp', k.name, re.I)]
        if re.search(r'hand', n) or not kids: continue
        tail = arm.matrix_world @ kids[0].head
        cur = (tail - head)
        if cur.length < 1e-6: continue
        sx = 1 if head.x > 0 else -1
        tgt = Vector((sx, 0, 0))
        q = cur.normalized().rotation_difference(tgt)
        R = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head)
        pb.matrix = arm.matrix_world.inverted() @ R @ mw
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

# report world bbox + bone world positions
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type != "MESH" or o.hide_viewport: continue
    e = o.evaluated_get(dg); m = e.to_mesh()
    pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
print("BBOX mn", tuple(round(v, 3) for v in mn), "mx", tuple(round(v, 3) for v in mx))
arm = arms[0]
for bn in ["Spine", "Spine1", "Spine2", "Neck", "Head", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand", "LeftShoulder", "RightShoulder"]:
    pb = arm.pose.bones.get(bn)
    if pb:
        w = arm.matrix_world @ pb.head
        print("BONE", bn, tuple(round(v, 3) for v in w))

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/zui_stage1.blend")

# quick front preview
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"; sh.show_shadows = False; sh.show_cavity = False
sh.background_type = "WORLD"; w.color = (1, 1, 1)
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
sc.render.resolution_x = sc.render.resolution_y = 1024; sc.render.image_settings.file_format = "PNG"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
c = (mn + mx) / 2; d = mx - mn
cam.location = (c.x, mn.y - 10 * max(d), c.z); cam.rotation_euler = (math.pi / 2, 0, 0)
cam.data.ortho_scale = max(d.x, d.z) * 1.15
sc.render.filepath = "/home/hatch/workspace/zui_preview_front.png"
bpy.ops.render.render(write_still=True)
print("PREVIEW DONE")
