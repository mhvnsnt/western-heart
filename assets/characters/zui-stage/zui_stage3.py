"""ZUI rework stage 3 (single session): import, tints via file-backed PNGs, sleeve scrunch,
tattoo decals (correct bone parenting), beads, gourd, renders, GLB export."""
import bpy, math, os, re
from mathutils import Vector, Matrix

WS = "/home/hatch/workspace"
FLASH = os.path.join(WS, "zui_flash")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(WS, "zui_base_v1.glb"))
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == "ARMATURE"][0]

def mesh_by(sub):
    o = [x for x in sc.objects if sub in x.name and x.type == "MESH"][0]
    return o

# ---- 1. hide hair (bald monk)
for o in sc.objects:
    if "Hair" in o.name and o.type == "MESH":
        o.hide_viewport = True; o.hide_render = True

# ---- 2. tints: swap material images to file-backed tinted PNGs
TINTS = [
    ("ModelShirt_Material011", "Shirt", "zui_tint_Shirt.png"),
    ("ModelLower_Material008", "Lower", "zui_tint_Lower.png"),
    ("ModelGloves_Main_Material004", "Gloves", "zui_tint_Gloves.png"),
    ("ModelGloves_Material006", "GlovesFinger", "zui_tint_GlovesFinger.png"),
]
for mat_name, img_name, png in TINTS:
    mat = bpy.data.materials.get(mat_name)
    if not mat or not mat.use_nodes:
        print("MAT MISSING:", mat_name); continue
    new_img = bpy.data.images.load(os.path.join(WS, png))
    swapped = 0
    for n in mat.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name == img_name:
            n.image = new_img; swapped += 1
    print("tint swap:", mat_name, "nodes:", swapped)

# ---- 3. T-pose normalize (same as tpose_render.py)
for o in sc.objects:
    if o.animation_data: o.animation_data_clear()
def side_of(n):
    n2 = n.lower()
    if re.search(r'(^|[^a-z])(l|left)([^a-z]|$)|left|_l$|\.l$|^l_|l_|lft', n2) and not re.search(r'right|_r$|\.r$|^r_', n2): return 1
    if re.search(r'(^|[^a-z])(r|right)([^a-z]|$)|right|_r$|\.r$|^r_|r_|rgt', n2): return -1
    return 0
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

# ---- 4. sleeve scrunch -> short-sleeve robe (bare forearms for the tattoos)
shirt = mesh_by("ModelShirt")
me = shirt.data
n = 0
for v in me.vertices:
    if abs(v.co.x) > 0.30:
        v.co.x = 0.30 if v.co.x > 0 else -0.30
        n += 1
me.update()
print("scrunched:", n)

# ---- 5. bone-parent helper (CORRECT keep-transform)
def bone_parent(child, bone_name):
    bpy.context.view_layer.update()
    bonemx = arm.matrix_world @ arm.pose.bones[bone_name].matrix
    child.parent = arm
    child.parent_type = "BONE"
    child.parent_bone = bone_name
    # child local == world (was unparented), so parent_inverse = bone_world^-1 keeps it
    child.matrix_parent_inverse = bonemx.inverted()
    bpy.context.view_layer.update()

