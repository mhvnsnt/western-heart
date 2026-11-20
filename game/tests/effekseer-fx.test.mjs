/* Effekseer FX modules — unit tests (node, no DOM/GL).
 * Covers: quality detection, color conversion, hit-kind routing,
 * budget/LOD gating, trail gating, Soul Urge event routing. */
import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  WHEffekseerFX, EFX_QUALITY, hexToRgb, detectQuality,
} from '../js/fx/particles.js';
import { WHHitEffects, kindForScale, EFX_ASSETS } from '../js/fx/hit-effects.js';
import { WHSoulUrgeFX, AURA_REPLAY_S } from '../js/fx/soulurge-fx.js';

/* ---- fake Effekseer wrapper: records play() calls, no GL ---- */
function fakeFX(quality = 'medium', ready = true) {
  return {
    ready,
    _q: EFX_QUALITY[quality],
    _played: [],
    _loaded: [],
    assetUrl(f) { return 'assets/' + f; },
    async loadEffect(name, url) { this._loaded.push([name, url]); return {}; },
    play(name, x, y, z, opts = {}) {
      this._played.push({ name, x, y, z, ...opts });
      return { exists: true, stop() {}, setLocation() {} };
    },
    stopAll() {},
  };
}

function fakeFallback() {
  return { spawned: [], spawn(x, y, z, c, s, k) { this.spawned.push([x, y, z, c, s, k]); return true; } };
}

function fakeFighter() {
  return { _urgeOn: false, root: { position: { x: 1, y: 0, z: -2 } } };
}

describe('particles: quality table', () => {
  it('all levels define instance caps, budgets, LOD, trails', () => {
    for (const q of ['low', 'medium', 'high']) {
      const t = EFX_QUALITY[q];
      assert.ok(t.instanceMaxCount > 0, q);
      assert.ok(t.squareMaxCount > 0, q);
      assert.ok(t.maxHandles > 0, q);
      assert.ok(t.lodDistance > 0, q);
      assert.equal(typeof t.trails, 'boolean', q);
    }
    // budgets grow with quality (phones stay cheap)
    assert.ok(EFX_QUALITY.low.maxHandles < EFX_QUALITY.high.maxHandles);
    assert.ok(EFX_QUALITY.low.instanceMaxCount < EFX_QUALITY.high.instanceMaxCount);
  });
  it('hexToRgb converts 0xRRGGBB to float channels', () => {
    assert.deepEqual(hexToRgb(0xff0000), [1, 0, 0]);
    assert.deepEqual(hexToRgb(0x00ff00), [0, 1, 0]);
    assert.deepEqual(hexToRgb(0x0000ff), [0, 0, 1]);
    assert.deepEqual(hexToRgb(0x9fd8ff).map(v => Math.round(v * 255)),
      [0x9f, 0xd8, 0xff]);
  });
});

describe('particles: detectQuality', () => {
  it('stored override wins', () => {
    const env = { localStorage: { getItem: () => 'high' }, navigator: {} };
    assert.equal(detectQuality(env), 'high');
    assert.equal(detectQuality({ localStorage: { getItem: () => 'nope' },
      navigator: { userAgent: 'x', hardwareConcurrency: 8 } }), 'medium');
  });
  it('phones and low-core devices get low', () => {
    const m = { localStorage: { getItem: () => null },
      navigator: { userAgent: 'Android 14', hardwareConcurrency: 8 } };
    assert.equal(detectQuality(m), 'low');
    const c = { localStorage: { getItem: () => null },
      navigator: { userAgent: 'x', hardwareConcurrency: 4 } };
    assert.equal(detectQuality(c), 'low');
  });
  it('desktop defaults to medium', () => {
    const d = { localStorage: { getItem: () => null },
      navigator: { userAgent: 'Windows', hardwareConcurrency: 16 } };
    assert.equal(detectQuality(d), 'medium');
  });
});

