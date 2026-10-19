# Western Heart Creation Suite — Systems Wiring Map

Owner order 2026-10-18: the Creation Suite sits ON TOP of the WWE and Tekken
customization systems, but is made proprietary to his universe. This doc maps
every system, what's wired, and what the pipeline path is for the rest.

## The flagship pipeline (what "inside the pipeline" means)

Customization is never a one-off script. Every change flows through:

```
PARTS-REGISTRY.json (customization/)          <- canonical part catalog
  eye-library/  MANIFEST.json                <- swappable eye variants
  decal-library/<char>/ MANIFEST.json         <- logos/decals w/ placements
  parts/<char>-eyes/                         <- per-character eye options
  parts/superhero/ + MANIFEST                 <- mesh attachments
  parts/tekken/ tekken7-slot-catalog.json    <- T7's 16-slot schema as JSON
packages/creation-suite/src/parts.js         <- runtime: loadRegistry, swapTexture, applyMeshPart
customization/create-fighter/                <- UI front end (tap-to-assign)
moveset-library/                             <- moveset editor (tap-to-assign)
```

## Tekken 7 — wired

- `customization/parts/tekken/tekken7-slot-catalog.json` (PR #254): T7's full
  customization DB schema as wireable JSON — 16 equipment slots, slot group IDs,
  21-field item CSV spec, asset prefixes (EI/ECI/ACI/CS/CCI/CI), slot conflict
  rules, color system, PlayerCus scope IDs, WH character IDs.
- T7 item 3D models (.uasset): NOT yet pulled — schema is wired, meshes pending
  the T7 pull. When they land, they arrive as a named DLC drop per
  CUSTOMIZATION-LIBRARY-LAYOUT.md.

## Tekken 6 (PSP) — teardown present, wiring in progress

- `teardown/tekken6/`: TEARDOWN.md, PPSSPP live-run guide, decrypted bank,
  `models/` (NDPP format docs + bounding-volume GLB), `ui/` (PSP UI captures).
- T6's customization: outfit slots map onto the same 16-slot schema as T7
  (catalog JSON covers both; slot group IDs are T7-era but T6 items slot in).
- T6 PSP's extracted files (478 in the earlier pull) are unsearched for item
  data — next step is grepping them for the item/equipment tables.

## Tekken Tag Tournament 2 — schema via T7, models pending

- No TTT2 teardown on disk yet. TTT2's customization is the direct ancestor of
  T7's (same slot architecture, Combot precedent for full-body replacement).
- The tekken7-slot-catalog.json slot schema covers TTT2 items structurally;
  TTT2 item models are a future pull.

## WWE — deep docs, parts on disk, 2K19 pull pending

- No Mercy: `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`
  (21KB — the actual edit-a-superstar flow), 702 UI/texture files indexed.
- WMXIX: `teardown/wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md`, wmxix
  parts (3,479 indexed in PARTS-INDEX.json), no-mercy parts (993 indexed).
- `customization/wwe2k-caw/`: PULL-PLAN.md + CAW-SUITE-BREAKDOWN.md +
  PARTS-CATALOG.md (PR #254). 2K19/2K18 `pac/edit/` files NOT on disk —
  the 51GB pull goes straight to TeraBox, then extraction with real 2K tools.
- WWE is the EDITOR model (tap-to-assign, library browsing); Tekken is the
  FIGHTING model (inputs, playstyle). Wrestling moves are welcome in the
  library — all get rewired to Tekken inputs and Tekken playstyle.

## Body + face morphs

- **MPFB2** (MakeHuman-based, pulled to cape-jones, PR #128): body morphs —
  body shapes, proportions. Integration point: `packages/creation-suite/src/body.js`.
- **GNM face rig** (Google GNM, `customization/tools/gnm/`, WH-INTEGRATION.md):
  face morphs — eyes, nose, mouth, face shapes. Integration point:
  `packages/creation-suite/src/regions.js`.

## Interaction model (owner law)

- Parts/attires: TAP a slot → SCROLL the library → TAP the part to assign.
  No drag-and-drop anywhere. (create-fighter already works this way.)
- Movesets: same tap model — tap a move slot → scroll the move library →
  tap the move to assign. Research: `moveset-library/MOVESET-EDITOR-RESEARCH.md`
  (WWE 2K + MDickie), spec in `moveset-library/UI-DESIGN-SPEC.md`.

## Rated M — nothing watered down (owner 2026-10-18)

The game targets rated M. Nudity/partial nudity stays; Mortal Kombat-level
visceral (bone breaks, fatalities, x-ray attacks) comes once the base is down.
No model is ever held back for nudity — the clothing system is a
customization option, never a gate.

## NO-GATE LAW (owner 2026-10-18)

Nothing gates a model from making it into the game. Models wire in as-is;
missing textures/meshes/UVs get corrected and put on the character;
customization dresses them. Nothing watered down, nothing held back.
