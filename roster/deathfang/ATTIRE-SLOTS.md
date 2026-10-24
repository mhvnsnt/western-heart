# DEATHFANG — Attire Slots (owner 2026-10-19, updated 2026-10-20)

Canonical slot map for DEATHFANG (proprietary, based on Iori Yagami).

| Slot | Display name | Status | Contents |
|------|--------------|--------|----------|
| 1 | **DEATHFANG — The Chained Prisoner** (default) | ✅ wired | The owner's own Tripo model (`6486151e`): emo prisoner, collar + chains, NO FUTURE face tattoo. `roster/deathfang/attires/attire1/model.glb`. The model's open eye shipped with no eyeball painted (closed skin-pink eyelid in the atlas) — repaired via the customization eye library (real iris + sclera at the verified UV island); see `customization/parts/deathfang-eyes/`. Proof: `deathfang-eye-fix-closeup-20261020.png`, `deathfang-human-attire1-front-20261020.png`. |
| 2 | **DEATHFANG — Chained Prisoner Werewolf** (transform form) | ✅ wired | The owner's own Tripo model (`b4094ecf`). Asset key `deathfang-werewolf` in `game/js/assets.js`. Reachable two ways: mid-fight transform (TRANSFORM touch button + full nine-soul meter; tap while crouching reverts) and directly from the attire picker. Moveset `deathfang-werewolf.json`: the full 122-move DEATHFANG kit + CRIMSON HOWL + 5 beast mix-in attacks. Stance and locomotion stay Iori's (owner's werewolf stance rule). |
| 3 | **DEATHFANG — Iori Reskin (legacy)** | preserved | The PR #368 reskin of the Sketchfab Iori model (emo re-grade, NO FUTURE texture tattoo, skinned chain meshes, 59 anims). Superseded as canon by the owner's Tripo models on 2026-10-20; the file is kept, not deleted: `roster/deathfang/attires/attire3/model.glb`. Not in the attire picker. |

Movesets: `game/assets/movesets/deathfang.json` (122 moves + special) and
`game/assets/movesets/deathfang-werewolf.json` (127 moves + special) — see README.md.
