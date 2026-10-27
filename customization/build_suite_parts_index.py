#!/usr/bin/env python3
"""build_suite_parts_index.py — rebuild the creation suite's parts library.

Worker 38 (2026-10-22): user directive "Parts incorporation: All WWE parts,
Def Jam parts (1,900), DOA parts — all incorporated into the creation suite's
parts library, not just sitting in teardowns."

Rebuilds create-fighter/data/PARTS-INDEX.json as ONE unified, browsable parts
library. Sources (repo-relative, verified at build time):

  1. create-fighter/data/PARTS-INDEX.json (existing 3,398 — kept verbatim,
     then upgraded: no-mercy meshes get geometryReady + real GLB paths)
  2. parts-converted/CATALOG.json (3,372 audited conversions — Worker A/36):
     - 303 no-mercy GLBs        -> geometryReady=true (real renderable mesh)
     - 1,477 wmxix decoded PNGs -> NEW texture parts (slot 'textures')
     - 379 no-mercy PNGs        -> already in the index; marked kind='texture'
  3. parts-converted/defjam/CATALOG.json (2,624 Def Jam FFNY CAW parts):
     1,201 converted to GLB, but the topology verdict is FAIL/BLOCKED
     (POINTS pools, vertex order unproven — sample-renders/V2CP_*_FAILED.png).
     All 2,624 enter the library as catalog entries with geometryPending=true
     and an honest note. The user's "1,900" = the V2CP_0..3.VIV CAW set;
     this catalog is its full 2,624-entry superset.
  4. teardown/def-jam-fight-for-ny/surgical/chars/v2ip_extracted/ (78 V2IP
     base models, PS2 .o — geometryPending, slot 'bodies')
  5. teardown/dead-or-alive-4/models/ (366 DOA4 GLBs: triangulated chrone /
     chrtwo / chrthree costumes + vertex-buffers + Bass Armstrong converted
     costumes — REAL geometry, geometryReady=true, slot 'attire')
  6. customization/parts/ashlane/ (owner's AshLane parts library: footwear,
     gloves, masks, hair, hoods, wristbands, rigged chains — REAL GLB
     geometry, geometryReady=true; attach specs in the slot manifests)

Honesty rules (owner law): nothing is marked renderable unless a real,
verifiable mesh file exists on disk. Def Jam parts stay GEOMETRY PENDING
until the topology decode lands. DOA4 has no separable costume pieces —
full costume models file under Full Body.

Run from anywhere:  python3 customization/build_suite_parts_index.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CUST = os.path.join(ROOT, "customization")
INDEX_PATH = os.path.join(CUST, "create-fighter", "data", "PARTS-INDEX.json")
CONVERTED = os.path.join(CUST, "parts-converted", "CATALOG.json")
DEFJAM_CAT = os.path.join(CUST, "parts-converted", "defjam", "CATALOG.json")
V2IP_DIR = os.path.join(ROOT, "teardown", "def-jam-fight-for-ny",
                        "surgical", "chars", "v2ip_extracted")
DOA_MODELS = os.path.join(ROOT, "teardown", "dead-or-alive-4", "models")
ASHLANE_DIR = os.path.join(CUST, "parts", "ashlane")

# AshLane part directory -> library slot (owner's customizer slot model:
# hair, facialHair, mask, hood, chain, gloves, wristbands, shoes)
ASHLANE_SLOT = {"footwear": "shoes", "gloves": "gloves",
                "masks": "masks", "hair": "hair", "hoods": "head",
                "wristbands": "accessories", "accessories": "accessories"}

# Def Jam CAW category codes -> library slot (from parts/defjam/PARTS-INDEX.json)
DEFJAM_SLOT = {"110": "head", "111": "upper_body",
               "112": "lower_body", "113": "accessories"}
NM_SLOT_FROM_CAT = {"body_parts": "bodies", "face": "faces",
                    "weapon": "accessories", "attire_parts": "attire"}


def load(p):
    with open(p) as f:
        return json.load(f)


def main():
    report = {"kept": 0, "nm_upgraded": 0, "nm_tex_marked": 0,
              "defjam_added": 0, "v2ip_added": 0, "doa_added": 0,
              "wmxix_tex_added": 0, "ashlane_added": 0, "missing": []}
    idx = load(INDEX_PATH)
    parts = idx["parts"]
    report["kept"] = len(parts)

    # --- 1. no-mercy upgrades: real GLB paths + texture markers ---
    conv = load(CONVERTED)
    glb_by_stem = {}   # (category, stem) -> repo-relative glb
    tex_by_file = {}   # origin_file -> texture path
    for e in conv["parts"]:
        if e.get("glb") and e.get("status") == "converted" \
                and e.get("source_game") == "no-mercy":
            stem = os.path.splitext(os.path.basename(e["glb"]))[0]
            cat = e.get("category") or ""
            glb_by_stem[(cat, stem)] = e["glb"]
        if e.get("texture"):
            tex_by_file[e.get("origin_file")] = e["texture"]

    nm_mesh_re = re.compile(r"^no-mercy:0x[0-9a-f]+:([^/]+)/(.+)\.obj$", re.I)
    for p in parts:
        m = nm_mesh_re.match(p.get("part_id", ""))
        if m:
            cat, stem = m.group(1), m.group(2)
            glb = glb_by_stem.get((cat, stem))
            if glb and os.path.exists(os.path.join(ROOT, glb)):
                p["geometryReady"] = True
                p["glb"] = glb
                report["nm_upgraded"] += 1
            else:
                report["missing"].append(p["part_id"])
        elif p.get("source_game") == "no-mercy" and p["part_id"].endswith(".png"):
            p["kind"] = "texture"
            report["nm_tex_marked"] += 1

    # --- 2. wmxix decoded textures: new texture parts ---
    seen_ids = {p["part_id"] for p in parts}
    wmxix_added = 0
    for e in conv["parts"]:
        if e.get("texture") and "wmxix-textures" in e["texture"]:
            pid = "wmxix-tex:" + os.path.basename(e["texture"])
            if pid in seen_ids:
                continue
            tex_path = e["texture"]
            if not os.path.exists(os.path.join(ROOT, tex_path)):
                report["missing"].append(pid)
                continue
            parts.append({
                "part_id": pid,
                "name": os.path.basename(tex_path),
                "source_game": "wmxix",
                "slot": "textures",
                "file_path": tex_path,
                "kind": "texture",
                "texture": tex_path,
                "origin": e.get("origin_file", ""),
                "size": os.path.getsize(os.path.join(ROOT, tex_path)),
            })
            seen_ids.add(pid)
            wmxix_added += 1
    report["wmxix_tex_added"] = wmxix_added

    # --- 3. Def Jam CAW parts (2,624) ---
    dj = load(DEFJAM_CAT)["parts"]
    for e in dj:
        pid = "defjam:" + e["id"]
        if pid in seen_ids:
            continue
        name = e.get("name") or e["id"]
        code_m = re.search(r"V2CP_(\d+)_", e["id"])
        slot = DEFJAM_SLOT.get(code_m.group(1), "defjam_unsorted") if code_m else "defjam_unsorted"
        entry = {
            "part_id": pid,
            "name": name,
            "source_game": "defjam",
            "slot": slot,
            "file_path": e.get("glb") or "",
            "size": 0,
            # Topology verdict: FAIL/BLOCKED (POINTS pools, vertex order
            # unproven). Never presented as renderable.
            "geometryPending": True,
            "note": "PS2 .o CAW part — mesh topology decode blocked "
                    "(see parts-converted/defjam/samples/SAMPLES.md verdict 3).",
        }
        if e.get("glb"):
            entry["glb"] = e["glb"]
        parts.append(entry)
        seen_ids.add(pid)
        report["defjam_added"] += 1

    # --- 4. Def Jam V2IP base models (78 local .o files) ---
    if os.path.isdir(V2IP_DIR):
        for fn in sorted(os.listdir(V2IP_DIR)):
            if not fn.endswith(".o"):
                continue
            pid = "defjam-v2ip:" + fn
            if pid in seen_ids:
                continue
            parts.append({
                "part_id": pid,
                "name": fn.replace(".o", ""),
                "source_game": "defjam",
                "slot": "bodies",
                "file_path": os.path.join("teardown/def-jam-fight-for-ny",
                                          "surgical/chars/v2ip_extracted", fn),
                "size": os.path.getsize(os.path.join(V2IP_DIR, fn)),
                "geometryPending": True,
                "note": "Def Jam base character model (PS2 .o) — "
                        "conversion for web rendering pending.",
            })
            seen_ids.add(pid)
            report["v2ip_added"] += 1

    # --- 5. DOA4 GLBs (real geometry) ---
    for dirpath, _dirnames, filenames in os.walk(DOA_MODELS):
        for fn in sorted(filenames):
            if not fn.endswith(".glb"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            pid = "doa4:" + fn
            if pid in seen_ids:
                continue
            label = fn.replace(".glb", "")
            parts.append({
                "part_id": pid,
                "name": label,
                "source_game": "doa4",
                "slot": "attire",
                "file_path": rel,
                "glb": rel,
                "geometryReady": True,
                "size": os.path.getsize(os.path.join(dirpath, fn)),
                "note": "DOA4 costume model (full-body) — real GLB geometry.",
            })
            seen_ids.add(pid)
            report["doa_added"] += 1

    # --- 6. AshLane owner parts (real GLB geometry) ---
    if os.path.isdir(ASHLANE_DIR):
        for dirpath, _dirnames, filenames in os.walk(ASHLANE_DIR):
            for fn in sorted(filenames):
                if not fn.endswith(".glb"):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
                pid = "ashlane:" + rel.replace(os.sep, "/")
                if pid in seen_ids:
                    continue
                slot_dir = os.path.basename(dirpath)
                slot = ASHLANE_SLOT.get(slot_dir, "accessories")
                parts.append({
                    "part_id": pid,
                    "name": fn,
                    "label": fn.replace(".glb", "").replace("_", " "),
                    "source_game": "ashlane",
                    "slot": slot,
                    "file_path": rel.replace(os.sep, "/"),
                    "glb": rel.replace(os.sep, "/"),
                    "geometryReady": True,
                    "size": os.path.getsize(os.path.join(dirpath, fn)),
                    "note": "Owner's AshLane parts library (mhvnsnt/AshLane-prototype) — "
                            "real GLB geometry. Attach specs in "
                            "customization/parts/ashlane/<slot>/manifest.json.",
                })
                seen_ids.add(pid)
                report["ashlane_added"] += 1

    idx["total_parts"] = len(parts)
    idx["sources"] = sorted({p.get("source_game", "?") for p in parts})
    with open(INDEX_PATH, "w") as f:
        json.dump(idx, f, indent=1)
        f.write("\n")
    print(json.dumps(report, indent=1))
    print("TOTAL:", len(parts))


if __name__ == "__main__":
    sys.exit(main())
