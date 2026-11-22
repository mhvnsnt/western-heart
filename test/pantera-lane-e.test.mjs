// Lane E — regressions (2026-11-19). Node, no browser.
// Run: node --test test/pantera-lane-e.test.mjs
// R1 (Lane B regression, found by Lane D): FC.1+2 was unreachable by keyboard on df0e900.
// Lane D's exact live input — hold d 6 stepped frames, press 1+2 while still holding d —
// resolved d+1+2, and releasing d first resolved WS.1+2, so no keyboard path reached FC.1+2
// and BT entry was unproven. Root cause (T7 actual code, not a hand-tooled threshold):
// Lane B's fresh-crouch window was 15 f (0.25 s, a WH precedent); T7's crouch establishment
// is 6 f — the fastest universal while-rising input in T7 is "any Down for 6 frames, then
// Neutral+Attack" (wavu tech compendium, frame-perfect), and King's T7 graph
// (game/assets/anim/t7/king/graph.json) offers the crouch stance dwKAM_00D's button cancels
// from frame 1 while d+1+2 (Kg_WHummer) cancels from the STANDING stance Kg_sKAM00_, so
// FC. vs d+ is state-at-button-time with the state flipping at 6 f of down. The fix:
// FRESH_CROUCH_WINDOW_S 0.25 -> 6/60, with a 1e-9 epsilon because 6 accumulated 1/60 s
// ticks sum to 0.09999999999999999 in floating point (below 0.1; the same float-boundary
// bug made the old 15 f window need 16 f). A 3 f hold is still one gesture (standing
// directional, Lane B's kick-string fix intact); a 6 f hold is an established crouch.
// Ticks here mirror game.js _update order (tryCrouch BEFORE input consumption in the same
// tick, then fighter update) — that order is where the regression lived; the lane-B
// harness calls tryAttack between frames and never saw it.
// R2 (throw-chain 8/9 on df0e900) does NOT reproduce on current main: throw-chain.test.mjs
// is 9/9, and the break test passes on B-only, C-only, and merged fighter.js alike, so no
// engine change and no test change was made for it; that file is the R2 guard.
import test from 'node:test';
import assert from 'node:assert/strict';
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
const bank = 't7_king';
const clips = await T.loadT3Clips(THREE, bank);
await T.ensureT7Moves('pantera', THREE);
console.log = q; console.warn = qw;
const DT = 1 / 60;

function pantera() {
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { char: { id: 'pantera' }, _movesetId: 'pantera', t3actions: {}, _t3: { bank, clips },
    root: { position: { x: 0, y: 0, z: 0 } }, facing: 1, dead: false, stun: 0, onGround: true,
    brawler: false, state: 'idle', stateT: 0, vx: 0, _clock: 0,
    stats: { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 } });
  f.tekken = new M.TekkenBuffer('pantera');
  f._opp = null;
  f._animate = () => {};
  f.blob = { position: { x: 0, y: 0, z: 0 }, scale: { set() {} }, material: { opacity: 1 } };
  return f;
}
// One live tick in game.js _update order: stick -> tryMove -> tryCrouch ->
// noteDirection -> (consume actions -> tryAttack) -> fighter update.
function tick(f, d, act) {
  f.setStick(d);
  f.tryMove(0);
  f.tryCrouch(d === 'd' || d === 'd/b' || d === 'd/f');
  const had = f.tekken._dash; f.tekken.noteDirection(d, DT); const dl = f.tekken._dash;
  if (dl && dl !== had) f.trySystemMotion(dl.dir);
  if (act) f.tryAttack(act);
  f.update(DT, f._opp);
}
function holdThenPress(n, act, dir = 'd') {
  const f = pantera();
  for (let i = 0; i < n; i++) tick(f, dir, null);
  tick(f, dir, act);
  return f;
}
function untilIdle(f, cap = 400) { for (let i = 0; i < cap && f.state !== 'idle'; i++) tick(f, 'n', null); return f.state; }

test('FC.1+2 reachable by keyboard: hold d 6 frames (Lane D live input), press 1+2 with d held', () => {
  const f = holdThenPress(6, '1+2', 'd');
  assert.equal(f.attackName, 'FC.1+2', '6-frame d hold is an established crouch in T7, not a gesture');
  assert.equal(untilIdle(f), 'idle', 'FC.1+2 completes');
  assert.equal(f._bt, true, 'the move ends back-turned: BT entry restored');
});

test('fresh gesture still standing: hold d 0-5 frames + 1+2 resolves d+1+2, never FC.', () => {
  for (const n of [0, 1, 3, 5]) {
    const f = holdThenPress(n, '1+2', 'd');
    assert.equal(f.attackName, 'd+1+2', `${n}-frame d hold is one gesture (standing d+1+2)`);
  }
});

test('crouch establishment boundary is exactly 6 frames (float-safe): 6 -> FC, 30 -> FC', () => {
  assert.equal(holdThenPress(6, '1+2', 'd').attackName, 'FC.1+2', '6 accumulated 1/60 ticks must clear the window (epsilon)');
  assert.equal(holdThenPress(30, '1+2', 'd').attackName, 'FC.1+2', '30-frame hold is FC.');
  assert.equal(holdThenPress(6, '4', 'd/f').attackName, 'FC.d/f+4', '6-frame d/f hold is FC. for singles too');
});

test('kick-string fix intact in live order: d/f+4 at 3 f is standing, at 30 f is FC., string continues', () => {
  assert.equal(holdThenPress(3, '4', 'd/f').attackName, 'd/f+4', '3-frame d/f hold is one gesture');
  assert.equal(holdThenPress(30, '4', 'd/f').attackName, 'FC.d/f+4', '30-frame d/f hold is FC.');
  const f = holdThenPress(3, '4', 'd/f');
  for (let i = 0; i < 6; i++) tick(f, 'n', null);
  tick(f, 'n', '3');
  for (let i = 0; i < 40; i++) tick(f, 'n', null);
  assert.equal(f.attackName, 'd/f+4,3', 'the string continues from the standing opener');
});

test('release path unchanged: release d then 1+2 is WS.1+2 (T7-correct); after WS expiry it is plain 1+2', () => {
  const f = pantera();
  for (let i = 0; i < 30; i++) tick(f, 'd', null);
  tick(f, 'n', '1+2'); // release tick: tryCrouch(false) opens WS, then the press consumes it
  assert.equal(f.attackName, 'WS.1+2', 'releasing from an established crouch gives the while-standing move');
  const g = pantera();
  for (let i = 0; i < 30; i++) tick(g, 'd', null);
  tick(g, 'n', null);
  for (let i = 0; i < 30; i++) tick(g, 'n', null); // 0.5 s neutral: the 0.35 s WS window expired
  tick(g, 'n', '1+2');
  assert.equal(g.attackName, '1+2', 'once the WS window expires the press is the plain chord');
});
