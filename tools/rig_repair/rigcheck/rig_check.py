#!/usr/bin/env python3
"""rig-check: validation gate for skinned character GLBs (AshLane, Brutal-Fist, Bannon).

usage: rig_check.py MODEL.glb [--clips DIR|name=path,...] [--sheet OUT.png] [--json OUT.json]
                    [--frames 6] [--metric-frames 16] [--retarget aligned|rest|absolute|world]
                    [--facing +Z|-Z|+X|-X] [--quiet]
                    (--retarget default is 'aligned'; the docstring's old claim that 'rest'
                    was the default was wrong and has been corrected here.)

Exit code 0 = PASS, 1 = FAIL, 2 = could not read the file.

Static checks : skin present, standard (Mixamo-compatible) skeleton names, rest pose (T/A pose,
                legs and spine straight), scale (1.3-2.3 m), facing (--facing, default +Z; AshLane
                cast files face +X because makeRig turns them -90 deg), weights normalized,
                <= 4 influences, no unweighted verts, no NaN, bind pose == rest pose.
Clip checks   : each clip of the standard set (idle, walk, jab, kick, hit_react, knockdown) is played
                by bone name (--retarget rest = AshLane's retargetUal rest-relative mapping, the
                default; --retarget absolute = raw AnimationMixer track binding; --retarget world =
                frame-independent world-delta retarget, isolates skinning quality), hips translation
                rescaled to this character's hip height, and measured for:
                NaN, edge stretch/collapse (weight bleed, candy-wrapper), ground contact
                (sinking / floating), knee and elbow hinge flips, effector error vs the clip's own
                skeleton, and whether it moved at all.
Every number is computed from the file; nothing is assumed. UNKNOWN is never PASS.
"""
import sys, os, re, json, math, subprocess, tempfile, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gltf_np import GLB, SkinnedModel, sample_track, qmat, mat_to_q  # noqa: E402

STANDARD = ["idle", "walk", "jab", "kick", "hit_react", "knockdown"]
GROUNDED = {"idle": True, "walk": True, "jab": True, "kick": False, "hit_react": True, "knockdown": False}
CORE = ["hips", "spine", "neck", "head",
        "leftarm", "leftforearm", "lefthand", "rightarm", "rightforearm", "righthand",
        "leftupleg", "leftleg", "leftfoot", "rightupleg", "rightleg", "rightfoot"]
OPTIONAL = ["spine1", "spine2", "leftshoulder", "rightshoulder", "lefttoebase", "righttoebase"]
EFF = ["lefthand", "righthand", "leftfoot", "rightfoot"]
TH = dict(stretch=2.5, compress=0.15, sink=-0.02, sink_air=-0.07, sink_median=-0.006, float_median=0.04, eff=20.0,
          flip_frac=0.2, disp=0.004, wsum=0.01, height=(1.3, 2.3), facing_deg=30.0,
          arm_min=-60.0, arm_max=25.0, leg_deg=20.0, spine_deg=20.0, bind_dev=0.01, floor=0.03)

def norm(n):
    n = re.sub(r"^mixamorig\d*[:_]?", "", n or "", flags=re.I)
    return n.replace(".", "").replace(" ", "").lower()

NEEDS_DECODE = {"EXT_meshopt_compression", "KHR_draco_mesh_compression", "KHR_mesh_quantization"}

def readable(path, tmp):
    """Decode path: meshopt/multi-buffer GLBs are decoded to plain GLBs with
    the pipeline's pure-Python ingest (no node_modules needed; PR #77's node
    decode path was dead on every box without @gltf-transform installed).
    Draco-compressed models raise a clear error -> route through Blender ingest."""
    g = GLB(path)
    used = set(g.j.get("extensionsUsed", []))
    if not (used & NEEDS_DECODE):
        return path
    sys.path.insert(0, os.path.join(HERE, ".."))
    from ingest import decode_to_plain, DracoError  # noqa: E402
    out = os.path.join(tmp, "decoded_" + os.path.basename(path))
    try:
        return decode_to_plain(path, out)
    except DracoError as e:
        raise RuntimeError(str(e))

AXES = {"+Z": (0, 0, 1.0), "-Z": (0, 0, -1.0), "+X": (1.0, 0, 0), "-X": (-1.0, 0, 0)}

def qmul(a, b):
    """Hamilton product for glTF (x, y, z, w) quaternions."""
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by,
                     aw * by - ax * bz + ay * bw + az * bx,
                     aw * bz + ax * by - ay * bx + az * bw,
                     aw * bw - ax * bx - ay * by - az * bz])

def qinv(q):
    return np.array([-q[0], -q[1], -q[2], q[3]]) / max(float(q @ q), 1e-12)

