#!/usr/bin/env python3
"""Lane 4 — stage VMD geometry decode via roster-lib toolnative/vmd_mesh.read_mesh.
Extracts each stage PPK's single VMD entry (the key whose parse_vmd decoded)
and measures: groups, draws, vertex totals, position bounds, texture samplers.
No hand-written VMD parser: read_mesh IS the parser.
"""
import sys, json
from pathlib import Path
import numpy as np

RL = Path.home()/"workspace/urban-reign-redux/work/tools/vendor/roster-lib"
sys.path.insert(0, str(RL))
from toolnative.ppk_index import ppk_entries
from toolnative.vmd_structure import parse_vmd
from toolnative.vmd_mesh import read_mesh

IN = Path.home()/"workspace/urban-reign-redux/decoded/inputs"
OUT = Path.home()/"workspace/urban-reign-redux/decoded/stages"
OUT.mkdir(parents=True, exist_ok=True)

for ppk_path in sorted(IN.glob("stage*.ppk")):
    b = ppk_path.read_bytes()
    p = ppk_entries(b)
    # find the VMD entry: the one parse_vmd accepts
    vmd_entry = None
    for e in p["entries"]:
        data = b[e["offset"]:e["offset"]+e["size"]]
        try:
            parse_vmd(data)
            vmd_entry = (e, data)
            break
        except Exception:
            continue
    rec = {"file": ppk_path.name, "vmd_key": vmd_entry[0]["key"] if vmd_entry else None,
           "vmd_size": vmd_entry[0]["size"] if vmd_entry else None}
    if vmd_entry is None:
        rec["read_mesh"] = "NOT DECODED: no VMD entry found by parse_vmd"
    else:
        try:
            m = read_mesh(vmd_entry[1])
            groups = []
            for g in m["groups"]:
                groups.append({"index": g["index"], "weighted": bool(g["weighted"]),
                               "type": g["type"], "palette": g["palette"],
                               "chains": len(g["chains"])})
            total_verts = sum(len(d["vertices"]) for d in m["draws"])
            total_packets = sum(len(d["packets"]) for d in m["draws"])
            # bounds from influence-0 positions (influence positions are bone-local per PPK-GEOMETRY.md)
            pos = []
            for d in m["draws"]:
                for v in d["vertices"]:
                    if v["influences"]:
                        pos.append(v["influences"][0]["position"])
            pos = np.array(pos, dtype=float) if pos else np.zeros((0, 3))
            rec["read_mesh"] = "DECODED"
            rec["group_count"] = len(m["groups"])
            rec["draw_count"] = len(m["draws"])
            rec["total_vertices"] = int(total_verts)
            rec["total_packets"] = int(total_packets)
            rec["groups"] = groups
            rec["draws"] = [{"group": d["group"], "chain": d["chain"],
                             "vertices": len(d["vertices"]), "packets": len(d["packets"]),
                             "texture": d["texture"], "material_offset": d["material"]}
                            for d in m["draws"]]
            rec["skeleton_nodes"] = m["skeleton"]["node_slots"]
            rec["skeleton_active"] = m["skeleton"]["active_named_nodes"]
            if len(pos):
                rec["position_bounds_influence0"] = {
                    "min": [float(x) for x in pos.min(axis=0)],
                    "max": [float(x) for x in pos.max(axis=0)],
                    "extent": [float(x) for x in (pos.max(axis=0) - pos.min(axis=0))]}
            # node names full list
            rec["node_names"] = [n.get("name") for n in m["skeleton"]["nodes"] if not n.get("unused")]
        except Exception as ex:
            rec["read_mesh"] = f"NOT DECODED: {ex!r}"
    (OUT/(ppk_path.stem + ".vmd.json")).write_text(json.dumps(rec, indent=2))
    print(ppk_path.name, rec["vmd_key"], rec["read_mesh"],
          "verts:", rec.get("total_vertices"), "draws:", rec.get("draw_count"),
          "bounds:", rec.get("position_bounds_influence0", {}).get("extent"))
print("done")
