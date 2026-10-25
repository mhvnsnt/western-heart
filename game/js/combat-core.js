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

/* ============ GAP-FILL LANE 1 (2026-10-24) — combat systems ============
   PROPRIETARY NAMES: NEEDS NAME (owner names them). No canon name for
   these systems exists in CANON.md, SOUL-SYSTEMS.md, docs/decisions/ or
   docs/research/ as of this lane (only "Soul Urge" is user-locked).
   The Tekken names below appear ONLY in this technical module and in
   code comments — never in canon bios or in-universe writing — and
   user-facing text must use the neutral labels noted at each system
   until the owner picks canon names. Buttons use LP1/RP2/LK3/RK4.
   Sources (web, 2026-10-24): Tekken Wiki "Power Crush" / "Screw" /
   "Tornado", wavu.wiki "Attack" (Power Crush armor startup) + "Combo"
   (one extender per combo), Tekken 8 recoverable-gauge descriptions.
   Per-move DATA (which moves are Power Crush / Screw / Tornado /
   item-gated) is the moveset lane's job: this engine only reads the
   flags when present and falls back honestly (UNMAPPED) when absent —
   it never invents a flag for a move. */

/* T7 Power Crush armor startup: most moves ~8 frames (wavu.wiki).
   Before this delay the move can still be interrupted normally. */
export const POWER_CRUSH_ARMOR_FRAMES = 8;
export const POWER_CRUSH_ARMOR_DELAY = POWER_CRUSH_ARMOR_FRAMES * FRAME;

/* Is `move` a low? Level-string first (authoritative when present);
   otherwise the decoded T3 hit word: a low is blocked ONLY by a
   crouching guard (guard bit 0x08 set, standing bit 0x10 clear) in
   fighter.js's guard encoding. Unknown level => not low (WH's
   defaultWord is mid), so an unmapped move never silently breaks
   a Power Crush. */
export function isLowHit(move) {
  if (!move) return false;
  const rawSrc = move.hit_level ?? (move.t7 && move.t7.hit_level) ?? (move.t8 && move.t8.tgt) ?? '';
  const raw = String(rawSrc).replace(/\([^)]*\)/g, ' ').trim().toLowerCase();
  if (raw) {
    const toks = raw.split(/[ ,]+/).filter(Boolean);
    const c = toks.length ? toks[toks.length - 1] : '';
    return c.startsWith('l');
  }
  const w = move.hitWord;
  if (typeof w === 'number') return (w & 0x08) !== 0 && (w & 0x10) === 0;
  return false;
}

/* Power Crush flag, from any field the moveset lane may author.
   Absent everywhere => false (UNMAPPED, never inferred from damage
   or class — a heavy strike is not automatically a Power Crush). */
export function isPowerCrushMove(move) {
  if (!move) return false;
  return !!(move.powerCrush || move.power_crush || move.powercrush ||
    (move.t7 && move.t7.powerCrush) || (move.t8 && move.t8.powerCrush));
}

/* Does the defender's in-flight Power Crush absorb `incoming`?
   T7 rules: absorbs mid/high strikes, full damage still applies,
   the swing continues; lows, throws, unblockables and Rage Arts
   break it. `phase`/`stateT` are the defender's attack phase and
   time-in-state (fighter.js _attackPhase / stateT). */
export function powerCrushAbsorbs(defMove, phase, stateT, incoming) {
  if (!isPowerCrushMove(defMove)) return false;
  if (!incoming) return false;
  if (incoming.isGrab || incoming.move_class === 'throw') return false;
  if (incoming.unblockable || incoming.rageArt) return false;
  if (isLowHit(incoming)) return false;
  if (phase === 'active') return true;
  if (phase === 'startup') return (Number(stateT) || 0) >= POWER_CRUSH_ARMOR_DELAY;
  return false;
}

/* ---- Combo extenders: Screw (T7) / Tornado (T8) ----
   T7: Screw (S!) spins an airborne opponent into a slump and
   extends the juggle; T8: Tornado flips them into a ground-bound
   state. Both eras share ONE extender slot per combo (wavu.wiki
   "Combo": "There is only one combo extender available to any
   given combo"), so fighter.js tracks a single _extenderUsed flag
   and records which kind fired. A grounded connect does NOT fire
   either (T7 pirouette stun on the ground is not a Screw). */
