"""GameRig bone-heat debug (Blender)

Same as gamerig_debug.py plus the parent-with-automatic-weights step and a per-bone vertex
count, to see which bones received weights.
Usage: blender -b -P tools/model-audit/gamerig_debug_heat.py -- MODEL.dec.glb

Part of the 2026-10-20/21 Claude combat-animation audit (see tools/TOOLS-INDEX.md and
docs/handoffs/CLAUDE_TO_MUSE_FIXES_2026-10-20.md). Read-only: never writes to the models.
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO/'tools/auto_rig/backends'))
import bpy, time
import gamerig_backend as G
inp = sys.argv[sys.argv.index('--') + 1]
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
for target in (8000, 12000, 16000, 24000):
    bpy.ops.object.select_all(action='DESELECT'); m.select_set(True); bpy.context.view_layer.objects.active = m
    bpy.ops.object.duplicate(); p = bpy.context.object
    r = p.modifiers.new('r', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = 0.008 / m.scale[0]; bpy.ops.object.modifier_apply(modifier='r')
    d = p.modifiers.new('d', 'DECIMATE'); d.ratio = target / len(p.data.polygons); bpy.ops.object.modifier_apply(modifier='d')
    bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); p.select_set(True); bpy.context.view_layer.objects.active = rig
    t = time.time(); bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    unw = sum(1 for v in p.data.vertices if not v.groups)
    print(f'T {target} faces={len(p.data.polygons)} unweighted={unw}/{len(p.data.vertices)} {time.time()-t:.1f}s')
    bpy.data.objects.remove(p, do_unlink=True)
