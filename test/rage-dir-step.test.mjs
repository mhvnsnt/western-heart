// Dio's Rage row (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// '(During Rage) 1,1,f,3,2' (Wrath of the Raging Demon) failed in r16 as
// fired ["3"] only — the string broke at the bare 'f' step. The resolver's
// string-continuation candidates attached the held direction to the button
// ('R.1,1,f+3'), but the row's own input_slots carry '...1,1,f' as its own
// comma step, so no candidate matched 'R.1,1,f,3'. The fix adds bare-dir-step
// candidates (tried last) plus a recent-direction fallback for the released
// stick (the sweep releases to neutral before the button for motion-only
// steps, and pad players do the same). Chatur 'u/f+1+2,d/b,1' is the second
// core-8 string with a bare direction step, and it resolves the same way.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const _ls = {};
globalThis.localStorage = { getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: k => { delete _ls[k]; } };
globalThis.WH_INPUT_RESOLVER = 'v2';
const M = await import(join(root, 'game', 'js', 'movesets.js'));
M.registerMoveset('dio', JSON.parse(readFileSync(join(root, 'game', 'assets', 'movesets', 'dio.json'), 'utf8')));
M.registerMoveset('chatur', JSON.parse(readFileSync(join(root, 'game', 'assets', 'movesets', 'chatur.json'), 'utf8')));
const feed = (buf, dir, n = 4) => { for (let i = 0; i < n; i++) buf.noteDirection(dir); };
const RAGE = { rage: true };

test('Dio rage string resolves through a bare direction step, direction held', () => {
  const buf = new M.TekkenBuffer('dio');
  feed(buf, 'n');
  assert.equal(buf.press('1', RAGE), null);
  feed(buf, 'n');
  assert.equal(buf.press('1', RAGE), null);
  feed(buf, 'f', 2);
  assert.equal(buf.press('3', RAGE), null);
  assert.equal(buf._strPath, 'R.1,1,f,3');
  feed(buf, 'n');
  assert.equal(buf.press('2', RAGE), 'R.1,1,f,3,2');
});

test('Dio rage string resolves through a bare direction step, direction released (sweep cadence)', () => {
  const buf = new M.TekkenBuffer('dio');
  feed(buf, 'n');
  assert.equal(buf.press('1', RAGE), null);
  feed(buf, 'n');
  assert.equal(buf.press('1', RAGE), null);
  feed(buf, 'f', 3); feed(buf, 'n', 1);
  assert.equal(buf.press('3', RAGE), null);
  assert.equal(buf._strPath, 'R.1,1,f,3');
  feed(buf, 'n');
  assert.equal(buf.press('2', RAGE), 'R.1,1,f,3,2');
});

test('Chatur u/f+1+2,d/b,1 resolves through a bare direction step', () => {
  const buf = new M.TekkenBuffer('chatur');
  feed(buf, 'n'); feed(buf, 'u/f', 2);
  assert.equal(buf.pressChord('1+2', {}), 'u/f+1+2');
  feed(buf, 'd/b', 3); feed(buf, 'n', 1);
  assert.equal(buf.press('1', {}), 'u/f+1+2,d/b,1');
});

test('guards: stale direction, plain continuation, and fresh direction+button unchanged', () => {
  const buf = new M.TekkenBuffer('dio');
  feed(buf, 'n'); buf.press('1', RAGE);
  feed(buf, 'n'); buf.press('1', RAGE);
  feed(buf, 'f', 3); feed(buf, 'n', 30);
  assert.equal(buf.press('3', RAGE), '3');
  const plain = new M.TekkenBuffer('dio');
  feed(plain, 'n');
  assert.equal(plain.press('1', {}), '1');
  feed(plain, 'n');
  assert.equal(plain.press('2', {}), '1,2');
  const fresh = new M.TekkenBuffer('dio');
  feed(fresh, 'f', 2);
  assert.equal(fresh.press('3', RAGE), 'f+3');
});
