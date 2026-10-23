import bpy, sys, os, math
from mathutils import Vector
# Phase 11 Job 2: composite builder with explicit per-pair anchor.
# Usage: composite_ab.py outdir glbdir -- pairs are hardcoded below as
# (body, head, anchorY, anchorZ, tag). Head roots translated by the
# glTF->Blender mapped vector (0, -anchorZ, anchorY) as in phase 10.
# Prints evaluated bounds of body-only and combined scenes for the record.
argv = sys.argv[sys.argv.index('--') + 1:]
outdir, glbdir = argv[0], argv[1]
pairs = [
    # A/B for floaters + marginal: tag nb = neck-base (phase-10), hj = head-joint
    ("chrone-pkg10", "chrtwo-pkg09", 0.398, -0.020, "nb"),
    ("chrone-pkg10", "chrtwo-pkg09", 0.478, -0.020, "hj"),
    ("chrone-pkg10", "chrtwo-pkg33", 0.398, -0.024, "nb"),
    ("chrone-pkg10", "chrtwo-pkg33", 0.478, -0.024, "hj"),
    ("chrone-pkg17", "chrtwo-pkg21", 0.388, -0.025, "nb"),
    ("chrone-pkg17", "chrtwo-pkg21", 0.468, -0.025, "hj"),
    ("chrtwo-pkg50", "chrtwo-pkg25", 0.397, -0.041, "nb"),
    ("chrtwo-pkg50", "chrtwo-pkg25", 0.477, -0.041, "hj"),
    ("chrone-pkg00", "chrtwo-pkg18", 0.406, -0.021, "nb"),
    ("chrone-pkg00", "chrtwo-pkg18", 0.486, -0.021, "hj"),
    ("chrone-pkg17", "chrtwo-pkg07", 0.388, -0.025, "nb"),
    ("chrone-pkg17", "chrtwo-pkg07", 0.468, -0.025, "hj"),
]
BODYDIR = "/home/hatch/workspace/_doa4p2-scratch/p8/glb-chrone/extracted"
BODY2 = "/home/hatch/workspace/_doa4p2-scratch/p9/glb-chrtwo/extracted"
SAN = "/home/hatch/workspace/_doa4p2-scratch/p10/sanitized"
def bodypath(b):
    p = os.path.join(BODYDIR, b + "-skinned.glb")
    return p if os.path.exists(p) else os.path.join(BODY2, b + "-skinned.glb")
for body, head, ty, tz, tag in pairs:
    name = "%s+%s-%s" % (body, head, tag)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=bodypath(body))
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(SAN, head + "-skinned.glb"))
    t = Vector((0.0, -tz, ty))
    for o in bpy.data.objects:
        if o.name not in before and o.parent is None:
            o.location += t
    glbpath = os.path.join(glbdir, name + ".glb")
    bpy.ops.export_scene.gltf(filepath=glbpath, export_yup=True)
    print("EXPORTED", glbpath, flush=True)
    w = bpy.data.worlds.new('W') if not bpy.data.worlds else bpy.data.worlds[0]
    bpy.context.scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.32, 0.32, 0.32, 1); bg.inputs[1].default_value = 0.8
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in bpy.data.objects:
        if o.type == 'MESH':
            eo = o.evaluated_get(dg); m = eo.to_mesh(); pts += [eo.matrix_world @ v.co for v in m.vertices]
    def pct(vals, q):
        s = sorted(vals); return s[min(len(s) - 1, max(0, int(q * len(s))))]
    mn = Vector((pct([q[i] for q in pts], 0.002) for i in range(3))); mx = Vector((pct([q[i] for q in pts], 0.998) for i in range(3)))
    c = (mn + mx) / 2; size = max((mx - mn)[i] for i in range(3)) or 1.0
    cam = bpy.data.cameras.new('c'); cam.clip_end = 1000
    co = bpy.data.objects.new('cam', cam); bpy.context.scene.collection.objects.link(co)
    co.location = (c.x, c.y - size * 1.45, c.z); co.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = co
    lt = bpy.data.lights.new('s', 'SUN'); lt.energy = 4
    lo = bpy.data.objects.new('sun', lt); bpy.context.scene.collection.objects.link(lo); lo.rotation_euler = (math.radians(50), 0, math.radians(30))
    lt2 = bpy.data.lights.new('f', 'SUN'); lt2.energy = 1.2
    lo2 = bpy.data.objects.new('fill', lt2); bpy.context.scene.collection.objects.link(lo2); lo2.rotation_euler = (math.radians(70), 0, math.radians(-120))
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 8; sc.cycles.use_denoising = True; sc.cycles.device = 'CPU'
    sc.render.resolution_x = 512; sc.render.resolution_y = 640
    sc.render.filepath = os.path.join(outdir, "p11-composite-" + name + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath, flush=True)
print("BATCH DONE")
