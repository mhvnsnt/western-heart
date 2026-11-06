"""author_placements_blender.py — author default TATTOO / SCAR placements per body
region on the 9 creation-suite template bodies, in Blender (bpy + BVHTree).

Owner instruction (2026-11-02): "find a way to use blender, show me it all, and do all the rest".

Run (from repo root; see run_author.sh, which does all three steps):
  node tools/creation-suite/decals/decode_glb.mjs /tmp/wh-decoded customization/templates/meshes/*.glb
  node -e "import('./game/js/decal-layers.js').then(m=>process.stdout.write(JSON.stringify(m.BODY_REGIONS)))" > /tmp/wh-regions.json
  blender -b --python tools/creation-suite/decals/author_placements_blender.py -- \
      /tmp/wh-decoded /tmp/wh-regions.json customization/templates/decal-placements.json [proof_dir]

What it does, per template, per region (regions come from game/js/decal-layers.js BODY_REGIONS,
so Blender and the game use ONE definition):
  1. imports the template GLB (meshopt stripped — Blender 4.3 can't read EXT_meshopt_compression),
  2. takes the SKIN material's faces whose verts are majority-weighted (dominant vertex group)
     to the region's bones, builds a BVHTree of them in rest pose,
  3. builds the region's UV canvas from the armature: v along the bone axis, u around it
     (u = 0 = front, +Z glTF / -Y Blender),
  4. casts from the bone axis at the PREFERRED (u, v) below; if the region's own skin is not
     there (e.g. the women's underwear mesh covers the skin at the bra band, the super
     heavyweight's neck folds are weighted to spine03), it searches outward in v then u and
     keeps the nearest hit that lands on the region's skin,
  5. writes u, v, the anchor point + normal (glTF Y-up metres), the hit bone, and size_m:
     the region's base decal size scaled by this body's measured girth (axis->skin distance)
     relative to the technician (cruiserweight) template.
Optionally renders proof PNGs (Cycles, CPU): each template front + back with a marker sphere
at every region anchor. WH_PROOF_ONLY=tid1,tid2 limits which templates render (time budget).
"""
import sys, os, json, math
sys.path.insert(0, '/tmp/bpylib')  # numpy for Blender's python when the distro lacks it (glTF importer needs it)
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index('--') + 1:]
DEC_DIR, REGIONS_JSON, OUT_JSON = argv[0], argv[1], argv[2]
PROOF_DIR = argv[3] if len(argv) > 3 else None
REGIONS = json.load(open(REGIONS_JSON))
TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
             'powerhouse-w', 'athletic-w', 'striker-w']
REF_TEMPLATE = 'technician'

# Authored preferred spots (u around the axis, v along it). WWE 2K CAW full-body canvas regions;
# spots chosen where tattoos / scars usually sit: upper chest, upper back, side of neck,
# cheek, mid upper arm, mid forearm, front thigh, shin-side calf.
PREFERRED = {
    'chest': (0.0, 0.64), 'back': (0.5, 0.62), 'neck': (0.0, 0.45), 'face': (0.07, 0.18),
    'upper_arm_L': (0.0, 0.5), 'upper_arm_R': (0.0, 0.5), 'forearm_L': (0.0, 0.5), 'forearm_R': (0.0, 0.5),
    'thigh_L': (0.0, 0.45), 'thigh_R': (0.0, 0.45), 'calf_L': (0.0, 0.4), 'calf_R': (0.0, 0.4),
}
V_STEPS = [0, 0.04, -0.04, 0.08, -0.08, 0.12, -0.12, 0.16, -0.16, 0.2, -0.2, 0.25, -0.25, 0.3, -0.3]
U_STEPS = [0, 0.03, -0.03, 0.06, -0.06, 0.1, -0.1]

g2b = lambda p: Vector((p[0], -p[2], p[1]))         # glTF (Y up, +Z front) -> Blender (Z up, -Y front)
b2g = lambda v: [round(v.x, 5), round(v.z, 5), round(-v.y, 5)]


