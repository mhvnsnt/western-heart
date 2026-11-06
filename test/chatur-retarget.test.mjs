// Chatur retarget profile (Roster-100 Chatur lane, 2026-11-06). Node, no browser.
// Run: node --test test/chatur-retarget.test.mjs
//
// THE DEFECT: Chatur (Rahkasa, True Ogre base) is the roster's only
// four-armed fighter. Her shipped GLB (PR #1572) carries her blend's
// full 263-bone deform set, but its hierarchy is FLAT — the limb roots
// (shoulders, arms, up-legs, the waist arm pair) are parented to the
// armature root, not to the torso, because the deform-only Blender
// export dropped their ORG parents. analyzeRig's chest search (lowest
// common ancestor of the two upper arms) therefore landed on the
// armature node — not a bone — and retargetT3Clips returned null for
// EVERY clip: she was pose-only while her ogre bank (211 clips) sat
// loaded. docs/proof/2026-11-06/item7-bank-stance-fit/DIAGNOSIS.md
// recorded it as "rig analysis bails on his four-armed 264-joint rig".
//
// THE FIX (RETARGET_PROFILES in game/js/t3anims.js, the bone-mask /
// retarget-profile pattern of Unreal IK Retargeter / Unity Avatar
// Masks): analyzeRig falls back to the rig's canonical chest anchor
// when the LCA is not a bone; the core fit metric (contact/floor set,
// the select gate's clavicle pair) covers ONLY the canonical core
// chain; her waist arm pair is a masked SECONDARY layer driven by
// the same bank clip sampled timeOffsetFrames later (Phase 1 fill —
// Phase 2 swaps the layer source per move from chatur.json layer2).
//
// The model here is built from test/fixtures/chatur-rig.json — the
// node hierarchy + rest TRS extracted verbatim from the shipped GLB
// (roster/rahkasa/attires/attire1/model-rigged-textured.glb, git blob
// bba5d1e0 on main) — so the test runs on her real rig, not a stand-in.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const T = await import(join(ROOT, 'game/js/t3anims.js'));

// GLTFLoader sanitizes node names at load (PropertyBinding
// .sanitizeNodeName strips '.'): the runtime model carries
// 'DEF-upper_armL002', not the file's 'DEF-upper_arm.L.002'. The
// fixture builder applies the same sanitization so this test runs
// under the browser's conditions, not the file's.
const gltfName = (n) => String(n || '').replace(/[^a-zA-Z0-9_]/g, '');

function buildModelFromFixture(file) {
  const fx = JSON.parse(readFileSync(join(ROOT, 'test/fixtures', file), 'utf8'));
  const objs = fx.nodes.map((n) => {
    const o = n.bone ? new THREE.Bone() : new THREE.Object3D();
    o.name = gltfName(n.name);
    o.position.fromArray(n.translation);
    o.quaternion.fromArray(n.rotation);
    o.scale.fromArray(n.scale);
    return o;
  });
  fx.nodes.forEach((n, i) => { for (const c of n.children) objs[i].add(objs[c]); });
  const model = new THREE.Group();
  model.name = 'test-instance';
  for (const r of fx.roots) model.add(objs[r]);
  model.updateMatrixWorld(true);
  return model;
}

function boneByName(model, name) {
  let hit = null;
  model.traverse((o) => { if (o.name === name && !hit) hit = o; });
  return hit;
}
const wp = (o) => o.getWorldPosition(new THREE.Vector3());

