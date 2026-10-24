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

## Owner's models (2026-10-20 — canon attires)
The owner's own Tripo models supersede the reskin below as the canon attires:
- **Attire 1 (human):** Tripo `6486151e` — `attires/attire1/model.glb`. Its open
  eye shipped unpainted (skin-pink eyelid in the atlas) and was repaired via
  the customization eye library (`customization/parts/deathfang-eyes/`).
- **Attire 2 (werewolf):** Tripo `b4094ecf` — `attires/attire2/model.glb`,
  asset key `deathfang-werewolf`. Transform form (TRANSFORM + full nine-soul
  meter, both directions) and selectable attire. Character, per the owner: the
  human is an emo loner people underestimate — "this dude can't be who they
  say he is"; the wolf is the monster that terrorizes towns, the bloodlust
  that put him in prison — "oh shit... we get it."
- **Movesets:** `deathfang.json` = 122 moves + CRIMSON HOWL special (full set,
  PR #355 union). `deathfang-werewolf.json` = the same 122 + special, plus 5
  beast mix-in attacks (MOONFANG LUNGE, FERAL MAUL, GRAVE BITE, CHAINBREAK
  RUSH, RISING MOONCLAW). Stance and locomotion stay Iori's in both forms —
  beast flavor is attack-only (owner's werewolf stance rule).

## Build (legacy reskin — preserved at Attire 3)
Attire 1 was originally a surgical reskin of the Iori base model
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
- `game/js/roster-full.js`: roster entry (Rushdown, surge: NO FUTURE) + `forms`
  transform map (WEREWOLF UNLEASHED up / CHAINED AGAIN down)
- `game/js/attires.js`: attire picker (ATTIRE 1 · CHAINED PRISONER / ATTIRE 2 · WEREWOLF)
- `game/js/movesets.js`: `deathfang` + `deathfang-werewolf` in MOVESET_IDS
- The legacy reskin GLB moved (git mv, history kept) to
  `attires/attire3/model.glb` — preserved, not deleted, no longer canon.
