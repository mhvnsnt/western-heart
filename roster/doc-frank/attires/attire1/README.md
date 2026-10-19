# DOC FRANK Attire 1 — Mid-match TRANSFORMATION (Roshi-style)

## Owner spec (2026-10-19, verbatim)

- "Doc Frank attire 1 (Old man/Pre transformation) he can transform mid match
  and he will transform to his bigger glb model version of attire 1, when I share it"
- "he transforms like master roshi from dbz"

## The two forms

| Form | Model | Source |
|------|-------|--------|
| **Pre-transform (old man)** | `pre-transform/model.glb` | The Doc Frank Machine Shop reskin (`roster/doc-frank/attires/machine-shop/doc-frank-machine-shop.glb`, PR #263) — wild grey hair, goggles, trench coat. |
| **Post-transform (bigger)** | `post-transform/model.glb` | Tripo pull 2026-10-19: https://studio.tripo3d.ai/3d-model/597c67b3-c1ea-4827-b736-97318c4e154a ("futuristic character 3d model" by dg88will), 20.6MB meshopt. |

Concept targets: the 4 renders the owner sent 2026-10-19 (old man in suit →
shirtless muscular forms, brain-dome variants).

## How the mechanic works (game/js/)

**Generic system — any fighter with `charData.transform` can transform.**

1. **Trigger:** `KeyT` on keyboard, or the 💪 TRANSFORM touch button
   (`game/js/input.js` pushes the `'transform'` action; `game/js/game.js`
   dispatches it to `p1.tryTransform()`).
2. **Swap:** `Fighter.tryTransform()` (`game/js/fighter.js`) removes the old
   model from the lean group and attaches a fresh `assets.createInstance()`
   of the target model — facing, position, and body english are preserved
   because the swap happens under the same `lean` group.
3. **Stat changes** (owner spec: bigger = more damage, slower):
   - `power × 1.4`, `speed × 0.88` (clamped to the 3.5 game cap), `defense × 1.15`
   - Optional `bodyScale` grows the root (Roshi bulk-up).
4. **One-way per match.** The transform target is preloaded in
   `game/js/main.js` `startFight()` alongside the base models
   (`createInstance` is synchronous — no mid-fight download hitch).
5. **Feedback:** full-body aura flash (`_auraFlash = 1.0`) + power-up sound.

## Honest flags

- Both GLBs are **static Tripo meshes** (no skeleton). They need the
  `tools/auto_rig/` pass before the swap looks right in the live game —
  same pipeline every other Tripo fighter went through. The mechanic code
  is complete and follows the existing `createInstance` contract exactly.
- The old-man Machine Shop GLB is also unrigged (2.5MB, PR #263) — the
  wiring lane's rig work covers it.
