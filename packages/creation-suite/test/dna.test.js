import test from 'node:test';
import assert from 'node:assert/strict';
import { makeDNA, migrate, fromJSON, toJSON, clampSlider } from '../src/dna.js';
import { physicsFor, REGIONS } from '../src/regions.js';

test('body types + clamp', () => {
  const d = makeDNA({ bodyType: 'heavy', sliders: { belly: 9 } });
  assert.equal(d.sliders.belly, 2.0);
  assert.equal(d.sliders.weight, 1.0);
  assert.throws(() => clampSlider('nope', 1));
});
test('Bannon DNA v1 migrates', () => {
  const v2 = migrate({ v: 1, name: 'BANNON', base: 'male', morphs: { chest: 1.4, bust: 1.2 }, boneScale: { height: 1.15 }, spec: { mask: 'bannon_mask' } });
  assert.equal(v2.v, 2); assert.ok(Math.abs(v2.sliders.height - 0.15) < 1e-9); assert.equal(v2.attire.face.id, 'bannon_mask');
  assert.deepEqual(fromJSON(toJSON(v2)), v2);
});
test('physics adapts to size', () => {
  assert.equal(physicsFor('chestL', 0.03, 0.08), null);           // flat chest -> no jiggle bone
  const slim = physicsFor('belly', 0.12, 0.13), heavy = physicsFor('belly', 0.2, 0.13);
  assert.ok(heavy.mass > slim.mass && heavy.stiffness < slim.stiffness && heavy.maxOffset > slim.maxOffset);
  for (const r of Object.values(REGIONS)) assert.ok(r.a && r.b && r.radius.length === 3);
});
import { suiteMenu } from '../src/menu.js';
test('per-game suite names and flow', () => {
  assert.equal(suiteMenu('Bannon').label, 'Create a Wrestler');
  assert.equal(suiteMenu('western-heart').label, 'Create a Fighter');
  for (const c of suiteMenu('AshLanev2').children) assert.equal(c.next, 'characterList');
});
