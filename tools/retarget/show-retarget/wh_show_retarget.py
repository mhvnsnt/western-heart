"""Cape Jones show-retarget, adapted for Western Heart — pure Python.

Sources (adapted, not copied):
  * cape-jones/tools/show-retarget/retarget_idle_cape.py — rotation-delta
    retarget of a CMU idle clip onto the 94-bone Cape Jones show rig,
    in place, parent-first. Target bones keep their own rest offsets.
  * cape-jones/tools/show-retarget/bonemap_cmu_to_capejones.json —
    CMU -> Cape Jones bone map (25 bones).
  * cape-jones/tools/show/bake_stance_ik.py — direction-based stance
    bake: orientation retarget fails where bone rolls differ (a bone
    can twist about its own axis without moving its segment), so ARMS
    are solved from source segment DIRECTIONS via shortest-arc
    rotation from rest direction to desired direction, while
    torso/legs keep the orientation bake.
  * cape-jones/tools/show/bake_cape_t3.py — orientation-bake predecessor
    of bake_stance_ik (kept as the non-arm path here).
  * cape-jones/tools/show-retarget/qa_weights.py — head-region weight
    QA: head verts dominated by spine/pelvis/lower bones = face-stretch
    risk, FAIL above a 5% suspect fraction.
  * cape-jones/tools/show-retarget/qa_render.py — T-pose QA render
    (EEVEE, front + side). The CI equivalent here is qa_render_svg(),
    a dependency-free stick-figure SVG; the EEVEE render stays owed.
  * cape-jones/tools/show/render_paired.py + show-retarget/export_stage.py
    — paired/stage render + export conventions; adapted as the
    report + SVG output shape, not as a Blender render.

Western Heart adaptations — read before using:
  * Target is WH, not the Cape Jones rig. The chain is
    show source -> Cape Jones deform bones -> WH-Canonical-22
    (cape_show_bonemap.json), NOT show -> Cape Jones rig directly.
  * MAP DISCREPANCY, flagged not hidden: the CJ bonemap file maps
    LeftArm -> upperarm_L, LeftForeArm -> forearm_L, LeftHand -> hand_L,
    while retarget_idle_cape.py's BONEMAP maps LeftShoulder ->
    upperarm_L, LeftArm -> forearm_L, LeftForeArm -> hand_L (shifted
    by one, as if the CJ shoulder bone were a clavicle). This module
    uses the BONEMAP FILE as primary (it matches the deform-bone
    names in the CJ rig) and lists the idle-script variant as
    ``idle_script_shifted_variant`` in the bonemap JSON. If you
    retarget a clip that was authored against the idle script, use
    that variant explicitly — do not mix the two.
  * Spine collapse: CJ spine_1..spine_4 + chest (5 segments) map onto
    WH Spine + Chest (2 bones). When two source bones map to one
    target, their deltas are sign-aligned and averaged (not picked
    arbitrarily); the intermediate spine motion is therefore
    smoothed, not preserved 1:1.
  * Fingers: CJ's bonemap carries only thumb + index. WH Mixamo49
    has full finger chains; middle/ring/pinky hold rest in the
    canonical map and are listed as unmapped in the QA report.
  * Cape: CJ cape/collar have no WH skeleton counterpart and are
    dropped from the skeleton retarget (routed to tools/cape/).
    A show idle with a cape therefore retargets the BODY and the
    cape is re-driven by the WH cape system, not by bone copy.
  * Axis: CJ show work is Z-up / faces -Y; WH-Canonical-22 is Y-up /
    faces +Z. Convert source rest positions with the same
    (x, y, z) -> (x, z, -y) rule as cape-rigging before stance IK.
  * Root: like retarget_tekken.py, root translation is scaled by
    the hip-height ratio, or zeroed with in_place=True (the game
    pins Hips anyway). Cape Jones idle is in-place by default.
  * Blender: all functions here are stdlib-only and CI-runnable.
    The Blender import/export (BVH/FBX/GLB in, animated GLB out)
    and the EEVEE QA render are NOT faked: see blender_steps().

Usage:
  python3 tools/retarget/show-retarget/wh_show_retarget.py retarget \
      --bonemap cape_show_bonemap.json --map show_to_wh_canonical \
      --pose pose.json --out out.json
  python3 tools/retarget/show-retarget/wh_show_retarget.py stance \
      --stance stance.json --out out.json
  python3 tools/retarget/show-retarget/wh_show_retarget.py qa \
      --weights weights.json --out report.json
  python3 tools/retarget/show-retarget/wh_show_retarget.py render-svg \
      --joints joints.json --out qa.svg
  python3 tools/retarget/show-retarget/wh_show_retarget.py blender-steps

Pose JSON shape: {"rest": {bone: [w, x, y, z]}, "pose": {bone: [w, x, y, z]},
  "parents": {bone: parent-or-null}, "root_translation": [x, y, z] (optional)}.
Target rest/parents live in the same file under "target_rest" /
"target_parents" when retargeting between two skeletons, or are
taken as identity rest when omitted.
"""
import argparse
import json
import math
import sys

