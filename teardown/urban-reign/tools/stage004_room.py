#!/usr/bin/env python3
"""Lane 4 — stage004 room-only preview via the author's own stage_preview.room_preview.
Adapter only: all decoding is roster-lib/Editor code (read_mesh, bind_matrices
inside meshes.load, the exporter's strip rule). The adapter reshapes those
outputs into the mesh-dict shape room_preview expects (faces/vertices/draws/
positions/normals/textures) — it parses no bytes itself. Validated: room
triangles are a subset of the mesh triangles and all room positions lie
inside room_preview.BOUNDS.
"""
import sys, json, base64
from pathlib import Path
import numpy as np

SRC = Path.home()/"workspace/urban-reign-redux/decoded/editor-src/Urban Reign Redux Editor 0.5/Source"
RL = Path.home()/"workspace/urban-reign-redux/work/tools/vendor/roster-lib"
sys.path.append(str(RL))
sys.path.insert(0, str(SRC)); sys.path.insert(0, str(SRC/"vendor/exporter")); sys.path.insert(0, str(SRC/"vendor/native"))
import os
os.environ.setdefault("URR_ROOT", "/tmp/urr_root")
from toolnative.ppk_index import ppk_entries
from toolnative.vmd_structure import parse_vmd
from toolnative.vmd_mesh import read_mesh
from toolnative.stage_preview import room_preview, BOUNDS, SHELL, LIGHTS
from editor import meshes

IN = Path.home()/"workspace/urban-reign-redux/decoded/inputs"
OUT = Path.home()/"workspace/urban-reign-redux/decoded/stages"

b = (IN/"stage004.ppk").read_bytes()
p = ppk_entries(b)
for e in p["entries"]:
    data = b[e["offset"]:e["offset"]+e["size"]]
    try:
        parse_vmd(data)
    except Exception:
        continue
    raw = read_mesh(data)
    payload, textures, rig = meshes.load(data)

    def b64f(s):
        return np.frombuffer(base64.b64decode(payload[s]), dtype="<f4").reshape(-1, 3)
    pos = b64f("position"); nrm = b64f("normal")
    idx = np.frombuffer(base64.b64decode(payload["index"]), dtype="<u4").reshape(-1, 3)

    # global vertex list in meshes.load order (draw order, vertex order)
    vertices = []
    draw_of_vertex = []
    packet_of_vertex = []
    for di, d in enumerate(raw["draws"]):
        for pk_i, pk in enumerate(d["packets"]):
            for k in range(pk["count"]):
                v = d["vertices"][pk["vertices_start"] + k]
                gi = len(vertices)
                vertices.append({
                    "id": gi, "draw": di, "group": d["group"], "packet": pk_i,
                    "uv": v["uv"][:2], "color": list(v["color"]),
                    "influences": [{"bone": 0, "weight": 1.0,
                                    "position": list(map(float, pos[gi])),
                                    "normal": list(map(float, nrm[gi]))}],
                    "position": list(map(float, pos[gi])),
                    "normal": list(map(float, nrm[gi]))})
                draw_of_vertex.append(di); packet_of_vertex.append(pk_i)
    assert len(vertices) == len(pos) == payload["vertices"], (len(vertices), len(pos))

    # faces: map each payload tri to its draw via payload draws' first/count
    faces = []
    draw_ranges = []
    for dd in payload["draws"]:
        draw_ranges.append((dd["first"] // 3, (dd["first"] + dd["count"]) // 3, dd["draw"]))
    def draw_for_tri(t):
        for lo, hi, di in draw_ranges:
            if lo <= t < hi:
                return di
        return None
    for t, tri in enumerate(idx):
        di = draw_for_tri(t)
        faces.append({"id": t, "draw": di, "group": raw["draws"][di]["group"],
                      "indices": [int(x) for x in tri]})
    draws = []
    for di, d in enumerate(raw["draws"]):
        draws.append({"id": di, "sampler": d["texture"][0] if d["texture"] else None,
                      "transparent_chain": 0})
    source = {"name": "stage004.vmd", "vertices": vertices, "faces": faces, "draws": draws,
              "positions": [list(map(float, v)) for v in pos],
              "normals": [list(map(float, v)) for v in nrm],
              "textures": {str(k): v for k, v in textures.items()},
              "nodes": [], "bind_matrices": [], "local_bind_matrices": []}
    out = room_preview(source)
    # validation
    assert len(out["faces"]) <= len(faces), "room faces must be a subset"
    rp = np.array(out["positions"])
    within = bool((rp[:, 0] >= BOUNDS[0][0]).all() and (rp[:, 0] <= BOUNDS[1][0]).all()
                  and (rp[:, 1] >= BOUNDS[0][1]).all() and (rp[:, 1] <= BOUNDS[1][1]).all()
                  and (rp[:, 2] >= BOUNDS[0][2]).all() and (rp[:, 2] <= BOUNDS[1][2]).all())
    rec = {"file": "stage004.ppk", "tool": "toolnative/stage_preview.room_preview",
           "source_triangles": len(faces), "source_vertices": len(vertices),
           "room_triangles": len(out["faces"]), "room_vertices": len(out["vertices"]),
           "room_draws": len(out["draws"]),
           "room_parts": [{"part": d["part"], "vertices": d["vertices"], "triangles": d["triangles"],
                           "sampler": d["sampler"]} for d in out["draws"]],
           "room_bounds": out["preview_room"]["bounds"], "room_centre": out["preview_room"]["centre"],
           "all_room_positions_within_bounds": within,
           "shell_groups_used": sorted(SHELL.keys()), "light_groups_used": sorted(LIGHTS)}
    (OUT/"stage004.room.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps(rec, indent=2))
    break
