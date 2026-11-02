"""Cape Jones rigging, adapted for Western Heart — pure Python (stdlib only).

Sources (adapted, not copied):
  * cape-jones/tools/rigging/blenrig_fit.py — BlenRig 6 reproportion fit:
    scale rest pose, fit guide bones to measured joints, rest-bake.
  * cape-jones/tools/rigging/blenrig_warp.py — edit-mode warp: every
    non-guide bone follows its nearest guide's transform.
  * cape-jones/tools/rigging/blenrig_setup.py — BlenRig biped setup;
    faces -Y, feet at z=0, L=+X (BlenRig convention).
  * cape-jones/tools/rigging/joint_detect.py — cross-section joint
    detector: slice the mesh, cluster each slice, read joint heights
    from radius minima/maxima (knee = radius minimum between thigh
    and calf bulges; ankle = low radius minimum).
  * cape-jones/tools/rigging/weight_cage.py — MDEF cage fit + procedural
    zone weights: locked bones (head/hands/feet) get weight 1.0,
    stretch bones get 1/d^2 falloff, max 4 influences, normalised.
  * cape-jones/blender523-rig-fixed-20261101 + blender523-rig-refined-20261101
    — 2D toon peg rig seating rules. Those are PEG rules (17 pegs,
    11 drawings), not a 3D skeleton: they are carried here only as a
    pose/seating gate (see cape_rig_map.json), never as bones, and no
    .blend binary from cape-jones is copied into this repo.

Western Heart adaptations — read before using:
  * NO 0.544 scale. Cape Jones shrank the BlenRig default biped
    (1.70 m) to its 0.9248 m toon (blenrig_fit.py, "REST SCALED x0.544").
    Western Heart characters are realistic-proportioned, so guides are
    fitted in target space at target height. If you do fit a toon-sized
    character, pass rest_scale explicitly; it defaults to 1.0.
  * Axis: Cape Jones joint detection runs Z-up, faces -Y, L=+X.
    WH-Canonical-22 (lab/skeleton/canonical_skeleton.json) is Y-up,
    faces +Z, left=+X. fit_guides() works in whatever space its input
    joints are in; convert with to_wh_space() before feeding WH data.
  * Skeleton: Cape Jones show rig is 94 bones with cape bones, BlenRig
    ``*_str`` guides and pole bones. WH targets are the verified
    WH-Canonical-22 core plus the Mixamo49 finger/toe extension in
    tools/retarget/tekken-bonemap.json. Guides, poles and cape bones
    have no WH skeleton counterpart and are dropped from the skeleton
    map (cape goes to the WH cape accessory system, not to a bone).
    The full MB-Lab skeleton named in the wiring brief (71 joints) is
    NOT enumerated in tools/retarget or tools/mb-lab at the base head,
    so this module is skeleton-agnostic: pass any target joint list
    and unmapped joints hold rest. See cape_rig_map.json.
  * Blender: the pure functions below import with no Blender and no
    third-party package, so they run in CI. The Blender steps
    (BlenRig addon install, MDEF cage bind, EEVEE render) are NOT
    faked here: blender_steps() prints the exact headless commands,
    and they need a real Blender 5.2.3 LTS binary plus the BlenRig
    addon. MB-Lab itself is pinned to Blender 4.0.2 in
    tools/mb-lab/README.md; do not claim MB-Lab runs on 5.2.3 until
    a headless run proves it. GPU/Windows-only steps stay owed.

Usage (no Blender needed):
  python3 tools/retarget/cape-rigging/cape_rig.py fit \
      --joints joints.json --out guides.json
  python3 tools/retarget/cape-rigging/cape_rig.py cage \
      --skeleton skeleton.json --out weights.json
  python3 tools/retarget/cape-rigging/cape_rig.py detect \
      --verts verts.json --out joints.json
  python3 tools/retarget/cape-rigging/cape_rig.py blender-steps
"""
import argparse
import json
import math
import sys

# ---------------------------------------------------------------- vectors
def vadd(a, b):
    return [a[i] + b[i] for i in range(3)]

def vsub(a, b):
    return [a[i] - b[i] for i in range(3)]

def vscale(a, s):
    return [a[i] * s for i in range(3)]

