/* ============================================================
   WESTERN HEART — hitbox.js (pure hit / hurt geometry)
   Headless-testable: no THREE, no window, no game state. The
   fight loop (fighter.js builds the segments from live bones,
   game.js resolves them) only calls the pure tests here.

   WHY THIS EXISTS (owner playtest 2026-10-24: "Hitbox stuff and
   hurtbox stuff is not making contact right. A lot of contacts
   not being made during fight"):
   - Before, getHurtboxes() returned TWO spheres (Spine1 + Head)
     and game.js only ever tested hurts[0]. A defender whose rig
     lacked those two bone names returned NO hurtboxes at all, so
     the range fallback (which requires hurts.length > 0) silently
     disabled itself and EVERY strike whiffed against that fighter.
   - Before, a hitbox was ONE sphere at the weapon bone's current
     point. A fast limb could step past a hurt sphere between
     120 Hz ticks, and 'both'-limb moves (275 Pantera moves) only
     ever swept the RIGHT hand.

   WHAT IT IS NOW:
   - Hurtbox: 14 capsules (segments + radii) over the defender's
     LIVE bone positions — head, chest, abdomen, pelvis, upper /
     fore arm x2, thigh / shin / foot x2. Positions are never
     guessed: they are the posed bones of the clip actually
     playing (T3 row clip or procedural layer). Radii are the one
     approximated layer: body-thickness capsules in metres for the
     game's ~1.5-2.2 m fighters (assets.js playable gate), not
     per-move numbers.
   - Hitbox: a SWEPT segment pair — the weapon limb's segment
     (elbow->fist, knee->foot) at this frame, plus the fist/foot
     travel segment (previous frame -> this frame). A hit counts
     when either segment comes within (limb radius + hurt radius)
     of any hurt capsule. Segment-segment distance is the exact
     capsule test (Ericson), not a point sample.
   - The range fallback in game.js (combat-core moveReach /
     inReach, Tekken range classes from move limb + class +
     advancing input) is KEPT as a second path for fighters whose
     animation does not extend the limb (the documented T-pose
     case). Geometry can only ADD hits the fallback missed; it
     can never remove a fallback hit. Posture / hit-level gating
     still lives in fighter.js canBeHitBy (decoded T3 hit words),
     never in this module's band labels: `band` is a report label
     (which body zone was hit), not a filter.

   Buttons in docs/comments use LP1/RP2/LK3/RK4 (owner directive
   2026-10-24): LP1 = Tekken 1, RP2 = Tekken 2, LK3 = Tekken 3,
   RK4 = Tekken 4.
   ============================================================ */

/* 14 hurt capsules. a/b are Mixamo / WH-Canonical-22 bone names
   (the names fighter.js + assets.js already use). A segment whose
   endpoint bone is missing is replaced by its fallback twin from
   FALLBACK_HURTS (fighter.js), never dropped silently. */
export const HURT_SEGMENTS = [
  { id: 'head',    a: 'Neck',        b: 'Head',        r: 0.18, band: 'high' },
  { id: 'chest',   a: 'Spine1',      b: 'Spine2',      r: 0.34, band: 'high' },
  { id: 'abdomen', a: 'Spine',       b: 'Spine1',      r: 0.32, band: 'mid' },
  { id: 'pelvis',  a: 'Hips',        b: 'Spine',       r: 0.30, band: 'mid' },
  { id: 'upperArmL', a: 'LeftArm',   b: 'LeftForeArm', r: 0.16, band: 'mid' },
  { id: 'foreArmL',  a: 'LeftForeArm', b: 'LeftHand',  r: 0.14, band: 'mid' },
  { id: 'upperArmR', a: 'RightArm',  b: 'RightForeArm', r: 0.16, band: 'mid' },
  { id: 'foreArmR',  a: 'RightForeArm', b: 'RightHand', r: 0.14, band: 'mid' },
  { id: 'thighL',  a: 'LeftUpLeg',   b: 'LeftLeg',     r: 0.20, band: 'mid' },
  { id: 'shinL',   a: 'LeftLeg',     b: 'LeftFoot',    r: 0.16, band: 'low' },
  { id: 'footL',   a: 'LeftFoot',    b: 'LeftToeBase', r: 0.13, band: 'low' },
  { id: 'thighR',  a: 'RightUpLeg',  b: 'RightLeg',    r: 0.20, band: 'mid' },
  { id: 'shinR',   a: 'RightLeg',    b: 'RightFoot',   r: 0.16, band: 'low' },
  { id: 'footR',   a: 'RightFoot',   b: 'RightToeBase', r: 0.13, band: 'low' },
];

