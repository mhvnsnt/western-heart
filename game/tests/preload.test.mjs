/* preload.test.mjs — Kaggle-GPU load lane (2026-10-24).
 * WHAT THIS GUARDS: game/js/preload.js must (a) preload every select
 * card image without ever rejecting on a missing portrait, (b) cache
 * so a second warm is free, (c) warm only the fighters passed to
 * warmFight (never the whole roster — that was the preloadAll pipe
 * saturation), and (d) stay wired into select-screen.js + main.js
 * (a wiring guard: if a future edit drops the calls, this fails).
 * Run: node --test game/tests/preload.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import {
  cardUrl, preloadCards, warmSelect, warmFight,
  isCardCached, cardCacheSize, _resetCardCache,
} from '../js/preload.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

/* Fake Image: resolves onload for ids not containing 'missing',
   onerror for 'missing' — mirrors the browser contract preload.js
   relies on (src assignment triggers load/error asynchronously). */
function fakeImageFactory(calls) {
  return class FakeImage {
    constructor() { calls.push(this); }
    set src(_url) {
      const missing = String(_url).includes('missing');
      setTimeout(() => {
        if (missing) { if (this.onerror) this.onerror(); }
        else if (this.onload) this.onload();
      }, 0);
    }
  };
}

test('cardUrl uses the portrait path the card DOM already renders', () => {
  assert.equal(cardUrl('pantera'), 'assets/portraits/pantera.png');
  assert.equal(cardUrl('demonio'), 'assets/portraits/demonio.png');
});

test('preloadCards resolves always, counts loaded/failed, never rejects on missing', async () => {
  _resetCardCache();
  const calls = [];
  const r = await preloadCards(['pantera', 'missing-fighter', 'demonio'], {
    imageCtor: fakeImageFactory(calls),
  });
  assert.equal(r.total, 3);
  assert.equal(r.loaded, 2);
  assert.equal(r.failed, 1);
  assert.equal(isCardCached('pantera'), true);
  assert.equal(isCardCached('missing-fighter'), false);
  assert.equal(cardCacheSize(), 2);
});

test('preloadCards dedups ids and second warm is free (cache hit, no new Image)', async () => {
  _resetCardCache();
  const calls = [];
  const Ctor = fakeImageFactory(calls);
  await preloadCards(['pantera', 'pantera', 'demonio'], { imageCtor: Ctor });
  assert.equal(calls.length, 2);
  const r2 = await preloadCards(['pantera', 'demonio'], { imageCtor: Ctor });
  assert.equal(r2.cached, 2);
  assert.equal(calls.length, 2);
});

test('warmSelect returns the preload result and records it for loadperf', async () => {
  _resetCardCache();
  const calls = [];
  const r = await warmSelect(['pantera'], { imageCtor: fakeImageFactory(calls) });
  assert.equal(r.total, 1);
  assert.equal(r.loaded, 1);
});

test('warmFight prefetches exactly the deduped ids passed — never the roster', () => {
  const warmed = [];
  const ids = warmFight(['pantera', 'demonio', 'pantera'], (id) => warmed.push(id));
  assert.deepEqual(ids, ['pantera', 'demonio']);
  assert.deepEqual(warmed, ['pantera', 'demonio']);
  assert.deepEqual(warmFight([], () => { throw new Error('must not be called'); }), []);
});

test('wiring guard: select-screen calls warmSelect + warmLockedFighters, main calls it on stage', () => {
  const select = readFileSync(join(root, 'js/select-screen.js'), 'utf8');
  assert.ok(select.includes("from './preload.js'"), 'select-screen must import preload.js');
  assert.ok(select.includes('warmSelect('), 'select-screen onShow must warmSelect the roster cards');
  assert.ok(select.includes('warmLockedFighters'), 'select-screen must expose warmLockedFighters');
  const main = readFileSync(join(root, 'js/main.js'), 'utf8');
  assert.ok(main.includes('warmLockedFighters'), 'main show(stage) must warm locked fighters');
});