# ---- 6. tattoo decals
def add_tattoo(name, png, pos, target_substr, bone, size):
    bpy.ops.mesh.primitive_plane_add(size=size, location=pos)
    d = bpy.context.active_object
    d.name = f"ZX_Tat_{name}"
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=3)
    bpy.ops.object.mode_set(mode="OBJECT")
    d.rotation_euler = (math.pi / 2, 0, 0)  # normal -> -Y (front)
    bpy.context.view_layer.update()
    tgt = mesh_by(target_substr)
    mod = d.modifiers.new("SW", "SHRINKWRAP")
    mod.target = tgt
    mod.wrap_method = "NEAREST_SURFACEPOINT"
    mod.offset = 0.004
    mat = bpy.data.materials.new(f"ZX_Mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(FLASH, png))
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mat.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat.blend_method = "BLEND"
    d.data.materials.append(mat)
    bone_parent(d, bone)
    # verify it stayed
    loc = d.matrix_world.translation
    print(f"tattoo {name}: placed {tuple(round(v,2) for v in pos)} -> now {tuple(round(v,2) for v in loc)}")

TATS = [
    ("tiger",  "tiger.png",  (0.0, -0.10, 1.42),   "ModelTorso", "Spine2",       0.30),
    ("koi",    "koi.png",    (-0.52, -0.10, 1.49),  "ModelArms",  "LeftForeArm",  0.20),
    ("dragon", "dragon.png", (-0.60, -0.10, 1.47),  "ModelArms",  "LeftForeArm",  0.20),
    ("torii",  "torii.png",  (0.52, -0.10, 1.49),   "ModelArms",  "RightForeArm", 0.20),
    ("temple", "temple.png", (0.60, -0.10, 1.47),   "ModelArms",  "RightForeArm", 0.22),
    ("skull",  "skull.png",  (-0.325, -0.10, 1.49), "ModelArms",  "LeftArm",      0.22),
    ("wave",   "wave.png",   (0.325, -0.10, 1.49),  "ModelArms",  "RightArm",     0.22),
    ("flames", "flames.png", (0.0, -0.12, 1.52),    "ModelNeck",  "Neck",         0.24),
    ("crane",  "crane.png",  (-0.07, -0.10, 1.58),  "ModelFace",  "Head",         0.10),
]
for t in TATS:
    add_tattoo(*t)

# ---- 7. prayer beads (hanging U in front of chest)
bead_mat = bpy.data.materials.new("ZX_Mat_Beads")
bead_mat.use_nodes = True
bead_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.12, 0.08, 1)
nb = 16
for i in range(nb):
    t = i / (nb - 1)
    x = 0.32 * (t - 0.5)
    z = 1.50 - 0.20 * math.sin(math.pi * t)
    y = -0.14
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=(x, y, z))
    b = bpy.context.active_object
    b.name = f"ZX_Bead_{i:02d}"
    b.data.materials.append(bead_mat)
    bone_parent(b, "Neck")
print("beads done")

# ---- 8. sake gourd in hand (bone LeftHand = world -X)
gourd_mat = bpy.data.materials.new("ZX_Mat_Gourd")
gourd_mat.use_nodes = True
gourd_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.50, 0.32, 0.15, 1)
hx, hy, hz = (arm.matrix_world @ arm.pose.bones["LeftHand"].head)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(hx - 0.05, hy - 0.02, hz - 0.16))
gb = bpy.context.active_object; gb.name = "ZX_Gourd_Body"
gb.scale = (1, 1, 1.25); gb.data.materials.append(gourd_mat)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(hx - 0.05, hy - 0.02, hz - 0.045))
gn = bpy.context.active_object; gn.name = "ZX_Gourd_Neck"
gn.scale = (1, 1, 1.1); gn.data.materials.append(gourd_mat)
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.03, location=(hx - 0.05, hy - 0.02, hz + 0.015))
gc = bpy.context.active_object; gc.name = "ZX_Gourd_Cork"
gc.data.materials.append(gourd_mat)
for g in (gb, gn, gc):
    bone_parent(g, "LeftHand")
print("gourd done")

# ---- 9. save + export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WS, "zui_stage3.blend"))
bpy.ops.export_scene.gltf(filepath=os.path.join(WS, "zui_rework_v2.glb"), export_format="GLB")
print("SAVED stage3 + GLB")

# ---- 10. renders
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"; sh.show_shadows = False; sh.show_cavity = False
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
sh.background_type = "WORLD"; w.color = (1, 1, 1)
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
sc.render.resolution_x = sc.render.resolution_y = 2048
sc.render.image_settings.file_format = "PNG"
cam = bpy.data.objects.new("rcam", bpy.data.cameras.new("rcam"))
sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.clip_end = 1000
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type != "MESH" or o.hide_viewport: continue
    e = o.evaluated_get(dg); m = e.to_mesh()
    pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
c = (mn + mx) / 2; d = mx - mn
span = max(d.x, d.z) * 1.15
for view, loc, rot in [
    ("front", (c.x, mn.y - 10 * max(d), c.z), (math.pi / 2, 0, 0)),
    ("side", (mx.x + 10 * max(d), c.y, c.z), (math.pi / 2, 0, math.pi / 2)),
    ("back", (c.x, mx.y + 10 * max(d), c.z), (math.pi / 2, 0, math.pi)),
]:
    cam.location = loc; cam.rotation_euler = rot
    cam.data.ortho_scale = span
    sc.render.filepath = os.path.join(WS, f"zui_v2_{view}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", view)
print("STAGE3 DONE")
