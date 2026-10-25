/* creation-suite-rig-adapter.test.mjs — Node test for the Creation Suite's
   UNIVERSAL COMPATIBILITY layer (owner directive 2026-10-24 19:54 CDT: tools
   must work on EVERY model, EVERY rig, EVERY bone, EVERY part).
   Run: node test/creation-suite-rig-adapter.test.mjs (no dependencies).
   Fixtures:
   - ALISA_BONES: the real 160-joint T7 Alisa bone list, keys of
     workspace/ep1-farm/bonemap_alisa_to_capejones.json (160/160 map).
   - CAPE_BONES: the real 54 unique Cape deform bones, values of the same map.
   - MIXAMO_BONES / RIGIFY_BONES / MPFB_BONES: convention examples (labeled
     as such, NOT claimed as extracted data) for the other rig families.
   - TEMPLATES: the real 9 body-templates.json entries (id, body_type,
     proportions, skin_tone, head_shape, base_mesh), mirrored 2026-10-24.
     The suite loads the live JSON at runtime; this test pins the mapping
     logic against the same values. */
import assert from 'node:assert';
import { resolveBonesFromNames, resolveBonesFromObject3D, normalizeBoneName, adaptScale,
         CANONICAL_BONES } from '../packages/creation-suite/src/rig-adapter.js';
import { bodyTypeToDNA, propsToDNA, mergeDNA, DEFAULT_PROPS,
         LEGACY_HW } from '../packages/creation-suite/src/template-map.js';

