// tools/canon — browser runtime of the shared canon renamer (tools/canon/canon.mjs, #903).
// Contract:
//   canonName(kind, sourceId, { source }) -> EMWH canon display name.
// Imported part/item/colour names from T7, Def Jam etc. NEVER reach the suite UI.
// The original-name <-> canon mapping lives only in the private repo
// (mhvnsnt/game-reverse-engineering: naming/CANON-NAME-MAP.json, same file canon.mjs uses)
// and is installed at runtime as globalThis.__WH_CANON_MAP (only with __WH_PRIVATE_ASSETS):
// either its {entries:[{original,canon,source,kind}]} object / entries array, or a flat
// {"source:kind:id": canon} object. Unmapped names get a deterministic EMWH placeholder.
const SYL = ['ka', 'ren', 'shi', 'mo', 'tsu', 'ra', 'en', 'hai', 'do', 'yu', 'zan', 'ko', 'mi', 'ga', 'ru', 'sen'];
const KIND = { part: 'Piece', item: 'Relic', color: 'Hue', slot: 'Mount' };
function h32(s) { let h = 2166136261; for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }
export function canonName(kind, sourceId, { source = '' } = {}) {
  const map = globalThis.__WH_CANON_MAP;
  const k = `${source}:${kind}:${sourceId}`;
  const entries = Array.isArray(map) ? map : (map && Array.isArray(map.entries) ? map.entries : null);
  if (entries) {
    const lc = String(sourceId).toLowerCase();
    const e = entries.find(x => String(x.original).toLowerCase() === lc && (!x.source || !source || x.source === source) && (!x.kind || x.kind === kind))
      || entries.find(x => String(x.original).toLowerCase() === lc && (!x.source || !source || x.source === source));
    if (e) return e.canon;
  } else if (map && map[k]) return map[k];
  const h = h32(k);
  const w = SYL[h & 15] + SYL[(h >>> 4) & 15] + SYL[(h >>> 8) & 15];
  return `${w[0].toUpperCase()}${w.slice(1)} ${KIND[kind] || 'Mark'} ${(h >>> 12) % 900 + 100}`;
}