test('chatur: retarget no longer bails — ogre stance retargets onto her 264-joint rig', async () => {
  const clips = await T.loadT3Clips(THREE, 'ogre');
  assert.ok(clips && clips.stance, 'ogre bank stance loaded');
  const model = buildModelFromFixture('chatur-rig.json');
  const rc = T.retargetT3Clips(clips, 'ogre', model, THREE, 'chatur');
  assert.ok(rc, 'retargetT3Clips returned null (the pose-only defect)');
  assert.ok(rc.stance, 'no stance clip retargeted');
  assert.ok(rc.light && rc.medium && rc.heavy, 'generic attack clips retargeted');
  // The intrinsic stamp is the SOURCE clip's own chest-relative
  // clavicle swing (Wave 3 item 7): measured 0.69 / 0.55 rad for the
  // ogre neutral on its own skeleton (intrinsic.json). Pinned here as
  // data truth — the stamp must keep reporting the clip, not the rig.
  const intr = rc.stance.userData.intrinsicRel;
  assert.ok(intr, 'stance clip carries no intrinsicRel stamp');
  assert.ok(Math.abs(intr.L - 0.69) < 0.08, `intrinsic L ${intr.L} != measured 0.69`);
  assert.ok(Math.abs(intr.R - 0.55) < 0.08, `intrinsic R ${intr.R} != measured 0.55`);
});

test('chatur: stance pose passes the gate geometry checks (head above hips, hands within reach)', async () => {
  const clips = await T.loadT3Clips(THREE, 'ogre');
  const model = buildModelFromFixture('chatur-rig.json');
  const rc = T.retargetT3Clips(clips, 'ogre', model, THREE, 'chatur');
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(rc.stance);
  action.setLoop(THREE.LoopRepeat, Infinity);
  action.play();
  mixer.update(0.05); // the select gate's sample time
  model.updateWorldMatrix(true, true);
  const head = wp(boneByName(model, 'Head')), hips = wp(boneByName(model, 'Hips'));
  assert.ok(head.y - hips.y > 0.25, `head-hips gap ${head.y - hips.y} (gate check a)`);
  for (const s of ['Left', 'Right']) {
    const arm = wp(boneByName(model, s + 'Arm'));
    const fore = wp(boneByName(model, s + 'ForeArm'));
    const hand = wp(boneByName(model, s + 'Hand'));
    const reach = (arm.distanceTo(fore) + fore.distanceTo(hand)) * 1.25 + 0.05;
    assert.ok(arm.distanceTo(hand) <= reach, `${s} hand beyond arm reach (gate check b)`);
  }
});

test('chatur: the waist pair is driven by the masked secondary layer (real clip data, offset)', async () => {
  const clips = await T.loadT3Clips(THREE, 'ogre');
  const model = buildModelFromFixture('chatur-rig.json');
  const rc = T.retargetT3Clips(clips, 'ogre', model, THREE, 'chatur');
  const names = new Set(rc.stance.tracks.map((t) => t.name));
  for (const n of ['DEF-upper_arm.L.002', 'DEF-forearm.L.002', 'DEF-hand.L.001',
    'DEF-upper_arm.R.002', 'DEF-forearm.R.002', 'DEF-hand.R.001']) {
    assert.ok(names.has(`${gltfName(n)}.quaternion`), `stance clip has no secondary track for ${n} (loaded as ${gltfName(n)})`);
  }
  // The layer must actually MOVE the waist hands, and on the offset
  // layer's own timing — not copy the primary hands' positions.
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(rc.stance);
  action.setLoop(THREE.LoopRepeat, Infinity);
  action.play();
  const hand2 = boneByName(model, gltfName('DEF-hand.L.001'));
  const hand1 = boneByName(model, 'LeftHand');
  mixer.update(0.05); model.updateWorldMatrix(true, true);
  const a2 = wp(hand2), a1 = wp(hand1);
  mixer.update(0.45); model.updateWorldMatrix(true, true);
  const b2 = wp(hand2), b1 = wp(hand1);
  assert.ok(a2.distanceTo(b2) > 0.01, 'waist hand never moves — secondary layer is dead');
  assert.ok(a1.distanceTo(b1) > 0.01, 'primary hand never moves — core retarget is dead');
});