const ALISA_BONES = ["Hips", "ValveBiped.Bip01_Pelvis", "Spine", "Spine1", "Spine2", "ValveBiped.Bip01_Spine4", "Neck", "Head", "head jaw", "lPectoral_Root", "lPectoral", "rPectoral_Root", "rPectoral", "Butt_Root.L", "Butt.L", "Butt_Root.R", "Butt.R", "LeftUpLeg", "ValveBiped.Bip01_L_Thigh_Helper", "LeftLeg", "ValveBiped.Bip01_L_Calf_Helper", "LeftFoot", "ValveBiped.Bip01_L_Foot_Helper", "ValveBiped.Bip01_L_Heel", "LeftToeBase", "ValveBiped.Bip01_L_Toe1", "ValveBiped.Bip01_L_Toe11", "ValveBiped.Bip01_L_Toe2", "ValveBiped.Bip01_L_Toe21", "ValveBiped.Bip01_L_Toe3", "ValveBiped.Bip01_L_Toe31", "ValveBiped.Bip01_L_Toe4", "ValveBiped.Bip01_L_Toe41", "ValveBiped.Bip01_L_Toe5", "ValveBiped.Bip01_L_Toe51", "LeftShoulder", "ValveBiped.Bip01_L_Clavicle_Helper", "LeftArm", "ValveBiped.Bip01_L_UpperArm_Helper", "UpperArm_Twist.L", "LeftForeArm", "ValveBiped.Bip01_L_Forearm_Helper", "ForeArm_Twist.L", "LeftHand", "ValveBiped.Bip01_L_Hand_Helper", "LeftHandThumb1", "LeftHandThumb2", "LeftHandThumb3", "LeftHandIndex1", "LeftHandIndex2", "LeftHandIndex3", "Hand_Carpal01.L", "LeftHandMiddle1", "LeftHandMiddle2", "LeftHandMiddle3", "Hand_Carpal02.L", "LeftHandRing1", "LeftHandRing2", "LeftHandRing3", "Hand_Carpal03.L", "LeftHandPinky1", "LeftHandPinky2", "LeftHandPinky3", "Hand_Carpal04.L", "RightUpLeg", "ValveBiped.Bip01_R_Thigh_Helper", "RightLeg", "ValveBiped.Bip01_R_Calf_Helper", "RightFoot", "ValveBiped.Bip01_R_Foot_Helper", "ValveBiped.Bip01_R_Heel", "RightToeBase", "ValveBiped.Bip01_R_Toe1", "ValveBiped.Bip01_R_Toe11", "ValveBiped.Bip01_R_Toe2", "ValveBiped.Bip01_R_Toe21", "ValveBiped.Bip01_R_Toe3", "ValveBiped.Bip01_R_Toe31", "ValveBiped.Bip01_R_Toe4", "ValveBiped.Bip01_R_Toe41", "ValveBiped.Bip01_R_Toe5", "ValveBiped.Bip01_R_Toe51", "RightShoulder", "ValveBiped.Bip01_R_Clavicle_Helper", "RightArm", "ValveBiped.Bip01_R_UpperArm_Helper", "UpperArm_Twist.R", "RightForeArm", "ValveBiped.Bip01_R_Forearm_Helper", "ForeArm_Twist.R", "RightHand", "ValveBiped.Bip01_R_Hand_Helper", "RightHandThumb1", "RightHandThumb2", "RightHandThumb3", "RightHandIndex1", "RightHandIndex2", "RightHandIndex3", "Hand_Carpal01.R", "RightHandMiddle1", "RightHandMiddle2", "RightHandMiddle3", "Hand_Carpal02.R", "RightHandRing1", "RightHandRing2", "RightHandRing3", "Hand_Carpal03.R", "RightHandPinky1", "RightHandPinky2", "RightHandPinky3", "Hand_Carpal04.R", "ctr bero1 joint pos", "hair back left 1", "hair back middle 1", "hair back right 1", "hair front left a 1", "hair front left a 2", "hair front left a 3", "hair front left b 1", "hair front left b 2", "hair front left b 3", "hair front right a 1", "hair front right b 1", "hair root back left", "hair root back middle", "hair root back right", "hair root front left a", "hair root front left b", "hair root front right a", "hair root front right b", "head cheek left 1", "head cheek left 2", "head cheek right 1", "head cheek right 2", "head eyeball left", "head eyeball right", "head eyebrow left 1", "head eyebrow left 2", "head eyebrow left 3", "head eyebrow right 1", "head eyebrow right 2", "head eyebrow right 3", "head eyelid left lower", "head eyelid left upper", "head eyelid right lower", "head eyelid right upper", "head lip corner left", "head lip corner right", "head lip lower left", "head lip lower middle", "head lip lower right", "head lip upper left", "head lip upper middle", "head lip upper right", "head nose left 1", "head nose left 2", "head nose right 1", "head nose right 2", "head tongue 1", "head tongue 2"];
const CAPE_BONES = ["pelvis", "spine_1", "spine_2", "spine_3", "spine_4", "chest", "neck_1", "neck_2", "head", "jaw", "thigh_L", "shin_L", "foot_L", "toe_L", "clavicle_L", "upperarm_L", "forearm_L", "hand_L", "finger_thumb_1_L", "finger_thumb_2_L", "finger_index_1_L", "finger_index_2_L", "finger_index_3_L", "finger_middle_1_L", "finger_middle_2_L", "finger_middle_3_L", "finger_ring_1_L", "finger_ring_2_L", "finger_ring_3_L", "finger_pinky_1_L", "finger_pinky_2_L", "finger_pinky_3_L", "thigh_R", "shin_R", "foot_R", "toe_R", "clavicle_R", "upperarm_R", "forearm_R", "hand_R", "finger_thumb_1_R", "finger_thumb_2_R", "finger_index_1_R", "finger_index_2_R", "finger_index_3_R", "finger_middle_1_R", "finger_middle_2_R", "finger_middle_3_R", "finger_ring_1_R", "finger_ring_2_R", "finger_ring_3_R", "finger_pinky_1_R", "finger_pinky_2_R", "finger_pinky_3_R"];

const MIXAMO_BONES = ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine1',
  'mixamorig:Spine2', 'mixamorig:Neck', 'mixamorig:Head', 'mixamorig:LeftShoulder',
  'mixamorig:RightShoulder', 'mixamorig:LeftArm', 'mixamorig:RightArm',
  'mixamorig:LeftForeArm', 'mixamorig:RightForeArm', 'mixamorig:LeftHand',
  'mixamorig:RightHand', 'mixamorig:LeftHandThumb1', 'mixamorig:RightHandThumb1',
  'mixamorig:LeftHandIndex1', 'mixamorig:RightHandIndex1', 'mixamorig:LeftHandMiddle1',
  'mixamorig:RightHandMiddle1', 'mixamorig:LeftHandRing1', 'mixamorig:RightHandRing1',
  'mixamorig:LeftHandPinky1', 'mixamorig:RightHandPinky1', 'mixamorig:LeftUpLeg',
  'mixamorig:RightUpLeg', 'mixamorig:LeftLeg', 'mixamorig:RightLeg',
  'mixamorig:LeftFoot', 'mixamorig:RightFoot', 'mixamorig:LeftToeBase',
  'mixamorig:RightToeBase'];
