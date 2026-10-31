"""Blender (headless): apply 0xC8 frames with Kiloutre's applyRotationFromAnimdata and dump each body bone's pose
matrix_basis (local rotation relative to its rest, i.e. exactly what the applier wrote) plus rotation modes.
blender -b TekkenMannequin_no_ik.blend --python bl_basis.py -- <TekkenAnimHelper.py> <frames.json> <out.json>"""
import bpy, sys, json, importlib.util
argv = sys.argv[sys.argv.index('--') + 1:]
spec = importlib.util.spec_from_file_location('tah', argv[0]); tah = importlib.util.module_from_spec(spec); spec.loader.exec_module(tah)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
BONES = ['BASE', 'Spine1', 'Hip', 'Neck', 'Head', 'R_Shoulder', 'R_Arm', 'R_ForeArm', 'R_Hand', 'L_Shoulder', 'L_Arm',
         'L_ForeArm', 'L_Hand', 'R_UpLeg', 'R_Leg', 'R_Foot', 'L_UpLeg', 'L_Leg', 'L_Foot']
out = {'modes': {b: arm.pose.bones[b].rotation_mode for b in BONES}, 'frames': []}
for fr in json.load(open(argv[1]))['frames']:
    tah.applyRotationFromAnimdata(arm, fr)
    bpy.context.view_layer.update()
    out['frames'].append({b: [list(r) for r in arm.pose.bones[b].matrix_basis.to_3x3()] for b in BONES})
json.dump(out, open(argv[2], 'w'))
print('BASIS', len(out['frames']))
