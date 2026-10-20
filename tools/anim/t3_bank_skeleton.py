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
}
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
    # Foot direction for rigs without a ToeBase joint: the centroid of the vertices
    # skinned (dominant weight) to the foot — the same "Toe*" the bake swings to
    # (t3_motion_bake.retarget: sp[s+"Toe*"] = mean of the T3 foot part's stance verts).
    tips = {}
    for side in ("Left", "Right"):
        foot = side + "Foot"
        if side + "ToeBase" in names or foot not in names:
            continue
        fi = names.index(foot)
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
        if acc_n:
            # Mesh is bound in rest = world (identity rest, no node transform above the skin root).
            tips[foot] = [round(float(x), 6) for x in acc_v / acc_n]
    root = out[0]
    return {
        "format": "wh-anim-skel/1",
        "source_glb": glb_rel,
        "source_glb_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "tool": "tools/anim/t3_bank_skeleton.py",
        "note": "Rest pose of the rig the bank's clips were baked onto. All joint rest rotations are identity; rest = world joint positions (glTF space, meters, faces +Z, character left = +X).",
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