const RIGIFY_BONES = ['hips', 'spine', 'spine.001', 'chest', 'neck', 'head', 'shoulder.L',
  'shoulder.R', 'upper_arm.L', 'upper_arm.R', 'forearm.L', 'forearm.R',
  'hand.L', 'hand.R', 'thumb.01.L', 'thumb.01.R', 'f_index.01.L', 'f_index.01.R',
  'f_middle.01.L', 'f_middle.01.R', 'f_ring.01.L', 'f_ring.01.R', 'f_pinky.01.L',
  'f_pinky.01.R', 'thigh.L', 'thigh.R', 'shin.L', 'shin.R', 'foot.L', 'foot.R',
  'toe.L', 'toe.R'];
const MPFB_BONES = ['pelvis', 'spine01', 'spine02', 'spine03', 'neck', 'head',
  'clavicle_L', 'clavicle_R', 'upperarm_L', 'upperarm_R', 'forearm_L',
  'forearm_R', 'hand_L', 'hand_R', 'thigh_L', 'thigh_R', 'shin_L', 'shin_R',
  'foot_L', 'foot_R'];

const TEMPLATES = [
  { id: 'super-heavyweight', body_type: 'Rikishi', proportions: { height: 1.02, muscle: 1.05, weight: 1.42 }, skin_tone: '#8a5240', head_shape: 'male_5', base_mesh: 'customization/templates/meshes/super-heavyweight.glb' },
  { id: 'powerhouse', body_type: 'Austin', proportions: { height: 1.0, muscle: 1.15, weight: 1.12 }, skin_tone: '#c98d5e', head_shape: 'male_1', base_mesh: 'customization/templates/meshes/powerhouse.glb' },
  { id: 'showman', body_type: 'Rock', proportions: { height: 1.01, muscle: 1.22, weight: 1.16 }, skin_tone: '#a06a42', head_shape: 'male_3', base_mesh: 'customization/templates/meshes/showman.glb' },
  { id: 'technician', body_type: 'Medium 1', proportions: { height: 1.0, muscle: 1.0, weight: 1.0 }, skin_tone: '#e8a87c', head_shape: 'male_3', base_mesh: 'customization/templates/meshes/technician.glb' },
  { id: 'highflyer', body_type: 'HBK', proportions: { height: 0.99, muscle: 1.1, weight: 1.02 }, skin_tone: '#f7c2a1', head_shape: 'male_2', base_mesh: 'customization/templates/meshes/highflyer.glb' },
  { id: 'luchador', body_type: 'Skinny 1', proportions: { height: 1.02, muscle: 0.85, weight: 0.86 }, skin_tone: '#d89671', head_shape: 'male_4', base_mesh: 'customization/templates/meshes/luchador.glb' },
  { id: 'powerhouse-w', body_type: 'Chyna', proportions: { height: 1.03, muscle: 1.2, weight: 1.25 }, skin_tone: '#c98d5e', head_shape: 'female_1', base_mesh: 'customization/templates/meshes/powerhouse-w.glb' },
  { id: 'athletic-w', body_type: 'Fit 2', proportions: { height: 1.0, muscle: 1.08, weight: 1.02 }, skin_tone: '#e8a87c', head_shape: 'female_2', base_mesh: 'customization/templates/meshes/athletic-w.glb' },
  { id: 'striker-w', body_type: 'Petit 1', proportions: { height: 0.96, muscle: 0.95, weight: 0.88 }, skin_tone: '#f7c2a1', head_shape: 'female_3', base_mesh: 'customization/templates/meshes/striker-w.glb' },
];

let pass = 0;
const check = (name, fn) => { fn(); pass++; console.log('ok - ' + name); };

// --- normalization: underscores are load-bearing (Cape spine_1 != T7 Spine1)
check('normalize keeps underscores apart', () => {
  assert.notStrictEqual(normalizeBoneName('spine_1'), normalizeBoneName('Spine1'));
  assert.strictEqual(normalizeBoneName('mixamorig:LeftHand'), 'lefthand');
  assert.strictEqual(normalizeBoneName('upper_arm.L'), 'upper_arml');
});

