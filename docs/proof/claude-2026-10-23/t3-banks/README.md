# Four more Tekken 3 banks decoded: Ogre, Kuma, Gon, Law (2026-10-23, Claude session)

Owner: "we're not just pulling stuff from t3 we're pulling stuff from all the taking games"; "marshall law and
firrest law moves both go to ashes/buffalo bill"; the SmutBase fighters must play.

## Why

Chatur (True Ogre base), Menajerii (Kuma beast banks), Dorowani (Gon) and Buffalo Bill (Marshall Law) had movesets but
no animation bank: 17 of the 22 T3 divmot banks were decoded, these were not. In a fight Chatur loaded 0 T3 clips and
stood rigid (`docs/proof/claude-2026-10-23/smutbase/README.md`).

## How (nothing authored)

`tools/anim/t3_bake_bank.py` (new) runs the existing pipeline of the 2026-10-20 remainder banks
(`docs/anim/T3-REMAINDER-BANKS-20261020.md`):
- `lab/tools/t3_motion_bake.py` decodes `teardown/tekken3/animations/divmot{14_ogre,11_kuma,19_gon,01_law}.bin`
  (pose_assemble + usa_motion, bit-exact) onto each character's own body rig `lab/game/assets/t3body_<bank>.glb`
  (`tools/anim/t3_extract_bodies.py`) → `lab/game/assets/t3_<bank>_t3real.glb`.
- The 26 universal move-index slots every shipped bank uses (identical slot numbers across all 17 banks) plus
  light/medium/heavy picked from the bank's own decoded move table by a stated rule (tool docstring); the rule
  reproduces the shipped picks for light 4/4 and heavy 3/4 (anna, paul, hwoarang, bosconovitch).
- Clips re-encoded to the shipped wh-anim/1 layout (WH-Canonical-22, Spine/Neck/toes identity) like `anim/t3/anna/`.
- `tools/anim/t3_bank_skeleton.py` → `skeleton.json` (existing 17 banks regenerate byte-identical; `--check` OK on all
  four new banks, max |1-|q.q'|| ≈ 4e-08).
- `tools/anim/t3_row_bake.py --bank <b>` → `rows.pack.json` with every row the WH movesets reference:
  ogre 187 rows (Chatur's 152 moves), gon 147 (Dorowani), kuma 161, law 216 (Buffalo Bill's 228 moves).

Forest Law: all four of his KMD costumes fail the body fit in `t3_extract_bodies.py` (the reason he never had a body
rig). His moves for Buffalo Bill can be baked onto Law's body (`t3_row_bake.py --kmd-from law`) as a follow-up.

## Wiring

- `game/js/t3anims.js`: `T3_BANKS` += ogre, kuma, gon, law; `SOURCE_TO_BANK` += ogre, kuma, panda→kuma (Panda shares
  Kuma's bank in T3), gon, law. Buffalo Bill's moveset source is `law`, so he resolves to his bank directly.
- `game/js/fighter.js` FIGHTER_BANK: chatur → ogre, dorowani → gon, menajerii → kuma (their movesets name the source as
  a teardown path or not at all).

## Proof (viewed)

- `new_banks_stance_on_pantera_and_chatur.png`: each new bank's T3 stance retargeted by the game onto Pantera Leo man
  and onto Chatur. Ogre and Law: upright guards; Kuma: the low bear stance; Gon: the small dinosaur crouch.
  `rig_sheet_<bank>.json`: max bone-direction error on Chatur 0.4–1.5°, on Pantera 6.8–30.9° — the shipped banks sit in
  the same range on Pantera (anna 16.1°, paul 10.1°: `rig_sheet_anna.json`, `rig_sheet_paul.json`).
- `fight_chatur_ogre_bank_vs_pantera.png` + `fight_chatur_console.log`: arcade fight, Chatur on the Ogre bank: 22 T3
  clips loaded, stance `t3_ogre_stance`, walk `t3_ogre_walkFwd`, attack `2` plays Ogre's own row 50
  (`t3_ogre_row50`), `2,3` plays `t3_ogre_medium`; round `fight`, no page errors.

## Loader race fixed on the way (`game/js/assets.js`)

The first Chatur vs Pantera fight failed: `fight load failed: AbortError: BodyStreamBuffer was aborted`. `loadModels`
cancels the idle warm lane, then joined that same just-cancelled download for any fighter still warming (Pantera is in
the warm list), so the fight rejected. A load whose signal is already aborted is no longer joined; a fresh fetch starts.

## Forest Law → Buffalo Bill (update)

Owner: "So marshall law and firrest law moves both go to ashes/buffalo bill".

- Forest Law bank: his own `divmot20_forestlaw.bin` motion posed on Law's body (`law79/law4.kmd`; his four KMD costumes
  fail the body fit), the `heihachi_on_jin` pattern → `game/assets/anim/t3/forestlaw_on_law/` (29 clips; `t3_crouch`
  resolves into the divmot99 common bank, which pose_assemble does not decode yet — no fighter uses this bank as its
  action bank, Buffalo Bill's is `law`), skeleton.json, rows.pack.json with all 198 rows of his move index.
  `forestlaw_on_law_vs_law_stance.png`: his guard on Pantera / Chatur next to Law's (max bone error 17.2° / 0.9°,
  `rig_sheet_forestlaw.json`).
- Buffalo Bill's moveset: `tools/moveset-merge/bases.json` override (t8 law, t7 law, t3 law + forestlaw, with the
  owner's words), then `merge_sources.py --write --only buffalo-bill`: 228 → 795 moves (T8 Law 162, T7 Law 303, T3
  Law/Forest Law 102), playable input slots 73 → 326; the tool's guard: no move, string, special or input lost.
  Every added move carries `anim_t3` (law 440, forestlaw 25; `same-notation` or `nearest`, flagged); all their rows are
  in the baked packs.
