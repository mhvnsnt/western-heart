"""tools/portrait-poses/render_portraits.py — headless Blender portrait renderer.

For each fighter: import the GLB, swing canonical bones from their OWN rest
directions to the preset's target directions (character space: x=left,
y=forward, z=up, mapped onto the model's measured facing), frame with a
consistent orthographic camera, render a 512x768 transparent PNG card.

These are AUTHORED portrait poses (owner-requested personality pass), NOT
teardown motion data — never present them as such (docs/RULES_NO_GUESSING.md).

Usage:
    xvfb-run -a env -u PYTHONPATH blender -b --factory-startup --python render_portraits.py -- \
        --manifest /tmp/portrait_manifest.json --presets presets.json \
        --outdir game/assets/portraits [--only pantera,demonio]

Manifest: JSON list of {"id": <fighter id>, "model": <glb path>, "preset": <preset name>}.
"""
import bpy, sys, math, os, json
from mathutils import Vector, Matrix, Quaternion, Euler

argv = sys.argv[sys.argv.index("--") + 1:]

def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default

manifest = json.load(open(arg("--manifest")))
presets = json.load(open(arg("--presets")))["presets"]
outdir = arg("--outdir")
only = set(arg("--only", "").split(",")) if arg("--only") else None
os.makedirs(outdir, exist_ok=True)

BONE_Y = Vector((0, 1, 0))   # bone local +Y = head->tail

def ordered_bones(arm):
    """Pose bones in parent-before-child order."""
    out, seen = [], set()
    def visit(b):
        if b.name in seen:
            return
        if b.parent:
            visit(b.parent)
        seen.add(b.name); out.append(b)
    for b in arm.pose.bones:
        visit(b)
    return out

def char_frame(arm):
    """Character basis (left, forward, up) in armature-LOCAL space, from bones.
    Left is unambiguous: the LeftArm shoulder sits to the character's left.
    forward = up x left (right-handed)."""
    pb = arm.pose.bones
    up = Vector((0, 0, 1))
    if "Head" in pb and "Hips" in pb:
        up = (pb["Head"].bone.head_local - pb["Hips"].bone.head_local)
        up = up.normalized() if up.length > 1e-6 else Vector((0, 0, 1))
    left = None
    if "LeftArm" in pb and "RightArm" in pb:
        l = pb["LeftArm"].bone.head_local - pb["RightArm"].bone.head_local
        l = l - up * l.dot(up)
        if l.length > 1e-6:
            left = l.normalized()
    if left is None:
        left = Vector((1, 0, 0)) - up * up.x
        left = left.normalized() if left.length > 1e-6 else Vector((1, 0, 0))
    fwd = up.cross(left).normalized()
    return left, fwd, up


def apply_preset(arm, spec, frame):
    """Pose via matrix_basis = B0 @ q, where q is solved from the bone's
    world frame M (columns = world dirs of bone-local X/Y/Z at rest).
    Verified exact (dbg6): the bone's world direction hits the target."""
    left, fwd, up = frame
    R_aw = arm.matrix_world.to_3x3()
    # world-space character axes
    lw, fw, uw = (R_aw @ left).normalized(), (R_aw @ fwd).normalized(), (R_aw @ up).normalized()

    def char_dir(d):
        return (lw * d[0] + fw * d[1] + uw * d[2]).normalized()

    def char_euler(e):
        rx, ry, rz = (math.radians(a) for a in e)
        return (Quaternion(uw, rz) @ Quaternion(fw, ry) @ Quaternion(lw, rx))

    bones = {b.name: b for b in arm.pose.bones}
    B0 = {b.name: b.matrix_basis.copy() for b in arm.pose.bones}
    spec_bones = spec.get("bones", {})
    for pbb in ordered_bones(arm):
        if pbb.name not in spec_bones:
            continue
        s = spec_bones[pbb.name]
        E = pbb.matrix.copy()  # current, includes posed parents
        M3 = (arm.matrix_world @ E).to_3x3()
        M = Matrix([ (M3 @ Vector((1, 0, 0))).normalized(),
                     (M3 @ Vector((0, 1, 0))).normalized(),
                     (M3 @ Vector((0, 0, 1))).normalized() ]).transposed()
        try:
            Minv = M.inverted()
        except Exception:
            continue
        pbb.rotation_mode = "QUATERNION"
        if "dir" in s:
            d1w = char_dir(s["dir"])
            v = (Minv @ d1w).normalized()
            q = BONE_Y.rotation_difference(v)
            if "twist" in s:
                q = q @ Quaternion(BONE_Y, math.radians(s["twist"]))
        elif "euler" in s:
            Qw = char_euler(s["euler"])
            q = (Minv @ Qw.to_matrix() @ M.to_3x3()).to_quaternion()
        else:
            continue
        pbb.matrix_basis = B0[pbb.name] @ q.to_matrix().to_4x4()
        bpy.context.view_layer.update()
    if "hips_loc" in spec:
        # whole-armature drop (no floor in the portrait; bounds-based framing)
        hb = bones.get("Hips")
        if hb:
            o_local = left * spec["hips_loc"][0] + fwd * spec["hips_loc"][1] + up * spec["hips_loc"][2]
            arm.location += R_aw @ o_local
    bpy.context.view_layer.update()