def load(tid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(DEC_DIR, tid + '.glb'))
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    body = max((o for o in bpy.data.objects if o.type == 'MESH' and o.vertex_groups), key=lambda o: len(o.data.vertices))
    return arm, body


def bone_heads(arm):
    return {b.name: arm.matrix_world @ b.head_local for b in arm.data.bones}


def region_bvh(body, bones):
    me = body.data
    skin_mi = [i for i, m in enumerate(me.materials) if m and 'skin' in m.name.lower()]
    gname = {g.index: g.name for g in body.vertex_groups}
    dom = []
    for v in me.vertices:
        best = max(v.groups, key=lambda g: g.weight, default=None)
        dom.append(gname.get(best.group) if best else None)
    mw = body.matrix_world
    verts = [mw @ v.co for v in me.vertices]
    polys, owner = [], []
    for p in me.polygons:
        if p.material_index not in skin_mi:
            continue
        if sum(1 for vi in p.vertices if dom[vi] in bones) * 3 >= len(p.vertices) * 2 - 0.01 or \
           (len(p.vertices) == 3 and sum(1 for vi in p.vertices if dom[vi] in bones) >= 2):
            polys.append(list(p.vertices)); owner.append(p.index)
    return BVHTree.FromPolygons(verts, polys), polys, verts, dom


def frame(heads, R):
    a = heads[R['axis'][0]]
    if R['axis'][1]:
        b = heads[R['axis'][1]]
    else:
        n = heads.get('neck', a - Vector((0, 0, 0.1)))
        b = a + (a - n).normalized() * R['axis'][2]
    axis = (b - a).normalized()
    front_g = Vector((0, -1, 0))  # glTF +Z front
    front = front_g - axis * axis.dot(front_g)
    front = front.normalized() if front.length > 1e-4 else Vector((0, 0, 1))
    # side = cross(axis, front) in glTF handedness; Blender's axis swap is a proper rotation, so it carries over
    side = axis.cross(front)
    return a, b, axis, front, side


def cast(bvh, a, b, front, side, u, v):
    ang = 2 * math.pi * u
    d = (front * math.cos(ang) + side * math.sin(ang)).normalized()
    o = a + (b - a) * v
    loc, nrm, idx, dist = bvh.ray_cast(o, d)
    return (loc, nrm, idx, dist, o, d) if loc is not None else None


def main():
    out = {'_doc': 'Default tattoo/scar placements per body region on the 9 template bodies. Authored in Blender 4.3 by '
                   'tools/creation-suite/decals/author_placements_blender.py (BVHTree ray cast from the region bone axis). '
                   'u = around the bone axis (0 front, 0.5 back), v = along it (0 start joint, 1 end joint); anchor/normal in '
                   'glTF space (Y up, +Z front, metres, bind pose); size_m = region base decal size x this body\'s measured '
                   'girth / technician girth. Read by game/js/decal-layers.js defaultPlacement() and checked by '
                   'test/decal-layers.test.mjs against the game\'s own JS resolver.',
           'blender': bpy.app.version_string, 'ref_template': REF_TEMPLATE, 'templates': {}}
    girth_ref = {}
    results = {}
    for tid in [REF_TEMPLATE] + [t for t in TEMPLATES if t != REF_TEMPLATE]:
        arm, body = load(tid)
        heads = bone_heads(arm)
        regs = {}
        for R in REGIONS:
            bvh, polys, verts, dom = region_bvh(body, set(R['bones']))
            a, b, axis, front, side = frame(heads, R)
            pu, pv = PREFERRED[R['key']]
            hit = None
            for dv in V_STEPS:
                for du in U_STEPS:
                    u, v = (pu + du) % 1.0, min(1.0, max(0.0, pv + dv))
                    h = cast(bvh, a, b, front, side, u, v)
                    if h:
                        hit = (u, v, h); break
                if hit:
                    break
            if not hit:
                regs[R['key']] = None
                print(f'[author] {tid} {R["key"]}: NO HIT on region skin', flush=True)
                continue
            u, v, (loc, nrm, idx, dist, o, d) = hit
            p = polys[idx]
            vi = min(p, key=lambda k: (verts[k] - loc).length)
            if nrm.dot(d) < 0:
                nrm = -nrm
            if tid == REF_TEMPLATE:
                girth_ref[R['key']] = dist
            girth = dist / max(girth_ref.get(R['key'], dist), 1e-6)
            regs[R['key']] = {
                'u': round(u, 4), 'v': round(v, 4),
                'anchor': b2g(loc), 'normal': [round(x, 4) for x in b2g(nrm)],
                'bone': dom[vi], 'girth_m': round(dist, 4),
                'size_m': round(R['size'] * max(0.75, min(1.6, girth)), 4),
                'searched': not (abs(u - pu) < 1e-9 and abs(v - pv) < 1e-9),
            }
        out['templates'][tid] = {'regions': regs}
        results[tid] = (arm, body)
        if PROOF_DIR and (not os.environ.get('WH_PROOF_ONLY') or tid in os.environ['WH_PROOF_ONLY'].split(',')):
            render_proof(tid, regs)
        print(f'[author] {tid}: ' + ', '.join(f"{k}={'ok' if r else 'MISS'}" for k, r in regs.items()), flush=True)
    out['templates'] = {t: out['templates'][t] for t in TEMPLATES}
    os.makedirs(os.path.dirname(os.path.abspath(OUT_JSON)), exist_ok=True)
    with open(OUT_JSON, 'w') as f:
        json.dump(out, f, indent=1)
    print('[author] wrote', OUT_JSON)


