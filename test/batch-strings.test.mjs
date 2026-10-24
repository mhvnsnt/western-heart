// Batch string + moveset verification (2026-10-24, batch one-pass).
// User report: longest combo doable was 1-2 (LP1,RP2); 3+ hit strings broke.
// Root causes found (not guessed):
//  1. SHADOW KEYS broke chaining: slots['1'] = '1~t8.king' (MOD damage), so
//     lastMove became '1~t8.king' and continuation tried '1~t8.king,2'
//     (nonexistent) instead of '1,2'. Fix: continuation tries the stripped
//     base too ('1' -> '1,2', '1,2' -> '1,2,1').
//  2. Timing too tight for touch: grace 200ms, continuation 800ms.
//     Fix: grace 500ms, STRING_PENDING 1500ms.
//  3. Queued string hit dropped if recovery phase skipped (short move jumps
//     active->done in one tick). Fix: fire queued hit on completion.
// This test verifies:
//  1. The timing constants + shadow-strip code in the edited engine files.
//  2. Pantera (T7 King) string chains resolve to TRUE STRING moves (keys
//     containing ','), not separate singles — exactly as the fixed runtime
//     resolver does (lastMove + ',' + input, with ~shadow stripping).
//  3. No string maps to a chord row (LP1,RP2,LP1 != LP1+RP2 chord row).
//  4. Batch: mapped WH fighters' moveset files have moves + strings and
//     LP1/RP2/LK3/RK4 display inputs.
// Run: node test/batch-strings.test.mjs (from repo root; CI runs the loop).

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const failures = [];
const ok = (cond, msg) => { if (!cond) failures.push(msg); else console.log('  ok: ' + msg); };

// ---- 1. Engine fixes present in edited files ----
console.log('== engine string fixes ==');
const fighterJs = readFileSync(join(root, 'game', 'js', 'fighter.js'), 'utf8');
const movesetsJs = readFileSync(join(root, 'game', 'js', 'movesets.js'), 'utf8');
ok(fighterJs.includes('+ 500;') && fighterJs.includes('_stringGraceUntil'), 'fighter.js string grace is 500ms');
ok(/STRING_PENDING = 1500/.test(movesetsJs), 'movesets.js STRING_PENDING is 1500ms');
ok(movesetsJs.includes('now - this.lastMoveT < STRING_PENDING'), 'V2 contOk uses STRING_PENDING');
ok(movesetsJs.includes('performance.now() - this.lastMoveT < STRING_PENDING'), 'legacy contOk uses STRING_PENDING');
ok(movesetsJs.includes("this.lastMove.slice(0, tilde)") || movesetsJs.includes('slice(0, tilde)'),
  'movesets.js continuation strips ~shadow suffix');
ok(fighterJs.includes('if (this._queuedNext)') && fighterJs.includes('if (this._fireNotation(next)) break;'),
  'fighter.js fires queued string hit on move completion');

