# DEATHFANG — Attire Slots (owner 2026-10-19)

Canonical slot map for DEATHFANG (proprietary, based on Iori Yagami).

| Slot | Display name | Status | Contents |
|------|--------------|--------|----------|
| 1 | **DEATHFANG — The Chained Prisoner** (default) | ✅ wired | Reskin of Iori attire 1: emo black hair/clothing, pale skin, NO FUTURE face tattoo (texture), wrist/ankle shackles + dangling chains, inter-ankle chain, neck collar, chest cross chains (all skinned to Iori's skeleton; 59 anims preserved). `roster/deathfang/attires/attire1/model.glb`. Renders: `docs/tpose-refs/deathfang/a1_front.png`, `a1_back.png`, `a1_face.png` (own-eyes verified, textured). |
| 2 | **DEATHFANG — Chained Prisoner Werewolf** (transform form) | ⏳ follow-up | The werewolf transform form (move 23 in `game/assets/movesets/deathfang.json`). Free the werewolf (Soul Eater) folds into this form's canon. Asset key `deathfang-werewolf` already reserved in `game/js/assets.js`; the GLB lands in a follow-up PR. |

Moveset: `game/assets/movesets/deathfang.json` — Iori's full kit, 24 moves
with Tekken inputs (see README.md).
