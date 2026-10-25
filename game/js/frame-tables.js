// T8 frame tables (wavu.wiki, CC0-1.0) -> runtime lookup.
// Data: game/data/t8_frame_tables.json, built by tools/frame-data/build_t8_frame_tables.py
// from docs/t7t8-reference/frame-data-t8-full (41 characters).
// Used by fighter.js for block stun, hit stun, counter-hit stun and throw-break inputs.
// If a lookup misses, the T3-derived defaults apply.
import { loadT7FrameData, findMove } from './t7-frame-data-loader.js';
// T7 DLC frame data (TekkenDocs sheet damage, NOT MOD values) - lazy lookup; anim_ref stays UNMAPPED.
export async function t7Frame(slug, input) { const d = await loadT7FrameData(slug); return findMove(d, input); }
let TABLE = null;
const url = new URL('../data/t8_frame_tables.json', import.meta.url);
export const frameTablesReady = fetch(url).then((r) => (r.ok ? r.json() : null))
  .then((j) => { TABLE = j && j.chars; return !!TABLE; }).catch(() => false);

const norm = (s) => String(s || '').toLowerCase().replace(/[\s-]/g, '_');
// ms.tekken_base is "bank:character" (moveset-library) or ms.base = {bank, character}.
export function t8CharFor(ms) {
  if (!TABLE || !ms) return null;
  const raw = ms.tekken_base || (ms.base && ms.base.character) || ms.fighter || '';
  const c = norm(String(raw).split(':').pop());
  return TABLE[c] ? c : null;
}
export function t8Frame(ms, input) {
  const c = t8CharFor(ms);
  return c && input ? (TABLE[c][input] || TABLE[c][String(input).replace(/\s/g, '')] || null) : null;
}
// Frame advantage -> defender stun seconds. Attacker remaining time = active tail + recovery.
export function stunFromAdvantage(adv, attackerMove) {
  const rem = (attackerMove.active || 0) * 0.5 + (attackerMove.recovery || 0);
  return Math.max(0.05, Math.min(1.4, rem + adv / 60));
}