def ang(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12: return float("nan")
    return math.degrees(math.acos(float(np.clip(a @ b / (na * nb), -1, 1))))

class Character:
    def __init__(self, path, tmp):
        self.path = path
        self.m = SkinnedModel(readable(path, tmp))
        g = self.g = self.m.g
        self.joint_set = set()
        for s in self.m.skins: self.joint_set.update(s["joints"])
        # normalized-name -> node index (prefer skin joints)
        self.ix = {}
        for i, n in enumerate(g.name):
            k = norm(n)
            if k not in self.ix or (i in self.joint_set and self.ix[k] not in self.joint_set): self.ix[k] = i
        self.skinned_prims = [d for d in self.m.prims if "J" in d]
        self.L0 = self.m.local_at()
        self.V0, self.W0 = self.m.skin_verts(self.L0)
        P = np.concatenate([p for p in self.V0]) if self.V0 else np.zeros((0, 3))
        self.P0 = P
        self.ymin0 = float(P[:, 1].min()) if len(P) else 0.0
        self.H = float(P[:, 1].max() - P[:, 1].min()) if len(P) else 0.0
        self.edges = []
        for k, d in enumerate(self.m.prims if self.skinned_prims else []):
            idx = d["idx"]
            e = np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]]); e.sort(1); e = np.unique(e, axis=0)
            L0 = np.linalg.norm(self.V0[k][e[:, 0]] - self.V0[k][e[:, 1]], axis=1)
            self.edges.append((e, L0))
        self.fwd = self.facing(self.W0)
        y = math.atan2(self.fwd[0], self.fwd[2]); c, s = math.cos(-y), math.sin(-y)
        self.R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])  # rotate so the character faces +Z
    def jpos(self, W, k):
        i = self.ix.get(k)
        return None if i is None else W[i][:3, 3]
    def cmap(self, k):
        """Name of the clip bone that drives this character's bone k (mirrored if L/R are swapped)."""
        if not getattr(self, "mirror", False): return k
        return "right" + k[4:] if k.startswith("left") else ("left" + k[5:] if k.startswith("right") else k)
    def facing(self, W):
        """Forward = where the toes point (foot -> toe base), falling back to the hip/shoulder line.
        Also sets self.mirror when the bone named Left* sits on the character's right side."""
        self.mirror = False
        toes = []
        for sd in ("left", "right"):
            a, b = self.jpos(W, sd + "foot"), self.jpos(W, sd + "toebase")
            if a is not None and b is not None:
                d = b - a; d[1] = 0
                if np.linalg.norm(d) > 1e-9: toes.append(d / np.linalg.norm(d))
        l, r = self.jpos(W, "leftupleg"), self.jpos(W, "rightupleg")
        if l is None or r is None: l, r = self.jpos(W, "leftarm"), self.jpos(W, "rightarm")
        if toes:
            f = np.mean(toes, 0)
            if np.linalg.norm(f) > 1e-6:
                f = f / np.linalg.norm(f)
                if l is not None and r is not None:
                    left = l - r; left[1] = 0
                    self.mirror = bool(left @ np.cross([0, 1.0, 0], f) < -1e-6)
                return f
        l, r = self.jpos(W, "leftupleg"), self.jpos(W, "rightupleg")
        if l is None or r is None:
            l, r = self.jpos(W, "leftarm"), self.jpos(W, "rightarm")
        if l is None or r is None: return np.array([0, 0, 1.0])
        left = l - r; left[1] = 0
        if np.linalg.norm(left) < 1e-9: return np.array([0, 0, 1.0])
        f = np.cross(left / np.linalg.norm(left), [0, 1, 0]); return f / np.linalg.norm(f)

class Clip:
    def __init__(self, name, path, tmp):
        self.name, self.path = name, path
        self.c = Character(path, tmp) if True else None
        g = self.c.g
        an = g.anim_names()
        if not an: raise ValueError(f"clip {path} has no animation")
        self.anim = g.anim(0)
        self.dur = max(self.anim["duration"], 1e-3)
        Wr = self.c.W0
        feet = [self.c.jpos(Wr, k) for k in ("leftfoot", "rightfoot", "lefttoebase", "righttoebase")]
        feet = [f for f in feet if f is not None]
        h = self.c.jpos(Wr, "hips")
        self.floor = min(f[1] for f in feet) if feet else 0.0
        self.hips_h = (h[1] - self.floor) if h is not None else 1.0
        self.hips0 = h
        self.R = self.c.R
    def world(self, t):
        return self.c.g.world(self.c.m.local_at(self.anim, t))

