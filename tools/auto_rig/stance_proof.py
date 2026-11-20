#!/usr/bin/env python3
"""tools/auto_rig/stance_proof.py — stance + motion proof for rigged models.

Parent refinement 2026-10-22: T-pose/bind-pose alone is NOT sufficient proof.
For each rigged model, proof must include:
  1. BIND-POSE overlay (render_poses.py, as before)
  2. IDLE STANCE CHECK: fighter in fighting stance — stance correct?
     All parts facing right IN THE STANCE? (the Julia backwards-shins case)
  3. ANIMATION CHECK: idle, walk, basic strikes — do parts stay correct
     through motion? Flag breaks/flips/stretches.

This script poses the rigged model in the character's REAL T3 fighting stance
(t3_neutral), walk (t3_walk_fwd), and renders front/side views. It uses the
same world-delta retarget math as the game (t3anims.js retargetT3Clips) and
the same facing correction (bankFacing -> turn 180 deg when knees face back).
Poses are SET directly (no keyframing) for speed on dense meshes.

The motion gate is covered by the pipeline's baked CMU clip + anim_check
(edge p99.9 < 2.5). This script covers the STANCE gate: foot yaw in stance
(the backwards-feet check) + viewed renders.

Usage (inside Blender):
    blender -b --factory-startup --python stance_proof.py -- \
        --in RIGGED.glb --bank-dir game/assets/anim/t3/nina \
        --render-dir RENDERS/ [--frames 15,8]

Writes RENDERS/stance_proof_metrics.json with foot yaw + facing info.
"""
import argparse
import json
import math
import os
import sys


def load_bank(bank_dir):
    skel = json.load(open(os.path.join(bank_dir, "skeleton.json")))
    clips = {}
    for name in ("t3_neutral", "t3_walk_fwd"):
        p = os.path.join(bank_dir, name + ".json")
        if os.path.exists(p):
            clips[name] = json.load(open(p))
    return skel, clips