IDENTITY = (1.0, 0.0, 0.0, 0.0)

# ---------------------------------------------------------------- quats
def qnorm(q):
    n = math.sqrt(sum(x * x for x in q))
    return tuple(x / n for x in q) if n > 1e-12 else IDENTITY

def qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)

def qinv(q):
    w, x, y, z = qnorm(q)
    return (w, -x, -y, -z)

def q_from_xyzw(v):
    q = (v[3], v[0], v[1], v[2])
    return qnorm(q) if q[0] >= 0 else tuple(-x for x in qnorm(q))

def q_rotate(q, v):
    """Rotate vector v by unit quat q."""
    qv = (0.0, v[0], v[1], v[2])
    r = qmul(qmul(q, qv), qinv(q))
    return [r[1], r[2], r[3]]

def q_average(quats):
    """Sign-aligned average of unit quats (for collapsed spine bones)."""
    if not quats:
        return IDENTITY
    ref = quats[0]
    acc = [0.0, 0.0, 0.0, 0.0]
    for q in quats:
        q = qnorm(q)
        if sum(a * b for a, b in zip(q, ref)) < 0:
            q = tuple(-x for x in q)
        for i in range(4):
            acc[i] += q[i]
    return qnorm(tuple(acc))

def shortest_arc(a, b):
    """Shortest-arc quat taking unit vector a to unit vector b."""
    def norm(v):
        n = math.sqrt(sum(x * x for x in v))
        return [x / n for x in v] if n > 1e-12 else [0.0, 0.0, 0.0]
    a, b = norm(a), norm(b)
    d = sum(a[i] * b[i] for i in range(3))
    if d > 0.999999:
        return IDENTITY
    if d < -0.999999:
        axis = [1.0, 0.0, 0.0] if abs(a[0]) < 0.9 else [0.0, 1.0, 0.0]
        axis = norm([axis[i] - a[i] * sum(axis[j] * a[j] for j in range(3)) for i in range(3)])
        return (0.0, axis[0], axis[1], axis[2])
    c = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    return qnorm((1.0 + d, c[0], c[1], c[2]))

def _depth(parents, bone, seen=None):
    seen = seen or set()
    p = parents.get(bone)
    if p is None or p in seen:
        return 0
    seen.add(bone)
    return 1 + _depth(parents, p, seen)

# ---------------------------------------------------------------- retarget
def retarget_pose(source_pose, source_rest, target_rest, bonemap, target_parents=None):
    """Rotation-delta retarget, parent-first (retarget_idle_cape.py math,
    local-space form as in WH retarget_tekken.py):

        delta        = source_pose * source_rest^-1
        target_pose  = delta * target_rest

    Target bones keep their own rest offsets (lengths never change).
    Unmapped target bones are absent from the result (caller holds
    them at rest); unmapped source bones are dropped and reported
    by retarget_report(). Colliding sources are averaged.
    """
    target_parents = target_parents or {}
    deltas = {}
    for src, tgt in bonemap.items():
        if src in source_pose:
            s_rest = tuple(source_rest.get(src, IDENTITY))
            deltas.setdefault(tgt, []).append(qmul(tuple(source_pose[src]), qinv(s_rest)))
    out = {}
    for tgt in sorted(deltas, key=lambda t: _depth(target_parents, t)):
        delta = q_average(deltas[tgt]) if len(deltas[tgt]) > 1 else deltas[tgt][0]
        t_rest = tuple(target_rest.get(tgt, IDENTITY))
        out[tgt] = qnorm(qmul(delta, t_rest))
    return out

