// T3 clip-variant rows ('b_c36') get a playable input from their source command.
import assert from 'node:assert/strict';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
assert.deepEqual(M.t3CommandNotations('4/6/7/8/9+LK+RK'), ['b+3+4', 'f+3+4', 'u/b+3+4', 'u+3+4', 'u/f+3+4']);
assert.deepEqual(M.t3CommandNotations('6/9+LP'), ['f+1', 'u/f+1']);
assert.deepEqual(M.t3CommandNotations('9/9/9+any-button'), []);
M.registerMoveset('cv-test', { moves: {
  'f+1': { name: 'base', input: 'f+1' },
  f_c36_r45: { name: 'clip', input: 'f_c36_r45', t3_command: '6/9+LP', t3_condition: 36 },
  b_c37: { name: 'clip2', input: 'b_c37', t3_command: '4+RK', t3_condition: 37 } } });
assert.equal(M.resolveMoveKey('cv-test', 'f+1'), 'f+1');          // existing slot kept
assert.equal(M.resolveMoveKey('cv-test', 'u/f+1'), 'f_c36_r45');  // next free source spelling
assert.equal(M.resolveMoveKey('cv-test', 'b+4'), 'b_c37');
console.log('t3-command-notation: 6/6 ok');
