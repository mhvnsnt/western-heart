"""Blender (headless): apply 69-value T7 frames to Koenji's TekkenMannequin with Kiloutre's
applyRotationFromAnimdata and dump world joint positions.
blender -b <mannequin.blend> --python bl_apply.py -- <frames.json> <out.json>
frames.json: {"frames": [[69 floats], ...]}"""
import bpy, sys, json, importlib.util
argv = sys.argv[sys.argv.index('--') + 1:]
spec = importlib.util.spec_from_file_location('tah', '/tmp/claude-0/-home-user-western-heart/0e2ac5b9-e898-5469-94b9-4c1c13f1e581/scratchpad/ext/BlenderTekkenDirect/TekkenAnimHelper.py')
tah = importlib.util.module_from_spec(spec); spec.loader.exec_module(tah)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
JOINTS = ['BASE', 'Spine1', 'Spine2', 'Neck', 'Head', 'Hip', 'R_Shoulder', 'R_Arm', 'R_ForeArm', 'R_Hand', 'L_Shoulder',
          'L_Arm', 'L_ForeArm', 'L_Hand', 'R_UpLeg', 'R_Leg', 'R_Foot', 'L_UpLeg', 'L_Leg', 'L_Foot']
frames = json.load(open(argv[0]))['frames']
out = {'rotation_modes': {b: arm.pose.bones[b].rotation_mode for b in JOINTS if b in arm.pose.bones}, 'frames': []}
for fr in frames:
    tah.applyRotationFromAnimdata(arm, fr)
    bpy.context.view_layer.update()
    pos = {}
    for b in JOINTS:
        pb = arm.pose.bones.get(b)
        if pb is None: continue
        h = arm.matrix_world @ pb.head; t = arm.matrix_world @ pb.tail
        pos[b] = [list(h), list(t)]
    out['frames'].append(pos)
json.dump(out, open(argv[1], 'w'))
print('DONE', len(out['frames']))
