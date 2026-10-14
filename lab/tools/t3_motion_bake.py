#!/usr/bin/env python3
"""Bake REAL decoded Tekken 3 motion (owner's own disc teardown) onto WH-Canonical-22 GLBs.

No hand keys, no IK, no procedural curves. Pipeline per frame:
  divmot bank -> teardown/tekken3/tools/local/pose_assemble.py (bit-exact AnimDecodePose +
  PoseBuildMatrices port, USA tables) -> posed part verts -> per-part rigid Kabsch fit
  against the T3 stance (the bind pose of t3_king.glb) -> part world rotation delta ->
  glTF space (same conv/facing/floor transform as t3_to_gltf.py) -> per-bone global rotation.
Retarget onto any WH-Canonical-22 rig (identity rest, e.g. pantera_leoman.glb):
  G_target(b) = G_t3(src(b)) . S_b, S_b = swing from target rest bone dir to T3 stance bone dir.
Bones T3 lacks (Spine, Neck, ToeBase) inherit (Spine = halfway Hips->Chest, Neck = Chest, Toe = Foot).

Usage:
  t3_motion_bake.py <in.glb> <out.glb> [--bank king] [--clips t3_stance=0,t3_win_lp=0xD67,...] [--json-dir DIR]
Needs n0madic/Tekken3Remake tools/research on T3REMAKE_RESEARCH (motion.py) -- see docs/anim/T3_MOTION_BAKE.md.
"""
import argparse, json, math, os, struct, sys, hashlib
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; REPO = HERE.parents[1]
T3 = REPO / "teardown/tekken3"
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(T3 / "tools/local"))
sys.path.insert(0, os.environ.get("T3REMAKE_RESEARCH", "/workspace/t3anim/t3r/tools/research"))
from t3_common import kmd_parse, PART_ROW, NPARTS, load_obj_parts, kabsch
from clips import rot_between, quat
import usa_tables
usa_tables.EXE_PATH = T3 / "disc/files/TEKKEN3/SLUS_004.02"
import pose_assemble as PA, motion

UNIT = 1 / 1000.0
C = np.diag([1.0, -1.0, -1.0])
DEFAULT_CLIPS = {"t3_stance": 0, "t3_stance_b": 1, "t3_stance_c": 2,
                 "t3_win_lp": 0xD67, "t3_win_rp": 0xD68, "t3_win_lk": 0xD69, "t3_win_rk": 0xD6A}
BANKS = {"king": ("models/king95/king95.kmd", "animations/divmot03_king.bin", "renders/pose-check/king_stance75.obj")}

def parse_obj_text(txt):
    parts, cur = {}, None
    for l in txt.splitlines():
        if l.startswith("o "): cur = int(l.split()[1].split("_")[1]); parts[cur] = []
        elif l.startswith("v ") and cur is not None: parts[cur].append([float(x) for x in l.split()[1:4]])
    return {k: np.array(v) for k, v in parts.items() if len(v)}

