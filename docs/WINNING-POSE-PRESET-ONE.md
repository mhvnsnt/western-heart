# Winning Pose Style — Preset One (2026-10-22)

**Status:** OWNER-APPROVED baseline. Do not change without owner approval.
**Owner's verdict:** "I like how ours does it better" than Tekken's cinematic cuts.

## The Feel
When a fighter wins, the camera STAYS where it was during the fight. No cuts, no cinematic angles, no zoom-ins. You see the whole fight, the KO lands, and the winner does their pose right there in the same frame. It feels more immersed — you're still in the fight, not watching a movie.

This is deliberately DIFFERENT from Tekken, which does focused cutscene-style camera work on victory. Ours is better (owner's call).

## Exact Trigger Logic

**File:** `game/js/game.js`
- Loser's HP hits 0 → `_knockout(dir)` → enters `'ko'` state, launched (vx = dir * 5.5, vy = 6), stun locked at 999
- Winner → `victory()` → enters `'victory'` state (guard: only if not dead)
- UI banner shows "K.O.", round wins increment, HUD updates

**File:** `game/js/fighter.js`
- `victory()`: `if (!this.dead) this._enter('victory')`
- Victory animation: `case 'victory': this._playT3('win', { loop: true })` — loops indefinitely
- KO animation: `case 'ko'` — lean back, play 'ko' clip once

## Camera Behavior
**File:** `game/js/scene.js` — dynamic fighting camera

The camera has NO victory-specific behavior. It continues normal fight tracking. There are no camera cuts, zoom-ins, angle changes, or cinematic sequences. The camera simply stays panned as it was. This is the defining characteristic of Preset One.

## Timing
- Victory triggers IMMEDIATELY on KO (same frame as the knockout call)
- No delay, no slow-mo, no freeze-frame before the pose
- The 'win' animation loops indefinitely until the next round starts or match ends
- Round transition handled by `_afterRound()` in game.js

## Why This Matters
If future teardown integration brings in Tekken's cinematic victory camera system, THIS document is the reference for what ours looked like before. The owner's preference is clear: our immersive no-cut style beats Tekken's focused cutscene style.

**To restore:** ensure no camera overrides exist in the victory path, `victory()` enters the looping 'win' state, and the scene camera continues normal fight tracking.
