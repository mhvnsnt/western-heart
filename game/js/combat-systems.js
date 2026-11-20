/* ============================================================
   WESTERN HEART — Tekken combat systems (owner pt217u + parent add-on, 2026-10-23)
   Pure, DOM-free layer over combat-core.js (#952). Builds on it, replaces nothing.
   Covers the T7/T8 combat data set by system:
     hurtboxes per bone (capsules) + pushbox, attack hitbox per limb,
     contact = hitbox/hurtbox overlap at the active frame,
     hit reactions per hit level / direction / property
       (stagger, crumple, launch, spin/screw, wall splat, floor bound,
        knockdown + wake-up), block reactions (block stun / guard break),
     throws with throw breaks (1 / 2 / 1+2), counter-hit,
     hitstop, hit-spark, camera shake and sound hooks.
   Raw T7 values stay private (__WH_PRIVATE_ASSETS); these are canon
   defaults shaped like the T7 tables and overridable per move.
   ============================================================ */
import { effectiveActive, moveReach, FRAME } from './combat-core.js';

/* ---- bodies: per-bone hurt capsules (metres, root-relative, x forward) ---- */
export const BONES = {
  head:   { y: 1.62, r: 0.13, x: 0.02 },
  neck:   { y: 1.48, r: 0.08, x: 0.0 },
  chest:  { y: 1.30, r: 0.20, x: 0.0 },
  spine:  { y: 1.08, r: 0.18, x: 0.0 },
  pelvis: { y: 0.92, r: 0.18, x: 0.0 },
  armL:   { y: 1.20, r: 0.09, x: 0.10 }, armR: { y: 1.20, r: 0.09, x: 0.10 },
  thighL: { y: 0.65, r: 0.11, x: 0.03 }, thighR: { y: 0.65, r: 0.11, x: 0.03 },
  shinL:  { y: 0.30, r: 0.08, x: 0.05 }, shinR: { y: 0.30, r: 0.08, x: 0.05 },
};
export const PUSHBOX = { halfWidth: 0.36, height: 1.75 }; // two pushboxes keep roots >= 0.72 apart
export const STATE_SCALE = { stand: 1, crouch: 0.55, air: 1, down: 0.22 };

/** Hurt capsules for a body at root x (facing +1/-1), state stand|crouch|air|down, airY lift. */
export function hurtboxes(x, facing, state = 'stand', airY = 0, scale = 1) {
  const s = (STATE_SCALE[state] ?? 1) * scale;
  return Object.entries(BONES).map(([bone, b]) => ({
    bone, x: x + facing * b.x * scale, y: b.y * s + (state === 'air' ? airY : 0), r: b.r * scale,
  }));
}

/* Hit level -> height band of the attack sphere. */
const LEVEL_Y = { h: 1.55, m: 1.15, sm: 1.0, s: 1.0, l: 0.3, sl: 0.3, t: 1.2, ub: 1.15 };
export function primaryLevel(mv) {
  const raw = String(mv.hit_level || mv.t7_hit_level || (mv.isGrab ? 't' : (String(mv.limb || '').startsWith('leg') ? 'm' : 'h')));
  const parts = raw.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
  return (parts[0] || 'm').replace(/[^a-z]/g, '') || 'm';
}

/** Attack hitbox (sphere at the limb tip) for a move at its active frame. */
export function hitbox(ax, facing, mv, notation = '', airY = 0) {
  const lv = primaryLevel(mv);
  const reach = moveReach(mv, notation);
  // limb segment from the shoulder/hip (x0) to the tip (x); contact tests the whole swept limb
  return { x0: ax + facing * 0.3, x: ax + facing * (reach - 0.12), y: (LEVEL_Y[lv] ?? 1.1) + airY, r: mv.isGrab ? 0.3 : 0.16, level: lv };
}

/** Contact: does the attack sphere overlap any hurt capsule (2-D side view)? Returns bone or null.
    Height rules: highs whiff crouchers; lows hit grounded bodies; throws whiff airborne. */