def render_one(entry):
    fid, model, preset_name = entry["id"], entry["model"], entry["preset"]
    spec = presets[preset_name]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=model)
    scn = bpy.context.scene
    arms = [o for o in scn.objects if o.type == "ARMATURE"]
    meshes = [o for o in scn.objects if o.type == "MESH"]
    if not arms or not meshes:
        print(f"PORTRAIT_SKIP {fid}: no armature/mesh")
        return False
    arm = max(arms, key=lambda a: len(a.pose.bones))
    # SKIN FIX (verified 2026-10-22 on demonio): the glTF importer bakes an
    # axis-correction into pose matrix_basis, so the "rest" pose is not the
    # skin bind pose — the armature modifier then displaces the mesh (demonio
    # shifted +8Y, rendered empty). Reset pose to true rest and re-bind with
    # fresh modifiers using the existing vertex groups (weights preserved).
    for pbb in arm.pose.bones:
        pbb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    for o in [o for o in scn.objects if o.type == "MESH"]:
        for m in [m for m in o.modifiers if m.type == "ARMATURE"]:
            o.modifiers.remove(m)
        mod = o.modifiers.new("portrait_bind", "ARMATURE")
        mod.object = arm
        mod.use_vertex_groups = True
        mod.use_bone_envelopes = False
    bpy.context.view_layer.update()
    frame = char_frame(arm)
    left, fwd, up = frame
    facing = (arm.matrix_world.to_3x3() @ fwd).normalized()
    # Camera needs a horizontal facing: the armature may carry a Y-up→Z-up
    # rotation making fwd tilt (demonio fwd.z=-0.99 local). Project to XY.
    facing = Vector((facing.x, facing.y, 0))
    if facing.length < 1e-6:
        facing = Vector((0, 1, 0))
    facing = facing.normalized()
    if entry.get("facing_flip"):
        facing = -facing
    apply_preset(arm, spec, frame)
    # BAKE: bpy.ops.render.render ignores armature-pose changes made via
    # matrix_basis (depsgraph quirk, verified 2026-10-22) — bake the deformed
    # meshes and render those instead. Deterministic.
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    # frame bounds from the baked verts (bound_box goes stale after o.data swap)
    bmin = Vector((1e9,) * 3); bmax = Vector((-1e9,) * 3)
    for o in [o for o in scn.objects if o.type == "MESH"]:
        if any(m.type == "ARMATURE" for m in o.modifiers):
            ev = o.evaluated_get(dg)
            baked = bpy.data.meshes.new_from_object(ev)
            o.modifiers.clear()
            o.data = baked
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            bmin = Vector((min(a, b) for a, b in zip(bmin, w)))
            bmax = Vector((max(a, b) for a, b in zip(bmax, w)))
    bpy.context.view_layer.update()
    center = (bmin + bmax) / 2
    size = bmax - bmin
    # camera: front, swung 18 deg for a 3/4 view
    az = math.radians(-18)
    fwd = facing.copy()
    fwd.rotate(Quaternion(Vector((0, 0, 1)), az))
    campos = center + fwd * 6.0 + Vector((0, 0, 0.15))
    cd = bpy.data.cameras.new("pcam")
    cd.type = "ORTHO"
    cd.sensor_fit = "HORIZONTAL"  # ortho_scale = horizontal width in world units
    # 2:3 card (512x768, aspect 0.667): ortho_scale is the horizontal width;
    # vertical height = scale/aspect. Fit horizontal extent and vertical (Z).
    _horiz = max(size.x, size.y)
    cd.ortho_scale = max(_horiz, size.z * (512 / 768)) * 1.15
    cam = bpy.data.objects.new("pcam", cd)
    scn.collection.objects.link(cam)
    cam.location = campos
    cam.rotation_euler = (center - campos).to_track_quat("-Z", "Y").to_euler()
    # Fix up: to_track_quat gives upside-down (camera Y = world -Z) for
    # horizontal views. Rebuild with explicit Z-up basis.
    _view = (center - campos).normalized()
    _up = Vector((0, 0, 1))
    _right = _view.cross(_up).normalized()
    _up2 = _right.cross(_view).normalized()
    _mat = Matrix((_right, _up2, -_view)).transposed()
    cam.rotation_euler = _mat.to_euler()
    scn.camera = cam
    # Cycles CPU: Workbench render aborts on this VM (no libEGL.so.1 for the
    # GL context); Cycles needs no GL. Consistent 3-point studio rig per card.
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = 24
    scn.cycles.use_denoising = True
    scn.render.film_transparent = True
    for lname, ltype, energy, loc in (
        ("pkey", "AREA", 900, (2.5, 3.5, 4.0)),
        ("prim", "AREA", 350, (-3.5, 1.5, 2.5)),
        ("pback", "AREA", 500, (0.0, -4.0, 3.0)),
    ):
        ld = bpy.data.lights.new(lname, type=ltype)
        ld.energy = energy
        ld.size = 3.0
        lo = bpy.data.objects.new(lname, ld)
        lo.location = center + Vector(loc)
        scn.collection.objects.link(lo)
        lo.rotation_euler = (Vector(loc) * -1).to_track_quat("-Z", "Y").to_euler()
    scn.world = bpy.data.worlds.new("pworld")
    scn.world.use_nodes = True
    scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.03, 0.045, 1.0)
    scn.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scn.render.resolution_x = 512
    scn.render.resolution_y = 768
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    out = os.path.join(outdir, f"{fid}.png")
    scn.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(f"PORTRAIT_OK {fid} <- {preset_name} ({model})")
    return True

ok, fail = 0, []
for e in manifest:
    if only and e["id"] not in only:
        continue
    try:
        if render_one(e):
            ok += 1
        else:
            fail.append(e["id"])
    except Exception as ex:
        print(f"PORTRAIT_FAIL {e['id']}: {ex}")
        fail.append(e["id"])
print(f"PORTRAIT_DONE ok={ok} fail={len(fail)} {fail}")
