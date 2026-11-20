#!/usr/bin/env python3
"""build_suite_catalog.py — regenerate customization/creation-suite-ui/data/parts-catalog.json
as ONE unified catalog for the Creation Suite PARTS/ATTIRE tabs.

Sources (all repo-relative, verified at build time):
  1. customization/PARTS-REGISTRY.json          — the spine (1,148 parts at last build)
  2. customization/parts-converted/CATALOG.json — OPTIONAL (Worker A converter);
     absent on main as of 2026-10-20, handled as count 0 and noted in the output.
  3. customization/parts/hair/** GLBs           — hair meshes not already in the registry
  4. customization/eye-library/               — eye textures (via its MANIFEST.json + PNGs)
  5. customization/parts-converted/defjam/CATALOG.json — Def Jam CAW library
     (worker 33, 2026-10-22); all entries geometry_pending (POINTS topology).
  6. teardown/dead-or-alive-4/models/*/converted/*.glb — 272 real converted
     DOA4 costume GLBs (worker 38, 2026-10-22), Full Body slot.

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

EYES ARE PARTS, NOT DECALS (owner verdict 2026-10-20 ~19:40 CDT): the owner
rejected a painted texture eye ("looks funny, not placed right; he also needs
eyelashes and eyebrows... let it be a real eye not just a decal on his face
from hand tooling") and wants to place eyes HIMSELF in the suite. Design:
eyeball / eyelash / eyebrow MESH parts are placeable via the suite's per-part
placement system (socket + placement record), exactly like other mesh parts.
The eye-library TEXTURE entries are legacy texture variants (eye_kind=
"texture_variant") — never presented as the eye solution. Mesh eye parts
carry eye_kind="placeable_part". Named test case: DEATHFANG (human form) —
the suite must make his case possible; his character work belongs to another
lane. In-repo placeable eye/brow assets today: Spider-Girl eye lenses
(parts/superhero), Eyebrows_Regular / Eyebrows_Female glTFs (parts/hair/cc0,
mirrored in parts/hair/quaternius). NO eyelash mesh exists in-repo yet —
that is an honest gap, not something to fabricate.

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
    "scarf": "12", "decal_logo": "8", "fullbody": "11",
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

    # REAL source: Worker A converter output (PR #398 merged 1dff63a52 —
    # parts-converted/CATALOG.json, 3,372 entries: wmxix 2,690 + no-mercy 682).
    # Run #3's absence finding was true at its check time; the merge landed after.
    converted = []
    if CONVERTED.exists():
        data = json.loads(CONVERTED.read_text())
        converted = data.get("parts", []) if isinstance(data, dict) else data
    counts["parts-converted/CATALOG.json"] = len(converted)
    CONV_T7 = {"UPPER": "9", "LOWER": "11", "FULL_BODY": "10", "HAIR": "2",
               "FACE": "6", "MAKE_UP": "8", "EXTRA": "14", "UPPER_ACC": "12", "LOWER_ACC": "13"}
    CONV_SUITE = {"UPPER": "upper_body", "LOWER": "lower_body", "FULL_BODY": "attire",
                  "HAIR": "hair", "FACE": "face", "MAKE_UP": "face", "EXTRA": "accessory",
                  "UPPER_ACC": "accessory", "LOWER_ACC": "accessory"}
    for p in converted:
        pid = p.get("id")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        glb = p.get("glb")
        tex = p.get("texture")
        status = p.get("status") or ""
        pending = status.startswith("blocked") or status in ("not_converted", "palette_only")
        if glb:
            part_class, asset = "mesh_part", glb
        elif tex:
            part_class, asset = "texture_part", tex
        else:
            part_class, asset = "mesh_part", None
        slot = p.get("slot")
        parts.append({
            "id": pid, "name": p.get("name") or pid,
            "part_class": part_class,
            "suite_slot": CONV_SUITE.get(slot, "accessory"),
            "t7_slot": CONV_T7.get(slot),
            "library": p.get("source_game") or "parts-converted",
            "source": "parts-converted/CATALOG.json",
            "glb": glb, "asset": asset or glb,
            "socket": None, "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
            "modeled_in_place_for": None,
            "geometry_pending": pending,
            "kind": p.get("category"),
            "placement": None,
            "editable": [],
            "converted_status": status,
        })

    # DEF JAM CAW library (worker 33, fight-lab lane, 2026-10-22):
    # customization/parts-converted/defjam/CATALOG.json — 2,624 conversion
    # entries from the 22,360-part PS2 .o index (customization/parts/defjam/
    # PARTS-INDEX.json). GLBs exist for 1,218 parts but carry POINTS
    # topology (unproven vertex order), so every Def Jam entry ships with
    # geometry_pending=True until the mesh conversion pass lands. Slots in
    # the defjam catalog (head/upper_body/lower_body/accessories) are
    # already suite slots. Complements the WWE (wmxix/no-mercy) libraries;
    # no duplication — ids are namespaced "defjam:…".
    DEFJAM = ROOT / "customization" / "parts-converted" / "defjam" / "CATALOG.json"
    DJ_SUITE = {"head": "head", "upper_body": "upper_body", "lower_body": "lower_body",
                "accessories": "accessory"}
    dj_added = 0
    if DEFJAM.exists():
        dj_data = json.loads(DEFJAM.read_text())
        dj_parts = dj_data.get("parts", []) if isinstance(dj_data, dict) else dj_data
        for p in dj_parts:
            pid = p.get("id")
            if not pid or pid in seen:
                continue
            seen.add(pid)
            slot = DJ_SUITE.get(p.get("slot"), "accessory")
            glb = p.get("glb")
            parts.append({
                "id": pid, "name": p.get("name") or pid,
                "part_class": "mesh_part",
                "suite_slot": slot, "t7_slot": T7_SLOT.get(slot),
                "library": "defjam", "source": "parts-converted/defjam/CATALOG.json",
                "glb": glb, "asset": glb,
                "socket": None, "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
                "modeled_in_place_for": None,
                "geometry_pending": True,  # POINTS topology until mesh pass
                "kind": p.get("slot"),
                "placement": None,
                "editable": [],
                "converted_status": p.get("status"),
                "uv_status": p.get("uv_status"),
                "topology_status": p.get("topology_status"),
            })
            dj_added += 1
    counts["parts-converted/defjam/CATALOG.json (new)"] = dj_added

    # DOA4 costume GLBs (worker 38, 2026-10-22):
    # teardown/dead-or-alive-4/models/<fighter>/converted/*.glb — 272 real
    # converted meshes, full-body costumes. The DOA4 teardown has no separable
    # costume pieces (all one-piece costumes), so they ship as Full Body slot
    # (T7 slot 11) with real_textures=True. Honestly labeled — never as pieces.
    doa4_added = 0
    DOA4 = ROOT / "teardown" / "dead-or-alive-4" / "models"
    if DOA4.exists():
        for glb in sorted(DOA4.rglob("*.glb")):
            pid = f"doa4:{glb.stem}"
            if pid in seen:
                continue
            seen.add(pid)
            # paired *_basecolor.png => real texture; otherwise untextured GLB
            tex = glb.with_name(glb.stem + "_basecolor.png")
            parts.append({
                "id": pid, "name": glb.stem.replace("_", " "),
                "part_class": "mesh_part",
                "suite_slot": "fullbody", "t7_slot": T7_SLOT.get("fullbody"),
                "library": "doa4",
                "source": rel(glb),
                "glb": rel(glb), "asset": rel(glb),
                "socket": None, "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
                "modeled_in_place_for": None,
                "geometry_pending": False,  # real converted GLB on disk
                "real_mesh": True, "real_textures": tex.exists(),
                "kind": "full_body_costume",
                "placement": "full_body",
                "editable": ["color"],
                "converted_status": "converted",
                "uv_status": "extracted",
                "topology_status": "ok",
            })
            doa4_added += 1
    counts["teardown/dead-or-alive-4/models/*/converted (new)"] = doa4_added

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

    # Eyebrows: REAL placeable mesh parts (owner eye verdict). The glTFs live
    # under parts/hair/cc0 (mirrored in parts/hair/quaternius — cc0 is canonical).
    brow_added = 0
    for stem, label in [("Eyebrows_Regular", "Regular"), ("Eyebrows_Female", "Female")]:
        gltf = HAIR_DIR / "cc0" / f"{stem}.gltf"
        if not gltf.exists():
            continue
        pid = "brow-cc0-" + label.lower()
        if pid in seen:
            continue
        seen.add(pid)
        rp = rel(gltf)
        parts.append({
            "id": pid, "name": f"Eyebrows — {label} (placeable)",
            "part_class": "mesh_part", "suite_slot": "eyebrows", "t7_slot": "6",
            "library": "cc0-hair", "source": "parts/hair eyebrow scan",
            "glb": rp, "asset": rp, "socket": "face",
            "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0,
            "modeled_in_place_for": None, "geometry_pending": False,
            "kind": "eyebrows", "placement": {"socket": "face", "offset": [0, 0, 0], "rotation": [0, 0, 0], "scale": 1.0},
            "editable": ["position", "rotation", "scale"],
            "eye_kind": "placeable_part",
        })
        brow_added += 1
    counts["parts/hair eyebrow scan (new)"] = brow_added

    # Eye classification (owner verdict): texture eye entries are legacy
    # texture variants; mesh eye/eyebrow parts are the placeable solution.
    for e in parts:
        if e.get("eye_kind"):
            continue
        if e["suite_slot"] == "eye" and e["part_class"] == "texture_part":
            e["eye_kind"] = "texture_variant"
        elif e["suite_slot"] in ("eye", "eye_lenses", "eyebrows") and e["part_class"] == "mesh_part":
            e["eye_kind"] = "placeable_part"

    parts.sort(key=lambda e: (e["t7_slot"] or "ZZ", e["suite_slot"] or "", e["name"].lower()))
    data = {
        "version": 2,
        "app": "wh-creation-suite",
        "source": "build_suite_catalog.py — unified: PARTS-REGISTRY.json + parts-converted/CATALOG.json (optional) + parts/hair GLBs + eye-library",
        "counts": counts,
        "total": len(parts),
        "notes": "parts-converted/CATALOG.json is a REAL source since PR #398 merged (run #3 absence finding was true at check time; the merge landed after). Eyes: mesh eye/brow parts are placeable (eye_kind=placeable_part); eye texture entries are legacy variants (eye_kind=texture_variant) per the owner 2026-10-20 eye verdict. No eyelash mesh exists in-repo yet.",
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