export function contact(hb, hurts, defState = 'stand') {
  if (hb.level === 'h' && defState === 'crouch') return null;
  if (hb.level === 't' && (defState === 'air' || defState === 'down')) return null;
  let best = null, bestD = Infinity;
  const lo = Math.min(hb.x0 ?? hb.x, hb.x), hi = Math.max(hb.x0 ?? hb.x, hb.x);
  for (const c of hurts) {
    const px = Math.max(lo, Math.min(hi, c.x)); // closest point on the limb segment
    const m = Math.hypot(px - c.x, hb.y - c.y) - (hb.r + c.r);
    if (m <= 0 && m < bestD) { best = c.bone; bestD = m; }
  }
  if (!best && (defState === 'air' || defState === 'down') && hb.level !== 't') {
    // juggle/OTG: lows and mids still sweep a body near the floor within reach
    const near = hurts.find(c => c.x >= lo - c.r - 0.25 && c.x <= hi + c.r + 0.25);
    if (near) return near.bone;
  }
  return best;
}

/** Push two roots apart so pushboxes never overlap (no floating gaps either: max gap untouched). */
export function resolvePush(x1, x2) {
  const min = PUSHBOX.halfWidth * 2, d = x2 - x1;
  if (Math.abs(d) >= min) return [x1, x2];
  const s = Math.sign(d || 1), push = (min - Math.abs(d)) / 2;
  return [x1 - s * push, x2 + s * push];
}

/* ---- reactions ---- */
export const REACTIONS = ['stagger', 'crumple', 'launch', 'screw', 'wall_splat', 'floor_bound',
  'knockdown', 'wakeup', 'block', 'guard_break', 'throw', 'throw_break', 'juggle', 'spin', 'hit'];

/** Resolve the reaction a hit plays. ctx: {blocking, crouching, airborne, counter, nearWall,
    screwUsed, boundUsed, dir:'front'|'back'|'side'}. Order mirrors T7 reaction priority. */
export function reactionFor(mv, ctx = {}) {
  const lv = primaryLevel(mv);
  if (mv.isGrab || lv === 't') return ctx.breakInput && breaks(mv, ctx.breakInput) ? 'throw_break' : 'throw';
  const blocked = ctx.blocking && !mv.unblockable && !(lv === 'l' && !ctx.crouching) && !(lv === 'm' && ctx.crouching) && !(lv === 'h' && ctx.crouching);
  if (blocked) return (mv.heavy && Number(mv.on_block) <= -15) || mv.guardBreak ? 'guard_break' : 'block';
  if (ctx.airborne) {
    if (ctx.nearWall && (mv.heavy || mv.wall)) return 'wall_splat';
    if (mv.bound || (!ctx.boundUsed && mv.screw)) return mv.bound ? 'floor_bound' : 'screw';
    if (mv.knockdown || mv.heavy && ctx.juggleHits >= 4) return 'knockdown';
    return 'juggle';
  }
  if (ctx.nearWall && (mv.wall || mv.heavy && mv.knockdown)) return 'wall_splat';
  if (mv.launch || (ctx.counter && mv.launchOnCH)) return 'launch';
  if (mv.crumple || (ctx.counter && mv.crumpleOnCH)) return 'crumple';
  if (mv.knockdown) return 'knockdown';
  if (ctx.dir === 'back' || mv.spin) return 'spin';
  if (lv === 'l' && (ctx.counter || mv.heavy)) return 'stagger';
  if (ctx.counter || mv.heavy) return 'stagger';
  return 'hit';
}