// --- real rigs: every canonical bone resolves on Alisa AND Cape
check('T7 Alisa rig resolves all canonical bones', () => {
  const r = resolveBonesFromNames(ALISA_BONES);
  assert.strictEqual(r.missing.length, 0, 'missing: ' + r.missing.join(','));
  assert.strictEqual(r.map.head, 'Head');
  assert.strictEqual(r.map.upperArmL, 'LeftArm');
  assert.strictEqual(r.map.thighL, 'LeftUpLeg');
  assert.strictEqual(r.map.thumbL, 'LeftHandThumb1');
  assert.strictEqual(r.coverage, 1);
});
check('Cape rig resolves all canonical bones', () => {
  const r = resolveBonesFromNames(CAPE_BONES);
  assert.strictEqual(r.missing.length, 0, 'missing: ' + r.missing.join(','));
  assert.strictEqual(r.map.hips, 'pelvis');
  assert.strictEqual(r.map.spine, 'spine_1');
  assert.strictEqual(r.map.spine1, 'spine_2');
  assert.strictEqual(r.map.spine2, 'spine_3');
  assert.strictEqual(r.map.clavicleL, 'clavicle_L');
  assert.strictEqual(r.map.upperArmL, 'upperarm_L');
  assert.strictEqual(r.map.thumbL, 'finger_thumb_1_L');
  assert.strictEqual(r.coverage, 1);
});
check('Mixamo rig resolves all canonical bones', () => {
  const r = resolveBonesFromNames(MIXAMO_BONES);
  assert.strictEqual(r.missing.length, 0, 'missing: ' + r.missing.join(','));
});
check('Rigify rig resolves all canonical bones', () => {
  const r = resolveBonesFromNames(RIGIFY_BONES);
  assert.strictEqual(r.missing.length, 0, 'missing: ' + r.missing.join(','));
  assert.strictEqual(r.map.spine2, 'chest');
  assert.strictEqual(r.map.clavicleL, 'shoulder.L');
});

// --- MPFB: core resolves, fingers honestly reported missing (unconfirmed names)
check('MPFB rig resolves core bones, reports fingers missing (not guessed)', () => {
  const r = resolveBonesFromNames(MPFB_BONES);
  for (const c of ['hips', 'spine', 'spine1', 'spine2', 'neck', 'head', 'clavicleL',
    'upperArmL', 'forearmL', 'handL', 'thighL', 'shinL', 'footL']) {
    assert.ok(r.map[c], 'expected core bone ' + c + ' to resolve');
  }
  assert.ok(r.missing.includes('thumbL'), 'thumbL must be reported missing, not guessed');
  assert.ok(r.coverage < 1 && r.coverage > 0.6, 'coverage ' + r.coverage);
});

// --- empty/unknown rigs report honestly, never crash
check('empty rig reports everything missing', () => {
  const r = resolveBonesFromNames([]);
  assert.strictEqual(r.missing.length, CANONICAL_BONES.length);
  assert.strictEqual(r.coverage, 0);
});

// --- Object3D resolution (plain {name, isBone, children} tree, no three.js)
check('resolveBonesFromObject3D works on plain trees (Cape-style)', () => {
  // (bone, parent) pairs — same skeleton as the Cape rig, built flat.
  const pairs = [
    ['pelvis', null], ['spine_1', 'pelvis'], ['spine_2', 'spine_1'],
    ['spine_3', 'spine_2'], ['chest', 'spine_3'],
    ['neck_1', 'chest'], ['neck_2', 'neck_1'], ['head', 'neck_2'],
    ['clavicle_L', 'chest'], ['upperarm_L', 'clavicle_L'],
    ['forearm_L', 'upperarm_L'], ['hand_L', 'forearm_L'],
    ['finger_thumb_1_L', 'hand_L'], ['finger_index_1_L', 'hand_L'],
    ['finger_middle_1_L', 'hand_L'], ['finger_ring_1_L', 'hand_L'],
    ['finger_pinky_1_L', 'hand_L'],
    ['clavicle_R', 'chest'], ['upperarm_R', 'clavicle_R'],
    ['forearm_R', 'upperarm_R'], ['hand_R', 'forearm_R'],
    ['finger_thumb_1_R', 'hand_R'], ['finger_index_1_R', 'hand_R'],
    ['finger_middle_1_R', 'hand_R'], ['finger_ring_1_R', 'hand_R'],
    ['finger_pinky_1_R', 'hand_R'],
    ['thigh_L', 'pelvis'], ['shin_L', 'thigh_L'], ['foot_L', 'shin_L'],
    ['toe_L', 'foot_L'],
    ['thigh_R', 'pelvis'], ['shin_R', 'thigh_R'], ['foot_R', 'shin_R'],
    ['toe_R', 'foot_R'],
  ];
  const nodes = {};
  for (const [n] of pairs) nodes[n] = { name: n, isBone: true, children: [] };
  let root = null;
  for (const [n, p] of pairs) {
    if (p) nodes[p].children.push(nodes[n]); else root = nodes[n];
  }
  const scene = { name: 'Scene', children: [root] };
  const r = resolveBonesFromObject3D(scene);
  assert.strictEqual(r.missing.length, 0, 'missing: ' + r.missing.join(','));
  assert.strictEqual(r.bones.spine.name, 'spine_1');
  assert.strictEqual(r.bones.upperArmL.name, 'upperarm_L');
  assert.strictEqual(r.boneCount, pairs.length, 'tree holds ' + pairs.length + ' bones, got ' + r.boneCount);
});