def bank_facing(skel, datas):
    """Port of t3anims.js bankFacing."""
    P = {j["name"]: j["rest"] for j in skel["joints"]}
    par = {j["name"]: j["parent"] for j in skel["joints"]}
    order = [j["name"] for j in skel["joints"]]

    def qmul(a, b):
        return [a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],
                a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],
                a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],
                a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]]

    def qrot(q, v):
        x, y, z, w = q
        tx = 2*(y*v[2]-z*v[1]); ty = 2*(z*v[0]-x*v[2]); tz = 2*(x*v[1]-y*v[0])
        return [v[0]+w*tx+(y*tz-z*ty), v[1]+w*ty+(z*tx-x*tz), v[2]+w*tz+(x*ty-y*tx)]

    fwd_sum = left_sum = samples = 0
    for data in datas:
        if not data or "rot_xyzw" not in data:
            continue
        n = max((len(v) for v in data["rot_xyzw"].values() if v), default=0)
        for f in range(0, n, max(1, n // 8)):
            G, X = {}, {}
            for j in order:
                r = data["rot_xyzw"].get(j)
                q = r[min(f, len(r)-1)] if r else [0, 0, 0, 1]
                p = par[j]
                if p and p in G:
                    G[j] = qmul(G[p], q)
                    ox = [P[j][0]-P[p][0], P[j][1]-P[p][1], P[j][2]-P[p][2]]
                    o = qrot(G[p], ox)
                    X[j] = [X[p][0]+o[0], X[p][1]+o[1], X[p][2]+o[2]]
                else:
                    G[j] = q; X[j] = list(P[j])
            if "Hips" not in G:
                continue
            hx = qrot(G["Hips"], [1, 0, 0])
            fx, fz = -hx[2], hx[0]
            fl = math.hypot(fx, fz)
            if fl < 1e-6:
                continue
            fx /= fl; fz /= fl
            for s in ("Left", "Right"):
                a, k, e = X.get(s+"UpLeg"), X.get(s+"Leg"), X.get(s+"Foot")
                if not (a and k and e):
                    continue
                ox = k[0]-(a[0]+e[0])/2; oz = k[2]-(a[2]+e[2])/2
                fwd_sum += ox*fx + oz*fz
                left_sum += ox*fz - oz*fx
                samples += 1
    return {"turned": samples > 0 and fwd_sum < 0,
            "knee_deg": math.degrees(math.atan2(left_sum, fwd_sum)) if samples else 0.0,
            "samples": samples}


def swap_lr(n):
    if n.startswith("Left"):
        return "Right" + n[4:]
    if n.startswith("Right"):
        return "Left" + n[5:]
    return n


def turn_data(data):
    rot = {}
    for b, arr in data["rot_xyzw"].items():
        rot[swap_lr(b)] = [[-q[0], q[1], -q[2], q[3]] for q in arr]
    data["rot_xyzw"] = rot
    if data.get("bones"):
        data["bones"] = [swap_lr(b) for b in data["bones"]]


def pose_from_clip(rig, tgt_rest, tgt_parent, tgt_offset, order_t,
                   name_map, P, par, order, rot, frame, C, Cinv):
    """Set the rig's pose from a T3 clip frame (no keyframing)."""
    from mathutils import Matrix, Quaternion
    # Source FK in glTF space.
    G = {}
    for j in order:
        r = rot.get(j)
        if r:
            qv = r[min(frame, len(r)-1)]
            q = Quaternion((qv[3], qv[0], qv[1], qv[2]))
        else:
            q = Quaternion((1, 0, 0, 0))
        p = par[j]
        G[j] = (G[p] @ q) if (p and p in G) else q
    # Apply deltas to target.
    world_rot, world_pos, eff = {}, {}, {}
    for name in order_t:
        p = tgt_parent[name]
        if name in name_map:
            d = C @ G.get(name, Quaternion((1, 0, 0, 0))) @ Cinv
        elif p is not None:
            d = eff[p]
        else:
            d = Quaternion((1, 0, 0, 0))
        eff[name] = d
        rest_rot = tgt_rest[name].to_quaternion()
        world_rot[name] = d @ rest_rot
        if p is None:
            world_pos[name] = tgt_offset[name].copy()
        else:
            world_pos[name] = world_pos[p] + (world_rot[p] @ tgt_offset[name])
        m = Matrix.Translation(world_pos[name]) @ world_rot[name].normalized().to_matrix().to_4x4()
        if p is None:
            rest_local = tgt_rest[name]
            local_m = m
        else:
            parent_m = Matrix.Translation(world_pos[p]) @ world_rot[p].normalized().to_matrix().to_4x4()
            local_m = parent_m.inverted() @ m
            rest_local = tgt_rest[p].inverted() @ tgt_rest[name]
        basis = rest_local.inverted() @ local_m
        t_pb = rig.pose.bones[name]
        t_pb.matrix_basis = basis


def main():
    import bpy
    from mathutils import Quaternion, Vector

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--bank-dir", required=True)
    ap.add_argument("--render-dir", required=True)
    ap.add_argument("--frames", default="15,8",
                    help="frame indices: neutral_frame,walk_frame")
    a = ap.parse_args()

    skel, clips = load_bank(a.bank_dir)
    if "t3_neutral" not in clips:
        raise RuntimeError("t3_neutral.json not found in %s" % a.bank_dir)

    facing = bank_facing(skel, list(clips.values()))
    print("bank facing: turned=%s knee=%.1f" % (facing["turned"], facing["knee_deg"]), flush=True)
    if facing["turned"]:
        for d in clips.values():
            turn_data(d)

    P = {j["name"]: Vector(j["rest"]) for j in skel["joints"]}
    par = {j["name"]: j["parent"] for j in skel["joints"]}
    order = [j["name"] for j in skel["joints"]]

    C = Quaternion((math.cos(math.radians(-45)), math.sin(math.radians(-45)), 0, 0))
    Cinv = C.inverted()

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.inp)
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    rig = max(arms, key=lambda x: len(x.data.bones))
    scene = bpy.context.scene

    tgt_rest = {b.name: b.matrix_local.copy() for b in rig.data.bones}
    tgt_parent = {b.name: (b.parent.name if b.parent else None) for b in rig.data.bones}
    tgt_offset = {}
    for name, rw in tgt_rest.items():
        p = tgt_parent[name]
        if p is None:
            tgt_offset[name] = rw.translation.copy()
        else:
            pr = tgt_rest[p]
            tgt_offset[name] = pr.to_quaternion().inverted() @ (rw.translation - pr.translation)
    order_t, seen = [], set()
    def visit(n):
        if n in seen: return
        seen.add(n)
        if tgt_parent[n]: visit(tgt_parent[n])
        order_t.append(n)
    for n in tgt_rest: visit(n)
    rig_bones = set(tgt_rest)
    name_map = {c: c for c in order if c in rig_bones}
    print("mapped %d/%d" % (len(name_map), len(order)), flush=True)

    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="POSE")
    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"

    os.makedirs(a.render_dir, exist_ok=True)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.film_transparent = True
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
    for o in meshes:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    center = (mn + mx) / 2; height = max(0.5, mx.z - mn.z)
    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    tgt = bpy.data.objects.new("tgt", None)
    tgt.location = (center.x, center.y, center.z)
    scene.collection.objects.link(tgt)
    con = cam.constraints.new(type="TRACK_TO")
    con.target = tgt; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
    light_data = bpy.data.lights.new("l", type="SUN")
    light_data.energy = 3.0
    light = bpy.data.objects.new("l", light_data)
    light.location = (2, -2, 4)
    scene.collection.objects.link(light)

    n_fr, w_fr = (int(x) for x in a.frames.split(","))
    metrics = {"bank": os.path.basename(a.bank_dir.rstrip("/")),
               "facing": facing, "renders": []}

    # STANCE
    rot = clips["t3_neutral"]["rot_xyzw"]
    n = max(len(v) for v in rot.values() if v)
    pose_from_clip(rig, tgt_rest, tgt_parent, tgt_offset, order_t, name_map,
                   P, par, order, rot, min(n_fr, n-1), C, Cinv)
    bpy.context.view_layer.update()
    # Foot yaw (Julia check).
    foot_yaw = {}
    for side in ("Left", "Right"):
        fb = rig.pose.bones.get(side + "Foot")
        if fb:
            fw = (rig.matrix_world @ fb.matrix).to_quaternion() @ Vector((0, 1, 0))
            foot_yaw[side] = round(math.degrees(math.atan2(fw.x, -fw.y)), 1)
    metrics["foot_yaw_deg_in_stance"] = foot_yaw
    print("foot yaw: %s" % foot_yaw, flush=True)
    d = height * 2.2
    for label, view in (("stance_front", (0, -1, 0.25)), ("stance_side", (1, 0, 0.25))):
        cam.location = (center.x + view[0]*d, center.y + view[1]*d, center.z + view[2]*d)
        p = os.path.join(a.render_dir, label + ".png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        metrics["renders"].append(label + ".png")

    # WALK (one mid frame)
    if "t3_walk_fwd" in clips:
        rot = clips["t3_walk_fwd"]["rot_xyzw"]
        n = max(len(v) for v in rot.values() if v)
        pose_from_clip(rig, tgt_rest, tgt_parent, tgt_offset, order_t, name_map,
                       P, par, order, rot, min(w_fr, n-1), C, Cinv)
        bpy.context.view_layer.update()
        cam.location = (center.x, center.y - d, center.z + 0.25*d)
        p = os.path.join(a.render_dir, "walk_mid.png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        metrics["renders"].append("walk_mid.png")

    with open(os.path.join(a.render_dir, "stance_proof_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=1)
    print("STANCE PROOF DONE", flush=True)


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    sys.argv = [sys.argv[0]] + argv
    main()
