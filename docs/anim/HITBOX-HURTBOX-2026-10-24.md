# Hitbox / hurtbox hit detection (HITBOX LANE, 2026-10-24)

Owner playtest 2026-10-24: "Hitbox stuff and hurtbox stuff is not making
contact right. A lot of contacts not being made during fight."

## 1. Where Claude's Lane C data was / was not found

The task brief said "Claude's Lane C has 14 hurt cylinders/fighter,
swept-segment hitboxes, 633 reaction records — use that if available".
Verified against the repo on 2026-10-24 (main `374a6a4`, PR #1003
merged, 700 branches listed, open PRs scanned):

- **633 reaction records: FOUND, and they are NOT hitboxes.**
  `game/assets/anim/t3/reactions.json` (1.9 MB, PR #1003) holds the
  decoded T3 EXE tables: 633 records x 21 words, 58 close reactions,
  6 air kinds, per-bank row reactions/throws. `tools/anim/
  t3_reaction_tables.py` contains no hitbox, hurtbox, cylinder or
  swept-segment data (grep: zero hits), and neither does
  `docs/anim/T3-REACTIONS.md` except as reaction-slot vocabulary.
  Reactions say what happens WHEN a hit lands; they cannot say
  WHETHER it lands. The brief's "633 reaction records" belong to
  lane E (reactions), not to hit detection.
- **14 hurt cylinders / swept-segment hitboxes: NOT FOUND anywhere.**
  Code search over the repo returns no hurt-cylinder table, no
  hitbox table, no collision data file. The closest prior art:
  - `game/js/hitdetect.js` (WHHitDetect): a BVH *verify-only* layer.
    Its own header says it "never changes outcomes" and its default
    mode is `verify`. It is not the contact authority and it is not
    wired into `game.js` combat resolution.
  - `game/js/combat-core.js`: a *temporal* swept check (a 30 fps tick
    stepping over a 1-frame active window still counts as active)
    and a root-distance range model. No spatial sweep, no capsules.
  - Branch `fix/combat-playability-20261023` (unmerged, diverged,
    behind main by 193 commits): 5 hurt spheres (spine, head, hips,
    2 thighs) and a bigger strike radius. Never merged; main kept
    the 2-sphere shape. Its sphere list was the seed for the
    segment list below, extended to the full body.
  - Branch `hitfx/tekken-hit-detection`: hit-FX lane, no hurt
    cylinders (last commit 2026-10-22, merge into branch).
- **Conclusion: Claude's Lane C hitbox/hurtbox model is UNAVAILABLE
  in the repo (unmerged branch, local work, or never landed — the
  repo cannot distinguish those, and this lane does not assume).**
  The geometry below is therefore a RE-DERIVATION from live data,
  not a wiring of Lane C. Nothing in it is copied from an assumed
  Lane C file.

## 2. What was actually broken on main (measured, not assumed)

On main before this lane, `fighter.js` `getHurtboxes()` returned
exactly two spheres (Spine1 r=0.58, Head r=0.34) and `game.js`
`_resolveCombat` tested only `hurts.slice(0, 1)` — the spine sphere.
The range fallback (`inReach`/`moveReach`) was the real contact
authority, and it required `hurts.length > 0`. Consequences:

1. **A defender whose rig lacked the `Spine1`/`Head` bone names
   returned ZERO hurtboxes**, so the range fallback disabled itself
   and every strike whiffed against that fighter at any distance.
   Foreign/Bip001 rigs (Iori, Deathfang carry Bip001 names, which
   `assets.js` does not rename) are the known case; any future
   non-Mixamo rig is the same bug.
2. **A hitbox was one sphere at the weapon bone's current point.**
   A fast limb could step past a hurt sphere between 120 Hz ticks,
   and the sphere's centre was the fist/foot endpoint only — the
   rest of the limb did not count.
3. **'both'-limb moves swept only the right hand.** 275 Pantera
   moves carry `limb: 'both'`; the old `_weaponBone()` fell through
   to `RightHand` for all of them.
4. **Hit levels were wrong for 206 Pantera moves.** They carry no
   top-level `hit_level` and no decoded `hit_words` entry, so
   `hitWordFor` returned `undefined` and `fighter.js` defaulted
   them to mid: highs hit crouchers, lows were unblockable by
   crouch guard. (Over-hits, not whiffs — but the same
   posture-gating code this lane touches, so it is fixed here.)
5. **Reaction selection was unwired.** PR #1003's doc says "the
   lead agent wires it into fighter.js"; no runtime file referenced
   `reactions.json` or the packs. Hitstun played one generic `hit`
   clip for every hit.

## 3. What this lane implements

### Files

| File | What |
|---|---|
| `game/js/hitbox.js` (new, pure) | 14 hurt capsules, weapon segments, segment-segment distance, swept test, root-anchored fallback capsules |
| `game/js/t3-reaction-select.js` (new, pure) | HitSelectReaction pick over the PR #1003 tables |
| `game/js/fighter.js` (edited) | `getHitbox` (swept segments), `getHurtboxes` (14 capsules + fallback), `_pickReaction`, attack-start travel reset, hitstun `react:` preference |
| `game/js/game.js` (edited) | `_resolveCombat`: geometry OR range, all 14 segments, hit segment recorded |
| `game/js/combat-core.js` (edited) | `hitWordFor`: top-level, then T7, then T8 level; parentheses stripped |
| `test/hitbox.test.mjs` (new) | Simulation tests (see §5) |

### Hurtbox: 14 capsules from LIVE bones

`HURT_SEGMENTS` (hitbox.js): head (Neck→Head), chest
(Spine1→Spine2), abdomen (Spine→Spine1), pelvis (Hips→Spine),
upper/fore arm x2, thigh/shin/foot x2. Endpoints are the posed
bone world positions of the clip actually playing (T3 row clip or
procedural layer) — never guessed positions. Radii are the one
approximated layer: body-thickness capsules in metres for the
game's gated 1.5–2.2 m fighters, documented in the module header.
A segment whose bone is missing uses its root-anchored twin
(`fallbackHurts`, facing-aware, crouch lowers the head zone by
0.55 m); a live, hittable defender now always returns 14 segments.
`band` (high/mid/low) is a REPORT label (which zone was hit), not
a filter — posture/level gating stays in `canBeHitBy` (decoded T3
hit words), so a mid against a croucher still connects via the
range path even when the geometry only grazes the lowered torso.

### Hitbox: swept segments, not a point sphere

Per active frame, `getHitbox()` returns the weapon limb's segment
(elbow→fist, knee→foot; both arms for `limb: 'both'`) plus the
weapon point's travel segment (previous frame → this frame), with
radius 0.22 (strikes), 0.95 (grabs, unchanged), 1.0 (Soul Surge,
unchanged). `testSweptHit` runs the exact segment-segment capsule
test (Ericson) of both segments against all 14 hurt capsules and
returns the closest hit segment. The old 0.5 strike sphere is
replaced by a 0.22 capsule around a ~0.35 m limb segment: the
endpoint coverage is comparable, the limb-path coverage is new,
and — critically — the range fallback is untouched, so no hit the
old code landed can be lost to the smaller radius. Geometry can
only ADD hits (e.g. a fully extended fist past the 1.75 m jab
range class, tested in §5).

### Range fallback: kept, unchanged in formula

`moveReach`/`inReach` (combat-core) still encode Tekken range
classes from move limb + heavy/launch + advancing input
(jab 1.75, kick 1.95, +0.25 advancing, +0.30 heavy/launch, throw
1.7, body separation 1.45). It covers fighters whose animation
does not extend the limb (the documented T-pose case). The
`hb.reach / moveReach(move, '')` ratio in `game.js` is preserved
and now commented: it carries the advancing bonus that a bare
`moveReach(move, '')` call would drop.

### Hit words: decoded first, T7/T8 second, mid last

`fighter.js` precedence is unchanged: `ms.hit_words` (decoded T3)
first. `hitWordFor` (the fallback) now also reads
`mv.t7.hit_level` and `mv.t8.tgt`, with parenthesised annotations
stripped ('mid (TC)' → mid, not a throw misread). Pantera hit-word
coverage rises from 667/873 (decoded only) to 708/873; the
remaining 165 moves (specials, strings, T3-merge strikes with no
level in the moveset JSON) still default to mid, exactly as
before — see §6 for the row-word follow-up that would cover them.

### Reactions: selection wired, clip playback pending

`receiveHit` now computes `_reactionSel` via
`t3-reaction-select.js` (guard → air → down → counter → quadrant,
with the class 1/3 and class-2-airborne/down gates and the close
override, per `docs/anim/T3-REACTIONS.md`) whenever
`globalThis.WH_T3_REACTIONS` (parsed `reactions.json`) is present,
for both blocked and unblocked hits. `_animate` plays a
`react:<slot>` action when one exists, else the generic `hit`
clip. No loader sets that global yet, and no pack clip plays yet:
the packs are ~6.5 MB per bank and need a lazy per-fight loader
lane (see §6). This lane does NOT claim reaction clips play.

### Damage / stun / block: unchanged

`receiveHit` damage (MOD-scaled), counter-hit, juggle scaling,
block (12% chip, block stun from T8 advantage or default),
hitstop, throw-lock and KO paths are untouched. This lane changes
WHEN contact is detected, not what contact does.

## 4. Buttons

Docs and comments use LP1/RP2/LK3/RK4 (owner directive
2026-10-24): LP1 = Tekken 1, RP2 = Tekken 2, LK3 = Tekken 3,
RK4 = Tekken 4. Data files keep their 1/2/3/4 keys.

## 5. Verification (simulation, not code inspection)

`node test/hitbox.test.mjs` — 19 checks, all passing on
2026-10-24 (mirror of main + this lane, Node 24):

- Pure geometry: segment-segment distances (parallel, crossing,
  degenerate), travel-crossing hit vs endpoint-only miss,
  closest-segment selection, legacy sphere shape, fallback
  capsules (14, facing mirror, crouch drop).
- `hitWordFor`: old cases preserved; T7 'mid (TC)' → mid,
  'low' → low, 'high, mid' → mid, '(Special) (TJ)(JGS)' →
  undefined; top-level wins over T7.
- Real `Fighter.prototype` methods with stub bones:
  `getHurtboxes` = 14 on a rigged fighter AND on a boneless rig
  (was 0); `getHitbox` LP1 = 1 limb segment + travel on the 2nd
  call, `both` = 2 segments, startup = null; `canBeHitBy` high
  whiffs croucher / mid hits croucher; `receiveHit` unguarded
  (front record) vs guarded (guard record) pick different slots.
- Contact decisions: Pantera LP1 hits at 1.45 m, whiffs at 3.5 m;
  a fully extended fist connects at 1.90 m (past the 1.75 range
  class, geometry path); f,F+2 (the f,f+RP2 analogue, reach 2.30)
  hits at 2.10 m; low (d+3) hits a croucher; high whiffs a
  croucher (posture-whiff).
- Pantera data: LP1/RP2/LK3/RK4 limbs, f,F+2 out-reaches LP1,
  hit-word coverage 708/873.
- Real `Game.prototype._resolveCombat` (headless import, stubbed
  game object): LP1 at 1.45 m damages the defender and sets
  `hasHit`. In the CI sparse checkout this section skips with a
  NOTE (packages/creation-suite is not in the sparse list); the
  gate-order-identical section above it always runs.
- Regression: `node test/combat-contact.test.mjs` still passes
  (Pantera subset in the mirror: 395 moves, 11 strings, 0 fails).
- NOT verified here (needs the live browser, which a subagent
  cannot drive): playing the deployed build on a phone, portrait,
  like the owner. That step is handed back to the parent agent.

## 6. What remains UNMAPPED / open

1. **Reaction pack clip playback.** Needs a lazy loader for
   `reactions.pack.json` per fighter bank (~6.5 MB each) plus
   `decodePackRow` → `react:<slot>` actions. Selection is done;
   playback is a separate lane. Do not claim otherwise.
2. **Row attack words for the 165 uncovered Pantera moves.**
   `hit_frames.json` per bank carries `[first, last, frames,
   attack_word, throw]` per row; wiring that word into
   `getRealMove` (which is synchronous while the bank data loads
   async) would cover strikes like `d+1`, `b+4`, `BT.3` that have
   no level in the moveset JSON. They default to mid today.
3. **Live-browser play verification** (see §5): phone portrait,
   Pantera LP1 / f,f+RP2 / crouch lows against every roster
   family, especially Bip001-rig fighters (Iori, Deathfang) and
   any fighter whose rig lacks Mixamo names.
4. **Capsule radii are approximations** (see §3). They are
   body-thickness values, not decoded T3 data — T3's own
   collision representation was not decoded in this lane, and no
   source in the repo currently holds it. If a future teardown
   decodes T3 hurt volumes, the radii table in `hitbox.js` is the
   single place to replace.
5. **Claude's Lane C model** remains unlocated (see §1). If it
   surfaces (branch, PR, or local work), its 14-cylinder table
   should be diffed against `HURT_SEGMENTS` before any merge —
   not assumed identical.
