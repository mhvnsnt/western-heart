#!/usr/bin/env python3
"""Follow-on 1 — full 100-mission-PPK census (Lane 4 extension, same tools only).
Uses ONLY Redux roster-lib tools (toolnative/ppk_index.py, vmd_structure.py,
vmd_mesh.py) + the Editor's meshes.load (Source/editor/meshes.py) — the same
tools Lane 4 used. No hand-written PPK/VMD parser.
Per mission PPK (001-100):
  - ppk_index + per-entry parse_vmd (node slots, active named nodes, names)
  - stage-geometry VMD: meshes.load -> world verts/tris/bounds/textures
    (largest VMD entry by node count that is NOT a fighter skeleton is the
    stage shell; fighter VMDs are identified by the fighter-bone signature
    'KUBI'/'KOSHI' nodes AND a small node count; stage VMDs have no KUBI)
  - fighter VMDs: parse_vmd node census only (bone-name sample, node count)
  - position-set (quantized world positions, 0.5 m grid) for the stage VMD,
    for the mission<->stage link test
Outputs (small JSONs, no raw arrays): decoded/missions/census/missionNNN.ppk.json,
missionNNN.mesh.json, missionNNN.fighters.json, missionNNN.posset.json.
Usage: mission_census.py [start] [end]  (1-based mission numbers, inclusive)
Idempotent: skips a mission when all four outputs exist.
"""
import sys, os, json, hashlib, struct, time
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

INP = HOME / "workspace/urban-reign-redux/decoded/inputs"
MIS = HOME / "workspace/urban-reign-redux/decoded/inputs/mission_ppks"
OUT = HOME / "workspace/urban-reign-redux/decoded/missions/census"
OUT.mkdir(parents=True, exist_ok=True)
STAGES = HOME / "workspace/urban-reign-redux/decoded/stages"

FIGHTER_BONES = {"KUBI", "KOSHI", "MUNE", "KATA_L", "KATA_R", "HIZA_L", "HIZA_R"}


def ascii_strings(b, minlen=4):
    out, cur = [], b""
    for ch in b:
        if 32 <= ch < 127:
            cur += bytes([ch])
        else:
            if len(cur) >= minlen:
                out.append(cur.decode())
            cur = b""
    if len(cur) >= minlen:
        out.append(cur.decode())
    return out


def stage_posset():
    """Position sets of the 6 decoded stage PPKs (from their mesh JSONs)."""
    sets = {}
    for name in ("stage003", "stage004", "stage028", "stage029", "stage030", "stage031"):
        p = STAGES / f"{name}.mesh.json"
        if not p.exists():
            continue
        m = json.loads(p.read_text())
        # mesh.json has no positions; rebuild posset from the stage VMD via read_mesh
        sets[name] = None
    return sets


