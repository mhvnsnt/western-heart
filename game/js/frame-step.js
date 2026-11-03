/* frame-step.js — fixed-step catch-up guard for the fight loop (2026-11-02).
 *
 * The fight loop runs the sim at FIXED_DT = 1/120 s and drains the
 * accumulated frame time in a while loop (game.js _loop). With NO cap,
 * any hitch — a slow frame, a reaction-slot decode, a GC pause, the
 * frame right after hitstop ends — makes the NEXT frame run extra
 * sim steps (a 50 ms frame is 6 steps at 1/120), which makes that
 * frame even longer: the classic spiral of death. On a phone that
 * reads as visual lag and input lag, because inputs are only read
 * inside _update, so a long frame delays the next input read too.
 *
 * This helper caps the drain: at most MAX_STEPS sim steps per render
 * frame, and any leftover accumulator is DROPPED (not carried over).
 * Dropping costs at most one frame of sim time under load; carrying
 * it over costs unbounded frame time. Held input state persists
 * across the drop (InputManager state is not queued in _update),
 * so no button press is lost — it is processed on the next frame.
 *
 * Pure (no three.js, no DOM) so node tests can drive it directly.
 */

export const MAX_FIXED_STEPS = 4;

/**
 * Drain `acc` seconds of accumulated sim time in steps of `fixedDt`.
 * Returns { steps, acc } where acc is the leftover (< fixedDt), or 0
 * when the cap was hit and the excess was dropped.
 */
export function drainFixedSteps(acc, fixedDt, maxSteps = MAX_FIXED_STEPS) {
  let steps = 0;
  while (acc >= fixedDt && steps < maxSteps) {
    acc -= fixedDt;
    steps++;
  }
  // Cap hit with time still owed: drop it. Carrying it over would
  // re-run the same excess on every following frame (spiral).
  if (acc >= fixedDt) acc = 0;
  return { steps, acc };
}