class T3Space:
    """Reproduces t3_to_gltf.import_fighter's stance->glTF transform exactly."""
    def __init__(self, kmd_path, stance_path):
        k = kmd_parse.parse_kmd(Path(kmd_path).read_bytes())
        self.st = {p: v for p, v in load_obj_parts(stance_path).items() if len(v)}; self.A = {}; piv = {}
        for p in range(NPARTS):
            row = k["rows"][PART_ROW[p]]
            if not row["verts"]: continue
            A = np.array(row["verts"], float); R, t, e = kabsch(A, self.st[p]); piv[p] = t
        piv[0] = piv[2].copy(); self.piv_t3 = piv
        conv = lambda p: (np.asarray(p, float) @ C.T) * UNIT
        P = {p: conv(v) for p, v in piv.items()}; V = {p: conv(v) for p, v in self.st.items()}
        lat = P[9] - P[13]; lat[1] = 0; lat /= np.linalg.norm(lat)
        fwd = np.cross(lat, [0, 1, 0]); fwd /= np.linalg.norm(fwd)
        if np.dot(V[17].mean(0) - P[17], fwd) < 0: fwd = -fwd
        ang = math.atan2(fwd[0], fwd[2]); c, s = math.cos(-ang), math.sin(-ang)
        self.Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        off = np.array([P[0][0], 0, P[0][2]])
        V2 = {p: (v - off) @ self.Ry.T for p, v in V.items()}
        floor = min(v[:, 1].min() for v in V2.values())
        self.off, self.floor = off, floor
        self.M = self.Ry @ C
        self.pos = lambda x: ((np.asarray(x, float) @ C.T) * UNIT - off) @ self.Ry.T - [0, floor, 0]
        Pg = {p: self.pos(v) for p, v in piv.items()}; self.P = Pg
        self.Vst = {p: self.pos(v) for p, v in self.st.items()}
        A_, B_ = ("Left", "Right") if Pg[9][0] > 0 else ("Right", "Left")
        C_, D_ = ("Left", "Right") if Pg[3][0] > 0 else ("Right", "Left")
        rmap = json.load(open(REPO / "lab/skeleton/retarget_maps.json"))["tekken3_rigid27"]["map"]
        self.name = {int(kk[4:]): vv.format(A=A_, B=B_, C=C_, D=D_) for kk, vv in rmap.items()}

    def frame_globals(self, posed):
        """posed: part->verts (T3 space). Returns bone-name -> (G 3x3 glTF, pivot glTF)."""
        out = {}
        for p, B in posed.items():
            if p not in self.st or p >= NPARTS: continue
            R, t, e = kabsch(self.st[p], B)
            G = self.M @ R @ self.M.T
            pv = self.pos(R @ self.piv_t3[p] + t)
            out[self.name[p]] = (G, pv)
        if "Root" not in out and "Hips" in out: out["Root"] = out["Hips"]
        return out

def sample_clip(space, kmd, bank_path, slot, step=2):
    bank = motion.parse_bank(open(bank_path, "rb").read())
    row = bank.move_index[slot]
    cp = Path(bank_path).with_name("divmot99_common.bin")
    rb = motion.parse_bank(cp.read_bytes()) if row >= motion.COMMON_FLAG else bank
    w = rb.move_row(row % motion.COMMON_FLAG)[0]
    ab = motion.parse_bank(cp.read_bytes()) if w >= motion.COMMON_FLAG else rb
    st = motion.parse_anim(ab.data, ab.anim_offset(w % motion.COMMON_FLAG))
    frames = []
    for f in range(0, st.frames, step):
        obj, _ = PA.assemble(Path(kmd), Path(bank_path), slot, f, usa_tables.EXE_PATH)
        frames.append(space.frame_globals(parse_obj_text(obj)))
    return {"slot": slot, "move_row": int(row), "stream_frames": int(st.frames), "fps": 60 / step, "frames": frames}

class TargetRig:
    def __init__(self, glb):
        b = open(glb, "rb").read(); n = struct.unpack("<I", b[12:16])[0]
        self.j = json.loads(b[20:20 + n]); self.bin = bytearray(b[20 + n + 8:])
        sk = self.j["skins"][0]; self.joints = sk["joints"]
        self.names = [self.j["nodes"][i]["name"] for i in self.joints]
        self.idx = {nm: k for k, nm in enumerate(self.names)}
        par = {c: i for i in self.joints for c in self.j["nodes"][i].get("children", [])}
        self.parent = [self.joints.index(par[i]) if par.get(i) in self.joints else -1 for i in self.joints]
        self.loc = [np.array(self.j["nodes"][i].get("translation", [0, 0, 0]), float) for i in self.joints]
        for i in self.joints: assert self.j["nodes"][i].get("rotation") in (None, [0, 0, 0, 1]), "rest must be identity (WH-Canonical-22)"
        self.wpos = []
        for k in range(len(self.joints)):
            self.wpos.append(self.loc[k] + (self.wpos[self.parent[k]] if self.parent[k] >= 0 else 0))
    def p(self, n): return self.wpos[self.idx[n]]

