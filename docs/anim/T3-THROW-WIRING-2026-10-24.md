# Tekken grapple wiring (2026-10-24)

Owner complaint, verbatim intent (2026-10-24 19:09 CDT): the grapple
animation played even when the grapple did not connect; the reach
should play whether it connects or not; if it connects, the next part
should play automatically, not because of a button press; the opponent
must play the receiving grapple animation when it connects, like
Tekken. Owner reinforcement (19:11 CDT): do not hook it up with
guesses — use the stuff from the files, how it is hooked up in the
files.

## The state machine (now in code)

```
ATTEMPT (LP1+LK3, RP2+RK4, or a command throw)
  -> the move's own ATTEMPT row clip plays (fighter.js
     _attackClipPlan, same as any move). It plays whether the
     grab connects or not. A whiff ends in neutral: no throw
     execution, no receiver clip. Nothing about the attempt
     changed — the bug was never the reach.
  -> IF the grab hitbox touches the opponent hurtbox during the
     attempt's active window (the PR #1005 swept-capsule system,
     unchanged):
       AUTOMATICALLY, with no further button press:
         * the file's throw pair is selected (below),
         * the thrower plays the thrower's slot clip,
         * the victim plays the paired victim slot clip,
         * both clips start on the same frame, on the shared
           root frame anchored at the victim's root
           (docs/anim/T3-REACTIONS.md "Shared root frame"),
         * the break window is the first frames of those same
           clips (there is no separate lock in T3),
         * damage lands at the file's damage_frames.
       A correct break input inside the window starts the file's
       escape pair with roles swapped. Outside the window the
       throw lands. After the pair, the thrower returns to
       neutral and the victim continues with the victim slot's
       `next` chain (lying, then get-up) via the knockdown state.
  -> IF the file has no pair for this throw, the old 0.3 s
     break lock + procedural lift/slam runs instead, and the
     connect is logged `[WH-THROW] ... no file pair (reason)`.
     That is the UNMAPPED fallback, not a pairing.
```

## Where the pair comes from (file wiring, no guesses)

New module `game/js/t3-throw.js` (pure, headless-testable) implements
`docs/anim/T3-REACTIONS.md` "Throws" over
`game/assets/anim/t3/reactions.json`:

1. Attempt row — (a) the attempt clip plan's own `row:<n>` name,
   i.e. the file row the reach actually played; else (b) the
   file's `throw_inputs` row for an EXACT `LP+LK` / `RP+RK` chord
   (standing slot 3, crouching slot 40, cond 36 = thrower's back
   turned). Exact match only: `1+LP+LK` is a different attempt
   (King row 277, a crouching throw) from neutral `LP+LK`
   (row 273), and a substring match would wire the wrong one.
   A generic `grab` action has no row of its own and is NOT
   mapped through `throw_inputs` — its chord is ambiguous.
2. Branch — walk `throw_attempts[<row>].branches` in BranchFind
   order; take the first branch whose situation matches and whose
   distance is `<= param` (param in T3 units × the pack's
   `anchor_mm_to_rig_m` = metres). Situation codes: standing
   front 2 / back 3 / +X side 4 / −X side 5, crouching 6–9, lying
   10–13 (14–17 lying the other way), thrower's back turned
   18/19, plus the `0x14`–`0x17` aliases that accept the standing
   or crouching code of a quadrant.
3. Throw — `throws.find(slot === branch.throw_slot)`: damage,
   `damage_frames`, `victim_slot`, `victim_frames`, `breaks[]`
   (`input` + window in victim-move frames + `escape_slot`),
   `next`.
