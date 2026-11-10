// Tekken dash / backdash for Pantera (King T7) — 2026-11-10 Pantera-first audit. Node, no browser.
// Run: node --test test/tekken-dash-pantera.test.mjs
// Owner: "KBD, ffd ... run and dash gone or not working". The stick double-tap latch only
// started KOF `system` rows and Pantera has none, so f,f / b,b did nothing. This drives the
// SAME path game.js runs every frame — TekkenBuffer.noteDirection(stick, dt), then
// trySystemMotion(latch.dir) on a NEW latch — at 60 fps, then ticks _tickState and asserts
// the travel equals King T7's own clip root travel at the motbin end frame (30).
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
const quiet = console.log, qw = console.warn; console.log = () => {}; console.warn = () => {};
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
await T.loadT3Clips(THREE, 't7_king');
console.log = quiet; console.warn = qw;

const DT = 1 / 60;
const clipRoot = (slot) => JSON.parse(readFileSync(join(ROOT, `game/assets/anim/t3/t7_king/t3_${slot}.json`), 'utf8')).root_t;
const fwdAt = (rt, frame) => rt[Math.min(frame, rt.length - 1)][0] - rt[0][0];

function pantera(facing = 1) {
  const f = Object.create(F.Fighter.prototype);
  f.char = { id: 'pantera' }; f._movesetId = 'pantera'; f.t3actions = {};
  f.root = { position: { x: 0, y: 0, z: 0 } };
  f.facing = facing; f.dead = false; f.stun = 0; f.onGround = true; f.brawler = false;
  f.state = 'idle'; f.stateT = 0; f.vx = 0;
  f.tekken = new M.TekkenBuffer('pantera');
  return f;
}
// One frame of game.js's input step (the exact latch logic) + the fighter's state tick.
function frame(f, stick) {
  const had = f.tekken._dash; f.tekken.noteDirection(stick, DT); const dl = f.tekken._dash;
  if (dl && dl !== had) f.trySystemMotion(dl.dir);
  f.stateT += DT; f._tickState(DT);
}
const press = (f, seq) => { for (const [d, n] of seq) for (let i = 0; i < n; i++) frame(f, d); };

test('own-slot bank is King T7 and the sourced end frames are 30/30', () => {
  assert.equal(F.ownSlotBankFor('pantera'), 't7_king');
  assert.deepEqual(F.TEKKEN_DASH_END_FRAMES.t7_king, { f: 30, b: 30 });
});

test('f,f starts the Tekken forward dash and travels King\'s dash_fwd root distance', () => {
  const f = pantera();
  press(f, [['f', 2], ['n', 2], ['f', 1]]);
  assert.equal(f.state, 'tekdash', 'f,f must start the dash');
  assert.equal(f._tekDash.name, 'dash');
  press(f, [['n', 40]]);
  assert.equal(f.state, 'idle', 'dash ends at the motbin end frame');
  const want = fwdAt(clipRoot('dash_fwd'), 30);
  assert.ok(Math.abs(f.root.position.x - want) < 0.03, `x=${f.root.position.x} want ~${want}`);
  assert.ok(want > 1.3, 'King dash covers ~1.41 m');
});

test('b,b starts the backdash (no invulnerability) and travels backwards; mirrored when facing -1', () => {
  for (const facing of [1, -1]) {
    const f = pantera(facing); f.invuln = 0;
    press(f, [['b', 2], ['n', 2], ['b', 1]]);
    assert.equal(f.state, 'tekdash'); assert.equal(f._tekDash.name, 'backdash');
    assert.equal(f.invuln, 0, 'a Tekken backdash is not invulnerable');
    press(f, [['n', 40]]);
    const want = fwdAt(clipRoot('backdash'), 30) * facing;
    assert.ok(want * facing < -0.5);
    assert.ok(Math.abs(f.root.position.x - want) < 0.03, `facing ${facing}: x=${f.root.position.x} want ~${want}`);
  }
});

test('negatives: single f tap, held f, f then b, and a dash while airborne do NOT dash', () => {
  for (const seq of [[['f', 1], ['n', 30]], [['f', 40]], [['f', 2], ['n', 2], ['b', 2], ['n', 30]]]) {
    const f = pantera(); press(f, seq);
    assert.notEqual(f.state, 'tekdash'); assert.equal(f.root.position.x, 0);
  }
  const air = pantera(); air.onGround = false;
  assert.equal(air.trySystemMotion('f'), false);
});

test('a button can cancel the dash from frame 1 (motbin 1/2/3/4 cancels, window [1, 32767])', () => {
  const f = pantera();
  press(f, [['f', 2], ['n', 2], ['f', 1]]);
  assert.equal(f.state, 'tekdash');
  assert.equal(f.tekDashCancelable, true);
  assert.equal(f.tryAttack('1'), true, '1 during the dash must fire a dash move');
  assert.equal(f.state, 'attack');
  // Resolves the dash move f,F+1 (Jaguar Hook). Since pass 3 (test/t7-king-motions.test.mjs) the row plays
  // King's real T7 Kg_lygerlp00 (the dash's own f+1 cancel); the plain dash+1 -> Kg_jprk00F cancel in the motbin
  // is requirement-gated and is NOT Jaguar Hook (earlier lead corrected).
  assert.equal(f.attackName, 'f,F+1');
  assert.equal(f._tekDash, null, 'leaving the dash clears it');
});