describe('hit-effects: kind routing', () => {
  it('kindForScale thresholds match WHHitFX', () => {
    assert.equal(kindForScale(0.6), 'impact');
    assert.equal(kindForScale(0.9), 'heavy');
    assert.equal(kindForScale(1.0), 'heavy');
    assert.equal(kindForScale(1.3), 'ko');
  });
  it('ko plays blow + light at high priority', async () => {
    const fx = fakeFX(), h = new WHHitEffects();
    await h.init(fx, fakeFallback());
    assert.equal(h.spawn(0, 1, 0, 0xffcf4d, 1.4), true);
    const names = fx._played.map(p => p.name).sort();
    assert.deepEqual(names, ['blow', 'light']);
    assert.ok(fx._played.every(p => p.priority === 'high'));
    assert.ok(fx._played.every(p => p.color === 0xffcf4d), 'combat color tints both');
  });
  it('heavy layers toon-hit + light; impact plays toon-hit', async () => {
    const fx = fakeFX(), h = new WHHitEffects();
    await h.init(fx, fakeFallback());
    h.spawn(0, 1, 0, 0xffcf4d, 1.0);
    assert.deepEqual(fx._played.map(p => p.name).sort(), ['light', 'toon-hit']);
    fx._played.length = 0;
    h.spawn(0, 1, 0, 0xffcf4d, 0.6);
    assert.deepEqual(fx._played.map(p => p.name), ['toon-hit']);
  });
  it('block plays light; dust/surge go to the nebula fallback', async () => {
    const fx = fakeFX(), fb = fakeFallback(), h = new WHHitEffects();
    await h.init(fx, fb);
    h.spawn(0, 1, 0, 0xffcf4d, 0.8, 'block');
    assert.deepEqual(fx._played.map(p => p.name), ['light']);
    fx._played.length = 0;
    h.spawn(0, 1, 0, 0xffcf4d, 1, 'dust');
    assert.equal(fx._played.length, 0);
    assert.equal(fb.spawned.length, 1);
    assert.equal(fb.spawned[0][5], 'dust');
  });
  it('preloads the four combat effects', async () => {
    const fx = fakeFX(), h = new WHHitEffects();
    await h.init(fx, null);
    assert.deepEqual(new Set(fx._loaded.map(l => l[0])),
      new Set(['toon-hit', 'light', 'blow', 'cure']));
    assert.ok(fx._loaded.every(l => l[1].endsWith('.efkefc')));
    assert.equal(EFX_ASSETS['toon-hit'], 'ToonHit.efkefc');
  });
  it('falls back fully when Effekseer is unavailable', async () => {
    const fb = fakeFallback(), h = new WHHitEffects();
    await h.init(fakeFX('medium', false), fb);
    assert.equal(h.spawn(0, 1, 0, 0xffcf4d, 1.0), true);
    assert.equal(fb.spawned.length, 1);
  });
});

describe('hit-effects: kick wind trails', () => {
  it('disabled on low quality, on for medium/high', async () => {
    const hLow = new WHHitEffects();
    await hLow.init(fakeFX('low'), null);
    const anchor = { getWorldPosition(v) { return v.setFromMatrixPosition({ elements: [0,0,0,0,0,0,0,0,0,0,0,0,3,1,0,1] }); } };
    assert.equal(hLow.trailStart(anchor), null);
    const hMed = new WHHitEffects();
    await hMed.init(fakeFX('medium'), null);
    const id = hMed.trailStart(anchor);
    assert.ok(id, 'trail id returned on medium');
    assert.equal(hMed.trailStop(id), true);
    assert.equal(hMed.trailStop(id), false, 'double stop is a no-op');
  });
});

describe('soulurge-fx: event routing', () => {
  it('no-op when Effekseer unavailable', async () => {
    const s = new WHSoulUrgeFX();
    await s.init(fakeFX('medium', false));
    assert.equal(s.ready, false);
    assert.equal(s.onActivate(fakeFighter()), false);
  });
  it('activate bursts + starts aura; expire clears it', async () => {
    const fx = fakeFX(), s = new WHSoulUrgeFX();
    await s.init(fx);
    const f = fakeFighter();
    assert.equal(s.onActivate(f), true);
    assert.deepEqual(fx._played.map(p => p.name).sort(), ['light', 'toon-hit']);
    // aura re-pulses while urging
    f._urgeOn = true;
    s.update(AURA_REPLAY_S);
    assert.ok(fx._played.some(p => p.name === 'cure'), 'aura re-pulsed');
    s.onExpire(f);
    s.update(AURA_REPLAY_S);
    const cures = fx._played.filter(p => p.name === 'cure').length;
    assert.equal(cures, 1, 'no more auras after expire');
  });
  it('smash and dash play their bursts', async () => {
    const fx = fakeFX(), s = new WHSoulUrgeFX();
    await s.init(fx);
    assert.equal(s.onSmash(fakeFighter()), true);
    assert.deepEqual(fx._played.map(p => p.name).sort(), ['blow', 'light', 'toon-hit']);
    fx._played.length = 0;
    assert.equal(s.onDash(fakeFighter()), true);
    assert.deepEqual(fx._played.map(p => p.name), ['blow']);
  });
});