/* Weapon limb segments, by move limb (fighter.js attackLimb).
   'both' (chords like d+1+2, and double-limb specials) sweeps
   BOTH arms — the old code swept only the right hand. */
export const WEAPON_SEGMENTS = {
  armL: [{ a: 'LeftForeArm', b: 'LeftHand' }],
  armR: [{ a: 'RightForeArm', b: 'RightHand' }],
  legL: [{ a: 'LeftLeg', b: 'LeftFoot' }],
  legR: [{ a: 'RightLeg', b: 'RightFoot' }],
  both: [{ a: 'LeftForeArm', b: 'LeftHand' }, { a: 'RightForeArm', b: 'RightHand' }],
};

/* Capsule radius around a weapon limb segment, metres. Strikes use
   the limb's own thickness; grabs keep the old generous sphere
   (0.95) and Soul Surge keeps 1.0, so neither path gets stricter
   than the behaviour the game already shipped. */
export const LIMB_RADIUS = { strike: 0.22, grab: 0.95, surge: 1.0 };

/* ---- vector helpers (plain {x,y,z} objects; no THREE) ---- */
const sub = (a, b) => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
const dot = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;
const clamp = (v, lo, hi) => (v < lo ? lo : v > hi ? hi : v);

/* Squared distance between segments p1-p2 and p3-p4 (Ericson,
   Real-Time Collision Detection 5.1.8). Degenerate (zero-length)
   segments degrade to point tests, so head-style spheres work. */
export function segSegDist2(p1, p2, p3, p4) {
  const d1 = sub(p2, p1), d2 = sub(p4, p3), r = sub(p1, p3);
  const a = dot(d1, d1), e = dot(d2, d2), f = dot(d2, r);
  let s, t;
  if (a <= 1e-12 && e <= 1e-12) return dot(r, r);
  if (a <= 1e-12) { t = clamp(f / e, 0, 1); return dot(sub(r, { x: d2.x * t, y: d2.y * t, z: d2.z * t }), sub(r, { x: d2.x * t, y: d2.y * t, z: d2.z * t })); }
  const c = dot(d1, r);
  if (e <= 1e-12) { s = clamp(-c / a, 0, 1); const q = sub(r, { x: d1.x * s, y: d1.y * s, z: d1.z * s }); return dot(q, q); }
  const b = dot(d1, d2), denom = a * e - b * b;
  s = denom > 1e-12 ? clamp((b * f - c * e) / denom, 0, 1) : 0;
  t = (b * s + f) / e;
  if (t < 0) { t = 0; s = clamp(-c / a, 0, 1); }
  else if (t > 1) { t = 1; s = clamp((b - c) / a, 0, 1); }
  const q = { x: r.x + d1.x * s - d2.x * t, y: r.y + d1.y * s - d2.y * t, z: r.z + d1.z * s - d2.z * t };
  return dot(q, q);
}

/* One hurt capsule, in the shape fighter.js returns: midpoint
   x/y/z (backward compatible with the old sphere readers) plus
   the segment endpoints, radius, band and id. */
export function hurtCapsule(p) { return p; }

/* Test a swept hitbox against hurt capsules.
   hitbox: { segments: [{ax,ay,az,bx,by,bz}...], travel: {ax..bz} | null, r }
     segments = this frame's weapon limb segment(s)
     travel   = previous-frame weapon point -> this-frame weapon point (may be null on frame 1)
   hurts: [{x1,y1,z1,x2,y2,z2,r,band,id, x,y,z}...]
   Returns { hit, segment, dist } with the CLOSEST hurt segment, or { hit: false }. */