def swing(rig, sp, bone, child, t3a, t3b):
    if bone not in rig.idx or child not in rig.idx or t3a not in sp or t3b not in sp: return np.eye(3)
    return rot_between(rig.p(child) - rig.p(bone), sp[t3b] - sp[t3a])

def retarget(rig, space, clip):
    sp = {space.name[p]: v for p, v in space.P.items()}
    # stance foot dir from foot verts centroid
    for s in ("Left", "Right"):
        fp = [p for p, nm in space.name.items() if nm == s + "Foot"][0]
        sp[s + "Toe*"] = space.Vst[fp].mean(0)
    S = {}
    for s in ("Left", "Right"):
        S[s + "Shoulder"] = swing(rig, sp, s + "Shoulder", s + "Arm", s + "Shoulder", s + "Arm")
        S[s + "Arm"] = swing(rig, sp, s + "Arm", s + "ForeArm", s + "Arm", s + "ForeArm")
        S[s + "ForeArm"] = swing(rig, sp, s + "ForeArm", s + "Hand", s + "ForeArm", s + "Hand")
        S[s + "Hand"] = S[s + "ForeArm"]
        S[s + "UpLeg"] = swing(rig, sp, s + "UpLeg", s + "Leg", s + "UpLeg", s + "Leg")
        S[s + "Leg"] = swing(rig, sp, s + "Leg", s + "Foot", s + "Leg", s + "Foot")
        S[s + "Foot"] = swing(rig, sp, s + "Foot", s + "ToeBase", s + "Foot", s + "Toe*")
    S["Chest"] = swing(rig, sp, "Chest", "Neck", "Chest", "Head")
    hip0 = sp["Hips"]; scale = rig.p("Hips")[1] / max(hip0[1], 1e-6)
    tracks = {n: ([], []) for n in rig.names}; root_t = []
    # heading normalisation: each clip starts facing +Z (the bind facing); T3 stores the
    # fighter's world heading in the pose, which differs per move. Pure yaw, no reshaping.
    f0 = clip["frames"][0]
    fw = f0["Hips"][0] @ np.array([0, 0, 1.0]) if "Hips" in f0 else np.array([0, 0, 1.0])
    yaw0 = math.atan2(fw[0], fw[2]); c0, s0 = math.cos(-yaw0), math.sin(-yaw0)
    Y = np.array([[c0, 0, s0], [0, 1, 0], [-s0, 0, c0]])
    hp00 = f0["Hips"][1] if "Hips" in f0 else hip0
    for fr in clip["frames"]:
        G = {}
        for n in rig.names:
            if n in fr and n not in ("Root",): G[n] = Y @ fr[n][0] @ S.get(n, np.eye(3))
        G["Root"] = np.eye(3)
        if "Hips" in G and "Chest" in G:
            from scipy.spatial.transform import Rotation as Rr, Slerp
            G["Spine"] = Slerp([0, 1], Rr.from_matrix([G["Hips"], G["Chest"]]))(0.5).as_matrix()
        if "Chest" in G: G["Neck"] = G["Chest"]
        for s in ("Left", "Right"):
            if s + "Foot" in G: G[s + "ToeBase"] = G[s + "Foot"]
        for k, n in enumerate(rig.names):
            g = G.get(n, np.eye(3)); pg = G.get(rig.names[rig.parent[k]], np.eye(3)) if rig.parent[k] >= 0 else np.eye(3)
            tracks[n][0].append(quat(pg.T @ g))
        hp = fr["Hips"][1] if "Hips" in fr else hip0
        d = Y @ (hp - hp00); d[1] = hp[1] - hip0[1]   # travel from the clip start (xz), height vs stance (y)
        root_t.append((rig.loc[rig.idx["Root"]] + d * scale).tolist())
    return tracks, root_t

