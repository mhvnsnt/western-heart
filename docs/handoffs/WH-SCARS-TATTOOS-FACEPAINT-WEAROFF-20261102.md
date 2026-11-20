# Scars + tattoos + face paint from WWE files, with wear-off — 2026-11-02

## Owner correction that drives this PR
Scars are NOT a create-or-cut binary. The owner said WWE game files
already have a bunch of scars, tattoos and face paints — get them from
there, study how the games make them, and how face paint disappears /
wears off, then make more the same way.

## What the data actually shows (checked, not assumed)
- **No file in western-heart is named "scar", "face paint" or "makeup"
  as a scar asset.** Tree search: `scar` hits are only "scarf"
  (butterfly scarf PNGs) and a fighter named Scarlett. Catalog search:
  zero scar / face_paint rows.
- **WMXIX Face_op (208 PNGs, already in the repo, already catalogued
  as face/textures with editable []):** alpha probe — 140 have >20%
  transparent pixels (overlay layers), 68 are opaque. Montage check:
  masks, face-paint patterns, facial marks and facial hair — e.g.
  ta0_012 (full mask), ta0_023 (blotch pattern). ta2_* (44) are all
  opaque full-face textures, not overlays.
- **WMXIX MAKE_UP / 64gara (ty2_*, 41 PNGs, already in the repo):**
  alpha probe — 39 overlay-like (>20% transparent). Montage check:
  these are LOGO / TATTOO decals (rose, dragon, banana, "POWER",
  W logo, devil face), not scars and not face paint.
- **WMXIX body overlays (already in the repo):** Upper_Body tu2/tu4
  59 overlay-like of 218 (tu0 147 are opaque base skins); Lower_Body
  73 overlay-like of 142 (tc2/tc4). Montage check: tattoo patterns,
  flames, chains, logos — body tattoos, not scars.
- **WWE 2K19 teardown (1,677 files, PRs #1480/#1481/#1483/#1485):**
  597 DDS textures, hash-named (HSPC 16-hex / SHDC 4-hex), no
  readable wrestler or part names, 0 catalog entries. No scar or
  face-paint set can be identified from 2K19 without CNPC mapping
  of the 607 edit/ch part files — listed as owed, not faked.
- **No Mercy:** 99 tattoos already wired in #1505 (catalog 7,424 →
  7,523); 146 NM face PNGs catalogued as face textures.
- **How the games make them, per the repo code:** a static layered
  texture on top of a base face/body texture. Western Heart today
  only does full_replace texture swaps
  (`packages/creation-suite/src/parts.js` applyPart — no opacity,
  no layered decal, no wear). The catalog's tattoo entries list
  "opacity" as editable, but no game code uses it. **There is no
  wear-off mechanism in any WWE data in the repo** — no fading,
  rub-off, sweat or damage-driven paint loss is documented in the
  teardown docs or code. Wear-off in this PR is therefore a NEW
  Western Heart system, and it is labeled as such in the code.

## What this PR wires (no new binary files, no raw commercial files)
- 179 WMXIX face overlay PNGs already in the repo, wired as
  `decal_logo` texture parts exactly like the #1505 tattoos:
  Face_op 140 + MAKE_UP 39. Catalog 7,523 → 7,702; decal_logo
  111 → 290. Their existing face/texture catalog rows are left
  untouched; these are additional decal entries with distinct ids.
  Placement is null (same caveat as #1505: suite preview falls
  back to its chest-socket marker until a placement is authored).
  They are NOT labeled "scar" — the data does not support that
  label. They surface as face decals / face paint in Decals.
- `game/js/wear-off.js`: pure wear logic (see its header). Face
  paint: 0.20/hit to its zone, 0.10/min + 0.10/min at full sweat,
  floor 0 (gone). Tattoo: 0.05/hit, 0.01/min, floor 0.55 (faded,
  never gone). Scar: 0.01/hit, floor 0.85 (barely fades — a scar
  is not paint; this is the system's scar slot for when scar
  assets are identified or authored). `setMaterialOpacity` bridges
  to a THREE material (transparent + opacity + needsUpdate).
- Tests: `test/wear-off.test.mjs` (5/5) and
  `test/parts-face-decals.test.mjs` (header totals, 179 unique
  non-pending entries, decal_logo 290, PNGs in repo).
  `test/parts-tattoos.test.mjs` decal assertion updated 111 → 290.

## Still owed (counts, reasons)
- Scars labeled as scars: 0 found / 0 wired / owed — no labeled
  scar asset exists in WMXIX, No Mercy, or 2K19 data as landed.
  Options, in order: (a) human visual pass over the 179 face
  decals + 132 body overlays to tag any scar-shaped marks
  (e.g. tiny marks in ta1_*), (b) CNPC mapping of 2K19's 607
  edit/ch files against its 597 DDS textures, (c) author original
  scar decals in the WMXIX overlay style (procedural marks, not
  copied commercial art).
- Body overlays: 132 found (Upper 59 + Lower 73) / 0 wired as
  decals / owed — they are body-UV maps, and wiring them as
  chest-socket decals without a UV/placement mapping would
  misplace them. Placement mapping is the blocker.
- Face_op opaque 68 + ta2 44: full-face textures, not overlays —
  not decals, correctly left as face textures.
- 2K19 scar/face-paint identification: 597 DDS + 607 edit/ch
  files, unmapped (hash names) — owed, needs CNPC work.
- Wear-off live wiring: the module is pure + tested, but it is
  NOT yet hooked into the fight loop / hit path or the
  customization consumer's texture layers — that hook-up (hit
  zone from combat-systems, material handles from the consumer)
  is the next PR, not claimed here.
