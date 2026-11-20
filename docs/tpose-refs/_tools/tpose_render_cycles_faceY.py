"""T-pose reference renderer - Cycles CPU path. faceY VARIANT.

Adaptation of docs/tpose-refs/_tools/tpose_render.py for this VM, where
Blender Workbench/Eevee segfaults (no libEGL). Uses Cycles CPU with an
emission override to get the spec's flat unlit look (Workbench FLAT equiv).

Spec: 2048x2048 RGB PNG, pure white 255,255,255 bg, ortho camera,
ortho_scale = 1.12 * max(span) (~5% / ~109px margin), T-pose via skeleton,
front = true front (character faces -X in RigModels T7 FBX rips),
side = character's left side (camera on -Y).

Usage: blender -b --python tpose_render_cycles_faceY.py -- <model.fbx|glb> <outbase> [res]
VARIANT: for models authored facing -Y (not -X like the RigModels T7 FBX rips).
Applies Rz(-90deg) after import so the front faces -X where the front camera sits.
Verified by own-eyes check: side.png (camera on -Y) shows the model front-on,
proving the model faces -Y; Rz(-90) maps -Y -> -X. Side camera then sees the
model's left side, matching the base script's spec.
Writes <outbase>_front.png, <outbase>_side.png, <outbase>_report.json
"""
import bpy, sys, math, os, re, json, glob
from mathutils import Vector, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
SRC = a[0]
OUTBASE = a[1]
RES = int(a[2]) if len(a) > 2 else 2048

os.makedirs(os.path.dirname(OUTBASE) or ".", exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

ext = os.path.splitext(SRC)[1].lower()
if ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=SRC)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=SRC, ignore_leaf_bones=True)
else:
    raise SystemExit(f"unsupported: {ext}")
print("IMPORT OK:", SRC)

# --- faceY variant: rotate -90deg about Z so a -Y-facing model faces -X ---
R = Matrix.Rotation(-math.pi / 2, 4, 'Z')
for o in sc.objects:
    o.matrix_world = R @ o.matrix_world
bpy.context.view_layer.update()
print("ROTATED -90deg Z (faceY->faceX)")

for o in sc.objects:
    if o.animation_data:
        o.animation_data_clear()
for o in list(sc.objects):
    if o.type == "MESH" and re.match(r'(icosphere|cube|plane|sphere|cylinder)', o.name, re.I):
        bpy.data.objects.remove(o)

# --- texture resolution + flat unlit look: emission override fed by albedo ---
# FBX rips reference textures by absolute Windows paths, so image datablocks
# often exist with has_data=False. Recover from files next to the source.
texdir = os.path.dirname(SRC)
report = {"src": SRC, "armatures": 0, "posed": []}
def find_tex_file(mat_name, texdir):
    base = re.sub(r'^MI_', '', mat_name)
    m = re.match(r'mat_\d+-(.+)', base)
    if m:
        base = m.group(1)
    for ext in (".jpg", ".jpeg", ".tga", ".png", ".bmp"):
        for cand in glob.glob(os.path.join(texdir, base if base.lower().endswith(ext) else base + ext)):
            return cand
    # loose: any file whose stem matches
    stem = os.path.splitext(base)[0]
    for f in glob.glob(os.path.join(texdir, stem + ".*")):
        if os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".tga", ".png", ".bmp"):
            return f
    return None

tex_report = {"recovered": 0, "missing": []}


def diffuse_node(nt):
    """Prefer the TEX_IMAGE feeding Principled Base Color, else the first one."""
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        for link in nt.links:
            if link.to_node == bsdf and link.to_socket.name == "Base Color":
                if link.from_node.type == "TEX_IMAGE":
                    return link.from_node
    for n in nt.nodes:
        if n.type == "TEX_IMAGE":
            return n
    return None