def apply_clip(ch, clip, t):
    """Rotations by bone name, in one of the modes (ch.retarget; default 'aligned'):
      rest     - rest-relative, q = qRestTarget * inverse(qRestClip) * qClip. This is what AshLane's
                 retargetUal() does, and it equals 'absolute' when both skeletons share rest frames.
      absolute - three.js AnimationMixer on a same-named track: local rotation = qClip.
    Hips are translated by the clip's world-space hip motion rescaled to this character's hip height."""
    g = ch.g
    local = [[x.copy() for x in r] for r in g.rest]
    floor_dy = 0.0
    if ch.retarget in ("world", "aligned"):
        if ch.retarget == "aligned":
            # straightening an A-pose / wide stance onto the clip's rest changes leg reach; measure
            # that once per clip so the hips are lifted/lowered by the same amount (no fake sink)
            cache = ch.__dict__.setdefault("_floor_dy", {})
            if id(clip) not in cache:
                l2 = [[x.copy() for x in r] for r in g.rest]
                world_retarget(ch, clip, 0.0, l2, aligned=True, rest_only=True)
                V2, _ = ch.m.skin_verts(l2)
                cache[id(clip)] = ch.ymin0 - float(np.concatenate(V2)[:, 1].min()) if V2 else 0.0
            floor_dy = cache[id(clip)]
        world_retarget(ch, clip, t, local, aligned=ch.retarget == "aligned")
    for tr in ([] if ch.retarget in ("world", "aligned") else clip.anim["tracks"]):
        if tr["path"] != "rotation": continue
        i = ch.ix.get(norm(tr["node"]))
        if i is None: continue
        v = np.array(sample_track(tr, t), float); v = v / np.linalg.norm(v)
        if ch.retarget == "rest":
            ci = clip.c.ix.get(norm(tr["node"]))  # same-name source bone (in-game binding is by name)
            if ci is not None:
                v = qmul(g.rest[i][1], qmul(qinv(clip.c.g.rest[ci][1]), v)); v = v / np.linalg.norm(v)
        local[i][1] = v
    hi = ch.ix.get("hips")
    if hi is not None and clip.hips0 is not None:
        Wc = clip.world(t)
        d = clip.R @ (clip.c.jpos(Wc, "hips") - clip.hips0)
        hips_h = ch.W0[hi][1, 3] - ch.ymin0 + floor_dy
        d = ch.R.T @ (d * (hips_h / max(clip.hips_h, 1e-6)))
        target = ch.W0[hi][:3, 3] + d + np.array([0, floor_dy, 0])
        p = g.parent[hi]
        Wtmp = g.world(local)
        PW = Wtmp[p] if p >= 0 else np.eye(4)
        local[hi][0] = (np.linalg.inv(PW) @ np.append(target, 1))[:3]
    else:
        Wc = None
    V, W = ch.m.skin_verts(local)
    return V, W, (Wc if Wc is not None else clip.world(t))

def _rot(M):
    R = np.asarray(M, float)[:3, :3]
    return R / np.maximum(np.linalg.norm(R, axis=0, keepdims=True), 1e-12)

def _arc(a, b):
    """Minimal rotation matrix taking direction a to direction b."""
    a = a / max(np.linalg.norm(a), 1e-12); b = b / max(np.linalg.norm(b), 1e-12)
    v = np.cross(a, b); c = float(a @ b)
    if c < -0.999999:
        ax = np.cross(a, [1.0, 0, 0]);
        if np.linalg.norm(ax) < 1e-6: ax = np.cross(a, [0, 1.0, 0])
        ax /= np.linalg.norm(ax); return 2 * np.outer(ax, ax) - np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)

CHILD_PREF = ("spine", "neck", "head", "arm", "forearm", "hand", "leg", "foot", "toebase", "middle1")

CHAIN_ROOTS = ("leftarm", "rightarm", "leftupleg", "rightupleg")

def _align(ch, clip, match, A):
    """T-pose calibration, like a Humanoid avatar setup: the upper arms and thighs get the swing that
    takes this character's rest bone direction onto the clip skeleton's rest direction (an A-pose
    model plays T-pose clips correctly). Every bone below a chain root inherits that same rotation,
    so elbows, wrists, knees and fingers keep their own bind relationship (no fake twist)."""
    g = ch.g; own = {}
    kids = {}
    for i in range(len(g.nodes)):
        if g.parent[i] >= 0 and i in match: kids.setdefault(g.parent[i], []).append(i)
    for i, ci in match.items():
        nm = norm(g.name[i])
        if nm not in CHAIN_ROOTS: continue
        want = {"leftarm": "leftforearm", "rightarm": "rightforearm", "leftupleg": "leftleg", "rightupleg": "rightleg"}[nm]
        ks = [k for k in kids.get(i, []) if norm(g.name[k]) == want]
        if not ks: continue
        k = ks[0]; ck = match[k]
        dT = ch.W0[k][:3, 3] - ch.W0[i][:3, 3]
        dC = A @ (clip.c.W0[ck][:3, 3] - clip.c.W0[ci][:3, 3])
        if np.linalg.norm(dT) < 1e-9 or np.linalg.norm(dC) < 1e-9: continue
        own[i] = _arc(dT, dC)
    out = {}
    for i in range(len(g.nodes)):
        p = i
        while p >= 0 and p not in own: p = g.parent[p]
        if p >= 0: out[i] = own[p]
    return out

