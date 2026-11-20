#!/usr/bin/env python3
"""Western Heart model import (prototype). Spec: docs/MODEL_IMPORT_AUTORIG.md
  python3 tools/import_model.py <path.glb | drive-link | drive-file-id> --character <id> [--new "NAME"] --attire <a1|...> [--render]
Steps: fetch -> version copy (never overwrite) -> rig map -> segment -> retarget map (P1) -> rig gates -> register -> (optional) card render.
Exit 0 only when every gate passes. Originals are never modified."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, pathlib
import numpy as np, pygltflib
ROOT = pathlib.Path(__file__).resolve().parents[1]
CANON = json.load(open(ROOT / "lab/skeleton/canonical_skeleton.json"))
ALIASES = {"Spine2": "Chest", "Spine1": "Spine", "UpperChest": "Chest", "Pelvis": "Hips", "Hip": "Hips",
           "L_UpperArm": "LeftArm", "R_UpperArm": "RightArm", "Head_end": None}
SEG = {"head": ["Head", "Neck"], "torso": ["Hips", "Spine", "Chest", "Root"],
       "arm_l": ["LeftShoulder", "LeftArm", "LeftForeArm"], "hand_l": ["LeftHand"],
       "arm_r": ["RightShoulder", "RightArm", "RightForeArm"], "hand_r": ["RightHand"],
       "leg_l": ["LeftUpLeg", "LeftLeg"], "foot_l": ["LeftFoot", "LeftToeBase"],
       "leg_r": ["RightUpLeg", "RightLeg"], "foot_r": ["RightFoot", "RightToeBase"]}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

def canon_name(n):
    n = re.sub(r"^(mixamorig[:_]?|Bip0?1[ _]?|DEF[-_])", "", n)
    if n in ALIASES: return ALIASES[n]
    for k in ("Thumb", "Index", "Middle", "Ring", "Pinky"):
        if k in n: return None          # fingers ride along, not canonical-22
    return n if n in {b["name"] for b in CANON["bones"]} else None

def fetch(src, work):
    if os.path.exists(src): return src
    m = re.search(r"(?:/d/|id=)([\w-]{20,})", src) or re.fullmatch(r"([\w-]{20,})", src)
    if not m: sys.exit(f"FAIL fetch: {src} is not a file or Drive id/link")
    out = work / f"drive_{m.group(1)}.glb"
    if shutil.which("gdown") and subprocess.call(["gdown", "--id", m.group(1), "-O", str(out)]) == 0: return str(out)
    sys.exit("FAIL fetch: Drive file needs auth. Agents: use the DownloadFile tool (connection google-drive, "
             f"fileId {m.group(1)}) to a local path, then re-run with that path.")

def world_mats(g):
    W = {}
    def tr(n):
        if n.matrix: return np.array(n.matrix).reshape(4, 4).T
        T, R, S = np.eye(4), np.eye(4), np.eye(4)
        if n.translation: T[:3, 3] = n.translation
        if n.rotation:
            x, y, z, w = n.rotation
            R[:3, :3] = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
        if n.scale: S = np.diag(list(n.scale) + [1])
        return T @ R @ S
    def walk(i, P):
        W[i] = P @ tr(g.nodes[i])
        for c in g.nodes[i].children or []: walk(c, W[i])
    for s in g.scenes[g.scene or 0].nodes: walk(s, np.eye(4))
    return W

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("--character", required=True)
    ap.add_argument("--new"); ap.add_argument("--attire", default="a1"); ap.add_argument("--render", action="store_true")
    a = ap.parse_args(); cid = a.character
    d = ROOT / "roster" / cid / "imports"; d.mkdir(parents=True, exist_ok=True)
    src = fetch(a.src, d)
    # BLENDER17-01 fallback import path (worker 80, 2026-10-22): SmutBase
    # .blend files carrying the 17-byte BLENDER17-01 header (often inside a
    # zstd stream mislabeled ".blend") route through the direct mesh
    # extractor instead of failing at the GLB gate. The extractor builds an
    # unrigged GLB (+ armature/weights JSON sidecars) for the normal
    # auto-rig pipeline. See tools/blender17-extract/README.md.
    _b17 = ROOT / "tools" / "blender17-extract" / "route.py"
    if _b17.exists():
        import importlib.util
        _spec = importlib.util.spec_from_file_location("blend17_route", str(_b17))
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        _routed = _mod.maybe_route(src, d / "blend17")
        if _routed:
            print(f"BLEND17-01 fallback: {src} -> {_routed}")
            src = _routed
    # UNIRIG GPU auto-rig hook (tools/rig-intake/): when an unrigged mesh comes
    # in and a CUDA GPU + UniRig checkout are present, rig it here so the rest
    # of the pipeline runs unchanged. Graceful no-op otherwise.
    _unirig_rep = {}
    try:
        _probe = pygltflib.GLTF2().load(str(src)) if str(src).lower().endswith(".glb") else None
    except Exception:
        _probe = None
    if _probe is not None and not _probe.skins:
        _uri = ROOT / "tools" / "rig-intake" / "unirig_intake.py"
        if _uri.exists():
            import importlib.util as _ilu
            try:
                _uspec = _ilu.spec_from_file_location("wh_unirig_intake", str(_uri))
                _umod = _ilu.module_from_spec(_uspec)
                _uspec.loader.exec_module(_umod)
                _rigged = _umod.maybe_autorig(src, d / "unirig")
                if _rigged:
                    print(f"UNIRIG auto-rig: {src} -> {_rigged}")
                    _unirig_rep = {"provider": "UniRig (SIGGRAPH 2025)",
                                   "unrigged_input": str(src), "rigged_output": str(_rigged)}
                    src = _rigged
            except Exception as e:
                print(f"UNIRIG hook skipped ({e}); continuing with original mesh")
    v = 1
    while (d / f"{a.attire}_v{v}.glb").exists(): v += 1           # version, never overwrite
    dst = d / f"{a.attire}_v{v}.glb"; shutil.copy2(src, dst)
    assert sha(src) == sha(dst); print("COPY", dst.relative_to(ROOT), sha(dst)[:16])
    g = pygltflib.GLTF2().load(str(dst)); gates, rep = {}, {"source": a.src, "sha256_source": sha(src), "file": str(dst.relative_to(ROOT)), "sha256": sha(dst)}
    if _unirig_rep:
        rep["unirig_autorig"] = _unirig_rep
    if not g.skins:
        gates["rigged"] = False
        rep["fix"] = ("Unrigged mesh and no GPU auto-rig ran. Options: "
                      "(1) UniRig GPU auto-rig — setup: tools/rig-intake/UNIRIG-SETUP.md (needs CUDA 8GB+); "
                      "(2) run Tripo/Mixamo auto-rig on the T-pose model (docs/tpose-refs/MUSE_TPOSE_SPEC.md), then re-import.")
    else:
        sk = g.skins[0]; W = world_mats(g)
        bmap = {g.nodes[j].name: canon_name(g.nodes[j].name) for j in sk.joints}
        have = {c: j for j, c in zip(sk.joints, bmap.values()) if c}
        rep["bone_map"] = bmap
        SEC = {"breast": r"breast|bust|boob", "butt": r"butt|glute|cheek", "thigh": r"thigh", "hair": r"hair|ponytail|pigtail|bun", "tail": r"tail", "skirt": r"skirt", "belly": r"belly"}
        rep["secondary"] = {k: [n for n in bmap if re.search(rx, n, re.I)] for k, rx in SEC.items()}; P = {c: W[j][:3, 3] for c, j in have.items()}
        req = CANON["required_for_rig_check"]; missing = [r for r in req if r not in have]
        gates["rigged"] = True; gates["required_bones"] = not missing; rep["missing"] = missing
        if not missing:
            up = P["Head"] - P["Hips"]; ax = int(np.argmax(np.abs(up)))
            h = float(np.ptp(np.array(list(P.values()))[:, ax])) * 1.1; rep["height_m"] = round(h, 3)
            gates["height_1.3_2.4m"] = 1.3 < h < 2.4
            arm = P["LeftHand"] - P["LeftArm"]; rep["arm_vs_up_deg"] = round(float(np.degrees(np.arccos(abs(arm @ up) / np.linalg.norm(arm) / np.linalg.norm(up)))), 1)
            gates["t_or_a_pose(arm>=40deg_from_spine)"] = rep["arm_vs_up_deg"] >= 40
            lr = (P["LeftHand"] - P["RightHand"]); rep["left_minus_right"] = [round(float(x), 3) for x in lr]
            gates["symmetric_hands"] = abs(np.linalg.norm(P["LeftHand"] - P["Hips"]) - np.linalg.norm(P["RightHand"] - P["Hips"])) < 0.05 * h
        # segment: dominant joint per vertex -> Tekken-style body segments
        jn = [bmap[g.nodes[j].name] for j in sk.joints]; seg_of = {b: s for s, bs in SEG.items() for b in bs}
        counts = {s: 0 for s in SEG}; counts["unmapped"] = 0
        blob = g.binary_blob()
        for m in g.meshes:
            for p in m.primitives:
                if p.attributes.JOINTS_0 is None: continue
                def arr(acc_i, dt, n):
                    acc = g.accessors[acc_i]; bv = g.bufferViews[acc.bufferView]
                    return np.frombuffer(blob, dtype=dt, count=acc.count * n, offset=(bv.byteOffset or 0) + (acc.byteOffset or 0)).reshape(-1, n)
                ja = g.accessors[p.attributes.JOINTS_0]; J = arr(p.attributes.JOINTS_0, {5121: np.uint8, 5123: np.uint16}[ja.componentType], 4)
                Wt = arr(p.attributes.WEIGHTS_0, np.float32, 4)
                for jdx in J[np.arange(len(J)), Wt.argmax(1)]:
                    c = jn[jdx] if jdx < len(jn) else None; counts[seg_of.get(c, "unmapped")] += 1
        rep["segments_vertex_count"] = counts
        gates["segments_cover_body"] = all(counts[s] > 0 for s in ("head", "torso", "arm_l", "arm_r", "leg_l", "leg_r"))
        # retarget: canonical skeleton is world-aligned, clips retarget by name -> the map IS the retarget spec
        p1 = pygltflib.GLTF2().load(str(ROOT / "lab/game/assets/pantera_leoman.glb"))
        rep["p1_clips"] = [an.name for an in p1.animations]
        rep["retarget_map"] = {k: v for k, v in bmap.items() if v}
        gates["retarget_map_complete"] = gates["required_bones"]
    gates = {k: bool(x) for k, x in gates.items()}; rep["gates"] = gates; ok = all(gates.values()); rep["status"] = "PASS" if ok else "FAIL"
    man = ROOT / "docs/roster" / cid; man.mkdir(parents=True, exist_ok=True)
    (man / f"import_{a.attire}_v{v}.json").write_text(json.dumps(rep, indent=1))
    if ok:   # register in select data
        reg = ROOT / "game/ui-wh/imports.json"; R = json.loads(reg.read_text()) if reg.exists() else {}
        R.setdefault(cid, {})[a.attire] = {"glb": rep["file"], "sha256": rep["sha256"], "name": a.new or cid.upper(),
            "bust": f"portraits/{cid}_{a.attire}v{v}_bust.png", "full": f"portraits/{cid}_{a.attire}v{v}_full.png", "new_fighter": bool(a.new)}
        reg.write_text(json.dumps(R, indent=1, ensure_ascii=False))
        if a.render:
            pre = ROOT / f"game/ui-wh/portraits/{cid}_{a.attire}v{v}"
            subprocess.call(["xvfb-run", "-a", "godot", "--rendering-driver", "opengl3", "--path", str(ROOT / "lab/game"), "-s",
                             "res://tools/render_card.gd", "--", str(dst), str(pre), "none", "20"])
    for k, x in gates.items(): print(("PASS " if x else "FAIL ") + k)
    print("IMPORT", rep["status"], man / f"import_{a.attire}_v{v}.json"); sys.exit(0 if ok else 1)
main()