for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        continue
    img_node = diffuse_node(nt)
    if img_node is not None and img_node.image is None:
        # no image at all: try material-name-derived filename
        f1 = find_tex_file(mat.name, texdir)
        if f1 and os.path.isfile(f1):
            try:
                img_node.image = bpy.data.images.load(f1)
                tex_report["recovered"] += 1
            except Exception:
                pass
    if img_node is not None and img_node.image is not None:
        # NOTE: image.has_data is unreliable in background mode (False even for
        # valid files); Cycles reads the file at render time, so only the
        # filepath matters. Recover when the referenced file is not loadable.
        ipath = (img_node.image.filepath or "").strip()
        needs_recovery = ipath.startswith("http") or not os.path.isfile(ipath)
        if needs_recovery:
            # recover: try basename of the referenced path (often a rigmodels.com URL),
            # then T_<base>_C.tga, then material-name-derived filename
            cands = []
            bn = os.path.basename(ipath.rstrip("/"))
            if bn:
                cands.append(os.path.join(texdir, bn))
            base = re.sub(r'^MI_', '', mat.name)
            cands += [f for suf in ("_C", "_D", "_BC", "_ALB")
                      for f in glob.glob(os.path.join(texdir, "T_" + base + suf + ".tga"))]
            f1 = find_tex_file(mat.name, texdir)
            if f1:
                cands.append(f1)
            loaded = False
            for cpath in cands:
                if os.path.isfile(cpath):
                    try:
                        img_node.image = bpy.data.images.load(cpath)
                        loaded = True
                        tex_report["recovered"] += 1
                        break
                    except Exception:
                        continue
            if not loaded:
                img_node = None
    if img_node is None or img_node.image is None:
        tex_report["missing"].append(mat.name)
        continue
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    try:
        nt.links.new(img_node.outputs["Color"], em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    except Exception:
        pass
report["textures"] = tex_report
print("TEXTURES recovered=%d missing=%d" % (tex_report["recovered"], len(tex_report["missing"])))
if tex_report["missing"]:
    print("  missing:", tex_report["missing"][:10])

# --- force T-pose via skeleton ---
def side_of(n):
    n2 = n.lower()
    if re.search(r'(^|[^a-z])(l|left)([^a-z]|$)|left|_l$|\.l$|^l_|l_|lft', n2) and not re.search(r'right|_r$|\.r$|^r_', n2):
        return 1
    if re.search(r'(^|[^a-z])(r|right)([^a-z]|$)|right|_r$|\.r$|^r_|r_|rgt', n2):
        return -1
    return 0

report["armatures"] = 0
arms = [o for o in sc.objects if o.type == "ARMATURE"]
report["armatures"] = len(arms)
for arm in arms:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    order = sorted(arm.pose.bones, key=lambda b: len(b.parent_recursive))
    for pb in order:
        n = pb.name.lower()
        if not re.fullmatch(
            r'(l|r)_(upperarm|lowerarm|hand)|(left|right)(arm|forearm|hand)|'
            r'(mixamorig:)?(left|right)(arm|forearm|hand)|'
            r'(upperarm|lowerarm|forearm|hand)[._](l|r)|bip01_[lr]_(upperarm|forearm|hand)', n):
            continue
        if side_of(pb.name) == 0:
            continue
        bpy.context.view_layer.update()
        mw = arm.matrix_world @ pb.matrix
        head = mw.translation
        kids = [k for k in pb.children
                if re.search(r'arm|hand', k.name, re.I)
                and not re.search(r'twt|twist|mus|drv|adr|pmp', k.name, re.I)]
        if re.search(r'hand', n) or not kids:
            continue
        tail = arm.matrix_world @ kids[0].head
        cur = (tail - head)
        if cur.length < 1e-6:
            continue
        sx = 1 if head.x > 0 else -1
        tgt = Vector((sx, 0, 0))
        q = cur.normalized().rotation_difference(tgt)
        R = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head)
        pb.matrix = arm.matrix_world.inverted() @ R @ mw
        report["posed"].append(pb.name)
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

# --- posed bbox from evaluated depsgraph ---
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for o in sc.objects:
    if o.type != "MESH":
        continue
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    pts += [e.matrix_world @ v.co for v in m.vertices]
    e.to_mesh_clear()
if not pts:
    raise SystemExit("no mesh vertices")
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
c = (mn + mx) / 2
d = mx - mn
maxd = max(d.x, d.y, d.z)
report["bbox"] = [list(mn), list(mx)]
print(f"BBOX dx={d.x:.3f} dy={d.y:.3f} dz={d.z:.3f}")

# --- white world, Cycles CPU ---
w = bpy.data.worlds.new("WhiteVoid")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (1, 1, 1, 1)
bg.inputs["Strength"].default_value = 1.0
sc.world = w
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 2
sc.cycles.use_denoising = False
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.view_settings.exposure = 0.0
sc.render.resolution_x = sc.render.resolution_y = RES
sc.render.resolution_percentage = 100
sc.render.film_transparent = False
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_end = 100 * maxd

# RigModels T7 FBX rips face -X (verified on Asuka pilot: +X side showed the back).
# Front cam sits on -X; side cam on -Y (character's left side when facing -X).
# Camera orientation is set via an explicit look-at matrix (euler/constraint
# approaches proved unreliable in background mode).
def look_at(eye, target, up):
    z = (eye - target).normalized()
    x = up.cross(z).normalized()
    y = z.cross(x)
    M = Matrix.Identity(4)
    M[0][0], M[1][0], M[2][0] = x[0], x[1], x[2]
    M[0][1], M[1][1], M[2][1] = y[0], y[1], y[2]
    M[0][2], M[1][2], M[2][2] = z[0], z[1], z[2]
    M[0][3], M[1][3], M[2][3] = eye[0], eye[1], eye[2]
    return M

UP = Vector((0, 0, 1))
views = {
    "front": (Vector((mn.x - 10 * maxd, c.y, c.z)), max(d.y, d.z)),
    "side": (Vector((c.x, mn.y - 10 * maxd, c.z)), max(d.x, d.z)),
}
for view, (eye, span) in views.items():
    cam.matrix_world = look_at(eye, Vector((c.x, c.y, c.z)), UP)
    cam.data.ortho_scale = span * 1.12
    sc.render.filepath = f"{OUTBASE}_{view}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", view, "ortho_scale=%.4f" % cam.data.ortho_scale)

json.dump(report, open(OUTBASE + "_report.json", "w"), indent=1, default=str)
print("DONE")