4. Clips — `resolveThrowClips` (DivmotMergeSharedSlots): the
   victim clip comes from the victim's own bank when it defines
   the victim slot, else the thrower's bank. When
   `defined === false` (Forest Law's standard throws) the thrower
   clip itself comes from the victim bank's throw of the same
   slot. `t.defined` victims with a zero `+0x32` (Bosconovitch
   reversals) play slot 0 per the doc; that path is covered by
   the same resolver (the slot-0 clip is in the pack).

## What the runtime loads (the missing lane)

`game/js/t3anims.js` gains `loadReactionPack` /
`getReactionPack` / `getReactionClip`: a bank's
`reactions.pack.json` is cached at fight start and its clips are
decoded ONE SLOT AT A TIME on demand (decoding all ~568 clips up
front would triple fight-load clip memory on a phone, on top of
the row clips `loadT3Clips` already builds) — the same decode
`loadT3Clips` uses for `rows.pack.json` `row:<n>` clips, keyed by
slot (`0xaeb`). Turned banks get the same 180° turn as their row
clips. `main.js` loads `reactions.json` (which also fills
`globalThis.WH_T3_REACTIONS`, the table `_pickReaction` already
reads) and both fighters' reaction packs at fight start,
inside a non-fatal try/catch — a pack failure keeps the legacy
lock, it never blocks the fight. `fighter.js` retargets only the
two slots of a pair, on connect, onto each fighter's own rig
(the same lazy pattern as row clips), as actions
`throw:0x…` (thrower) and `victim:0x…` (victim).

## Decisions, stated (not silently mixed)

- **Connect test stays the WH hitbox system.** The file's branch
  evaluation happens at the attempt entry frame; WH moves do not
  run on T3 stream frames, they run on WH startup/active frames
  whose active window the attempt clip plan already maps from
  the file's decoded active window. So the hitbox touching during
  the active window IS the file's active-window test, and branch
  selection then picks the variant and the paired clips. The
  distance gate (`param`) is still applied at selection.
- **Damage amount stays WH, timing comes from the file.** The
  throw is a WH move with a WH damage value (MOD damage
  decision, 2026-10-24); only `damage_frames` timing is taken
  from the file. Escape pairs are not WH moves, so they use the
  file damage scaled T3 170 HP → WH 100 HP, the scaling
  `fighter.js` documents for T3 frame data.
- **Quadrant is a documented WH approximation.** WH fights are
  x-axis fights with transient z separation after a sidestep.
  The quadrant uses the same convention `_pickReaction` already
  uses (attacker ahead of the victim's facing = front, behind =
  back, otherwise the world-z side). It is not a file value, and
  it only chooses between the file's own branches — it never
  invents a throw.
- **Posture** is the victim's WH state: `crouch` → crouching,
  `knockdown` → lying, otherwise standing. Airborne victims are
  already excluded by the grab hit path (throws whiff airborne).
- **Shared frame vertical:** the clip's own hip motion (`ry`
  via retarget, as for every T3 clip); only x/z follow the doc's
  anchor formula, at the thrower's anchor scale for both clips.
  Body-vs-body pushout is skipped while a pair runs, or it would
  fight the shared frame every frame.

## Worked example (King = Pantera, verified by test)

- LP1+LK3 front, standing, 1.0 m: attempt row 273 → branch cond 2
  → throw slot `0xaeb` (2795), damage 35 at frame 61 of 131,
  victim slot `0xbca` (3018, 130 frames), break LP1 frames 1–15,
  escape slot 2898. Victim clip from King's bank (Jin's bank does
  not define `0xbca`).
- RP2+RK4 front: attempt row 274 → slot 2797.
- Same attempt from the side → slot 2798; from behind → 2800.
- Same attempt crouching → no branch matches → UNMAPPED for that
  situation (the legacy lock runs; the file simply has no
  crouching variant of attempt 273 — its crouching variants are
  attempts 275/276, reached by their own inputs).
- Beyond 1536 T3 units (~1.27 m at King's scale) → no branch →
  the grab does not connect as a pair.

## Verification

- `node --test test/t3-throw.test.mjs` — 8 tests, all against the
  real `reactions.json`: the two generic throws above, side/back
  branches, the crouch non-match, the distance gate, the unknown
  row, the escape pair, situation/alias codes, shared-frame math.
- Batch sweep over all 22 banks (`selectThrow`, front/standing/
  1.0 m): 223 of 238 attempt rows select a file throw and every
  one resolves both clip banks. The 15 non-selects are all
  correct per file: crouch-only (cond 6), lying-only (10–17),
  back-only (cond 3), and back-turned-only (18/19) attempts —
  a front/standing test must not select them.
- Syntax: `node --check` passes on all five touched JS files.
- NOT yet verified: playing it on the live build. The paired
  clips, the shared-frame drive, and the break window must be
  eye-checked by playing (reach on whiff, full pair + receiver
  on connect, break inside the window, no execution on whiff)
  before anyone calls this fixed.

## Files

- NEW `game/js/t3-throw.js` — pure selection + shared-frame math.
- `game/js/t3anims.js` — reaction-pack loader (surgical addition).
- `game/js/fighter.js` — pair resolution, binding, start, break,
  pair clock, shared-frame drive, paired clip playback; legacy
  lock/procedural exec kept as the UNMAPPED fallback.
- `game/js/game.js` — do not overwrite a bound pair with
  `startThrowing`; break prompt reads the pair's break input;
  lock-resolution loop skips paired fighters.
- `game/js/main.js` — fight-start load of throw tables + packs.
- NEW `test/t3-throw.test.mjs`.
- This doc. No other files touched.