def world_retarget(ch, clip, t, local, aligned=False, rest_only=False):
    """Frame-independent retarget (like SkeletonUtils.retarget): each matched bone gets the clip
    bone's WORLD rotation change from its rest pose, applied on top of this character's own rest
    world rotation. Tests skinning/weights independently of how each bone's local axes are rolled."""
    g = ch.g
    Wc = None if rest_only else clip.world(t); Wc0 = clip.c.W0
    A = ch.R.T @ clip.R  # clip facing -> character facing
    if not hasattr(ch, "_order"):
        depth = []
        for i in range(len(g.nodes)):
            d, p = 0, g.parent[i]
            while p >= 0: d += 1; p = g.parent[p]
            depth.append(d)
        ch._order = sorted(range(len(g.nodes)), key=lambda i: depth[i])
    match = {}
    for i in range(len(g.nodes)):
        k = norm(g.name[i])
        if ch.ix.get(k) == i and ch.cmap(k) in clip.c.ix: match[i] = clip.c.ix[ch.cmap(k)]
    if aligned:
        key = id(clip)
        if getattr(ch, "_align_key", None) != key:
            ch._align_key, ch._align = key, _align(ch, clip, match, A)
        S = ch._align
    else:
        S = {}
    Wr = {}
    for i in ch._order:
        p = g.parent[i]
        Pr = Wr[p] if p >= 0 else np.eye(3)
        ci = match.get(i)
        if ci is not None:
            D = np.eye(3) if rest_only else _rot(Wc[ci]) @ _rot(Wc0[ci]).T
            Rw = A @ D @ A.T @ S.get(i, np.eye(3)) @ _rot(ch.W0[i])
            local[i][1] = mat_to_q(Pr.T @ Rw)
            Wr[i] = Rw
        else:
            Wr[i] = Pr @ qmat(local[i][1])

def hinge(W, j, a, b, c, R):
    pa, pb, pc = j(W, a), j(W, b), j(W, c)
    if pa is None or pb is None or pc is None: return None, 0.0
    u, l = R @ (pb - pa), R @ (pc - pb)
    bend = ang(u, l)
    n = np.cross(u, l); nn = np.linalg.norm(n)
    return (n / nn if nn > 1e-9 else None), bend

