#!/usr/bin/env python3
"""Bake King's real T7 stance (nakg_kg2kam, format-200/0xC8) directly onto Pantera's
in-game rig as a wh-anim/1 asset (t3-bank layout). Two modes:

1) PREP (plain python3, no Blender):
     python3 t7_c8_pantera_stance_bake.py --prep --arc kinrotsm.arc --out nakg_kg2kam_0xC8.bin
   Extracts the clip (kin section 0, rel offset 2334372, 16660 B, sha256
   1e0c6b34...) and re-serializes it field-by-field from the proven big-endian
   MOTA layout into the little-endian layout Kiloutre's importer parses
   (struct "<2B H 24I" header + "<69f" frames). Lossless: same fields, same order.

2) BAKE (inside Blender's Python, mannequin .blend open):
     xvfb-run -a env -u PYTHONPATH <blender> -b "$T7_MANNEQUIN" --python t7_c8_pantera_stance_bake.py
   Env: T7_PLUGIN_DIR, T7_CLIP_BIN, T7_PANTERA_GLB, T7_OUT (verification json),
        T7_ASSET_OUT (final wh-anim json path).
   Method: pose Koenji's mannequin with the plugin (verified 0xC8 path), then
   transfer each mapped bone's WORLD orientation onto Pantera's rig
   (Q_wh = Q_mq_pose * Q_mq_rest^-1 * Q_wh_rest), Root translation from the
   mannequin Hip trajectory scaled by rig height, per-frame grounding pinning
   the lower foot joint to its rest height. Export converts Blender bone
   frames to glTF joint frames via Rg = C * Rb * Rb_rest^-1 * C^-1 so the
   rest pose exports as exact identity (verified: 0.0 rad deviation).
   Bone map note: mannequin Spine1 sits at pelvis-top -> WH Spine (NOT Chest);
   WH Chest and ToeBases have no T7 body channel and stay identity.
   Gotcha: the Pantera GLB ships its T3 clips as NLA tracks + an active
   action, and the importer leaves a pose in the basis values - clear
   animation_data AND reset every pose bone before posing, or the NLA stack
   silently overrides the transfer.
   Renders use CYCLES CPU (no libEGL on this VM; EEVEE aborts).
"""
import os, sys, json, math

