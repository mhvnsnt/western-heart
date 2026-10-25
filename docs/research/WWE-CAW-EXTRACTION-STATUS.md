# WWE CAW extraction status — per game (2026-10-22)

What the creation suite's template/parts library is built ON, game by game.
The suite pulls the real parts library; it does not hand-tool templates.

## Consolidated library (what the suite reads)

`customization/parts/` — **3,398 parts**, `PARTS-INDEX.json`:

| Source game | Parts | Where |
|---|---|---|
| WWF No Mercy (N64, AKI) | 220 body meshes, 48 face/hair meshes, 146 face PNGs, 233 skin PNGs, 34 weapons | `customization/parts/no-mercy/` |
| WWE WrestleMania X8/XIX era — WMXIX (GC, Yukes) | 2,690 CAW edit_data files (1,470 tex + 1,200 YOBJ meshes) | `customization/parts/wmxix/` |
| CC0 universal hair | 9 styles | `customization/parts/` |
| Western Heart library | eyes, masks, decals | `customization/parts/` |

Template definitions: `customization/templates/*.json` (data-driven).

## Per-game extractability

### 1. WWF No Mercy — ✅ FULLY EXTRACTED
- **What:** the complete CAW part set — body parts, attire parts, face/hair
  meshes, face textures, skins, weapons.
- **How:** N64 ROM teardown (teardown/wwf-no-mercy/: models/, textures/,
  re-docs/ with the full Edit-a-Superstar menu sequence).
- **Creation data captured:** 14 male + 9 female body types, 8 skin tones,
  7M+3F head shapes, 98M+20F faces, hair + front-hair, 31 facial-hair
  styles, masks/accessories, hats, full attire tables — the exact option
  lists in `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`.
- **In the suite:** body-type names, skin tones, face pools, facial-hair and
  mask options are the No Mercy lists verbatim.

### 2. WWE WrestleMania XIX (GameCube, Yukes) — ✅ SUBSTANTIALLY EXTRACTED
- **What:** 2,690 CAW `edit_data` files cataloged
  (`teardown/wmxix/caw-parts/CATALOG.md`): 1,470 textures, 1,200 YOBJ
  meshes (hair, gear, accessories), 8 YCG palettes.
- **How:** streamed from ISO 2026-10-13; YOBJ decode via
  `teardown/wmxix/extract_wrestlers.py`, wrestler-000 fully solved
  (`teardown/wwe-wrestlemania-xix/wrestler-000-solved.obj`).
- **In the suite:** the 1,200-mesh hair/gear/accessory library
  (`customization/parts/wmxix/`), the ATTIRE grid's bulk categories.
- **Open:** 1,478 raw textures still need slot sorting (tracked in
  customization/CHARACTER-CREATION.md §9).

### 3. WWE WrestleMania XIX — wrestler models — 🟡 PARTIAL
- YOBJ/YANM formats documented (`teardown/wwe-wrestlemania-xix/*.md`),
  assembly solution + axis permutation solved, wrestler-000 posed and
  verified. Remaining wrestlers decode with the same scripts — not yet
  batch-run. Not blocking: CAW parts (the creation library) are done.

### 4. Def Jam: Fight for NY (PS2, EA Chicago) — 🟡 PARTIAL
- **What:** ISO pulled via surgical HTTP Range extraction (~450MB, not the
  full 4.7GB); models, motion data (`WRES_ALL.VIV`), and the XML data model
  extracted. EAGL/BIGF container tools in
  `teardown/def-jam-fight-for-ny/tools/` (bigf_extract.py,
  eabig_extract.py, iso_tree.py).
- **Blocked:** mesh decode (SHPS chunk format) is open RE work —
  `EAGL-FORMAT-SPEC.md` documents what's known. No CAW-style part library
  yet; Def Jam contributes **fight-system** findings (grappling core,
  styles), not creation parts, until SHPS decodes.
- **Verdict:** not stalled on — documented, moving on.

### 5. WWE 2K15–2K23 (PC) — 🔴 NOT ACQUIRED
- **Blocked on acquisition, not tooling.** Each game is 33–84GB compressed
  (~412GB for the priority set); the VM cannot hold them
  (`teardown/wwe-2k/WWE2K15-23-ACQUISITION.md`, 2026-10-14). The path is
  the TeraBox browser lane (parent delegation — subagents can't run it).
- Moves/entrance animation data for 2K15–2K20 is already secured
  (wwe2k19-animation-packs-v1 release); the full game is needed for
  MODELS, CAW parts, and arenas.
- **What the suite does meanwhile:** `customization/wwe2k-caw/` holds the
  CAW structure research (CAW-STRUCTURE-2026-10-19.md,
  COMBINED-CREATION-SUITE.md, PARTS-CATALOG.md) so the 2K part taxonomy
  slots straight into `customization/parts/` the day the files land.
- **Verdict:** documented as blocked, not stalling the directive.

## Bottom line

The suite's template system and parts library are built on **fully
extracted No Mercy + WMXIX CAW data** (3,398 parts, real option lists,
real menu sequences). WrestleMania XIX wrestler meshes and Def Jam meshes
are partial (format work ongoing, not blocking). WWE 2K proper is
acquisition-blocked and documented as such.
