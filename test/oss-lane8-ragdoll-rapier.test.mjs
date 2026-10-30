// Lane 8 Rapier ragdoll test — real @dimforge/rapier3d-compat WASM.
// Run: node test/oss-lane8-ragdoll-rapier.test.mjs  (from repo root)
// The Rapier package is a dev/test dependency: if it is not
// installed in this checkout, the test SKIPS cleanly instead of
// failing (the joint physics was proven in the pull-wire session
// with the same package + same body definition). In staging, run
// with NODE_PATH pointing at the pull-wire node_modules.
//   NODE_PATH=~/workspace/pulls-wire/js-tests/node_modules node test/oss-lane8-ragdoll-rapier.test.mjs
import assert from 'node:assert';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);

let RAPIER;
try {
  RAPIER = require('@dimforge/rapier3d-compat').default || require('@dimforge/rapier3d-compat');
} catch (e) {
  console.log('OSS LANE 8 RAPIER TEST: SKIP — @dimforge/rapier3d-compat not installed in this checkout: ' + e.message);
  process.exit(0);
}
const { createRagdoll } = await import('../game/js/ragdoll.js');

const rag = await createRagdoll(RAPIER, { spawn: [0, 3, 0] });
rag.step(120); // 2s sim, same as the pull-wire proof
const pos = rag.positions();
console.log('ragdoll positions:', JSON.stringify(pos));
// Full-body version: legs touch the ground and hold the torso up,
// so the torso rests ABOVE the 4-part proof's y~0.5 (torso alone).
// What must hold: nothing falls through the floor, legs are near
// the ground, torso is settled (not floating at spawn height).
assert.ok(pos.torso[1] > 0.4 && pos.torso[1] < 1.8, `rapier: torso settled above ground, got ${pos.torso[1]}`);
assert.ok(pos.legL[1] < 0.6 && pos.legR[1] < 0.6, `rapier: legs rest near ground, got L=${pos.legL[1]} R=${pos.legR[1]}`);
assert.ok(Object.values(pos).every((p) => p[1] >= -0.05), 'rapier: no part fell through the floor');
const dHead = rag.distance('torso', 'head');
assert.ok(dHead < 1.2, `rapier: torso-head joint held (dist ${dHead} < 1.2)`);
const dArm = rag.distance('torso', 'armL');
assert.ok(dArm < 1.2, `rapier: torso-armL joint held (dist ${dArm} < 1.2)`);
assert.ok(pos.armL[1] < pos.torso[1] + 0.5, 'rapier: arm hangs (not floating above torso)');
const fakeBones = { torso: { position: { set(x, y, z) { this.v = [x, y, z]; } } } };
rag.applyToBones(fakeBones);
assert.ok(fakeBones.torso.position.v, 'rapier: applyToBones writes bone positions');
console.log(`OSS LANE 8 RAPIER TEST: PASS (torso y=${pos.torso[1].toFixed(2)}, torso-head=${dHead.toFixed(3)}, torso-armL=${dArm.toFixed(3)})`);