def append_anim(rig, name, tracks, root_t, fps, extras):
    j, b = rig.j, rig.bin
    def acc(arr, kind, minmax=False):
        arr = np.ascontiguousarray(np.asarray(arr, np.float32))
        while len(b) % 4: b.append(0)
        off = len(b); b.extend(arr.tobytes())
        j["bufferViews"].append({"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes})
        a = {"bufferView": len(j["bufferViews"]) - 1, "componentType": 5126, "count": int(arr.shape[0]), "type": kind}
        if minmax: a["min"] = [float(arr.min())]; a["max"] = [float(arr.max())]
        j["accessors"].append(a); return len(j["accessors"]) - 1
    n = len(root_t); ta = acc(np.arange(n) / fps, "SCALAR", True)
    ch, smp = [], []
    for k, bn in enumerate(rig.names):
        smp.append({"input": ta, "output": acc(tracks[bn][0], "VEC4"), "interpolation": "LINEAR"})
        ch.append({"sampler": len(smp) - 1, "target": {"node": rig.joints[k], "path": "rotation"}})
    smp.append({"input": ta, "output": acc(root_t, "VEC3"), "interpolation": "LINEAR"})
    ch.append({"sampler": len(smp) - 1, "target": {"node": rig.joints[rig.idx["Root"]], "path": "translation"}})
    j["animations"] = [a for a in j.get("animations", []) if a["name"] != name] + [{"name": name, "channels": ch, "samplers": smp, "extras": extras}]

def save(rig, path):
    j = rig.j; b = bytes(rig.bin)
    while len(b) % 4: b += b"\0"
    j["buffers"] = [{"byteLength": len(b)}]
    js = json.dumps(j, separators=(",", ":")).encode()
    while len(js) % 4: js += b" "
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(b)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(b), 0x004E4942)); f.write(b)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--bank", default="king"); ap.add_argument("--clips", default="")
    ap.add_argument("--step", type=int, default=2); ap.add_argument("--json-dir")
    a = ap.parse_args()
    kmd, bank, stance = (T3 / x for x in BANKS[a.bank])
    clips = dict(DEFAULT_CLIPS)
    if a.clips: clips = {k: int(v, 0) for k, v in (c.split("=") for c in a.clips.split(","))}
    space = T3Space(kmd, stance); rig = TargetRig(a.inp)
    sha = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (kmd, bank, usa_tables.EXE_PATH)}
    report = {}
    for nm, slot in clips.items():
        try: clip = sample_clip(space, kmd, bank, slot, a.step)
        except (SystemExit, Exception) as e: report[nm] = f"MISSING: {type(e).__name__}: {str(e)[:120]} (anim word likely in divmot99 common bank; pose_assemble.py does not resolve it yet)"; continue
        tr, rt = retarget(rig, space, clip)
        ex = {"source": "REAL decoded Tekken 3 motion (owner's disc teardown)", "bank": str(bank.relative_to(REPO)),
              "slot": hex(slot), "move_row": clip["move_row"], "stream_frames": clip["stream_frames"], "fps": clip["fps"],
              "decoder": "teardown/tekken3/tools/local/pose_assemble.py + usa_motion.py", "tool": "lab/tools/t3_motion_bake.py", "sha256": sha, "hand_keyed": False}
        append_anim(rig, nm, tr, rt, clip["fps"], ex); report[nm] = {k: ex[k] for k in ("slot", "move_row", "stream_frames")}
        if a.json_dir:
            Path(a.json_dir).mkdir(parents=True, exist_ok=True)
            json.dump({"format": "wh-anim/1", **ex, "bones": rig.names, "rot_xyzw": {k: v[0] for k, v in tr.items()}, "root_t": rt},
                      open(Path(a.json_dir) / f"{nm}.json", "w"), separators=(",", ":"))
    rig.j.setdefault("extras", {})["t3_real_clips"] = report
    save(rig, a.out); print(json.dumps(report, indent=1))

if __name__ == "__main__": main()
