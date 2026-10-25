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
