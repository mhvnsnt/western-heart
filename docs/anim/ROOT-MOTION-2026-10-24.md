# Root motion (2026-10-24)

Owner playtest report 2026-10-24 (verbatim): "Animations that should
make him TRAVEL different distances aren't making him move. He's stuck
in place, fighting kind of stuck."

## What was wrong

`fighter.js` had zero `rootMotion`/`root_motion` references (verified:
0 occurrences). The word "root" occurs 96 times in `fighter.js`, but
none of them is root *motion*:

- `this.root` — the fighter's `THREE.Group`, i.e. the world-position
  node (`root -> lean -> model`). Almost every "root" hit is
  `this.root.position`, `attacker.root.position`, `opponent.root.position`.
- "rooted" — the adjective for "cannot act" (transform cinematic).
- "root drift" — two comments about the sidestep clip choice
  (`_sidestepClip`, `_animate` sidestep case): the clip's decoded
  lateral drift only *selects* which sidestep clip plays; it never
  moved the character.
- `root->tip` — an IK chain comment; `worldToLocal` — a pose helper.

The actual movement paths before this fix were all procedural, never
clip-driven:

- Walk/dash/dodge/sidestep: `vx`/`vz` set by intent code
  (`tryMove`, `tryDodge`, sidestep), integrated in `_physics`.
- Attacks: `_tryAttackFresh` sets `vx = 0`, and `_physics` decays any
  `vx` toward 0 while grounded and not walking/dodging/sidestepping.
  The only attack travel was the authored grab lunge
  (`vx = facing * 2.5` for grabs) — every strike played in place.
- Contact: `combat-core.js` `moveReach` (jabs ~1.75 m, kicks ~1.95 m,
  lunging moves ~2.25 m) decides whether a hit *connects*; it never
  moves the attacker. Reach is not root motion.

## The data was already there

Every decoded T3 clip carries its root trajectory in `root_t`
(`t3anims.js`: `jsonToClip` for `wh-anim/1` files, `decodePackRow`
for `rows.pack.json` — `rx`/`ry`/`rz` in millimetres, `/1000` to
metres). Canonical source frame, after the load-time facing fix:
forward = +Z, character-left = +X, faces +Z. Banks baked facing -Z
(bosconovitch, eddy, gunjack, heihachi own-rig, yoshimitsu) have
their `root_t` flipped to `(-x, y, -z)` by `turnData` in
`loadT3Clips`, so the clips `fighter.js` reads are all in the same
frame. Calibration from the armorking bank's own locomotion clips
(measured, not assumed):

| clip | root_t delta (x, z) |
|---|---|
| `t3_dash_fwd` | (+0.313, +1.125) — forward is +Z |
| `t3_walk_fwd` | (+0.175, +0.628) |
| `t3_backdash` | (-0.232, -0.834) |
| `t3_sidestep_a` | (+1.135, -0.308) — lateral is +X (character-left) |

But the game threw the horizontal part away: `retargetT3Clips`
keeps only the vertical (`y`) part of `root_t` for the
`Hips.position` track (hip bob / crouch height), and
`jsonToClip`'s own comment says "Root motion (root_t) is SKIPPED —
the game handles positioning." The game then never handled it.

Measured on Pantera's bank (`king_on_pantera_leoman`,
`rows.pack.json`, 256 rows): 187 rows travel >1 cm horizontally;
some travel >3 m (rows 237, 183, 220 — long lunges/throws). The
travel is real Tekken data, not authored distances.

## The system (fighter.js, 2026-10-24)

- `rootMotionSample(root_t, fps, t)` (exported, pure): the clip's
  horizontal displacement from its own frame 0 at clip time `t`,
  linearly interpolated between decoded frames. Returns
  `{ fwd, lat }` = source-Z and source-X displacement. Vertical is
  deliberately excluded: hip height already rides the retargeted
  `Hips.position` track and gravity/`vy` owns `root.position.y`.