def retarget_clip(frames, source_rest, target_rest, bonemap, target_parents=None,
                  hip_height_ratio=1.0, in_place=True):
    """Retarget a list of pose frames. Each frame may carry
    'root_translation'; it is scaled by hip_height_ratio, or zeroed
    when in_place (Cape Jones idle default; WH game pins Hips)."""
    out = []
    for fr in frames:
        pose = retarget_pose(fr.get("pose", {}), source_rest, target_rest, bonemap, target_parents)
        rt = fr.get("root_translation")
        if rt is None:
            rt_out = [0.0, 0.0, 0.0]
        elif in_place:
            rt_out = [0.0, 0.0, 0.0]
        else:
            rt_out = [x * hip_height_ratio for x in rt]
        out.append({"pose": {k: list(v) for k, v in pose.items()},
                    "root_translation": rt_out})
    return out

def retarget_report(source_bones, target_bones, bonemap):
    """Mapped / dropped source bones and held-at-rest target bones."""
    mapped_src = [s for s in bonemap if s in source_bones]
    dropped_src = [s for s in source_bones if s not in bonemap]
    mapped_tgt = {bonemap[s] for s in mapped_src}
    held_tgt = [t for t in target_bones if t not in mapped_tgt]
    return {"mapped_source": sorted(mapped_src), "dropped_source": sorted(dropped_src),
            "mapped_target": sorted(mapped_tgt), "held_at_rest_target": sorted(held_tgt),
            "n_mapped": len(mapped_src), "n_dropped": len(dropped_src),
            "n_held_at_rest": len(held_tgt)}

# ---------------------------------------------------------------- stance IK
def bake_stance_ik(orientation_pose, desired_arm_dirs, target_rest_quats,
                   target_rest_positions, target_parents, arm_map):
    """Direction-based stance bake (bake_stance_ik.py, data-only).

    orientation_pose: orientation-baked target quats (world) for
      torso/legs/clavicle/hand — kept as-is.
    desired_arm_dirs: {target_arm_bone: desired world direction}
      for upperarm/forearm bones, from source segment directions.
    target_rest_positions: {bone: world rest position}.
    arm_map: {target_arm_bone: child_bone} giving the segment whose
      rest direction is used (upperarm -> elbow bone, etc.).
    Returns world quats; convert to local with world_to_local().
    Arms: world = shortest_arc(rest_dir, desired_dir) * rest_world.
    """
    out = dict(orientation_pose)
    for bone, desired in desired_arm_dirs.items():
        child = arm_map.get(bone)
        if child is None or bone not in target_rest_positions or child not in target_rest_positions:
            continue
        rest_dir = [target_rest_positions[child][i] - target_rest_positions[bone][i] for i in range(3)]
        n = math.sqrt(sum(x * x for x in rest_dir))
        if n < 1e-12:
            continue
        rest_dir = [x / n for x in rest_dir]
        rest_world = tuple(target_rest_quats.get(bone, IDENTITY))
        out[bone] = qnorm(qmul(shortest_arc(rest_dir, desired), rest_world))
    return out

def world_to_local(world_quats, target_parents):
    """World quats -> local quats, parent-first."""
    out = {}
    for bone in sorted(world_quats, key=lambda b: _depth(target_parents, b)):
        parent = target_parents.get(bone)
        pw = world_quats.get(parent, IDENTITY) if parent else IDENTITY
        # Parent world quat here is the solved world quat if present,
        # else identity (rest) — callers pass the full solved dict.
        out[bone] = qnorm(qmul(qinv(pw), world_quats[bone]))
    return out

