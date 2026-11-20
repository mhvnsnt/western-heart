"""ZUI rework stage 2: sleeve scrunch, glove tint, tattoo decals, beads, gourd, GLB export, renders."""
import bpy, math, os
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath="/home/hatch/workspace/zui_stage1.blend")
sc = bpy.context.scene
arm = [o for o in sc.objects if o.type == "ARMATURE"][0]
FLASH = "/home/hatch/workspace/zui_flash"

def objs(name_part):
    return [o for o in sc.objects if name_part in o.name and o.type == "MESH"]

# ---- 1. sleeve scrunch: collapse shirt verts with |x|>0.30 to x=+-0.30 (short-sleeve robe)
shirt = objs("ModelShirt")[0]
me = shirt.data
n = 0
for v in me.vertices:
    if abs(v.co.x) > 0.30:
        v.co.x = 0.30 if v.co.x > 0 else -0.30
        n += 1
me.update()
print("scrunched verts:", n)

# ---- 2. glove tint -> cream hand-wraps
def solid_fill(img_name, rgb):
    img = bpy.data.images.get(img_name)
    if not img: print("IMG MISSING:", img_name); return
    img.pixels = [c for _ in range(img.size[0] * img.size[1]) for c in (rgb[0], rgb[1], rgb[2], 1.0)]
    img.update(); print("tinted:", img_name)
solid_fill("Gloves", (0.85, 0.72, 0.55))
solid_fill("GlovesFinger", (0.85, 0.72, 0.55))

# ---- 3. tattoo decals
def bone_head(bn):
    return arm.matrix_world @ arm.pose.bones[bn].head

def add_tattoo(name, png, pos, target_substr, bone, size):
    bpy.ops.mesh.primitive_plane_add(size=size, location=pos)
    d = bpy.context.active_object
    d.name = f"ZX_Tat_{name}"
    # subdivide for drape
    bpy.context.view_layer.objects.active = d
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=3)
    bpy.ops.object.mode_set(mode="OBJECT")
    # orient +Z along -Y (facing viewer/front)
    d.rotation_euler = (math.pi / 2, 0, 0)  # plane normal +Z -> -Y? check below
    # shrinkwrap to skin
    tgt = objs(target_substr)[0]
    mod = d.modifiers.new("SW", "SHRINKWRAP")
    mod.target = tgt
    mod.wrap_method = "NEAREST_SURFACEPOINT"
    mod.offset = 0.004
    # material with alpha
    mat = bpy.data.materials.new(f"ZX_Mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(FLASH, png))
    mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    mat.node_tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat.blend_method = "BLEND"
    d.data.materials.append(mat)
    # bone parent (keep transform)
    bpy.context.view_layer.update()
    d.parent = arm
    d.parent_type = "BONE"
    d.parent_bone = bone
    bonemx = arm.matrix_world @ arm.pose.bones[bone].matrix
    d.matrix_parent_inverse = bonemx.inverted() @ d.matrix_world
    print("tattoo:", name, "->", bone)
    return d

# NOTE: bone "Left*" is at world -X (anatomical right); "Right*" at +X (anatomical left)
TATS = [
    ("tiger",   "tiger.png",   (0.0, -0.10, 1.42),  "ModelTorso", "Spine2",       0.30),
    ("koi",     "koi.png",     (-0.52, -0.10, 1.49), "ModelArms",  "LeftForeArm",  0.20),
    ("dragon",  "dragon.png",  (-0.60, -0.10, 1.47), "ModelArms",  "LeftForeArm",  0.20),
    ("torii",   "torii.png",   (0.52, -0.10, 1.49),  "ModelArms",  "RightForeArm", 0.20),
    ("temple",  "temple.png",  (0.60, -0.10, 1.47),  "ModelArms",  "RightForeArm", 0.22),
    ("skull",   "skull.png",   (-0.325, -0.10, 1.49), "ModelArms", "LeftArm",      0.22),
    ("wave",    "wave.png",    (0.325, -0.10, 1.49),  "ModelArms", "RightArm",     0.22),
    ("flames",  "flames.png",  (0.0, -0.12, 1.52),   "ModelNeck",  "Neck",         0.24),
    ("crane",   "crane.png",   (-0.07, -0.10, 1.58), "ModelFace",  "Head",         0.10),
]
for t in TATS:
    add_tattoo(*t)

# ---- 4. prayer beads: hanging loop in front of chest
bead_mat = bpy.data.materials.new("ZX_Mat_Beads")
bead_mat.use_nodes = True
bead_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.12, 0.08, 1)
nb = 16
for i in range(nb):
    t = i / (nb - 1)  # 0..1 across a hanging U in front of the chest
    x = 0.32 * (t - 0.5)          # -0.16 .. 0.16
    z = 1.50 - 0.20 * math.sin(math.pi * t)  # dips to mid-chest
    y = -0.14
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=(x, y, z))
    b = bpy.context.active_object
    b.name = f"ZX_Bead_{i:02d}"
    b.data.materials.append(bead_mat)
    b.parent = arm; b.parent_type = "BONE"; b.parent_bone = "Neck"
    bpy.context.view_layer.update()
    bonemx = arm.matrix_world @ arm.pose.bones["Neck"].matrix
    b.matrix_parent_inverse = bonemx.inverted() @ b.matrix_world
print("beads done")

# ---- 5. sake gourd in right hand (bone LeftHand, world -X)
gourd_mat = bpy.data.materials.new("ZX_Mat_Gourd")
gourd_mat.use_nodes = True
gourd_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.50, 0.32, 0.15, 1)
hx, hy, hz = bone_head("LeftHand")
# gourd body (bulb)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(hx - 0.05, hy - 0.02, hz - 0.16))
gb = bpy.context.active_object; gb.name = "ZX_Gourd_Body"
gb.scale = (1, 1, 1.25); gb.data.materials.append(gourd_mat)
# gourd neck (smaller bulb on top)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(hx - 0.05, hy - 0.02, hz - 0.045))
gn = bpy.context.active_object; gn.name = "ZX_Gourd_Neck"
gn.scale = (1, 1, 1.1); gn.data.materials.append(gourd_mat)
# cork
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.03, location=(hx - 0.05, hy - 0.02, hz + 0.015))
gc = bpy.context.active_object; gc.name = "ZX_Gourd_Cork"
gc.data.materials.append(gourd_mat)
for g in (gb, gn, gc):
    g.parent = arm; g.parent_type = "BONE"; g.parent_bone = "LeftHand"
    bpy.context.view_layer.update()
    bonemx = arm.matrix_world @ arm.pose.bones["LeftHand"].matrix
    g.matrix_parent_inverse = bonemx.inverted() @ g.matrix_world
print("gourd done")

bpy.ops.wm.save_as_mainfile(filepath="/home/hatch/workspace/zui_stage2.blend")
bpy.ops.export_scene.gltf(filepath="/home/hatch/workspace/zui_rework_v2.glb", export_format="GLB")
print("SAVED stage2 + GLB")

# ---- 6. renders: front / side / back, 2048, white
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
    if o.type != "MESH" or o.hide_viewport or o.name.startswith("ZX_Tat"): continue
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
    sc.render.filepath = f"/home/hatch/workspace/zui_rework_{view}.png"
    bpy.ops.render.render(write_still=True)
    print("rendered", view)
print("STAGE2 DONE")
