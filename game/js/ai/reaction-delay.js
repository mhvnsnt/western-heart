/* ============================================================
   WESTERN HEART — Reaction Delay (the human-fairness model)
   FightingICE lesson (competition rules, 2017+): "the information
   sent to AIs will have a delay of 15 frames... to simulate human
   response time." A CPU that decides from this-frame's exact game
   state reads the player's inputs — inhuman, unbeatable, unfun.

   So the brains DECIDE from a delayed snapshot while the body
   EXECUTES on live data:

     live snapshot ──▶ ReactionDelay.push() ──▶ brains decide
                          (every tick)              from N-frames-ago
                                                    (the human view)

   Tekken-style difficulty curve: a rookie sees the fight a full
   15 frames late (FightingICE's number); a maxed-out boss still
   waits ~8 frames. The floor keeps the AI humanlike — it can never
   become an input-reader, no matter the tier.

   Pure logic: no fighter handles, no DOM, no THREE. The controller
   owns pushing snapshots; the buffer owns the delay math.
   ============================================================ */

/**
 * Ring buffer of snapshots. push() every tick; delayed() returns the
 * snapshot from `delayFrames` ticks ago (or the oldest held when the
 * buffer hasn't filled yet — no null-decision at round start).
 */
export class ReactionDelay {
  constructor(delayFrames = 12) {
    this._buf = [];
    this.setDelay(delayFrames);
  }

  setDelay(n) {
    this.delayFrames = Math.max(0, Math.round(n ?? 12));
  }

  push(snap) {
    this._buf.push(snap);
    const over = this._buf.length - (this.delayFrames + 1);
    if (over > 0) this._buf.splice(0, over);
  }

  /** The snapshot the brains are allowed to see. */
  delayed() {
    if (!this._buf.length) return null;
    const i = this._buf.length - 1 - this.delayFrames;
    return this._buf[i >= 0 ? i : 0];
  }

  /** The true current snapshot (execution layer only). */
  live() {
    return this._buf.length ? this._buf[this._buf.length - 1] : null;
  }

  reset() {
    this._buf.length = 0;
  }
}

/**
 * Tekken-style difficulty curve for the human-delay model.
 * diff 0..1 (arcade ladder / rank-battle tier). 15f at rookie —
 * FightingICE's human-reaction number — tightening to 8f at max.
 * The floor is the point: even the hardest CPU reacts like a person.
 */
export function delayFramesForDifficulty(diff) {
  const d = Math.min(1, Math.max(0, diff ?? 0.5));
  return Math.round(15 - d * 7);
}
