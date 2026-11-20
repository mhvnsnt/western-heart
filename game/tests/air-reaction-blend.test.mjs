/* Air-reaction blend — FightingEngine public catch-height formula.
   Run: node --test game/tests/air-reaction-blend.test.mjs */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import {
  FE_AIR_BLEND_WEIGHT,
  airCatchOffset,
  blendedAirHeight,
  decayAirBlendWeight,
  beginAirCatch,
  sampleAirBlend,
} from '../js/air-reaction-blend.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const blendSrc = readFileSync(path.join(here, '../js/air-reaction-blend.js'), 'utf8');

test('FE public weight is 0.758', () => {
  assert.equal(FE_AIR_BLEND_WEIGHT, 0.758);
});

test('airCatchOffset is catch minus clip-start', () => {
  assert.equal(airCatchOffset(2.0, 1.5), 0.5);
  assert.equal(airCatchOffset(1.5, 2.0), -0.5);
  assert.equal(airCatchOffset(NaN, 1), 0);
  assert.equal(airCatchOffset(1, Infinity), 0);
});

test('blendedAirHeight = clip + offset * weight', () => {
  const offset = airCatchOffset(2.0, 1.5);
  assert.ok(Math.abs(blendedAirHeight(1.6, offset) - (1.6 + 0.5 * 0.758)) < 1e-12);
  assert.equal(blendedAirHeight(1.0, 0), 1.0);
  assert.equal(blendedAirHeight(1.0, 1, 0), 1.0);
  assert.equal(blendedAirHeight(1.0, 1, 1), 2.0);
});

test('decayAirBlendWeight clamps and decays', () => {
  assert.equal(decayAirBlendWeight(0.758, 0), 0.758);
  assert.ok(decayAirBlendWeight(0.758, 0.1, 1.6) < 0.758);
  assert.equal(decayAirBlendWeight(0.1, 1, 1.6), 0);
  assert.equal(decayAirBlendWeight(1.5, 0), 1);
});

test('beginAirCatch + sampleAirBlend pins first frame toward catch', () => {
  let st = beginAirCatch(2.0);
  let r = sampleAirBlend(st, 1.5);
  st = r.state;
  assert.equal(st.clipStartY, 1.5);
  assert.ok(Math.abs(r.y - blendedAirHeight(1.5, 0.5)) < 1e-12);
  r = sampleAirBlend(st, 1.7);
  assert.ok(Math.abs(r.y - blendedAirHeight(1.7, 0.5)) < 1e-12);
});

test('module header forbids FE leak hunting / Tag Battle canon (source anchors)', () => {
  assert.match(blendSrc, /2026-12-25/);
  assert.match(blendSrc, /do not hunt/);
  assert.match(blendSrc, /never WH roster/);
});