if '--prep' in sys.argv:
    import struct, hashlib, argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--prep', action='store_true')
    ap.add_argument('--arc', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--section-offset', type=int, default=64)
    ap.add_argument('--rel-offset', type=int, default=2334372)
    ap.add_argument('--size', type=int, default=16660)
    a = ap.parse_args()
    data = open(a.arc, 'rb').read()
    clip = data[a.section_offset + a.rel_offset: a.section_offset + a.rel_offset + a.size]
    assert hashlib.sha256(clip).hexdigest() == \
        '1e0c6b34ca537ee459edfd2d8313d47b09910a3be3c8767b32d6e7a99bb9aeb0', 'clip sha mismatch'
    w, n = struct.unpack('>HH', clip[:4]); assert (w, n) == (200, 23)
    tf = struct.unpack('>I', clip[4:8])[0]
    fields = struct.unpack('>23I', clip[8:100])
    vals = struct.unpack('>%df' % (tf * n * 3), clip[100:])
    out = struct.pack('<HHI', w, n, tf) + struct.pack('<23I', *fields) + struct.pack('<%df' % (tf * n * 3), *vals)
    open(a.out, 'wb').write(out)
    print('PREP ok: format', w, 'tracks', n, 'frames', tf, '->', a.out)
    sys.exit(0)

# ---------------- BAKE mode (Blender) ----------------
import bpy
sys.path.insert(0, os.environ['T7_PLUGIN_DIR'])
from mathutils import Matrix, Vector, Quaternion

OUT = os.environ.get('T7_OUT', '.')
for ob in bpy.data.objects:
    if ob.name.endswith('.001'): ob.hide_render = True
arm_mq = bpy.data.objects['Armature']

before = set(o.name for o in bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.environ['T7_PANTERA_GLB'])
arm_wh = next(o for o in bpy.data.objects if o.name not in before and o.type == 'ARMATURE')
assert all(abs(s - 1.0) < 1e-6 for s in arm_wh.scale)
arm_wh.animation_data_clear()
for pb in arm_wh.pose.bones:
    pb.location = (0, 0, 0); pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((1, 0, 0, 0)); pb.scale = (1, 1, 1)
bpy.context.view_layer.update()

MAP = {'Root': 'BASE', 'Hips': 'Hip', 'Spine': 'Spine1', 'Neck': 'Neck', 'Head': 'Head',
       'RightShoulder': 'R_Shoulder', 'RightArm': 'R_Arm', 'RightForeArm': 'R_ForeArm', 'RightHand': 'R_Hand',
       'LeftShoulder': 'L_Shoulder', 'LeftArm': 'L_Arm', 'LeftForeArm': 'L_ForeArm', 'LeftHand': 'L_Hand',
       'RightUpLeg': 'R_UpLeg', 'RightLeg': 'R_Leg', 'RightFoot': 'R_Foot',
       'LeftUpLeg': 'L_UpLeg', 'LeftLeg': 'L_Leg', 'LeftFoot': 'L_Foot'}
WH_BONES = ['Root', 'Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand',
            'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'LeftToeBase',
            'RightUpLeg', 'RightLeg', 'RightFoot', 'RightToeBase']

def bone_depth(b):
    d = 0
    while b.parent: d += 1; b = b.parent
    return d
wh_order = sorted(WH_BONES, key=lambda n: bone_depth(arm_wh.data.bones[n]))
rest_local_rot = {}
for n in WH_BONES:
    b = arm_wh.data.bones[n]
    m = (b.parent.matrix_local.inverted() @ b.matrix_local) if b.parent else b.matrix_local
    rest_local_rot[n] = m.to_quaternion()
mq_rest_world = {mb: (arm_mq.matrix_world @ arm_mq.data.bones[mb].matrix_local) for mb in set(MAP.values())}
wh_rest_world = {n: (arm_wh.matrix_world @ arm_wh.data.bones[n].matrix_local) for n in WH_BONES}
mq_hip_rest_pos = (arm_mq.matrix_world @ arm_mq.data.bones['Hip'].head_local).copy()
wh_root_rest_pos = (arm_wh.matrix_world @ arm_wh.data.bones['Root'].head_local).copy()
mq_top = (arm_mq.matrix_world @ arm_mq.data.bones['ATH_Head_Top'].head_local).z
wh_top = (arm_wh.matrix_world @ arm_wh.data.bones['Head'].tail_local).z
S = wh_top / mq_top
wh_foot_rest_z = min((arm_wh.matrix_world @ arm_wh.data.bones[n].head_local).z for n in ('LeftFoot', 'RightFoot'))
arm_wh_rot_inv = arm_wh.matrix_world.to_quaternion().inverted()
G = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1))); Ginv = G.inverted()
Cq = G.to_quaternion(); Cq_inv = Cq.inverted()
wh_rest_world_rot = {n: wh_rest_world[n].to_quaternion() for n in WH_BONES}

def export_frame():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm_wh.evaluated_get(dg)
    Rg, Mg = {}, {}
    for n in WH_BONES:
        W = arm_wh.matrix_world @ ev.pose.bones[n].matrix
        Mg[n] = G @ W @ Ginv
        Rg[n] = Cq @ W.to_quaternion() @ wh_rest_world_rot[n].inverted() @ Cq_inv
    quats, world = {}, {}
    for n in WH_BONES:
        b = arm_wh.data.bones[n]
        q = (Rg[b.parent.name].inverted() @ Rg[n]) if b.parent else Rg[n]
        q.normalize()
        quats[n] = [round(q.x, 6), round(q.y, 6), round(q.z, 6), round(q.w, 6)]
        t = Mg[n].translation
        world[n] = [round(t.x, 4), round(t.y, 4), round(t.z, 4)]
    rt = Mg['Root'].translation
    return quats, [round(rt.x, 4), round(rt.y, 4), round(rt.z, 4)], world

