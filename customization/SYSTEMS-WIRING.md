# Western Heart Creation Suite — Systems Wiring Map

---

## 2026-10-20 — Creation Suite Pass, Worker A: inventory, gap map, CAW conversion

Owner order 2026-10-20: unify the torn-down creation systems into one working
suite. This section is the data-layer inventory: every count below was counted
from disk in this repo on 2026-10-20 (no inherited numbers without a recount —
where a number comes from an older doc it is labeled as such).

### The converted-parts contract (new this pass)

`customization/parts-converted/CATALOG.json` — entries
`{id, name, source_game, slot, category, glb, origin_file, status}` (+ a
`texture` field on texture parts, whose `glb` is null). Slots are Tekken 7 slot
titles from `parts/tekken/tekken7-slot-catalog.json`. Built by
`customization/tools/convert_caw_parts.py` (resumable; per-file status in
`parts-converted/convert-log.jsonl`). Two sibling lanes build on this file.

### Per-source inventory + gap map

**WWF No Mercy (N64, AKI) — CONVERTED this pass**
- On disk: `customization/parts/no-mercy/` = 986 files: 303 `.obj` meshes each
  with a sibling `.vc` (one `R G B` line per OBJ vertex, OBJ vertex order) +
  379 PNGs (146 face textures in `faces/`, 233 body-skin textures in `skins/`)
  + `manifest.json`. Meshes by folder: body_parts 220, face 48, weapon 34,
  attire_parts 1. Teardown side: `teardown/wwf-no-mercy/` = 18,554 files
  (docs incl. the 21KB edit-a-superstar flow; SYSTEMS-WIRING previously cited
  702 indexed UI/texture files from that tree).
- Suite can apply today: all 303 meshes converted to GLB with COLOR_0 vertex
  colors + UVs preserved (`parts-converted/no-mercy/<category>/`), cataloged
  to T7 slots (body_parts→FULL_BODY, face→FACE, weapon→EXTRA,
  attire_parts→UPPER). The 379 PNGs are cataloged as texture parts
  (faces→FACE, skins→FULL_BODY) — in No Mercy these atlases are applied by UV,
  and the GLBs keep the source UVs, so the pairing is mechanical.
- Gap: the AKI native scale/anchor offsets in `manifest.json` (per-model
  `offset`/`scale` fields) are not yet applied at runtime — parts are in
  native units, unanchored. Per-part semantic labels are thin (most manifest
  labels are generic).

**WrestleMania XIX (GC, Yukes) — textures CONVERTED, meshes BLOCKED (evidence below)**
- On disk: `customization/parts/wmxix/` = 2,691 files: 1,200 `.ymg` meshes,
  1,470 `.tex` texture containers, 8 `.ycg` color palettes, 3 `.ymm`, 2 `.tga`,
  2 `.tpl`, 2 `.psd`, 1 `.tm2`, 1 `.tpg`, 1 `.txt`, + `PARTS-INDEX.jsonl`
  (2,690 rows). Meshes by category: upper_body 476, hair 153 (+3 non-ymg),
  faces 153 (+1), gears 140, lower_body 120, accessories 60, shoes 50,
  gloves 48. Of the 1,200 `.ymg`, 998 carry `YOBJ` magic and 202 are `DUMY`
  placeholders (the game's own empty-slot marker, per the DOL file-type
  table: DUMY = id −1, skip).
- Suite can apply today: textures. 1,044 of the 1,470 `.tex` embed standard
  GameCube TPL textures; decoded to PNG with the in-repo decoder
  (`teardown/wmxix/decode_tpl.py`, format code vendored into
  convert_caw_parts.py) → `parts-converted/wmxix-textures/`, cataloged as
  MAKE_UP texture parts. Verified by eye: decoded face textures are real
  faces (eyes/nose/mouth/ears). The other 426 `.tex` carry no embedded TPL
  (name-table-only containers, e.g. `TEX/64gara`) — logged
  `blocked_no_tpl`, not faked.