def vlen(a):
    return math.sqrt(sum(x * x for x in a))

def vnorm(a):
    n = vlen(a)
    return [x / n for x in a] if n > 1e-12 else [0.0, 0.0, 0.0]

def vdot(a, b):
    return sum(a[i] * b[i] for i in range(3))

def vcross(a, b):
    return [a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]]

def dist_point_segment(p, a, b):
    """Distance from point p to segment a-b, plus closest parameter t."""
    ab = vsub(b, a)
    denom = vdot(ab, ab)
    t = 0.0 if denom < 1e-12 else max(0.0, min(1.0, vdot(vsub(p, a), ab) / denom))
    closest = vadd(a, vscale(ab, t))
    return vlen(vsub(p, closest)), t

def to_wh_space(p):
    """Cape Jones Z-up / faces -Y -> WH-Canonical Y-up / faces +Z.

    CJ (x, y, z) with up +Z and facing -Y maps to WH (x, z, -y):
    the old up axis becomes WH up (Y), the old facing axis flips.
    """
    return [p[0], p[2], -p[1]]

# ---------------------------------------------------------------- fit
def fit_guides(joints, rest_scale=1.0):
    """BlenRig-style guide targets from measured joints.

    Mirrors blenrig_fit.py / blenrig_warp.py guide tables (torso,
    neck/head, per-side limbs, poles, fingers) but returns plain
    ``{guide: [head, tail]}`` data instead of touching a Blender
    armature, so it is testable without Blender. ``rest_scale``
    replaces Cape Jones' hard-coded 0.544: WH uses 1.0.
    """
    def V(key):
        v = joints[key]
        return vscale([float(v[0]), float(v[1]), float(v[2])], rest_scale)

    def need(*keys):
        return all(k in joints and joints[k] is not None for k in keys)

    T = {}
    if need("hip_z", "waist_z", "chest_z", "neck_z", "chin_z"):
        hip_z = joints["hip_z"] * rest_scale
        waist_z = joints["waist_z"] * rest_scale
        chest_z = joints["chest_z"] * rest_scale
        neck_z = joints["neck_z"] * rest_scale
        chin_z = joints["chin_z"] * rest_scale
        T["master_torso_str"] = [[0, 0, hip_z - 0.02 * rest_scale], [0, 0, chest_z]]
        T["pelvis_str"] = [[0, 0, hip_z - 0.04 * rest_scale], [0, 0, hip_z + 0.03 * rest_scale]]
        T["spine_ctrl_1_str"] = [[0, 0, waist_z - 0.07 * rest_scale], [0, 0, waist_z + 0.01 * rest_scale]]
        T["spine_ctrl_2_str"] = [[0, 0, waist_z + 0.01 * rest_scale], [0, 0, (waist_z + chest_z) / 2]]
        T["spine_ctrl_3_str"] = [[0, 0, (waist_z + chest_z) / 2], [0, 0, chest_z]]
        T["spine_ctrl_4_str"] = [[0, 0, chest_z - 0.02 * rest_scale], [0, 0, chest_z + 0.05 * rest_scale]]
        T["neck_ctrl_2_str"] = [[0, -0.01 * rest_scale, neck_z - 0.03 * rest_scale],
                                [0, -0.015 * rest_scale, neck_z + 0.005 * rest_scale]]
        T["neck_ctrl_3_str"] = [[0, -0.015 * rest_scale, neck_z + 0.005 * rest_scale],
                                [0, -0.02 * rest_scale, neck_z + 0.035 * rest_scale]]
        T["neck_ctrl_4_str"] = [[0, -0.02 * rest_scale, neck_z + 0.035 * rest_scale],
                                [0, -0.02 * rest_scale, chin_z]]
        if need("head_top"):
            T["head_str"] = [[0, -0.02 * rest_scale, chin_z], V("head_top")]
        if need("face_y"):
            face_y = joints["face_y"] * rest_scale
            T["face_mstr_str"] = [[0, face_y + 0.055 * rest_scale, 0.862 * rest_scale],
                                  [0, face_y + 0.005 * rest_scale, 0.862 * rest_scale]]
    for side, s in (("L", 1), ("R", -1)):
        if not need(f"shoulder_{side}", f"elbow_{side}", f"wrist_{side}",
                    f"fingertip_{side}", f"hip_{side}", f"knee_{side}",
                    f"ankle_{side}", f"toe_{side}", f"heel_{side}"):
            continue
        sh, el, wr = V(f"shoulder_{side}"), V(f"elbow_{side}"), V(f"wrist_{side}")
        tip = V(f"fingertip_{side}")
        hip, knee, ank, toe = V(f"hip_{side}"), V(f"knee_{side}"), V(f"ankle_{side}"), V(f"toe_{side}")
        heel = V(f"heel_{side}")
        neck_z = joints["neck_z"] * rest_scale
        T[f"clavi_str_{side}"] = [[0, -0.01 * rest_scale, neck_z], sh]
        T[f"shoulder_str_{side}"] = [sh, el]
        T[f"elbow_str_{side}"] = [el, wr]
        T[f"wrist_str_{side}"] = [wr, tip]
        T[f"hand_str_{side}"] = [wr, tip]
        T[f"elbow_pole_str_{side}"] = [vadd(el, [0, 0.24 * rest_scale, -0.02 * rest_scale]),
                                       vadd(el, [0, 0.30 * rest_scale, -0.02 * rest_scale])]
        T[f"pelvis_str_{side}"] = [hip, knee]
        T[f"knee_str_{side}"] = [knee, ank]
        T[f"ankle_str_{side}"] = [ank, toe]
        T[f"foot_str_{side}"] = [ank, toe]
        T[f"toe_str_1_{side}"] = [toe, vadd(toe, [0, -0.028 * rest_scale, -0.004 * rest_scale])]
        T[f"toe_str_2_{side}"] = [vadd(toe, [0, -0.028 * rest_scale, -0.004 * rest_scale]),
                                  vadd(toe, [0, -0.052 * rest_scale, -0.006 * rest_scale])]
        T[f"sole_str_{side}"] = [heel, toe]
        T[f"knee_pole_str_{side}"] = [vadd(knee, [0, -0.24 * rest_scale, 0.02 * rest_scale]),
                                      vadd(knee, [0, -0.30 * rest_scale, 0.02 * rest_scale])]
        if need(f"finger_dir_{side}", f"palm_{side}", f"finger_len_{side}"):
            fdir = vnorm(V(f"finger_dir_{side}"))
            palm = V(f"palm_{side}")
            flen = max(0.035 * rest_scale, joints[f"finger_len_{side}"] * rest_scale * 2.2)
            perp = vnorm(vcross(fdir, [0, 0, 1])) or [1, 0, 0]
            if vlen(vcross(fdir, [0, 0, 1])) < 1e-6:
                perp = [1, 0, 0]
            for fi, fn in enumerate(["ind", "mid", "ring", "lit"]):
                base = vadd(vadd(palm, vscale(fdir, 0.008 * rest_scale)),
                            vscale(perp, (-0.018 + fi * 0.012) * rest_scale))
                seg = flen / 5
                for sg in range(1, 6):
                    h = vadd(base, vscale(fdir, (sg - 1) * seg))
                    T[f"fing_{fn}_str_{sg}_{side}"] = [h, vadd(h, vscale(fdir, seg))]
            thumb = V(f"thumb_{side}") if joints.get(f"thumb_{side}") else vadd(palm, [0, -0.02 * rest_scale, -0.01 * rest_scale])
            tdir = vnorm(vadd(vscale(fdir, 0.6), [0, -0.55, -0.45]))
            tlen = flen * 0.8
            seg = tlen / 4
            for sg in range(1, 5):
                h = vadd(thumb, vscale(tdir, (sg - 1) * seg))
                T[f"fing_thumb_str_{sg}_{side}"] = [h, vadd(h, vscale(tdir, seg))]
    return T