def static_checks(ch):
    fails, warns, info = [], [], {}
    g = ch.g
    info["nodes"] = len(g.nodes); info["skins"] = len(ch.m.skins)
    nv = sum(len(d["pos"]) for d in ch.m.prims); ntri = sum(len(d["idx"]) for d in ch.m.prims)
    info["verts"], info["tris"] = int(nv), int(ntri)
    info["height_m"] = round(ch.H, 3)
    if nv == 0: fails.append("no mesh geometry"); return fails, warns, info
    sk_v = sum(len(d["pos"]) for d in ch.skinned_prims)
    info["skinned_vert_frac"] = round(sk_v / nv, 3)
    if not ch.skinned_prims: fails.append("no skin: 0 skinned primitives (JOINTS_0/WEIGHTS_0 + node.skin missing) - mesh cannot deform")
    elif sk_v / nv < 0.95: fails.append(f"only {sk_v/nv:.0%} of vertices are skinned; the rest stay frozen")
    names = {norm(n) for n in g.name}
    missing = [k for k in CORE if k not in ch.ix or (ch.joint_set and ch.ix[k] not in ch.joint_set)]
    info["skeleton"] = "mixamo-prefixed" if any(n.lower().startswith("mixamorig") for n in g.name) else ("mixamo-plain" if "hips" in names and "leftupleg" in names else "other")
    info["joints"] = len(ch.joint_set)
    if missing: fails.append(f"non-standard skeleton: missing {len(missing)} core Mixamo bones ({', '.join(missing[:8])}{'...' if len(missing) > 8 else ''})")
    opt_missing = [k for k in OPTIONAL if k not in ch.ix]
    if opt_missing and not missing: warns.append(f"optional bones missing: {', '.join(opt_missing)}")
    # NaN
    bad = sum(int(np.isnan(d["pos"]).sum()) for d in ch.m.prims)
    bad += sum(int(np.isnan(d["W"]).sum()) for d in ch.skinned_prims)
    bad += sum(int(np.isnan(m).sum()) for m in ch.m.ibm)
    bad += sum(int(np.isnan(np.concatenate(r)).sum()) for r in g.rest)
    info["nan"] = bad
    if bad: fails.append(f"NaN values x{bad} in positions/weights/inverse-bind/rest")
    # weights
    if ch.skinned_prims:
        dev = max(float(np.abs(d["W"].sum(1) - 1).max()) for d in ch.skinned_prims)
        zero = sum(int((d["W"].sum(1) <= 1e-6).sum()) for d in ch.skinned_prims)
        over4 = sum(int(((d["W"] > 1e-4).sum(1) > 4).sum()) for d in ch.skinned_prims)
        info["weight_sum_maxdev"] = round(dev, 4); info["unweighted_verts"] = zero; info["verts_over_4_influences"] = over4
        if zero: fails.append(f"{zero} vertices have zero total weight (collapse to origin)")
        if dev > TH["wsum"]: fails.append(f"weights not normalized (max |sum-1| = {dev:.3f})")
        if over4: fails.append(f"{over4} vertices use more than 4 influences (three.js/WebGL drops the extras)")
        # bind pose == rest pose (IBMs consistent with the node rest transforms)
        devs = []
        for k, d in enumerate(ch.m.prims):
            if "J" not in d: continue
            M = ch.W0[d["node"]]
            raw = d["pos"] @ M[:3, :3].T + M[:3, 3]
            devs.append(np.linalg.norm(ch.V0[k] - raw, axis=1))
            # glTF: skinned mesh node transform is ignored -> compare against raw positions too
            devs[-1] = np.minimum(devs[-1], np.linalg.norm(ch.V0[k] - d["pos"], axis=1))
        bd = float(np.median(np.concatenate(devs))) / max(ch.H, 1e-6) if devs else 0
        info["bind_vs_rest_dev_over_H"] = round(bd, 4)
        if bd > TH["bind_dev"]: fails.append(f"rest pose does not match bind pose (median vertex offset {bd:.1%} of height) - inverse bind matrices are stale")
    # scale / facing / floor
    lo, hi = TH["height"]
    if not (lo <= ch.H <= hi): fails.append(f"scale: rest height {ch.H:.2f} m outside {lo}-{hi} m (Mixamo clips expect ~1.8 m)")
    fdeg = ang(ch.fwd, np.array(AXES[ch.facing_axis]))
    info["facing_expected"] = ch.facing_axis
    info["facing_detected"] = min(AXES, key=lambda k: ang(ch.fwd, np.array(AXES[k])))
    info["facing_deg_off"] = round(fdeg, 1)
    info["left_right_swapped"] = bool(getattr(ch, "mirror", False))
    if info["left_right_swapped"]: warns.append("skeleton: Left*/Right* bones are swapped (LeftUpLeg/LeftArm sit on the character's right side); clips play mirrored (southpaw), checked mirrored")
    if fdeg > TH["facing_deg"]: fails.append(f"facing: character faces {info['facing_detected']} ({fdeg:.0f} deg away from the expected {ch.facing_axis})")
    info["rest_minY_over_H"] = round(ch.ymin0 / max(ch.H, 1e-6), 4)
    if abs(ch.ymin0) > TH["floor"] * ch.H: warns.append(f"rest feet are {ch.ymin0/ch.H:+.1%} of height off the y=0 floor")
    # rest pose shape
    W, j = ch.W0, ch.jpos
    for side in ("left", "right"):
        a, f = j(W, side + "arm"), j(W, side + "forearm")
        if a is not None and f is not None:
            d = f - a; el = math.degrees(math.asin(np.clip(d[1] / max(np.linalg.norm(d), 1e-9), -1, 1)))
            info[f"rest_{side}_arm_elev_deg"] = round(el, 1)
            if not (TH["arm_min"] <= el <= TH["arm_max"]): fails.append(f"rest pose: {side} upper arm at {el:.0f} deg (needs T/A pose, {TH['arm_min']:.0f}..{TH['arm_max']:.0f})")
        u, ft = j(W, side + "upleg"), j(W, side + "foot")
        if u is not None and ft is not None:
            la = ang(ft - u, np.array([0, -1.0, 0])); info[f"rest_{side}_leg_deg"] = round(la, 1)
            if la > TH["leg_deg"]: fails.append(f"rest pose: {side} leg {la:.0f} deg off vertical")
    h, hd = j(W, "hips"), j(W, "head")
    if h is not None and hd is not None:
        sa = ang(hd - h, np.array([0, 1.0, 0])); info["rest_spine_deg"] = round(sa, 1)
        if sa > TH["spine_deg"]: fails.append(f"rest pose: spine {sa:.0f} deg off vertical")
    return fails, warns, info

