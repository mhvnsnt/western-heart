// Reconciliation verification: PR #1039 playable + PR #1048 t7_motbin layer.
// Adapted from PR #1039's test/mega-batch-t7.test.mjs (moveset checks only;
// #1039's tap-for-audio section is NOT included — that work lives in
// PRs #1042/#1037, not in this moveset-only reconciliation PR).
// Torch is NOT T8-purged here (#1039 never touched torch): the torch
// checks below assert its t7_motbin wiring only, never a purge.
// Run: node test/reconcile-1039-1048.test.mjs (from repo root).
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const PURGED = ['pantera', 'burger', 'demonio', 'diablo', 'kinpo', 'phantom', 'scimitar', 'skull'];
const ALL = [...PURGED, 'torch'];
const PLAYABLE = { pantera: 768, burger: 502, demonio: 671, diablo: 594, kinpo: 482, phantom: 834, scimitar: 329, skull: 634, torch: 892 };
const MOTBIN = { pantera: 2787, burger: 2325, demonio: 2227, diablo: 2480, kinpo: 2243, phantom: 2520, scimitar: 2099, skull: 2319, torch: 2335 };
const CHARACTER = { pantera: '[KING]', burger: '[BOB_SATSUMA]', demonio: '[JIN]', diablo: '[HEIHACHI]', kinpo: '[Asuka]', phantom: '[YOSHIMITSU]', scimitar: '[SHAHEEN]', skull: '[Bryan]', torch: '[ANNA]' };
let failures = 0;
const check = (cond, msg) => { if (!cond) { failures++; console.log('FAIL:', msg); } };

for (const f of ALL) {
  const p = join(root, 'game', 'assets', 'movesets', `${f}.json`);
  check(existsSync(p), `${f} moveset file exists`);
  const d = JSON.parse(readFileSync(p, 'utf8'));
  const moves = d.moves;
  check(Object.keys(moves).length === PLAYABLE[f], `${f}: ${Object.keys(moves).length} playable moves, expected ${PLAYABLE[f]}`);
  check(d.t7_motbin && d.t7_motbin.moves && d.t7_motbin.moves.length === MOTBIN[f],
    `${f}: t7_motbin moves ${d.t7_motbin && d.t7_motbin.moves && d.t7_motbin.moves.length}, expected ${MOTBIN[f]}`);
  check(d.t7_motbin && d.t7_motbin.character_name === CHARACTER[f],
    `${f}: t7_motbin character_name ${d.t7_motbin && d.t7_motbin.character_name}, expected ${CHARACTER[f]}`);
  // MOD body sync (in-file t7 block rule, same as #1039): wired +
  // numeric-single + non-throw => body damage equals t7.damage.
  let mism = 0;
  for (const [, v] of Object.entries(moves)) {
    if (v.t7 && v.t7.wired && !v.throw) {
      const td = v.t7.damage;
      const single = (typeof td === 'number' || (typeof td === 'string' && /^-?\d+(\.\d+)?$/.test(td)));
      if (single && Number(td) !== Number(v.damage)) mism++;
    }
  }
  check(mism === 0, `${f}: ${mism} body-vs-MOD damage mismatches remain`);
  // String-to-chord (#1039 definition): bare-chord t3_rows never in strings.
  const chordRows = new Set();
  for (const [k, v] of Object.entries(moves)) {
    if (/^[1234]\+[1234]$/.test(k) && v.t3_row != null) chordRows.add(v.t3_row);
  }
  let strChord = 0;
  for (const s of (d.strings || [])) {
    if (s && typeof s === 'object' && s.t3_rows && s.t3_rows.some((r) => chordRows.has(r))) strChord++;
  }
  check(strChord === 0, `${f}: ${strChord} strings map to chord rows`);
}
for (const f of PURGED) {
  const d = JSON.parse(readFileSync(join(root, 'game', 'assets', 'movesets', `${f}.json`), 'utf8'));
  const t8 = Object.entries(d.moves).filter(([, v]) => typeof v.anim_ref === 'string' && v.anim_ref.startsWith('t8:'));
  check(t8.length === 0, `${f}: ${t8.length} T8 anim refs remain in playable moves`);
  check(d.t8_quarantine_20261024 && Object.keys(d.t8_quarantine_20261024).length > 0,
    `${f}: quarantine section present with entries`);
}
const pantera = JSON.parse(readFileSync(join(root, 'game', 'assets', 'movesets', 'pantera.json'), 'utf8'));
check(pantera.moves['1'].damage === 9, `pantera LP1 body damage is ${pantera.moves['1'].damage}, expected 9 (MOD)`);

console.log(failures === 0 ? 'RECONCILE-1039-1048 PASS' : `RECONCILE-1039-1048 FAIL (${failures})`);
process.exit(failures === 0 ? 0 : 1);