# ---------------------------------------------------------------- QA
SUSPECT_SUBSTRINGS = ("spine", "pelvis", "thigh", "shin", "hips", "root")

def qa_weights(vert_weights, vert_positions, height_axis=1, suspect_fraction_limit=0.05):
    """qa_weights.py, WH edition: height axis is Y (WH Y-up), not Z
    (CJ Z-up). Head region = top 16% of height. A head vert whose
    dominant bone is spine/pelvis/lower is suspect; verdict is
    FAIL-FACE-STRETCH-RISK above 5% suspects, else PASS. Also checks
    weight sums and unweighted verts (CJ's script only checked the
    head region; sums are added here because the cage weights in
    cape-rigging must sum to 1)."""
    if not vert_weights:
        return {"verdict": "FAIL-NO-VERTS", "n_verts": 0}
    coords = [p[height_axis] for p in vert_positions]
    zmin, zmax = min(coords), max(coords)
    head_cut = zmax - 0.16 * (zmax - zmin)
    head_verts = 0
    head_dominant = {}
    suspect = []
    sum_errors = []
    unweighted = 0
    for i, (weights, pos) in enumerate(zip(vert_weights, vert_positions)):
        total = sum(weights.values())
        sum_errors.append(abs(total - 1.0) if weights else 1.0)
        if not weights:
            unweighted += 1
            continue
        if pos[height_axis] < head_cut:
            continue
        head_verts += 1
        dom, w = max(weights.items(), key=lambda kv: kv[1])
        head_dominant[dom] = head_dominant.get(dom, 0) + 1
        if any(k in dom.lower() for k in SUSPECT_SUBSTRINGS):
            suspect.append({"vert": i, "bone": dom, "w": round(w, 3),
                            "height": round(pos[height_axis], 3)})
    sus_frac = len(suspect) / max(head_verts, 1)
    verdict = "FAIL-FACE-STRETCH-RISK" if sus_frac > suspect_fraction_limit else "PASS"
    return {"verdict": verdict, "n_verts": len(vert_weights),
            "head_verts": head_verts, "head_dominant": head_dominant,
            "suspect": suspect, "suspect_fraction": round(sus_frac, 4),
            "max_weight_sum_error": max(sum_errors) if sum_errors else 1.0,
            "unweighted_verts": unweighted}

