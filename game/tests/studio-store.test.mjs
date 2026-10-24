// Studios (Bannon port): store contract + consumers. node --test game/tests/studio-store.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
const mem = {}; globalThis.localStorage = { getItem: k => mem[k] ?? null, setItem: (k, v) => { mem[k] = String(v); } };
const S = await import('../js/studio/studio-store.js');
const A = await import('../js/studio/studio-apply.js');
const P = await import('../js/studio/studio-pose.js').catch(() => null);

test('patchFighter persists per fighter and exports a bundle', () => {
  S.patchFighter('pantera', { selectPose: { RightArm: [0.1, 0, 0] } });
  assert.deepEqual(S.getFighterData('pantera').selectPose.RightArm, [0.1, 0, 0]);
  const b = S.exportBundle(); assert.equal(b.format, 'wh-studio-bundle'); assert.ok(b.fighters.pantera);
});
test('Buffalo Bill select pose stays locked (owner rule)', () => {
  S.patchFighter('buffalo-bill', { selectPose: { Head: [1, 0, 0] }, ai: { aggression: 0.9 } });
  assert.equal(S.getFighterData('buffalo-bill').selectPose, undefined);
  assert.equal(S.getFighterData('buffalo-bill').ai.aggression, 0.9);
});
test('import bundle merges and respects the lock', () => {
  S.importBundle({ format: 'wh-studio-bundle', fighters: { skull: { fightPose: { Spine: [0, 0.2, 0] } }, 'buffalo-bill': { selectPose: { Head: [1, 1, 1] } } }, library: { poses: { p1: {} } } });
  assert.ok(S.getFighterData('skull').fightPose); assert.equal(S.getFighterData('buffalo-bill').selectPose, undefined);
  assert.ok(S.loadDB().library.poses.p1);
});
test('applyCharOverrides puts AI DNA + strike tuning on the real fighter, clamped', () => {
  S.patchFighter('pantera', { ai: { aggression: 5, reaction: 0.2 }, strike: { power: 9, speed: 1 } });
  const f = { char: { id: 'pantera' }, aiProfile: { aggression: 0.6, grabBias: 0.15, reaction: 0.55 }, stats: { speed: 2.8, power: 1.1 } };
  assert.ok(A.applyCharOverrides(f));
  assert.equal(f.aiProfile.aggression, 1); assert.equal(f.aiProfile.reaction, 0.2); assert.equal(f.aiProfile.grabBias, 0.15);
  assert.equal(f.stats.power, 1.4); assert.equal(f.stats.speed, 2.0); assert.ok(f.studio.selectPose);
});
test('bone matching handles mixamo prefixes and spine aliases', () => {
  const idx = { hips: 1, spine2: 2, rightarm: 3 };
  assert.equal(A.normBone('mixamorig:RightArm'), 'rightarm');
  assert.equal(A.findBone(idx, 'Spine1'), 2); assert.equal(A.findBone(idx, 'RightArm'), 3);
});
test('fighter.js and select-screen.js consume studio saves', async () => {
  const fs = await import('node:fs');
  const f = fs.readFileSync(new URL('../js/fighter.js', import.meta.url), 'utf8');
  const s = fs.readFileSync(new URL('../js/select-screen.js', import.meta.url), 'utf8');
  assert.match(f, /applyCharOverrides\(this\)/); assert.match(f, /studio\.fightPose/);
  assert.match(s, /studioPoseFor\(c\.id, 'selectPose'\)/);
});
