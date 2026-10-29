// Engine regression gate for the 2026-10-21 moveset engine (game/js/movesets.js).
//
//   node tools/moveset-merge/engine_check.mjs OLD_MOVESET_DIR [NEW_MOVESET_DIR]
//
// For every fighter file in OLD_MOVESET_DIR (e.g. a `git archive origin/main game/assets/movesets`
// export), every input the OLD engine could fire (moves[exact key] for button / dir+button /
// chord / button strings, plus specials parseSpecialInput can match) must still resolve to a move
// in the NEW data through the NEW engine (slots + loadout). Also presses each fighter's raw
// buttons and throw chords through TekkenBuffer.press(). Exit 1 on any failure.
// (docs/movesets/moveset_suite.mjs is stale — it fails identically on origin/main.)
import fs from 'fs';
import path from 'path';
const [, , oldDir, newDir = path.resolve('game/assets/movesets')] = process.argv;
const M = await import(path.resolve('game/js/movesets.js'));
globalThis.localStorage = { _s: {}, getItem(k) { return this._s[k] ?? null; }, setItem(k, v) { this._s[k] = String(v); } };

const BTN = /^(?:(?:f|b|u|d|d\/f|d\/b|u\/f|u\/b)\+)?[1-4](?:\+[1-4])*$/;
function oldFires(k, specials) {
  if (specials.has(k)) {
    const parts = k.split('+'); const b = [];
    while (parts.length && /^[1234]$/.test(parts[parts.length - 1])) b.unshift(parts.pop());
    if (b.length) return true;
  }
  const parts = k.split(',');
  return parts.every(p => BTN.test(p)) && parts.slice(1).every(p => /^[1-4]$/.test(p));
}
let fighters = 0, checked = 0;
const fails = [];
for (const f of fs.readdirSync(oldDir).filter(x => x.endsWith('.json') && x !== 'index.json').sort()) {
  const id = f.slice(0, -5);
  const old = JSON.parse(fs.readFileSync(path.join(oldDir, f), 'utf8'));
  if (!old || typeof old.moves !== 'object' || Array.isArray(old.moves)) continue;
  const nf = path.join(newDir, f);
  if (!fs.existsSync(nf)) { fails.push(`${id}: file missing in new data`); continue; }
  const neu = JSON.parse(fs.readFileSync(nf, 'utf8'));
  M.registerMoveset(id, neu);
  fighters++;
  const specials = new Set((old.specials || []).map(s => s && s.input).filter(Boolean));
  const excused = new Set(((neu.merge_sources || {}).owner_excluded_inputs) || []);
  for (const k of Object.keys(old.moves)) {
    if (!oldFires(k, specials)) continue;
    checked++;
    if (!M.getMove(id, k) && !excused.has(k)) fails.push(`${id}: input '${k}' fired a move before, resolves to nothing now`);
  }
  for (const b of ['1', '2', '3', '4', '1+3', '2+4']) {
    if (!old.moves[b]) continue;
    const buf = new M.TekkenBuffer(id);
    const n = buf.press(b);
    if (!n || !M.getMove(id, n)) fails.push(`${id}: press('${b}') -> ${n} (no move)`);
  }
}
console.log(`fighters ${fighters}, previously-firing inputs checked ${checked}, failures ${fails.length}`);
for (const x of fails.slice(0, 40)) console.log(' -', x);
process.exit(fails.length ? 1 : 0);
