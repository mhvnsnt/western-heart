/* GRAB-HOLD + RAGDOLL BEHAVIOUR (clean-room, 2026-10-23).
   Design study: a physics brawler's per-hand grip / limb-target / struggle /
   throw-release model. Reimplemented from the idea; no code copied. Drives
   the existing active ragdoll via plain impulses — works with physics.js. */
export const LIMBS = ['head', 'torso', 'armL', 'armR', 'legL', 'legR'];
export class GrabHold {
  constructor(opts = {}) { this.maxGrip = opts.maxGrip ?? 1; this.drain = opts.drain ?? 0.35; this.hands = { L: null, R: null }; this.grip = { L: 0, R: 0 }; }
  grab(hand, target, limb = 'torso') {
    if (!LIMBS.includes(limb) || this.hands[hand]) return false;
    this.hands[hand] = { target, limb }; this.grip[hand] = this.maxGrip; return true;
  }
  /* struggle: victim mashing (0..1) drains grip faster; both hands = 40% slower drain */
  update(dt, struggle = 0) {
    const both = this.hands.L && this.hands.R; const out = [];
    for (const h of ['L', 'R']) if (this.hands[h]) {
      this.grip[h] -= dt * this.drain * (1 + 2 * struggle) * (both ? 0.6 : 1);
      if (this.grip[h] <= 0) { out.push({ hand: h, ...this.hands[h], reason: 'broken' }); this.hands[h] = null; this.grip[h] = 0; }
    }
    return out;
  }
  holding() { return !!(this.hands.L || this.hands.R); }
  /* throw: release all, impulse scales with grip left and limb leverage */
  release(dir = { x: 1, y: 0.5, z: 0 }, power = 8) {
    const lev = { head: 1.1, torso: 1, armL: .8, armR: .8, legL: 1.25, legR: 1.25 };
    const res = [];
    for (const h of ['L', 'R']) if (this.hands[h]) {
      const k = power * (0.4 + 0.6 * this.grip[h]) * lev[this.hands[h].limb];
      res.push({ target: this.hands[h].target, limb: this.hands[h].limb, impulse: { x: dir.x * k, y: dir.y * k, z: dir.z * k } });
      this.hands[h] = null; this.grip[h] = 0;
    }
    return res;
  }
}
/* Apply to a cannon-es/jolt-style body if present; no-op otherwise. */
export function applyRelease(results, bodyOf) {
  for (const r of results) { const b = bodyOf && bodyOf(r.target, r.limb); if (b && b.applyImpulse) b.applyImpulse(r.impulse); }
  return results.length;
}