- Gap — `.ymg` mesh assembly is UNSOLVED with existing tooling:
  - The container parses (72-bone skeleton, materials, batch table) via
    `wrestlemania-xix-mod/teardown/wwe-wrestlemania-xix/tools/yobj_decode.py`
    and `yobj_vertex_decode.py`, but each CAW part's batch table holds only
    1–3 strip batches (9–70 verts). Rendered with my own eyes 2026-10-20:
    tangled ribbons/spikes in a shared ~16-unit space — fragments, not parts.
  - The 2026-10-15 "YOBJ-SKINNING-SOLUTION.md" (idx = bone index, bone-matrix
    transform) was DISPROVEN by the Lane-A re-test
    (`YOBJ-SKINNING-LANE-A-REPORT.md`, own-eyes renders: scattered garbage;
    11 hypotheses rejected).
  - The 2026-10-17 "WMXIX-ASSEMBLY-SOLUTION.md" (translation-only, /2500
    verts, material-name batch→bone map for wrestler 000_0) claims a working
    humanoid, but its artifacts (`work/wrestler-output/*.obj/.png`) are NOT
    in the repo — unverifiable, and its mapping is wrestler-file-specific
    (batch material names like `hhh_body` that CAW edit parts don't carry).
  - The DOL decoder report names the real unblock path: reverse the game's
    own YOBJ vertex loader in main.dol (file-type table at DOL 0x30B2B0),
    or a Dolphin GX vertex dump. Until then all 1,200 `.ymg` are cataloged
    `blocked_ymg_decode` (998) / `blocked_dumy_placeholder` (202). No fake
    GLBs were produced.

**WWE 2K (2K14–2K23) — docs only, unchanged**
- On disk: `customization/wwe2k-caw/` = 9 documents (CAW-SUITE-BREAKDOWN,
  PARTS-CATALOG, PULL-PLAN, structure/audit/transfer docs) +
  `teardown/wwe-2k/` = 4 catalog/spec docs. No `pac/edit` binaries on disk —
  the ~96GB transfer is still the blocker (structure-level integration only,
  per the 2026-10-19 audit). Nothing in the suite can apply 2K parts today.

**Tekken 7 — slot schema wired, item meshes absent**
- `customization/parts/tekken/` = 6 files: T7 + T6 + TTT2 slot catalogs,
  MANIFEST, README, PARTS-INDEX (26 entries — full-character FBX models,
  explicitly "not separable parts"). T7 `.uasset` item meshes were never
  pulled. The 16-slot T7 schema is the suite's slot system of record (all
  converted parts in this pass are mapped onto it).

**Tekken 6 (PSP) — item-table hunt: DONE, tables are NOT on disk as files**
- `teardown/tekken6/` = 69 files (8.6MB): TEARDOWN.md, DATA401-RE-NOTES.md,
  PPSSPP guide, `decrypted/EBOOT.DECRYPTED.ELF` (4.16MB), NDPP model docs +
  bounding-volume GLB, UI captures, 40 ending-frame JPGs, cipher tools.
  Grepped the whole tree + the decrypted EBOOT for item/equipment data:
  - NO item/equipment table files exist in the extracted set. The
    `sbcustomize_item_t` definition array (slot/price/model-ref per item)
    was never located by any lane.
  - What IS here: the EBOOT string table proves the system —
    `sbcustomize_item_t`, `tcb_CustomizePSP_Manager`,
    `CUSTOMIZEPACK%d_%d`, `HAIRCUSTOMIZEPACK%d`, `DEFAULTPACK%d` (verified
    by direct `strings` run 2026-10-20) — and
    `teardown/tekken6-customization-research.md` documents item NAME tables
    (record format `[u32 size][u8 item_idx][ASCII name]`, 10,495 records
    validated) found inside the 384MB decrypted bulk at
    `~/workspace/game-reverse-engineering/tekken6/work/decrypt3/` — that
    bulk and its scan output (`/tmp/item_tables.json`) are NOT in this repo
    and the /tmp output no longer exists. Slot categories confirmed from
    NTXL string tables there (`Hair - Back`, `Hair - Front (Right)`,
    `Face - Other`, …).
  - Next step (not this pass): re-run the name-table scan against the
    game-reverse-engineering bulk and commit the resulting table here; the
    definition array needs EBOOT data-segment analysis. T6 item models are
    NDPP inside the still-partly-encrypted archives — not extractable today.
  - The suite-side T6 mapping already exists: `tekken6-slot-catalog.json`
    (4 slots + `t7_slot_map`).

**Tekken 3 / TTT2 / Tekken 8 — schema/research only**
- Tekken 3: `teardown/tekken3/` = 19,436 files (incl. the recompiled
  outfit-slots doc indexed in CUSTOMIZATION-FILES-INDEX.json) — no separable
  customization parts in `customization/parts/`; T3 predates item
  customization (outfit = palette/2P variants).
- TTT2: `teardown/tekken-tag-tournament-2/` = 21 files + `ttt2-slot-catalog.json`;
  no item models on disk.
- Tekken 8: `teardown/tekken8/` = 3 files; no parts.

**CC0 / Quaternius hair — applies today**
- `customization/parts/hair/` = 49 files: 16 glTF hairstyles (8 styles ×
  CC0 + Quaternius copies, `.gltf`+`.bin`), 2 dread GLBs + 1 toon-dread GLB,
  11 texture PNGs, manifests + CC0 license. Already GLB/glTF — suite-ready,
  no conversion needed; mapped to HAIR slot in create-fighter's index
  (9 cc0-hair entries).

