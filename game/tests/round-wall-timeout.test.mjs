/* round-wall-timeout.test.mjs — Round ends on the WALL clock, not just sim time
 * (Piece 1 re-test Bug 2, 2026-11-08).
 *
 * The re-test: at ~1 fps one sim second takes ~30 wall seconds, so the
 * displayed clock hit 00 at 60 s wall while the sim timer still had most
 * of its 60 s left — the fight ran ~25 min past 00 with no TIME UP, no
 * round award, no result screen. Tekken rule (teardown spec: T7
 * tournament 60 s timer, TIME UP ends the round) and UR's rule (when the
 * condition expires the mission ENDS): the round ends on wall time too.
 *
 * Pattern follows test/input-timing.test.mjs: the wall-clock block is read
 * out of game/js/game.js itself (no three.js import) and driven with a
 * simulated slow clock, so this tests the real code text, not a copy.
 *
 * Run: node --test game/tests/round-wall-timeout.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const JS = join(dirname(fileURLToPath(import.meta.url)), '..', 'js');
const gameSrc = readFileSync(join(JS, 'game.js'), 'utf8');

const ROUND_TIME = Function(`return (${/const ROUND_TIME\s*=\s*([^;]+);/.exec(gameSrc)[1]});`)();

// Extract the wall-clock block at the top of _loop: from the
// `if (this.running && !this.paused && this._roundWallLast != null) {`
// through its matching close brace, plus the `this._roundWallLast = now;`
// line that follows it. Brace-count so the extraction survives edits
// inside the block.
function extractWallBlock(src) {
  // The if-condition differs between the old code (which also required
  // roundState === 'fight') and the fixed code (which handles 'fight'
  // and 'over' inside); match either so the test fails on the BEHAVIOR
  // on old code instead of on the extraction.
  const m = /if \(this\.running && !this\.paused && (?:this\.roundState === 'fight' && )?this\._roundWallLast != null\) \{/.exec(src);
  assert.ok(m, 'wall-clock block not found in game.js _loop');
  const start = m.index;
  let depth = 0, i = src.indexOf('{', start);
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) break; }
  }
  const close = i;
  const tail = src.indexOf('this._roundWallLast = now;', close);
  assert.ok(tail !== -1, '_roundWallLast update not found after wall-clock block');
  return src.slice(start, tail) + 'this._roundWallLast = now;';
}

const wallBlock = extractWallBlock(gameSrc);
const runWallBlock = new Function('now', 'ROUND_TIME', wallBlock);

function fakeGame(overrides = {}) {
  const g = {
    running: true, paused: false, roundState: 'fight',
    roundTime: 60, _roundWallElapsed: 0, _roundWallLast: 0, _roundLockT: 3.0,
    timeOutCalls: 0, afterRoundCalls: 0,
    _timeOut() { this.timeOutCalls++; this.roundState = 'over'; },
    _afterRound() { this.afterRoundCalls++; this.roundState = 'done'; },
    ...overrides,
  };
  return g;
}

// Step the wall block at 1 fps (1000 ms per call — the re-test's slow tab).
function stepSeconds(g, seconds) {
  let now = g._roundWallLast;
  for (let s = 0; s < seconds; s++) {
    now += 1000;
    runWallBlock.call(g, now, ROUND_TIME);
  }
  return now;
}

test('wall clock ends the round at the limit on a 1 fps machine', () => {
  const g = fakeGame();
  stepSeconds(g, 59);
  assert.equal(g.timeOutCalls, 0, 'no timeout before 60 wall seconds');
  assert.equal(g.roundState, 'fight');
  stepSeconds(g, 1);
  assert.equal(g.timeOutCalls, 1, 'timeout fires at exactly 60 wall seconds');
  assert.equal(g.roundState, 'over');
});

test('wall timeout fires exactly once even if the clock keeps running', () => {
  const g = fakeGame();
  stepSeconds(g, 60);
  assert.equal(g.timeOutCalls, 1);
  stepSeconds(g, 30);
  assert.equal(g.timeOutCalls, 1, 'no second timeout once the round is over');
});

test('post-round lockout counts down in wall time, result follows in 3 s', () => {
  const g = fakeGame({ roundState: 'over', _roundLockT: 3.0, _roundWallElapsed: 60 });
  stepSeconds(g, 2);
  assert.equal(g.afterRoundCalls, 0, 'no result before 3 wall seconds');
  stepSeconds(g, 1);
  assert.equal(g.afterRoundCalls, 1, 'result screen after 3 wall seconds, not ~90 s');
});

test('roundTime 0 (INFINITY) never times out on the wall clock', () => {
  const g = fakeGame({ roundTime: 0 });
  stepSeconds(g, 200);
  assert.equal(g.timeOutCalls, 0);
});

test('paused time never counts toward the wall clock', () => {
  const g = fakeGame({ paused: true });
  stepSeconds(g, 120);
  assert.equal(g.timeOutCalls, 0);
  assert.equal(g._roundWallElapsed, 0);
});

test('ROUND_TIME default is 60 s (T7 tournament timer, teardown spec)', () => {
  assert.equal(ROUND_TIME, 60);
});
