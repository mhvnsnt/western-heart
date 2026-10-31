#!/usr/bin/env python3
"""T7 format-200 (0xC8) CONTROL TEST - run INSIDE Blender's Python.

Reproduces the community control test for Kiloutre's BlenderTekkenAnimationImporter
0xC8 -> skeleton path: loads Koenji's T7 mannequin (.blend, NO autoexec), applies a
0xC8 clip with the plugin's own Animation0xC8 parser + AnimationImporter keyframing
code, reads back posed joint positions for every frame, and (optionally) renders
proof frames.

Safety: the .blend is opened without --enable-autoexec; embedded text blocks/drivers
are only inspected (probe mode), never executed. The plugin modules were inspected
before first use (pure animation math + bpy pose writes; no network/subprocess/eval).

Inputs (env vars):
  T7_MANNEQUIN   path to TekkenMannequin_no_ik.blend (Koenji; MEGA link in Kiloutre's README)
  T7_PLUGIN_DIR  dir containing the BlenderTekkenAnimationImporter package
  T7_CLIP_BIN    clip in Kiloutre layout (little-endian) - see t7_c8_stance_bake.py --prep
  T7_OUT         output dir for readback.json + renders
Usage:
  xvfb-run -a env -u PYTHONPATH <blender> -b "$T7_MANNEQUIN" --python t7_c8_control_test.py
Blender on this VM has no libEGL: renders use CYCLES CPU (EEVEE aborts).
"""
import bpy, sys, os, json

sys.path.insert(0, os.environ['T7_PLUGIN_DIR'])
OUT = os.environ.get('T7_OUT', '.')
BONES = ['BODY_SCALE__group','BASE','Hip','Spine1','Spine2','Neck','Head','ATH_Head_Top',
         'R_Shoulder','R_Arm','R_ForeArm','R_Hand','L_Shoulder','L_Arm','L_ForeArm','L_Hand',
         'R_UpLeg','R_Leg','R_Foot','R_Toe','L_UpLeg','L_Leg','L_Foot','L_Toe',
         'ATH_L_Foot_Btm','ATH_R_Foot_Btm','ATH_L_Toe_Btm','ATH_R_Toe_Btm']

# probe: report embedded scripts (never run them - autoexec stays off)
print('EMBEDDED TEXTS:', [t.name for t in bpy.data.texts])
arm = bpy.data.objects['Armature']
print('DRIVERS:', [d.data_path for d in arm.animation_data.drivers] if arm.animation_data else [])

for ob in bpy.data.objects:
    if ob.name.endswith('.001'):
        ob.hide_render = True

from BlenderTekkenAnimationImporter.Animation0xC8 import Animation0xC8
from BlenderTekkenAnimationImporter.AnimationImporter import AnimationImporter

anim = Animation0xC8(open(os.environ['T7_CLIP_BIN'], 'rb').read())
print('PARSED frames:', len(anim.AnimationFrames))
# Real plugin code path (insert_key_frames_for_animation never touches self)
AnimationImporter.insert_key_frames_for_animation(None, anim)

meshes = [ob for ob in bpy.data.objects if ob.type == 'MESH' and not ob.name.endswith('.001')]
def mesh_minmax_z(frame):
    bpy.context.scene.frame_set(frame)
    dg = bpy.context.evaluated_depsgraph_get()
    mn, mx = 1e9, -1e9
    for ob in meshes:
        ev = ob.evaluated_get(dg); me = ev.to_mesh(); mw = ev.matrix_world
        for v in me.vertices:
            z = (mw @ v.co).z; mn = min(mn, z); mx = max(mx, z)
        ev.to_mesh_clear()
    return round(mn, 4), round(mx, 4)

readback = []
for f in range(1, len(anim.AnimationFrames) + 1):
    bpy.context.scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg); mw = ev.matrix_world
    rec = {'frame': f, 'joints': {}}
    for bn in BONES:
        pb = ev.pose.bones[bn]
        rec['joints'][bn] = {'head': [round(v, 4) for v in (mw @ pb.head)],
                             'tail': [round(v, 4) for v in (mw @ pb.tail)]}
    rec['mesh_minmax_z'] = mesh_minmax_z(f)
    readback.append(rec)
json.dump(readback, open(os.path.join(OUT, 'readback.json'), 'w'))
print('READBACK saved', len(readback), 'frames')
print('CONTROL_TEST_DONE')
