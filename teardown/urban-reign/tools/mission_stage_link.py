#!/usr/bin/env python3
"""Mission<->stage link test + place-name mapping (follow-on 4).
Inputs (all measured, no guessing):
 - /var/tmp/ur-census/missionNNN.posset.json (0.5 m grid position sets)
 - /var/tmp/ur-census/missionNNN.mesh.json (stage vmd_key per mission)
 - /var/tmp/ur-census/missionNNN.ppk.json (entry SHA256s -> stage VMD identity)
 - /var/tmp/ur-census/stageNNN.posset.json (6 stage PPK possets, from exporter)
 - /var/tmp/ur-census/mission_bin_fields.json (off00 area id per mission)
 - SLUS stage-name table (id, name) 0-54, proven from the (id,ptr) records
   at file 0x4ea3c0 in SLUS_212.09.
Outputs:
 - mission_stage_link.json: per-mission best stage-PPK match (overlap %),
   stage-VMD SHA cluster, off00 area id + place name.
 - place_ppk_map.json: place id -> {name, stage PPKs, missions, mission count}.
Overlap = |mission posset ∩ stage posset| / |mission posset| (Lane 4's measure).
"""
import json
from pathlib import Path
from collections import defaultdict, Counter

C = Path("/var/tmp/ur-census")
STAGE_TABLE = {
    0: "CHINA TOWN", 1: "RESTAURANT", 2: "SCRAPPED CAR", 3: "WAREHOUSE",
    4: "GLENN'S HIDEOUT", 5: "BAR", 6: "SOUTH END", 7: "SUBWAY",
    8: "SHOPPING CENTER 1", 9: "SHOPPING CENTER 2", 10: "BACK ALLEY",
    11: "HOMELESS", 12: "MEETING SPACE", 13: "CENTER CITY A",
    14: "SOUTH END(N)", 15: "SHOPPING CENTER(B)", 16: "APARTMENT",
    17: "CENTER CITY B", 18: "GREEN HILL", 19: "BOSS ROOF", 20: "PARKING",
    21: "LAST BOSS FLOOR", 22: "GROUND FLOOR", 23: "LAST BOSS AREA",
    24: "THEATER", 25: "RESTAURANT(D)", 26: "WAREHOUSE(VS)",
    27: "TAEKWONDO(VS)", 28: "VS BATTLE 4", 29: "VS BATTLE 5",
    30: "VS BATTLE 6", 31: "SCRAPPED CAR(VS)", 32: "SPEECH MEETING",
    33: "AURORA VISION", 34: "CITY HALL", 35: "KIDNAPPING", 36: "ARMY",
    37: "STAGE1(B)", 38: "STAGE2(B)", 39: "STAGE3(B)", 40: "STAGE4(B)",
    41: "STAGE5(B)", 42: "STAGE6(B)", 43: "STAGE7(B)", 44: "THROW AWAY",
    45: "STAGE 46", 46: "STAGE 47", 47: "STAGE 48", 48: "STAGE 49",
    49: "STAGE 50", 50: "STAGE 51", 51: "STAGE 52", 52: "STAGE 53",
    53: "STAGE 54", 54: "STAGE 55",
}
STAGE_PPK_VMD = {  # measured from the 7 stage PPK JSONs (entry SHA256)
    "stage003": ("fff0", "5b0ac7c7eccde4e8"),
    "stage004": ("1eb9", "1fe8193c869390af"),
    "stage028": ("d863", "9ee5c2835a717eb8"),
    "stage029": ("96cb", "40784af4020c9a18"),
    "stage030": ("718d", "ef1921004485dab3"),
    "stage031": ("3f25", "0981f5b91e96465b"),
    "stage020": ("bd01", "c6036a2cee286370"),  # geometry undecodable in-VM
}
SHA_TO_PPK = {v[1]: k for k, v in STAGE_PPK_VMD.items()}

fields = {r["mission"]: r for r in json.loads((C / "mission_bin_fields.json").read_text())["missions"]}

