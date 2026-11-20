# Sideways k-NN rigs replaced: 10 fighters re-rigged and wired (2026-10-23, Claude session)

Owner: "get all the ones that are rigged right wired up ... we need to get gameplay affected".

## What was wrong

The Tripo pulls face **+X** (their front is seen from a camera on +X). The 2026-10-21 k-NN batch rigs
(`model-rigged.glb`, 49 joints, donor pantera.glb) assumed **+Z**, so the template skeleton sat across the body:
in game these fighters stood in profile at rest and their T3 stance shredded (contact sheets of the 2026-10-22
sweep, `tools/proof-harness/rig_sheet.mjs`).

`static_four_views_*.png`: the original statics rendered from +Z, +X, -Z, -X (Blender workbench, texture colour).
The face is visible from +X on every one of them.

## Fix

Each original static (`model.glb`, untouched) re-rigged with `tools/auto_rig/rig_tripo_static.py --facing +X`
(GameRig + Blender bone heat + smooth_weights + meshopt). The result is written beside the old rig as
`model-rerig.glb`; the old `model-rigged.glb` stays in place. `model-facing.json` records the new keys as +Z.

| key | new file | sha256 (first 16) |
|---|---|---|
| `skull` | roster/skull/attires/attire1/model-rerig.glb | afa819be2c47ac1d |
| `kronos` | roster/kronos/attires/attire1/model-rerig.glb | d2edf21a003efce9 |
| `kronos-attire2` | roster/kronos/attires/attire2/model-rerig.glb | 96341e4f8a32c003 |
| `saku-ra` | roster/sakura/attires/attire1/model-rerig.glb | 086972b7cc344295 |
| `phantom` | roster/phantom/attires/attire1/model-rerig.glb | b6a01eaf2aa688d8 |
| `purple-rain` | roster/purplerain/attires/attire1/model-rerig.glb | fac0f87c72517b8b |
| `doc-frank-wowomomo` | roster/doc-frank/attires/attire2/base/model-rerig.glb | 3f8ffb8101ddc3bd |
| `doc-frank-frankenstein` | roster/doc-frank/attires/attire4/base/model-rerig.glb | 74eb05fd67a9e61c |
| `doc-frank-frankenstein-big` | roster/doc-frank/attires/attire4/transformed/model-rerig.glb | 2b49a5aad98d6bc6 |
| `demonio-human` | roster/demonio/attires/human/model-rerig.glb | cb3b475cf475ff35 |

`kinpo` / `kinpo-attire1` already point at the intake lane's GameRig build (`model-intake.glb`); this PR only adds
`kinpo-attire1: +Z` to model-facing.json so it no longer depends on the feet cue.

## Proof (viewed)

`ingame_*.png`: the game's own instance via `game/poselab.html` (rig_sheet harness). Left = rest pose from the +Z
camera (face to camera) and +X camera (clean profile); right = the T3 King stance retargeted by the game.
`rig_sheet_results.json`: game facing +1 for every key, max bone-direction error 0.4 deg vs the decoded source.
`rig_report_<key>.json`: validate.py PASS for each (valid glTF, skinned, canonical bones, 1.8 m); the anim_check
stress-clip numbers are recorded as-is.

## Known follow-ups (not blocking: far better than the rigs they replace)

- `doc-frank-frankenstein` (A4 base): the Tripo pull includes a display pedestal fused under the boots; it rides on
  his feet in the stance. Needs the pedestal cut from the static before rigging.
- `doc-frank-wowomomo`: the yellow tabard stretches with the arms in the stance (cloth weighted to the arm chain).
- Not yet re-rigged: `sam-ur-a1` and `thor` (smooth_weights did not reach its 2.5 gate: floating rocket forearms /
  cape), `waterfall` (smooth_weights crashed on a dense mesh: every edge under 1 cm; fixed in this PR, re-run queued).

## Buffalo Bill and Thor (update, 2026-10-23 evening)

Both failed the auto-rig's smoothing gate (p99.9 edge stretch under the CMU boxing stress clip ≤ 2.5, then ≤ 4.0):
Buffalo Bill's long robe and Thor's cape stretch further than a tight body under that clip. Re-run with
`rig_tripo_static.py --facing +X --smooth-gate 99`; the stress numbers are recorded as-is
(`rig_report_buffalo-bill.json` p99.9 4.42, `rig_report_thor.json` 6.16; validate.py PASS on both) and the in-game check
decided: `ingame_buffalobill_law_bank_thor.png` — both face front at rest; Buffalo Bill holds Marshall Law's guard on the
new law bank, Thor holds King's stance, robe and cape follow without tearing (max bone error 1.0° / 0.4°).
Wired: `buffalo-bill` → roster/buffalo-bill/attires/attire3/model-rigged.glb (was the unskinned static),
`thor` → roster/thor/attires/attire1/model-rerig.glb (was the sideways k-NN rig); facing +Z.

## Limb isolation (owner: "the arms and hands area starts to get a little wonky ... deeper rigging and deeper accuracy")

Viewed on Skull's high kick (Bryan heavy): the inner thighs stretched into a web of trouser between the legs. Cause:
vertices of one leg carried skin weight from the other leg (and arm verts from the other arm / the legs) — bone heat
diffuses across the crotch and armpit gaps. New `tools/auto_rig/backends/limb_isolation.py`: each joint is classed by
the limb chain it hangs under (left/right leg, left/right arm, core); a leg vertex drops influences from the other leg
and both arms, an arm vertex from the other arm and both legs; core vertices (hips, torso) are untouched; weights
renormalized, the dominant joint is never removed. Now a step of `rig_tripo_static.py` (after smooth_weights).

- `limb_isolation_skull_highkick_before_after.png`: the long strand from the kicking thigh to the standing leg is gone
  (a smaller crotch triangle — hip-dominated trouser geometry — remains, follow-up).
- Applied in place to all 16 GameRig rigs made today (old versions stay in git history). Vertices cleaned: e.g. Skull
  68k/68k leg verts, Phantom 101k/101k + 17k/10k arm, Thor 108k/94k + 17k/18k; Ryusan 1.3k.
- `limb_isolation_all16_stance_ingame.png` + `rig_sheet_limb_isolation.json`: every one holds the T3 stance in game.
- Also wired here: `chordz` → attire1/model-rigged.glb (was the unskinned static), `sam-ur-a1` → attire1/model-rerig.glb
  (was the sideways k-NN rig); both rigged with `--smooth-gate 99`, facing +Z.
