// Phase 4b fight-animation proof (2026-11-02). Node, no browser.
// Run: node --test test/custom-template-fight.test.mjs
// Owner task: created fighters must fight on their chosen template
// body (not the stock Soldier model), with their morphs, and must
// not T-pose. The old failure: the template GLBs name their bones
// the MB-Lab way, the game did not recognise them, and the templates
// ship zero embedded clips — so a template body in a fight had no
// animation at all and stood in its bind pose.
//
// This test proves the fix on the real rig, not just the mapping:
// it parses a real template GLB with the game's own vendored
// three.js + meshopt decoder, builds an instance through
// game/js/assets.js (which runs the MB-Lab -> T3 bone remap),
// binds the real jin fallback bank through t3anims.js's own
// retarget, plays a stance and a real attack row on the mixer,
// and measures the posed bones moving — head above hips, feet
// on the floor, a hand travelling a real distance. A mapping-only
// unit test could pass while the fighter still T-posed; this one
// cannot: a bind-pose fighter displaces nothing.
//
// Known Node limit, stated plainly: Node cannot decode the GLB's
// embedded PNG textures (no Image), so the GLTF is parsed directly
// and injected into assets.gltfs instead of going through
// assets.loadModels/_ingest (whose material gate needs decoded
// images). In a browser the same textures decode through the same
// GLTFLoader path every other fighter uses. The material gate is
// therefore NOT proven here; the rig, the remap, the retarget and
// the motion are.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// GLTFLoader reads self.URL at texture-parse time; Node has no
// `self`, so point it at the global object before parsing.
globalThis.self = globalThis;

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without customization/:
// a file that is not on disk is read from git's object store, like
// test/creation-suite-templates.test.mjs does.
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });

