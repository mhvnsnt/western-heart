#!/usr/bin/env python3
"""
retarget_def_rig.py — retarget real mocap (BVH) onto a DEF-skeleton rig whose
control layer is disconnected (0 constraints), then layer verlet-spring jiggle.

WHY THIS EXISTS (diagnosis, 2026-10-19):
  RIG-SCARLETT-style rigs carry a full Rigify control layer (FK/IK/MCH bones)
  with ZERO constraints and use_deform=False on every control bone. Scripts
  that key the control bones (torso / spine_fk / thigh_fk / hips) animate
  NOTHING — the mesh only deforms from the DEF bones, and the main driver
  bone from the old test (`hips`) has no deform bones in its subtree at all.
  Result seen by the owner: only the directly-keyed DEF-breast chains moved;
  legs/arms never bent; spine leaned with unbent legs = stretched silhouette.

METHOD (same rest-relative delta math as retarget_blender.py):
  For every mapped bone, per frame:
      T_pose_world = T_rest_world @ S_rest_world^-1 @ S_pose_world
  Pairs are applied in target-depth order (parents before children).
  Mechanism parents that the DEF bones hang from (ORG-spine, ORG-shoulder,
  MCH-breast, MCH-ROT-head) are driven as FOLLOWERS of the mocap bone whose
  motion they must track, using their own rest matrices — otherwise thighs,
  arms, breasts and head detach from the body the moment the DEF chain moves.

  Root motion: translation scaled by hip-height ratio; XZ travel pinned to
  the first frame (in-place) while vertical bob is preserved (dance needs it).

JIGGLE (second pass, verlet springs — same solver family as
jiggle-work/star_jiggle_bake_fixed.py, params derived there):
  Springs drive the deform jiggle chains (DEF-breast, Butt) from the posed
  parent motion of the baked mocap — secondary motion follows the REAL
  movement instead of a hand-authored sine. Face bones are never touched.

Usage (headless):
  xvfb-run -a env -u PYTHONPATH <blender> -b <target.blend> --python \
      retarget_def_rig.py -- --source clip.bvh --target-arm RIG-SCARLETT \
      --out out.blend [--no-jiggle]
"""
import argparse, json, math, os, sys

import bpy
from mathutils import Matrix, Vector

# CMU (MotionBuilder names) -> DEF-skeleton targets.
# One source bone may drive several targets (followers marked in comments).
PAIRS = [
    ("Hips",         "DEF-spine"),      # pelvis (deform)
    ("Hips",         "ORG-spine"),      # FOLLOWER: thighs + tail hang off this
    ("LowerBack",    "DEF-spine.001"),
    ("Spine",        "DEF-spine.002"),
    ("Spine1",       "DEF-spine.004"),
    ("Spine1",       "ORG-shoulder.L"), # FOLLOWER: arm chains hang off this
    ("Spine1",       "ORG-shoulder.R"), # FOLLOWER
    ("Spine1",       "MCH-breast.L"),   # FOLLOWER: breast chains hang off this
    ("Spine1",       "MCH-breast.R"),   # FOLLOWER
    ("Neck",         "DEF-spine.006"),
    ("Neck1",        "DEF-spine.007"),
    ("Neck1",        "MCH-ROT-head"),   # FOLLOWER: head hangs off this
    ("Head",         "head"),
    ("LeftShoulder",  "DEF-shoulder.L"),
    ("LeftArm",       "DEF-upper_arm.L"),
    ("LeftForeArm",   "DEF-forearm.L"),
    ("LeftHand",      "DEF-hand.L"),
    ("RightShoulder", "DEF-shoulder.R"),
    ("RightArm",      "DEF-upper_arm.R"),
    ("RightForeArm",  "DEF-forearm.R"),
    ("RightHand",     "DEF-hand.R"),
    ("LeftUpLeg",     "DEF-thigh.L"),
    ("LeftLeg",       "DEF-shin.L"),
    ("LeftFoot",      "DEF-foot.L"),
    ("LeftToeBase",   "DEF-toe.L"),
    ("RightUpLeg",    "DEF-thigh.R"),
    ("RightLeg",      "DEF-shin.R"),
    ("RightFoot",     "DEF-foot.R"),
    ("RightToeBase",  "DEF-toe.R"),
]

# Jiggle chains: (bone, params) — params from the owner's approved Star bake
# (deriveParams, intensity 1.25); chain tips get decayed amplitude.
JIGGLE = []
for side in ("L", "R"):
    JIGGLE.append((f"DEF-breast.{side}",     dict(stiffness=1.343, damping=0.282, amplitude=0.158, gravity=1.400)))
    JIGGLE.append((f"DEF-breast.{side}.001", dict(stiffness=1.343, damping=0.282, amplitude=0.095, gravity=1.400)))
    JIGGLE.append((f"Butt_{side}",           dict(stiffness=1.633, damping=0.346, amplitude=0.128, gravity=1.475)))
    JIGGLE.append((f"Butt_{side}.001",       dict(stiffness=1.633, damping=0.346, amplitude=0.077, gravity=1.475)))

