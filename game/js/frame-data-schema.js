/* ============================================================
   WESTERN HEART — Frame-data row schema (transfer T1/T3)
   Pure, headless-testable. No DOM, no THREE, no fighter handles.

   SOURCE (docs only): the public frame-data row schema documented
   for a 60 fps 3D fighting game — command, hit level, damage,
   startup, on-block / on-hit / on-counter-hit advantage, property
   tags with frame windows, stance transitions, recovery.
   This module is WH's own implementation of that *shape*.
   It copies no per-character table, no move name and no numeric
   tuning from any source game: every row it validates is authored
   in WH data (see game/data/frame-data-schema-examples.json),
   and every value it cannot parse exactly stays null + flagged,
   exactly like the existing frame-data loader's UNMAPPED rule.

   Timing base: 60 fps. Startup strings use the documented forms:
     "i16"          -> 16
     "i30~31"       -> { min: 30, max: 31 } (range, first hit = min)
     "i10, i23"     -> [10, 23] (multi-hit, one startup per hit)
   Advantage strings: "+1", "-9", "+1c" (c = crouch state),
   "+46a" (a = airborne/juggle state), "KND" / "STUN" / "?" -> null
   (a knockdown/stun is a state, not a frame count — never coerced).
   Tags (machine-readable property flags, frame windows inclusive):
     "hb"           homing / tracking (tracks sidestep)
     "pc7~16"       power-crush / armour window, frames 7-16
     "js21~29"      jump-status window
     "cs7~16"       crouch-status window
     "screw" / "tailspin"  combo-extender flag (see combat-core.js)
   Hit levels: "h" high, "m" mid, "l" low, plus "s" special-mid.
   Guard rules (documented, engine-neutral): a high whiffs a
   crouching defender, a mid hits a croucher, a low is blocked
   only by a crouching guard.
   ============================================================ */

export const FPS = 60;
export const FRAME = 1 / FPS;

/** Parse "i16" / "i30~31" / "i10, i23" -> number | {min,max} | number[] | null. */
export function parseStartup(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'number') return Number.isFinite(v) && v > 0 ? Math.round(v) : null;
  const s = String(v).trim().toLowerCase().replace(/^i/, '');
  if (!s) return null;
  const parts = s.split(',').map((p) => p.trim().replace(/^i/, '')).filter(Boolean);
  const parsed = parts.map((p) => {
    const m = /^(\d+)(?:~(\d+))?$/.exec(p);
    if (!m) return null;
    return m[2] ? { min: +m[1], max: +m[2] } : +m[1];
  });
  if (parsed.some((p) => p === null)) return null;
  return parsed.length === 1 ? parsed[0] : parsed;
}

/** First (earliest) startup frame of a parsed startup value, or null. */
export function firstStartup(parsed) {
  if (parsed === null || parsed === undefined) return null;
  if (typeof parsed === 'number') return parsed;
  if (Array.isArray(parsed)) return firstStartup(parsed[0]);
  return parsed.min;
}

/** Parse "+1", "-9", "+1c", "+46a" -> int; "KND"/"STUN"/"?" / "" -> null. */
export function parseAdvantage(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'number') return Number.isFinite(v) ? Math.round(v) : null;
  const m = /([+-]?\d+)/.exec(String(v).trim());
  return m ? +m[1] : null;
}

/** "9,20" -> [9,20]; annotated / non-numeric damage -> null (flagged by caller). */
export function parseDamage(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'number') return [v];
  const parts = String(v).split(',').map((p) => p.trim());
  if (!parts.every((p) => /^-?\d+$/.test(p))) return null;
  return parts.map((p) => +p);
}

/** "h,m" / "mid" / "low" -> ['h','m'] etc; unknown tokens dropped, empty -> []. */
export function parseHitLevels(v) {
  if (v === null || v === undefined) return [];
  const words = String(v).toLowerCase().replace(/\(.*?\)/g, ' ').split(/[,\s]+/).filter(Boolean);
  const map = { h: 'h', high: 'h', m: 'm', mid: 'm', l: 'l', low: 'l', s: 's', smid: 's', special: 's' };
  return words.map((w) => map[w]).filter(Boolean);
}

/** Parse a tag string ("hb pc7~16 js21~29") into a structured object. */
export function parseTags(v) {
  const out = { homing: false, powerCrush: null, jumpStatus: null, crouchStatus: null, screw: false, raw: [] };
  if (v === null || v === undefined) return out;
  const toks = String(v).split(/[,\s]+/).filter(Boolean);
  for (const t of toks) {
    out.raw.push(t);
    const low = t.toLowerCase();
    if (low === 'hb' || low === 'homing') out.homing = true;
    else if (low === 'screw' || low === 'tailspin') out.screw = true;
    else {
      const m = /^(pc|js|cs)(\d+)(?:~(\d+))?$/.exec(low);
      if (m) {
        const win = { start: +m[2], end: m[3] ? +m[3] : +m[2] };
        if (m[1] === 'pc') out.powerCrush = win;
        if (m[1] === 'js') out.jumpStatus = win;
        if (m[1] === 'cs') out.crouchStatus = win;
      }
    }
  }
  return out;
}