def clip_checks(ch, clip, nframes):
    m = dict(clip=clip.name, file=os.path.basename(os.path.realpath(clip.path)), duration=round(clip.dur, 2))
    ts = np.linspace(0, clip.dur, nframes)
    nan = 0; st = []; co = []; ymin = []; disp = []; eff = []; flips = {"knee": [0, 0], "elbow": [0, 0]}
    J = ch.jpos
    def Jc(W, k): return clip.c.jpos(W, ch.cmap(k))
    for t in ts:
        V, W, Wc = apply_clip(ch, clip, float(t))
        for k, d in enumerate(V):
            nan += int(np.isnan(d).sum())
            e, L0 = ch.edges[k]
            if len(e) == 0: continue
            ok = L0 > 1e-6 * ch.H
            if not ok.any(): continue
            r = np.linalg.norm(d[e[:, 0]] - d[e[:, 1]], axis=1)[ok] / L0[ok]
            st.append(float(np.percentile(r, 99.9))); co.append(float(np.percentile(r, 0.1)))
        P = np.concatenate(V)
        # relative to the clip's own character mesh (some clips crouch or let the body dip below the
        # floor as authored): what is left is this character's contribution. Clips without a mesh
        # are measured against the rest floor.
        ref = 0.0
        if clip.c.skinned_prims and clip.c.H > 0:
            Vc, _ = clip.c.m.skin_verts(clip.c.m.local_at(clip.anim, float(t)))
            ref = float((np.concatenate(Vc)[:, 1].min() - clip.c.ymin0) / clip.c.H)
        ymin.append(float((P[:, 1].min() - ch.ymin0) / ch.H - ref))
        disp.append(float(np.linalg.norm(P - ch.P0, axis=1).mean() / ch.H))
        h, hc = J(W, "hips"), Jc(Wc, "hips")
        if h is not None and hc is not None:
            for k in EFF:
                a, b = J(W, k), Jc(Wc, k)
                if a is None or b is None: continue
                eff.append(ang(ch.R @ (a - h), clip.R @ (b - hc)))
        for kind, chain in (("knee", ("upleg", "leg", "foot")), ("elbow", ("arm", "forearm", "hand"))):
            for side in ("left", "right"):
                n1, b1 = hinge(W, J, *(side + c for c in chain), ch.R)
                n2, b2 = hinge(Wc, Jc, *(side + c for c in chain), clip.R)
                if n1 is None or n2 is None or b1 < 25 or b2 < 25: continue
                flips[kind][1] += 1
                if n1 @ n2 < 0: flips[kind][0] += 1
    m["nan"] = nan
    m["stretch_p999_max"] = round(max(st), 3) if st else None
    m["compress_p001_min"] = round(min(co), 3) if co else None
    m["minY_over_H"] = dict(min=round(min(ymin), 4), median=round(float(np.median(ymin)), 4))
    m["mean_disp_over_H"] = round(float(np.mean(disp)), 4)
    m["effector_err_deg"] = round(float(np.nanmean(eff)), 1) if eff else None
    m["knee_flips"] = f"{flips['knee'][0]}/{flips['knee'][1]}"; m["elbow_flips"] = f"{flips['elbow'][0]}/{flips['elbow'][1]}"
    R = []
    if nan: R.append(f"NaN x{nan}")
    if m["stretch_p999_max"] is None: R.append("stretch UNKNOWN (no edges)")
    elif m["stretch_p999_max"] > TH["stretch"]: R.append(f"stretch: p99.9 edge ratio {m['stretch_p999_max']} > {TH['stretch']} (weight bleed / exploding verts)")
    if m["compress_p001_min"] is not None and m["compress_p001_min"] < TH["compress"]: R.append(f"collapse: p0.1 edge ratio {m['compress_p001_min']} < {TH['compress']} (candy-wrapper)")
    sink = TH["sink"] if GROUNDED.get(clip.name, True) else TH["sink_air"]
    if m["minY_over_H"]["min"] < sink: R.append(f"ground: sinks {m['minY_over_H']['min']:+.1%} of height below the floor")
    if GROUNDED.get(clip.name, True):
        if m["minY_over_H"]["median"] < TH["sink_median"]: R.append(f"ground: feet sit {m['minY_over_H']['median']:+.1%} below the floor on a typical frame")
        if m["minY_over_H"]["median"] > TH["float_median"]: R.append(f"ground: floats {m['minY_over_H']['median']:+.1%} above the floor")
    if m["mean_disp_over_H"] < TH["disp"]: R.append("clip did not move the mesh (no bones matched)")
    if m["effector_err_deg"] is None: R.append("effector error UNKNOWN (hands/feet/hips not found)")
    elif m["effector_err_deg"] > TH["eff"]: R.append(f"motion mismatch: effector error {m['effector_err_deg']} deg > {TH['eff']}")
    for kind in ("knee", "elbow"):
        b, n = flips[kind]
        if n and b / n > TH["flip_frac"]: R.append(f"{kind} flips: hinge bends the wrong way in {b}/{n} samples")
    m["verdict"] = "PASS" if not R else "FAIL"; m["reasons"] = R
    return m

