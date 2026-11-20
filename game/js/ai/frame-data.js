/* ============================================================
   WESTERN HEART — Frame-Data Reasoning
   FightingICE lesson: every serious fighting-game AI reasons in
   FRAMES, not vibes. The competition platform hands agents a forward
   model plus per-move frame data; the winning agents (MCTS sample AI,
   ERHEAPI 2020) plan action sequences through that model. This module
   is WH's frame-data layer: units, normalization, and the two pieces
   of Tekken math every CPU needs — startup comparison and punish
   selection.

   Units in this repo:
     • moveset `startup` / `active` / `recovery` are SECONDS
       (e.g. 0.1667 = 10f).
     • T7 teardown fields (`t7_startup_frames`, `t7_on_block`,
       `t7_on_hit`) are FRAMES / frame-advantage strings ("-9").
     • The brains (reversal-logic) speak FRAMES. ai.js used to feed
       raw seconds into `foeStartupFrames` — the sidestep window
       (>= 15f) could never open. Fixed here via startupFramesOf.

   Pure functions only: no fighter handles, no DOM, no THREE.
   ============================================================ */

export const FPS = 60;

/** seconds -> integer frames (60fps). */
export const secsToFrames = (s) => Math.max(0, Math.round((+s || 0) * FPS));

/** frames -> seconds. */
export const framesToSecs = (f) => (+f || 0) / FPS;

/**
 * Normalize a startup value to integer frames.
 * Moveset fields are seconds (0.217); T7 teardown fields are already
 * frames (13). Heuristic: no real startup exceeds 3 seconds, so
 * anything larger is already frames.
 */
export function startupFramesOf(v) {
  if (v === null || v === undefined) return null;
  const n = +v;
  if (!Number.isFinite(n) || n <= 0) return null;
  return n > 3 ? Math.round(n) : Math.max(1, Math.round(n * FPS));
}

/**
 * Parse a T7-style frame-advantage string to an integer.
 * "-9" -> -9, "+4" -> 4, "-6 (OC)" -> -6, "KND"/"STUN"/"ATK" -> null.
 */
export function parseAdvantage(v) {
  if (v === null || v === undefined) return null;
  const m = String(v).match(/([+-]?\d+)/);
  return m ? +m[1] : null;
}

const _lvl = (m) => String(m.hit_level || m.t7_hit_level || m.note || '').toLowerCase();

/**
 * Normalize any moveset move record to frame units.
 * @returns {{input,startupF,activeF,recoveryF,damage,hitLevel,isLow,onBlock,onHit}|null}
 */
export function frameMove(move, input) {
  if (!move) return null;
  const lvl = _lvl(move);
  return {
    input: input ?? move.input ?? null,
    startupF: startupFramesOf(move.t7_startup_frames ?? move.startup) ?? 12,
    activeF: secsToFrames(move.active ?? 0.05),
    recoveryF: secsToFrames(move.recovery ?? 0.4),
    damage: +move.damage || 0,
    hitLevel: lvl,
    isLow: /(^|[\s,(])l\b|low/.test(lvl),
    isHigh: /(^|[\s,(])h\b|high/.test(lvl) && !/(^|[\s,(])m\b|mid/.test(lvl),
    onBlock: parseAdvantage(move.on_block ?? move.t7_on_block),
    onHit: parseAdvantage(move.on_hit ?? move.t7_on_hit),
  };
}

/**
 * Tekken punish math. With `advantageF` frames to work with, the
 * launch-speed move that lands is startupF <= advantageF - 1 (one frame
 * of execution margin). Returns the highest-damage move that fits,
 * or null when nothing is guaranteed.
 */
export function bestPunish(moves, advantageF) {
  if (!moves || !moves.length || !(advantageF > 1)) return null;
  const window = Math.floor(advantageF) - 1;
  let best = null;
  for (const m of moves) {
    if (!m || !(m.damage > 0) || m.startupF > window) continue;
    if (!best || m.damage > best.damage) best = m;
  }
  return best;
}

/**
 * Frame-trap check: my move leaves me at `myAdv` on block; the foe's
 * fastest realistic button is `foeFastestF` frames. If my followup's
 * startup beats their button, the trap is real.
 */
export function frameTrapWins(myAdv, myFollowupF, foeFastestF = 10) {
  if (myAdv === null || myAdv === undefined) return false;
  return myFollowupF - myAdv < foeFastestF;
}

/** Rough speed class for logging / opponent-model features. */
export function speedClass(startupF) {
  if (startupF <= 10) return 'jab';
  if (startupF <= 14) return 'poke';
  if (startupF <= 20) return 'mid';
  return 'slow';
}
