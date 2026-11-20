#!/usr/bin/env python3
"""Lane 4 — stage PPK decode driver. Uses ONLY Redux roster-lib tools:
toolnative/ppk_index.py (ppk_entries), toolnative/vmd_structure.py (parse_vmd),
toolnative/vmd_mesh.py (read_mesh), toolnative/stage_preview.py (room_preview).
No hand-written PPK parser: ppk_entries IS the parser. If it raises, that is
reported as NOT DECODED with the exact error — not worked around.
"""
import sys, json, hashlib, struct
from pathlib import Path

RL = Path.home()/"workspace/urban-reign-redux/work/tools/vendor/roster-lib"
sys.path.insert(0, str(RL))
from toolnative.ppk_index import ppk_entries
from toolnative.vmd_structure import parse_vmd
from toolnative.vmd_mesh import read_mesh

IN = Path.home()/"workspace/urban-reign-redux/decoded/inputs"
OUT = Path.home()/"workspace/urban-reign-redux/decoded/stages"
OUT.mkdir(parents=True, exist_ok=True)

def ascii_strings(b, minlen=4):
    out, cur = [], b""
    for ch in b:
        if 32 <= ch < 127:
            cur += bytes([ch])
        else:
            if len(cur) >= minlen: out.append(cur.decode())
            cur = b""
    if len(cur) >= minlen: out.append(cur.decode())
    return out

for ppk_path in sorted(IN.glob("stage*.ppk")):
    b = ppk_path.read_bytes()
    rec = {"file": ppk_path.name, "size": len(b),
           "sha256": hashlib.sha256(b).hexdigest(),
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
        entries = []
        for e in p["entries"]:
            data = b[e["offset"]:e["offset"]+e["size"]]
            er = dict(e)
            er["sha256"] = hashlib.sha256(data).hexdigest()
            er["header_hex"] = data[:32].hex()
            er["magic4"] = data[:4].decode("latin1", "replace")
            # VMD? roster-lib vmd_structure.parse_vmd is the tool for it
            try:
                v = parse_vmd(data)
                er["vmd_structure"] = "DECODED"
                er["vmd_nodes"] = v["node_slots"]
                er["vmd_active_nodes"] = v["active_named_nodes"]
                er["vmd_node_names"] = [n.get("name") for n in v["nodes"] if not n.get("unused")][:40]
            except Exception as ex:
                er["vmd_structure"] = f"NOT VMD / parse failed: {ex!r}"
            entries.append(er)
        rec["entries"] = entries
    except Exception as ex:
        rec["roster_lib_ppk_index"] = f"NOT DECODED: {ex!r}"
        # repo's own ppk_probe.py fallback observation only (header census, no decode claim)
        rec["ascii_strings_sample"] = ascii_strings(b)[:40]
    (OUT/(ppk_path.stem + ".json")).write_text(json.dumps(rec, indent=2))
    print(ppk_path.name, len(b), rec["roster_lib_ppk_index"], "entries:", rec.get("declared_entries"))
print("done")
