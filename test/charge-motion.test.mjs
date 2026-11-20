// Charge motions (moveset sweep 2026-10-29): 'charge_b,f+1' fires only after the stick sat back
// CHARGE_FRAMES (40f), then forward + button; a quick b,f+1 or plain f+1 does not.
import test from 'node:test';
import assert from 'node:assert/strict';
const _ls = {};
globalThis.localStorage = { getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: k => { delete _ls[k]; } };
const M = await import('../game/js/movesets.js');
const mv = (name) => ({ name, startup: 10, active: 3, recovery: 20, damage: 10 });
M.registerMoveset('chg', { moves: { '1': mv('jab'), 'f+1': mv('fwd jab'), 'charge_b,f+1': mv('sonic'), 'charge_d,u+3': mv('flash'), 'charge_db,f+3': mv('db charge') } });
const feed = (b, d, n) => { for (let i = 0; i < n; i++) b.noteDirection(d); };
const press = (b, btn, dir) => b.press(btn, { dir });
test('parseMotion reads charge heads', () => {
  assert.deepEqual(M.parseMotion('charge_b,f+1'), { prefix: '', dirs: ['f'], btn: '1', neutral: false, charge: 'b' });
  assert.equal(M.parseMotion('charge_db,f+3').charge, 'd/b');
});
test('charge held 45f then f+1 fires the charge move', () => {
  const b = new M.TekkenBuffer('chg'); feed(b, 'n', 5); feed(b, 'b', 45); feed(b, 'f', 2);
  assert.equal(press(b, '1', 'f'), 'charge_b,f+1');
});
test('d/b counts as back charge', () => {
  const b = new M.TekkenBuffer('chg'); feed(b, 'n', 5); feed(b, 'd/b', 45); feed(b, 'f', 2);
  assert.equal(press(b, '1', 'f'), 'charge_b,f+1');
});
test('short charge falls back to f+1', () => {
  const b = new M.TekkenBuffer('chg'); feed(b, 'n', 5); feed(b, 'b', 10); feed(b, 'f', 2);
  assert.equal(press(b, '1', 'f'), 'f+1');
});
test('stale charge (released too long ago) does not fire', () => {
  const b = new M.TekkenBuffer('chg'); feed(b, 'n', 5); feed(b, 'b', 45); feed(b, 'n', 60); feed(b, 'f', 2);
  assert.equal(press(b, '1', 'f'), 'f+1');
});
test('down charge, up + 3', () => {
  const b = new M.TekkenBuffer('chg'); feed(b, 'n', 5); feed(b, 'd', 45); feed(b, 'u', 1);
  assert.equal(press(b, '3', 'u'), 'charge_d,u+3');
});