export function isScrewMove(move) {
  if (!move) return false;
  return !!(move.screw || move.tailspin || move.screwAttack ||
    (move.t7 && move.t7.screw));
}
export function isTornadoMove(move) {
  if (!move) return false;
  return !!(move.tornado || (move.t8 && move.t8.tornado));
}
export function extenderKind(move) {
  if (isScrewMove(move)) return 'screw';
  if (isTornadoMove(move)) return 'tornado';
  return null;
}
export const SCREW_SLUMP_STUN = 0.9;   // slump follow-up window, seconds
export const TORNADO_BOUND_STUN = 0.8; // ground-bound follow-up window
export const EXTENDER_LAND_STUN_FLOOR = 0.7; // slump/bound window survives landing

/* ---- Wall splat (distinct from wall BREAK) ----
   T7: a knocked-back fighter hitting an unbroken wall sticks to
   it (W!) and eats a wall combo. Wall game allows 3 hits on the
   wall before the victim drops fast; the splat itself is not a
   break (stagebreaks.js owns breaks; fighter.js owns this state). */
export const WALL_SPLAT_MAX_HITS = 3;
export const WALL_SPLAT_STUN = 0.55;
export function nextWallSplatState(hits) {
  return hits >= WALL_SPLAT_MAX_HITS ? 'knockdown' : 'wallsplat';
}

/* ---- Item moves (T7 item-gated attacks) ----
   A move may require an equipped customization item. The gate is
   data-driven: `requiresItem` (or `item` / `itemMove` + `item`)
   on the move record, matched against the fighter's equipped
   item ids (fighter.js equippedItems, set by the customization
   lane). No item data in WH movesets yet => no move is gated
   until the moveset lane authors one. */
export function requiresItemOf(move) {
  if (!move) return null;
  return move.requiresItem || move.requiredItem || move.item || null;
}
export function itemGate(move, equipped) {
  const item = requiresItemOf(move);
  if (!item) return { blocked: false, item: null };
  const list = Array.isArray(equipped) ? equipped : [];
  const ids = list.map((e) => (typeof e === 'string' ? e : (e && (e.id || e.itemId)) || null));
  return { blocked: !ids.includes(item), item };
}

/* ---- Per-move hitbox / hurtbox lookup (ENGINE side) ----
   Reads per-move geometry when the moveset lane has authored it
   and reports UNMAPPED otherwise — never synthesized from limb
   or class. Accepted shapes: {shape:'sphere'|'capsule', radius},
   {radius}, {shape:'box', w,h,d} (dims preserved; no radius is
   invented from a box — callers keep the generic radius then).
   fighter.js getHitbox() applies radius/reach from this result;
   getHurtboxes() applies a hurtbox radiusScale only when the
   data itself supplies one. */
function _perMoveBox(src) {
  if (!src || typeof src !== 'object') return null;
  const radius = src.radius ?? src.r ?? null;
  const shape = src.shape || (radius != null ? 'sphere' : (src.w != null ? 'box' : null));
  // A hurtbox that carries only a radiusScale is still mapped data
  // (fighter.js applies the scale); it is not UNMAPPED.
  if (!shape && radius == null && src.radiusScale == null) return null;
  return {
    mapped: true, shape, radius: radius != null ? Number(radius) : null,
    reach: src.reach ?? src.range ?? null,
    forward: src.forward ?? src.offset_x ?? src.x ?? null,
    height: src.height ?? src.y ?? null,
    dims: shape === 'box' ? { w: src.w, h: src.h, d: src.d } : null,
    radiusScale: src.radiusScale ?? null,
  };
}
export function resolvePerMoveHitbox(move) {
  if (!move) return { mapped: false, reason: 'UNMAPPED' };
  const src = move.hitbox ?? (move.t7 && move.t7.hitbox) ?? (move.t8 && move.t8.hitbox) ?? null;
  if (src != null && typeof src === 'number') return { mapped: true, shape: 'sphere', radius: src, reach: null, forward: null, height: null, dims: null, radiusScale: null };
  const box = _perMoveBox(src);
  return box || { mapped: false, reason: 'UNMAPPED' };
}
export function resolvePerMoveHurtbox(move) {
  if (!move) return { mapped: false, reason: 'UNMAPPED' };
  const src = move.hurtbox ?? (move.t7 && move.t7.hurtbox) ?? (move.t8 && move.t8.hurtbox) ?? null;
  const box = _perMoveBox(src);
  return box || { mapped: false, reason: 'UNMAPPED' };
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
