// INPUT-TO-MOVE FIDELITY — pure-logic test (no browser).
// Drives TekkenBuffer + the real moveset JSON through the full Tekken input
// matrix and asserts every input resolves to its specific, predictable move.
// node tools/input-verify/buffer-test.mjs [fighterId]  (default: torch)
import { readFile } from 'fs/promises';
import { TekkenBuffer, registerMoveset, resolveMove, resolveMoveKey } from '../../../../pwtmp/ms-test.mjs';

const fid = process.argv[2] || 'torch';
// Per-fighter expectations: fighters whose data genuinely lacks a move get an
// INFO (data gap for a later batch), not a FAIL. The engine is proven by the
// pilot (torch); the sweep measures data coverage.
const EXPECT = {
  torch:   { dash2: 'Headless Horseman', strings: ['1,2', '1,2,2', '2,1', 'f+2,1'], qcf2: true,
             // Canon: T7 Anna has NO SS.1 / SS.4 (docs/t7t8-reference/frame-data-t7/anna.json:
             // sidestep moves are SS.2 Chaos Tail, SS.3 Heel Mash, SS.1+2 Bloody Chaos).
             // Sidestep+1 / sidestep+4 fall through to neutral — Tekken-correct.
             skip: ['SS.1', 'SS.4'] },
  pantera: { dash2: 'Beast Elbow', strings: ['1,2', '2,1'], qcf2: false },
  demonio: { dash2: "Demon's Paw", strings: ['1,2'], qcf2: false },
};
const exp = EXPECT[fid] || { dash2: null, strings: [], qcf2: false };
const STRICT = fid === 'torch'; // pilot gets strict assertions; others get coverage-aware info
const data = JSON.parse(await readFile(new URL(`../../game/assets/movesets/${fid}.json`, import.meta.url)));
registerMoveset(fid, data);
console.log(`${fid}: ${Object.keys(data.moves).length} moves, ${Object.keys(data.slots || {}).length} slots`);

let pass = 0, fail = 0;
const results = [];
function check(label, actual, expected) {
  const ok = actual === expected;
  ok ? pass++ : fail++;
  results.push(`${ok ? 'PASS' : 'FAIL'} ${label}: got ${JSON.stringify(actual)}${ok ? '' : `, want ${JSON.stringify(expected)}`}`);
}
function checkMove(label, notation, wantKey) {
  const r = resolveMove(fid, notation);
  check(`${label} resolves`, r && r.key, wantKey);
  check(`${label} has move`, !!(r && r.move && r.move.name), true);
}
const buf = () => new TekkenBuffer(fid);

