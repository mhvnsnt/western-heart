/* rig-adapter.js — UNIVERSAL RIG COMPATIBILITY for the Creation Suite.
   Owner directive 2026-10-24 19:54 CDT: MPFB/MB-Lab, Google GNM, Build-A-Bod,
   GameRig/NaughTyRig, Fluid Painter, Tripo, gltfpack tooling must work on
   EVERY model, EVERY rig, EVERY bone, EVERY part — not one test model.

   This module is the rig-agnostic layer that makes that possible:
   - CANONICAL_BONES: one stable name per body bone (hips -> toes, fingers
     included). Every tool in the suite addresses bones by canonical name.
   - BONE_ALIASES: the real bone-name conventions of every rig family in the
     game, normalized the same way, so one lookup resolves any of them:
       * T7 (Alisa port, 160 joints): Hips, Spine, Spine1, Spine2, Neck, Head,
         LeftShoulder (= clavicle), LeftArm, LeftForeArm, LeftHand,
         LeftHandThumb1/Index1/Middle1/Ring1/Pinky1, LeftUpLeg, LeftLeg,
         LeftFoot, LeftToeBase — verified against the Alisa->Cape bonemap
         (workspace/ep1-farm/bonemap_alisa_to_capejones.json, 160/160).
       * Cape 94-bone rig: pelvis, spine_1..4, chest, neck_1/2, head,
         clavicle_L, upperarm_L, forearm_L, hand_L, finger_thumb/index/
         middle/ring/pinky_1_L, thigh_L, shin_L, foot_L, toe_L — same bonemap.
       * Mixamo: mixamorig: prefix + T7-style names (the viewer already
         strips that prefix; the resolver does too).
       * Rigify (Blender, MPFB auto-rig output): hips, spine, chest,
         shoulder.L, upper_arm.L, forearm.L, hand.L, thumb.01.L,
         f_index.01.L, f_middle.01.L, f_ring.01.L, f_pinky.01.L, thigh.L,
         shin.L, foot.L, toe.L — Blender Rigify convention.
       * MB-Lab / MPFB / MakeHuman family: pelvis, spine01/02/03, neck,
         head, clavicle_L, upperarm_L, forearm_L, hand_L, thigh_L, shin_L,
         foot_L — MakeHuman skeleton convention. FINGER names for this family
         are NOT confirmed from a baked mesh yet (template GLBs are 9MB and
         their joint lists were not readable from this VM) — the resolver
         REPORTS them missing for MB-Lab-style rigs instead of guessing.
         That is a documented gap, not a silent skip (see RIG-COMPAT doc).
   - Normalization: lowercase, strip mixamorig:/mixamorig prefix, drop
     spaces/dots/dashes, KEEP underscores. Underscores are load-bearing:
     Cape spine_1 (lowest spine) must NOT collide with T7 Spine1 (mid spine).
   - No guessing: a canonical bone with no alias match is reported in
     `missing[]` with its coverage fraction. Callers degrade visibly
     (socket fallback, record-only) — never silently bind the wrong bone.
   - DOM-free: works on plain bone-name arrays (Node tests) and on
     three.js Object3D trees (suite viewer) via the same resolver.
   - Proportion adaptation: parts/morphs authored for one body must fit
     another. adaptScale() gives the height-normalized factor (same 1.7m
     reference the viewer already uses for socket offsets); cross-model
     part swaps multiply by it instead of copying raw scale. */

export const CANONICAL_BONES = [
  'hips', 'spine', 'spine1', 'spine2', 'neck', 'head',
  'clavicleL', 'clavicleR',
  'upperArmL', 'upperArmR', 'forearmL', 'forearmR', 'handL', 'handR',
  'thumbL', 'thumbR', 'indexL', 'indexR', 'middleL', 'middleR',
  'ringL', 'ringR', 'pinkyL', 'pinkyR',
  'thighL', 'thighR', 'shinL', 'shinR', 'footL', 'footR', 'toeL', 'toeR',
];

/* canonical -> normalized alias forms (see header for sources).
   Normalized form = normalizeBoneName() output. */