COLORS = [(1, .2, .2), (1, .6, .1), (1, 1, .2), (.3, 1, .3), (.2, .9, 1), (.3, .4, 1), (.8, .3, 1),
          (1, .3, .7), (.9, .9, .9), (.5, 1, .8), (1, .8, .6), (.6, .6, 1)]


def render_proof(tid, regs):
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = 24
    scn.cycles.device = 'CPU'
    scn.cycles.use_denoising = False
    scn.render.resolution_x, scn.render.resolution_y = 360, 640
    scn.render.film_transparent = False
    # MB-Lab's imported skin shader renders as speckle under CPU Cycles here: proof renders use plain clay
    clay = bpy.data.materials.new('clay'); clay.use_nodes = True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.62, 0.55, 0.5, 1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.7
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and not o.name.startswith('mk_') and not o.name.startswith('decal_'):
            if o.name == 'Icosphere':
                o.hide_render = True; continue
            for i in range(len(o.material_slots)):
                if not (o.material_slots[i].material and o.material_slots[i].material.name.startswith('decal_')):
                    o.material_slots[i].material = clay
    world = bpy.data.worlds.new('w'); scn.world = world; world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (0.05, 0.06, 0.09, 1)
    world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
    for i, (k, r) in enumerate(regs.items()):
        if not r:
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=g2b(r['anchor']))
        s = bpy.context.active_object; s.name = 'mk_' + k
        m = bpy.data.materials.new('mk_' + k); m.use_nodes = True
        bsdf = m.node_tree.nodes['Principled BSDF']
        bsdf.inputs['Base Color'].default_value = (*COLORS[i % len(COLORS)], 1)
        bsdf.inputs['Emission Color'].default_value = (*COLORS[i % len(COLORS)], 1)
        bsdf.inputs['Emission Strength'].default_value = 2.0
        s.data.materials.append(m)
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(60), 0, math.radians(20))); bpy.context.active_object.data.energy = 3.5
    bpy.ops.object.light_add(type='SUN', rotation=(math.radians(-60), 0, math.radians(-20))); bpy.context.active_object.data.energy = 2.5
    cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data)
    scn.collection.objects.link(cam); scn.camera = cam
    cam_data.type = 'ORTHO'; cam_data.ortho_scale = 2.05
    for view, (loc, rot) in {'front': ((0, -4, 0.95), (math.pi / 2, 0, 0)),
                             'back': ((0, 4, 0.95), (math.pi / 2, 0, math.pi))}.items():
        cam.location = loc; cam.rotation_euler = rot
        scn.render.filepath = os.path.join(PROOF_DIR, f'{tid}_{view}.png')
        bpy.ops.render.render(write_still=True)


main()