// ---- 1. determinism: same input 3x -> identical notation ----
for (const b of ['1', '2', '3', '4']) {
  const seen = new Set();
  for (let i = 0; i < 3; i++) seen.add(buf().press(b, {}));
  check(`determinism press '${b}' x3`, seen.size, 1);
}
// ---- 2. distinctness: 1/2/3/4 -> four distinct notations ----
check('1/2/3/4 distinct', new Set(['1', '2', '3', '4'].map(b => buf().press(b, {}))).size, 4);
// ---- 3. singles resolve to a real move each (slot key may differ from notation) ----
for (const b of ['1', '2', '3', '4']) {
  const n = buf().press(b, {});
  const r = n && resolveMove(fid, n);
  check(`single '${b}' -> '${n}' has named move`, !!(r && r.move && r.move.name), true);
  if (r) results.push(`  info single '${b}' -> notation '${n}' key '${r.key}' name '${r.move.name}'`);
}
// ---- 4. chords (strict for pilot; coverage-aware elsewhere) ----
for (const c of ['1+2', '3+4', '1+3', '2+4', '1+4', '2+3']) {
  const b = buf();
  const n = b.pressChord(c, {});
  const r = n && resolveMove(fid, n);
  if (STRICT || resolveMoveKey(fid, c)) {
    check(`chord '${c}' -> move`, !!(r && r.move), true);
  } else {
    results.push(`  info '${fid}' lacks chord '${c}' (data gap)`);
  }
  if (n && r) results.push(`  info chord '${c}' -> notation '${n}' key '${r.key}' name '${r.move.name}'`);
}
// ---- 5. directionals: stick + button (coverage-aware) ----
function dirCheck(label, dir, btn, want) {
  const b = buf(); b.lastDir = dir;
  const got = b.press(btn, {});
  if (STRICT || resolveMoveKey(fid, want)) check(label, got, want);
  else results.push(`  info '${fid}' lacks '${want}' (falls through to '${got}')`);
}
for (const [btn, want] of [['1', 'f+1'], ['2', 'f+2'], ['3', 'f+3'], ['4', 'f+4']]) {
  dirCheck(`f+${btn}`, 'f', btn, want);
}
for (const [dir, btn, want] of [['d', '1', 'd+1'], ['d/f', '2', 'd/f+2'], ['d/b', '4', 'd/b+4'], ['b', '1', 'b+1'], ['u/f', '4', 'u/f+4']]) {
  dirCheck(`${dir}+${btn}`, dir, btn, want);
}
// ---- 6. states (strict for the pilot; info elsewhere) ----
function stateCheck(label, got, want) {
  if (STRICT) {
    if ((exp.skip || []).includes(want)) {
      // Canon-absent notation: Tekken-correct behavior is fall-through to neutral.
      check(`${label} falls through (canon: no ${want})`, got, want.replace(/^SS\./, ''));
      return;
    }
    check(label, got, want); return;
  }
  const slotKey = resolveMoveKey(fid, want);
  if (slotKey) check(`${label} (has slot)`, got, want);
  else results.push(`  info '${fid}' lacks '${want}' (data gap; falls through)`);
}
{
  const bc = buf(); stateCheck('WS.2', bc.press('2', { rising: true, inMove: false }), 'WS.2');
  const bd = buf(); stateCheck('FC.3', bd.press('3', { crouching: true, inMove: false }), 'FC.3');
  const be = buf(); stateCheck('SS.2', be.press('2', { sidestep: true, inMove: false }), 'SS.2');
  const bf = buf(); stateCheck('BT.1', bf.press('1', { backturned: true, inMove: false }), 'BT.1');
  const bg = buf(); stateCheck('BT.2 (canon pair)', bg.press('2', { backturned: true, inMove: false }), 'BT.2');
  const bh = buf(); stateCheck('BT.4 (canon pair)', bh.press('4', { backturned: true, inMove: false }), 'BT.4');
  const bi = buf(); stateCheck('SS.1', bi.press('1', { sidestep: true, inMove: false }), 'SS.1');
  const bj = buf(); stateCheck('SS.4', bj.press('4', { sidestep: true, inMove: false }), 'SS.4');
}
// ---- 7. strings (per-fighter: only strings the data actually has) ----
{
  const b = buf();
  if (exp.strings.includes('1,2')) {
    b._recordMove('1');
    check("string '1' then '2' -> '1,2'", b.press('2', { inMove: true }), '1,2');
  }
  if (exp.strings.includes('1,2,2')) {
    check("string '1,2' then '2' -> '1,2,2'", b.press('2', { inMove: true }), '1,2,2');
  } else {
    results.push(`  info '${fid}' has no canned '1,2,2' (falls through to '2' — Tekken-correct)`);
  }
  if (exp.strings.includes('2,1')) {
    const b2 = buf(); b2._recordMove('2');
    check("string '2' then '1' -> '2,1'", b2.press('1', { inMove: true }), '2,1');
  }
  if (exp.strings.includes('f+2,1')) {
    const b3 = buf(); b3.lastDir = 'f'; b3._recordMove('f+2');
    check("string 'f+2' then '1' -> 'f+2,1'", b3.press('1', { inMove: true }), 'f+2,1');
  }
  // no continuation when the previous move is done
  const b4 = buf(); b4._recordMove('1'); b4.lastMoveT = performance.now() - 5000;
  check("stale string does not fire", b4.press('2', { inMove: false }), '2');
}
// ---- 8. motions: qcf+2 via injected history (if the fighter has one) ----
if (exp.qcf2) {
  const b = buf();
  // hist: newest..oldest = f, d/f, d  (game steps, newest at hi)
  b.hist.fill('n');
  b.hi = 10;
  b.hist[10] = 'f'; b.hist[9] = 'd/f'; b.hist[8] = 'd';
  b.lastDir = 'f';
  const n = b.press('2', {});
  check('qcf+2 motion', n, 'qcf+2');
} else {
  results.push(`  info '${fid}' has no qcf+2 (data gap)`);
}
// ---- 9. dash: f,F+2 via double-tap history; latch expires after 500ms wall-clock ----
{
  const b = buf();
  b.hist.fill('n');
  b.hi = 20;
  b.hist[20] = 'n'; b.hist[19] = 'f'; // noteDirection('f') -> hi=21:'f', 20:'n', 19:'f' = double tap
  b.noteDirection('f'); // latches the dash (wall-clock)
  b.lastDir = 'f';
  const dashN = b.press('2', {});
  const dashR = dashN && resolveMove(fid, dashN);
  if (exp.dash2) {
    check(`f,F+2 dash (fresh) fires ${exp.dash2}`, dashR && dashR.move && dashR.move.name, exp.dash2);
  } else {
    check('f,F+2 dash (fresh) fires a dash move', !!(dashR && dashR.move), true);
    if (dashR) results.push(`  info dash+2 -> '${dashN}' '${dashR.move.name}'`);
  }
  // expire the latch and clear the stale double-tap pattern (stick now held:
  // history fills with 'f', so no re-latch) -> plain f+2 must come out
  b._dash.until = performance.now() - 1;
  b.hist.fill('f');
  b.noteDirection('f');
  check('f+2 after dash expiry', b.press('2', {}), 'f+2');
}
// ---- 10. key-notation coverage: every core input resolves ----
const core = ['1','2','3','4','1+2','3+4','1+3','2+4','1+4','2+3',
  'f+1','f+2','f+3','f+4','b+1','b+2','b+3','b+4','d+1','d+2','d+3','d+4',
  'd/f+1','d/f+2','d/f+3','d/f+4','d/b+3','d/b+4','u+3','u+4','u/f+3','u/f+4',
  'WS.1','WS.2','WS.3','WS.4','FC.1','FC.2','FC.3','FC.4',
  'SS.1','SS.2','SS.3','SS.4','BT.1','BT.2','BT.3','BT.4',
  'f,F+2','f,F+3','f,F+4','qcf+1','qcf+2','qcf+3','qcf+4',
  '1,2','2,1','1,2,2','f+2,1','1,2,4','2,2','1,4','3,3'];
const missing = core.filter(n => !resolveMoveKey(fid, n) && !(exp.skip || []).includes(n));
if ((exp.skip || []).length) results.push(`  info '${fid}' canon-skipped: ` + exp.skip.join(', '));
if (STRICT) {
  check('core coverage gaps', missing.length, 0);
  if (missing.length) results.push('  missing: ' + missing.join(', '));
} else {
  results.push(`  info '${fid}' core coverage gaps (${missing.length}): ` + (missing.join(', ') || 'none'));
}
// ---- 11. slots integrity: every slot value points at a real move ----
const bad = Object.entries(data.slots || {}).filter(([n, k]) => !data.moves[k]);
check('slots integrity', bad.length, 0);
if (bad.length) results.push('  bad slots: ' + bad.slice(0, 5).map(([n]) => n).join(', '));

for (const r of results) console.log(r);
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
