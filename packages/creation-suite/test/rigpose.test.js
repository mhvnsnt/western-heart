import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createRigPoseState, applyRigSection, setBoneOffset, setBoneVisible,
  addBone, removeBone, addWeightStroke, setMeshVisibility, setPose, setFrame,
  toRigSection, rigPoseSummary,
} from '../src/rigpose.js';

// A measured-skeleton fixture in the shape glb_inspect.py emits
// (values mirror the shipped Star report: drifted rests and all).
const INSPECT = {
  skins: [{
    skin: 0, joints: 3, has_ibm: true,
    joint_rows: [
      { node: 0, name: 'Root', rest_rot_deg: 120.0, world: [0, -0.043, 0] },
      { node: 1, name: 'Hips', rest_rot_deg: 120.05, world: [0, -0.0742, 0] },
      { node: 2, name: 'Spine', rest_rot_deg: 45.0, world: [0, 0.1, 0] },
    ],
  }],
};

test('fresh state serializes to null (absence = no-op)', () => {
  const s = createRigPoseState(INSPECT);
  assert.equal(toRigSection(s), null);
  assert.equal(rigPoseSummary(s).bones, 3);
});

test('owner edits serialize to exactly the schema rig section', () => {
  const s = createRigPoseState(INSPECT);
  setFrame(s, { translate: [0, 1.05, 0] });
  setBoneOffset(s, 'Hips', { rot_deg: [-120.05, 0, 0] });
  setBoneVisible(s, 'Spine', false);
  addBone(s, { name: 'Tail', parent: 'Hips', head: [0, -0.1, -0.2], tail: [0, -0.2, -0.6] });
  addWeightStroke(s, { bone: 'Tail', center: [0, 0.8, -0.2], radius: 0.2, strength: 0.8 });
  setMeshVisibility(s, 'BodyMesh', false);
  setPose(s, 'Root', { rot_deg: [0, 30, 0] });
  removeBone(s, 'Spine');
  const rig = toRigSection(s);
  assert.deepEqual(rig.frame, { translate: [0, 1.05, 0] });
  assert.deepEqual(rig.bones.Hips.offset.rot_deg, [-120.05, 0, 0]);
  assert.equal(rig.bones.Spine.visible, false);
  assert.deepEqual(rig.add_bones[0].name, 'Tail');
  assert.deepEqual(rig.weights[0], { bone: 'Tail', center: [0, 0.8, -0.2], radius: 0.2, strength: 0.8, mode: 'add' });
  assert.deepEqual(rig.visibility, { BodyMesh: false });
  assert.deepEqual(rig.pose.Root.rot_deg, [0, 30, 0]);
  assert.deepEqual(rig.remove_bones, ['Spine']);
});

test('save -> reload reproduces the identical section (round-trip)', () => {
  const s = createRigPoseState(INSPECT);
  setBoneOffset(s, 'Root', { rot_deg: [-120, 0, 0], pos: [0, 0.05, 0] });
  addWeightStroke(s, { bone: 'Hips', center: [0, 0, 0], radius: 0.5 });
  const saved = toRigSection(s);
  const reloaded = createRigPoseState(INSPECT, saved);
  assert.deepEqual(toRigSection(reloaded), saved);
  const viaApply = applyRigSection(createRigPoseState(INSPECT), saved);
  assert.deepEqual(toRigSection(viaApply), saved);
});

test('invalid operations fail loudly', () => {
  const s = createRigPoseState(INSPECT);
  assert.throws(() => setBoneOffset(s, 'Nope', { rot_deg: [0, 0, 0] }), /unknown bone/);
  assert.throws(() => addBone(s, { name: 'Hips', parent: 'Root', head: [0, 0, 0], tail: [0, 1, 0] }), /already exists/);
  assert.throws(() => addBone(s, { name: 'X', parent: 'Ghost', head: [0, 0, 0], tail: [0, 1, 0] }), /unknown parent/);
  assert.throws(() => addWeightStroke(s, { bone: 'Ghost', center: [0, 0, 0], radius: 1 }), /unknown bone/);
});
