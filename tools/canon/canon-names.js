// tools/canon — STUB of the shared Eastern Mind Western Heart canon renamer.
// The real renamer is being built by another job; this keeps the same contract:
//   canonName(kind, sourceId, { source }) -> EMWH canon display name.
// Imported part/item/colour names from T7, WWE, Def Jam etc. NEVER reach the suite UI.
// The original-name <-> canon mapping lives only in the private repo
// (mhvnsnt/game-reverse-engineering: canon/name-map.json) and is installed at
// runtime as globalThis.__WH_CANON_MAP (only with __WH_PRIVATE_ASSETS).
const SYL = ['ka', 'ren', 'shi', 'mo', 'tsu', 'ra', 'en', 'hai', 'do', 'yu', 'zan', 'ko', 'mi', 'ga', 'ru', 'sen'];
const KIND = { part: 'Piece', item: 'Relic', color: 'Hue', slot: 'Mount' };
function h32(s) { let h = 2166136261; for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }
export function canonName(kind, sourceId, { source = '' } = {}) {
  const map = globalThis.__WH_CANON_MAP;
  const k = `${source}:${kind}:${sourceId}`;
  if (map && map[k]) return map[k];
  const h = h32(k);
  const w = SYL[h & 15] + SYL[(h >> 4) & 15] + SYL[(h >> 8) & 15];
  return `${w[0].toUpperCase()}${w.slice(1)} ${KIND[kind] || 'Mark'} ${(h >> 12) % 900 + 100}`;
}