- `Fighter._rootMotionApply()`: called from `_physics` once per
  frame, during `attack` / `vskill` / `vreversal` only, after
  velocity integration and before the arena clamp and body-vs-body
  pushout — so walls and opponents are resolved against root-motion
  travel in the same frame. It reads the clip
  `_attackClipPlan` already chose for this attack from
  `this._t3.clips` (the *source* clips, which still carry
  `userData.raw.root_t`; the retargeted `t3actions` copies drop
  `raw` and cannot be used). Clip time follows the same warp as
  the visible animation (`attackClipTime(plan.timing, stateT)`),
  so the body arrives exactly when the animated limbs do.
  Displacement is applied incrementally (this frame's sample minus
  the previous frame's), so clips that step forward and settle back
  move the fighter back too, and a string's next hit starts from
  where the last hit left the fighter — no snap-back, no
  double-count.
- Game mapping: `root.position.x += facing * fwd` (source +Z is
  forward); `root.position.z += -facing * lat` (source +X is
  character-left, and character-left is world -z when facing +x,
  as the sidestep comment in `_animate` already records).
  `facing` is frozen during attacks (`update()` only re-faces
  when `canAct()`), so one attack keeps one mapping throughout.
- Whiff vs hit: root motion never reads `hasHit` or any hit
  detection. A whiffed lunge travels exactly as far as a connected
  one, as in Tekken.
- All characters: the code reads whatever bank is bound
  (`this._t3.clips`), with no per-character or per-move distances
  anywhere. A bank's flipped `root_t` is already canonical at load
  time, so turned banks work the same way.

## Guards (what root motion does NOT do)

- Row clips only (`plan.name` starts with `row:`). Generic
  light/medium/heavy/grab fallbacks are excluded: light/medium
  travel 0, but heavy/grab are the row-230 throw-execution clip
  (2.63 m forward, 1.24 m lateral), whose travel belongs to
  `throwExec`, not to an attack attempt. A move with no row clip
  and no raw `root_t` gets no root motion (today's in-place
  behaviour) — marked UNMAPPED, never an invented distance.
- Never during block, sidestep, dodge, jump, throw execution,
  hitstun or knockdown — those positions are already driven
  (procedural `vx`/`vz`, gravity, or the throw lift/slam in
  `_tickState`). Walk/dash locomotion keeps its procedural
  velocity; applying clip travel there too would double-move.
- Never touches `root.position.y`.
- Walls/ring-out: the existing `ARENA_LIMIT` clamp in `_physics`
  runs after root motion, and pushout runs after that. A lunging
  move at the wall stops at the wall; it never leaves the stage
  and never passes through the opponent.
- Known interaction, unchanged by this PR: grab attacks keep
  their legacy `vx = facing * 2.5` lunge on top of clip travel
  (throw-attempt rows travel 0.1–0.5 m; the decaying lunge adds
  roughly 0.3 m). Removing the lunge would change throw reach
  balance, so it stays until the throw lane playtests it — flagged
  here, not silently changed.

## Verified by simulation (test/root-motion.test.mjs, 60 fps ticks)

Real Pantera bank + real `_attackClipPlan`, through the same
`_rootMotionApply` the game runs. All values are the clips' own
decoded `root_t`, not authored distances.

| move (LP1/RP2/LK3/RK4) | clip played | travel (facing +1) | verdict |
|---|---|---|---|
| LP1 jab (`1`) | `row:44` (own) | 0.00 m forward, 0.00 m lateral | stays in place, as a jab should |
| RP2 (`2`) | `row:203` (notation) | +0.85 m forward, -0.40 m lateral | travels; mirrored when facing -1 |
| f,F+2 Beast Elbow (RP2 dash elbow) | `row:111` (donor: King's own f+2) | +0.15 m net, +0.30 m peak, -0.14 m lateral | travels forward; the donor is a standing f+2, so its travel is modest — the T7 dash-elbow's full lunge is a moveset-lane question, not a number to invent here |
| f,F+4 Konvict Kick (RK4) | `row:114` (donor: King's own f+4) | +0.48 m forward, -0.225 m lateral | travels far |
| generic fallback (`heavy`) | — | 0.00 m | excluded by the row-only guard |
| block / sidestep / idle / jump with a stale attack plan | — | 0.00 m, cursor reset | never runs outside attacks |
| RP2 at x = 8.3 through `_physics` | `row:203` | clamped to ≤ 8.4 (`ARENA_LIMIT`) | wall-safe |

Cross-bank check: bosconovitch (a turned bank) `row:4` reads
`fwd -0.802 m, lat -0.325 m` from the loaded clip — the flipped
values, proving root motion reads the canonical frame for
non-Pantera banks too. Full per-character travel tables are not
verified here: Pantera (plus the bosconovitch flip check) is the
simulated proof; every other bound bank flows through the same
bank-agnostic code path, and a per-roster sweep is follow-up work.

## Classification note: Konvict Kick is a mid kick, not a throw

King's T8 frame table (`game/data/t8_frame_tables.json`) marks
`f,F+4` tgt `(t)` — a throw transition on counter-hit
(Konvict Kick to DDT). On the main this PR was first built against,
that `(t)` misclassified the base kick as throw-class (plan:
throw-attempt row `row:283`, 0.19 m net), because the move carries
no top-level hit_level and no decoded hit_words entry. The hitbox
lane merged to main 2026-10-24 (PR #1005) fixed the fallback chain
in `combat-core.js` `hitWordFor`: level is now read from the T7
hit_level (`mid`) before the T8 tgt, so the plan on current main
is the strike donor `row:114` (0.48 m) — the behaviour this PR's
test asserts. The test still awaits `frameTablesReady` so it
asserts production behaviour deterministically.

## UNMAPPED / follow-up (not guessed, not in this PR)

- Moves that fall back to generic light/medium/heavy/grab clips:
  no root motion until those fallbacks are replaced by real rows
  (or re-baked per move). This includes any T7/T8 move whose
  donor/match row is in place but whose real move should travel —
  the clip, not the engine, is the gap; fixing it means assigning
  a travelling row in the moveset lane, not scaling distances here.
- Per-roster travel audit: simulate every bound fighter's
  slot moves and tabulate clip travel vs. the T7/T8 move's
  expected travel; flag mismatches (e.g. a lunging move playing
  a retreating row) for the moveset lane.
- Grab lunge interaction (above): playtest whether clip travel +
  legacy lunge overshoots throw range; if so, zero the lunge for
  row-clip grabs in the throw lane.
- Touch playtest on the live build (this PR's proof is simulation
  + unit tests, per the task's test requirement; the owner verifies
  by playing, as always).
