// Numeric / name-keyed moves (KOF imports) whose only slot is themselves must still be
// reachable by their `input` notation, so a string's head (qcb+1) resolves when equipped.
import assert from 'node:assert/strict';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
M.registerMoveset('slot-test', {
  slots: { '15': '15', '16': '16', aoihana_c1: 'aoihana_c1' },
  moves: {
    '15': { name: 'head', input: 'qcb+1', startup: 0.2, active: 0.05, recovery: 0.3 },
    '16': { name: 'string', input: 'qcb+1,1', startup: 0.2, active: 0.05, recovery: 0.3 },
    aoihana_c1: { name: 'c1', input: 'qcb+2', startup: 0.2, active: 0.05, recovery: 0.3 },
  },
});
assert.equal(M.resolveMoveKey('slot-test', 'qcb+1'), '15');
assert.equal(M.resolveMoveKey('slot-test', 'qcb+1,1'), '16');
assert.equal(M.resolveMoveKey('slot-test', 'qcb+2'), 'aoihana_c1');
console.log('input-slotting: 3/3 ok');
