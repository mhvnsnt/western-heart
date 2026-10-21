#!/usr/bin/env python3
"""build_suite_catalog.py — regenerate customization/creation-suite-ui/data/parts-catalog.json
as ONE unified catalog for the Creation Suite PARTS/ATTIRE tabs.

Sources (all repo-relative, verified at build time):
  1. customization/PARTS-REGISTRY.json          — the spine (1,148 parts at last build)
  2. customization/parts-converted/CATALOG.json — OPTIONAL (Worker A converter);
     absent on main as of 2026-10-20, handled as count 0 and noted in the output.
  3. customization/parts/hair/** GLBs           — hair meshes not already in the registry
  4. customization/eye-library/               — eye textures (via its MANIFEST.json + PNGs)

Output entry shape (superset of the old curated 34-entry catalog, so the
existing suite.js consumers keep working):
  { id, name, part_class, suite_slot, t7_slot, library, source,
    glb (mesh GLB path or null), asset (any asset path or null),
    socket, offset, rotation, scale, modeled_in_place_for,
    geometry_pending (bool), kind, placement, editable }

T7 slot mapping mirrors UNIFIED-UI-SPEC.md §7 (T7 numeric spine):
suite_slot -> t7_slot. Texture parts keep the packages/creation-suite
parts.js swap semantics: their `placement` block (texture/material/mode/
pixel_rect) is carried through untouched.

Run from anywhere:  python3 customization/build_suite_catalog.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "customization" / "PARTS-REGISTRY.json"
CONVERTED = ROOT / "customization" / "parts-converted" / "CATALOG.json"
HAIR_DIR = ROOT / "customization" / "parts" / "hair"
EYE_DIR = ROOT / "customization" / "eye-library"
OUT = ROOT / "customization" / "creation-suite-ui" / "data" / "parts-catalog.json"

# UNIFIED-UI-SPEC §7 spine: registry suite_slot -> T7 slot id
T7_SLOT = {
    "eye": "EYES", "eye_lenses": "6", "mask": "3", "cowl": "3", "face": "8",
    "hair": "2", "upper_body": "9", "top": "9", "outfit": "9", "attire": "10",
    "lower_body": "11", "tights": "11", "pants": "11", "gloves": "H",
    "gauntlets": "H", "shoes": "F", "gear": "12", "accessory": "12",
    "scarf": "12", "decal_logo": "8",
}
# registry has no part_class for most wmxix/no-mercy rows: infer from asset.
MESH_EXTS = {".glb", ".gltf"}
TEX_EXTS = {".png", ".jpg", ".jpeg", ".dds", ".tga"}


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def norm_registry_part(p: dict) -> dict:
    asset = p.get("asset")
    placement = p.get("placement") or {}
    ext = Path(asset).suffix.lower() if asset else ""
    part_class = p.get("part_class")
    if not part_class:
        part_class = "mesh_part" if ext in MESH_EXTS else "texture_part" if ext in TEX_EXTS else "texture_part"
    glb = None
    if part_class == "mesh_part" and ext in MESH_EXTS:
        glb = asset
    elif p.get("glb"):
        glb = p.get("glb")
    return {
        "id": p["id"],
        "name": p.get("name") or p["id"],
        "part_class": part_class,
        "suite_slot": p.get("suite_slot"),
        "t7_slot": T7_SLOT.get(p.get("suite_slot")),
        "library": p.get("library"),
        "source": "PARTS-REGISTRY.json",
        "glb": glb,
        "asset": asset,
        "socket": placement.get("socket") or p.get("socket"),
        "offset": placement.get("offset", [0, 0, 0]),
        "rotation": placement.get("rotation", [0, 0, 0]),
        "scale": placement.get("scale", 1.0),
        "modeled_in_place_for": placement.get("modeled_in_place_for"),
        "geometry_pending": bool(p.get("geometryPending")),
        "kind": p.get("kind"),
        "placement": placement or None,
        "editable": p.get("editable", []),
    }


def main() -> int:
    counts = {}
    parts = []
    seen = set()

    reg = json.loads(REGISTRY.read_text())
    reg_parts = reg.get("parts", [])
    for p in reg_parts:
        e = norm_registry_part(p)
        if e["id"] in seen:
            continue
        seen.add(e["id"])
        parts.append(e)
    counts["PARTS-REGISTRY.json"] = len(reg_parts)

    # OPTIONAL source: Worker A converter output (absent on main 2026-10-20).
    converted = []
    if CONVERTED.exists():
        try:
            data = json.loads(CONVERTED.read_text())
            converted = data.get("parts", data) if isinstance(data, dict) else data
        except Exception as exc:  # malformed optional source: note, don't die
            print(f"WARNING: parts-converted/CATALOG.json unreadable: {exc}")
            converted = []
    counts["parts-converted/CATALOG.json"] = len(converted)
    for p in converted:
        pid = p.get("id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        asset = p.get("asset") or p.get("glb")
        ext = Path(asset).suffix.lower() if asset else ""
        parts.append({
            "id": pid, "name": p.get("name") or pid,
            "part_class": p.get("part_class") or ("mesh_part" if ext in MESH_EXTS else "texture_part"),
            "suite_slot": p.get("suite_slot") or p.get("slot"),
            "t7_slot": p.get("t7_slot") or T7_SLOT.get(p.get("suite_slot") or p.get("slot")),
            "library": p.get("library") or "parts-converted",
            "source": "parts-converted/CATALOG.json",
            "glb": asset if ext in MESH_EXTS else p.get("glb"),
            "asset": asset,
            "socket": (p.get("placement") or {}).get("socket") or p.get("socket"),
            "offset": (p.get("placement") or {}).get("offset", [0, 0, 0]),
            "rotation": (p.get("placement") or {}).get("rotation", [0, 0, 0]),
            "scale": (p.get("placement") or {}).get("scale", 1.0),
            "modeled_in_place_for": (p.get("placement") or {}).get("modeled_in_place_for"),
            "geometry_pending": bool(p.get("geometryPending")),
            "kind": p.get("kind"),
            "placement": p.get("placement"),
            "editable": p.get("editable", []),
        })

    # Hair GLBs anywhere under customization/parts/hair (skip .gltf sidecars:
    # the viewer loads single-file GLBs; gltf+bin pairs are registry rows already).
    hair_added = 0
    if HAIR_DIR.is_dir():
        for glb in sorted(HAIR_DIR.rglob("*.glb")):
            rp = rel(glb)
            if any(e["glb"] == rp or e["asset"] == rp for e in parts):
                continue
            pid = "hair-" + glb.stem.lower().replace("_", "-").replace(" ", "-")
            if pid in seen:
                continue
            seen.add(pid)
            parts.append({
                "id": pid, "name": f"Hair — {glb.stem.replace('_', ' ')}",
                "part_class": "mesh_part", "suite_slot": "hair", "t7_slot": "2",
                "library": "parts/hair", "source": "parts/hair GLB scan",
                "glb": rp, "asset": rp, "socket": "head",
                "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
                "modeled_in_place_for": None, "geometry_pending": False,
                "kind": "hair", "placement": {"socket": "head", "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0},
                "editable": ["position", "rotation", "scale"],
            })
            hair_added += 1
    counts["parts/hair GLB scan (new)"] = hair_added

    # Eye library: every PNG in customization/eye-library not already registered.
    eye_added = 0
    if EYE_DIR.is_dir():
        for png in sorted(EYE_DIR.glob("*.png")):
            rp = rel(png)
            if any(e["asset"] == rp for e in parts):
                continue
            pid = "eye-" + png.stem.lower().replace("_", "-").replace(" ", "-").replace("eye-", "", 1)
            pid = "eye-" + png.stem.replace("eye-", "", 1).lower().replace("_", "-")
            if pid in seen:
                continue
            seen.add(pid)
            parts.append({
                "id": pid, "name": f"Eye — {png.stem.replace('-', ' ').replace('_', ' ')}",
                "part_class": "texture_part", "suite_slot": "eye", "t7_slot": "EYES",
                "library": "eye-library", "source": "eye-library scan",
                "glb": rp, "asset": rp, "socket": None,
                "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
                "modeled_in_place_for": None, "geometry_pending": False,
                "kind": "eye", "placement": None, "editable": ["position", "size", "opacity"],
            })
            eye_added += 1
    counts["eye-library scan (new)"] = eye_added

    parts.sort(key=lambda e: (e["t7_slot"] or "ZZ", e["suite_slot"] or "", e["name"].lower()))
    data = {
        "version": 2,
        "app": "wh-creation-suite",
        "source": "build_suite_catalog.py — unified: PARTS-REGISTRY.json + parts-converted/CATALOG.json (optional) + parts/hair GLBs + eye-library",
        "counts": counts,
        "total": len(parts),
        "notes": "parts-converted/CATALOG.json was absent on main at build time (count 0); re-run this builder if it lands. Texture parts carry the registry placement block for packages parts.js swap semantics.",
        "parts": parts,
    }
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"total={len(parts)} counts={counts} -> {rel(OUT)}")
    from collections import Counter
    print("by t7_slot:", dict(Counter(e["t7_slot"] for e in parts)))
    print("by source:", dict(Counter(e["source"] for e in parts)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
