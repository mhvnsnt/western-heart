/* morph-apply.test.mjs — Phase 3 completion (2026-11-02).
 * WHAT THIS GUARDS: the game side must READ the creation suite's saved
 * morph slider values (body.morph_targets) and turn them into
 * morphTargetInfluences on the built model, with the suite's exact
 * '<id>+' / '<id>-' convention — previously custom-fighter.js silently
 * dropped morph_targets, so a created fighter's body/face shaping never
 * reached the game at all.
 * Run: node --test game/tests/morph-apply.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { applyMorphTargets, clampMorph } from '../js/morph-apply.js';
import { customFighterToRoster } from '../js/custom-fighter.js';

function fakeMesh() {
  return {
    morphTargetDictionary: { 'chest+': 0, 'chest-': 1, 'jaw+': 2, 'jaw-': 3, 'cs_proxy': 4 },
    morphTargetInfluences: [0, 0, 0, 0, 0.7],
  };
}

test('positive value drives the + target, negative the - target', () => {
  const m = fakeMesh();
  const live = applyMorphTargets([m], { chest: 0.5, jaw: -0.25 });
  assert.equal(live, 2);
  assert.equal(m.morphTargetInfluences[0], 0.5);
  assert.equal(m.morphTargetInfluences[3], 0.25);
  assert.equal(m.morphTargetInfluences[1], 0);
  assert.equal(m.morphTargetInfluences[2], 0);
});

test('stale slider targets reset to 0; non-slider targets untouched', () => {
  const m = fakeMesh();
  m.morphTargetInfluences[0] = 0.9;
  applyMorphTargets([m], {});
  assert.equal(m.morphTargetInfluences[0], 0);
  assert.equal(m.morphTargetInfluences[4], 0.7); // cs_proxy left alone
});

test('values clamp to -1..1 and unknown sliders are ignored', () => {
  const m = fakeMesh();
  const live = applyMorphTargets([m], { chest: 5, nose: 0.5 });
  assert.equal(live, 1);
  assert.equal(m.morphTargetInfluences[0], 1);
  assert.equal(clampMorph(-3), -1);
  assert.equal(clampMorph('x'), 0);
});

test('models without morph targets are a no-op, not a crash', () => {
  assert.equal(applyMorphTargets([{ name: 'plain' }], { chest: 1 }), 0);
  assert.equal(applyMorphTargets(null, { chest: 1 }), 0);
});

test('customFighterToRoster passes morph_targets through (was silently dropped)', () => {
  const F = {
    profile: { name: 'TESTER' },
    body: { body_type: 'Medium 1', skin_tone: '#c98d5e', morph_targets: { chest: 0.5, jaw: -0.25 } },
    template: 'powerhouse',
    baseGlb: 'customization/templates/meshes/powerhouse.glb',
  };
  const r = customFighterToRoster(F);
  assert.deepEqual(r.morphTargets, { chest: 0.5, jaw: -0.25 });
  assert.equal(r.template, 'powerhouse');
  assert.equal(r.baseGlb, 'customization/templates/meshes/powerhouse.glb');
});

test('customFighterToRoster defaults morphTargets to {} when the suite saved none', () => {
  const r = customFighterToRoster({ profile: { name: 'PLAIN' }, body: { body_type: 'Medium 1' } });
  assert.deepEqual(r.morphTargets, {});
  assert.equal(r.baseGlb, null);
});
