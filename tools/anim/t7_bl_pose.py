"""Blender side of tools/anim/t7_c8_stance_bake.py (run headless, never imported by the game).

Poses Koenji's TekkenMannequin with Kiloutre's applyRotationFromAnimdata (BlenderTekkenDirect, TekkenAnimHelper.py:
the community path that applies T7 0xC8 frames) and dumps, per frame, each T7 joint's world rotation (3x3) and head
position, plus the rest pose.

  blender -b TekkenMannequin_no_ik.blend --python tools/anim/t7_bl_pose.py -- <TekkenAnimHelper.py> <frames.json> <out.json>
"""
import bpy, sys, json, importlib.util

argv = sys.argv[sys.argv.index('--') + 1:]
helper, frames_path, out_path = argv[0], argv[1], argv[2]
spec = importlib.util.spec_from_file_location('tah', helper)
tah = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tah)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
JOINTS = ['BODY_SCALE__group', 'BASE', 'Spine1', 'Spine2', 'Neck', 'Head', 'Hip', 'R_Shoulder', 'R_Arm', 'R_ForeArm',
          'R_Hand', 'L_Shoulder', 'L_Arm', 'L_ForeArm', 'L_Hand', 'R_UpLeg', 'R_Leg', 'R_Foot', 'L_UpLeg', 'L_Leg',
          'L_Foot', 'R_Toe', 'L_Toe']
MW = arm.matrix_world


def rest_of(name):
    b = arm.data.bones[name]
    m = MW @ b.matrix_local
    return {'rot': [list(r[:3]) for r in m.to_3x3()], 'head': list(MW @ b.head_local), 'tail': list(MW @ b.tail_local)}


def posed_of(name):
    pb = arm.pose.bones[name]
    m = MW @ pb.matrix
    return {'rot': [list(r[:3]) for r in m.to_3x3()], 'head': list(MW @ pb.head), 'tail': list(MW @ pb.tail)}


have = [j for j in JOINTS if j in arm.pose.bones]
missing = [j for j in JOINTS if j not in arm.pose.bones]
if missing:
    raise SystemExit('mannequin lacks joints: %s' % missing)
out = {'armature': arm.name, 'joints': have, 'rest': {j: rest_of(j) for j in have}, 'frames': []}
for fr in json.load(open(frames_path))['frames']:
    tah.applyRotationFromAnimdata(arm, fr)
    bpy.context.view_layer.update()
    out['frames'].append({j: posed_of(j) for j in have})
json.dump(out, open(out_path, 'w'))
print('POSED', len(out['frames']), 'frames;', len(have), 'joints')