bpy.context.scene.frame_set(1)
rest_quats, rest_rt, _ = export_frame()
maxdev = max(2 * math.acos(min(1.0, abs(q[3]))) for q in rest_quats.values())
print('REST export max quat deviation (rad):', round(maxdev, 6), 'root_t rest:', rest_rt)
assert maxdev < 1e-3, 'rest export must be identity'

from BlenderTekkenAnimationImporter.Animation0xC8 import Animation0xC8
from BlenderTekkenAnimationImporter.AnimationImporter import AnimationImporter
anim = Animation0xC8(open(os.environ['T7_CLIP_BIN'], 'rb').read())
AnimationImporter.insert_key_frames_for_animation(None, anim)

def solve_pose(f):
    bpy.context.scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ev_mq = arm_mq.evaluated_get(dg)
    des_world = {}
    for wb, mb in MAP.items():
        Wq = (arm_mq.matrix_world @ ev_mq.pose.bones[mb].matrix).to_quaternion()
        des_world[wb] = Wq @ mq_rest_world[mb].to_quaternion().inverted() @ wh_rest_world[wb].to_quaternion()
    mq_hip_pos = arm_mq.matrix_world @ ev_mq.pose.bones['Hip'].head
    P = wh_root_rest_pos + S * (mq_hip_pos - mq_hip_rest_pos)
    A_root = arm_wh.matrix_world.inverted() @ Matrix.Translation(P) @ des_world['Root'].to_matrix().to_4x4()
    arm_wh.pose.bones['Root'].matrix = A_root
    A_rot = {'Root': A_root.to_quaternion()}
    for n in wh_order:
        if n == 'Root': continue
        b = arm_wh.data.bones[n]; pn = b.parent.name
        if n in des_world:
            A_des = arm_wh_rot_inv @ des_world[n]
            basis = rest_local_rot[n].inverted() @ A_rot[pn].inverted() @ A_des
            arm_wh.pose.bones[n].rotation_quaternion = basis
            A_rot[n] = A_rot[pn] @ rest_local_rot[n] @ basis
        else:
            arm_wh.pose.bones[n].rotation_quaternion = Quaternion((1, 0, 0, 0))
            A_rot[n] = A_rot[pn] @ rest_local_rot[n]
    bpy.context.view_layer.update()
    return des_world, P

def ground_shift():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm_wh.evaluated_get(dg)
    z = min((arm_wh.matrix_world @ ev.pose.bones[n].head).z for n in ('LeftFoot', 'RightFoot'))
    return wh_foot_rest_z - z

frames_out = {'rot_xyzw': {n: [] for n in WH_BONES}, 'root_t': [], 'wh_world': [], 'rot_err_deg': []}
src_frames = list(range(1, 61, 2))
for f in src_frames:
    des_world, P = solve_pose(f)
    dz = ground_shift()
    if abs(dz) > 1e-4:
        A_root = arm_wh.matrix_world.inverted() @ Matrix.Translation(P + Vector((0, 0, dz))) @ des_world['Root'].to_matrix().to_4x4()
        arm_wh.pose.bones['Root'].matrix = A_root
        bpy.context.view_layer.update()
    q, rt, world = export_frame()
    for n in WH_BONES: frames_out['rot_xyzw'][n].append(q[n])
    frames_out['root_t'].append(rt); frames_out['wh_world'].append(world)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm_wh.evaluated_get(dg)
    errs = {}
    for wb in MAP:
        Wq = (arm_wh.matrix_world @ ev.pose.bones[wb].matrix).to_quaternion()
        dq = Wq @ des_world[wb].inverted()
        errs[wb] = round(math.degrees(2 * math.acos(min(1.0, abs(dq.w)))), 3)
    frames_out['rot_err_deg'].append(errs)
frames_out['src_frames'] = src_frames
frames_out['rest_check'] = {'max_quat_dev_rad': round(maxdev, 6), 'root_t': rest_rt}
json.dump(frames_out, open(os.path.join(OUT, 'bake_raw.json'), 'w'))
print('BAKE_RAW saved', len(src_frames), 'frames ->', os.path.join(OUT, 'bake_raw.json'))
print('BAKE_DONE - assemble the wh-anim/1 asset header around rot_xyzw/root_t (see docs/anim/T7-0xC8-CONTROL-TEST-2026-10-30.md)')