test('chatur: move rows retarget with the secondary layer too (row 38 = her "1")', async () => {
  const clips = await T.loadT3Clips(THREE, 'ogre');
  const model = buildModelFromFixture('chatur-rig.json');
  T.retargetT3Clips(clips, 'ogre', model, THREE, 'chatur'); // bind-time pass captures the rig
  const rc = T.retargetT3Clips(clips, 'ogre', model, THREE, 'chatur', ['row:38']);
  assert.ok(rc && rc['row:38'], 'row 38 did not retarget');
  const names = new Set(rc['row:38'].tracks.map((t) => t.name));
  assert.ok(names.has('DEFhandL001.quaternion'), 'row 38 has no secondary hand track');
  assert.ok(names.has('LeftHand.quaternion'), 'row 38 has no primary hand track');
});

test('profile is data, not a name hack: only chatur has one, and its chains resolve on her rig', () => {
  assert.deepEqual(Object.keys(T.RETARGET_PROFILES), ['chatur']);
  const p = T.retargetProfileFor('chatur');
  assert.equal(p.secondaryChains.length, 2);
  assert.equal(T.retargetProfileFor('pantera'), null);
  const model = buildModelFromFixture('chatur-rig.json');
  for (const chain of p.secondaryChains) {
    for (const role of ['Arm', 'ForeArm', 'Hand']) {
      assert.ok(boneByName(model, gltfName(chain.bones[role])), `profile bone ${chain.bones[role]} missing on the rig`);
    }
  }
});

test('phase 2: a donor-bank clip drives the waist pair (layer2 composite), core untouched', async () => {
  const ogre = await T.loadT3Clips(THREE, 'ogre');
  const kuma = await T.loadT3Clips(THREE, 'kuma');
  const model = buildModelFromFixture('chatur-rig.json');
  const plain = T.retargetT3Clips(ogre, 'ogre', model, THREE, 'chatur', ['row:50']);
  assert.ok(plain && plain['row:50'], 'plain row 50 retargets');
  // Second Mudra (ogre row 50, contact 11f@60) + Kuma row 130 paw
  // (contact 14f@60): phase_offset_frames +3 in the data's 60 fps
  // domain = +2 clip frames (30 fps) at the engine boundary.
  const layered = T.retargetT3Clips(ogre, 'ogre', model, THREE, 'chatur', ['row:50'],
    { cacheAs: 'row:50#l2', layer: { clips: kuma, bankId: 'kuma', clipName: 'row:130', offsetFrames: 2 } });
  assert.ok(layered && layered['row:50#l2'], 'layered composite retargets under its cache key');
  assert.ok(!layered['row:50'], 'layered call does not masquerade as the plain clip');
  const lc = layered['row:50#l2'], pc = plain['row:50'];
  const trackOf = (clip, name) => clip.tracks.find((t) => t.name === name);
  // Core chain: byte-identical values — the layer never touches it.
  assert.deepEqual(trackOf(lc, 'LeftHand.quaternion').values, trackOf(pc, 'LeftHand.quaternion').values,
    'layer altered the primary hand track');
  assert.deepEqual(trackOf(lc, 'Hips.quaternion').values, trackOf(pc, 'Hips.quaternion').values,
    'layer altered the hips track');
  // Waist chain: present, and DIFFERENT motion from the self fill —
  // it is the donor clip's data now.
  for (const n of ['DEFupper_armL002', 'DEFforearmL002', 'DEFhandL001', 'DEFupper_armR002', 'DEFforearmR002', 'DEFhandR001']) {
    assert.ok(trackOf(lc, `${n}.quaternion`), `layered clip missing waist track ${n}`);
  }
  assert.notDeepEqual(trackOf(lc, 'DEFhandR001.quaternion').values, trackOf(pc, 'DEFhandR001.quaternion').values,
    'waist hand still on the self fill — donor layer did not take over');
  // And it moves: sample the layered clip on a mixer.
  const mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(lc);
  action.setLoop(THREE.LoopOnce, 1);
  action.play();
  const hand2 = boneByName(model, gltfName('DEF-hand.R.001'));
  mixer.update(0.05); model.updateWorldMatrix(true, true);
  const a = wp(hand2);
  mixer.update(0.3); model.updateWorldMatrix(true, true);
  const b = wp(hand2);
  assert.ok(a.distanceTo(b) > 0.02, 'donor-layered waist hand does not travel during Second Mudra');
  // The plain clip is still cached clean afterwards.
  const again = T.retargetT3Clips(ogre, 'ogre', model, THREE, 'chatur', ['row:50']);
  assert.equal(again['row:50'], pc, 'plain row 50 cache polluted by the layered variant');
});

