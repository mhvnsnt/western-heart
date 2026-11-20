// Head-frame normalization (roster head/face audit, 2026-11-06). Node, no browser.
// Run: node --test test/head-frame-normalization.test.mjs
//
// THE DEFECT (owner, 2026-11-06): "some characters, more than the ones
// in naming, but kinpo, zui, and others, have a twisted neck and head
// where they are facing 3/4 towards the cam in a odd way instead of
// facing their opponents... Yukihyo has some face stretch issues
// during match and so do many others."
//
// MEASURED ROOT CAUSE: the head is the one driven joint whose swing
// correction A(c) is identity in retargetT3Clips, so a bank's head
// track lands on the target rig exactly as baked. The banks were
// baked on each source character's own part rig, whose head joint
// frame is itself rotated: the head-vs-chest rotation of a bank's
// own neutral stance is a large CONSTANT (jin 90.9°, heihachi
// 114.6°, yoshimitsu 96.5°, jun 85.9°, bryan 77.2°, ...), while the
// one canonically-baked bank — king — measures 0.0° and its fighter
// (Pantera) is the roster's reference-good. On target rigs the
// constant is a twisted neck (the neck chain takes the chest driver,
// the head takes the twisted head driver), and the skin between
// shears — the "face stretch during match" (kinpo's head-region
// vertex distortion measured 17% mean in stance before the fix,
// 5.6% after; pantera 0.1%).
//
// THE FIX (game/js/t3anims.js, estimateHeadOffset + the frame-loop
// counter-rotation): the bank's constant is measured from its own
// stance at the first full retarget call and counter-rotated out of
// the head's world rotation in the chest frame, preserving every
// clip's variation around the constant. Banks under 20° keep their
// data exactly (king 0.0°, bosconovitch 16.2°); 't7:' skeletons are
// exempt (jointed-rig path, owner-approved fighters).
//
// This test runs the REAL jin and king banks through the REAL
// retarget onto a synthetic canonical rig (Mixamo-shaped, identity
// rest) and pins the behavior for the owner-named fighters:
// kinpo + zui fight on the jin bank, yukihyo on the king bank.
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const T = await import(join(ROOT, 'game/js/t3anims.js'));

// A canonical humanoid rig: identity rest rotations, spine up +Y,
// arms out along +/-X, legs down. analyzeRig finds the chest as the
// arms' lowest common ancestor (Spine2), like the shipped Mixamo rigs.
function buildCanonicalRig() {
  const B = (name, parent, x, y, z) => {
    const b = new THREE.Bone(); b.name = name; b.position.set(x, y, z);
    if (parent) parent.add(b); return b;
  };
  const root = new THREE.Object3D(); root.name = 'Armature';
  const hips = B('Hips', root, 0, 1.00, 0);
  const spine = B('Spine', hips, 0, 0.14, 0);
  const spine1 = B('Spine1', spine, 0, 0.14, 0);
  const spine2 = B('Spine2', spine1, 0, 0.14, 0);
  const neck = B('Neck', spine2, 0, 0.16, 0);
  B('Head', neck, 0, 0.12, 0);
  for (const s of ['Left', 'Right']) {
    const d = s === 'Left' ? 1 : -1;
    const sh = B(s + 'Shoulder', spine2, d * 0.09, 0.13, 0);
    const arm = B(s + 'Arm', sh, d * 0.11, 0, 0);
    const fore = B(s + 'ForeArm', arm, d * 0.28, 0, 0);
    B(s + 'Hand', fore, d * 0.26, 0, 0);
    const up = B(s + 'UpLeg', hips, d * 0.10, -0.05, 0);
    const leg = B(s + 'Leg', up, 0, -0.45, 0);
    const foot = B(s + 'Foot', leg, 0, -0.45, 0);
    B(s + 'ToeBase', foot, 0, -0.07, 0.10);
  }
  const model = new THREE.Group(); model.name = 'test-instance';
  model.add(root); model.updateMatrixWorld(true);
  return model;
}
const byCanon = (model, cn) => {
  let h = null;
  model.traverse((o) => { if (!h && o.isBone && T.canonBoneName(o.name) === cn) h = o; });
  return h;
};
const wq = (o) => o.getWorldQuaternion(new THREE.Quaternion());
// Head-vs-chest world-delta (each vs its own rest), YXZ degrees, at
// `frames` sampled times of the clip playing on a fresh mixer.
function headVsChest(model, clip, frames = 9) {
  const head = byCanon(model, 'Head'), chest = byCanon(model, 'Chest') || byCanon(model, 'Spine2');
  const restH = wq(head), restC = wq(chest);
  const mixer = new THREE.AnimationMixer(model);
  const act = mixer.clipAction(clip); act.setLoop(THREE.LoopRepeat, Infinity); act.play();
  const out = [];
  for (let i = 0; i < frames; i++) {
    mixer.setTime((i / (frames - 1)) * clip.duration * 0.95);
    model.updateMatrixWorld(true);
    const rel = wq(chest).multiply(restC.clone().invert()).invert()
      .multiply(wq(head).multiply(restH.clone().invert()));
    const e = new THREE.Euler().setFromQuaternion(rel, 'YXZ');
    const ws = head.getWorldScale(new THREE.Vector3());
    out.push({ yaw: e.y * 180 / Math.PI, pitch: e.x * 180 / Math.PI, scale: ws });
  }
  mixer.stopAllAction();
  return out;
}
const meanAbs = (a) => a.reduce((s, v) => s + Math.abs(v), 0) / a.length;

