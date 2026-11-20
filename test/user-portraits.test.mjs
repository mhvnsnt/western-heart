// User portraits (game/js/user-portraits.js): on-device select-screen cards.
// Run: node --test test/user-portraits.test.mjs
// The Creation Suite's TAKE PICTURE saves through this module; the select
// screen and versus plates prefer the stored portrait over the repo card
// (game/assets/portraits/<id>.png). These tests pin the storage contract:
// key scheme, preference + fallback, and rejection of non-image values.
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// Map-backed localStorage stub with the full Storage surface the module uses.
function makeStore() {
  const m = new Map();
  return {
    get length() { return m.size; },
    key: (i) => [...m.keys()][i] ?? null,
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); },
    _map: m,
  };
}
globalThis.localStorage = makeStore();

const UP = await import(join(ROOT, 'game/js/user-portraits.js'));
const PNG = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
const PNG2 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==';

test('key scheme: wh.portrait.<fighterId>.<attireId>, attire normalized', () => {
  assert.equal(UP.USER_PORTRAIT_PREFIX, 'wh.portrait.');
  assert.equal(UP.portraitKey('pantera'), 'wh.portrait.pantera.attire1');
  assert.equal(UP.portraitKey('pantera', 'attire1'), 'wh.portrait.pantera.attire1');
  assert.equal(UP.portraitKey('pantera', 2), 'wh.portrait.pantera.attire2');
  assert.equal(UP.portraitKey('pantera', 'Attire 3'), 'wh.portrait.pantera.attire3');
  assert.equal(UP.normalizeAttireId(undefined), 'attire1');
  assert.equal(UP.normalizeAttireId('leomon'), 'leomon'); // named slots keep their id
});

test('save / get / has roundtrip, per fighter + attire', () => {
  assert.equal(UP.savePortrait('pantera', 'attire1', PNG), true);
  assert.equal(UP.getPortrait('pantera', 'attire1'), PNG);
  assert.equal(UP.getPortrait('pantera', 1), PNG); // numeric attire resolves to the same key
  assert.equal(UP.hasPortrait('pantera'), true);
  assert.equal(UP.getPortrait('pantera', 'attire2'), null);
  assert.equal(UP.getPortrait('negativo', 'attire1'), null);
  // overwriting replaces the card
  assert.equal(UP.savePortrait('pantera', 'attire1', PNG2), true);
  assert.equal(UP.getPortrait('pantera'), PNG2);
});

test('portraitSrcFor: stored portrait wins, repo card is the fallback', () => {
  const repo = 'assets/portraits/pantera.png';
  assert.equal(UP.portraitSrcFor('pantera', 'attire1', repo), PNG2);
  assert.equal(UP.portraitSrcFor('pantera', 'attire4', repo), repo); // no attire4 portrait stored
  assert.equal(UP.portraitSrcFor('demonio', 'attire1', 'assets/portraits/demonio.png'), 'assets/portraits/demonio.png');
});

test('clearPortrait removes the stored card and reports whether one existed', () => {
  assert.equal(UP.clearPortrait('pantera', 'attire1'), true);
  assert.equal(UP.getPortrait('pantera'), null);
  assert.equal(UP.portraitSrcFor('pantera', 'attire1', 'assets/portraits/pantera.png'), 'assets/portraits/pantera.png');
  assert.equal(UP.clearPortrait('pantera', 'attire1'), false);
});

test('non-image values are rejected and never clobber an existing card', () => {
  assert.equal(UP.savePortrait('zen', 'attire1', PNG), true);
  assert.equal(UP.savePortrait('zen', 'attire1', 'https://example.com/x.png'), false);
  assert.equal(UP.savePortrait('zen', 'attire1', 'data:text/html;base64,PGI+'), false);
  assert.equal(UP.savePortrait('zen', 'attire1', ''), false);
  assert.equal(UP.getPortrait('zen', 'attire1'), PNG);
});

test('listPortraits enumerates stored cards and ignores foreign keys', () => {
  globalThis.localStorage.setItem('wh_creation_suite_v1', '{}');
  globalThis.localStorage.setItem('unrelated', 'x');
  const list = UP.listPortraits();
  assert.deepEqual(list.map((e) => e.key).sort(), ['wh.portrait.zen.attire1']);
  assert.equal(list[0].fighterId, 'zen');
  assert.equal(list[0].attireId, 'attire1');
});

test('storage failure (quota / private mode) degrades to the repo card', () => {
  const good = globalThis.localStorage;
  globalThis.localStorage = {
    get length() { return 0; },
    key: () => null,
    getItem: () => { throw new Error('denied'); },
    setItem: () => { throw new Error('quota'); },
    removeItem: () => { throw new Error('denied'); },
  };
  assert.equal(UP.savePortrait('pantera', 'attire1', PNG), false);
  assert.equal(UP.getPortrait('pantera', 'attire1'), null);
  assert.equal(UP.portraitSrcFor('pantera', 'attire1', 'assets/portraits/pantera.png'), 'assets/portraits/pantera.png');
  assert.equal(UP.clearPortrait('pantera', 'attire1'), false);
  globalThis.localStorage = good;
});
