/* ============================================================
   WESTERN HEART — T7 DLC frame-data loader (adapter, not a moveset)
   Loads the PR #999-schema frame-data files produced by
   ../kaggle_batch_convert.py (t7-{slug}-lp-rp-lk-rk.json) and exposes
   them for lookup by LP1/RP2/LK3/RK4 notation.

   WHAT THIS IS: the FRAME-DATA layer. It is NOT a drop-in replacement
   for game/assets/movesets/{fighter}.json, which uses schema v2
   (moves dict, numeric damage/startup, anim_ref per move). Converting
   frame data into a playable v2 moveset requires a move->animation
   mapping that does NOT exist in the frame-data source — the King
   file itself warns "Animation column stays UNMAPPED until live T7
   extraction lands". This loader therefore NEVER invents anim_ref,
   numeric damage, or numeric startup: anything it cannot parse
   exactly stays null and is flagged.

   Button map: LP1 = Tekken 1 = Left Punch, RP2 = Tekken 2 = Right
   Punch, LK3 = Tekken 3 = Left Kick, RK4 = Tekken 4 = Right Kick.

   Usage (browser, ES module, from a page served under game/):
     import { loadT7FrameData, findMove } from
       './js/t7-frame-data-loader.js';
     const zafina = await loadT7FrameData('zafina');
     findMove(zafina, 'd/f+LP1'); // -> move object or null
   Node: the same functions work with a `fetch` polyfill or by
   passing already-parsed JSON to indexT7FrameData().
   ============================================================ */

// Relative to the page, mirroring game/js/movesets.js (MS_BASE).
// When applied by wiring/apply.sh, frame-data files live at
// game/data/t7-frame-data/t7-{slug}-lp-rp-lk-rk.json.
export const T7_FRAME_DATA_BASE = 'data/t7-frame-data/';

export const T7_DLC_SLUGS = [
  'fahkumram', 'ganryu', 'geese', 'kunimitsu', 'leroy',
  'lidia', 'negan', 'noctis', 'zafina',
];

export const BUTTON_MAP_TEXT =
  'LP1=Tekken 1=Left Punch, RP2=Tekken 2=Right Punch, ' +
  'LK3=Tekken 3=Left Kick, RK4=Tekken 4=Right Kick';

const MOVE_FIELDS = [
  'notation', 'hit_level', 'damage', 'speed', 'on_block', 'on_hit',
  'on_ch', 'notes', 'notation_original', 'notation_lp',
];

/** Validate one frame-data file against the PR #999 / King schema. */
export function validateT7FrameData(data) {
  const problems = [];
  if (!data || typeof data !== 'object') return ['not an object'];
  for (const k of ['source', 'metadata_original', 'move_count',
    'dups_removed', 'moves']) {
    if (!(k in data)) problems.push(`missing top-level key: ${k}`);
  }
  if (Array.isArray(data.moves)) {
    if (data.move_count !== data.moves.length) {
      problems.push(
        `move_count ${data.move_count} != moves.length ${data.moves.length}`);
    }
    for (const m of data.moves) {
      for (const f of MOVE_FIELDS) {
        if (!(f in m)) problems.push(`move missing field ${f}: ${m.notation_original}`);
        else if (m[f] === '') problems.push(`empty string in ${f}: ${m.notation_original}`);
      }
      if (m.notation !== m.notation_lp) {
        problems.push(`notation != notation_lp: ${m.notation_original}`);
      }
    }
  }
  return problems;
}

/** Index a parsed frame-data file for lookup. Returns { data, byNotation, byOriginal }. */
export function indexT7FrameData(data) {
  const problems = validateT7FrameData(data);
  if (problems.length) {
    throw new Error(`Invalid T7 frame-data file: ${problems.join('; ')}`);
  }
  const byNotation = new Map();
  const byOriginal = new Map();
  for (const m of data.moves) {
    if (!byNotation.has(m.notation)) byNotation.set(m.notation, m);
    if (!byOriginal.has(m.notation_original)) {
      byOriginal.set(m.notation_original, m);
    }
  }
  return { data, byNotation, byOriginal };
}

/** Fetch + index one character's frame data. `fetchFn` defaults to global fetch. */
export async function loadT7FrameData(slug, fetchFn = fetch) {
  if (!T7_DLC_SLUGS.includes(slug)) {
    throw new Error(`Unknown DLC slug: ${slug}`);
  }
  const url = `${T7_FRAME_DATA_BASE}t7-${slug}-lp-rp-lk-rk.json`;
  const res = await fetchFn(url);
  if (!res.ok) throw new Error(`Failed to load ${url}: ${res.status}`);
  return indexT7FrameData(await res.json());
}

/** Find a move by LP1/RP2/LK3/RK4 notation, or by original 1/2/3/4 notation. */
export function findMove(indexed, notation) {
  return indexed.byNotation.get(notation)
    || indexed.byOriginal.get(notation)
    || null;
}

/** True when a move is a throw row (Negan framesThrows rows included). */
export function isThrowMove(move) {
  return !!move && (
    (move.notes || '').startsWith('Throw') || move.on_hit === '?');
}

/** Moves whose frame data is incomplete in the source (any frame field null). */
export function incompleteMoves(indexed) {
  const frameFields = ['hit_level', 'damage', 'speed', 'on_block', 'on_hit', 'on_ch'];
  return indexed.data.moves.filter(
    (m) => frameFields.some((f) => m[f] === null));
}

/**
 * Adapter stub toward a game moveset move. Maps ONLY what can be parsed
 * exactly; everything else stays null with an explicit flag. In
 * particular anim_ref is ALWAYS null here — a real animation mapping
 * must come from live T7 extraction, never from this file.
 *   damageNumber: first integer of damage ONLY when the whole damage
 *     string is a plain integer list (e.g. "9,20" -> [9,20]); multi-hit
 *     or annotated values ("20 cs6", "12 js9", "14(,25)") -> null + flag.
 *   startupNumber: leading integer of speed ONLY when speed starts with
 *     digits ("10", "13", "20 pc8" -> 20); ranges/annotated ("-16",
 *     "10 (19~20)", "--") -> null + flag. A negative or missing startup
 *     is NOT a startup and is never coerced.
 */
export function toGameMoveStub(move) {
  const damageNumber = (() => {
    if (move.damage === null) return null;
    const parts = move.damage.split(',');
    if (parts.every((p) => /^-?\d+$/.test(p.trim()))) {
      return parts.map((p) => parseInt(p.trim(), 10));
    }
    return null;
  })();
  const startupNumber = (() => {
    if (move.speed === null) return null;
    const m = /^(\d+)/.exec(move.speed.trim());
    return m ? parseInt(m[1], 10) : null;
  })();
  return {
    notation: move.notation,
    notation_original: move.notation_original,
    hit_level: move.hit_level,
    damage: move.damage,
    damageNumber,
    speed: move.speed,
    startupNumber,
    on_block: move.on_block,
    on_hit: move.on_hit,
    on_ch: move.on_ch,
    notes: move.notes,
    isThrow: isThrowMove(move),
    anim_ref: null,
    anim_status: 'UNMAPPED - needs live T7 extraction (see King file warnings)',
    flags: [
      ...(damageNumber === null && move.damage !== null
        ? ['damage_not_plain_numeric'] : []),
      ...(startupNumber === null && move.speed !== null
        ? ['startup_not_plain_numeric'] : []),
      ...(move.damage === null ? ['damage_null_in_source'] : []),
      ...(move.speed === null ? ['speed_null_in_source'] : []),
    ],
  };
}
