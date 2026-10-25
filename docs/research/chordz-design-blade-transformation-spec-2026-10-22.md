# Chordz — Design, Canon & Blade Transformation Spec

**Date:** 2026-10-22 | **Source:** user directives (2026-10-22, worker 78) | **PR:** #733 (branch `archive/chordz-a1-p1-p2-20261022`)

**Status:** ALL FOUR STAGES ARCHIVED. Stage 1 (Normal) by PR #725 (merge
commit `13bd1d9`); Stages 2–4 (Phase 1, Phase 2, Final) by PR #733.

## Character (user's design, user's own words)

> "Chordz — the emo guitarist (Lars' moveset, already claimed). Edward
> Scissorhands look: pale face, dark eye circles, face paint, black
> lipstick, straight jacket, crazy sideways hair."

## Canon (established in repo, no inventions)

- **Tekken base → WH character ladder:** Lars→Chordz (`docs/decisions/2026-10-22-session-directives.md`).
- **Moveset:** Lars — fully banked (`docs/MOVESET-COVERAGE.md`: chordz | Lars | 115 moves, FULL-BANKED).
- No backstory beyond the user's design words above; lore beyond this is NOT
  authorized in this doc.

## Blade Transformation System (user design, 4 stages — user's own words)

1. **Normal:** "No blades, just the emo guitarist look"
2. **Stage 2:** "Blades shoot out of his hands (Edward Scissorhands)"
3. **Stage 3:** "Mass of blades all over hands — spiked ball of blades instead of hands"
4. **Final form:** "Batman Who Laughs with knives ALL OVER body. Only hair and
   smile visible. Big knife across eyes (can't see eyes). Razor blades in hair."

### Mechanics (user, verbatim)

> "Gradual transformation with visual transformation sequences. Strength and
> power INCREASE with each stage."

## Archive status (PR #725 for Stage 1, PR #733 for Stages 2–4)

| Stage | Slot | Model | Size | md5 | Tag |
|---|---|---|---|---|---|
| 1 (Normal) | `roster/chordz/attires/attire1/source/chordz-a1.glb` — archived by PR #725 (byte-identical to this lane's pull: same Tripo model, md5 `c29e6da1ea8fd3efcf0b9a5d27d9bb44`) | Tripo "gothic leather character 3d model" ([studio.tripo3d.ai/3d-model/fda3612c-62de-4c4a-83e3-43c79c218c43](https://studio.tripo3d.ai/3d-model/fda3612c-62de-4c4a-83e3-43c79c218c43)) | 21,913,940 | `c29e6da1ea8fd3efcf0b9a5d27d9bb44` | `chordz-a1-original` (anchors #725's merge commit `13bd1d9`) |
| 2 (Phase 1) | `roster/chordz/transformations/phase1/source/chordz-p1-edward-scissorhands.glb` | Tripo "edward scissorhands 3d model" ([studio.tripo3d.ai/3d-model/f9a71d52-20b7-43dd-a819-d8c21fe5dfda](https://studio.tripo3d.ai/3d-model/f9a71d52-20b7-43dd-a819-d8c21fe5dfda)) | 20,735,052 | `7710f5b90ff89cef155444a428302c32` | `chordz-p1-original` |
| 3 (Phase 2) | `roster/chordz/transformations/phase2/source/chordz-p2-blade-spikes.glb` | Tripo "edward scissorhands 3d model" ([studio.tripo3d.ai/3d-model/7c25a9a1-d627-4fd6-b41e-3432c715b253](https://studio.tripo3d.ai/3d-model/7c25a9a1-d627-4fd6-b41e-3432c715b253)) | 21,751,348 | `f0e4d68c7fff50689d13502c8ac34fb5` | `chordz-p2-original` |
| 4 (Final) | `roster/chordz/transformations/final/source/chordz-final-cutter-who-strums.glb` — "The Cutter Who Strums" | Tripo "spiky humanoid 3d model" ([studio.tripo3d.ai/3d-model/67484a7f-0c85-45ed-8fc1-1797b7894f33](https://studio.tripo3d.ai/3d-model/67484a7f-0c85-45ed-8fc1-1797b7894f33)) | 24,748,736 | `bcd95a431b434d6b6c6289c7606352ca` | `chordz-final-original` |

- Archive-only: all three are unrigged static sources, NOT wired into
  MODEL_URLS.
- Byte-verified: md5 of each committed file matches the staging original.
- Immutable-original restore-point tags, message "Restore point: these bytes
  never change": `chordz-a1-original` anchors PR #725's merge commit
  (`13bd1d9`); `chordz-p1-original`, `chordz-p2-original`, and
  `chordz-final-original` are created on PR #733's merge commit (per #603
  pattern).
- The #603 (dorowani) archive pattern was followed: GLB + manifest.json per
  slot, same field schema.

## Future work (explicitly NOT built here — for the rig/anim lane)

- Rigging/skinning of all four archived stages (they are unrigged statics).
- Visual transformation sequences between stages (gradual transformation).
- Power scaling per stage wired to gameplay (strength/power increase).
- Do NOT touch the archived source files: any rework goes in new files/slots
  with a new restore-point tag.