/** Throw breaks: T7 1 / 2 / 1+2 by throw input (author break in mv.throw_break). */
export function throwBreakFor(mv, notation = '') {
  if (mv.throw_break) return String(mv.throw_break);
  if (/1\+2$/.test(notation)) return '1+2';
  if (/(^|\+)1\+3$/.test(notation)) return '1';
  if (/(^|\+)2\+4$/.test(notation)) return '2';
  return '1+2';
}
export function breaks(mv, input, notation = mv.input || '') {
  const want = throwBreakFor(mv, notation).split(/\s*or\s*|\//);
  return want.includes(input);
}

/** Counter-hit: defender in startup/recovery of their own attack. T7 CH bonus in damage. */
export function isCounter(defPhase) { return defPhase === 'startup' || defPhase === 'recovery'; }
export function damageFor(mv, { counter = false, juggleHits = 0 } = {}) {
  const base = Number(mv.damage) || 0;
  const scale = juggleHits ? Math.max(0.3, 1 - 0.1 * juggleHits) : 1; // juggle damage scaling
  return Math.round(base * (counter ? 1.2 : 1) * scale);
}

/* ---- feel: hitstop, spark, shake, sound ---- */
const FX = {
  hit:         { stop: 6,  spark: 'spark_s', shake: 0.00, sound: 'hit_light' },
  stagger:     { stop: 9,  spark: 'spark_m', shake: 0.02, sound: 'hit_mid' },
  spin:        { stop: 8,  spark: 'spark_m', shake: 0.02, sound: 'hit_mid' },
  crumple:     { stop: 12, spark: 'spark_l', shake: 0.05, sound: 'hit_heavy' },
  launch:      { stop: 12, spark: 'spark_l', shake: 0.06, sound: 'hit_launch' },
  juggle:      { stop: 5,  spark: 'spark_s', shake: 0.01, sound: 'hit_light' },
  screw:       { stop: 10, spark: 'spark_l', shake: 0.04, sound: 'hit_screw' },
  floor_bound: { stop: 11, spark: 'spark_l', shake: 0.07, sound: 'hit_bound' },
  wall_splat:  { stop: 14, spark: 'spark_wall', shake: 0.08, sound: 'hit_wall' },
  knockdown:   { stop: 10, spark: 'spark_l', shake: 0.05, sound: 'hit_heavy' },
  block:       { stop: 4,  spark: 'spark_block', shake: 0.00, sound: 'block' },
  guard_break: { stop: 10, spark: 'spark_block', shake: 0.04, sound: 'guard_break' },
  throw:       { stop: 0,  spark: null, shake: 0.03, sound: 'throw' },
  throw_break: { stop: 6,  spark: 'spark_break', shake: 0.01, sound: 'throw_break' },
  wakeup:      { stop: 0,  spark: null, shake: 0, sound: 'wakeup' },
};
export function feelFor(reaction, { counter = false } = {}) {
  const f = { ...(FX[reaction] || FX.hit) };
  if (counter && reaction !== 'block') { f.stop += 3; f.spark = 'spark_ch'; f.sound = 'counter_hit'; f.shake += 0.02; }
  f.stopSec = f.stop * FRAME;
  return f;
}

/* Wake-up options after knockdown (T7): stand, roll back, roll side, rising kick low/mid. */
export const WAKEUPS = ['stand', 'back_roll', 'side_roll', 'rise_kick_low', 'rise_kick_mid'];

/* Sound / VFX hook bus: game code subscribes; tests record. */
const _hooks = [];
export function onCombatEvent(fn) { _hooks.push(fn); return () => _hooks.splice(_hooks.indexOf(fn), 1); }
export function emit(ev) { for (const h of _hooks) try { h(ev); } catch (e) {} return ev; }

/** One headless exchange: returns {connected, bone, reaction, damage, feel}. */
export function resolveHit(att, def, mv, notation, ctx = {}) {
  const hb = hitbox(att.x, att.facing, mv, notation, att.airY || 0);
  const hurts = hurtboxes(def.x, -att.facing, def.state || 'stand', def.airY || 0, def.scale || 1);
  const bone = contact(hb, hurts, def.state || 'stand');
  if (!bone) return emit({ type: 'whiff', notation, connected: false });
  const counter = ctx.counter ?? isCounter(def.phase);
  const reaction = reactionFor(mv, { ...ctx, counter, crouching: def.state === 'crouch', airborne: def.state === 'air' });
  const damage = reaction === 'block' || reaction === 'throw_break' ? 0 : damageFor(mv, { counter, juggleHits: ctx.juggleHits || 0 });
  return emit({ type: 'hit', notation, connected: true, bone, reaction, damage, counter, feel: feelFor(reaction, { counter }), activeFrames: Math.round(effectiveActive(mv) / FRAME) });
}
