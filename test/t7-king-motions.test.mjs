// Pantera King T7 dash / run moves (2026-11-10, t386u pass 3). Node, no browser, no touchscreen.
// Run: node --test test/t7-king-motions.test.mjs
// tools/anim/t7_move_resolve.py --motions maps f,F+X / f,f,n,X / f,f,f+X on King's own link tables (stance cancel
// 0x8001 -> Kg_sDASHF; dash f+X / n+X; dash f -> sRUN__00F, then X) with the final move's damage + first active
// frame checked. This drives the stick frame by frame through the SAME path game.js runs (TekkenBuffer.noteDirection
// -> trySystemMotion on a new latch -> _tickState), presses the button (tryAttack), and asserts the resolved row and
// that the game's clip plan plays the exact King T7 motbin move.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const FT = await import(join(ROOT, 'game/js/frame-tables.js'));
await FT.frameTablesReady;
const q = console.log, qw = console.warn; console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
const bank = F.bankIdFor('pantera', 'pantera');
const clips = await T.loadT3Clips(THREE, bank);
await T.loadT3Clips(THREE, 't7_king');
await T.ensureT7Moves('pantera', THREE);
console.log = q; console.warn = qw;
const pack = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t7/king/moves.pack.json'), 'utf8'));
const DT = 1 / 60;

function pantera() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, _t3: { bank, clips },
    root: { position: { x: 0, y: 0, z: 0 } }, facing: 1, dead: false, stun: 0, onGround: true, brawler: false,
    state: 'idle', stateT: 0, vx: 0 });
  f.tekken = new M.TekkenBuffer('pantera');
  return f;
}
function drive(f, seq) {
  for (const [d, n] of seq) for (let i = 0; i < n; i++) {
    if (f.setStick) f.setStick(d);
    const had = f.tekken._dash; f.tekken.noteDirection(d, DT); const dl = f.tekken._dash;
    if (dl && dl !== had) f.trySystemMotion(dl.dir);
    f.stateT += DT; f._tickState(DT);
  }
}
const DASH_HELD = [['f', 2], ['n', 2], ['f', 3]];        // f, F (second tap held)
const DASH_N = [['f', 2], ['n', 2], ['f', 2], ['n', 3]];  // f, f, n
const RUN = [['f', 2], ['n', 2], ['f', 2], ['n', 2], ['f', 2]]; // f, f, f

const CASES = [
  ['f,F+1', DASH_HELD, '1', 'Kg_lygerlp00'],
  ['f,F+2', DASH_HELD, '2', 'Kg_p00'],
  ['f,F+4', DASH_HELD, '4', 'Kg_tkr01'],
  ['f,F+3+4', DASH_HELD, '3+4', 'Kg_dki10'],
  ['f,f,n,2', DASH_N, '2', 'Kg_p01'],
  ['f,f,f+3', RUN, '3', 'Kg_666lk'],
  ['f,f,f+3+4', RUN, '3+4', 'Kg_dki11'],
];

for (const [row, seq, btn, motbin] of CASES) {
  test(`stick ${seq.map(([d, n]) => d + 'x' + n).join(' ')} + ${btn} -> ${row} -> King T7 ${motbin}`, () => {
    const f = pantera(); drive(f, seq);
    assert.equal(f.tryAttack(btn), true, 'press must fire');
    assert.equal(f.state, 'attack');
    assert.equal(f.attackName, row);
    const p = f._attackClipPlan(f.attack, f.attackName);
    assert.ok(p && String(p.name).startsWith('t7:'), `${row}: plan ${p && p.name} is not King T7`);
    assert.equal(pack.moves[String(p.name).slice(3)].motbin_move, motbin);
  });
}

test('negatives: a plain 1 is the jab, not a dash move; f+1 (no dash) is not f,F+1', () => {
  const a = pantera(); assert.equal(a.tryAttack('1'), true); assert.notEqual(a.attackName, 'f,F+1');
  const b = pantera(); drive(b, [['f', 3]]); b.tryAttack('1'); assert.notEqual(b.attackName, 'f,F+1');
});

test('motion normalizer: exact, plus the ONE sourced alias (run third input held == tapped)', () => {
  assert.equal(T.t7NormMotion('f, F+1'), 'f,F+1');
  // Pass 4 (2026-11-10): the run move's third forward input is the dash's direction-STATE cancel
  // (Kg_sDASHF dir 0x40 at frame 12, req 0 -> sRUN__00F), so held F and tapped f reach the same move.
  for (const [x, want] of [['f,f,F+3', 'f,f,f+3'], ['f,f,F+3+4', 'f,f,f+3+4'], ['f,f,F+1', 'f,f,f+1'],
    ['f, f, F+4', 'f,f,f+4'], ['f,f,f+3', 'f,f,f+3']]) assert.equal(T.t7NormMotion(x), want, x);
  // Negatives: no blind case folding — a held SECOND input is the dash's own F+X, never folded;
  // lowercase f,f+X is not a dash move; F,f,f / f,F,f are not aliases; strings/singles never match.
  for (const x of ['f,F', '1,2', '1', 'd/f+1', 'f,F+1~t7.king', 'f,f+1', 'F,f,f+3', 'f,F,f+3', 'f,F,F+3',
    'f,f,F', 'f,f,F+5', 'b,b,B+3']) assert.equal(T.t7NormMotion(x), null, x);
  assert.notEqual(T.t7NormMotion('f,F+3'), T.t7NormMotion('f,f,f+3'));
});

// Real presses for the alias: third f HELD (20 frames) must play the SAME King T7 move as tapped.
const RUN_HELD = [['f', 2], ['n', 2], ['f', 2], ['n', 2], ['f', 20]];
for (const [btn, motbin] of [['3', 'Kg_666lk'], ['3+4', 'Kg_dki11']]) {
  test(`held third f (f,f,F+${btn}) -> same King T7 ${motbin} as tapped, never T3`, () => {
    const f = pantera(); drive(f, RUN_HELD);
    assert.equal(f.tryAttack(btn), true);
    const p = f._attackClipPlan(f.attack, f.attackName);
    assert.ok(p && String(p.name).startsWith('t7:'), `${f.attackName}: plan ${p && p.name} is not King T7`);
    assert.equal(pack.moves[String(p.name).slice(3)].motbin_move, motbin);
  });
}
test('negative: f,F+3 (dash, second input held) is NOT routed to the run move', () => {
  const f = pantera(); drive(f, DASH_HELD); f.tryAttack('3');
  const p = f._attackClipPlan(f.attack, f.attackName);
  assert.ok(!(p && String(p.name).startsWith('t7:') && pack.moves[String(p.name).slice(3)].motbin_move === 'Kg_666lk'));
});

test('gated dash follow-up stays out with its reason (no substitute)', () => {
  assert.match(pack.skipped['f,F+2,1~t7.king'], /plausibility gate/);
});
