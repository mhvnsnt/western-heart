"""Rebuild Pond (Tsuyu Asui) meshes from the clean source .blend, in the game frame, with 52-joint weights.
Run: b5.sh -b "/pond/src/Tsuyu Asui IK.blend" --python /ppp/pond/build_pond.py -- OUT.glb TWIN.glb
Output GLB is for grafting only (its skin is discarded; JOINTS are remapped by name onto the original skeleton).
"""
import bpy, bmesh, sys, mathutils, json
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree
argv = sys.argv[sys.argv.index('--') + 1:]
OUT, TWIN = argv[0], argv[1]
KEEP = {'tsuyu': 'Tsuyu', 'suit': 'Holo_001', 'gloves': 'Plane_003', 'boots': None,
        'Body_belt.dmx': 'Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Belt_Body_be',
        'Body_google.dmx': 'Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Googles_Body',
        'Body_mask.dmx': 'Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_Mask_Body_ma',
        'Hair': 'Tsuyu_Asui_MHA_rstar_Tsuyu_Asui_Tsuyu_Asui_SFM_mdl_hair_BodyHai'}
S = 2.4521072; T = Vector((0, 0.08413951, -0.02454758))
G = Matrix.Diagonal((1 / S, 1 / S, 1 / S, 1)) @ Matrix.Translation(-T)
report = {}
rig = bpy.data.objects['tsuyu rig']; rig.data.pose_position = 'REST'
dg = bpy.context.evaluated_depsgraph_get()
# record evaluated (masked) counts for verification
for n in KEEP:
    o = bpy.data.objects[n]; ev = o.evaluated_get(dg); m = ev.to_mesh(); report[n] = {'src_verts': len(o.data.vertices), 'eval_verts': len(m.vertices)}; ev.to_mesh_clear()
for n in KEEP:
    o = bpy.data.objects[n]
    report[n]['drivers'] = [d.data_path for d in o.animation_data.drivers] if o.animation_data else []
    if o.animation_data: o.animation_data_clear()
    if o.data.shape_keys and o.data.shape_keys.animation_data: o.data.shape_keys.animation_data_clear()
    report[n]['obj_loc'] = list(o.location)
# delete everything not kept (Penis, Bulge, widgets, templates, cameras, lights, rig)
for o in list(bpy.data.objects):
    if o.name not in KEEP:
        bpy.data.objects.remove(o, do_unlink=True)
for n in KEEP:
    o = bpy.data.objects[n]
    # 1) reproduce enabled Mask modifiers by deleting vertices
    masks = [m for m in o.modifiers if m.type == 'MASK']
    me = o.data
    drop = set()
    for m in masks:
        if not m.show_render: continue
        assert m.mode == 'VERTEX_GROUP', (n, m.name, m.mode)
        gi = o.vertex_groups[m.vertex_group].index
        ing = set(v.index for v in me.vertices if any(g.group == gi and g.weight > m.threshold for g in v.groups))
        out = ing if m.invert_vertex_group else set(range(len(me.vertices))) - ing
        drop |= out
        report[n].setdefault('masks', []).append((m.name, m.vertex_group, m.invert_vertex_group, m.threshold, len(out)))
    if drop:
        bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in drop], context='VERTS')
        bm.to_mesh(me); bm.free(); me.update()
    for m in list(o.modifiers): o.modifiers.remove(m)
    report[n]['kept_verts'] = len(me.vertices)
    # 2) into the game frame (rest pose = identity deform), unparent
    mw = o.matrix_world.copy(); o.parent = None
    me.transform(G @ mw, shape_keys=True); o.matrix_world = Matrix()
    me.shade_smooth()
    for ca in list(me.color_attributes): me.color_attributes.remove(ca)
    o.vertex_groups.clear()
# 3) weights from the shipped 52-joint twin
pre = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=TWIN)
imp = [o for o in bpy.data.objects if o not in pre]
arm = [o for o in imp if o.type == 'ARMATURE'][0]
twins = {o.name: o for o in imp if o.type == 'MESH'}
def twin_data(obj):
    dgm = bpy.context.evaluated_depsgraph_get()
    me = obj.data; mw = obj.matrix_world
    names = [g.name for g in obj.vertex_groups]
    kd = KDTree(len(me.vertices)); W = []
    for v in me.vertices:
        kd.insert(mw @ v.co, v.index); W.append([(names[g.group], g.weight) for g in v.groups if g.weight > 0])
    kd.balance(); return kd, W
def apply_w(o, kd, W, k=1, off=Vector()):
    dist = []
    for v in o.data.vertices:
        if k == 1:
            co, i, d = kd.find(v.co + off); acc = dict(W[i]); dist.append(d)
        else:
            hits = kd.find_n(v.co, k); acc = {}; tot = 0
            for co, i, d in hits:
                w = 1 / max(d, 1e-5); tot += w
                for nm, wt in W[i]: acc[nm] = acc.get(nm, 0) + wt * w
            acc = {a: b / tot for a, b in acc.items()}; dist.append(hits[0][2])
        top = sorted(acc.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top) or 1
        for nm, w in top:
            g = o.vertex_groups.get(nm) or o.vertex_groups.new(name=nm); g.add([v.index], w / s, 'REPLACE')
    dist.sort(); return {'max': dist[-1], 'p99': dist[int(len(dist) * .99)], 'median': dist[len(dist) // 2]}
cache = {}
for n, tw in KEEP.items():
    o = bpy.data.objects[n]
    src = twins[tw] if tw else twins['Tsuyu']
    if src.name not in cache: cache[src.name] = twin_data(src)
    kd, W = cache[src.name]
    # source object offset (e.g. Body_google.dmx loc z -0.1286) is in the source, absent from the shipped twin
    off = (G.to_3x3() @ Vector(report[n]['obj_loc'])) * -1 if tw else Vector()
    report[n]['twin_offset_comp'] = list(off)
    report[n]['weight_nn_dist'] = apply_w(o, kd, W, 1 if tw else 4, off)
    report[n]['weight_from'] = src.name
    mod = o.modifiers.new('Armature', 'ARMATURE'); mod.object = arm; o.parent = arm
# 4) materials: suit roughness = alpha of suit_Roughness (all 1.0) -> constant 1.0
suit = bpy.data.materials['suit']
for n in suit.node_tree.nodes:
    if n.type == 'BSDF_PRINCIPLED':
        for l in list(n.inputs['Roughness'].links): suit.node_tree.links.remove(l)
        n.inputs['Roughness'].default_value = 1.0
for o in list(bpy.data.objects):
    if o in imp and o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects: o.select_set(o.name in KEEP or o == arm)
for n in KEEP:
    o=bpy.data.objects[n]; o.hide_viewport=False; o.hide_render=False; o.hide_set(False); o.select_set(True)
assert all(bpy.data.objects[n].select_get() for n in KEEP), 'not all kept objects selectable'
print('SELECTED', [(o.name, o.type, o.select_get(), o.visible_get(), [c.name for c in o.users_collection]) for o in bpy.data.objects])
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_yup=True,
    export_skins=True, export_animations=False, export_morph=True, export_morph_normal=False,
    export_apply=False, export_image_format='AUTO', export_def_bones=False)
for n in KEEP: report[n]['shape_keys'] = len(bpy.data.objects[n].data.shape_keys.key_blocks) if bpy.data.objects[n].data.shape_keys else 0
json.dump(report, open(OUT + '.report.json', 'w'), indent=1, default=str)
print('REPORT', json.dumps(report, default=str))
