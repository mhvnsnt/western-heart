// Lane 8 real-rig test — rig-compat against REAL bone names from
// owned full-game files (2026-10-24 owned-file correction), NOT
// community approximations and NOT guessed patterns.
// Run: node test/oss-lane8-real-rigs.test.mjs  (from repo root)
// Fixtures (names only — no mesh, texture, or animation data):
//   test/fixtures/cape-node-names.json  — 95 CapeJones_Rig node
//     names from WH's own Cape stance GLB (deform + FK/IK/pole
//     control bones; the mapper must pick the deform bones).
//   test/fixtures/alisa-bone-names.json — 111 Alisa source bone
//     names from the WH Alisa->Cape bonemap (source: T7 Alisa_ARM).
// What this proves: mapRigBones + resolveRig work on the real
// rigs WH actually builds on. What it does NOT prove: T3 or
// Tripo rigs (their patterns are still provisional — see
// game/js/rig-compat.js header and the lane doc).
import assert from 'node:assert';
import fs from 'node:fs';
import { mapRigBones, resolveRig } from '../game/js/rig-compat.js';

const CORE = ['hips', 'spine', 'chest', 'neck', 'head',
  'shoulderL', 'elbowL', 'wristL', 'shoulderR', 'elbowR', 'wristR',
  'hipL', 'kneeL', 'ankleL', 'hipR', 'kneeR', 'ankleR'];
let checks = 0;

function load(rel) {
  return JSON.parse(fs.readFileSync(new URL(rel, import.meta.url), 'utf8')).bones;
}

const cape = load('./fixtures/cape-node-names.json');
assert.strictEqual(cape.length, 95, 'cape fixture: 95 node names');
const capeMap = mapRigBones('cape-94', cape);
for (const role of CORE) {
  assert.ok(capeMap[role], `real cape rig: ${role} unmapped`);
  checks++;
}
// Deform bones win over FK/IK control bones (normalization must
// not match forearm_fk_L for forearm_L, etc.).
assert.strictEqual(capeMap.elbowL, 'forearm_L', 'real cape: elbowL must be forearm_L, got ' + capeMap.elbowL);
assert.strictEqual(capeMap.wristL, 'hand_L', 'real cape: wristL must be hand_L, got ' + capeMap.wristL);
assert.strictEqual(capeMap.hipL, 'thigh_L', 'real cape: hipL must be thigh_L, got ' + capeMap.hipL);
assert.strictEqual(capeMap.shoulderL, 'clavicle_L', 'real cape: shoulderL must be clavicle_L (bonemap authority), got ' + capeMap.shoulderL);
assert.strictEqual(resolveRig(cape), 'cape-94', 'real cape rig must resolve to cape-94, got ' + resolveRig(cape));
checks += 5;

const alisa = load('./fixtures/alisa-bone-names.json');
assert.strictEqual(alisa.length, 111, 'alisa fixture: 111 bone names');
const alisaMap = mapRigBones('t7-160', alisa);
for (const role of CORE) {
  assert.ok(alisaMap[role], `real alisa rig: ${role} unmapped`);
  checks++;
}
assert.strictEqual(alisaMap.shoulderL, 'LeftShoulder', 'real alisa: shoulderL');
assert.strictEqual(alisaMap.elbowL, 'LeftForeArm', 'real alisa: elbowL');
assert.strictEqual(alisaMap.hipL, 'LeftUpLeg', 'real alisa: hipL');
assert.strictEqual(resolveRig(alisa), 't7-160', 'real alisa rig must resolve to t7-160, got ' + resolveRig(alisa));
checks += 4;

// Cross-check: the bonemap's own role mapping agrees with ours
// on the core chain (bonemap: LeftShoulder->clavicle_L, etc. —
// our cape map puts shoulderL on clavicle_L, elbowL on forearm_L,
// hipL on thigh_L, exactly as the bonemap's targets).
assert.strictEqual(capeMap.elbowL, 'forearm_L', 'bonemap cross-check elbow');
assert.strictEqual(capeMap.kneeL, 'shin_L', 'bonemap cross-check knee');
assert.strictEqual(capeMap.ankleL, 'foot_L', 'bonemap cross-check ankle');
checks += 3;

console.log(`OSS LANE 8 REAL-RIG TESTS: PASS (${checks} checks, real Cape 95-node + real Alisa 111-bone fixtures)`);