test('phase 2: ambient stance layer (donor stance clip) retargets onto the waist pair', async () => {
  const ogre = await T.loadT3Clips(THREE, 'ogre');
  const kuma = await T.loadT3Clips(THREE, 'kuma');
  assert.ok(kuma.stance, 'kuma bank has a stance clip');
  const model = buildModelFromFixture('chatur-rig.json');
  T.retargetT3Clips(ogre, 'ogre', model, THREE, 'chatur');
  const layered = T.retargetT3Clips(ogre, 'ogre', model, THREE, 'chatur', ['stance'],
    { cacheAs: 'stance#l2', layer: { clips: kuma, bankId: 'kuma', clipName: 'stance', offsetFrames: 0 } });
  assert.ok(layered && layered['stance#l2'], 'layered stance retargets');
  const names = new Set(layered['stance#l2'].tracks.map((t) => t.name));
  assert.ok(names.has('DEFhandL001.quaternion') && names.has('DEFhandR001.quaternion'),
    'ambient stance layer carries no waist tracks');
});

test('regression: a canonical hierarchy rig still retargets (jin bank, synthetic Mixamo chain)', async () => {
  // Minimal canonical rig: torso chain intact, arms parented under the
  // chest, legs under the hips — the shape every other fighter ships.
  const mk = (name, parent, x, y, z) => {
    const b = new THREE.Bone(); b.name = name; b.position.set(x, y, z);
    if (parent) parent.add(b);
    return b;
  };
  const model = new THREE.Group();
  const hips = mk('Hips', model, 0, 1.0, 0);
  const spine = mk('Spine', hips, 0, 0.12, 0);
  const spine1 = mk('Spine1', spine, 0, 0.12, 0);
  const chest = mk('Chest', spine1, 0, 0.12, 0);
  const neck = mk('Neck', chest, 0, 0.14, 0);
  mk('Head', neck, 0, 0.16, 0);
  for (const s of ['Left', 'Right']) {
    const d = s === 'Left' ? 1 : -1;
    const sh = mk(s + 'Shoulder', chest, d * 0.10, 0.10, 0);
    const arm = mk(s + 'Arm', sh, d * 0.16, 0, 0);
    const fore = mk(s + 'ForeArm', arm, d * 0.26, 0, 0);
    mk(s + 'Hand', fore, d * 0.24, 0, 0);
    const up = mk(s + 'UpLeg', hips, d * 0.10, -0.06, 0);
    const leg = mk(s + 'Leg', up, 0, -0.45, 0);
    const foot = mk(s + 'Foot', leg, 0, -0.44, 0);
    mk(s + 'ToeBase', foot, 0, -0.03, 0.10);
  }
  model.updateMatrixWorld(true);
  const clips = await T.loadT3Clips(THREE, 'jin');
  const rc = T.retargetT3Clips(clips, 'jin', model, THREE, 'synthetic-canonical');
  assert.ok(rc && rc.stance, 'canonical rig retarget regressed');
  const names = new Set(rc.stance.tracks.map((t) => t.name));
  assert.ok(![...names].some((n) => n.includes('DEF-')), 'canonical rig gained secondary tracks');
});
