# T7 throw fix — proof videos (2026-11-21, Lane E)

Owner order (2026-11-21 ~19:55 EST): flip the orange victim upright, feet to
the floor, facing the thrower; audit all other T7 grapples for the same flip;
wire up + show. The fix: all 24 receivers rebuilt with the joint sandwich
(`tools/anim/tkmovesets2/joint-sandwich.json`); the `_n` motions re-labelled
the thrower's throw motions and the `_y` receivers wired as the victim
(`game/js/t7-throw-clips.js`); the grabbed hold (move 554) and 15 escapes
pulled from the real King `.tkmvst`.

## The videos (all 1280×720 @60fps)

**Primary show pieces — the throw plays connected:**
- `king-1plus3-winding-nut-t3-vs-t7-shared.mp4` (131f, 2.18 s) — shared
  thrower-frame placement. The pair closes to 0.51 m mid-throw (T3: 0.48 m).
- `king-2plus4-suplex-t3-vs-t7-shared.mp4` (138f, 2.30 s) — min 0.46 m
  (T3: 0.74 m).

**Clean f0 grab stance:**
- `king-1plus3-winding-nut-t3-vs-t7-fixed.mp4` (131f) — Lane D placement.
  f0: victim upright, feet on the floor, facing the thrower, hands meeting —
  matching the T3 panel.
- `king-2plus4-suplex-t3-vs-t7-fixed.mp4` (138f) — same for 2+4.

**Grab+hold+throw as one sequence:**
- `king-1plus3-sequence-grab-hold-throw.mp4` (160f, 2.67 s) — grab (40f,
  connect f12) + hold 554 (30f) + throw 574/575-fixed (130f).
- `king-2plus4-sequence-grab-hold-throw.mp4` (168f, 2.80 s) — grab + hold +
  throw 578/579-fixed (138f).

## What the sequence does and does not show (read this first)

The grab connects into a real bent-over hold (move 554 — the victim folds
double, feet dangling 0.31 m, facing the thrower at 42–58° chest bearing);
the hold clinches; then the throw plays connected and ends with the victim
flat. At the hold→throw boundary (out f29→f30) there is a VISIBLE CUT: the
victim snaps from folded-double to upright in one frame (hand jump 1.27 m
1+3 / 1.11 m 2+4). Root position is continuous by construction; the cut is
pure POSE — the hold-end pose and the receiver-f0 pose are different
authored poses. The real game blends that transition; this render does not
(and must not invent a blend). The sequence is the best connected version
stageable from the authored clips without inventing motion.

No upright face-to-face grab stance exists anywhere in the sequence — the
authored data never has one. The clean upright face-to-face stance is what
the `-fixed` videos show (throw f0, Lane D placement).

Full numbers, staging design, and own-eyes verdicts:
`~/workspace/_t7throw-fix-20261121/lane-e-wireup/RENDER-REPORT.md`
(workdir; the PR body links the same numbers).
