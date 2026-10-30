// Dio's 9 During-Jump sweep failures (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// T7 jump attacks canonicalise to the AIR. prefix, resolved from ctx.airborne the way R.
// resolves from rage — so a jump attack no longer collides with its ground namesake
// (Dio's ground qcf+1 Hadoken vs his air qcf+1 Zanku Hadoken) and no longer falls through
// the sweep's parse as 'During Jump qcf+1'. Vertical-jump rows keep their passing u+ form.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation, registerMoveset, resolveMoveKey, TekkenBuffer } from '../game/js/movesets.js';

test('jump contexts canonicalise to AIR., vertical jump keeps u+', () => {
  assert.equal(canonNotation('(During Jump) qcf+1'), 'AIR.qcf+1');
  assert.equal(canonNotation('(During Jump) qcb+3'), 'AIR.qcb+3');
  assert.equal(canonNotation('(During Jump) qcf+1+2'), 'AIR.qcf+1+2');
  assert.equal(canonNotation('(During Jump) qcb+3+4'), 'AIR.qcb+3+4');
  assert.equal(canonNotation('(During Forward or Backward Jump) 1'), 'AIR.1');
  assert.equal(canonNotation('(During Forward or Backward Jump) 2'), 'AIR.2');
  assert.equal(canonNotation('(During Forward or Backward Jump) 3'), 'AIR.3');
  assert.equal(canonNotation('(During Forward or Backward Jump) 4'), 'AIR.4');
  assert.equal(canonNotation('(During Forward Jump Peak) d+3'), 'AIR.d+3');
  assert.equal(canonNotation('(During Vertical Jump) 1'), 'u+1');
  // Non-jump 'during X' rows are untouched by the AIR. rule.
  assert.equal(canonNotation('during Bad Stomach, 1+2'), 'BAD_STOMACH.1+2');
});

test('AIR. slots coexist with ground slots, nothing overwritten', () => {
  const ms = { moves: {
    'qcf+1': { name: 'Ground Hadoken', input: 'qcf+1' },
    '(During Jump) qcf+1': { name: 'Zanku Hadoken', input: '(During Jump) qcf+1' },
    '1': { name: 'Jab', input: '1' },
    '(During Forward or Backward Jump) 1': { name: 'Gokuken', input: '(During Forward or Backward Jump) 1' },
    '(During Vertical Jump) 1': { name: 'Hijitoshi', input: '(During Vertical Jump) 1' },
  } };
  registerMoveset('air-moves-test', ms);
  assert.equal(resolveMoveKey('air-moves-test', 'AIR.qcf+1'), '(During Jump) qcf+1');
  assert.equal(resolveMoveKey('air-moves-test', 'qcf+1'), 'qcf+1');
  assert.equal(resolveMoveKey('air-moves-test', 'AIR.1'), '(During Forward or Backward Jump) 1');
  assert.equal(resolveMoveKey('air-moves-test', '1'), '1');
  assert.equal(resolveMoveKey('air-moves-test', 'u+1'), '(During Vertical Jump) 1');
});

function feed(buf, dir, frames = 4) { for (let i = 0; i < frames; i++) buf.noteDirection(dir); }

test('resolver picks the AIR. move only while airborne, ground move otherwise', () => {
  const buf = new TekkenBuffer('air-moves-test');
  feed(buf, 'n');
  assert.equal(buf.press('1', { airborne: true }), 'AIR.1');
  assert.equal(buf.press('1', {}), '1');
});

test('resolver picks AIR. motion over the ground motion while airborne', () => {
  const buf = new TekkenBuffer('air-moves-test');
  feed(buf, 'n', 30);
  for (const d of ['d', 'd/f', 'f']) feed(buf, d, 2);
  assert.equal(buf.press('1', { airborne: true }), 'AIR.qcf+1');
  const buf2 = new TekkenBuffer('air-moves-test');
  feed(buf2, 'n', 30);
  for (const d of ['d', 'd/f', 'f']) feed(buf2, d, 2);
  assert.equal(buf2.press('1', {}), 'qcf+1');
});
