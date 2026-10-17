# Blender headless: import model, force T-pose via skeleton, render 1:1 front+side on pure white.
import bpy, sys, math, os, re, json
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--")+1:]
src, outbase = a[0], a[1]
side = "side" in a[2:]
flip = "flip" in a[2:]
bpy.ops.wm.read_factory_settings(use_empty=True)
ext = os.path.splitext(src)[1].lower()
if ext in (".glb", ".gltf"): bpy.ops.import_scene.gltf(filepath=src)
elif ext == ".fbx": bpy.ops.import_scene.fbx(filepath=src, ignore_leaf_bones=True)
sc = bpy.context.scene
for o in sc.objects: o.animation_data_clear() if o.animation_data else None
for o in list(sc.objects):
    if o.type=="MESH" and re.match(r'(icosphere|cube|plane|sphere|cylinder)', o.name, re.I): bpy.data.objects.remove(o)
arms = [o for o in sc.objects if o.type == "ARMATURE"]
import glob
texdir = os.path.dirname(src)
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    if any(n.type=="TEX_IMAGE" and n.image for n in mat.node_tree.nodes): continue
    base = re.sub(r'^MI_', '', mat.name)
    cand = [f for suf in ("_C","_D","_BC","_ALB") for f in glob.glob(os.path.join(texdir, "T_"+base+suf+".tga"))]
    if not cand: continue
    try: img = bpy.data.images.load(cand[0])
    except Exception: continue
    nt = mat.node_tree; bsdf = next((n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"), None)
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
    if bsdf: nt.links.new(t.outputs[0], bsdf.inputs[0])
report = {"src": src, "armatures": len(arms), "posed": []}
def side_of(n):
    n2 = n.lower()
    if re.search(r'(^|[^a-z])(l|left)([^a-z]|$)|left|_l$|\.l$|^l_|l_|lft', n2) and not re.search(r'right|_r$|\.r$|^r_', n2): return 1   # character left -> +X
    if re.search(r'(^|[^a-z])(r|right)([^a-z]|$)|right|_r$|\.r$|^r_|r_|rgt', n2): return -1
    return 0
ARM = re.compile(r'(upper_?arm|upperarm|arm(?!or)|shoulder|clavicle|forearm|lowerarm|elbow|hand|wrist|finger|thumb|index|middle|ring|pinky|little)', re.I)
for arm in arms:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1,0,0,0); pb.location=(0,0,0)
    bpy.context.view_layer.update()
    # arm chain: upperarm, forearm, hand (exclude clavicle/fingers) -> point to +/-X horizontally
    order = sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive))
    for pb in order:
        n = pb.name.lower()
        if not re.fullmatch(r'(l|r)_(upperarm|lowerarm|hand)|(left|right)(arm|forearm|hand)|(mixamorig:)?(left|right)(arm|forearm|hand)|(upperarm|lowerarm|forearm|hand)[._](l|r)|bip01_[lr]_(upperarm|forearm|hand)', n): continue
        s = side_of(pb.name)
        if s == 0: continue
        bpy.context.view_layer.update()
        mw = arm.matrix_world @ pb.matrix
        head = mw.translation
        kids = [k for k in pb.children if re.search(r'arm|hand', k.name, re.I) and not re.search(r'twt|twist|mus|drv|adr|pmp', k.name, re.I)]
        if re.search(r'hand', n) or not kids: continue
        tail = arm.matrix_world @ kids[0].head
        cur = (tail - head)
        if cur.length < 1e-6: continue
        tgt = Vector((s*1, 0, 0)) if not (arm.matrix_world @ Vector((0,0,0))) is None else None
        # decide sign using actual world side of shoulder (robust to naming flips)
        sx = 1 if head.x > 0 else -1
        tgt = Vector((sx, 0, 0))
        q = cur.normalized().rotation_difference(tgt)
        R = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head)
        pb.matrix = arm.matrix_world.inverted() @ R @ mw
        report["posed"].append(pb.name)
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type != "MESH": continue
    e = o.evaluated_get(dg); m = e.to_mesh()
    pts += [e.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
c = (mn+mx)/2; d = mx-mn
report["bbox"] = [list(mn), list(mx)]
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading; sh.light = "FLAT"; sh.color_type = "TEXTURE"; sh.show_shadows = False; sh.show_cavity=False
sh.background_type = "WORLD"; w.color = (1,1,1)
sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
sc.render.resolution_x = sc.render.resolution_y = 2048; sc.render.image_settings.file_format = "PNG"
sc.display.render_aa = "8"
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"
for view in (["front","side"] if side else ["front"]):
    if view == "front":
        cam.location = (c.x, (mx.y + 10*max(d)) if flip else (mn.y - 10*max(d)), c.z); cam.rotation_euler = (math.pi/2, 0, math.pi if flip else 0); span = max(d.x, d.z)
    else:
        cam.location = (mx.x + 10*max(d), c.y, c.z); cam.rotation_euler = (math.pi/2, 0, math.pi/2); span = max(d.y, d.z)
    cam.data.ortho_scale = span * 1.12
    cam.data.clip_end = 100*max(d)
    sc.render.filepath = f"{outbase}_{view}.png"
    bpy.ops.render.render(write_still=True)
json.dump(report, open(outbase + "_report.json", "w"), indent=1, default=str)
print("DONE", json.dumps({k: report[k] for k in ("armatures",)}), len(report["posed"]))