def warp_bones(guide_targets, bones):
    """blenrig_warp.py, data-only: for each non-guide bone, record its
    nearest guide and distance, so the Blender warp step knows which
    guide transform to apply. Returns {bone: {head, tail,
    nearest_guide, nearest_guide_dist}}. Guide bones pass through
    with their fitted head/tail."""
    out = {}
    guides = list(guide_targets.items())
    for name, (head, tail) in bones.items():
        if name in guide_targets:
            out[name] = {"head": guide_targets[name][0], "tail": guide_targets[name][1],
                         "nearest_guide": name, "nearest_guide_dist": 0.0}
            continue
        best, best_d = None, 1e18
        for gname, (gh, gt) in guides:
            d, _ = dist_point_segment(head, gh, gt)
            if d < best_d:
                best, best_d = gname, d
        out[name] = {"head": head, "tail": tail,
                     "nearest_guide": best, "nearest_guide_dist": best_d}
    return out

# ---------------------------------------------------------------- detect
def _slice_clusters(pts, cell=0.02, min_n=8):
    """Grid-cluster one horizontal slice (x/y plane), CJ joint_detect
    union-find over 8-neighbourhood, simplified to gap clustering on
    sorted cell keys. Returns [{x, y, r, n}]."""
    cells = {}
    for p in pts:
        cells.setdefault((int(math.floor(p[0] / cell)), int(math.floor(p[1] / cell))), []).append(p)
    # Union-find over neighbouring cells.
    parent = {c: c for c in cells}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for c in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (c[0] + dx, c[1] + dy)
                if n in cells and find(c) != find(n):
                    parent[find(c)] = find(n)
    groups = {}
    for c, idxs in cells.items():
        groups.setdefault(find(c), []).extend(idxs)
    out = []
    for idxs in groups.values():
        if len(idxs) < min_n:
            continue
        cx = sum(p[0] for p in idxs) / len(idxs)
        cy = sum(p[1] for p in idxs) / len(idxs)
        dists = sorted(math.hypot(p[0] - cx, p[1] - cy) for p in idxs)
        r = dists[int(0.9 * (len(dists) - 1))]
        out.append({"x": cx, "y": cy, "r": r, "n": len(idxs)})
    return out

