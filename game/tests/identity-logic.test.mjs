/* identity-logic.test.mjs — Player identity core logic guard (worker 35).
 *
 * WHAT THIS GUARDS: game/js/identity.js is the single source of truth for
 * the player-identity economy (titles, cards, currency, loot, remap,
 * colorblind, assists). A regression here silently corrupts every player's
 * profile, currency balance, and unlocks — all localStorage-persisted.
 *
 * COVERAGE:
 *   - profile defaults (name, starter title, starter clay cache)
 *   - awardMatch economy: win = 120 + 20/streak + bonuses; loss = 40
 *     (Tekken rule: paid every battle, win or lose)
 *   - title auto-unlocks (Untouched on perfect, Unbroken on 5-streak)
 *   - Soul Cache drops on win, openCache shard ranges, overspend guard
 *   - input.js _remapCode: true rebind semantics (old key dead, conflict clear)
 *   - WHAssists.translate: throw-break assist maps any limb to the prompt
 *   - WHColorblind.apply: sets <html data-cb>
 *
 * Run: node --test game/tests/identity-logic.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

/* ---- minimal browser stubs (identity.js is dependency-free) ---- */
const store = {};
const promptEl = {
  classList: { contains: () => false },
  querySelector: () => ({ textContent: '' }),
};
let appliedCb = null;
globalThis.window = globalThis;
globalThis.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: (k) => { delete store[k]; },
};
globalThis.document = {
  documentElement: { setAttribute: (k, v) => { appliedCb = v; } },
  getElementById: (id) => (id === 'throw-prompt' ? promptEl : null),
  readyState: 'complete',
  addEventListener: () => {},
  createElement: () => ({ classList: { add: () => {}, remove: () => {} }, style: {}, appendChild: () => {} }),
  body: { appendChild: () => {} },
  querySelectorAll: () => [],
};
globalThis.requestAnimationFrame = (fn) => fn();

/* identity.js is a classic script: eval it into the stubbed globals */
eval(readFileSync(join(root, 'js', 'identity.js'), 'utf8'));
const I = globalThis.WHIdentity;
const { InputManager } = await import(join(root, 'js', 'input.js'));

test('profile defaults', () => {
  I.reset();
  const p = I.get();
  assert.equal(p.name, 'LOST SOUL');
  assert.deepEqual(p.titles, ['lost-soul']);
  assert.equal(p.caches.clay, 1);
  assert.equal(I.CURRENCY_NAME, 'Soul Shards'); // pending owner approval
});

test('awardMatch: win + perfect economy', () => {
  I.reset();
  const r = I.awardMatch({ won: true, perfect: true, great: false, surgeWin: false, maxCombo: 7 });
  const p = I.get();
  assert.equal(r.shards, 120 + 20 + 150);
  assert.equal(p.stats.wins, 1);
  assert.equal(p.stats.streak, 1);
  assert.equal(p.stats.perfects, 1);
  assert.ok(p.titles.includes('untouched'), 'Untouched unlocked by perfect');
  assert.ok(r.drops.length >= 1, 'win drops at least one cache');
});

test('awardMatch: loss still pays (Tekken rule)', () => {
  I.reset();
  const r = I.awardMatch({ won: false });
  const p = I.get();
  assert.equal(r.shards, 40);
  assert.equal(p.stats.streak, 0);
  assert.equal(p.stats.deaths, 1);
});

test('streak title unlock', () => {
  I.reset();
  for (let i = 0; i < 5; i++) I.awardMatch({ won: true });
  assert.ok(I.get().titles.includes('unbroken'));
});

test('openCache shard ranges + overspend guard', () => {
  I.reset();
  const before = I.get().shards;
  const opened = I.openCache('clay');
  assert.equal(opened.rarity.id, 'clay');
  assert.equal(I.get().shards, before + opened.shards);
  assert.ok(opened.shards >= 40 && opened.shards <= 120);
  assert.equal(I.openCache('prism'), null);
  I.addShards(500, 'test');
  assert.equal(I.spendShards(200), true);
  assert.equal(I.spendShards(99999), false);
});

test('input.js _remapCode: true rebind semantics', () => {
  I.reset();
  const im = new InputManager();
  assert.equal(im._remapCode('Digit1'), 'Digit1');
  I.setKey('limb1', 'KeyQ');
  assert.equal(im._remapCode('KeyQ'), 'Digit1');
  assert.equal(im._remapCode('Digit1'), '__unbound__');
  assert.equal(im._physicalCode('limb1'), 'KeyQ');
});

test('WHAssists.translate: throw-break assist', () => {
  I.reset();
  I.get().assists.throwAssist = true;
  const im = new InputManager();
  promptEl.classList.contains = (c) => c === 'show';
  promptEl.querySelector = () => ({ textContent: 'TAP RP' });
  assert.equal(globalThis.WHAssists.translate('3', im), '2');
  promptEl.querySelector = () => ({ textContent: 'TAP LP+RP' });
  assert.equal(globalThis.WHAssists.translate('4', im), '1+2');
});

test('WHColorblind.apply sets data-cb', () => {
  I.setColorblind('deutan');
  assert.equal(appliedCb, 'deutan');
});