**Other parts on disk (counted, for completeness)**
- accessories: 13 files (8 rigged/unrigged chain GLBs + PNGs + manifest) —
  suite-ready GLBs. superhero: 6 files (4 GLBs: Batgirl mask/gauntlets,
  Space Ghost cowl, Spider-Girl eyes). Per-character eye sets: 25 PNGs
  (baek/doc-frank/jin/lili/pantera/zafina). kaykit-adventurers: 31 files
  (14 GLBs). masks: 1 GLB (Bannon mask) + README. dxmmii-patchwork: 44.
  mariposa-default 6 + mariposa-monarch 4. silvertongue-default: 14.
  defjam: index only (PARTS-INDEX.json, no meshes). doa: 3 docs only.
  base: README only. Total `customization/parts/` = 3,883 files.

**MPFB2 body morphs — wired as data, applied by Worker B's bake tool**
- `customization/body-morphs/` = MANIFEST.json + apply script: 13 macro body
  morphs + 12 face-shape morphs mapped suite-slider → MPFB target paths.
  MPFB2 checkout present at `~/workspace/cape-jones/production/tools/mpfb2`
  (with WIRING.md). Morphs are parameter data, not parts — nothing to
  convert; application happens per-fighter at bake time.

**GNM face — parameter data, same status**
- `customization/face-morphs/MANIFEST.json`: GNM semantic face params
  (gnm_basis: left_eye 100, right_eye 100, lower_face 150, tongue 32,
  iris 1) + presets. `customization/tools/gnm/` = 35 files (integration
  docs + license). Expression/face params, not mesh parts.

**Indexes (pre-existing, for reference)**
- `create-fighter/data/PARTS-INDEX.json`: 3,398 parts (wmxix 2,690,
  no-mercy 682, western-heart-library 17, cc0-hair 9).
- `PARTS-REGISTRY.json`: 1,148 curated part entries, 21 suite slots,
  7 character mappings, 13 libraries. `creation-suite-ui/data/parts-catalog.json`:
  34 curated parts (the UI's current catalog). The new
  `parts-converted/CATALOG.json` is the conversion-status layer on top of
  these, not a replacement.

### Conversion results (2026-10-20, this pass)

From `parts-converted/convert-log.jsonl` + `CATALOG.json` (3,372 entries):

- **No Mercy meshes: 303/303 converted, 0 failed** — body_parts 220, face 48,
  weapon 34, attire_parts 1 → `parts-converted/no-mercy/<category>/<part>.glb`.
  GLB structure verified by parsing a converted file: attributes COLOR_0
  (from the `.vc` files), POSITION, NORMAL, TEXCOORD_0 (source UVs kept).
  Plus 379 PNG face/skin texture parts cataloged (`texture_part`).
- **WMXIX textures: 1,044/1,470 converted, 426 `blocked_no_tpl`, 0 failed** →
  `parts-converted/wmxix-textures/**/*.png`, cataloged as MAKE_UP texture
  parts. Decode sample viewed by eye: real face textures.
- **WMXIX meshes: 0 converted — 998 `blocked_ymg_decode` + 202
  `blocked_dumy_placeholder`** (evidence in the WMXIX gap section above).
  8 `.ycg` cataloged `palette_only`; 12 leftover files (`.ymm`/`.tga`/`.tpl`/
  `.tm2`/`.tpg`/`.psd`/`.txt`) cataloged `not_converted`.
- Contact sheets (locked render method, docs/RENDER-ORIENTATION.md):
  `parts-converted/contact-sheet-nm.png` (12 No Mercy parts across
  categories) and `parts-converted/contact-sheet-wmxix-textures.png`
  (12 decoded textures). OWN-EYES VERDICTS (Worker A, 2026-10-20):
  - NM sheet: 11/12 tiles show coherent low-poly part geometry (curved body
    patches, face slabs, a weapon pole, the attire piece) carrying the ROM's
    per-vertex Gouraud shading colors as COLOR_0 (gradient look is the
    source data — extractor ground truth: AKI vertex records store r,g,b
    per vertex; in-game they multiply the part texture via the preserved
    UVs). The 12th, weapon/model_2CB3, is a planar 4-vertex quad
    (1290×10320, zero thickness) — invisible from the locked front camera
    because it is edge-on; the GLB itself is a faithful 4-vert/2-tri
    conversion, not a failure.
  - WMXIX texture sheet: all 12 sampled decodes are real textures (eye
    close-up, lips, brow, tattooed torso skin, plus grayscale intensity/
    alpha maps which are grayscale by format design). No garbage tiles.
  - Render note: tiles were rendered in Blender Workbench (vertex-color
    display) with the locked camera/framing/background rules; Cycles tiles
    could not complete under the machine's concurrent load (two attempts
    died to runtime restarts), so Workbench carried the verification.

---

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
