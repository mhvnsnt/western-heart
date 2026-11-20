// ss2u-dir-hold.test.mjs — Demonio SS.2,U batch-13 regression proof (loop run 2026-10-29).
// The full-fight sweep trace could not be produced in this environment (page-load stalls
// recorded in LOOP-STATE.md), so this test proves the same mechanism headlessly with the
// repo's own game code, in the shape of the existing node tests (test/attack-anim.test.mjs):
//   1. the REAL Fighter._dirHoldUpgrade (game/js/fighter.js), driven frame by frame through
//      the REAL setStick entry point, on a prototype instance (the attack-anim pattern —
//      no 3D scene, no models, no fight load);
//   2. the REAL resolveMoveKey rows for Demonio (game/assets/movesets/demonio.json);
//   3. the sweep-page contract itself: test/e2e/moveset-sweep.page.js must hold a capital
//      direction-only step 12f, and 12f at 60 Hz must clear the fighter's 0.08 s threshold
//      while the old flat 4f hold could not.
// Run in CI: game-unit-tests runs every test/*.test.mjs in node against the real tree.
// Scope, stated plainly: this proves the upgrade mechanism and the hold duration the sweep
// now applies. It does not run a full 3D fight, so the live sweep trace for SS.2,U remains
// the final end-to-end confirmation if the loop ever gets a working fight harness again;
// the PR body says exactly that.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(join(ROOT, 'game/js/movesets.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));

await M.loadFighterMovesets();
const [demonio] = await M.ensureMovesets(['demonio']);
assert.ok(demonio && demonio.moves, 'demonio moveset did not load');

const tappedKey = M.resolveMoveKey('demonio', 'SS.2:u');
const heldKey = M.resolveMoveKey('demonio', 'SS.2,U');

// Fighter source + sweep page source, read from the tree under test (same pattern as
// test/input-timing.test.mjs reading game.js for its constants).
const fighterSrc = readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
const pageSrc = readFileSync(join(ROOT, 'test/e2e/moveset-sweep.page.js'), 'utf8');

function freshFighter() {
  // tryDirFollow('u') after SS.2 queues the tapped spelling first and arms _dirFollowQ
  // with the lowercase stick direction and the clock at press time; _dirHoldUpgrade then
  // swaps the queued row for the held row once the stick has been held long enough.
  const f = Object.create(F.Fighter.prototype);
  f._movesetId = 'demonio';
  f._dirFollowQ = { c: tappedKey, b: 'SS.2', sep: ':', d: 'u', t: 0 };
  f._queuedNext = tappedKey;
  f._queuedAfter = null;
  f.state = 'idle';
  f.attack = null;
  f.attackName = null;
  f._clock = 0;
  return f;
}

test('Demonio has both the tapped and held SS.2 rows, and they are different rows', () => {
  assert.ok(tappedKey, 'SS.2:u does not resolve for demonio');
  assert.ok(heldKey, 'SS.2,U does not resolve for demonio');
  assert.notEqual(heldKey, tappedKey, 'held row must differ from tapped row');
});

test('fighter threshold is 0.08 s and the sweep page holds capital dir-only steps 12f', () => {
  const tm = /-\s*dq\.t\s*<\s*([0-9.]+)/.exec(fighterSrc);
  assert.ok(tm, '_dirHoldUpgrade threshold not found in fighter.js');
  const threshold = Number(tm[1]);
  assert.equal(threshold, 0.08, `fighter threshold changed: ${threshold}`);
  const hm = /test\(h\.dir\)\s*\?\s*(\d+)\s*:\s*(\d+)/.exec(pageSrc);
  assert.ok(hm, 'capital dir-only hold not found in moveset-sweep.page.js');
  const capitalHold = Number(hm[1]);
  const lowerHold = Number(hm[2]);
  assert.equal(capitalHold, 12, `capital dir-only hold is ${capitalHold}f, not 12f`);
  assert.equal(lowerHold, 4, `lowercase dir-only hold changed: ${lowerHold}f`);
  // Frame arithmetic at 60 Hz: the old 4f hold ends at 4/60 = 0.067 s, under the
  // 0.08 s window, so the upgrade could never fire; 12f reaches 0.20 s, past it.
  assert.ok(4 / 60 < threshold, 'old 4f hold would already clear the threshold');
  assert.ok(12 / 60 > threshold, 'new 12f hold does not clear the threshold');
});

test('4f of held stick never upgrades the queued row (the old sweep behaviour)', () => {
  const f = freshFighter();
  for (let frame = 1; frame <= 4; frame++) {
    f._clock = frame / 60;
    f.setStick('u');
    assert.equal(f._queuedNext, tappedKey, `upgraded too early at frame ${frame}`);
  }
  assert.equal(f._dirFollowQ.held, undefined, 'held flag set inside the 4f window');
});

test('12f of held stick upgrades the queued row to the held row (the fix)', () => {
  const f = freshFighter();
  for (let frame = 1; frame <= 12; frame++) {
    f._clock = frame / 60;
    f.setStick('u');
    if (frame <= 4) assert.equal(f._queuedNext, tappedKey, `upgraded too early at frame ${frame}`);
    if (frame >= 5) assert.equal(f._queuedNext, heldKey, `not upgraded by frame ${frame}`);
  }
  assert.equal(f._dirFollowQ.held, true, 'held flag not set after upgrade');
  assert.equal(f._dirFollowQ.c, heldKey, 'dirFollowQ not retargeted to the held row');
  // Still holding after the upgrade keeps the held row (no flip-flop).
  f._clock = 13 / 60;
  f.setStick('u');
  assert.equal(f._queuedNext, heldKey);
});

test('below-threshold hold does not upgrade, above-threshold hold does (direct)', () => {
  const early = freshFighter();
  early._clock = 0.05;
  early.setStick('u');
  assert.equal(early._queuedNext, tappedKey, '0.05 s hold upgraded the row');
  const late = freshFighter();
  late._clock = 0.2;
  late.setStick('u');
  assert.equal(late._queuedNext, heldKey, '0.20 s hold did not upgrade the row');
});
