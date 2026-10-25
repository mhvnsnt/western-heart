/* ============================================================
   WESTERN HEART — hit-tables.js (lane C, 2026-10-24)
   Active frames from wavu T8 frame data (owner law: T5-T8 first, T3 last).
   game/data/hit_tables.json is built by tools/hit-contact/build_hit_tables.py:
   t8[char][input] = [active_frames, reach_m]. combat-core attackPhase still
   floors every window at 3 frames (MIN_ACTIVE); this supplies the data's own
   count where wavu records one (multi-frame actives: 4-12 frames).
   ============================================================ */
let HT = null;
export function setHitTables(j) { HT = j && j.t8 ? j : null; }
export const hitTablesReady = (typeof fetch === 'function'
  ? fetch(new URL('../data/hit_tables.json', import.meta.url)).then((r) => (r.ok ? r.json() : null))
      .then((j) => { if (j) setHitTables(j); return !!HT; })
  : Promise.resolve(false)).catch(() => false);

const normChar = (s) => String(s || '').toLowerCase().replace(/[\s-]/g, '_');
/* [activeFrames | null, reach | null] for a moveset move, or null. Only moves taken from the
   T8 base character (t8_source), or carrying no donor tag on a T8-based moveset, use its row:
   a donor move's input names a different character's move. */
export function t8ActiveOf(ms, mv, key, input) {
  if (!HT || !mv) return null;
  const donor = /donor\./.test(String(key || ''));
  const bases = (ms && ms.merge_sources && ms.merge_sources.bases && ms.merge_sources.bases.t8) || [];
  const ch = normChar(mv.t8_source || (!donor && bases[0]) || '');
  const rows = ch && HT.t8[ch];
  if (!rows) return null;
  for (const n of [mv.t8_input, mv.input, input]) if (n && rows[n]) return rows[n];
  return null;
}