export function testSweptHit(hitbox, hurts) {
  if (!hitbox || !hurts || !hurts.length) return { hit: false };
  const segs = [];
  for (const s of (hitbox.segments || [])) segs.push(s);
  if (hitbox.travel) segs.push(hitbox.travel);
  // Legacy shape (single sphere x/y/z/r, no segments): one degenerate segment.
  if (!segs.length && Number.isFinite(hitbox.x)) {
    segs.push({ ax: hitbox.x, ay: hitbox.y, az: hitbox.z, bx: hitbox.x, by: hitbox.y, bz: hitbox.z });
  }
  if (!segs.length) return { hit: false };
  let best = null;
  for (const s of segs) {
    const p1 = { x: s.ax, y: s.ay, z: s.az }, p2 = { x: s.bx, y: s.by, z: s.bz };
    for (const h of hurts) {
      const q1 = { x: h.x1, y: h.y1, z: h.z1 }, q2 = { x: h.x2, y: h.y2, z: h.z2 };
      const rr = hitbox.r + h.r;
      const d2 = segSegDist2(p1, p2, q1, q2);
      if (d2 <= rr * rr) {
        const dist = Math.sqrt(d2);
        if (!best || dist < best.dist) best = { hit: true, segment: h, dist };
      }
    }
  }
  return best || { hit: false };
}

/* Root-anchored fallback hurt capsules for a rig that lacks the
   canonical bones (foreign / Bip001 rigs): the defender is NEVER
   left with zero hurtboxes. World-space, facing-aware (x offsets
   flip with facing), in metres above root Y. `crouch` lowers the
   torso/head zone the way a crouch pose does (measured from the
   T3 crouch-hold clip's hip drop, ~0.55 m, not a tuned guess: the
   crouching head sits just above the standing pelvis).
   Returns the same shape as fighter.js getHurtboxes(). */
export function fallbackHurts(root, facing, crouch) {
  const f = facing >= 0 ? 1 : -1;
  const y = root.y || 0, x = root.x || 0, z = root.z || 0;
  const drop = crouch ? 0.55 : 0;
  const P = (dx, y0, dz) => ({ x: x + dx * f, y: y + y0, z: z + dz });
  const seg = (id, a, b, r, band) => ({
    id, band, r,
    x1: a.x, y1: a.y, z1: a.z, x2: b.x, y2: b.y, z2: b.z,
    x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, z: (a.z + b.z) / 2,
  });
  const head = P(0.05, 1.62 - drop, 0), neck = P(0.02, 1.45 - drop, 0);
  const chest = P(0, 1.28 - drop, 0), belly = P(0, 1.02 - drop * 0.5, 0);
  const hips = P(0, 0.92, 0);
  const shL = P(0.05, 1.38 - drop, -0.24), elL = P(0.12, 1.08 - drop, -0.30), haL = P(0.18, 0.82 - drop, -0.32);
  const shR = P(0.05, 1.38 - drop, 0.24), elR = P(0.12, 1.08 - drop, 0.30), haR = P(0.18, 0.82 - drop, 0.32);
  const hipL = P(0, 0.90, -0.14), kneeL = P(0.02, 0.48, -0.15), ankL = P(0.05, 0.10, -0.15), toeL = P(0.16, 0.06, -0.15);
  const hipR = P(0, 0.90, 0.14), kneeR = P(0.02, 0.48, 0.15), ankR = P(0.05, 0.10, 0.15), toeR = P(0.16, 0.06, 0.15);
  return [
    seg('head', neck, head, 0.18, 'high'),
    seg('chest', belly, chest, 0.34, 'high'),
    seg('abdomen', hips, belly, 0.32, 'mid'),
    seg('pelvis', hips, hips, 0.30, 'mid'),
    seg('upperArmL', shL, elL, 0.16, 'mid'),
    seg('foreArmL', elL, haL, 0.14, 'mid'),
    seg('upperArmR', shR, elR, 0.16, 'mid'),
    seg('foreArmR', elR, haR, 0.14, 'mid'),
    seg('thighL', hipL, kneeL, 0.20, 'mid'),
    seg('shinL', kneeL, ankL, 0.16, 'low'),
    seg('footL', ankL, toeL, 0.13, 'low'),
    seg('thighR', hipR, kneeR, 0.20, 'mid'),
    seg('shinR', kneeR, ankR, 0.16, 'low'),
    seg('footR', ankR, toeR, 0.13, 'low'),
  ];
}
