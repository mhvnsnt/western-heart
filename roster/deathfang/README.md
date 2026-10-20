# DEATHFANG

Proprietary character (owner 2026-10-19 ~20:06–20:12 CDT). All caps, one word,
everywhere: **DEATHFANG**.

## Canon
- New proprietary character based on Iori Yagami — keeps Iori's moves, stance
  and animations.
- Reskin: prisoner/slave — a prisoner to his own grief and emotions,
  chained/shackled, emo styling, with the Soul Eater "NO FUTURE" face tattoo.
- Transform: DEATHFANG transforms into a CHAINED PRISONER WEREWOLF
  (attire 2 / transform form). Iori's inspirations include Free the werewolf
  from Soul Eater — that folds into the werewolf form canon.

## Build
Attire 1 is a surgical reskin of the Iori base model
(`roster/iori/attires/attire1/model.glb`, Sketchfab CC-BY by 0xo,
scale-fixed PR #341). The original GLB binary is preserved byte-for-byte
except:
- Base texture re-graded per UV category (hair crimson → emo black, red
  pants → charcoal black, jacket/shirt deepened to black/grey, skin paled)
  and the **NO FUTURE** tattoo drawn onto the face region of the texture.
- Appended skinned chain meshes (`DEATHFANG_IRON` dark-metal material):
  wrist shackles with dangling chains, ankle shackles, an inter-ankle
  sagging chain, a neck collar with hanging links, and two chest cross
  chains — each 100% weighted to its anchor bone, so they follow Iori's
  stance and animations.
- All 59 original animation clips and the full skeleton are untouched.

Moveset: `game/assets/movesets/deathfang.json` — Iori's full kit (24 moves,
Tekken inputs: Yami Barai, Oniyaki, Kototsuki In, Aoi Hana rekka chain,
Dokugami, Tsumagushi, Ya Otome super, throws, plus the werewolf transform
and the NO FUTURE signature).

## Renders (own-eyes verified, textured)
- `docs/tpose-refs/deathfang/a1_front.png`
- `docs/tpose-refs/deathfang/a1_back.png`
- `docs/tpose-refs/deathfang/a1_face.png`

## Wiring
- `game/js/assets.js`: `deathfang` (attire 1), `deathfang-werewolf` (attire 2)
- `game/js/roster-full.js`: roster entry (Rushdown, surge: NO FUTURE)
- `game/js/movesets.js`: `deathfang` in MOVESET_IDS