export const BONE_ALIASES = {
  hips: ['hips', 'pelvis'],
  spine: ['spine', 'spine_1', 'spine01', 'spine00'],
  spine1: ['spine1', 'spine_2', 'spine02', 'spine001'],
  spine2: ['spine2', 'spine_3', 'spine03', 'spine_4', 'spine4', 'spine002', 'chest'],
  neck: ['neck', 'neck_1', 'neck01'],
  head: ['head'],
  clavicleL: ['leftshoulder', 'clavicle_l', 'shoulder_l', 'shoulderl'],
  clavicleR: ['rightshoulder', 'clavicle_r', 'shoulder_r', 'shoulderr'],
  upperArmL: ['leftarm', 'upperarm_l', 'upper_arml', 'upperarml'],
  upperArmR: ['rightarm', 'upperarm_r', 'upper_armr', 'upperarmr'],
  forearmL: ['leftforearm', 'forearm_l', 'forearml'],
  forearmR: ['rightforearm', 'forearm_r', 'forearmr'],
  handL: ['lefthand', 'hand_l', 'handl'],
  handR: ['righthand', 'hand_r', 'handr'],
  thumbL: ['lefthandthumb1', 'finger_thumb_1_l', 'thumb01l', 'thumb1_l'],
  thumbR: ['righthandthumb1', 'finger_thumb_1_r', 'thumb01r', 'thumb1_r'],
  indexL: ['lefthandindex1', 'finger_index_1_l', 'findex01l', 'f_index01l', 'index1_l'],
  indexR: ['righthandindex1', 'finger_index_1_r', 'findex01r', 'f_index01r', 'index1_r'],
  middleL: ['lefthandmiddle1', 'finger_middle_1_l', 'fmiddle01l', 'f_middle01l', 'middle1_l'],
  middleR: ['righthandmiddle1', 'finger_middle_1_r', 'fmiddle01r', 'f_middle01r', 'middle1_r'],
  ringL: ['lefthandring1', 'finger_ring_1_l', 'fring01l', 'f_ring01l', 'ring1_l'],
  ringR: ['righthandring1', 'finger_ring_1_r', 'fring01r', 'f_ring01r', 'ring1_r'],
  pinkyL: ['lefthandpinky1', 'finger_pinky_1_l', 'fpinky01l', 'f_pinky01l', 'pinky1_l'],
  pinkyR: ['righthandpinky1', 'finger_pinky_1_r', 'fpinky01r', 'f_pinky01r', 'pinky1_r'],
  thighL: ['leftupleg', 'thigh_l', 'thighl'],
  thighR: ['rightupleg', 'thigh_r', 'thighr'],
  shinL: ['leftleg', 'shin_l', 'shinl'],
  shinR: ['rightleg', 'shin_r', 'shinr'],
  footL: ['leftfoot', 'foot_l', 'footl'],
  footR: ['rightfoot', 'foot_r', 'footr'],
  toeL: ['lefttoebase', 'toe_l', 'toel'],
  toeR: ['righttoebase', 'toe_r', 'toer'],
};

/* Suite sockets -> canonical bones to try, in order. */
export const SOCKET_CANONICAL = {
  head: ['head'],
  face: ['head'],
  hands: ['handR'],
  chest: ['spine2', 'spine1'],
  waist: ['hips'],
};

export function normalizeBoneName(name) {
  if (!name) return '';
  return String(name)
    .replace(/^mixamorig:?/i, '')
    .toLowerCase()
    .replace(/[\s.\-]+/g, '');
}

/* Resolve canonical bones against a flat list of bone names.
   Returns { map: {canonical: actualName}, missing: [canonical],
             found, total, coverage } — coverage is a fraction 0..1. */
export function resolveBonesFromNames(names) {
  const byNorm = new Map();
  for (const n of names || []) {
    const norm = normalizeBoneName(n);
    if (norm && !byNorm.has(norm)) byNorm.set(norm, n);
  }
  const map = {};
  const missing = [];
  for (const c of CANONICAL_BONES) {
    let hit = null;
    for (const alias of BONE_ALIASES[c] || []) {
      if (byNorm.has(alias)) { hit = byNorm.get(alias); break; }
    }
    if (hit) map[c] = hit; else missing.push(c);
  }
  const found = CANONICAL_BONES.length - missing.length;
  return { map, missing, found, total: CANONICAL_BONES.length,
           coverage: found / CANONICAL_BONES.length };
}

/* Resolve against a three.js Object3D (or any {name, children} tree).
   Returns the rig profile (boneCount, namingStyles, coverage) plus bone
   objects in `bones`. Plain {name, isBone, children} trees work too, so
   Node tests can exercise it without three.js. */
export function resolveBonesFromObject3D(root) {
  const bones = {};
  const names = [];
  const walk = (o) => {
    if (!o) return;
    if (o.isBone) { bones[o.name] = o; names.push(o.name); }
    for (const c of (o.children || [])) walk(c);
  };
  walk(root);
  const rep = rigProfile(names);
  const boneObjs = {};
  for (const [c, actual] of Object.entries(rep.map)) boneObjs[c] = bones[actual];
  return { ...rep, bones: boneObjs };
}

/* Plain-data rig profile for display (TOOLS tab) + test reporting. */
export function rigProfile(names) {
  const rep = resolveBonesFromNames(names);
  const styles = [];
  const joined = (names || []).join(' ');
  if (/mixamorig/i.test(joined)) styles.push('mixamo');
  if (/\bpelvis\b/.test(joined) && /spine_\d/.test(joined)) styles.push('cape/mb-lab-snake');
  if (/LeftArm|LeftUpLeg/.test(joined)) styles.push('t7');
  if (/\.L\b/.test(joined) || /upper_arm\.L/.test(joined)) styles.push('rigify');
  return { boneCount: (names || []).length,
           namingStyles: styles.length ? styles : ['unknown'],
           ...rep };
}

/* Proportion adaptation: height-normalized scale factor between two models.
   Reference height 1.7m is the viewer's existing socket-offset reference, so
   a part authored at 1.7m keeps scale 1.0 and a part moving from a tall model
   to a short one shrinks instead of floating oversized. Clamped to a sane
   band so a broken head-height reading can never scale a part to absurdity. */
export function adaptScale(sourceHeadHeight, targetHeadHeight) {
  const s = Number(sourceHeadHeight) || 1.7;
  const t = Number(targetHeadHeight) || 1.7;
  return Math.min(1.4, Math.max(0.7, t / s));
}

export function adaptPartScale(baseScale, sourceHeadHeight, targetHeadHeight) {
  return (Number(baseScale) || 1) * adaptScale(sourceHeadHeight, targetHeadHeight);
}