const inWindow = (win, frame) => !!win && frame >= win.start && frame <= win.end;
/** True when `frame` falls inside the row's power-crush window (armour). */
export function isPowerCrushActive(tags, frame) { return inWindow(tags && tags.powerCrush, frame); }
/** True when `frame` falls inside the row's jump-status window. */
export function isJumpStatus(tags, frame) { return inWindow(tags && tags.jumpStatus, frame); }
/** True when `frame` falls inside the row's crouch-status window. */
export function isCrouchStatus(tags, frame) { return inWindow(tags && tags.crouchStatus, frame); }

/**
 * Guard outcome for one hit level against a defender guard.
 * guard: 'standing' | 'crouching' | 'none'. Returns 'blocked' | 'hit' | 'whiff'.
 * High whiffs a croucher; mid hits a croucher; low is blocked ONLY by crouch guard.
 */
export function guardOutcome(level, guard) {
  if (guard === 'none') return 'hit';
  if (level === 'h') return guard === 'crouching' ? 'whiff' : 'blocked';
  if (level === 'l') return guard === 'crouching' ? 'blocked' : 'hit';
  return 'blocked'; // mid / special-mid: blocked by either guard
}

/**
 * Validate a raw frame-data row. Returns a list of problem strings (empty = valid).
 * Required: command (non-empty string). Everything else must parse if present;
 * unparseable values are problems, not silently coerced — callers keep them null.
 */
export function validateFrameRow(row) {
  const problems = [];
  if (!row || typeof row !== 'object') return ['not an object'];
  if (!row.command || typeof row.command !== 'string') problems.push('missing command');
  if (row.startup !== undefined && parseStartup(row.startup) === null) problems.push(`unparseable startup: ${row.startup}`);
  if (row.damage !== undefined && row.damage !== null && parseDamage(row.damage) === null) problems.push(`damage not plain numeric: ${row.damage}`);
  for (const f of ['on_block', 'on_hit', 'on_ch']) {
    if (row[f] !== undefined && row[f] !== null && parseAdvantage(row[f]) === null && !/^(knd|stun|\?)$/i.test(String(row[f]).trim())) {
      problems.push(`unparseable ${f}: ${row[f]}`);
    }
  }
  if (row.recovery !== undefined && row.recovery !== null) {
    const m = /^r?(\d+)$/.exec(String(row.recovery).trim());
    if (!m) problems.push(`unparseable recovery: ${row.recovery}`);
  }
  return problems;
}

/**
 * Normalize a raw row into the WH frame row the game reads. Unparseable
 * numeric fields become null and are listed in `flags`; nothing is invented.
 * { command, hitLevels, damage, startup, startupF, onBlock, onHit, onCh,
 *   tags, transitions, recoveryF, recovery, flags }
 */
export function normalizeFrameRow(row) {
  const flags = [];
  const startup = parseStartup(row.startup);
  if (row.startup !== undefined && row.startup !== null && startup === null) flags.push('startup_unparseable');
  const damage = row.damage === undefined ? null : parseDamage(row.damage);
  if (row.damage !== undefined && row.damage !== null && damage === null) flags.push('damage_not_plain_numeric');
  const onBlock = row.on_block === undefined ? null : parseAdvantage(row.on_block);
  const onHit = row.on_hit === undefined ? null : parseAdvantage(row.on_hit);
  const onCh = row.on_ch === undefined ? null : parseAdvantage(row.on_ch);
  let recoveryF = null;
  if (row.recovery !== undefined && row.recovery !== null) {
    const m = /^r?(\d+)$/.exec(String(row.recovery).trim());
    recoveryF = m ? +m[1] : null;
    if (recoveryF === null) flags.push('recovery_unparseable');
  }
  return {
    command: row.command ?? null,
    hitLevels: parseHitLevels(row.hit_level ?? row.hitLevel ?? ''),
    damage,
    startup,
    startupF: firstStartup(startup),
    onBlock, onHit, onCh,
    tags: parseTags(row.tags ?? ''),
    transitions: Array.isArray(row.transitions) ? row.transitions : (row.transitions ? [row.transitions] : []),
    recoveryF,
    recovery: recoveryF === null ? null : recoveryF / FPS,
    flags,
  };
}

/**
 * Punish check, in frames: after blocking a move that leaves the attacker
 * at `onBlock` (negative), a punish with startup `punishStartupF` lands
 * when punishStartupF <= -onBlock. Returns false for safe / plus moves.
 */
export function canPunish(onBlock, punishStartupF) {
  if (onBlock === null || onBlock === undefined || onBlock >= 0) return false;
  return punishStartupF <= -onBlock;
}

/** Total move length in frames (startup + active + recovery), null-safe. */
export function totalFrames(normalized, activeF = 0) {
  const s = normalized.startupF, r = normalized.recoveryF;
  if (s === null || r === null) return null;
  return s + (activeF || 0) + r;
}