// ---- 2. Pantera string chains resolve to TRUE STRINGS ----
console.log('== Pantera (T7 King) string chains -> true string moves ==');
const panteraPath = join(root, 'game', 'assets', 'movesets', 'pantera.json');
if (!existsSync(panteraPath)) {
  failures.push('pantera.json missing from repo tree');
} else {
  const pantera = JSON.parse(readFileSync(panteraPath, 'utf8'));
  const slots = Object.assign({}, pantera.slots || {});
  for (const k of Object.keys(pantera.moves)) if (!(k in slots)) slots[k] = k;
  const resolve = (n) => { const k = slots[n]; return k && pantera.moves[k] ? k : null; };
  // Fixed continuation: try raw lastMove AND stripped base.
  const continuation = (lastMove, input) => {
    if (!lastMove) return null;
    const bases = [lastMove];
    const t = lastMove.indexOf('~');
    if (t > 0) bases.push(lastMove.slice(0, t));
    for (const base of bases) {
      for (const sep of [',', '~', ':']) {
        const c = base + sep + input;
        if (resolve(c)) return c;
      }
    }
    return null;
  };
  const chain = (steps) => {
    let last = null; const fired = [];
    for (const input of steps) {
      let key = null;
      if (last) key = continuation(last, input);
      if (!key) key = resolve(input);
      if (!key) return { ok: false, fired, failedAt: input, last };
      fired.push(key); last = key;
    }
    return { ok: true, fired };
  };
  const cases = [
    [['1', '2'], 'LP1,RP2', '1,2'],
    [['1', '2', '1'], 'LP1,RP2,LP1 Palm Strike Uppercut', '1,2,1'],
    [['1', '2', '1', '2+4'], 'LP1,RP2,LP1,RP2+RK4 Suplex', '1,2,1,2+4'],
    [['1', '2', '1', 'd+2+4'], 'LP1,RP2,LP1,d+RP2+RK4 V Driver', '1,2,1,d+2+4'],
    [['1', '2', '2+4'], 'LP1,RP2,RP2+RK4 Head Jammer', '1,2,2+4'],
    [['1', '2', 'd+2+4'], 'LP1,RP2,d+RP2+RK4 V Driver', '1,2,d+2+4'],
    [['2', '1'], 'RP2,LP1', '2,1'],
  ];
  for (const [steps, label, expectedFinal] of cases) {
    const r = chain(steps);
    const finalOk = r.ok && r.fired[r.fired.length - 1] === expectedFinal;
    ok(finalOk, `chain ${label} -> ${r.fired.join(' -> ')} (expected final ${expectedFinal})`);
  }
  // No string maps to a chord row.
  const stringKey = resolve('1,2,1');
  ok(stringKey === '1,2,1', `1,2,1 resolves to '${stringKey}', not a chord key`);
  // Animation status (info, not gating): T7 string moves with T3 rows vs T8-only.
  const t7strings = ['1,2', '1,2,1', '1,2,1,2+4', '1,2,1,d+2+4', '1,2,2+4', '1,2,d+2+4', '2,1'];
  let t3rows = 0, t8only = 0;
  for (const k of t7strings) {
    const m = pantera.moves[resolve(k) || k];
    if (!m) continue;
    if (m.t3_row) t3rows++;
    else if (String(m.anim_ref || '').startsWith('t8:')) t8only++;
  }
  console.log(`  info: Pantera T7 key strings: ${t3rows} with T3 rows, ${t8only} T8-only (UNMAPPED until T7 extraction lands; strings still fire with correct damage, animation is fallback)`);
}

// ---- 3. Batch: mapped fighters have moves + strings + LP1/RP2 display ----
console.log('== batch mapped fighters ==');
const MAP = {
  pantera: 'king', burger: 'bob', demonio: 'jin', diablo: 'heihachi',
  kinpo: 'asuka', phantom: 'yoshimitsu', scimitar: 'shaheen', skull: 'bryan',
};
for (const [fighter, t7] of Object.entries(MAP)) {
  const p = join(root, 'game', 'assets', 'movesets', `${fighter}.json`);
  if (!existsSync(p)) { failures.push(`${fighter}.json missing`); continue; }
  const data = JSON.parse(readFileSync(p, 'utf8'));
  const nMoves = Object.keys(data.moves || {}).length;
  const nStrings = (data.strings || []).length;
  ok(nMoves > 50, `${fighter} (T7 ${t7}): ${nMoves} moves`);
  ok(nStrings > 0, `${fighter} (T7 ${t7}): ${nStrings} strings listed`);
  const hasLp = Object.values(data.moves || {}).some(m => m.input_lp) ||
    (data.strings || []).some(s => s && s.input_lp);
  ok(hasLp, `${fighter}: LP1/RP2/LK3/RK4 display present`);
}

console.log('');
if (failures.length) {
  console.error('FAIL batch-strings:');
  for (const f of failures) console.error('  - ' + f);
  process.exit(1);
}
console.log('PASS batch-strings');
