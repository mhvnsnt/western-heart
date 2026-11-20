# Creation-suite parts status — 2026-11-02

Audited 2026-11-02 against what is actually wired in the suite (not the
older brief figures). Two inventories, not two views of one set — do not
add them together.

## Corrected inventory figures (supersede the old 4,523 / 7,920 brief)

- Suite catalog `customization/creation-suite-ui/data/parts-catalog.json`:
  **7,424 entries** (was 7,419; +5 AshLane hair wired by this PR).
  Header `counts` sum = header `total` = parts array length = 7,424.
- Create-fighter index `customization/create-fighter/data/PARTS-INDEX.json`:
  **7,960 entries** (header `total_parts`), 0 duplicate ids in either file.
- The suite UI loads the catalog only, NOT the index. The create-fighter UI
  loads the index. A part in one file is not automatically offered by the
  other UI.

## What this PR wires (real geometry only)

- 5 AshLane hair GLBs into the suite catalog, head socket, offset 0,
  scale 1, `geometry_pending: false`, editable position/rotation/scale —
  the same shape as the existing `hair-toon-dread-ponytail` entry, and the
  attach spec in `customization/parts/ashlane/hair/manifest.json`
  (attachBone Head, offset 0, scale 1.0) for all 5:
  - `ashlane-hair-echo-long-green` (179,964 bytes)
  - `ashlane-hair-hollow-long-black` (179,984 bytes)
  - `ashlane-hair-static-blond-beard` (218,480 bytes)
  - `ashlane-hair-theory-locs-beads` (1,309,136 bytes)
  - `ashlane-hair-theory-locs-pinned` (67,768 bytes)
- All 5 files verified present on main by exact size before wiring.
  Per-template fit tuning (AshLane cast scale/orientation notes in
  `customization/parts/ashlane/hair/FIT_NOTES.md`) is a follow-up, not a
  blocker to listing: the suite lets the player move/rotate/scale the part.
- Stale header comment fixed in `customization/create-fighter/js/catalog.js`
  ("3,372-part teardown index" → the 7,960-part index; the old "every part
  carries geometryPending:true" claim was already false in code).
  The archival copy `customization/create-fighter/reference/ref-catalog.js`
  is left untouched on purpose.

## Hair — catalog (suite UI)

- 332 entries: 312 pending (94.0%), 20 wired/not-pending (6.0%),
  17 with a `glb` (5.1%).
- Before this PR: 327 entries, 15 not-pending, 12 with a `glb`.
  The 312 pending are all `wmxix` name-only entries (no `glb`/`asset`).
- Index hair, for cross-check: 170 entries, 14 ready by the create-fighter
  rule (8.2%): 9 CC0 + 5 AshLane. The 5 AshLane hairstyles were index-only
  before this PR; now the suite UI offers them too.

## Clothing — catalog

- 2,345 total, 1,603 pending (68.4%), 742 wired/not-pending (31.6%),
  755 with a `glb` (32.2%).
- Excluding DOA4 fullbody: 2,073 total, 1,603 pending (77.3%),
  470 wired (22.7%).
- The wired figure is carried by `attire` (mostly textures) and DOA4
  fullbody (272/272 real GLBs). Upper body is 1,174/1,175 pending (99.9%);
  lower body 330/330 pending (100%); shoes 50/50 pending (100%);
  gloves 48/48 pending (100%).

## Accessories — catalog

- 2,891 total, 2,856 pending (98.8%), 35 wired (1.2%),
  976 with a `glb` (33.8%) — the 976 are almost entirely pending
  Def Jam POINTS-topology conversions, not usable meshes.

## Tattoos, scars, eyes

- Tattoos: **0 entries in either file** — an absent category, not a
  pending one. Must be created (or explicitly cut).
- Scars: **0 true entries** (only substring hit is a scarf, not a scar).
- Eyes (`eye`, `eyebrows`, `eye_lenses`): 16 total, 6 pending (37.5%),
  10 wired (62.5%), but only **3 with a real mesh (18.8%)** — the rest are
  PNG textures or pending rows with no file at all.

## Still owed (counts with percentages)

- Def Jam mesh conversion pass: 2,624 catalog entries, 100% pending
  (35.4% of the catalog). POINTS topology until the conversion lands.
- Hair conversion: 312/327 pending (95.4%) before this PR; 312/332 (94.0%)
  after it. The 312 are `wmxix` name-only entries.
- Clothing conversion: 1,603/2,345 pending (68.4%).
- Accessories conversion: 2,856/2,891 pending (98.8%).
- Tattoos: 0 — creation (or an explicit cut decision) owed.
- Scars: 0 — creation (or an explicit cut decision) owed.
- Eyes: 6 pending rows with no file + only 3 real meshes of 16.
- Facial hair standalone: 0 entries in either file. Glasses/eyewear:
  0 parts. Hair-accessory, effects, aura, and head slots: 0 parts each
  behind their UI labels (the 7 `head`-slot Def Jam entries land under
  "Slot?" — no `t7_slot`/SLOT2CAT entry).
- `customization/templates/face-parts.json`: 0/18 `part_ref` values match
  any catalog `id` or index `part_id` by exact string (old id format).
  Re-pointing needs verification, not guessed mappings.
- In-game vs suite wiring was NOT cross-checked entry-by-entry:
  `game/js/customization-consumer.js` merges `PARTS-REGISTRY.json` plus
  per-game catalogs, not either file audited here.
- ORDER-doc row updates for this step are deferred until Phase 4b
  (PR #1498) merges, to avoid an ORDER-doc conflict; this doc is the
  record until then.

## What is NOT claimed here

- No 100% claim for pending geometry. Pending means pending.
- No Def Jam conversion attempted in this PR (Blender conversion pass).
- No face-parts id mappings guessed.
- No in-fight wiring claimed for these 5 hairstyles beyond the suite
  catalog listing (suite attach path uses `glb` + `socket`, the same as
  the existing wired hair entries).
