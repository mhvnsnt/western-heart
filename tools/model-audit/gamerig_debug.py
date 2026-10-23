"""GameRig generate debug (Blender)

Runs normalize_and_face + metarig fit + GameRig generate on one decoded GLB and prints mesh /
rig transforms. Used to find the -74 deg facing-estimate failure behind the empty bone heat.
Usage: blender -b -P tools/model-audit/gamerig_debug.py -- MODEL.dec.glb

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys, json
sys.path.insert(0, str(REPO/'tools/auto_rig/backends'))
import bpy
import gamerig_backend as G
argv = sys.argv[sys.argv.index('--') + 1:]
inp = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
G.install_gamerig(G.DEFAULT_GAMERIG_DIR); G.enable_gamerig(); G.apply_blender402_shim()
bpy.ops.import_scene.gltf(filepath=inp)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
stats = G.normalize_and_face(meshes, 1.8, '+X')
bpy.ops.object.armature_human_metarig_add(); meta = bpy.context.object
G.strip_face(meta); G.fit_metarig(meta, stats)
bpy.ops.object.select_all(action='DESELECT'); meta.select_set(True); bpy.context.view_layer.objects.active = meta
bpy.ops.pose.gamerig_generate()
rig = max([o for o in bpy.context.scene.objects if o.type == 'ARMATURE' and o != meta], key=lambda o: len(o.data.bones))
G.strip_to_deform(rig)
m = meshes[0]
print('MESH', m.name, 'scale', tuple(m.scale), 'rot', tuple(m.rotation_euler), 'loc', tuple(m.location), 'parent', m.parent)
print('RIG', rig.name, 'scale', tuple(rig.scale), 'loc', tuple(rig.location), 'bones', len(rig.data.bones))
# where are key bones vs mesh bbox (world)
import mathutils
bb = [m.matrix_world @ mathutils.Vector(c) for c in m.bound_box]
print('MESH BBOX', [round(min(v[i] for v in bb),3) for i in range(3)], [round(max(v[i] for v in bb),3) for i in range(3)])
for bn in ['DEF-spine', 'DEF-spine.005', 'DEF-upper_arm.L', 'DEF-hand.L', 'DEF-thigh.L', 'DEF-foot.L']:
    b = rig.data.bones.get(bn)
    if b: print('BONE', bn, [round(x,3) for x in (rig.matrix_world @ b.head_local)], [round(x,3) for x in (rig.matrix_world @ b.tail_local)])
# Variation A: apply scale/rotation on mesh, make proxy, heat
bpy.ops.object.select_all(action='DESELECT'); m.select_set(True); bpy.context.view_layer.objects.active = m
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.duplicate(); proxy = bpy.context.object
r = proxy.modifiers.new('r', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = 0.012; bpy.ops.object.modifier_apply(modifier='r')
print('PROXY faces', len(proxy.data.polygons))
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); proxy.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
unw = sum(1 for v in proxy.data.vertices if not v.groups)
print('A applied-scale proxy heat: unweighted', unw, 'of', len(proxy.data.vertices), 'groups', len(proxy.vertex_groups))
# Variation B: envelope weights as comparison
# Variation C: keep only the largest connected component of the proxy
import bmesh
for g in list(proxy.vertex_groups): proxy.vertex_groups.remove(g)
for md in list(proxy.modifiers): proxy.modifiers.remove(md)
proxy.parent = None
bm = bmesh.new(); bm.from_mesh(proxy.data); bm.verts.ensure_lookup_table()
seen = set(); comps = []
for v in bm.verts:
    if v.index in seen: continue
    stack = [v]; comp = []; seen.add(v.index)
    while stack:
        x = stack.pop(); comp.append(x)
        for e in x.link_edges:
            o = e.other_vert(x)
            if o.index not in seen: seen.add(o.index); stack.append(o)
    comps.append(comp)
comps.sort(key=len, reverse=True)
print('C components', len(comps), 'sizes', [len(c) for c in comps[:8]])
bmesh.ops.delete(bm, geom=[v for c in comps[1:] for v in c], context='VERTS')
bm.to_mesh(proxy.data); bm.free()
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); proxy.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
unw = sum(1 for v in proxy.data.vertices if not v.groups)
print('C largest-component heat: unweighted', unw, 'of', len(proxy.data.vertices))
# Variation D: armature forced to REST position + constraints removed from DEF bones
for g in list(proxy.vertex_groups): proxy.vertex_groups.remove(g)
for md in list(proxy.modifiers): proxy.modifiers.remove(md)
ncon = 0
for pb in rig.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c); ncon += 1
    pb.matrix_basis.identity()
rig.data.pose_position = 'REST'
bpy.context.view_layer.update()
print('D removed constraints', ncon)
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); proxy.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
unw = sum(1 for v in proxy.data.vertices if not v.groups)
print('D rest+noconstraint heat: unweighted', unw, 'of', len(proxy.data.vertices))
# Variation E: decimate proxy to ~5k faces
for g in list(proxy.vertex_groups): proxy.vertex_groups.remove(g)
for md in list(proxy.modifiers): proxy.modifiers.remove(md)
bpy.ops.object.select_all(action='DESELECT'); proxy.select_set(True); bpy.context.view_layer.objects.active = proxy
d = proxy.modifiers.new('d', 'DECIMATE'); d.ratio = 5000 / max(1, len(proxy.data.polygons)); bpy.ops.object.modifier_apply(modifier='d')
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); proxy.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
unw = sum(1 for v in proxy.data.vertices if not v.groups)
print('E 5k-face heat: unweighted', unw, 'of', len(proxy.data.vertices))
