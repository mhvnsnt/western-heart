# T7 generic banks: every T7-stance fighter's walk / block / hit / KO from its OWN base's real Tekken 7 data (2026-11-10)

Owner (verbatim): "negativo should have only had t7 data from negan he never had a t3 skeleton I thought" and "do the
skin wait and get the rig ... and then put it on the ... Tekken 7 ... bases". Bake approved by the owner 2026-11-10
("I give the ok on the bake").

## Before

The 16 fighters with a real T7 stance (and T7 attacks) still played walk, block, hit, KO, crouch, jumps, dashes and
sidesteps from Tekken 3 banks (Negativo from T3 Bryan, Purple Rain / Chordz from T3 Jin, ...).

## What was done

- **Plans** (`tools/anim/t7_generic_slots.py`, committed in `tools/anim/t7_generic_slots/<code>.json`): each base's
  own moves, read from its motbin, nothing guessed:
  - walk / dash / crouch / jump / sidestep from its neutral stance's button-less cancels;
  - guard / damage / launch from the engine's shared states;
  - 1 / 3 / 4 from the moves its verified T7 move pack already plays for those buttons.
- **Bake** (`tools/anim/t7_generic_bank_bake.py --slots`): the same path as every in-game T7 stance and attack.
  - 0x64 clips go through the game's own sampler (emulated); 0xC8 clips through Kiloutre's applier on Koenji's
    mannequin.
  - Inputs hash-checked: helper `1b447b1f...`, mannequin `ce817108...`, exe `7f2b6872...`.
  - 13 banks, 245 clips, every FK self-check 0.000000 m.
- **Wiring**: `game/js/t3anims.js` T3_BANKS `t7_*` and `game/js/fighter.js` OWN_SLOT_BANKS.
  - The existing own-slot layering plays the base's own T7 state wherever one exists. The T7 stance still wins for
    the stance; the Tekken 3 bound bank fills only what the base has no state for.
- **KO is not `Fall_sKAM`.** That shared clip (`naco_700dwn2`) is a knockdown-and-recover: baked hips 0.98 -> 0.45 ->
  1.07 m, so a KO'd fighter stood back up.
  - Every candidate down state was baked and measured.
  - The KO is now the engine's standing knockdown (`Sco_nkdown`, via the base's own `sDm_nkdoBxC` / `sDm_InkdowCE`):
    hips 1.01 -> 0.15 m and it stays down.
  - Pond's and Ryusan's T7 banks (`raven`, `luckychloe`, 2026-11-03) had the same stand-back-up KO and get the same
    fix.
- **T7 data is not "corrected"**: banks baked by the T7 mannequin path (`skeleton.json` tool =
  `tools/anim/t7_c8_stance_bake.py`) skip the Tekken 3 head / spine / arm normalizations, like the `t7:` stance
  skeletons already did (a jointed rig; its head and arm angles are the character's real acting).

| Fighter(s) | Bank | Base |
|---|---|---|
| pantera | t7_king | King |
| diablo | t7_heihachi | Heihachi |
| skull, retsu | t7_bryan | Bryan |
| burger | t7_bob | Bob |
| sakura, sha | t7_xiaoyu | Xiaoyu |
| phantom | t7_yoshimitsu | Yoshimitsu |
| gyou, tobi | t7_hwoarang | Hwoarang |
| gashadokuro | t7_kuma | Kuma |
| aotsuki | t7_panda | Panda |
| nightwolf | t7_julia | Julia |
| purplerain | t7_lee | Lee |
| chordz | t7_lars | Lars |
| negativo | t7_negan | Negan |

## Judged by eye

The sheets `t3-vs-own-t7-1.jpg` .. `-3.jpg` show 17 fighters (gyou has no model yet). For each: walk, guard, hit and
KO, the game before (Tekken 3) next to the base's own T7 clip, in the game's own loader and retarget (poselab, 3/4
view, full body).

- Walk, guard and hit read as natural Tekken motion on every fighter, nothing worse than before.
- Every KO now ends lying down.
- Pond's and Ryusan's KO lie down instead of being caught mid-way back up.
- Burger's board-shaped geometry and Sha's floating hair shards are broken rig weights, the same in both columns.

## Tests

- `test/t7-generic-banks.test.mjs` (4): the banks are registered and T7-baked with their slots; every KO ends down;
  each fighter maps to its own T7 stance's base; T7-baked banks get no Tekken 3 normalization while a Tekken 3 bank
  (jin) still does.
- Unit suite: 107/108 files pass; `test/hitbox.test.mjs` fails the same way without this change in this container
  and passes in CI.

## Next

Hands: the motbins also carry 113 hand-pose clips per base (19 finger joints); the game's clips are 21 body joints.
Same bake path, plus decoding which hand pose each move triggers.
