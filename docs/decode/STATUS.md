# STATUS — living status table

One row per fix. Every fix PR adds or updates one row here, plus its own
per-file doc. A file stays flagged here as unsolved until a PR lands its
decode with before/after proof.

| Game | Fighter / file | Mechanism | Solved? | Source | Files fixed / remaining | Fix PR |
|---|---|---|---|---|---|---|
| Tekken 3 | King on Pantera — `game/assets/anim/t3/king_on_pantera_leoman/` | Bake defect (decode clean, bake used the wrong rig: pack hip 0.9805 m vs shipped rig 1.0613 m, 8% pair-geometry error) + old-tool Head-track deviation (50.908°) | **Fixed** (this PR) | Verified T3 divmot decode + shipped `game/assets/models/pantera.glb` + `lab/tools/t3_motion_bake.py` | 32 clips + `rows.pack.json` (256 rows) + `reactions.pack.json` (568 rows) + `skeleton.json` re-baked; `hit_frames.json` unchanged (rig-independent) | #1807 |
| Tekken 7 | King throws (10 clips; common_709, rotsm_534, rotsm_574, rotsm_578, …) | Clip roles swapped (thrower vs victim) | Hunt running — DO NOT TOUCH until the hunt decides roles | T7 memory-route decode | 0 fixed / 10 disputed | — |
| Virtua Fighter 5 | Motion (all) | Motion not decoded | **Unsolved** | — | 0 fixed | PR #713 open |
| Tekken Tag 2 | motbin motion | MOTA offsets present, motion not decoded | **Unsolved** | — | 0 fixed | — |

## Notes

- The T3 King row is the first fix in this directory. The T3 decode itself
  (divmot banks + AnimDecodePose port) was already solved in-repo before
  this PR; this PR fixed the *bake* of that decode onto the wrong rig, plus
  a Head-track deviation carried by the old bake. See
  `tekken3/king-pantera/fixed-vs-scrambled.md` §2 and §8.
- Honest limit (carried from the fix PR): the re-bake narrows the 8%
  pair-geometry error to ~0% by construction but does **not** close the
  1.45 m throw-connect gate on its own; the gate fix already landed
  (PR #1781). Do not claim otherwise.
