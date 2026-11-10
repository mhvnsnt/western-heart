// Tekken RUN locomotion for Pantera (King T7), 2026-11-10 pass 5. Node, no browser, no touchscreen, no model proof.
// Run: node --test test/tekken-run-pantera.test.mjs
// Source (King's T7 motbin kinmot.json): dash Kg_sDASHF cancel stick-f STATE at frame [12,12], requirement 0 ->
// sRUN__00F; run chain by each move's end: 00F (Bco_run00) -> 01F (Bco_run01) -> 02F (Bco_run02) -> 03F (Bco_run01)
// <-> 02F; exits b -> sWALK_00B and d|d/b|d/f -> crouch (requirement 0). Locomotion only: run-ATTACK recognition is
// tested in t7-king-motions.test.mjs and is not asserted here.
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
const q = console.log, qw = console.warn; console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
await T.loadT3Clips(THREE, 't7_king');
console.log = q; console.warn = qw;
const DT = 1 / 60;
const clip = (s) => JSON.parse(readFileSync(join(ROOT, `game/assets/anim/t3/t7_king/t3_${s}.json`), 'utf8'));
const travel = (s) => { const rt = clip(s).root_t; return rt[rt.length - 1][0] - rt[0][0]; };

function pantera() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, root: { position: { x: 0, y: 0, z: 0 } },
    facing: 1, dead: false, stun: 0, onGround: true, brawler: false, state: 'idle', stateT: 0, vx: 0 });
  f.tekken = new M.TekkenBuffer('pantera');
  return f;
}
// One frame of game.js's order: stick -> latch -> system motion -> crouch -> state tick.
function frame(f, d) {
  f.setStick(d);
  const had = f.tekken._dash; f.tekken.noteDirection(d, DT); const dl = f.tekken._dash;
  if (dl && dl !== had) f.trySystemMotion(dl.dir);
  f.tryCrouch(d === 'd' || d === 'd/b' || d === 'd/f');
  f.stateT += DT; f._tickState(DT);
}
const press = (f, seq) => { for (const [d, n] of seq) for (let i = 0; i < n; i++) frame(f, d); };
const DASH = [['f', 2], ['n', 2], ['f', 1]];

test('run clips: King T7 Bco_run00/01/02, same skeleton as the bank, forward = +x', () => {
  assert.deepEqual(F.TEKKEN_RUN.t7_king.chain, ['runStart', 'runA', 'runB']);
  for (const [s, anim] of [['run_start', 'Bco_run00'], ['run_a', 'Bco_run01'], ['run_b', 'Bco_run02']]) {
    assert.match(JSON.stringify(clip(s).t7_source || clip(s).source), new RegExp(anim));
    assert.ok(travel(s) > 1.5, `${s} travels forward (${travel(s)})`);
  }
});

test('f,f then HOLD f: the dash becomes the run at dash frame 12 and the chain plays start -> a -> b -> a', () => {
  const f = pantera(); press(f, DASH); assert.equal(f.state, 'tekdash');
  press(f, [['f', 10]]); assert.equal(f.state, 'tekdash', 'no run before frame 12');
  press(f, [['f', 2]]); assert.equal(f.state, 'tekrun', 'run at frame 12'); assert.equal(f._tekRun.name, 'runStart');
  const names = new Set();
  for (let i = 0; i < 31 + 15 + 15 + 3; i++) { frame(f, 'f'); names.add(f._tekRun && f._tekRun.name); }
  assert.equal(f.state, 'tekrun'); assert.deepEqual([...names].sort(), ['runA', 'runB', 'runStart'].sort());
  assert.ok(f.root.position.x > 1.0 + travel('run_start'), `run travels on the clips' own root (x=${f.root.position.x})`);
});

test('negatives: dash released before frame 12 never runs; f re-pressed after 12 does not run (window [12,12])', () => {
  const a = pantera(); press(a, DASH); press(a, [['n', 40]]);
  assert.notEqual(a.state, 'tekrun'); assert.equal(a.state, 'idle');
  const b = pantera(); press(b, DASH); press(b, [['n', 12], ['f', 20]]); assert.notEqual(b.state, 'tekrun');
  const c = pantera(); press(c, [['f', 40]]); assert.notEqual(c.state, 'tekrun', 'a held f without a dash is a walk');
  const k = pantera(); press(k, [['b', 2], ['n', 2], ['b', 1], ['b', 20]]); assert.notEqual(k.state, 'tekrun');
});

test('run exits (requirement 0): b -> idle (walk back), d / d/b / d/f -> crouch; release f ends at the clip end', () => {
  const go = () => { const f = pantera(); press(f, DASH); press(f, [['f', 20]]); assert.equal(f.state, 'tekrun'); return f; };
  const b = go(); press(b, [['b', 1]]); assert.equal(b.state, 'idle');
  for (const d of ['d', 'd/b', 'd/f']) { const c = go(); press(c, [[d, 1]]); assert.equal(c.state, 'crouch', d); }
  const n = go(); press(n, [['n', 1]]); assert.equal(n.state, 'tekrun', 'release does not stop mid-clip');
  press(n, [['n', 40]]); assert.equal(n.state, 'idle', 'release ends at the current clip end');
});

test('a button during the run fires an attack (cancel), recognition itself is not asserted here', () => {
  const f = pantera(); press(f, DASH); press(f, [['f', 20]]); assert.equal(f.state, 'tekrun');
  assert.equal(f.tryAttack('3'), true); assert.equal(f.state, 'attack');
});