# ------------------------------------------------------------------ contact sheet (numpy splat renderer)
def splat(V_list, prims, R, H, cw, ch_, center_x=None, floor=0.0):
    P = np.concatenate(V_list) @ R.T
    P = P - np.array([0, floor, 0])
    if not len(P): return np.full((ch_, cw, 3), 235, np.uint8)
    faces = []; off = 0
    for k, d in enumerate(prims):
        faces.append(d["idx"] + off); off += len(V_list[k])
    F = np.concatenate(faces) if faces else np.zeros((0, 3), int)
    img = np.full((ch_, cw, 3), 235, np.uint8)
    pad = 0.08 * H; scale = (ch_ - 8) / (H * 1.25 + 2 * pad)
    cx = center_x if center_x is not None else float(np.median(P[:, 0]))
    def proj(Q):
        x = ((Q[:, 0] - cx) * scale + cw / 2).astype(int)
        y = (ch_ - 4 - (Q[:, 1] + pad) * scale).astype(int)
        return x, y
    # floor line
    fy = ch_ - 4 - int(pad * scale)
    if 0 <= fy < ch_: img[fy, :, :] = (150, 150, 150)
    if len(F):
        A, B, C = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
        N = np.cross(B - A, C - A); nl = np.linalg.norm(N, axis=1, keepdims=True); N = N / np.maximum(nl, 1e-12)
        L = np.array([0.3, 0.5, 0.8]); L /= np.linalg.norm(L)
        shade = np.clip(np.abs(N @ L), 0, 1) * 0.75 + 0.2
        pts = []; sh = []
        for wts in ((1/3, 1/3, 1/3), (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6)):
            pts.append(A * wts[0] + B * wts[1] + C * wts[2]); sh.append(shade)
        Q = np.concatenate(pts); S = np.concatenate(sh)
    else:
        Q = P; S = np.full(len(P), 0.6)
    x, y = proj(Q)
    ok = (x >= 0) & (x < cw) & (y >= 0) & (y < ch_)
    x, y, z, S = x[ok], y[ok], Q[ok, 2], S[ok]
    order = np.argsort(z)  # far first, near last -> near wins
    col = (np.outer(S[order], [205, 120, 80])).clip(0, 255).astype(np.uint8)
    img[y[order], x[order]] = col
    # dilate 1px to close holes on sparse meshes
    mask = np.zeros((ch_, cw), bool); mask[y, x] = True
    holes = ~mask
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        sh_ = np.roll(np.roll(img, dy, 0), dx, 1); sm = np.roll(np.roll(mask, dy, 0), dx, 1)
        fill = holes & sm
        img[fill] = sh_[fill]; mask |= fill; holes = ~mask
    return img