GRAV = Vector((0, 0, -9.81))


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--target-arm", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-jiggle", action="store_true")
    return p.parse_args(argv)


def bone_depth(bone):
    d, b = 0, bone
    while b.parent:
        d += 1
        b = b.parent
    return d


class Spring:
    """Verlet point spring (mirror of jiggle-work/star_jiggle_bake_fixed.py)."""
    def __init__(self, pbone, prm):
        self.pb = pbone
        self.p = prm
        parent = pbone.parent
        self.rest_local = parent.bone.matrix_local.inverted() @ Vector(pbone.bone.head)
        self.bone_len = self.rest_local.length
        self.pos = Vector((0, 0, 0))
        self.prev = Vector((0, 0, 0))
        self.init = False
        self._pw = None

    def begin_frame(self):
        self._pw = self.pb.parent.matrix.copy()

    def step(self, h):
        pbone, p, pw = self.pb, self.p, self._pw
        rest_world = pw @ self.rest_local
        parent_pos = pw.translation
        if not self.init:
            self.pos = rest_world.copy()
            self.prev = rest_world.copy()
            self.init = True
        drag = min(0.99, max(0.0, p["damping"]))
        vel = (self.pos - self.prev) * (1 - drag)
        self.prev = self.pos.copy()
        self.pos = self.pos + vel + GRAV * (p["gravity"] * h * h)
        t = 1 - math.exp(-p["stiffness"] * h)
        self.pos = self.pos.lerp(rest_world, min(1.0, max(0.0, t)))
        d = self.pos - parent_pos
        if d.length > 1e-9:
            self.pos = parent_pos + d.normalized() * self.bone_len
        else:
            self.pos = rest_world.copy()
        cur = self.pos - parent_pos
        if cur.length > 1e-9:
            cur = cur.normalized()
            restd = (rest_world - parent_pos).normalized()
            ang = math.acos(min(1.0, max(-1.0, cur.dot(restd))))
            chord = 2 * self.bone_len * math.sin(ang / 2)
            if chord > p["amplitude"] and ang > 1e-6:
                target = 2 * math.asin(min(1.0, p["amplitude"] / (2 * self.bone_len)))
                tt = min(1.0, max(0.0, 1 - target / ang))
                s = math.sin(ang)
                newd = cur * (math.sin((1 - tt) * ang) / s) + restd * (math.sin(tt * ang) / s)
                self.pos = parent_pos + newd.normalized() * self.bone_len
        parent = pbone.parent
        mat = self._pw @ parent.bone.matrix_local.inverted() @ pbone.bone.matrix_local
        mat.translation = self.pos
        pbone.matrix_basis = pbone.bone.matrix_local.inverted() @ parent.bone.matrix_local @ self._pw.inverted() @ mat