for (const fighter of ['kinpo', 'zui']) {
  test(`${fighter} (jin bank): stance head faces the opponent after normalization`, async () => {
    const clips = await T.loadT3Clips(THREE, 'jin');
    assert.ok(clips && clips.stance, 'jin bank stance loaded');
    const model = buildCanonicalRig();
    const rc = T.retargetT3Clips(clips, 'jin', model, THREE, fighter);
    assert.ok(rc && rc.stance, 'stance retargeted');
    // No scale keys anywhere in the retarget output, ever.
    for (const tr of rc.stance.tracks) assert.ok(!tr.name.endsWith('.scale'), `scale track emitted: ${tr.name}`);
    const samples = headVsChest(model, rc.stance);
    // Before the fix this measured yaw ~+86 deg (head turned to the
    // camera). The bank constant (90.9 deg) is normalized out; what
    // remains is the stance's own small head-vs-chest acting.
    assert.ok(meanAbs(samples.map((s) => s.yaw)) <= 20,
      `stance head-vs-chest mean |yaw| ${meanAbs(samples.map((s) => s.yaw)).toFixed(1)}deg > 20deg`);
    for (const s of samples) {
      assert.ok(Math.abs(s.scale.x - 1) < 1e-6 && Math.abs(s.scale.y - 1) < 1e-6 && Math.abs(s.scale.z - 1) < 1e-6,
        `head world scale not 1.0: ${s.scale.toArray()}`);
    }
  });
  test(`${fighter} (jin bank): a move row's head stays on the opponent`, async () => {
    const clips = await T.loadT3Clips(THREE, 'jin');
    const rowName = Object.keys(clips).find((n) => n.startsWith('row:'));
    assert.ok(rowName, 'jin bank carries move rows');
    const model = buildCanonicalRig();
    T.retargetT3Clips(clips, 'jin', model, THREE, fighter);
    const rc = T.retargetT3Clips(clips, 'jin', model, THREE, fighter, [rowName]);
    assert.ok(rc && rc[rowName], `${rowName} retargeted`);
    const samples = headVsChest(model, rc[rowName]);
    assert.ok(meanAbs(samples.map((s) => s.yaw)) <= 25,
      `row head-vs-chest mean |yaw| ${meanAbs(samples.map((s) => s.yaw)).toFixed(1)}deg > 25deg`);
  });
}

test('yukihyo (king bank): the clean bank is NOT normalized — data untouched, head scale 1.0', async () => {
  const clips = await T.loadT3Clips(THREE, 'king');
  assert.ok(clips && clips.stance, 'king bank stance loaded');
  const model = buildCanonicalRig();
  const rc = T.retargetT3Clips(clips, 'king', model, THREE, 'yukihyo');
  assert.ok(rc && rc.stance, 'stance retargeted');
  const samples = headVsChest(model, rc.stance);
  // King's stance head-vs-chest IS his real data: the bank's own
  // stance composes to a 3.4 deg head-vs-chest total (audit census).
  // The retarget must reproduce that small real offset — if a future
  // change "normalized" king too, the offset would be driven to ~0,
  // and if the head regressed it would blow past the band.
  const totals = samples.map((s) => Math.hypot(s.yaw, s.pitch));
  const meanTotal = totals.reduce((a, b) => a + b, 0) / totals.length;
  assert.ok(meanTotal > 0.8 && meanTotal < 10, `king stance head-vs-chest ${meanTotal.toFixed(1)}deg outside the measured band`);
  assert.ok(meanAbs(samples.map((s) => s.yaw)) <= 12, 'king stance head yaw drifted');
  for (const s of samples) {
    assert.ok(Math.abs(s.scale.x - 1) < 1e-6 && Math.abs(s.scale.y - 1) < 1e-6 && Math.abs(s.scale.z - 1) < 1e-6,
      `head world scale not 1.0: ${s.scale.toArray()}`);
  }
});
