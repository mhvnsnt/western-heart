// Decal wear-off (2026-11-02): face paint disappears, tattoos fade to
// a floor, scars barely fade. Pure logic — no browser, no THREE.
// Run: node --test test/wear-off.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createLayer, applyHit, applyTime, isGone, setMaterialOpacity, WEAR_FLOORS,
} from '../game/js/wear-off.js';

test('face paint wears off on hits to its zone only', () => {
  const paint = createLayer({ id: 'p1', kind: 'facepaint', zone: 'face' });
  assert.equal(applyHit(paint, { zone: 'upper', strength: 1 }), 1, 'body hit does not touch face paint');
  assert.equal(applyHit(paint, { zone: 'face', strength: 1 }), 0.8);
  assert.equal(applyHit(paint, { zone: 'face', strength: 2 }), 0.4, 'stronger hit wears more');
});

test('face paint reaches 0 and is gone; tattoos and scars stop at their floors', () => {
  const paint = createLayer({ id: 'p', kind: 'facepaint', zone: 'face' });
  for (let i = 0; i < 10; i++) applyHit(paint, { zone: 'face' });
  assert.equal(paint.opacity, 0);
  assert.equal(isGone(paint), true);
  const tat = createLayer({ id: 't', kind: 'tattoo', zone: 'upper' });
  for (let i = 0; i < 30; i++) applyHit(tat, { zone: 'upper' });
  assert.equal(tat.opacity, WEAR_FLOORS.tattoo);
  assert.equal(isGone(tat), false, 'a tattoo never disappears');
  const scar = createLayer({ id: 's', kind: 'scar', zone: 'face' });
  for (let i = 0; i < 30; i++) applyHit(scar, { zone: 'face' });
  assert.equal(scar.opacity, WEAR_FLOORS.scar);
  assert.equal(isGone(scar), false, 'a scar never disappears');
});

test('sweat + time wear face paint, not tattoos or scars', () => {
  const dry = createLayer({ id: 'd', kind: 'facepaint', zone: 'face' });
  const sweaty = createLayer({ id: 'w', kind: 'facepaint', zone: 'face' });
  applyTime(dry, 5, 0);
  applyTime(sweaty, 5, 1);
  assert.ok(sweaty.opacity < dry.opacity, 'sweat speeds face-paint wear');
  const tat = createLayer({ id: 't', kind: 'tattoo', zone: 'face' });
  applyTime(tat, 5, 1);
  assert.equal(tat.opacity, 0.95, 'sweat does not speed tattoo wear');
});

test('setMaterialOpacity bridges to a THREE-style material, safely', () => {
  const mat = { opacity: 1, transparent: false, needsUpdate: false };
  assert.equal(setMaterialOpacity(mat, 0.4), true);
  assert.equal(mat.opacity, 0.4);
  assert.equal(mat.transparent, true);
  assert.equal(mat.needsUpdate, true);
  assert.equal(setMaterialOpacity({ color: 0xffffff }, 0.4), false, 'no opacity property: no touch, no throw');
  assert.equal(setMaterialOpacity(null, 0.4), false);
});

test('unknown kind and missing id are rejected, not silently accepted', () => {
  assert.throws(() => createLayer({ id: 'x', kind: 'blood' }), /unknown kind/);
  assert.throws(() => createLayer({ kind: 'tattoo' }), /needs an id/);
});