def qa_render_svg(joint_positions, edges, title="WH show-retarget QA"):
    """qa_render.py, dependency-free edition: front + side
    stick-figure SVG (WH Y-up: front = X/Y, side = Z/Y). This is a
    pose QA plot, not an EEVEE render — the Blender render of a real
    character is still owed (see blender_steps)."""
    def project(pts, axes):
        xs = [p[axes[0]] for p in pts.values()]
        ys = [p[axes[1]] for p in pts.values()]
        lo_x, hi_x = min(xs), max(xs)
        lo_y, hi_y = min(ys), max(ys)
        span = max(hi_x - lo_x, hi_y - lo_y, 1e-6)
        def pt(p):
            return (20 + (p[axes[0]] - lo_x) / span * 260,
                    280 - (p[axes[1]] - lo_y) / span * 260)
        return pt
    front = project(joint_positions, (0, 1))
    side = project(joint_positions, (2, 1))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="320">'
             f'<text x="10" y="16" font-size="13">{title}</text>']
    for ox, proj, label in ((0, front, "front"), (300, side, "side")):
        parts.append(f'<text x="{ox + 10}" y="36" font-size="11">{label}</text>')
        for a, b in edges:
            if a in joint_positions and b in joint_positions:
                x1, y1 = proj(joint_positions[a]); x2, y2 = proj(joint_positions[b])
                parts.append(f'<line x1="{x1 + ox:.1f}" y1="{y1:.1f}" x2="{x2 + ox:.1f}" y2="{y2:.1f}" stroke="black" stroke-width="2"/>')
        for name, p in joint_positions.items():
            x, y = proj(p)
            parts.append(f'<circle cx="{x + ox:.1f}" cy="{y:.1f}" r="3" fill="red"/>'
                         f'<text x="{x + ox + 4:.1f}" y="{y:.1f}" font-size="9">{name}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

def blender_steps():
    return (
        "Blender steps (NOT run by this script — needs Blender + source/target models):\n"
        "  1. Import source clip (BVH/FBX) and target GLB in Blender, as in\n"
        "     retarget_idle_cape.py: source action -> target armature, in place.\n"
        "  2. Apply cape_show_bonemap.json (primary map, not the idle-script\n"
        "     shifted variant, unless the clip was authored against it).\n"
        "  3. For stance clips, run the direction-based arm solve\n"
        "     (bake_stance_ik) instead of pure orientation retarget.\n"
        "  4. Export animated GLB (single armature, skins on, morphs off).\n"
        "  5. EEVEE QA render front + side, T-pose (qa_render.py recipe) —\n"
        "     the SVG in this PR is the CI pose plot, not that render.\n"
    )

def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("retarget"); r.add_argument("--bonemap", required=True); r.add_argument("--map", required=True)
    r.add_argument("--pose", required=True); r.add_argument("--out", required=True); r.add_argument("--in-place", action="store_true", default=True)
    r.add_argument("--hip-ratio", type=float, default=1.0)
    s = sub.add_parser("stance"); s.add_argument("--stance", required=True); s.add_argument("--out", required=True)
    q = sub.add_parser("qa"); q.add_argument("--weights", required=True); q.add_argument("--out", required=True)
    g = sub.add_parser("render-svg"); g.add_argument("--joints", required=True); g.add_argument("--out", required=True)
    sub.add_parser("blender-steps")
    args = ap.parse_args(argv)
    if args.cmd == "blender-steps":
        print(blender_steps()); return 0
    if args.cmd == "retarget":
        bm = json.load(open(args.bonemap))
        mapping = bm["maps"][args.map]
        pose_doc = json.load(open(args.pose))
        out_pose = retarget_pose({k: tuple(v) for k, v in pose_doc["pose"].items()},
                                 {k: tuple(v) for k, v in pose_doc.get("rest", {}).items()},
                                 {k: tuple(v) for k, v in pose_doc.get("target_rest", {}).items()},
                                 mapping, pose_doc.get("target_parents", {}))
        report = retarget_report(list(pose_doc["pose"].keys()),
                                 list(pose_doc.get("target_bones", out_pose.keys())),
                                 mapping)
        json.dump({"pose": {k: list(v) for k, v in out_pose.items()}, "report": report},
                  open(args.out, "w"), indent=1)
        print(f"RETARGET mapped={report['n_mapped']} dropped={report['n_dropped']} held_at_rest={report['n_held_at_rest']} -> {args.out}")
    elif args.cmd == "stance":
        doc = json.load(open(args.stance))
        world = bake_stance_ik({k: tuple(v) for k, v in doc["orientation_pose"].items()},
                               doc["desired_arm_dirs"], {k: tuple(v) for k, v in doc["target_rest_quats"].items()},
                               doc["target_rest_positions"], doc["target_parents"], doc["arm_map"])
        local = world_to_local(world, doc["target_parents"])
        json.dump({"world": {k: list(v) for k, v in world.items()},
                   "local": {k: list(v) for k, v in local.items()}}, open(args.out, "w"), indent=1)
        print(f"STANCE bones={len(local)} -> {args.out}")
    elif args.cmd == "qa":
        doc = json.load(open(args.weights))
        report = qa_weights(doc["vert_weights"], doc["vert_positions"],
                            height_axis=doc.get("height_axis", 1))
        json.dump(report, open(args.out, "w"), indent=1)
        print(f"QA verdict={report['verdict']} suspect_fraction={report['suspect_fraction']} -> {args.out}")
    elif args.cmd == "render-svg":
        doc = json.load(open(args.joints))
        svg = qa_render_svg(doc["positions"], [tuple(e) for e in doc["edges"]],
                            doc.get("title", "WH show-retarget QA"))
        open(args.out, "w").write(svg)
        print(f"SVG -> {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
