import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation, stateCode, registerMoveset, resolveMoveKey } from '../game/js/movesets.js';

test('ground states map to Tekken FUFT / FUHT prefixes', () => {
  assert.equal(canonNotation('while on back, feet towards opponent, 3, 3'), 'FUFT.3,3');
  assert.equal(canonNotation('while on back, 1+2+3+4'), 'FUFT.1+2+3+4');
  assert.equal(canonNotation('while on back, head towards opponent, 3+4'), 'FUHT.3+4');
});

test('named custom states map to their stance code', () => {
  assert.equal(stateCode('Bad Stomach'), 'BAD_STOMACH');
  assert.equal(canonNotation('during Bad Stomach, 1+2'), 'BAD_STOMACH.1+2');
  assert.equal(canonNotation('during Elbow Drop 1+4'), 'ELBOW_DROP.1+4');
  assert.equal(canonNotation('during Irish Whip 2, 1'), 'IRISH_WHIP_2.1');
  assert.equal(canonNotation('JGS, 1'), 'JGS.1');
});

test('state rows are slotted and their entry move enters the state, nothing overwritten', () => {
  const ms = { moves: {
    '1+4': { name: 'Bad Stomach', input: '1+4' },
    'bs_1+2': { name: 'Arm Takedown', input: 'during Bad Stomach, 1+2' },
    'bk_3': { name: 'Ground Kick', input: 'while on back, feet towards opponent, 3' },
    '3+4_charge': { name: 'Panik Charge', input: '3+4' },
    'pc_2': { name: 'Jab', input: 'during Panik Charge, 2' },
  }, stance_after: { '3+4_charge': 'KEEP' } };
  registerMoveset('state-gated-test', ms);
  assert.equal(resolveMoveKey('state-gated-test', 'BAD_STOMACH.1+2'), 'bs_1+2');
  assert.equal(resolveMoveKey('state-gated-test', 'FUFT.3'), 'bk_3');
  assert.equal(ms.stance_after['1+4'], 'BAD_STOMACH');
  assert.equal(ms.stance_after['3+4_charge'], 'KEEP');
});
