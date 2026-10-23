#!/usr/bin/env python3
"""Export the SOURCE skeleton of each decoded Tekken 3 motion bank for runtime retargeting.

The wh-anim/1 bank clips (game/assets/anim/t3/<bank>/*.json) store LOCAL joint
rotations of the rig they were baked onto by lab/tools/t3_motion_bake.py:
  king  -> lab/game/assets/pantera_leoman_t3real.glb  (WH-Canonical-22 hierarchy)
  jin, xiaoyu, bryan, gunjack, yoshimitsu
        -> lab/game/assets/t3_<bank>_t3real.glb        (T3 18-part import: Chest hangs off Root)
Every joint of those rigs has identity rest rotation, so a clip is only meaningful
together with that rig's hierarchy and rest joint positions. This tool writes them
next to the clips as skeleton.json (format wh-anim-skel/1); game/js/t3anims.js uses
it to retarget each clip onto the fighter's own rig (same swing math as
t3_motion_bake.retarget). Nothing here is authored: every number is read from the
source GLB, whose SHA-256 is recorded.

Usage: python3 tools/anim/t3_bank_skeleton.py            # all banks
       python3 tools/anim/t3_bank_skeleton.py --check    # verify bank clips match their source GLB
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
BANKS = {
    "king_on_pantera_leoman": "lab/game/assets/pantera_leoman_t3real.glb",
    "jin": "lab/game/assets/t3_jin_t3real.glb",
    "xiaoyu": "lab/game/assets/t3_xiaoyu_t3real.glb",
    "bryan": "lab/game/assets/t3_bryan_t3real.glb",
    "gunjack": "lab/game/assets/t3_gunjack_t3real.glb",
    "yoshimitsu": "lab/game/assets/t3_yoshimitsu_t3real.glb",
    # Heihachi's own divmot13 motion posed on Jin's T3 skeleton (tools/anim/t3_row_bake.py
    # --bank heihachi --kmd-from jin): heihachi191's KMD has no hip/shoulder vertex data.
    "heihachi_on_jin": "lab/game/assets/t3_jin.glb",
    # Remainder banks (2026-10-20): divmot banks decoded via lab/tools/t3_motion_bake.py
    # onto each character's own WH-Canonical-22 GLB (see docs/anim/T3-REMAINDER-BANKS-20261020.md).
    # heihachi = the own-rig divmot13 decode (pose-chain pivot override);
    # armorking = divmot03_king baked on King's own rig.
    "paul": "lab/game/assets/t3_paul_t3real.glb",
    "lei": "lab/game/assets/t3_lei_t3real.glb",
    "nina": "lab/game/assets/t3_nina_t3real.glb",
    "hwoarang": "lab/game/assets/t3_hwoarang_t3real.glb",
    "eddy": "lab/game/assets/t3_eddy_t3real.glb",
    "julia": "lab/game/assets/t3_julia_t3real.glb",
    "anna": "lab/game/assets/t3_anna_t3real.glb",
    "bosconovitch": "lab/game/assets/t3_bosconovitch_t3real.glb",
    "heihachi": "lab/game/assets/t3_heihachi_t3real.glb",
    "armorking": "lab/game/assets/t3_armorking_t3real.glb",
}
# ---------------------------------------------------------------------------
# NEUTRAL_BIND (2026-10-22, star segment-flip fix): the T3 18-part import
# rigs carry a POSED STANCE FRAME as their joint positions (xiaoyu: thighs
# slanted fwd ~33 deg, shins back ~31 deg, forearms crossed to the opposite
# hip, Chest joint sitting on the Hips). The runtime retarget
# (game/js/t3anims.js) derives its per-bone swing A from the bank skeleton's
# rest directions, so a posed "rest" injects that stance into every frame of
# every clip: measured in-game, xiaoyu-bank forearm fronts landed 130-170 deg
# off the decoded motion on every rig tested (Star, Pantera), legs pitched
# 33-39 deg. King's bank (WH-Canonical-22) uses a true neutral bind and
# retargets cleanly (all swings <= ~9 deg). For the banks listed here,
# rebuild the rest positions as a neutral bind in the king pattern from the
# source rig's OWN bone lengths (lengths are pose-invariant) and proportions.
# Clip files are untouched: their world rotations do not depend on skeleton
# positions (positions feed only the swing/facing derivation).
NEUTRAL_BIND_GLBS = {"lab/game/assets/t3_xiaoyu_t3real.glb"}
NEUTRAL_BIND_NOTE = (
    " CORRECTED 2026-10-22 (star segment-flip fix): the source GLB's joint positions are a posed stance frame, "
    "not a bind (thighs slanted fwd, shins back, forearms crossed to the opposite hip, Chest joint on the Hips). "
    "The runtime retarget derives its per-bone swing from these rest directions, so the stance was injected into "
    "every frame of every clip (forearm fronts 130-170 deg off the decoded motion on every rig tested). "
    "Rest positions rebuilt as a neutral bind from the source rig's own bone lengths and proportions "
    "(king-canonical pattern; tools/anim/t3_bank_skeleton.py NEUTRAL_BIND_GLBS). Clip files are unchanged: "
    "their world rotations do not depend on skeleton positions.")


def neutral_bind(out):
    """Neutral-bind rest positions for a stance-posed source skeleton."""
    P = {j["name"]: np.array(j["rest"], float) for j in out}
    L = lambda a, b: float(np.linalg.norm(P[b] - P[a]))
    root_y = float(P["Root"][1])
    scale = root_y / 0.9805  # king bank's root height (canonical proportions)
    hip_half = float(np.mean([abs(P["LeftUpLeg"][0]), abs(P["RightUpLeg"][0])]))
    hip_y = root_y - 0.056 * scale          # king: Hips -> UpLeg vertical drop
    chest_y = root_y + 0.351 * scale        # king: Hips -> Chest rise
    head_y = chest_y + 0.296 * scale        # king: Chest -> Head rise
    sh_y = chest_y + 0.053 * scale          # king: Chest -> Shoulder rise
    sh_half = max(0.055, min(0.074, 0.074 * (hip_half / 0.154)))
    new = {"Root": [0.0, root_y, 0.0], "Hips": [0.0, root_y, 0.0],
           "Chest": [0.0, chest_y, 0.0], "Head": [0.0, head_y, 0.0]}
    tips = {}
    for s, sgn in (("Left", 1.0), ("Right", -1.0)):
        thigh, shin = L(s + "UpLeg", s + "Leg"), L(s + "Leg", s + "Foot")
        knee_y = hip_y - thigh
        ank_y = knee_y - shin
        new[s + "UpLeg"] = [sgn * hip_half, hip_y, 0.0]
        new[s + "Leg"] = [sgn * (hip_half + 0.004), knee_y, 0.0]
        new[s + "Foot"] = [sgn * (hip_half + 0.004), ank_y, 0.0]
        clav, upper, fore = (L(s + "Shoulder", s + "Arm"), L(s + "Arm", s + "ForeArm"),
                             L(s + "ForeArm", s + "Hand"))
        new[s + "Shoulder"] = [sgn * sh_half, sh_y, 0.0]
        new[s + "Arm"] = [sgn * (sh_half + clav), sh_y, 0.0]
        new[s + "ForeArm"] = [sgn * (sh_half + clav + upper), sh_y, 0.0]
        new[s + "Hand"] = [sgn * (sh_half + clav + upper + fore), sh_y, 0.0]
        ts = root_y / 0.989226  # flat forward toe, king's foot direction
        tips[s + "Foot"] = [round(float(new[s + "Foot"][0]), 6),
                            round(float(new[s + "Foot"][1] - 0.048 * ts), 6),
                            round(float(new[s + "Foot"][2] + 0.135 * ts), 6)]
    for j in out:
        j["rest"] = [round(float(v), 6) for v in new[j["name"]]]
    return out, tips


COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def read_glb(path):
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    blob = b[20 + n + 8:]
    return j, blob


def accessor(j, blob, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    nc = NCOMP[a["type"]]
    dt = np.dtype(COMP[a["componentType"]])
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = bv.get("byteStride", 0) or nc * dt.itemsize
    out = np.empty((a["count"], nc), dt)
    for k in range(a["count"]):
        out[k] = np.frombuffer(blob, dt, nc, off + k * stride)
    return out


def skeleton(glb_rel):
    path = REPO / glb_rel
    j, blob = read_glb(path)
    N = j["nodes"]
    sk = j["skins"][0]
    joints = sk["joints"]
    par = {c: i for i, nd in enumerate(N) for c in nd.get("children", [])}
    for i in joints:
        r = N[i].get("rotation")
        if r not in (None, [0, 0, 0, 1]):
            sys.exit(f"{glb_rel}: joint {N[i]['name']} has non-identity rest {r} — not a wh-anim source rig")

    def world_pos(i):
        p = np.array(N[i].get("translation", [0, 0, 0]), float)
        return p + (world_pos(par[i]) if i in par else 0)

    out = []
    for i in joints:
        p = par.get(i)
        out.append({"name": N[i]["name"], "parent": N[p]["name"] if p in joints else None,
                    "rest": [round(float(x), 6) for x in world_pos(i)]})
    names = [N[i]["name"] for i in joints]
    # Foot direction for rigs without a ToeBase joint.
    # The game retarget (t3anims.js sourceInfo/retargetT3Clips) swings every
    # target foot's rest direction to this vector, so it MUST be the canonical
    # rig's toe (ankle->toe, forward-down). The old method — centroid of the
    # foot-part verts ("the same Toe* the bake swings to") — is a bad toe
    # estimator on blobby T3 parts: it put Bosconovitch's feet ~90 deg sideways
    # and Gunjack's backward, duck-footing every fighter on those banks
    # (owner report 2026-10-21: Doc Frank's feet point sideways on all models).
    # We keep the centroid when it agrees with the canonical toe (yaw within
    # 60 deg of the bank's forward) so good banks regenerate byte-identical;
    # otherwise we use the WH-Canonical-22 template toe in the bank's frame.
    wpos = {N[i]["name"]: world_pos(i) for i in joints}
    # Bank forward from the knees (same signal as t3anims.js bankFacing):
    # knee offset from the hip-ankle line, horizontal, averaged over legs.
    _fw = []
    for _s in ("Left", "Right"):
        if _s + "Leg" in wpos and _s + "Foot" in wpos and "Hips" in wpos:
            _kd = wpos[_s + "Leg"] - (wpos["Hips"] + wpos[_s + "Foot"]) / 2
            _kd[1] = 0
            if np.linalg.norm(_kd) > 1e-6:
                _fw.append(_kd / np.linalg.norm(_kd))
    _fwd = sum(_fw) / len(_fw) if _fw else np.array([0.0, 0.0, 1.0])
    _fwd /= np.linalg.norm(_fwd)
    # Template toe (ankle->toe tip); the template faces -Z (yaw 180 deg).
    _tt = np.array([0.0, -0.08, -0.21])
    _tt /= np.linalg.norm(_tt)
    _yaw = lambda _d: float(np.degrees(np.arctan2(_d[0], _d[2])))
    _rot = np.radians(_yaw(_fwd) - 180.0)
    _cc, _ss = float(np.cos(_rot)), float(np.sin(_rot))
    _tbank = np.array([_tt[0] * _cc + _tt[2] * _ss, _tt[1],
                       -_tt[0] * _ss + _tt[2] * _cc])
    tips = {}
    for side in ("Left", "Right"):
        foot = side + "Foot"
        if side + "ToeBase" in names or foot not in names:
            continue
        fi = names.index(foot)
        ankle = wpos[foot]
        acc_v, acc_n = np.zeros(3), 0
        for m in j["meshes"]:
            for pr in m["primitives"]:
                at = pr["attributes"]
                if "JOINTS_0" not in at:
                    continue
                pos = accessor(j, blob, at["POSITION"]).astype(float)
                jt = accessor(j, blob, at["JOINTS_0"]).astype(int)
                wt = accessor(j, blob, at["WEIGHTS_0"]).astype(float)
                dom = jt[np.arange(len(jt)), wt.argmax(1)]
                sel = dom == fi
                acc_v += pos[sel].sum(0)
                acc_n += int(sel.sum())
        if not acc_n:
            continue
        centroid = acc_v / acc_n
        _cd = centroid - ankle
        _ch = float(np.hypot(_cd[0], _cd[2]))
        _bad = _ch < 1e-6 or abs((_yaw(_cd) - _yaw(_tbank) + 180) % 360 - 180) > 60
        if _bad:
            # Canonical toe, scaled by ankle height (template: 0.225 m at 0.12 m).
            _L = 0.225 * (ankle[1] / 0.12)
            tip = ankle + _tbank * _L
        else:
            tip = centroid
        # Mesh is bound in rest = world (identity rest, no node transform above the skin root).
        tips[foot] = [round(float(x), 6) for x in tip]
    note = "Rest pose of the rig the bank's clips were baked onto. All joint rest rotations are identity; rest = world joint positions (glTF space, meters, faces +Z, character left = +X)."
    if glb_rel in NEUTRAL_BIND_GLBS:
        out, tips = neutral_bind(out)
        note += NEUTRAL_BIND_NOTE
    root = out[0]
    return {
        "format": "wh-anim-skel/1",
        "source_glb": glb_rel,
        "source_glb_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "tool": "tools/anim/t3_bank_skeleton.py",
        "note": note,
        "root": root["name"],
        "root_rest_y": root["rest"][1],
        "joints": out,
        "foot_tip": tips,
    }


def check(bank, glb_rel):
    """Clip rotations in the bank JSONs must equal the source GLB's own animation channels."""
    j, blob = read_glb(REPO / glb_rel)
    anims = {a["name"]: a for a in j.get("animations", [])}
    worst, n = 0.0, 0
    for f in sorted((REPO / "game/assets/anim/t3" / bank).glob("t3_*.json")):
        d = json.loads(f.read_text())
        a = anims.get(f.stem)
        if not a:
            continue
        for ch in a["channels"]:
            if ch["target"]["path"] != "rotation":
                continue
            nm = j["nodes"][ch["target"]["node"]]["name"]
            if nm not in d["rot_xyzw"]:
                continue
            A = np.array(d["rot_xyzw"][nm], float)
            B = accessor(j, blob, a["samplers"][ch["sampler"]]["output"]).astype(float)
            m = min(len(A), len(B))
            worst = max(worst, float(np.abs(np.abs((A[:m] * B[:m]).sum(1)) - 1).max()))
            n += 1
    return n, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    for bank, glb in BANKS.items():
        if a.check:
            n, worst = check(bank, glb)
            if n == 0:
                print(f"{bank:24s} no source-GLB clips to compare (clips baked by tools/anim/t3_row_bake.py)")
            else:
                print(f"{bank:24s} channels={n:4d} max |1-|q.q'|| = {worst:.2e}  {'OK' if worst < 1e-5 else 'MISMATCH'}")
            continue
        sk = skeleton(glb)
        dst = REPO / "game/assets/anim/t3" / bank / "skeleton.json"
        dst.write_text(json.dumps(sk, indent=1) + "\n")
        print(f"{bank:24s} {len(sk['joints'])} joints, root_rest_y={sk['root_rest_y']:.3f}, foot_tip={list(sk['foot_tip'])} -> {dst.relative_to(REPO)}")


if __name__ == "__main__":
    main()