await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');
const { MeshoptDecoder } = await import('three/addons/libs/meshopt_decoder.js');
const A = await import(join(ROOT, 'game/js/assets.js'));
const { applyMorphTargets } = await import(join(ROOT, 'game/js/morph-apply.js'));
const CF = await import(join(ROOT, 'game/js/custom-fighter.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));

const RIG_REQUIRED = ['Hips', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightArm', 'RightForeArm', 'RightHand',
  'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot'];

const TEMPLATES = JSON.parse(bytes('customization/templates/body-templates.json').toString('utf8')).templates;

async function loadTemplate(id) {
  const buf = bytes(`customization/templates/meshes/${id}.glb`);
  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  const gltf = await loader.parseAsync(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength), '');
  return gltf;
}

test('all 9 template GLBs carry the MB-Lab rig the remap expects (71 joints, 168 morph targets)', () => {
  assert.equal(TEMPLATES.length, 9);
  for (const t of TEMPLATES) {
    const buf = bytes(t.base_mesh);
    assert.equal(buf.toString('latin1', 0, 4), 'glTF', `${t.id}: is a GLB`);
    const len = buf.readUInt32LE(12);
    const j = JSON.parse(buf.toString('utf8', 20, 20 + len));
    const joints = j.skins[0].joints.map((i) => j.nodes[i].name);
    assert.equal(joints.length, 71, `${t.id}: 71 joints`);
    for (const src of Object.keys(A.MB_LAB_T3_BONE_REMAP)) assert.ok(joints.includes(src), `${t.id}: joint ${src}`);
    const targets = j.meshes[0].extras.targetNames;
    assert.equal(targets.length, 168, `${t.id}: 168 morph targets`);
    assert.ok(targets.includes('b_weight+') && targets.includes('b_weight-'), `${t.id}: b_weight +/- targets`);
  }
});

test('customFighterToRoster resolves a saved fighter to its template model key', () => {
  const blank = (over) => ({
    profile: { name: 'TEST', title: ['', ''] },
    body: { body_type: 'Medium 1', skin_tone: '#c98d5e', morph_targets: { b_weight: 0.5 } },
    ...over,
  });
  const ph = CF.customFighterToRoster(blank({ template: 'powerhouse', baseGlb: 'customization/templates/meshes/powerhouse.glb' }));
  assert.equal(ph.model, 'custom-template-powerhouse');
  assert.equal(ph.template, 'powerhouse');
  assert.equal(ph.morphTargets.b_weight, 0.5);
  assert.equal(ph.moveset, 'jin');
  assert.equal(ph.movesetFallback, 'jin');
  // Template-less legacy save follows the suite's own migration target.
  const legacy = CF.customFighterToRoster(blank({}));
  assert.equal(legacy.model, 'custom-template-technician');
  assert.equal(legacy.template, 'technician');
  // Roster-mode save keeps the legacy slot: its attire GLB has no
  // MODEL_URLS key, and wiring it is the still-owed Phase 4 work.
  const roster = CF.customFighterToRoster(blank({
    mode: 'roster', template: null, baseGlb: 'roster/pantera/attires/leomon/model.glb',
  }));
  assert.equal(roster.model, 'custom');
  // Every template id in body-templates.json has a MODEL_URLS key.
  for (const t of TEMPLATES) {
    assert.equal(A.MODEL_URLS['custom-template-' + t.id], '../' + t.base_mesh, t.id);
  }
});

test('created fighters fall back to the jin bank for animation (custom moveset slots still TODO)', () => {
  assert.equal(F.bankIdFor('custom', 'custom'), 'jin');
  assert.equal(F.bankIdFor('custom', 'jin'), 'jin');
});

test('MB-Lab remap is scoped: non-template models and already-renamed rigs are untouched', () => {
  const dummy = { traverse: () => {} };
  assert.equal(A.remapMblabBones('pantera', dummy), false);
  assert.equal(A.remapMblabBones('custom', dummy), false);
});

test('template fighter in a fight: remapped bones, baked morphs, retargeted jin bank moves the rig (no T-pose)', async () => {
  const gltf = await loadTemplate('technician');
  // Inject the parsed GLTF (see the Node limit note at the top:
  // loadModels/_ingest is skipped because Node cannot decode the
  // embedded PNG textures; the instance path below is identical).
  A.assets.gltfs['custom-template-technician'] = gltf;
  const inst = A.assets.createInstance('custom-template-technician', 0xc98d5e, 0xe8b64c, 0.3);
  for (const b of RIG_REQUIRED) assert.ok(inst.bones[b], `bone ${b} present after remap`);
  for (const b of ['Spine', 'Spine1', 'Spine2', 'Chest', 'Neck']) assert.ok(inst.bones[b], `bone ${b} present after remap`);
  assert.notEqual(inst.bones.Spine1, inst.bones.Spine, 'Spine1 is the real spine02, not a clobbered Spine alias');
  assert.equal(inst.bones.Spine2, inst.bones.Chest, 'Spine2 aliases the renamed Chest (spine03)');
  // The remap's signature guard: a second run on the renamed rig is a no-op.
  assert.equal(A.remapMblabBones('custom-template-technician', inst.model), false);

  // Morphs bake once at build: a slider value lands on the mesh,
  // and clearing the values returns the template shape.
  const live = applyMorphTargets(inst.model, { b_weight: 0.5 });
  assert.ok(live > 0, `b_weight 0.5 sets ${live} live influences`);
  assert.equal(applyMorphTargets(inst.model, {}), 0, 'cleared values return to the template shape');

  // The jin fallback bank retargets onto the remapped rig.
  const clips = await T.loadT3Clips(THREE, 'jin');
  assert.ok(clips && clips.stance, 'jin bank loads with a stance clip');
  const rc = T.retargetT3Clips(clips, 'jin', inst.model, THREE, 'custom-template-technician');
  assert.ok(rc && rc.stance, 'jin stance retargets onto the MB-Lab rig (analyzeRig did not return null)');
  const actions = T.createT3Actions(inst.mixer, rc, THREE);
  assert.ok(actions.stance, 'stance action exists on the fight mixer');

  // Measure motion, not just binding: rest pose vs posed frames.
  const model = inst.model;
  const wp = (b) => { model.updateMatrixWorld(true); return b.getWorldPosition(new THREE.Vector3()); };
  const rest = {
    handL: wp(inst.bones.LeftHand).clone(), handR: wp(inst.bones.RightHand).clone(),
    footL: wp(inst.bones.LeftFoot).clone(), hips: wp(inst.bones.Hips).clone(),
    head: wp(inst.bones.Head).clone(),
  };
  assert.ok(rest.head.y - rest.hips.y > 0.3, `rest head above hips (${(rest.head.y - rest.hips.y).toFixed(2)} m)`);
  assert.ok(rest.footL.y >= -0.05, `rest feet on the floor (${rest.footL.y.toFixed(3)} m)`);

  // Stance: the body must hold together (head above hips, feet on
  // the floor) through the clip — a mangled retarget pitches the
  // body flat or sinks it.
  actions.stance.setEffectiveWeight(1);
  actions.stance.play();
  for (let t = 0; t <= 1.0; t += 0.1) {
    inst.mixer.update(0.1);
    const head = wp(inst.bones.Head), hips = wp(inst.bones.Hips), foot = wp(inst.bones.LeftFoot);
    assert.ok(head.y - hips.y > 0.3, `stance t=${t.toFixed(1)}: head above hips`);
    assert.ok(foot.y >= -0.05, `stance t=${t.toFixed(1)}: foot above floor (${foot.y.toFixed(3)})`);
  }

  // Attack row: a real strike must MOVE a limb far from its rest
  // pose — this is the anti-T-pose measurement. A fighter standing
  // in its bind pose displaces nothing.
  const pool = T.bankAttackPool('jin').filter((r) => r && r.row != null);
  assert.ok(pool.length > 0, 'jin bank has attack rows');
  const rowName = 'row:' + pool[0].row;
  const rowClips = T.retargetT3Clips(clips, 'jin', model, THREE, 'custom-template-technician', [rowName]);
  assert.ok(rowClips && rowClips[rowName], `${rowName} retargets onto the rig`);
  const rowActions = T.createT3Actions(inst.mixer, rowClips, THREE);
  assert.ok(rowActions[rowName], `${rowName} action exists`);
  actions.stance.setEffectiveWeight(0);
  rowActions[rowName].setEffectiveWeight(1);
  rowActions[rowName].play();
  let maxHand = 0, maxFoot = 0;
  for (let t = 0; t <= 1.2; t += 0.05) {
    inst.mixer.update(0.05);
    maxHand = Math.max(maxHand, wp(inst.bones.LeftHand).distanceTo(rest.handL), wp(inst.bones.RightHand).distanceTo(rest.handR));
    maxFoot = Math.max(maxFoot, wp(inst.bones.LeftFoot).distanceTo(rest.footL));
  }
  const maxLimb = Math.max(maxHand, maxFoot);
  assert.ok(maxLimb > 0.05, `${rowName} moves a limb ${(maxLimb).toFixed(3)} m from rest (T-pose would be 0)`);
  console.log(`[WH-PROOF] technician + jin bank: stance holds (head above hips, feet on floor), ${rowName} moves a limb ${maxLimb.toFixed(3)} m`);
});