def main():
    start, end = int(sys.argv[1]) if len(sys.argv) > 1 else 1, int(sys.argv[2]) if len(sys.argv) > 2 else 100
    for n in range(start, end + 1):
        tag = f"mission{n:03d}"
        outs = {k: OUT / f"{tag}.{k}.json" for k in ("ppk", "mesh", "fighters", "posset")}
        if all(p.exists() for p in outs.values()):
            print(tag, "SKIP (done)", flush=True)
            continue
        ppk_path = MIS / f"{tag}.ppk"
        if not ppk_path.exists():
            ppk_path = INP / f"{tag}.ppk"
        b = ppk_path.read_bytes()
        t0 = time.time()
        rec = {"file": ppk_path.name, "size": len(b), "sha256": hashlib.sha256(b).hexdigest(),
               "magic": b[:4].decode("latin1"), "total_field": struct.unpack_from("<I", b, 4)[0],
               "data_offset_field": struct.unpack_from("<I", b, 8)[0],
               "tag_at_16": b[16:20].decode("latin1", "replace")}
        try:
            p = ppk_entries(b)
            rec["roster_lib_ppk_index"] = "DECODED"
            rec["payload_start"] = p["payload_start"]
            rec["fncc_size"] = p["fncc_size"]
            rec["declared_entries"] = p["declared_entries"]
            rec["lookup_groups"] = p["lookup_groups"]
        except Exception as ex:
            rec["roster_lib_ppk_index"] = f"NOT DECODED: {ex!r}"
            rec["ascii_strings_sample"] = ascii_strings(b)[:40]
            outs["ppk"].write_text(json.dumps(rec, indent=2))
            for k in ("mesh", "fighters", "posset"):
                outs[k].write_text(json.dumps({"file": ppk_path.name, "status": "NO PPK INDEX", "error": rec["roster_lib_ppk_index"]}, indent=2))
            print(tag, "NO PPK INDEX", flush=True)
            continue
        entries, vmds = [], []
        for e in p["entries"]:
            data = b[e["offset"]:e["offset"] + e["size"]]
            er = dict(e)
            er["sha256"] = hashlib.sha256(data).hexdigest()
            er["header_hex"] = data[:32].hex()
            er["magic4"] = data[:4].decode("latin1", "replace")
            try:
                v = parse_vmd(data)
                er["vmd_structure"] = "DECODED"
                er["vmd_nodes"] = v["node_slots"]
                er["vmd_active_nodes"] = v["active_named_nodes"]
                er["vmd_node_names"] = [nd.get("name") for nd in v["nodes"] if not nd.get("unused")][:40]
                vmds.append((e["key"], data, v))
            except Exception as ex:
                er["vmd_structure"] = f"NOT VMD / parse failed: {ex!r}"
            entries.append(er)
        rec["entries"] = entries
        outs["ppk"].write_text(json.dumps(rec, indent=2))
        # classify VMDs: fighter = has fighter-bone signature; stage = largest non-fighter VMD
        fighters, stage_cands = [], []
        for key, data, v in vmds:
            names = {nd.get("name") for nd in v["nodes"] if not nd.get("unused")}
            if names & FIGHTER_BONES:
                fighters.append((key, data, v))
            else:
                stage_cands.append((key, data, v))
        frec = {"file": ppk_path.name, "fighter_vmds": len(fighters), "stage_candidates": len(stage_cands),
                "fighters": []}
        for key, data, v in fighters:
            names = [nd.get("name") for nd in v["nodes"] if not nd.get("unused")]
            frec["fighters"].append({"vmd_key": key, "size": len(data), "nodes": v["node_slots"],
                                     "active_named_nodes": v["active_named_nodes"],
                                     "node_names": names[:40],
                                     "sha256": hashlib.sha256(data).hexdigest()})
        outs["fighters"].write_text(json.dumps(frec, indent=2))
        # stage geometry: largest non-fighter VMD by byte size
        mrec = {"file": ppk_path.name}
        posrec = {"file": ppk_path.name}
        if stage_cands:
            key, data, v = max(stage_cands, key=lambda t: len(t[1]))
            mrec["vmd_key"] = key
            mrec["vmd_nodes"] = v["node_slots"]
            mrec["vmd_active_nodes"] = v["active_named_nodes"]
            try:
                payload, textures, rig = meshes.load(data)
                P = payload["position"]
                import base64
                import numpy as np
                pos = np.frombuffer(base64.b64decode(P), dtype=np.float32).reshape(-1, 3)
                mrec["meshes_load"] = "DECODED"
                mrec["vertices_world"] = payload["vertices"]
                mrec["triangles"] = payload["triangles"]
                mrec["draws"] = len(payload["draws"])
                mrec["bounds_world"] = payload["bounds"]
                mrec["textures_decoded"] = len(payload["textures"])
                mrec["texture_errors"] = payload.get("texture_errors", {})
                mrec["compact_vif"] = bool(payload.get("compact_vif"))
                mrec["nodes"] = [dict(slot=nd.get("slot"), name=nd.get("name") or "", parent=nd.get("parent"),
                                      type=nd.get("type_byte")) for nd in payload.get("nodes", [])][:60]
                # position set, 0.5 m grid
                q = np.round(pos / 0.5).astype(np.int64)
                posrec["vmd_key"] = key
                posrec["positions"] = len(pos)
                posrec["posset_size"] = len(set(map(tuple, q.tolist())))
                posrec["posset"] = sorted(set(map(tuple, q.tolist())))
                posrec["bounds_world"] = payload["bounds"]
            except Exception as ex:
                mrec["meshes_load"] = f"NOT DECODED: {ex!r}"
                posrec["vmd_key"] = key
                posrec["status"] = "NO MESH"
                posrec["error"] = mrec["meshes_load"]
        else:
            mrec["meshes_load"] = "NO STAGE-CANDIDATE VMD"
            posrec["status"] = "NO STAGE-CANDIDATE VMD"
        outs["mesh"].write_text(json.dumps(mrec, indent=2))
        outs["posset"].write_text(json.dumps(posrec))
        print(tag, rec["roster_lib_ppk_index"], "entries", rec.get("declared_entries"),
              "fighters", len(fighters), "stage", mrec.get("vmd_key"), mrec.get("meshes_load"),
              f"{time.time() - t0:.0f}s", flush=True)
    print("done")


if __name__ == "__main__":
    main()
