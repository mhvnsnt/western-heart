# batch10 special/non-Tekken moveset pull — worker log (2026-10-23)

Owner instruction (verbatim, user 2026-10-23): "Now we need to get that done for every
other character" — replicate the Law/Lars pull pattern (PR #823) for the special/non-Tekken
fighters.

## Per-fighter
- deathfang (122→127): +5 documented KOF Iori moves from iori.json (Ya Sakazuki DM,
  getup low/mid, face-down kick, back-turned strike), diffed by kof_motion id.
- charger (199→203): +4 documented EX2+ supers from sf-blanka.json (Ground Shave Rolling,
  Jungle Beat, Beast Hurricane, Super Electric Thunder).
- vainabel (52→60): +8 documented DOA Bass moves from doa-bass.json; 63214T not
  double-added (already present as Powerbomb — documentation variance).
- cainelias (41→46): +5 documented WWF No Mercy Undertaker moves from
  banks/wrestling.json (name/input/anim_ref documented; frames/damage estimated by
  analogy, stated in-file). 5 existing WH SIGNATURE moves untouched.
- ryuji (103→127, +2 specials): Rock side merged from ryuji-rock.json (zero key
  collisions; merge_sources.rock_side_merge_20261023 recorded).
- kronos (772→900): SF/Zangief side verified complete (all 34 sf-zangief + 92 zangief
  sf_motion present); Golem (Urban Reign) side has NO documented source — gap filed,
  nothing invented. (900 includes 128 SF6 moves another lane landed.)
- koreshi (953→1080): Vega SF kit + T8 Yoshimitsu kit verified complete; flagged
  CUSTOM-SOURCE (no Kakashi/SSJ/ninja game source exists; nothing invented).
- dxmmii-patchwork (166→170): +0 moves; mimic system documented in-file (mimic block).

## Lock
All 8 files: anim_set_lock + per-move set stamps (FIGHT for combat, SHOW for taunts).

## Gap docs
docs/anim/DEATHFANG|KRONOS|KORESHI|CAINELIAS|CHARGER|VAINABEL|RYUJI|DXMMII-ANIM-GAP-20261023.md

## Verification
Semantic diff: 0 losses, 0 removals, additions only. fighter-completeness.test.mjs 4/4.
resolveMove 8/8. gitleaks clean.

## Handoff
game/assets/movesets/index.json moves/inputs/bytes for the 8 fighters need regeneration
(via tools/moveset-merge/merge_sources.py) — deferred to a follow-up to avoid the
high-contention index treadmill. The game loads full moveset files at fight time; the
index counts are display metadata only.
