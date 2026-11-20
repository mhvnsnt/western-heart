#!/usr/bin/env python3
"""Export the 6 decoded UR stage PPKs to OBJ for the game (follow-on 5).
Uses ONLY the Editor's meshes.load (Source/editor/meshes.py) — the same tool
Lane 4 used. No hand-written VMD/PPK parser.
Per stage PPK (003/004/028/029/030/031): largest non-fighter VMD -> meshes.load
-> OBJ (v x y z r g b / vt u v / f a/b c/d e/f triangles) + posset JSON
(0.5 m grid, for the mission<->stage link test) + color/bounds stats.
Vertex colors are the VMD's decoded per-vertex colors (clipped 0-1); the game
builder uses them directly (no texture map yet — textures are the named
follow-up; the OBJ keeps UVs so the textured swap can use them).
Output OBJs go straight into the branch working tree:
  /var/tmp/wh-ur-stages/game/assets/stages/ur/stageNNN.obj
"""
import sys, os, json, hashlib, base64
from pathlib import Path

os.environ.setdefault("URR_ROOT", "/tmp/urr_root")
HOME = Path.home()
RL = HOME / "workspace/urban-reign-redux/work/tools/vendor/roster-lib"
ED = HOME / "workspace/urban-reign-redux/decoded/editor-src/Urban Reign Redux Editor 0.5/Source"
sys.path.insert(0, str(RL))
sys.path.insert(0, str(ED))
sys.path.insert(0, str(ED / "vendor" / "native"))
sys.path.insert(0, str(ED / "vendor"))
from toolnative.ppk_index import ppk_entries
from toolnative.vmd_structure import parse_vmd
from editor import meshes
import numpy as np

INP = HOME / "workspace/urban-reign-redux/decoded/inputs"
OBJDIR = Path("/var/tmp/wh-ur-stages/game/assets/stages/ur")
OBJDIR.mkdir(parents=True, exist_ok=True)
OUT = Path("/var/tmp/ur-census")
FIGHTER_BONES = {"KUBI", "KOSHI", "MUNE", "KATA_L", "KATA_R", "HIZA_L", "HIZA_R"}

report = {}
for tag in ("stage003", "stage004", "stage028", "stage029", "stage030", "stage031"):
    b = (INP / f"{tag}.ppk").read_bytes()
    p = ppk_entries(b)
    cands = []
    for e in p["entries"]:
        data = b[e["offset"]:e["offset"] + e["size"]]
        try:
            v = parse_vmd(data)
        except Exception:
            continue
        names = {nd.get("name") for nd in v["nodes"] if not nd.get("unused")}
        if not (names & FIGHTER_BONES):
            cands.append((e["key"], data, v))
    key, data, v = max(cands, key=lambda t: len(t[1]))
    payload, textures, rig = meshes.load(data)
    pos = np.frombuffer(base64.b64decode(payload["position"]), dtype=np.float32).reshape(-1, 3)
    uv = np.frombuffer(base64.b64decode(payload["uv"]), dtype=np.float32).reshape(-1, 2)
    col = np.frombuffer(base64.b64decode(payload["color"]), dtype=np.float32).reshape(-1, 4)[:, :3]
    col = np.clip(col, 0, 1)
    idx = np.frombuffer(base64.b64decode(payload["index"]), dtype=np.uint32).reshape(-1, 3)
    lines = [f"# Urban Reign {tag}.ppk VMD {key} — decoded with Redux Editor meshes.load",
             f"# vertices {len(pos)} triangles {len(idx)} textures_decoded {len(payload['textures'])}",
             "# units: metres (world space, no scale). Vertex colors are the VMD decoded colors."]
    for (x, y, z), (r, g, bl) in zip(pos, col):
        lines.append(f"v {x:.4f} {y:.4f} {z:.4f} {r:.4f} {g:.4f} {bl:.4f}")
    for u, w in uv:
        lines.append(f"vt {u:.5f} {w:.5f}")
    for a, c_, d in idx:
        lines.append(f"f {a+1}/{a+1} {c_+1}/{c_+1} {d+1}/{d+1}")
    text = "\n".join(lines) + "\n"
    obj_path = OBJDIR / f"{tag}.obj"
    obj_path.write_text(text)
    q = np.round(pos / 0.5).astype(np.int64)
    posset = sorted(set(map(tuple, q.tolist())))
    (OUT / f"{tag}.posset.json").write_text(json.dumps(
        {"file": f"{tag}.ppk", "vmd_key": key, "positions": len(pos),
         "posset_size": len(posset), "posset": posset, "bounds_world": payload["bounds"]}))
    mean = col.mean(0)
    hexcol = "#%02x%02x%02x" % tuple(int(round(float(c) * 255)) for c in mean)
    report[tag] = {
        "vmd_key": key, "vertices": len(pos), "triangles": len(idx),
        "draws": len(payload["draws"]), "textures_decoded": len(payload["textures"]),
        "bounds_world": payload["bounds"],
        "color_mean_rgb": [round(float(c), 4) for c in mean],
        "color_mean_hex": hexcol,
        "color_frac_nonwhite": round(float((np.abs(col - 1.0).max(1) > 0.01).mean()), 4),
        "unique_rgb_rounded_0.1": len(set(map(tuple, np.round(col, 1).tolist()))),
        "uv_frac_zero": round(float(((uv == 0).all(1)).mean()), 4),
        "obj_bytes": len(text.encode()), "obj_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "obj_path": str(obj_path),
    }
    print(tag, "verts", len(pos), "tris", len(idx), "color mean", hexcol,
          "nonwhite frac", report[tag]["color_frac_nonwhite"], "obj MB", round(len(text.encode()) / 1e6, 2), flush=True)
(OUT / "stage_export_report.json").write_text(json.dumps(report, indent=2))
print("done")