def contact_sheet(ch, clips, results, out, nframes, label):
    from PIL import Image, ImageDraw
    cw, chh = 150, 210
    rows = [("rest", None)] + [(c.name, c) for c in clips]
    W_ = 150 + cw * nframes; Hh = 30 + chh * len(rows)
    sheet = Image.new("RGB", (W_, Hh), "white"); d = ImageDraw.Draw(sheet)
    d.text((4, 4), f"{label}  H={ch.H:.2f}m  verdict={results['verdict']}", fill=(0, 120, 0) if results["verdict"] == "PASS" else (200, 0, 0))
    for ri, (name, clip) in enumerate(rows):
        y0 = 30 + ri * chh
        if clip is None:
            frames = [ch.V0]; tl = ["rest"]
            v = "FAIL" if results["static"]["fails"] else "PASS"
            why = results["static"]["fails"][:3]
        else:
            ts = np.linspace(0, clip.dur, nframes); frames = []; tl = []
            for t in ts:
                V, W, _ = apply_clip(ch, clip, float(t)); frames.append(V); tl.append(f"t={t:.2f}")
            r = next((x for x in results["clips"] if x["clip"] == name), None)
            v = r["verdict"] if r else "UNKNOWN"; why = r["reasons"][:3] if r else []
        cx = float(np.median(np.concatenate(ch.V0) @ ch.R.T, axis=0)[0])
        for fi, V in enumerate(frames):
            im = Image.fromarray(splat(V, ch.m.prims, ch.R, ch.H, cw, chh, cx, ch.ymin0))
            sheet.paste(im, (150 + fi * cw, y0)); d.text((150 + fi * cw + 3, y0 + 2), tl[fi], fill=(60, 60, 60))
        d.text((4, y0 + 6), name, fill="black")
        d.text((4, y0 + 22), v, fill=(0, 140, 0) if v == "PASS" else (200, 0, 0))
        for k, w in enumerate(why):
            txt = w if len(w) < 24 else w[:23] + "…"
            d.text((4, y0 + 40 + 14 * k), txt, fill=(120, 0, 0))
    sheet.save(out)

def parse_clips(arg):
    if not arg: arg = os.environ.get("RIG_CHECK_CLIPS") or os.path.join(HERE, "..", "clips", "standard")
    out = []
    if os.path.isdir(arg):
        for n in STANDARD:
            p = os.path.join(arg, n + ".glb")
            out.append((n, p if os.path.exists(p) else None))
    else:
        for part in arg.split(","):
            n, _, p = part.partition("=")
            out.append((n.strip(), p.strip()))
    return out

def check(path, clips_arg=None, sheet=None, nframes=6, mframes=16, label=None, retarget="aligned", facing="+Z"):
    tmp = tempfile.mkdtemp(prefix="rigcheck_")
    res = dict(file=path, verdict="FAIL", static={}, clips=[])
    try:
        try:
            ch = Character(path, tmp)
            ch.retarget, ch.facing_axis = retarget, facing
        except Exception as e:  # unreadable = FAIL, never PASS
            res["static"] = dict(fails=[f"could not read GLB: {e}"], warns=[], info={}); res["error"] = True
            return res
        fails, warns, info = static_checks(ch)
        res["static"] = dict(fails=fails, warns=warns, info=info)
        res["options"] = dict(retarget=retarget, facing=facing)
        loaded = []
        can_play = bool(ch.skinned_prims) and "hips" in ch.ix and ch.H > 0
        for name, p in parse_clips(clips_arg):
            if p is None or not os.path.exists(p):
                res["clips"].append(dict(clip=name, verdict="FAIL", reasons=[f"clip file missing ({p}) - result UNKNOWN"])); continue
            if not can_play:
                res["clips"].append(dict(clip=name, verdict="FAIL", reasons=["not playable: no skin or no hips bone"])); continue
            try:
                c = Clip(name, p, tmp); loaded.append(c)
                res["clips"].append(clip_checks(ch, c, mframes))
            except Exception as e:
                res["clips"].append(dict(clip=name, verdict="FAIL", reasons=[f"clip check crashed: {e}"]))
        res["verdict"] = "PASS" if not fails and all(c["verdict"] == "PASS" for c in res["clips"]) else "FAIL"
        if sheet:
            try:
                contact_sheet(ch, loaded if can_play else [], res, sheet, nframes, label or os.path.basename(path))
                res["sheet"] = sheet
            except Exception as e:
                res["sheet_error"] = str(e)
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 0
    def opt(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
    path = argv[0]
    res = check(path, opt("--clips"), opt("--sheet"), int(opt("--frames", "6")), int(opt("--metric-frames", "16")),
                retarget=opt("--retarget", "aligned"), facing=opt("--facing", "+Z"))
    if opt("--json"):
        json.dump(res, open(opt("--json"), "w"), indent=1)
    if "--quiet" not in argv:
        print(f"{res['verdict']}  {path}")
        for f in res["static"].get("fails", []): print(f"  FAIL static: {f}")
        for w in res["static"].get("warns", []): print(f"  warn static: {w}")
        for c in res["clips"]:
            extra = "" if c["verdict"] == "PASS" else ": " + "; ".join(c["reasons"])
            stats = f" (stretch {c.get('stretch_p999_max')}, eff {c.get('effector_err_deg')} deg, minY {c.get('minY_over_H', {}).get('median')})" if "stretch_p999_max" in c else ""
            print(f"  {c['verdict']} {c['clip']}{stats}{extra}")
        if res.get("sheet"): print(f"  sheet: {res['sheet']}")
    return 2 if res.get("error") else (0 if res["verdict"] == "PASS" else 1)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
