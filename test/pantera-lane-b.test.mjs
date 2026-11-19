// Lane B — Pantera engine: movement + strings (2026-11-18). Node, no browser.
// Run: node --test test/pantera-lane-b.test.mjs
// Covers the owner 2026-11-11 report ("only the punch combos are working") and the WR gaps:
//  - kick strings at real-time input: a d/f-held d/f+4,3 (and d/f+4,3,4, b+2,4, 1+2,3,
//    d+3+4,4) must resolve the STANDING directional opener and continue, never the FC. row
//    and never the two-finger chord rescue (d/f+3+4 / 3+4) that hijacked the follow-up;
//  - fresh crouch vs held crouch: a direction+button pressed as one gesture (< 15 f) is the
//    standing directional; a deliberately held crouch (>= 15 f) still gives FC. rows; a
//    backdash-cancel crouch is established at once;
//  - WR attacks: a button pressed during a real run fires the WR. row (WR.1+2), not f+1+2 —
//    including at run entry (dash frame 12), where the buffer's running() latch is still false;
//  - BT engine: entry via a BT-ending move, BT.1 resolution while back-turned, clearing on
//    crouch / jump / sidestep.
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
await T.ensureT7Moves('pantera', THREE);
console.log = q; console.warn = qw;
const DT = 1 / 60;

function pantera() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, _t3: { bank, clips },
    root: { position: { x: 0, y: 0, z: 0 } }, facing: 1, dead: false, stun: 0, onGround: true,
    brawler: false, state: 'idle', stateT: 0, vx: 0, _clock: 0 });
  f.tekken = new M.TekkenBuffer('pantera');
  f._opp = null;
  return f;
}
// One frame of game.js's order: stick -> latch -> system motion -> crouch -> state tick.
function frame(f, d) {
  f.setStick(d);
  const had = f.tekken._dash; f.tekken.noteDirection(d, DT); const dl = f.tekken._dash;
  if (dl && dl !== had) f.trySystemMotion(dl.dir);
  f.tryCrouch(d === 'd' || d === 'd/b' || d === 'd/f');
  f._clock = (f._clock || 0) + DT;
  f.stateT += DT; f._tickState(DT);
}
const press = (f, seq) => { for (const [d, n] of seq) for (let i = 0; i < n; i++) frame(f, d); };
// Drive frames until the fighter is idle again (attack done) or the cap.
function untilIdle(f, cap = 300) { for (let i = 0; i < cap && f.state !== 'idle'; i++) frame(f, 'n'); return f.state; }
// A string chain: first button, 6 frames in, next button(s), then 40 frames; returns the final attackName.
function chain(f, first, rest) {
  f.tryAttack(first);
  for (const b of rest) { press(f, [['n', 6]]); f.tryAttack(b); }
  press(f, [['n', 40]]);
  return f.attackName;
}

test('kick strings: d/f+4,3 resolves the standing opener and continues, stick held and neutral', () => {
  const held = pantera();
  press(held, [['d/f', 3]]);
  assert.equal(held.tryAttack('4') && held.attackName, 'd/f+4', 'held d/f+4 is the standing kick, not FC.d/f+4');
  press(held, [['d/f', 6]]); held.tryAttack('3'); press(held, [['d/f', 40]]);
  assert.equal(held.attackName, 'd/f+4,3', 'held follow-up is the string, not the d/f+3+4 chord rescue');
  const neutral = pantera();
  press(neutral, [['d/f', 3]]);
  assert.equal(neutral.tryAttack('4') && neutral.attackName, 'd/f+4');
  press(neutral, [['n', 6]]); neutral.tryAttack('3'); press(neutral, [['n', 40]]);
  assert.equal(neutral.attackName, 'd/f+4,3', 'neutral follow-up is the string, not the 3+4 chord rescue');
});

test('kick strings: d/f+4,3,4 / b+2,4 / 1+2,3 / d+3+4,4 all continue; 1,2 control', () => {
  const three = pantera();
  press(three, [['d/f', 3]]);
  three.tryAttack('4'); press(three, [['n', 6]]); three.tryAttack('3');
  press(three, [['n', 20]]); three.tryAttack('4'); press(three, [['n', 40]]);
  assert.equal(three.attackName, 'd/f+4,3,4');
  const b = pantera();
  press(b, [['b', 3]]);
  assert.equal(chain(b, '2', ['4']), 'b+2,4');
  const e = pantera();
  assert.equal(chain(e, '1+2', ['3']), '1+2,3');
  const d = pantera();
  press(d, [['d', 3]]);
  assert.equal(chain(d, '3+4', ['4']), 'd+3+4,4');
  const c = pantera();
  assert.equal(chain(c, '1', ['2']), '1,2', 'punch control still works');
});

test('fresh crouch vs held crouch: gesture gives the standing directional, held gives FC.', () => {
  const fresh = pantera();
  press(fresh, [['d/f', 3]]);
  assert.equal(fresh.tryAttack('4') && fresh.attackName, 'd/f+4', '3-frame d/f hold is one gesture');
  const held = pantera();
  press(held, [['d/f', 30]]);
  assert.equal(held.tryAttack('4') && held.attackName, 'FC.d/f+4', '30-frame d/f hold is an established crouch');
  const neutral = pantera();
  assert.equal(neutral.tryAttack('4') && neutral.attackName, '4', 'neutral 4 is the plain kick');
});

test('backdash-cancel crouch is established at once: FC. resolves immediately', () => {
  const f = pantera();
  press(f, [['b', 2], ['n', 2], ['b', 1]]);
  assert.equal(f.state, 'tekdash', 'b,b is the backdash');
  press(f, [['d/f', 2]]);
  assert.equal(f.state, 'crouch', 'd/f cancels the backdash into crouch');
  assert.equal(f.tryAttack('4') && f.attackName, 'FC.d/f+4', 'KBD crouch is not a fresh gesture');
});

test('WR attacks: 1+2 during a real run fires WR.1+2, not f+1+2 — even at run entry', () => {
  const f = pantera();
  press(f, [['f', 2], ['n', 2], ['f', 1], ['f', 12]]);
  assert.equal(f.state, 'tekrun', 'run entered at dash frame 12');
  assert.equal(f._inputCtx().running, true, 'the run state itself counts as running (buffer latch still false)');
  assert.equal(f.tryAttack('1+2') && f.attackName, 'WR.1+2', 'running 1+2 is the WR move');
  // WR.4 has no row in pantera.json yet (Lane A data spec) — the engine fix cannot complete it
  // until the row exists. This assertion documents the gap; update it when the row lands.
  assert.equal(M.resolveMoveKey('pantera', 'WR.4'), null, 'no WR.4 row yet');
});

test('BT engine: FC.1+2 ends back-turned, BT.1 resolves, crouch/jump/sidestep clear it', () => {
  const enterBT = () => {
    const f = pantera();
    press(f, [['d/f', 30]]);
    assert.equal(f.tryAttack('1+2') && f.attackName, 'FC.1+2');
    assert.equal(untilIdle(f), 'idle', 'FC.1+2 completes');
    assert.equal(f._bt, true, 'the move ends back-turned');
    return f;
  };
  const f = enterBT();
  assert.equal(f.tryAttack('1') && f.attackName, 'BT.1', 'BT.1 resolves while back-turned');
  f.tryCrouch(true); frame(f, 'd/f');
  assert.equal(f._bt, false, 'crouching from back-turned turns you around');
  const j = enterBT();
  j.tryJump();
  assert.equal(j._bt, false, 'a jump turns you around');
  const s = enterBT();
  s.trySidestep(1);
  assert.equal(s._bt, false, 'a sidestep turns you around');
});
