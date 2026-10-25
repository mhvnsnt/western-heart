/* combat-core.js — pure, headless-testable Tekken contact + command rules.
   (tekken-command-interpreter lane, owner pt198u: "make contact with each other")

   Frame data is authored in seconds (T8 frames / 60). The renderer ticks with
   a variable dt (30 fps phones => 33 ms), so a 1-frame (16.7 ms) active window
   was skipped between ticks and moves never produced a hitbox. Contact here is
   decided from frame data + spacing (Tekken's model), with the animated bone
   sphere kept only as a secondary path. */

export const FRAME = 1 / 60;
/* T7 mothead active windows are typically 2-4 frames; T8 wiki data records
   only the first active frame. Floor at 3 frames so no move is unhittable. */
export const MIN_ACTIVE = 3 * FRAME;

/* T3 attack words (decoded): high/mid/low/s.mid/unblockable. */
export const HIT_WORD = { h: 0x412, m: 0x217, l: 0x10F, s: 0x31F, ub: 0x607 };

/* T8/T7 hit_level ('h','m','l','s','t', strings like 'h,m,l' use the last)
   -> T3 hit word, so the posture rules (highs whiff crouchers, lows beat
   standing guard) apply to every T7/T8 move instead of everything = mid.
   HITBOX LANE 2026-10-24: a move's level is read from, in order,
   its own hit_level, then its T7 frame-data hit_level, then its T8
   tgt — because 206 Pantera moves carry NO top-level hit_level and
   NO decoded hit_words entry, and all of those used to fall back
   to default-mid in fighter.js (highs hit crouchers, lows were
   unblockable by crouch guard). Decoded ms.hit_words still wins
   over all of this (fighter.js checks it first); this is only the
   fallback chain. T7 strings carry annotations in parentheses
   ('mid (TC)', 'low (TC), low (TC)(ALI)', '(Special) (TJ)(JGS)');
   the parentheses are stripped before tokenising, so 'mid (TC)'
   reads mid instead of misreading the annotation as a throw. */
export function hitWordFor(mv) {
  if (!mv) return undefined;
  if (mv.unblockable) return HIT_WORD.ub;
  const rawSrc = mv.hit_level ?? (mv.t7 && mv.t7.hit_level) ?? (mv.t8 && mv.t8.tgt) ?? '';
  const raw = String(rawSrc).replace(/\([^)]*\)/g, ' ').trim().toLowerCase();
  if (!raw) return undefined;
  const toks = raw.split(/[ ,]+/).filter(Boolean); // ',h' = this hit of a string
  const c = toks.length ? toks[toks.length - 1] : '';
  if (c.startsWith('t')) return undefined; // throws use isGrab rules
  if (c.startsWith('sm') || c === 's') return HIT_WORD.s;
  if (c.startsWith('h')) return HIT_WORD.h;
  if (c.startsWith('l')) return HIT_WORD.l;
  if (c.startsWith('m')) return HIT_WORD.m;
  if (c.startsWith('u')) return HIT_WORD.ub;
  return undefined;
}

