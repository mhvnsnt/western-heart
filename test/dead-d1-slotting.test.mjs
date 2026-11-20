// Dead d+1 fix (docs/movesets/DEAD-D1-DIAGNOSIS-2026-11-04.md): _prepare completes
// three data-sanctioned slot classes, each filling ONLY a still-free slot:
//  (a) a move's recorded input_slots alternates (same single step, same buttons,
//      one claimant) — negativo's d/b+1 lists d+1 ('d/b or d+1' in his source data)
//  (b) T3 any-of DOWN commands ('1/2/3+LP' = d/b, d or d/f + LP perform the row)
//  (c) d+1 falls back to the fighter's FC.1 crouch jab when no d+1 row exists
// Guards under test: string tables listing every button in input_slots stay
// unslotted, ambiguous alternates stay unslotted, up/side any-of T3 commands
// (jump rows) never slot their plain spellings, a real d+1 row always wins.
import test from 'node:test';
import assert from 'node:assert/strict';
const _ls = {}; globalThis.localStorage = { getItem: (k) => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: (k) => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
const mv = (extra) => ({ startup: 0.17, active: 0.03, recovery: 0.4, damage: 5, move_class: 'strike', ...extra });

test('(a) recorded input alternate slots the move on d+1', () => {
  M.registerMoveset('d1-alt', { moves: {
    'd/b+1': mv({ input: 'd/b+1', input_slots: ['d/b+1', 'd+1'] }),
  } });
  assert.equal(M.resolveMoveKey('d1-alt', 'd+1'), 'd/b+1');
  assert.equal(M.resolveMoveKey('d1-alt', 'd/b+1'), 'd/b+1');
});

test('(a) guards: string button lists and ambiguous alternates stay unslotted', () => {
  M.registerMoveset('d1-guard', { moves: {
    '1,2': mv({ input: '1,2', input_slots: ['1,2', '2'] }),          // string: '2' is a step, not an alternate
    'x_a': mv({ input: 'd/b+2', input_slots: ['d/b+2', 'd+2'] }),    // two claimants for 'd+2' ->
    'x_b': mv({ input: 'd/f+2', input_slots: ['d/f+2', 'd+2'] }),    // ambiguous, neither is slotted
  } });
  assert.equal(M.resolveMoveKey('d1-guard', '2'), null);
  assert.equal(M.resolveMoveKey('d1-guard', 'd+2'), null);
});

test('(b) T3 any-of down command slots every free down spelling', () => {
  M.registerMoveset('d1-t3', { moves: {
    'd/b': mv({ input: 'd/b', t3_row: 115, t3_command: '1/2/3+LP', name: 'BRYAN d/b_c37 (T3 bryan r115)' }),
    'u/f+1': mv({ input: 'u/f+1', t3_row: 54, t3_command: '6/9+LP' }),
  } });
  assert.equal(M.resolveMoveKey('d1-t3', 'd+1'), 'd/b');
  assert.equal(M.resolveMoveKey('d1-t3', 'd/b+1'), 'd/b');
  assert.equal(M.resolveMoveKey('d1-t3', 'd/f+1'), 'd/b');
  // up/side any-of groups are jump rows: the plain spelling stays unslotted
  assert.equal(M.resolveMoveKey('d1-t3', 'f+1'), null);
});

test('(c) d+1 falls back to the FC.1 crouch jab; a real d+1 row wins; neither stays dead', () => {
  M.registerMoveset('d1-fc', { moves: { 'FC.1': mv({ input: 'FC.1', name: 'FC jab' }) } });
  assert.equal(M.resolveMoveKey('d1-fc', 'd+1'), 'FC.1');
  M.registerMoveset('d1-real', { moves: {
    'FC.1': mv({ input: 'FC.1' }), 'd+1': mv({ input: 'd+1', name: 'own d+1' }),
  } });
  assert.equal(M.resolveMoveKey('d1-real', 'd+1'), 'd+1');
  M.registerMoveset('d1-none', { moves: { 'd/b+1': mv({ input: 'd/b+1' }) } });
  assert.equal(M.resolveMoveKey('d1-none', 'd+1'), null);
});