def detect_joints(verts, height=None):
    """Cross-section joint detection, adapted from joint_detect.py.

    Input: iterable of [x, y, z] in CJ space (faces -Y, up +Z,
    feet at z=0, L=+X). Output: joint dict in the same key style as
    /tmp/cj_joints.json. CJ's absolute z bands were tuned for a
    0.9248 m toon; here they scale by detected height / 0.9248, so
    the same detector works on WH-height characters. Where CJ
    hard-coded a value from one character (waist_z = 0.56), this
    version uses the anatomical midpoint between hip and chest.
    """
    V = [list(map(float, p)) for p in verts]
    if not V:
        raise ValueError("no vertices")
    zmin = min(p[2] for p in V)
    zmax = max(p[2] for p in V)
    height = height or (zmax - zmin)
    scale = height / 0.9248 if height > 0 else 1.0

    def profile(z0, z1, step):
        rows = []
        z = z0
        while z <= z1 + 1e-9:
            pts = [p for p in V if abs(p[2] - z) < 0.012 * scale]
            rows.append((z, _slice_clusters(pts, cell=0.035 * scale, min_n=6)))
            z += step
        return rows

    prof = profile(0.0, zmax, 0.02 * scale)
    # ---- legs: two clusters near centre, |x| in (0.015, 0.20)*scale
    leg_prof = []
    for z, cl in prof:
        if z > 0.52 * scale or z < 0.01:
            continue
        legs = [c for c in cl if abs(c["y"]) < 0.09 * scale and 0.015 * scale < abs(c["x"]) < 0.20 * scale]
        if len(legs) == 2:
            legs.sort(key=lambda c: c["x"])
            rgt, lft = legs[0], legs[1]
            leg_prof.append((z, lft["x"], lft["r"], rgt["x"], rgt["r"], lft["y"], rgt["y"]))
    if len(leg_prof) < 5:
        raise ValueError("leg profile too short: %d rows (need T-pose legs)" % len(leg_prof))
    crotch_z = max(r[0] for r in leg_prof)
    J = {"crotch_z": crotch_z, "hip_z": crotch_z + 0.035 * scale}
    top = max(leg_prof, key=lambda r: r[0])
    J["hip_L"] = [top[1], top[5], J["hip_z"]]
    J["hip_R"] = [top[3], top[6], J["hip_z"]]
    for side, (xi, ri, yi) in {"L": (1, 2, 5), "R": (3, 4, 6)}.items():
        zs = [r[0] for r in leg_prof]
        rs = [r[ri] for r in leg_prof]
        thigh = [(z, r) for z, r in zip(zs, rs) if 0.30 * scale < z < 0.46 * scale]
        calf = [(z, r) for z, r in zip(zs, rs) if 0.06 * scale < z < 0.22 * scale]
        zt = max(thigh, key=lambda t: t[1])[0]
        zc = max(calf, key=lambda t: t[1])[0]
        band = [(z, r) for z, r in zip(zs, rs) if zc <= z <= zt]
        zk = min(band, key=lambda t: t[1])[0]
        i = min(range(len(zs)), key=lambda k: abs(zs[k] - zk))
        J[f"knee_{side}"] = [leg_prof[i][xi], leg_prof[i][yi], zk]
        low = [(z, r) for z, r in zip(zs, rs) if z < 0.10 * scale]
        za = min(low, key=lambda t: t[1])[0]
        i = min(range(len(zs)), key=lambda k: abs(zs[k] - za))
        J[f"ankle_{side}"] = [leg_prof[i][xi], leg_prof[i][yi], za]
        # feet: lowest verts near the ankle x
        ax = J[f"ankle_{side}"][0]
        foot = [p for p in V if p[2] < J[f"ankle_{side}"][2] + 0.02 * scale and abs(p[0] - ax) < 0.07 * scale]
        if foot:
            J[f"toe_{side}"] = [ax, min(p[1] for p in foot), min(p[2] for p in foot) + 0.012 * scale]
            J[f"heel_{side}"] = [ax, max(p[1] for p in foot), min(p[2] for p in foot) + 0.012 * scale]
    # ---- torso: widest central cluster = chest; waist = midpoint
    def torso_radius(zc):
        pts = [p for p in V if abs(p[2] - zc) < 0.012 * scale]
        cl = [c for c in _slice_clusters(pts, cell=0.035 * scale, min_n=6)
              if abs(c["x"]) < 0.16 * scale and abs(c["y"]) < 0.16 * scale]
        if not cl:
            return 0.0
        return max(cl, key=lambda c: c["n"])["r"] * 2
    chest_band = []
    z = 0.60 * scale
    while z <= 0.74 * scale:
        chest_band.append((z, torso_radius(z)))
        z += 0.02 * scale
    J["chest_z"] = max(chest_band, key=lambda t: t[1])[0] if chest_band else 0.68 * scale
    J["waist_z"] = (J["hip_z"] + J["chest_z"]) / 2
    # ---- shoulder / arms: T-pose arms run along X at shoulder height
    J["shoulder_z"] = J["chest_z"] + 0.05 * scale
    J["neck_z"] = J["chest_z"] + 0.12 * scale
    band = [p for p in V if abs(p[2] - J["shoulder_z"]) < 0.06 * scale and abs(p[1]) < 0.10 * scale]
    if band:
        torso_hw = sorted(abs(p[0]) for p in band)[int(0.92 * (len(band) - 1))]
    else:
        torso_hw = 0.12 * scale
    for side, s in {"L": 1, "R": -1}.items():
        arm_pts = [p for p in band if s * p[0] > torso_hw]
        if arm_pts:
            # Arm profile along X: radius minima = elbow, then wrist.
            xs = []
            x = torso_hw
            xmax = max(abs(p[0]) for p in arm_pts)
            while x <= xmax:
                seg = [p for p in arm_pts if abs(abs(p[0]) - x) < 0.02 * scale]
                if len(seg) >= 6:
                    cy = sum(p[1] for p in seg) / len(seg)
                    cz = sum(p[2] for p in seg) / len(seg)
                    dists = sorted(math.hypot(p[1] - cy, p[2] - cz) for p in seg)
                    xs.append((x, cy, cz, dists[int(0.9 * (len(dists) - 1))]))
                x += 0.02 * scale
            if len(xs) >= 4:
                mid = [r for r in xs if 0.33 * scale < r[0] - torso_hw < 0.55 * scale]
                # Fallback bands relative to arm start, mirroring CJ's
                # absolute bands scaled by height.
                def _min_in(lo, hi):
                    cand = [r for r in xs if lo <= r[0] <= hi]
                    return min(cand, key=lambda r: r[3]) if cand else None
                el = _min_in(torso_hw + 0.20 * scale, torso_hw + 0.32 * scale)
                wr = _min_in(torso_hw + 0.32 * scale, torso_hw + 0.45 * scale)
                if el:
                    J[f"elbow_{side}"] = [s * el[0], el[1], el[2]]
                if wr:
                    J[f"wrist_{side}"] = [s * wr[0], wr[1], wr[2]]
                J[f"shoulder_{side}"] = [s * (torso_hw + 0.018 * scale),
                                         sum(p[1] for p in arm_pts) / len(arm_pts), J["shoulder_z"]]
                hand = [p for p in V if s * p[0] > (J[f"wrist_{side}"][0] * s if f"wrist_{side}" in J else xmax)
                        and abs(p[2] - J["shoulder_z"]) < 0.08 * scale]
                if hand:
                    J[f"fingertip_{side}"] = [sum(p[0] for p in hand) / len(hand),
                                              sum(p[1] for p in hand) / len(hand),
                                              sum(p[2] for p in hand) / len(hand)]
    # ---- head
    head = [p for p in V if p[2] > J["neck_z"] + 0.015 * scale and abs(p[0]) < 0.10 * scale]
    if head:
        J["head_center"] = [sum(p[0] for p in head) / len(head),
                            sum(p[1] for p in head) / len(head),
                            sum(p[2] for p in head) / len(head)]
        J["head_top"] = [J["head_center"][0], J["head_center"][1], max(p[2] for p in head)]
        J["chin_z"] = J["neck_z"] + 0.03 * scale
        J["face_y"] = min(p[1] for p in head)
    return J

