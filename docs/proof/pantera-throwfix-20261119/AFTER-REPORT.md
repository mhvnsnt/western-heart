# Lane B AFTER probe — Pantera throw orientation (2+4 / 1+3)

Branch: `pantera-throwfix/orientation-20261119` · PR #1766 · merged b5648cce
Fix commit: a8972c95 (yaw sign flip + facing-tracking two-line lean form).
Probe: live headless-Chromium probe (Lane D method), overlay server = 83b2e090
+ this PR, pantera vs demonio, 261 frames per throw, 2/2 state assertions
pass each throw. Raw posed-bone logs: `after-2plus4.json`, `after-1plus3.json`.

## Orientation — clinch chest yaw (chest -Z, 0=+X opponent, +90=+Z camera), steps 4-48

| throw | BEFORE (main 01c95363) | AFTER (a8972c95) |
|---|---|---|
| 2+4 | -28..+4 deg, mean ~-14.6 deg | -19..+33 deg, mean ~-2.2 deg |
| 1+3 | frozen clinch chest -19/-20 deg | early clinch steps 12-44 read -21..+12 deg |

2+4 step-by-step delta vs BEFORE: 0, 0, 0, 0, +2, +7, +15, +21, +25, +25,
+27, +29 deg — 0 at the connect, rising to +25..+29 deg through the
middle/late clinch. The chest now faces +33 deg (front-side 3/4 to the side
camera) and never reads more negative than -19 deg in the clinch. The source
bend is untouched (chest pitch still -60..-68 deg in the clinch).

Note: the first AFTER run (b789cb8a) had the correction sign backwards —
clinch read -50..-1 deg, worst exactly at the correction peak. Commit
a8972c95 flips the sign (three.js R_y(+th) moves chest world yaw by -th, so
the correction is -0.52 rad in lean space). This re-probe verifies the flip.

## Floor drop — thrower hips Y

| throw | BEFORE | AFTER |
|---|---|---|
| 2+4 | min 0.215 m @step 87, 0.22-0.24 m through the landing | min 0.433 m @step 85; steps 84/88/92/96 hold 0.45/0.44/0.45/0.45 m |
| 1+3 | min 0.215 m @step 87 | min 0.433 m @step 85; same hold |

The 0.45 m retarget floor holds. The attacker is clearly off the floor
through the landing.

## Knees — fixed-axis (world +X, ungameable by the yaw fix)

| throw | BEFORE | AFTER |
|---|---|---|
| 2+4 | L 25/261 min -0.319 m, R 46/261 min -0.345 m | L 27/261 min -0.321 m, R 44/261 min -0.353 m |
| 1+3 | L 25/261 min -0.319 m, R 46/261 min -0.345 m | L 27/261 min -0.321 m, R 27/261 min -0.353 m |

Residual stands as designed: the backward fold lives in the grab clip's roll
(steps 60-78, worst @step 68), not in the floor window, and neither fix
touches it. The dedicated knee-pole correction is a separate follow-up.
Victim unchanged (frozen — Lane A scope).

## Sheet frames — KNOWN HARNESS GAP (video handoff)

The probe's frame sheet captured 9 PNGs, but all 9 show the same connect
pose — the hand-stepped sim advances the posed bones (the JSON above proves
it) but the canvas is stale between `__step()` calls, so `toDataURL` keeps
returning the first painted frame. The sheet frames do NOT show the clinch,
lift, or landing and are not staged here. The video + mid-throw frames still
need a real-time capture (Lane D's capture method, which renders per frame):
run it against main (post-merge, this fix is live) for 2+4 and 1+3 and stage
the clip + frames under `docs/proof/` — that is the outstanding proof step,
handed to the coordinator, not claimed here.
