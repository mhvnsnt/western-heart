#!/usr/bin/env python3
"""Lane 2 extraction step D: parse the extracted fighter files with the author's own
roster-lib tools (Source/vendor/roster-lib/toolnative/):
- VMD: vmd_structure.parse_vmd + vmd_mesh.read_mesh
- PPK: ppk_index.ppk_entries; members scanned for GYU banks (gyu_structure.parse_gyu
  + gyu_decode.codec_summary) and for the embedded model copy (review.py mouth_nodes
  logic: first-512-bytes search; mouth node type bytes 3=moving, 0=static).

Writes extracted/fighters/<Name>/parse.json per fighter with an extracted file.
"""
import hashlib, json, struct, sys
from pathlib import Path

ROOT = Path.home() / "workspace" / "urban-reign-redux"
FIGHTERS = ROOT / "extracted" / "fighters"
TOOLS = ROOT / "work" / "tools" / "vendor" / "roster-lib"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "toolnative"))

from toolnative.vmd_structure import parse_vmd
from toolnative.vmd_mesh import read_mesh
from toolnative.ppk_index import ppk_entries
from toolnative.gyu_structure import parse_gyu
from toolnative.gyu_decode import codec_summary

H = lambda b: hashlib.sha256(b).hexdigest()
MOUTH_NODES = ("AGO", "KUCHI_R", "KUCHI_L")


def parse_vmd_file(path):
    b = path.read_bytes()
    out = {"file": path.name, "bytes": len(b), "sha256": H(b), "head_hex": b[:32].hex()}
    try:
        v = parse_vmd(b)
        out["vmd"] = {"node_slots": v["node_slots"], "active_named_nodes": v["active_named_nodes"],
                      "node_table_offset": v["node_table_offset"],
                      "nodes": [{k: n[k] for k in ("slot", "name", "type_byte", "parent") if k in n}
                                for n in v["nodes"] if not n.get("unused")]}
    except Exception as e:
        out["vmd_error"] = repr(e)
    try:
        m = read_mesh(b)
        draws = m["draws"]
        out["mesh"] = {"groups": len(m["groups"]),
                       "draws": len(draws),
                       "vertices": sum(len(d["vertices"]) for d in draws),
                       "bones_used": sorted({i["bone"] for d in draws for v in d["vertices"] for i in v["influences"]}),
                       "textures": sorted({tuple(d["texture"]) for d in draws if d.get("texture")})}
    except Exception as e:
        out["mesh_error"] = repr(e)
    return out, b


def parse_ppk_file(path):
    b = path.read_bytes()
    out = {"file": path.name, "bytes": len(b), "sha256": H(b), "head_hex": b[:32].hex()}
    try:
        p = ppk_entries(b)
        out["ppk"] = {"declared_entries": p["declared_entries"], "lookup_groups": p["lookup_groups"],
                      "payload_start": p["payload_start"], "fncc_size": p["fncc_size"]}
        members = []
        for e in p["entries"]:
            mb = b[e["offset"]:e["offset"] + e["size"]]
            mi = {"key": e["key"], "kind": e["lookup_kind"], "size": e["size"],
                  "sha256": H(mb), "head_hex": mb[:16].hex(),
                  "inline_name": e.get("inline_name")}
            # GYU bank?
            try:
                g = parse_gyu(mb)
                mi["gyu"] = {"records": g["record_count"], "channels": g["channel_count"],
                             "frames": [r["frame_count"] for r in g["records"]],
                             **codec_summary(g)}
            except Exception as ex:
                mi["gyu_error"] = str(ex)[:120]
            # embedded VMD? (VMD node-table check: u16 at +10, table/end at +16)
            try:
                n = struct.unpack_from("<H", mb, 10)[0]
                table, end = struct.unpack_from("<II", mb, 16)
                if 0 < n <= 256 and 40 <= table and table + n * 64 <= end <= len(mb):
                    v = parse_vmd(mb)
                    mi["embedded_vmd"] = {"node_slots": v["node_slots"],
                                         "active_named_nodes": v["active_named_nodes"],
                                         "nodes": [n2["name"] for n2 in v["nodes"] if not n2.get("unused")][:40]}
            except Exception:
                pass
            members.append(mi)
        out["members"] = members
    except Exception as e:
        out["ppk_error"] = repr(e)
    return out, b


def mouth_check(vmd_bytes, ppk_bytes):
    """Author's review.py mouth_nodes, verbatim logic."""
    v = parse_vmd(bytes(vmd_bytes))
    t = v["node_table_offset"]
    at = ppk_bytes.find(vmd_bytes[:512])
    res = {"loose": {}, "package": {}, "embedded": at >= 0, "embedded_at": at}
    for n in v["nodes"]:
        nm = str(n.get("name", "")).split(" ")[-1]
        if n.get("unused") or nm not in MOUTH_NODES:
            continue
        p = t + n["slot"] * 64 + 63
        res["loose"][nm] = vmd_bytes[p]
        if at >= 0:
            res["package"][nm] = ppk_bytes[at + p]
    return res


def main():
    for fdir in sorted(FIGHTERS.iterdir()):
        if not fdir.is_dir():
            continue
        name = fdir.name
        res = {"fighter": name}
        vmd_bytes = ppk_bytes = None
        mp = fdir / "model.vmd"
        pp = fdir / "package.ppk"
        if mp.exists():
            res["model"], vmd_bytes = parse_vmd_file(mp)
            print(f"{name}: model VMD nodes={res['model'].get('vmd', {}).get('active_named_nodes')} "
                  f"mesh verts={res['model'].get('mesh', {}).get('vertices')} mesh_err={res['model'].get('mesh_error', '')[:80]}")
        if pp.exists():
            res["package"], ppk_bytes = parse_ppk_file(pp)
            pk = res["package"]
            print(f"{name}: package PPK entries={pk.get('ppk', {}).get('declared_entries')} "
                  f"groups={pk.get('ppk', {}).get('lookup_groups')} err={pk.get('ppk_error', '')[:80]}")
            for mi in pk.get("members", []):
                extra = ""
                if "gyu" in mi:
                    extra = f" GYU records={mi['gyu']['records']} frames={mi['gyu']['frames'][:6]} codecs={mi['gyu']['codecs']} decodable={mi['gyu']['fully_decodable']}"
                if "embedded_vmd" in mi:
                    extra += f" EMBEDDED_VMD nodes={mi['embedded_vmd']['active_named_nodes']}"
                print(f"    member key={mi['key']} kind={mi['kind']} size={mi['size']} head={mi['head_hex'][:16]}{extra}")
        if vmd_bytes is not None and ppk_bytes is not None:
            try:
                res["mouth"] = mouth_check(vmd_bytes, ppk_bytes)
                print(f"{name}: mouth loose={res['mouth']['loose']} package={res['mouth']['package']} embedded={res['mouth']['embedded']}")
            except Exception as e:
                res["mouth_error"] = repr(e)
                print(f"{name}: mouth check failed: {e!r}")
        (fdir / "parse.json").write_text(json.dumps(res, indent=1))
    print("DONE step D")


if __name__ == "__main__":
    main()