# ---------------------------------------------------------------- cage
LOCKED_BONES = {"hand_L", "hand_R", "foot_L", "foot_R", "head", "chest",
                "LeftHand", "RightHand", "LeftFoot", "RightFoot", "Head", "Chest"}

def fit_cage_to_bbox(cage_verts, cage_bbox, char_bbox):
    """weight_cage.py mesh-level fit: scale cage verts about the cage
    bbox centre, then translate to the character bbox centre."""
    (gmin, gmax), (cmin, cmax) = cage_bbox, char_bbox
    gcenter = [(gmin[i] + gmax[i]) / 2 for i in range(3)]
    ccenter = [(cmin[i] + cmax[i]) / 2 for i in range(3)]
    scale = [((cmax[i] - cmin[i]) / (gmax[i] - gmin[i]) if gmax[i] > gmin[i] else 1.0)
             for i in range(3)]
    out = []
    for v in cage_verts:
        w = [gcenter[i] + (v[i] - gcenter[i]) * scale[i] for i in range(3)]
        out.append([w[i] + (ccenter[i] - gcenter[i]) for i in range(3)])
    return out

def build_cage(bone_segments, ring=8):
    """Procedural MDEF-style cage: a ring of ``ring`` vertices around
    each bone segment at its head, midpoint and tail. Cape Jones used
    BlenRig's shipped cage mesh (1,057 verts); this procedural cage
    is the dependency-free equivalent for WH test rigs."""
    cage = []
    for _name, (a, b) in bone_segments.items():
        axis = vnorm(vsub(b, a))
        ref = [0, 0, 1] if abs(axis[2]) < 0.9 else [1, 0, 0]
        u = vnorm(vcross(axis, ref))
        w = vcross(axis, u)
        length = vlen(vsub(b, a))
        radius = max(0.03, length * 0.35)
        for t in (0.0, 0.5, 1.0):
            centre = vadd(a, vscale(vsub(b, a), t))
            for k in range(ring):
                ang = 2 * math.pi * k / ring
                off = vadd(vscale(u, math.cos(ang) * radius), vscale(w, math.sin(ang) * radius))
                cage.append(vadd(centre, off))
    return cage