// --- proportion adaptation
check('adaptScale is height-normalized and clamped', () => {
  assert.strictEqual(adaptScale(1.7, 1.7), 1);
  assert.ok(Math.abs(adaptScale(2.0, 1.0) - 0.7) < 1e-9, 'clamped low');
  assert.ok(Math.abs(adaptScale(1.0, 2.0) - 1.4) < 1e-9, 'clamped high');
  assert.ok(Math.abs(adaptScale(1.9, 1.7) - 1.7 / 1.9) < 1e-9);
});

// --- template mapping: real data, honest basis labels
check('dedicated template: Medium 1 -> technician, basis dedicated', () => {
  const r = bodyTypeToDNA('Medium 1', TEMPLATES);
  assert.strictEqual(r.templateId, 'technician');
  assert.strictEqual(r.basis, 'dedicated');
  assert.deepStrictEqual(r.proportions, { ...DEFAULT_PROPS, height: 1.0, muscle: 1.0, weight: 1.0 });
});
check('dedicated template: Rikishi -> super-heavyweight', () => {
  const r = bodyTypeToDNA('Rikishi', TEMPLATES);
  assert.strictEqual(r.templateId, 'super-heavyweight');
  assert.strictEqual(r.proportions.weight, 1.42);
});
check('male type without template: Thick 1 -> legacy h/w + powerhouse muscle', () => {
  const r = bodyTypeToDNA('Thick 1', TEMPLATES);
  assert.strictEqual(r.basis, 'legacy+family');
  assert.strictEqual(r.templateId, 'powerhouse');
  assert.strictEqual(r.proportions.height, LEGACY_HW['Thick 1'].h);
  assert.strictEqual(r.proportions.weight, LEGACY_HW['Thick 1'].w);
  assert.strictEqual(r.proportions.muscle, 1.15);
});
check('female type without template: Curvy F -> powerhouse-w family', () => {
  const r = bodyTypeToDNA('Curvy F', TEMPLATES);
  assert.strictEqual(r.basis, 'family');
  assert.strictEqual(r.templateId, 'powerhouse-w');
  assert.strictEqual(r.proportions.muscle, 1.2);
});
check('unknown type -> default, never crashes', () => {
  const r = bodyTypeToDNA('Nope', TEMPLATES);
  assert.strictEqual(r.basis, 'default');
  assert.strictEqual(r.templateId, null);
});

// --- props -> DNA: deltas (0 = as authored), height/weight excluded, clamped
check('propsToDNA converts multipliers to deltas, excludes height/weight', () => {
  const d = propsToDNA({ height: 1.1, weight: 1.2, muscle: 1.15, shoulder: 0.9,
    chest: 1.3, waist: 1.0, hips: 1.0, arms: 1.0, legs: 1.3 });
  assert.strictEqual(d.height, undefined);
  assert.strictEqual(d.weight, undefined);
  assert.ok(Math.abs(d.muscle - 0.15) < 1e-9);
  assert.ok(Math.abs(d.shoulders - (-0.1)) < 1e-9);
  assert.ok(Math.abs(d.chest - 0.3) < 1e-9);
  assert.ok(Math.abs(d.legLen - 0.2) < 1e-9, 'legLen clamps to DNA range 0.2, got ' + d.legLen);
});
check('mergeDNA adds deltas and clamps', () => {
  const m = mergeDNA({ muscle: 0.15 }, { muscle: 0.2, chest: 0.1 });
  assert.ok(Math.abs(m.muscle - 0.35) < 1e-9);
  assert.ok(Math.abs(m.chest - 0.1) < 1e-9);
  const c = mergeDNA({ muscle: 0.9 }, { muscle: 0.5 });
  assert.strictEqual(c.muscle, 1.0, 'muscle clamps to DNA max 1.0');
});

console.log(`\n${pass} checks passed.`);