stage_possets = {}
for tag in ("stage003", "stage004", "stage028", "stage029", "stage030", "stage031"):
    p = C / f"{tag}.posset.json"
    if p.exists():
        d = json.loads(p.read_text())
        stage_possets[tag] = set(map(tuple, d["posset"]))

# stage VMD identity: cluster missions by stage VMD SHA256
def stage_vmd_sha(n):
    m = json.loads((C / f"mission{n:03d}.mesh.json").read_text())
    key = m.get("vmd_key")
    if not key:
        return None, None
    ppk = json.loads((C / f"mission{n:03d}.ppk.json").read_text())
    for e in ppk.get("entries", []):
        if e["key"] == key:
            return key, e.get("sha256")
    return key, None

rows, clusters = [], defaultdict(list)
for n in range(1, 101):
    m = json.loads((C / f"mission{n:03d}.mesh.json").read_text())
    p = json.loads((C / f"mission{n:03d}.posset.json").read_text())
    key, sha = stage_vmd_sha(n)
    if sha:
        clusters[sha].append(n)
    best, best_pct = None, 0.0
    if p.get("status") != "NO MESH" and "posset" in p:
        ps = set(map(tuple, p["posset"]))
        for stag, sps in stage_possets.items():
            if not ps:
                continue
            ov = len(ps & sps) / len(ps)
            if ov > best_pct:
                best, best_pct = stag, ov
    area = fields[n]["off00_area_id"]
    identity = SHA_TO_PPK.get((sha or "")[:16]) if sha else None
    rows.append({"mission": n, "area_id": area, "place": STAGE_TABLE.get(area),
                 "stage_ppk_identity": identity,
                 "stage_vmd_key": key, "stage_vmd_sha256": (sha or "")[:16],
                 "stage_mesh": m.get("meshes_load"), "posset_size": p.get("posset_size"),
                 "best_stage_ppk": best, "best_overlap_pct": round(best_pct * 100, 2)})

cluster_list = [{"sha256_prefix": sha[:16], "missions": ms, "count": len(ms)}
                for sha, ms in sorted(clusters.items(), key=lambda kv: -len(kv[1]))]
place_map = {}
for area in sorted(set(r["area_id"] for r in rows)):
    ms = [r["mission"] for r in rows if r["area_id"] == area]
    matched = Counter(r["best_stage_ppk"] for r in rows if r["area_id"] == area and r["best_stage_ppk"])
    place_map[area] = {"place": STAGE_TABLE.get(area), "missions": ms, "count": len(ms),
                       "stage_ppk_matches": dict(matched)}
(C / "mission_stage_link.json").write_text(json.dumps(
    {"missions": rows, "stage_vmd_clusters": cluster_list,
     "stage_vmd_cluster_count": len(cluster_list)}, indent=2))
(C / "place_ppk_map.json").write_text(json.dumps(place_map, indent=2))
print("missions:", len(rows))
print("stage-VMD SHA clusters:", len(cluster_list))
for c in cluster_list:
    print("  cluster", c["sha256_prefix"], "missions", c["missions"])
print("missions with a stage-PPK match >50%:", sum(1 for r in rows if r["best_overlap_pct"] > 50))
print("missions identified by byte-identical stage VMD:", sum(1 for r in rows if r["stage_ppk_identity"]))
for tag in STAGE_PPK_VMD:
    ms = [r["mission"] for r in rows if r["stage_ppk_identity"] == tag]
    areas = sorted(set(r["area_id"] for r in rows if r["stage_ppk_identity"] == tag))
    print(f"  {tag}: missions {ms} area_ids {areas} places {[STAGE_TABLE.get(a) for a in areas]}")
print("missions with NO stage mesh:", sum(1 for r in rows if r["stage_mesh"] != "DECODED"))
print("missions with best match but <10%:", sum(1 for r in rows if r["best_stage_ppk"] and r["best_overlap_pct"] < 10))
for area in sorted(place_map):
    pm = place_map[area]
    print(f"  area {area:2d} {pm['place']:20s} missions={pm['count']:2d} stage_matches={pm['stage_ppk_matches']}")
print("done")