def compute_weights(cage_verts, bone_segments, max_influences=4):
    """weight_cage.py zone weights, data-only: 1/d^2 falloff, top-4,
    normalised to sum 1. A vert whose nearest bone is locked gets
    that bone at 1.0 (rigid head/hands/feet, no stretch)."""
    names = list(bone_segments.keys())
    weights = {n: [0.0] * len(cage_verts) for n in names}
    for vi, p in enumerate(cage_verts):
        dlist = []
        for bn in names:
            a, b = bone_segments[bn]
            d, _ = dist_point_segment(p, a, b)
            dlist.append((d, bn))
        dlist.sort()
        top = dlist[:max_influences]
        if top[0][1] in LOCKED_BONES:
            weights[top[0][1]][vi] = 1.0
        else:
            ws = [1.0 / (d * d + 1e-6) for d, _ in top]
            s = sum(ws)
            for (d, bn), w in zip(top, ws):
                weights[bn][vi] = w / s
    return weights

def verify_weights(weights):
    """Per-vert weight sums; returns (max_error, n_verts, n_bad)."""
    if not weights:
        return 1.0, 0, 0
    n = len(next(iter(weights.values())))
    worst, bad = 0.0, 0
    for vi in range(n):
        s = sum(w[vi] for w in weights.values())
        err = abs(s - 1.0)
        worst = max(worst, err)
        if err > 1e-6:
            bad += 1
    return worst, n, bad