/* ============================================================
   COMBAT SYSTEMS 2026-10-24 — Power Crush, Screw/Tornado, Wall
   Splat, Recoverable Health, Item-move gate.
   Technical names only (Tekken terms stay in technical files, never
   in CANON.md bios). Universe names for these systems: NEEDS NAME
   (no name in CANON.md / SOUL-SYSTEMS.md as of 2026-10-24) — do not
   present the technical names below as canon.
   T7 rules implemented here (pure, headless-testable):
   • Power Crush: a move flagged powerCrush absorbs mid/high strikes
     and keeps swinging, but LOSES to lows, throws and unblockables.
     Damage taken while power-crushing becomes RECOVERABLE (T8 rule,
     wavu King Muscle Armor note: "Damage taken during power crush
     state is recoverable").
   • Screw (S!, T7 kirimomi / tailspin) + Tornado (T!, T8 successor):
     a flagged move against an AIRBORNE victim spins them into a
     slump; usable ONCE per combo — the second flagged hit in the
     same combo does not spin again. Both flags share one slot:
     a combo cannot spend Screw and then Tornado.
   • Wall splat (W!): a victim in hitstun/knockdown/spin whose
     knockback carries them into an unbroken stage wall sticks to
     the wall in a vulnerable window. Distinct from wall BREAK
     (stagebreaks.js): a break shatters the wall and EXTENDS the
     bounds; a splat leaves the wall and the bounds untouched.
   • Recoverable health (white gauge, T8): chip damage taken on
     block and damage absorbed by Power Crush do NOT vanish — they
     enter a recoverable pool (hp + pool <= maxHp). The pool is
     recovered ONLY by dealing damage (landed hits and chip you
     inflict); it never recovers with time. See fighter.js
     recoverFromPool / _recoverable.
   • Item moves (T7): a move flagged requiresItem is available
     only while that customization item is equipped; unflagged
     moves are unaffected (no item data exists in repo movesets
     yet, so this gate is currently a no-op scaffold).
   ============================================================ */

/* Hit level of a move: 'high' | 'mid' | 'low' | 'special' (s.mid)
   | 'unblockable' | 'throw' | null (unknown). Derived from the
   decoded hit word when present, else hitWordFor's fallback chain. */
export function hitLevelOf(mv) {
  if (!mv) return null;
  if (mv.isGrab) return 'throw';
  if (mv.unblockable) return 'unblockable';
  const w = mv.hitWord ?? hitWordFor(mv);
  if (w === HIT_WORD.h) return 'high';
  if (w === HIT_WORD.m) return 'mid';
  if (w === HIT_WORD.l) return 'low';
  if (w === HIT_WORD.s) return 'special';
  if (w === HIT_WORD.ub) return 'unblockable';
  return null;
}

/* Power Crush absorption: defender's powerCrush move, incoming strike
   that is NOT a low, throw or unblockable. Unknown-level strikes do
   NOT get absorbed (fail closed: a level we cannot prove mid/high
   must interrupt, or every unlevelled poke would be absorbed). */
export function powerCrushAbsorbs(defenderMove, incomingMove) {
  if (!defenderMove || !defenderMove.powerCrush) return false;
  if (!incomingMove || incomingMove.isGrab || incomingMove.unblockable) return false;
  const lvl = hitLevelOf(incomingMove);
  return lvl === 'mid' || lvl === 'high' || lvl === 'special';
}

/* Which spin (if any) a move carries: 'screw' wins if both are set. */
export function spinMoveKind(mv) {
  if (!mv) return null;
  if (mv.screw) return 'screw';
  if (mv.tornado) return 'tornado';
  return null;
}

/* A spin fires only against an airborne victim, once per combo. */
export function canSpin(mv, victimAirborne, spinUsed) {
  return !!spinMoveKind(mv) && !!victimAirborne && !spinUsed;
}

/* Wall-splat geometry: victim already clamped at a wall, still
   travelling toward that same wall fast enough to stick. */
export function shouldWallSplat({ x, limit, vx }) {
  if (!Number.isFinite(x) || !Number.isFinite(limit) || !Number.isFinite(vx)) return false;
  return Math.abs(x) >= limit - 0.01 && vx !== 0 && Math.sign(vx) === Math.sign(x)
    && Math.abs(vx) >= 0.5;
}

/* Recoverable-pool arithmetic. Invariant: hp + pool <= maxHp. */
export function addToRecoverable(hpAfter, maxHp, pool, amount) {
  if (!(amount > 0)) return pool || 0;
  return Math.min(Math.max(0, maxHp - hpAfter), (pool || 0) + amount);
}
export function greyRecover(hp, maxHp, pool, amount) {
  const recovered = Math.min(pool || 0, Math.max(0, amount || 0));
  return { hp: Math.min(maxHp, hp + recovered), pool: (pool || 0) - recovered, recovered };
}

