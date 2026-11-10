/* t7-graph-input.js — the shared player input (input.js InputManager: keyboard AND the on-screen stick / limb
   buttons) into a fighter's T7 source graph (fighter.js t7gFeed; development integration, fighter.js
   t7GraphDevEnabled). game.js calls feedT7GraphInput once per game tick for the player's fighter instead of its WH
   command layer, and the node replay harness (test/t7-graph-adapter-pantera.test.mjs) calls the very same function,
   so the harness exercises the real path: InputManager -> this function -> Fighter.t7gFeed -> T7GraphDriver.
     stick  : the facing-relative 8-way state every tick (tekkenDirOf, the function game.js always used), u/d from their
              first frame (vertNow), so the WH tap-vs-hold sidestep / jump / crouch layer never fires;
     presses: the shared queue's limb presses and chords (the input layer's 50 ms chord window; a chord completed after
              its first limb was read arrives as the chord on a later frame, where the source tables' own one-frame
              chord rows can take it);
     held   : InputManager.held[1..4] (keyboard key-up / touch release clear it);
     double tap: the shared TekkenBuffer dash latch (WH's double-tap timing; the T7 engine's own window is not in the
              tables) -> source specials 0x8001 (f) / 0x8002 (b).
   While caught in a throw (WH engine), limb presses stay throw-break attempts. */
export function tekkenDirOf(inp, facing) {
  const fwd = (inp.axisX || 0) * facing; // forward-positive
  const f = fwd > 0.25, b = fwd < -0.25;
  const v = inp.vertNow ? inp.vertNow() : (inp.up ? 'up' : inp.down ? 'down' : null);
  const up = v === 'up', down = v === 'down';
  if (up && f) return 'u/f';
  if (up && b) return 'u/b';
  if (up) return 'u';
  if (down && f) return 'd/f';
  if (down && b) return 'd/b';
  if (down) return 'd';
  if (f) return 'f';
  if (b) return 'b';
  return 'n';
}
const LIMBS = /^[1-4](\+[1-4]){0,3}$/;
export function feedT7GraphInput(p, inp, dt, { onThrowEscape = null } = {}) {
  const stick = tekkenDirOf(inp, p.facing);
  p.setStick(stick);
  const had = p.tekken._dash; p.tekken.noteDirection(stick, dt); const dl = p.tekken._dash;
  const q = inp.consume();
  if (p.state === 'thrown') {
    for (const act of q) if (/^[1-4](\+[1-4])?$/.test(act) && p.tryThrowBreak(act) && onThrowEscape) onThrowEscape();
    return stick;
  }
  p.t7gFeed({ dir: stick, presses: q.filter((a) => LIMBS.test(a)), held: inp.held, dashDir: dl && dl !== had ? dl.dir : null }, dt);
  return stick;
}