def blender_steps():
    return (
        "Blender steps (NOT run by this script — needs Blender + BlenRig):\n"
        "  1. Blender 5.2.3 LTS headless: blender -b --python <blender driver>\n"
        "     (driver imports cape_rig.fit_guides and writes guide targets\n"
        "     into a BlenRig biped, as in cape-jones blenrig_setup/fit/warp).\n"
        "  2. BlenRig 6 addon install + biped add, headless-safe viewport\n"
        "     patch from blenrig_setup.py; reproportion ON -> fit -> rest-bake\n"
        "     -> reproportion OFF, exactly as in blenrig_fit.py.\n"
        "  3. MDEF cage bind + weight_cage zone weights, then\n"
        "     verify_deform/verify_warp checks (deform bone head error).\n"
        "  4. EEVEE QA render (see show-retarget qa_render_svg for the\n"
        "     dependency-free stick-figure equivalent used in CI).\n"
        "MB-Lab note: WH pins Blender 4.0.2 for MB-Lab (tools/mb-lab/README.md).\n"
        "Use 4.0.2 for MB-Lab generation and 5.2.3 for this rig fit until\n"
        "MB-Lab on 5.2.3 is proven by a headless run — not claimed here.\n"
    )

def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit"); f.add_argument("--joints", required=True); f.add_argument("--out", required=True)
    f.add_argument("--rest-scale", type=float, default=1.0)
    c = sub.add_parser("cage"); c.add_argument("--skeleton", required=True); c.add_argument("--out", required=True)
    d = sub.add_parser("detect"); d.add_argument("--verts", required=True); d.add_argument("--out", required=True)
    sub.add_parser("blender-steps")
    args = ap.parse_args(argv)
    if args.cmd == "blender-steps":
        print(blender_steps()); return 0
    if args.cmd == "fit":
        joints = json.load(open(args.joints))
        guides = fit_guides(joints, rest_scale=args.rest_scale)
        json.dump(guides, open(args.out, "w"), indent=1)
        print(f"FIT guides={len(guides)} -> {args.out}")
    elif args.cmd == "detect":
        verts = json.load(open(args.verts))
        joints = detect_joints(verts)
        json.dump(joints, open(args.out, "w"), indent=1)
        print(f"DETECT joints={len(joints)} -> {args.out}")
    elif args.cmd == "cage":
        skel = json.load(open(args.skeleton))
        segs = {k: (v[0], v[1]) for k, v in skel.items()}
        cage = build_cage(segs)
        weights = compute_weights(cage, segs)
        worst, n, bad = verify_weights(weights)
        json.dump({"cage_verts": cage, "weights": weights,
                   "verify": {"max_sum_error": worst, "n_verts": n, "n_bad": bad}},
                  open(args.out, "w"))
        print(f"CAGE verts={n} max_sum_error={worst:.2e} bad={bad} -> {args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
