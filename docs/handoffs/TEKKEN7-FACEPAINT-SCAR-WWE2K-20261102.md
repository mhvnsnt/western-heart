# Face paint / scars / wear-off — WWE 2K + Tekken search, 2026-11-02

Owner direction: the face-painting, scars, and wear-off data would be in the
WWE 2K games or in the Tekken games — not just in the WMXIX / No Mercy legacy
data already searched in PR #1518 (0 labeled scars there, 140 Face_op
unclassified, no wear-off mechanism in that legacy code).

## What was searched, in order

1. WWE 2K19 teardown in Western Heart (PRs #1480/#1481/#1483/#1485, 1,677 files).
   `teardown/wwe2k19/extracted/edit/ch/` has 5 CAW part sets (48202, 50102,
   50202, 50302, 50402), each with one `0000.cnpc` (24,016 bytes, binary, no
   readable strings other than the `CNPC` magic) plus one `F423F.cnct` and
   roughly 109–127 hash-indexed `.dds` files (e.g. `0002.dds`, `0010.dds`).
   Total across the batch is 597 DDS + 607 edit/ch part files per the pull
   record. No DDS file is labeled scar, face paint, tattoo, damage, bruise,
   or sweat — the names are hash indices only. No scar/face-paint label can
   be extracted from them without visual DDS inspection plus CNPC format
   mapping, which is still owed (see below). No file was re-labeled here.
2. WWE 2K19 Creation Suite documentation already in the repo
   (`customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`, source WWE 2K19):
   Makeup / face paint / masks are a creation option, and tattoos are
   "layered, placeable, scalable, rotatable — full body canvas". That is
   creation-time layering, not in-match wear-off, and it carries no numeric
   fade rate.
3. WWE 2K20 / 2K22 / 2K24 in the repo: 2K20 and 2K22 are README-only pull
   plans, awaiting Steam extraction. No 2K20/2K22 game data, and no 2K24
   directory, is present in the repo to search. Steam auth is the blocker
   named in those plans. Nothing from 2K20/22/24 is claimed here.
4. Tekken teardowns in the repo + GRE:
   - Tekken 7 customization database (GRE `tekken7/customization/items.json`,
     23,548 items, source Tekken 7 Steam tkdata list): slot 8 is Face Paint,
     asset type CharacterItemTex, slot title MAKE_UP.
   - Tekken 5 / 3 / 6 / TTT2 teardowns in the repo: roster, model, motion,
     and customization-schema docs, but no face-paint item list and no
     wear-off values were found in them in this search. Tekken 3 predates
     the customization feature (which started in Tekken 5, per the
     customization extraction report).
   - Tekken 8 teardown in the repo: models/ui only, no customization item
     data present to search.

## Tekken 7 face paint — found, counted

- Slot 8 entries: **459 found, 0 wired as selectable decals, 459 reference-only**
- Distinct designs: **47** (see `teardown/tekken7/facepaint-reference.json`)
- Most common designs (character variants each): stamp 46, anger_m / g_rock /
  kabuki / kyou_m / skull_m / tribal 30 each, out_anim_m / tetu_m 29 each.
- Scar-named item: **exactly 1 — `kaz_fam_scar`, item_no 90016**.
  Scar-adjacent names (not labeled scar): `law_fam_suture_eye` (10014),
  `lar_fam_splinters` (180012), `lar_fam_injured` (180013),
  `dnc_fam_plaster` (220017), `kzm_fam_unhealthy` (260013).
- No tattoo-named, bruise-named, blood-named, or wound-named slot-8 item exists.
- Item record fields are only: item_no, mesh, slot_code, text_key, group,
  flags, aux. **There is no opacity, fade, damage, sweat, or wear field in
  any Tekken 7 item record.** Face paint in Tekken 7 is a static texture
  item, not a wearing layer.

## Wear-off / damage / sweat — what the two series actually do

- **WWE 2K19, in-match (public review description, not repo data):**
  sweat is visible, and worked areas turn red; damage shows and blood
  pours if blood is turned on. That is a damage overlay (redness / blood),
  not face paint, tattoos, or scars fading. No numeric rate, opacity curve,
  or per-zone fade value for decals was found in any repo data.
- **Tekken 7, in-match:** sweat/battle appearance in Tekken 7 was a display
  parameter, not a dynamic rolling effect (per the producer description
  quoted in Tekken 8 coverage). No face-paint wear value was found.
- **Tekken 8, in-match:** sweat, rain, and dirt are dynamically depicted
  rolling down / accumulating on character models, and characters take
  visible battle damage. That is a shader/material effect on the character
  model, not a face-paint decal fading, and no numeric wear-off rate for
  decals was found in any repo data (no Tekken 8 customization data is
  present to extract one from).
- **Conclusion for `game/js/wear-off.js` (landed in #1518): it is NOT
  changed by this PR.** No real wear-off value was found in WWE 2K or
  Tekken data actually present, so the WH design defaults in that module
  (facepaint hit 0.20 / time 0.10 / sweat 0.10, tattoo hit 0.05, scar hit
  0.01, floors facepaint 0 / tattoo 0.55 / scar 0.85) remain WH design
  defaults, not copied legacy values. Changing them to invented
  "Tekken/WWE values" would be fabrication.

## What this PR wires

- Reference index only: `teardown/tekken7/facepaint-reference.json`
  (47 distinct designs, 459 entries counted, scar + scar-adjacent items
  listed, every design marked `texture_pending`).
- **Selectable decals wired: 0.** No Tekken face-paint texture file is in
  western-heart, so no texture path is claimed and no catalog row points
  at a missing file. The 179 decals wired in #1518 remain the only
  selectable face/body decals from data actually in the repo.
- **Scars wired: 0.** The single scar-named Tekken item has no texture
  file in the repo; it is documented, not wired as a selectable scar.
- **Wear-off values changed: 0.**

## Still owed (counts + reasons)

- WWE 2K19 DDS visual classification + CNPC mapping: 597 DDS + 607 edit/ch
  files, hash-named, no labels — needs a visual montage pass (like #1518
  did for WMXIX) plus CNPC format work before any 2K19 scar/face-paint
  row can be written honestly.
- Tekken 7 face-paint textures: 459 item references, 0 texture files in
  western-heart — needs the actual CharacterItemTex files (not present)
  before any of the 47 designs becomes a selectable decal.
- WWE 2K20 / 2K22 extraction: README-only, Steam auth blocker; 2K24: no
  directory present.
- Tekken 8 dynamic sweat/dirt/battle-damage values: no customization or
  shader data present in the repo to extract numeric values from.
- Wear-off auto-hook into the fight hit path and `applyPart` opacity
  handling: still owed from #1518, unchanged by this PR.
