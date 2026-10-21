#!/usr/bin/env python3
"""build_no_mercy_catalog.py — generate the No Mercy CAW parts catalog.

Reads customization/parts/PARTS-INDEX.json (the source of truth for the
extracted part set) and emits customization/parts/no-mercy/CATALOG.json:
every WWF No Mercy part in PARTS-REGISTRY-entry shape (id, name, library,
slot, suite_slot, kind, part_class, file, format, conversion status), so
the Creation Suite runtime can enumerate No Mercy parts alongside the
registry (see packages/creation-suite/src/catalogs.js).

Deterministic: entries sorted by id; re-running reproduces the file
byte-for-byte except the _meta.generated date. The OBJ->GLB converter
(customization/tools/convert_no_mercy_parts.py) stamps conversion status
into the catalog after a conversion run; this generator resets it to
"pending" — always run the converter after regenerating.

Suite-slot mapping (index slot -> suite_slot), from the registry's
suite_slots vocabulary (customization/PARTS-REGISTRY.json):
  bodies   -> by label keyword: Chest/Back/Waist/Arm/Hand/Shoulder/Neck
              => upper_body; Pelvis/Leg/Foot/Thigh/Knee => lower_body;
              no keyword => null (kept under source slot, never guessed)
  faces    -> face            (OBJ = face_mesh, PNG = face_texture)
  skins    -> null            (full-body skin textures; bake-lane domain)
  accessories (weapon/) -> accessory
  attire   -> attire
part_class follows the runtime's two classes (parts.js PART_CLASSES):
  .obj => mesh_part, .png => texture_part.
"""
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INDEX_PATH = os.path.join(REPO_ROOT, "customization", "parts", "PARTS-INDEX.json")
OUT_PATH = os.path.join(REPO_ROOT, "customization", "parts", "no-mercy", "CATALOG.json")
GLB_DIR_REL = "customization/parts/no-mercy/glb"

UPPER_KEYWORDS = ("chest", "back", "waist", "arm", "hand", "finger", "shoulder", "neck", "torso")
LOWER_KEYWORDS = ("pelvis", "leg", "foot", "thigh", "knee", "hip", "ankle")

MESH_EDITABLE = ["tint", "roughness", "metalness", "offset", "rotation", "scale", "visible"]
TEXTURE_EDITABLE = ["tint", "opacity", "visible"]


def suite_slot_for(part):
    slot = part.get("slot")
    label = (part.get("label") or "").lower()
    ext = os.path.splitext(part.get("file_path", ""))[1].lower()
    if slot == "bodies":
        if any(k in label for k in LOWER_KEYWORDS):
            return "lower_body"
        if any(k in label for k in UPPER_KEYWORDS):
            return "upper_body"
        return None
    if slot == "faces":
        return "face"
    if slot == "skins":
        return None
    if slot == "accessories":
        return "accessory"
    if slot == "attire":
        return "attire"
    return None


def kind_for(part):
    slot = part.get("slot")
    ext = os.path.splitext(part.get("file_path", ""))[1].lower()
    if slot == "bodies":
        return "body_mesh"
    if slot == "faces":
        return "face_mesh" if ext == ".obj" else "face_texture"
    if slot == "skins":
        return "skin_texture"
    if slot == "accessories":
        return "weapon_mesh"
    if slot == "attire":
        return "attire_mesh"
    return "unknown"


def glb_rel_path(file_path):
    # customization/parts/no-mercy/<sub>/model_X.obj -> glb/<sub>/model_X.glb
    rel = os.path.relpath(file_path, "customization/parts/no-mercy")
    return os.path.join(GLB_DIR_REL, os.path.splitext(rel)[0] + ".glb").replace(os.sep, "/")


def main():
    idx = json.load(open(INDEX_PATH))
    parts = [p for p in idx["parts"] if p.get("source_game") == "no-mercy"]
    out = []
    for p in sorted(parts, key=lambda x: x["part_id"]):
        ext = os.path.splitext(p["file_path"])[1].lower()
        entry = {
            "id": p["part_id"],
            "name": p.get("label") or p.get("name"),
            "library": "no-mercy",
            "source_game": "no-mercy",
            "slot": p.get("slot"),
            "suite_slot": suite_slot_for(p),
            "kind": kind_for(p),
            "part_class": "mesh_part" if ext == ".obj" else "texture_part",
            "file": p["file_path"],
            "format": ext.lstrip("."),
            "editable": list(MESH_EDITABLE if ext == ".obj" else TEXTURE_EDITABLE),
        }
        if p.get("nverts") is not None:
            entry["nverts"] = p["nverts"]
        if p.get("nfaces") is not None:
            entry["nfaces"] = p["nfaces"]
        if ext == ".obj":
            entry["glb"] = glb_rel_path(p["file_path"])
            entry["conversion"] = {
                "status": "pending",
                "tool": "customization/tools/convert_no_mercy_parts.py",
                "source_format": "obj (AKI export, no normals, header scale in file)",
            }
        else:
            entry["conversion"] = {"status": "not_required", "note": "PNG is web-native."}
        out.append(entry)

    catalog = {
        "_meta": {
            "catalog": "WWF No Mercy CAW parts — Creation Suite catalog (registry-entry shape)",
            "generated_by": "customization/tools/build_no_mercy_catalog.py",
            "generated_from": "customization/parts/PARTS-INDEX.json (source_game == 'no-mercy')",
            "total": len(out),
            "by_slot": dict(Counter(e["slot"] for e in out)),
            "by_part_class": dict(Counter(e["part_class"] for e in out)),
            "by_suite_slot": dict(Counter(str(e["suite_slot"]) for e in out)),
            "suite_slot_mapping": "bodies: label keyword -> upper_body/lower_body (none => null); faces -> face; skins -> null (full-body textures); accessories -> accessory; attire -> attire",
            "consumer": "packages/creation-suite/src/catalogs.js",
            "note": "The 35 No Mercy entries already inside PARTS-REGISTRY.json point at these same files; catalogs.js dedupes by file path (registry wins, it carries bone/editable metadata).",
        },
        "parts": out,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(catalog, f, indent=1, sort_keys=False)
        f.write("\n")
    print(f"wrote {OUT_PATH}: {len(out)} entries")
    print("by_part_class:", catalog["_meta"]["by_part_class"])
    print("by_suite_slot:", catalog["_meta"]["by_suite_slot"])


if __name__ == "__main__":
    sys.exit(main())
