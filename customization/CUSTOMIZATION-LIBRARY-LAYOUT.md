# Customization Library — Canonical Layout

Owner directive 2026-10-18: a whole library of pieces/parts/decals — eyes,
hairstyles, clothes, accessories, character parts, clothing parts, FULL
CHARACTER TEMPLATES — that created characters can be built on top of.
WWE/Tekken-style swapping: every variant is saved, nothing is overwritten.

## Directory layout (under `customization/`)

```
customization/
├── eye-library/            # Universal eye options (done — owner's "I like" yellow tiger)
│   ├── eye-*.png
│   ├── MANIFEST.json       # entries + character_mappings (universal format)
│   └── README.md
├── decal-library/
│   └── <character>/        # e.g. pantera/ — logos, tights, pants + MANIFEST
├── parts/
│   ├── tekken/             # Tekken 7 slot schema + (later) item assets
│   ├── defjam/             # Def Jam CAW parts (raw + decoded)
│   ├── wwe2k/              # WWE 2K pac/edit parts (when pulled)
│   ├── wmxix/              # WMXIX CAW parts (3,479 files, indexed)
│   ├── no-mercy/           # No Mercy parts (993 files, indexed)
│   ├── superhero/          # Original superhero pieces (9)
│   ├── doa/                # DOA parts (4)
│   ├── base/               # Base body templates (2)
│   ├── hair/               # Hairstyle parts (CC0 pulls fold in here)
│   ├── attire/             # Attire/clothing parts
│   ├── accessories/        # Accessories (glasses, gloves, boots…)
│   ├── templates/          # FULL CHARACTER TEMPLATES for created characters
│   └── PARTS-INDEX.json    # master index (see below)
├── wwe2k-caw/              # WWE 2K research: CAW-SUITE-BREAKDOWN.md, PARTS-CATALOG.md, PULL-PLAN.md
├── create-fighter/         # Creation Suite web UI
├── tools/                  # extraction/RE tooling
└── CUSTOMIZATION-FILES-INDEX.json  # whole-tree file index (existing)
```

## Naming conventions

- Part files: `<category>-<descriptor>-<variant>.png|.glb` (e.g. `eye-yellow-tiger.png`)
- Libraries are per-domain (`eye-library/`, `decal-library/<character>/`); `parts/`
  is per-source-game for bulk extractions.
- Every library dir carries `MANIFEST.json` + `README.md`, no exceptions.

## MANIFEST entry format

```json
{
  "id": "eye-yellow-tiger",
  "name": "Yellow tiger eye (universal)",
  "type": "eye",
  "png": "eye-yellow-tiger.png",
  "size_px": [128, 128],
  "notes": "what it is, where it came from",
  "default_placement": "<placement key, for textures that composite into a rect>",
  "replaces_texture": "<texture name in target GLB>"
}
```

## The universal format (how parts drop onto ANY character)

Texture-swap parts (eyes, decals, face paint, tattoos) are universal by design:
the part is a standalone PNG; `character_mappings` in the MANIFEST says which
texture/material/rect it composites into per character. Add a mapping → the
part works on that character. No geometry changes, no new art.

Mesh parts (hair, clothes, accessories) attach at bone sockets with
position/rotation/scale offsets — Tekken's paradigm (already in PartPoser).
Each mesh part's MANIFEST entry names its default socket + offsets; the UI can
reposition or snap back, same as the decal library.

## Master indexes

- `customization/parts/PARTS-INDEX.json` — every indexed part: part_id, name,
  source_game, slot, file_path, size. Bulk extractions (wmxix, no-mercy) live here.
- `customization/CUSTOMIZATION-FILES-INDEX.json` — whole-tree file index.
- New libraries get their parts appended to PARTS-INDEX.json.