def main():
    args = parse_args()
    scene = bpy.context.scene
    scene.render.fps = 24

    tgt = bpy.data.objects[args.target_arm]
    if tgt.animation_data:
        tgt.animation_data_clear()

    # --- import mocap source ---
    before = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=args.source, rotate_mode="NATIVE")
    src = next(o for o in bpy.data.objects if o not in before and o.type == "ARMATURE")
    src_action = src.animation_data.action
    f0, f1 = [int(x) for x in src_action.frame_range]
    n = f1 - f0 + 1
    print(f"source {src.name}: frames {f0}..{f1} ({n})")

    # rest worlds (armature space)
    def rest_world(arm, name):
        return arm.matrix_world @ arm.data.bones[name].matrix_local

    pairs = []
    for s_name, t_name in PAIRS:
        if s_name not in src.data.bones:
            print(f"WARN source missing {s_name} — skipping {t_name}")
            continue
        if t_name not in tgt.data.bones:
            print(f"WARN target missing {t_name} — skipping")
            continue
        s_bone = src.data.bones[s_name]
        t_bone = tgt.data.bones[t_name]
        S_rest = rest_world(src, s_name)
        T_rest = rest_world(tgt, t_name)
        # local-rest-relative motion of the source bone (precomputed)
        P_src_rest = rest_world(src, s_bone.parent.name) if s_bone.parent else Matrix()
        P_tgt_rest = rest_world(tgt, t_bone.parent.name) if t_bone.parent else Matrix()
        S_local_rest_inv = (P_src_rest.inverted() @ S_rest).inverted()
        T_local = P_tgt_rest.inverted() @ T_rest
        pairs.append((s_name, s_bone.parent.name if s_bone.parent else None,
                      t_name, t_bone.parent.name if t_bone.parent else None,
                      S_local_rest_inv, T_local, bone_depth(t_bone),
                      S_rest.inverted(), T_rest))
    pairs.sort(key=lambda p: p[6])
    print(f"{len(pairs)} pairs (incl. followers)")

    def leg_len(arm, names):
        pts = [arm.matrix_world @ arm.data.bones[n].head_local for n in names]
        return sum((b - a).length for a, b in zip(pts, pts[1:]))

    src_leg = leg_len(src, ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot"])
    tgt_leg = leg_len(tgt, ["DEF-spine", "DEF-thigh.L", "DEF-shin.L", "DEF-foot.L"])
    root_scale = tgt_leg / max(src_leg, 1e-6)
    print(f"leg lengths src={src_leg:.3f} tgt={tgt_leg:.3f} root_scale={root_scale:.3f}")

    # --- pass 1: retarget ---
    bpy.context.view_layer.objects.active = tgt
    tgt.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb in tgt.pose.bones:
        pb.rotation_mode = "QUATERNION"
    action = bpy.data.actions.new(name="MocapRetarget")
    tgt.animation_data_create()
    tgt.animation_data.action = action

    # armature-space rest matrices for every target bone (parents not in the
    # pair list stay at rest for the whole clip)
    rest_arm = {b.name: rest_world(tgt, b.name) for b in tgt.data.bones}

    hips_pose0 = None
    for i, f in enumerate(range(f0, f1 + 1)):
        out_f = i + 1
        scene.frame_set(f)
        bpy.context.view_layer.update()
        set_mats = {}  # target bone -> armature-space matrix set this frame
        for (s_name, s_parent, t_name, t_parent,
             S_local_rest_inv, T_local, _depth, S_rest_inv, T_rest) in pairs:
            s_pb = src.pose.bones[s_name]
            t_pb = tgt.pose.bones[t_name]
            if s_name == "Hips":
                # root: rotation relative to bind; translation = displacement
                # from the FIRST FRAME's pose (in-place), scaled, Z only
                D = S_rest_inv @ s_pb.matrix
                _dloc, drot, _dscl = D.decompose()
                if hips_pose0 is None:
                    hips_pose0 = s_pb.matrix.translation.copy()
                T_loc, T_rot, _ = T_rest.decompose()
                dz = (s_pb.matrix.translation.z - hips_pose0.z) * root_scale
                loc = Vector((T_loc.x, T_loc.y, T_loc.z + dz))
                M = Matrix.Translation(loc) @ (T_rot @ drot).to_matrix().to_4x4()
            else:
                # local-rest-relative rotation only — parent carries position
                P_src = src.pose.bones[s_parent].matrix if s_parent else Matrix()
                local_pose = P_src.inverted() @ s_pb.matrix
                rel = S_local_rest_inv @ local_pose
                if t_parent is None:
                    P_tgt = Matrix()
                elif t_parent in set_mats:
                    P_tgt = set_mats[t_parent]
                else:
                    P_tgt = rest_arm[t_parent]
                M = P_tgt @ T_local @ rel
            # basis from OUR OWN tracked parent matrix (never the stale
            # depsgraph); parent-rest factor included (Spring-class formula)
            if t_parent is None:
                P = Matrix()
                PL = Matrix()
            elif t_parent in set_mats:
                P = set_mats[t_parent]
                PL = rest_arm[t_parent]
            else:
                P = rest_arm[t_parent]
                PL = rest_arm[t_parent]
            t_pb.matrix_basis = t_pb.bone.matrix_local.inverted() @ PL @ P.inverted() @ M
            t_pb.keyframe_insert(data_path="location", frame=out_f)
            t_pb.keyframe_insert(data_path="rotation_quaternion", frame=out_f)
            t_pb.keyframe_insert(data_path="scale", frame=out_f)
            set_mats[t_name] = M
        if out_f % 24 == 0:
            print(f"retarget frame {out_f}/{n}")
    bpy.ops.object.mode_set(mode="OBJECT")
    scene.frame_start, scene.frame_end = 1, n

    # --- pass 2: jiggle springs driven by the baked mocap ---
    if not args.no_jiggle:
        springs = {}
        for name, prm in JIGGLE:
            pb = tgt.pose.bones.get(name)
            if pb and pb.parent:
                springs[name] = Spring(pb, prm)
            else:
                print(f"WARN jiggle bone missing: {name}")
        print(f"jiggle springs: {list(springs)}")
        deps = bpy.context.evaluated_depsgraph_get()
        SUB = 2
        h = (1.0 / 24) / SUB
        bpy.context.view_layer.objects.active = tgt
        tgt.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")
        for f in range(1, n + 1):
            scene.frame_set(f)
            deps.update()
            for s in springs.values():
                s.begin_frame()
            for _ in range(SUB):
                for s in springs.values():
                    s.step(h)
            for name, s in springs.items():
                pb = tgt.pose.bones[name]
                pb.keyframe_insert(data_path="location", frame=f)
                pb.keyframe_insert(data_path="rotation_quaternion", frame=f)
                pb.keyframe_insert(data_path="scale", frame=f)
            if f % 24 == 0:
                print(f"jiggle frame {f}/{n}")
        bpy.ops.object.mode_set(mode="OBJECT")

    # drop the source rig, keep the animated target scene
    bpy.data.objects.remove(src, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=args.out)
    print(f"SAVED {args.out} ({n} frames)")


if __name__ == "__main__":
    main()