/* Item-move gate: unflagged moves always available. */
export function itemMoveAvailable(mv, equipped) {
  if (!mv || !mv.requiresItem) return true;
  return Array.isArray(equipped) && equipped.includes(mv.requiresItem);
}

export function effectiveActive(m) {
  return Math.max(Number(m && m.active) || 0, MIN_ACTIVE);
}

/* Phase for attack time t. `prevT` enables the swept check: if the tick
   stepped over the whole active window, that tick still counts as active. */
export function attackPhase(m, t, prevT = t) {
  const s = Number(m.startup) || 0, a = effectiveActive(m), r = Number(m.recovery) || 0;
  if (t < s) return 'startup';
  if (t < s + a) return 'active';
  if (prevT < s + a && prevT <= t) return 'active'; // swept past the window
  if (t < s + a + r) return 'recovery';
  return 'done';
}

/* Reach (root-to-root horizontal distance, metres) a move connects at.
   Bodies separate at 1.45 m (fighter.js), so every move must reach past it.
   Values follow Tekken range classes: jabs ~1.75, kicks ~1.95, lunging
   heavy/launch/specials ~2.25, throws 1.7. A move may author `reach`. */
export function moveReach(m, name = '') {
  if (!m) return 0;
  if (Number(m.reach) > 0) return Number(m.reach);
  if (m.isGrab || /^(1\+3|2\+4)$/.test(name) || name === 'grab') return 1.7;
  const leg = String(m.limb || '').startsWith('leg') || /(^|[+,])[34]$/.test(name);
  let r = leg ? 1.95 : 1.75;
  if (m.heavy || m.launch || m.knockdown || m.rageArt) r += 0.3;
  if (/^(f,f|f,F|qcf|uf|u\/f|SS|wr|b,f)/i.test(name)) r += 0.25; // advancing inputs
  return r;
}

/* Frame-data contact: attacker active, defender in front within reach and
   on the same line (|dz| small). Returns true when the move connects. */
export function inReach(ax, az, facing, dx_def, dz_def, m, name, reachMult = 1) {
  const dx = dx_def - ax, dz = dz_def - az;
  if (Math.sign(dx || facing) !== Math.sign(facing)) return false; // behind us
  if (Math.abs(dz) > 0.75) return false; // off-axis (sidestepped)
  return Math.abs(dx) <= moveReach(m, name) * reachMult;
}

/* Stick vector -> Tekken direction by 8-way octant with a magnitude gate
   (replaces axis thresholds that read diagonals as cardinals and noise as
   input). facing: +1 right. y: +up. Returns 'n','f','b','u','d','u/f'... */
export function stickToDir(x, y, facing = 1, dead = 0.38) {
  const mag = Math.hypot(x, y);
  if (mag < dead) return 'n';
  const fx = x * (facing >= 0 ? 1 : -1);
  const ang = Math.atan2(y, fx) * 180 / Math.PI; // 0 = forward, 90 = up
  const oct = ((Math.round(ang / 45) % 8) + 8) % 8;
  return ['f', 'u/f', 'u', 'u/b', 'b', 'd/b', 'd', 'd/f'][oct];
}

/* Press buffer: Tekken holds an input ~8-10 frames so a press made just
   before recovery ends still fires. A chord arriving inside the window
   upgrades a buffered single that is part of it. */
export class PressBuffer {
  constructor(frames = 10) { this.win = frames * FRAME; this.item = null; }
  push(name, now) {
    const cur = this.item;
    if (cur && name.includes('+') && now - cur.t <= 0.14 && !cur.name.includes('+') &&
        name.split('+').includes(cur.name)) { this.item = { name, t: cur.t }; return; }
    this.item = { name, t: now };
  }
  take(now) {
    const it = this.item;
    if (!it) return null;
    if (now - it.t > this.win) { this.item = null; return null; }
    return it.name;
  }
  clear() { this.item = null; }
}
