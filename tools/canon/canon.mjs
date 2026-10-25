#!/usr/bin/env node
// Shared canon renamer (owner rule). Every import pipeline calls this.
// Usage: node tools/canon/canon.mjs <in.json> <out.json> [--map PATH]
// The map is the PRIVATE game-reverse-engineering/naming/CANON-NAME-MAP.json:
//   {"entries":[{"original":"...","canon":"...","source":"<game>","kind":"move|part|mode|place|system|stat"}]}
// Every string value in <in.json> that matches an original (whole string or word-bounded) is replaced
// with its canon name. It exits 2 if any denylisted source name survives the rename.
import fs from 'node:fs';
const args = process.argv.slice(2);
const mi = args.indexOf('--map');
const mapPath = mi >= 0 ? args[mi + 1] : (process.env.WH_CANON_MAP || '');
const [inp, out] = args.filter((a, i) => a !== '--map' && i !== mi + 1);
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
export function loadMap(p) { return p && fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')).entries || [] : []; }
export function rename(v, entries) {
  if (typeof v === 'string') { let s = v; for (const e of [...entries].sort((a, b) => b.original.length - a.original.length)) s = s.replace(new RegExp(`\\b${esc(e.original)}\\b`, 'gi'), e.canon); return s; }
  if (Array.isArray(v)) return v.map(x => rename(x, entries));
  if (v && typeof v === 'object') return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, rename(x, entries)]));
  return v;
}
export function leaks(text, terms) { const t = text.toLowerCase(); return terms.filter(w => new RegExp(`\\b${esc(w)}\\b`).test(t)); }
if (inp && out) {
  const terms = JSON.parse(fs.readFileSync(new URL('./denylist.json', import.meta.url))).terms;
  const res = rename(JSON.parse(fs.readFileSync(inp, 'utf8')), loadMap(mapPath));
  const txt = JSON.stringify(res, null, 1); const bad = leaks(txt, terms);
  if (bad.length) { console.error('canon: unmapped source names remain:', bad.join(', ')); process.exit(2); }
  fs.writeFileSync(out, txt); console.log('canon: ok', out);
}
