#!/usr/bin/env python3
"""DEATHFANG rig + multi-clip bake driver (run INSIDE Blender 4.0.2).

Rigs a decoded+simplified Tripo static with the repo's GameRig backend
(tools/auto_rig/backends/gamerig_backend.py functions, reused not forked),
then bakes MULTIPLE Iori donor clips onto the rig in one session using the
backend's world-space FK transfer, with the donor's Bip001 bone names
injected through the backend's SRC_ALIASES hook.

    blender -b --factory-startup --python df_rig_bake.py -- \
        --in human-simp.glb --out human-rigged.glb \
        --donor roster/iori/attires/attire1/model.glb \
        --clips Battle_Idle:2,Skill_01:1,Skill_03:1 \
        --height 1.8 --metrics-out human-metrics.json

Output GLB: canonical WH joint names, animations = the baked clips plus
an "Idle" alias action copied from Battle_Idle.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BACKENDS = os.path.expanduser(
    "~/workspace/_wh-work/deathfang-tools/tools/auto_rig/backends")
sys.path.insert(0, BACKENDS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gamerig_backend as gb  # noqa: E402

# Iori donor (KOF All Star) Bip001 source names for canonical WH bones.
BIP001 = {
    "Hips": "Bip001 Pelvis_01",
    "Spine": "Bip001 Spine_02",
    "Spine1": "Bip001 Spine1_017",
    "Neck": "Bip001 Neck_018",
    "Head": "Bip001 Head_019",
    "LeftShoulder": "Bip001 L Clavicle_026",
    "RightShoulder": "Bip001 R Clavicle_043",
    "LeftArm": "Bip001 L UpperArm_027",
    "RightArm": "Bip001 R UpperArm_044",
    "LeftForeArm": "Bip001 L Forearm_028",
    "RightForeArm": "Bip001 R Forearm_045",
    "LeftHand": "Bip001 L Hand_029",
    "RightHand": "Bip001 R Hand_046",
    "LeftUpLeg": "Bip001 L Thigh_03",
    "RightUpLeg": "Bip001 R Thigh_010",
    "LeftLeg": "Bip001 L Calf_04",
    "RightLeg": "Bip001 R Calf_011",
    "LeftFoot": "Bip001 L Foot_05",
    "RightFoot": "Bip001 R Foot_012",
    "LeftToeBase": "Bip001 L Toe0_06",
    "RightToeBase": "Bip001 R Toe0_013",
    "LeftHandThumb1": "Bip001 L Finger0_030",
    "LeftHandThumb2": "Bip001 L Finger01_031",
    "LeftHandIndex1": "Bip001 L Finger1_032",
    "LeftHandIndex2": "Bip001 L Finger11_033",
    "LeftHandMiddle1": "Bip001 L Finger2_035",
    "LeftHandMiddle2": "Bip001 L Finger21_036",
    "LeftHandRing1": "Bip001 L Finger3_037",
    "LeftHandRing2": "Bip001 L Finger31_038",
    "RightHandThumb1": "Bip001 R Finger0_047",
    "RightHandThumb2": "Bip001 R Finger01_048",
    "RightHandIndex1": "Bip001 R Finger1_049",
    "RightHandIndex2": "Bip001 R Finger11_050",
    "RightHandMiddle1": "Bip001 R Finger2_052",
    "RightHandMiddle2": "Bip001 R Finger21_053",
    "RightHandRing1": "Bip001 R Finger3_054",
    "RightHandRing2": "Bip001 R Finger31_055",
}


def transfer_keep(rig, donor_path, clip_name, clip_step, keep_actions):
    """gb.transfer_clip variant: full-clip window, and previously baked
    actions (keep_actions) survive the donor cleanup."""
    import bpy
    before_objs = set(bpy.context.scene.objects)
    before_acts = set(bpy.data.actions)
    name, nframes, npairs = _transfer_body(
        rig, donor_path, clip_name, clip_step, before_objs, before_acts,
        keep_actions)
    return name, nframes, npairs


NEXT = {"Hips": "Spine", "Spine": "Spine1", "Spine1": "Spine2",
        "Spine2": "Neck", "Neck": "Head",
        "LeftShoulder": "LeftArm", "LeftArm": "LeftForeArm",
        "LeftForeArm": "LeftHand",
        "RightShoulder": "RightArm", "RightArm": "RightForeArm",
        "RightForeArm": "RightHand",
        "LeftUpLeg": "LeftLeg", "LeftLeg": "LeftFoot",
        "LeftFoot": "LeftToeBase",
        "RightUpLeg": "RightLeg", "RightLeg": "RightFoot",
        "RightFoot": "RightToeBase"}

_STANCE_CACHE = {}

# Frame-carried transfer for the spine column + head (stance-fix,
# 2026-10-21). Direction arcs carry no roll about the bone axis:
# measured on the shipped PR #443 rigs, that left the head canted
# -60 deg off level (donor: +10) on BOTH forms and the chest rolled
# (shoulder line -17 deg vs the donor's +15). For these bones the
# world frame is BUILT from donor geometry instead: the bone's own
# axis direction (donor_eval_dir) plus a lateral reference (the
# donor's hip line for Hips/Spine, his shoulder line for the upper
# column) — and for the Head, the donor head's own facing: the Bip001
# head bone axis points at the face (Max convention, verified: the
# evaluated tail-head direction is 82 deg off the neck segment and
# tracks the face in renders).
FRAME_CANON = {"Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"}
FRAME_LAT_SRC = {"Hips": "hips", "Spine": "hips",
                 "Spine1": "shoulders", "Spine2": "shoulders",
                 "Neck": "shoulders"}


def _frame_quat(aux_axis, axis_img, aux_img):
    """World quaternion whose local Y axis lands on axis_img and
    whose local aux_axis ('X' or 'Z') lands on aux_img
    (orthogonalized against Y). Returns None if degenerate."""
    from mathutils import Matrix
    y = axis_img.normalized()
    a = aux_img - y * aux_img.dot(y)
    if a.length < 1e-6:
        return None
    a.normalize()
    if aux_axis == "X":
        ix, iy = a, y
        iz = ix.cross(iy)
    else:
        iz, iy = a, y
        ix = iy.cross(iz)
    m = Matrix(((ix.x, iy.x, iz.x),
                (ix.y, iy.y, iz.y),
                (ix.z, iy.z, iz.z)))
    return m.to_quaternion()


def _stance_for(rig, donor_path):
    """Stance context for (rig, donor): bone maps, parent order, and
    the direction-based stance (world frames + local bases + stance
    directions). Imports its own donor copy to capture the evaluated
    Battle_Idle frame-10 directions, then removes it. Cached: the
    skin pass and every clip transfer share one stance."""
    key = (rig.name, donor_path)
    if key in _STANCE_CACHE:
        return _STANCE_CACHE[key]
    import bpy
    gb.SRC_ALIASES.update(BIP001)
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=donor_path)
    new_objs = [o for o in bpy.context.scene.objects if o not in before]
    donors = [o for o in new_objs if o.type == "ARMATURE"]
    if not donors:
        raise RuntimeError("donor %s has no armature" % donor_path)
    src = max(donors, key=lambda a: len(a.data.bones))

    def src_name(canon):
        return gb.SRC_ALIASES.get(canon, canon)

    def_for_canon = {c: d for c, d in gb.DONOR_TO_DEF.items()
                     if src_name(c) in src.data.bones
                     and d in rig.data.bones}
    if not def_for_canon:
        raise RuntimeError("no mappable bones between donor and rig")
    canon_for_def = {d: c for c, d in def_for_canon.items()}
    tgt_parent = {b.name: (b.parent.name if b.parent else None)
                  for b in rig.data.bones}
    tgt_rest_local = {}
    for b in rig.data.bones:
        rw = b.matrix_local.to_quaternion()
        if b.parent is not None:
            pw = b.parent.matrix_local.to_quaternion()
            tgt_rest_local[b.name] = pw.inverted() @ rw
        else:
            tgt_rest_local[b.name] = rw
    order = []
    seen = set()

    def visit(n):
        if n in seen:
            return
        seen.add(n)
        if tgt_parent[n]:
            visit(tgt_parent[n])
        order.append(n)
    for n in tgt_rest_local:
        visit(n)
    tgt_rest_world = {b.name: b.matrix_local.to_quaternion()
                      for b in rig.data.bones}

    # frame-transfer calibration: for each spine-column/head DEF
    # bone, which local axis (X or Z) plays the lateral role (column)
    # or the facing role (Head) at rest, and with what sign. The
    # references come from the rig's own rest geometry (shoulder line
    # = the figure's left; forward = left x up), never assumed axes.
    from mathutils import Vector as _Vec
    frame_cal = {}
    _sh = rig.data.bones.get(gb.DONOR_TO_DEF.get("LeftShoulder"))
    _sh2 = rig.data.bones.get(gb.DONOR_TO_DEF.get("RightShoulder"))
    if _sh is not None and _sh2 is not None:
        _lat_ref = (_sh.head_local - _sh2.head_local)
        if _lat_ref.length > 1e-6:
            _lat_ref.normalize()
            _fwd_ref = _lat_ref.cross(_Vec((0.0, 0.0, 1.0)))
            for _canon in FRAME_CANON:
                _dn = gb.DONOR_TO_DEF.get(_canon)
                if _dn not in tgt_rest_world:
                    continue
                _q = tgt_rest_world[_dn]
                _xw = _q @ _Vec((1.0, 0.0, 0.0))
                _zw = _q @ _Vec((0.0, 0.0, 1.0))
                _ref = _fwd_ref if _canon == "Head" else _lat_ref
                if abs(_xw.dot(_ref)) >= abs(_zw.dot(_ref)):
                    frame_cal[_dn] = ("X", 1.0 if _xw.dot(_ref) >= 0
                                      else -1.0)
                else:
                    frame_cal[_dn] = ("Z", 1.0 if _zw.dot(_ref) >= 0
                                      else -1.0)
    print("FRAME_CAL %s" % (frame_cal,), flush=True)

    def chain_dir(arm_bones, bone, canon, name_of):
        if canon == "Head":
            nb = arm_bones.get(name_of("Neck"))
            if nb is not None:
                d = bone.head_local - nb.head_local
                if d.length > 1e-9:
                    return d.normalized()
        nxt = NEXT.get(canon)
        if nxt is not None:
            cb = arm_bones.get(name_of(nxt))
            if cb is not None:
                d = cb.head_local - bone.head_local
                if d.length > 1e-9:
                    return d.normalized()
        d = bone.tail_local - bone.head_local
        return d.normalized() if d.length > 1e-9 else None

    _dmw = src.matrix_world
    src_pb = {canon: src.pose.bones[src_name(canon)]
              for canon in def_for_canon}

    def donor_child_pb(canon):
        nxt = NEXT.get(canon)
        while nxt is not None:
            nm = src_name(nxt)
            if nm in src.pose.bones:
                return src.pose.bones[nm]
            nxt = NEXT.get(nxt)
        return None

    def donor_eval_dir(canon):
        spb = src_pb[canon]
        if canon == "Head":
            d = _dmw @ spb.head - _dmw @ src_pb["Neck"].head
            return d.normalized() if d.length > 1e-9 else None
        cpb = donor_child_pb(canon)
        if cpb is not None:
            d = _dmw @ cpb.head - _dmw @ spb.head
        else:
            d = _dmw @ spb.tail - _dmw @ spb.head
        return d.normalized() if d.length > 1e-9 else None

    idle_act = None
    for a in bpy.data.actions:
        if a.name.startswith("Battle_Idle_"):
            idle_act = a
            break
    if idle_act is not None:
        if src.animation_data is None:
            src.animation_data_create()
        for track in src.animation_data.nla_tracks:
            track.mute = True
        src.animation_data.action = idle_act
        bpy.context.scene.frame_set(int(idle_act.frame_range[0]) + 10)
        bpy.context.view_layer.update()
    donor_dir = {canon: donor_eval_dir(canon) for canon in def_for_canon}

    # donor lateral references + head facing at the stance frame
    def _pos_line(canon_a, canon_b):
        pa = _dmw @ src_pb[canon_a].head
        pb2 = _dmw @ src_pb[canon_b].head
        d = pa - pb2
        return d.normalized() if d.length > 1e-9 else None

    donor_lat = {}
    if "LeftUpLeg" in src_pb and "RightUpLeg" in src_pb:
        donor_lat["hips"] = _pos_line("LeftUpLeg", "RightUpLeg")
    if "LeftArm" in src_pb and "RightArm" in src_pb:
        donor_lat["shoulders"] = _pos_line("LeftArm", "RightArm")
    # Donor head axes, calibrated on the donor's REST pose: which of
    # the head bone's local axes points at his face / up his skull.
    # (The bone's tail direction is NOT the facing: measured 52 deg
    # off it. The evaluated matrix axes are the true carriage.)
    donor_head_axes = None
    if "Head" in src_pb:
        from mathutils import Vector as _V2
        _hb = src.data.bones[src_name("Head")]
        _W = _dmw @ _hb.matrix_local
        _cols = []
        for _i in range(3):
            _c = _W.col[_i].to_3d()
            _cols.append(_c.normalized() if _c.length > 1e-9 else _c)
        # lateral reference from the SHOULDER JOINTS (upper-arm
        # heads, ~40cm apart) — the clavicle heads sit ~4cm apart
        # at the sternum and make a junk reference (iteration 2's
        # head landed facing backward: its "facing" calibration came
        # from that near-degenerate clavicle line).
        _la = src.data.bones[src_name("LeftArm")]
        _ra = src.data.bones[src_name("RightArm")]
        _lp = _dmw @ _la.head_local
        _rp = _dmw @ _ra.head_local
        _latr = (_lp - _rp)
        _up = _V2((0.0, 0.0, 1.0))
        _fwdr = _latr.cross(_up) if _latr.length > 1e-9 else None
        if _fwdr is not None and _fwdr.length > 1e-9:
            _latr.normalize()
            _fwdr.normalize()
            print("FRAME_AXES donor rest refs lat=%s fwd=%s"
                  % ([round(float(c), 2) for c in _latr],
                     [round(float(c), 2) for c in _fwdr]), flush=True)
            for _i in range(3):
                print("FRAME_AXES donor head local axis %d: "
                      "fwd=%+.2f lat=%+.2f up=%+.2f"
                      % (_i, _cols[_i].dot(_fwdr),
                         _cols[_i].dot(_latr),
                         _cols[_i].dot(_up)), flush=True)
            _fi = max(range(3), key=lambda i: abs(_cols[i].dot(_fwdr)))
            _fs = 1.0 if _cols[_fi].dot(_fwdr) >= 0 else -1.0
            _ei = max((i for i in range(3) if i != _fi),
                      key=lambda i: abs(_cols[i].dot(_latr)))
            _si = next(i for i in range(3) if i not in (_fi, _ei))
            _ss = 1.0 if _cols[_si].dot(_up) >= 0 else -1.0
            donor_head_axes = (_fi, _fs, _si, _ss)
    print("FRAME_AXES donor_head_axes=%s" % (donor_head_axes,),
          flush=True)

    def donor_head_FU():
        """(facing, skull_up) world dirs from the donor head's
        evaluated matrix, using the rest calibration above."""
        if donor_head_axes is None or "Head" not in src_pb:
            return None, None
        _fi, _fs, _si, _ss = donor_head_axes
        _W = _dmw @ src_pb["Head"].matrix
        _cf = _W.col[_fi].to_3d()
        _cs = _W.col[_si].to_3d()
        if _cf.length < 1e-9 or _cs.length < 1e-9:
            return None, None
        return _fs * _cf.normalized(), _ss * _cs.normalized()

    donor_face, donor_skull = donor_head_FU()
    print("FRAME_AUX lat=%s face=%s skull=%s" % (
        {k: (None if v is None else [round(float(c), 2) for c in v])
         for k, v in donor_lat.items()},
        None if donor_face is None else [round(float(c), 2)
                                         for c in donor_face],
        None if donor_skull is None else [round(float(c), 2)
                                          for c in donor_skull]),
        flush=True)

    stance_world = {}
    stance_basis = {}
    for name in order:
        p = tgt_parent[name]
        canon = canon_for_def.get(name)
        if canon is not None and donor_dir[canon] is not None:
            b = rig.data.bones[name]
            td = chain_dir(rig.data.bones, b, canon,
                           lambda c: gb.DONOR_TO_DEF[c])
            w = None
            if (canon in FRAME_CANON and name in frame_cal
                    and not os.environ.get("DF_NO_FRAME")):
                _ax, _sgn = frame_cal[name]
                if canon == "Head" and donor_face is not None:
                    _F = donor_face
                    _U = donor_skull if donor_skull is not None \
                        else donor_dir[canon]
                    _Yv = _U - _F * _U.dot(_F)
                    if _Yv.length > 1e-6:
                        w = _frame_quat(_ax, _Yv.normalized(),
                                        _sgn * _F)
                elif canon in FRAME_LAT_SRC:
                    _lat = donor_lat.get(FRAME_LAT_SRC[canon])
                    if _lat is not None:
                        w = _frame_quat(_ax, donor_dir[canon],
                                        _sgn * _lat)
            if w is None and td is not None:
                q = td.rotation_difference(donor_dir[canon])
                w = q @ tgt_rest_world[name]
            elif w is None:
                w = tgt_rest_world[name]
        elif p is not None:
            w = stance_world[p] @ tgt_rest_local[name]
        else:
            w = tgt_rest_local[name]
        stance_world[name] = w
        if p is not None:
            local = stance_world[p].inverted() @ w
        else:
            local = w
        stance_basis[name] = tgt_rest_local[name].inverted() @ local
    tgt_dir_rest = {}
    for name in order:
        canon = canon_for_def.get(name)
        if canon is not None:
            tgt_dir_rest[name] = chain_dir(
                rig.data.bones, rig.data.bones[name], canon,
                lambda c: gb.DONOR_TO_DEF[c])
    stance_dir = {}
    for name in order:
        if name in tgt_dir_rest and tgt_dir_rest[name] is not None:
            stance_dir[name] = stance_world[name] @ (
                tgt_rest_world[name].inverted() @ tgt_dir_rest[name])
    # stance verification: the head bone's resulting world facing /
    # skull dirs vs the donor's (the construction is exact, so any
    # large angle here means a calibration input is wrong — visible
    # in the log within minutes, not after a full bake + render).
    _hdn = gb.DONOR_TO_DEF.get("Head")
    if _hdn in stance_world and _hdn in frame_cal and donor_face:
        import math as _m3
        from mathutils import Vector as _V3
        _ax, _sgn = frame_cal[_hdn]
        _av = {"X": _V3((1.0, 0.0, 0.0)), "Z": _V3((0.0, 0.0, 1.0))}[_ax]
        _fr = stance_world[_hdn] @ _av * _sgn
        _sk = stance_world[_hdn] @ _V3((0.0, 1.0, 0.0))
        print("FRAME_VERIFY head facing err vs donor: %.1f deg | "
              "skull err: %.1f deg" % (
                  _m3.degrees(_fr.angle(donor_face)),
                  _m3.degrees(_sk.angle(donor_skull))
                  if donor_skull else -1), flush=True)
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    ctx = {"def_for_canon": def_for_canon,
           "canon_for_def": canon_for_def,
           "tgt_parent": tgt_parent,
           "tgt_rest_local": tgt_rest_local,
           "tgt_rest_world": tgt_rest_world,
           "order": order,
           "stance_world": stance_world,
           "stance_basis": stance_basis,
           "stance_dir": stance_dir,
           "chain_dir": chain_dir,
           "frame_cal": frame_cal,
           "donor_head_axes": donor_head_axes}
    _STANCE_CACHE[key] = ctx
    return ctx


def _transfer_body(rig, donor_path, clip_name, clip_step, before_objs,
                   before_acts, keep_actions):
    """Clip transfer onto the GameRig rig: stance+basis method (see
    the comment at the stance_basis construction) for donors bound in
    their stance pose, full-clip windows, and cleanup that preserves
    previously baked actions."""
    import bpy
    from mathutils import Matrix, Quaternion, Vector  # noqa: F401
    gb.SRC_ALIASES.update(BIP001)
    new_objs_pre = before_objs
    bpy.ops.import_scene.gltf(filepath=donor_path)
    new_objs = [o for o in bpy.context.scene.objects if o not in new_objs_pre]
    donors = [o for o in new_objs if o.type == "ARMATURE"]
    if not donors:
        raise RuntimeError("donor %s has no armature" % donor_path)
    src = max(donors, key=lambda a: len(a.data.bones))

    def src_name(canon):
        return gb.SRC_ALIASES.get(canon, canon)

    out_name = clip_name
    action = bpy.data.actions.get(clip_name)
    if action is None:
        for a in bpy.data.actions:
            if a.name == clip_name or a.name.startswith(clip_name + "_"):
                action = a
                break
    if action is None:
        raise RuntimeError("donor has no usable action (wanted %s)"
                           % clip_name)
    if src.animation_data is None:
        src.animation_data_create()
    for track in src.animation_data.nla_tracks:
        track.mute = True
    src.animation_data.action = action
    act_f0, act_f1 = (int(v) for v in action.frame_range)
    win_start = act_f0
    win_end = act_f1
    scene = bpy.context.scene

    # DIRECTION transfer. This donor is bound IN Iori's stance and its
    # Bip001 frames are Max-convention (Pelvis bind frame is a 180 flip;
    # its matrix_basis values are matched to those frames and poison
    # any basis/delta copy). The convention-free signal is GEOMETRY:
    # evaluated joint directions. Stance: arc each target bone's rest
    # frame from its own bind direction onto the donor's bind
    # direction. Per frame: arc the target bone's stance frame from
    # its stance direction onto the donor's EVALUATED direction that
    # frame (pb.head of the bone and its principal-chain child), then
    # basis = rest_local^-1 @ (parent_frame_world^-1 @ frame_world),
    # parent-first. Twist about a bone's own axis is not carried by
    # directions — acceptable; gross pose and stance read correctly.
    # Stance context (maps + direction stance) is shared with the
    # skin pass via _stance_for (cached per rig+donor).
    _ctx = _stance_for(rig, donor_path)
    def_for_canon = _ctx["def_for_canon"]
    canon_for_def = _ctx["canon_for_def"]
    tgt_parent = _ctx["tgt_parent"]
    tgt_rest_local = _ctx["tgt_rest_local"]
    order = _ctx["order"]
    stance_world = _ctx["stance_world"]
    stance_dir = _ctx["stance_dir"]
    frame_cal = _ctx.get("frame_cal", {})

    _dmw = src.matrix_world
    src_pb = {canon: src.pose.bones[src_name(canon)]
              for canon in def_for_canon}

    def donor_child_pb(canon):
        nxt = NEXT.get(canon)
        while nxt is not None:
            nm = src_name(nxt)
            if nm in src.pose.bones:
                return src.pose.bones[nm]
            nxt = NEXT.get(nxt)
        return None

    def donor_eval_dir(canon):
        spb = src_pb[canon]
        if canon == "Head":
            # the head bone's own axis is a Max convention (points at
            # the face); use the neck segment direction instead
            d = _dmw @ spb.head - _dmw @ src_pb["Neck"].head
            return d.normalized() if d.length > 1e-9 else None
        cpb = donor_child_pb(canon)
        if cpb is not None:
            d = _dmw @ cpb.head - _dmw @ spb.head
        else:
            d = _dmw @ spb.tail - _dmw @ spb.head
        return d.normalized() if d.length > 1e-9 else None

    src_child_pb = {canon: donor_child_pb(canon)
                    for canon in def_for_canon}

    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    out_action = bpy.data.actions.new(name=out_name)
    if rig.animation_data is None:
        rig.animation_data_create()
    rig.animation_data.action = out_action
    src_frames = list(range(win_start, win_end + 1, clip_step))
    for out_frame, frame in enumerate(src_frames):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        # donor lateral references + head facing, this frame
        _lat = {}
        if "LeftUpLeg" in src_pb and "RightUpLeg" in src_pb:
            _d = (_dmw @ src_pb["LeftUpLeg"].head
                  - _dmw @ src_pb["RightUpLeg"].head)
            if _d.length > 1e-9:
                _lat["hips"] = _d.normalized()
        if "LeftArm" in src_pb and "RightArm" in src_pb:
            _d = (_dmw @ src_pb["LeftArm"].head
                  - _dmw @ src_pb["RightArm"].head)
            if _d.length > 1e-9:
                _lat["shoulders"] = _d.normalized()
        _face = None
        _skull = None
        _dha = _ctx.get("donor_head_axes")
        if _dha is not None and "Head" in src_pb:
            _fi, _fs, _si, _ss = _dha
            _W = _dmw @ src_pb["Head"].matrix
            _cf = _W.col[_fi].to_3d()
            _cs = _W.col[_si].to_3d()
            if _cf.length > 1e-9 and _cs.length > 1e-9:
                _face = _fs * _cf.normalized()
                _skull = _ss * _cs.normalized()
        # donor evaluated directions this frame (armature space)
        frame_world = {}
        for name in order:
            p = tgt_parent[name]
            canon = canon_for_def.get(name)
            w = None
            if canon is not None and name in stance_dir:
                _dd = donor_eval_dir(canon)
                if _dd is not None:
                    if (canon in FRAME_CANON and name in frame_cal
                            and not os.environ.get("DF_NO_FRAME")):
                        _ax, _sgn = frame_cal[name]
                        if canon == "Head" and _face is not None:
                            _U = _skull if _skull is not None else _dd
                            _Yv = _U - _face * _U.dot(_face)
                            if _Yv.length > 1e-6:
                                w = _frame_quat(_ax, _Yv.normalized(),
                                                _sgn * _face)
                        elif canon in FRAME_LAT_SRC:
                            _lv = _lat.get(FRAME_LAT_SRC[canon])
                            if _lv is not None:
                                w = _frame_quat(_ax, _dd,
                                                _sgn * _lv)
                    if w is None:
                        q = stance_dir[name].rotation_difference(_dd)
                        w = q @ stance_world[name]
            if w is None:
                if p is not None:
                    w = frame_world[p] @ tgt_rest_local[name]
                else:
                    w = tgt_rest_local[name]
            frame_world[name] = w
            if canon is not None:
                if p is not None:
                    local = frame_world[p].inverted() @ w
                else:
                    local = w
                basis = tgt_rest_local[name].inverted() @ local
                if out_frame == 5 and name in ("DEF-spine", "DEF-spine.001",
                                               "DEF-spine.002"):
                    import math as _m2
                    def _a(_q):
                        return round(_m2.degrees(2 * _m2.acos(max(
                            -1.0, min(1.0, abs(_q.w))))), 1)
                    _ddv = donor_eval_dir(canon)
                    _dd = _ddv if _ddv is not None else stance_dir[name]
                    _arc = stance_dir[name].rotation_difference(
                        _dd.normalized())
                    print("DFDBG2 %s parent=%s basis=%s stance_dir=%s "
                          "donor_dir=%s arc=%s" % (
                              name, p, _a(basis),
                              [round(float(c), 2) for c in stance_dir[name]],
                              [round(float(c), 2) for c in _dd.normalized()],
                              _a(_arc)), flush=True)
                t_pb = rig.pose.bones[name]
                t_pb.rotation_quaternion = basis
                t_pb.keyframe_insert(data_path="rotation_quaternion",
                                     frame=out_frame)
    bpy.ops.object.mode_set(mode="OBJECT")
    scene.frame_start, scene.frame_end = 0, len(src_frames) - 1
    for o in new_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    for act in list(bpy.data.actions):
        if act != out_action and act not in keep_actions:
            bpy.data.actions.remove(act)
    bpy.context.view_layer.update()
    return out_action.name, len(src_frames), len(def_for_canon)


def main():
    import bpy
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--donor", required=True)
    ap.add_argument("--clips", required=True,
                    help="comma list Name:step, e.g. Battle_Idle:2,Skill_01:1")
    ap.add_argument("--height", type=float, default=1.8)
    ap.add_argument("--gamerig-dir", default=gb.DEFAULT_GAMERIG_DIR)
    ap.add_argument("--metrics-out", default=None)
    a = ap.parse_args(argv)

    clips = []
    for part in a.clips.split(","):
        nm, st = part.rsplit(":", 1)
        clips.append((nm.strip(), int(st)))

    metrics = {"backend": "gamerig+df-multi-bake", "input": a.inp,
               "output": a.out}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    gb.install_gamerig(a.gamerig_dir)
    gb.enable_gamerig()
    gb.apply_blender402_shim()
    metrics["shim"] = "stock 4.0.2 create_root_bone"

    bpy.ops.import_scene.gltf(filepath=a.inp)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("no meshes imported from %s" % a.inp)
    metrics["input_meshes"] = len(meshes)
    metrics["input_verts"] = sum(len(o.data.vertices) for o in meshes)
    stats = gb.normalize_and_face(meshes, a.height)
    metrics["normalize"] = {k: v for k, v in stats.items() if k != "_verts"}

    bpy.ops.object.armature_human_metarig_add()
    meta = bpy.context.object
    metrics["face_bones_stripped"] = gb.strip_face(meta)
    metrics["fit"] = gb.fit_metarig(meta, stats)
    stats.pop("_verts", None)

    bpy.ops.object.select_all(action="DESELECT")
    meta.select_set(True)
    bpy.context.view_layer.objects.active = meta
    bpy.ops.pose.gamerig_generate()
    cands = [o for o in bpy.context.scene.objects
             if o.type == "ARMATURE" and o != meta]
    if not cands:
        raise RuntimeError("GameRig generation produced no rig")
    rig = max(cands, key=lambda o: len(o.data.bones))
    bad_parents = [b.name for b in rig.data.bones if b.use_deform
                   and b.parent is not None and not b.parent.use_deform]
    if bad_parents:
        raise RuntimeError("DEF hierarchy not clean: %s" % bad_parents)
    kept, removed = gb.strip_to_deform(rig)
    metrics["strip"] = {"kept_def_bones": kept,
                        "removed_control_bones": removed}
    _ctx = _stance_for(rig, a.donor)
    import skin_donor
    skin_stats = skin_donor.skin_via_donor(
        gb, rig, meshes, a.donor, a.height, BIP001,
        stance_basis=_ctx["stance_basis"])
    metrics["skin"] = skin_stats
    metrics["unweighted_fixed"] = skin_stats.get("unweighted_fixed", 0)
    print("DFBAKE_RIGGED", json.dumps(metrics), flush=True)

    keep_objs = set(meshes) | {rig}
    for o in list(bpy.context.scene.objects):
        if o not in keep_objs:
            bpy.data.objects.remove(o, do_unlink=True)

    def export_state(path, actions):
        """(Re)build NLA strips from `actions` and export the current
        rig+meshes to `path`. Used as an OOM checkpoint after every
        phase: if the session is killed later, the last export on disk
        is a usable rigged GLB. In-session bones stay DEF-named; the
        file-level rename to canonical joints runs per export."""
        ad = rig.animation_data
        if ad is None:
            ad = rig.animation_data_create()
        ad.action = None
        for tr in list(ad.nla_tracks):
            ad.nla_tracks.remove(tr)
        for act in actions:
            tr = ad.nla_tracks.new()
            tr.name = act.name
            st = tr.strips.new(act.name, int(act.frame_range[0]), act)
            st.extrapolation = "NOTHING"
        bpy.ops.object.select_all(action="DESELECT")
        rig.select_set(True)
        for m in meshes:
            m.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.export_scene.gltf(
            filepath=path, export_format="GLB", use_selection=True,
            export_skins=True, export_def_bones=True,
            export_animations=bool(actions), export_nla_strips=True,
            export_yup=True)
        gb.rename_glb_joints(path)
        print("DFBAKE_CHECKPOINT_EXPORT", path,
              [a2.name for a2 in actions], flush=True)

    # checkpoint 0: rig-only GLB (survives any later OOM)
    export_state(a.out + ".rigonly.glb", [])
    if os.environ.get("DF_SKIN_ONLY"):
        print("DFBAKE_SKIN_ONLY_DONE", flush=True)
        return

    baked = []
    keep = []
    for clip_name, step in clips:
        nm, nf, nb = transfer_keep(rig, a.donor, clip_name, step, keep)
        act = bpy.data.actions[nm]
        keep.append(act)
        baked.append({"clip": nm, "frames": nf, "bones": nb})
        print("DFBAKE_CLIP", json.dumps(baked[-1]), flush=True)
        # "Idle" alias of Battle_Idle (engine looks up exact 'Idle';
        # the assets.js alias also maps Battle_Idle, ship both names).
        if nm == "Battle_Idle" and "Idle" not in [k.name for k in keep]:
            alias = act.copy()
            alias.name = "Idle"
            keep.append(alias)
            metrics["idle_alias"] = "Idle <- Battle_Idle (action copy)"
        if os.environ.get("DFBAKE_DEBUG") and nm == "Battle_Idle":
            # in-session verdict BEFORE any export touches the scene:
            # pose heads + one render of the pose as baked
            import math as _m
            from mathutils import Vector as _V
            if rig.animation_data is None:
                rig.animation_data_create()
            rig.animation_data.action = act
            bpy.context.scene.frame_set(10)
            bpy.context.view_layer.update()
            for _bn in ("DEF-spine", "DEF-spine.001", "DEF-spine.002",
                        "DEF-spine.003", "DEF-spine.004", "DEF-spine.005",
                        "DEF-shoulder.L", "DEF-upper_arm.L",
                        "DEF-forearm.L", "DEF-hand.L", "DEF-pelvis.L",
                        "DEF-pelvis.R", "DEF-thigh.L", "DEF-thigh.R",
                        "DEF-shin.L", "DEF-foot.L"):
                _pb = rig.pose.bones.get(_bn)
                if _pb is None:
                    print("DFDBG_POSE", _bn, "MISSING", flush=True)
                else:
                    _h = rig.matrix_world @ _pb.head
                    _r = rig.matrix_world @ _pb.bone.head_local
                    print("DFDBG_POSE %s head=(%.2f,%.2f,%.2f) "
                          "rest=(%.2f,%.2f,%.2f) basis_ang=%.1f" % (
                              _bn, _h.x, _h.y, _h.z, _r.x, _r.y, _r.z,
                              _m.degrees(2 * _m.acos(max(
                                  -1.0, min(1.0, abs(
                                      _pb.matrix_basis.to_quaternion()
                                      .w)))))), flush=True)
            _sc = bpy.context.scene
            _sc.render.engine = "BLENDER_WORKBENCH"
            _sc.display.shading.light = "STUDIO"
            _sc.display.shading.color_type = "TEXTURE"
            _sc.render.resolution_x = 480
            _sc.render.resolution_y = 480
            _mn = _V((1e9, 1e9, 1e9))
            _mx = _V((-1e9, -1e9, -1e9))
            for _o in meshes:
                for _c in _o.bound_box:
                    _w = _o.matrix_world @ _V(_c)
                    _mn = _V(map(min, _mn, _w))
                    _mx = _V(map(max, _mx, _w))
            _ctr = (_mn + _mx) / 2
            _hgt = _mx.z - _mn.z
            _cd = bpy.data.cameras.new("dbgcam")
            _cam = bpy.data.objects.new("dbgcam", _cd)
            _sc.collection.objects.link(_cam)
            _sc.camera = _cam
            _tgt = _V((_ctr.x, _ctr.y, _mn.z + _hgt * 0.52))
            _cam.location = (_tgt.x - _hgt * 0.85,
                             _tgt.y - _hgt * 1.75,
                             _tgt.z + _hgt * 0.12)
            _cam.rotation_euler = (
                _tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
            _sc.render.filepath = os.path.join(
                os.path.dirname(os.path.abspath(a.out)),
                "insession-f10.png")
            bpy.ops.render.render(write_still=True)
            print("DFDBG_RENDERED", _sc.render.filepath, flush=True)
        # checkpoint export after every clip
        export_state(a.out, keep)
    metrics["clips"] = baked
    metrics["export_actions"] = [act.name for act in keep]
    changed = gb.rename_glb_joints(a.out)
    metrics["renamed_joints"] = len(changed)
    metrics["joint_count"] = len(gb.joint_names_of_glb(a.out))
    print("DFBAKE_METRICS", json.dumps(metrics), flush=True)
    if a.metrics_out:
        with open(a.metrics_out, "w") as f:
            json.dump(metrics, f, indent=2)
    print("DFBAKE_OK", a.out, flush=True)


if __name__ == "__main__":
    main()
