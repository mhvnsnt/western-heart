/* ============================================================
   WESTERN HEART — Universal rig compatibility (creation suite)
   Rule (lane 8): every creation-suite tool must work on EVERY
   model / rig / bone / part — T7 160-bone, T3, Cape 94-bone,
   Tripo, custom. Works on one model only = NOT done.
   This module is the compatibility layer that makes that true:
     • RIG_TYPES: per-rig-type bone-name patterns (role -> names
       to look for), plus the precedent hand map (Alisa -> Cape,
       160/160 accounted) as the model for hand maps.
     • proportionScale(source, target): per-limb scale factors
       from measured bone lengths, applied on swap so a T7 clip
       does not stretch a Cape-proportioned body (or vice versa).
     • resolveRig(boneNames): identify a rig type from its bones,
       or 'custom' when nothing matches (custom still works — the
       correspondence-free path in retarget.js covers it).
   Bone lengths here are caller-measured ({ bone: length }); this
   module does the math, the intake pipeline does the measuring.
   ============================================================ */
import { SEMANTIC_ROLES } from './retarget.js';

// Bone-name patterns per rig type. PROVENANCE (owned-file rule,
// 2026-10-24 correction): t7-160 and cape-94 patterns are taken
// from the FULL FILES, not guessed and not community approximations
// — t7-160 from the WH Alisa->Cape bonemap (source: T7 Alisa_ARM,
// the Alisa rig WH actually builds Cape Jones on), cape-94 from
// the CapeJones_Rig node names in WH's own Cape stance GLB
// (95 nodes, deform chain). The bonemap proves the point: Cape
// has NO 'shoulder' bone — LeftShoulder maps to clavicle_L,
// LeftArm to upperarm_L, LeftUpLeg to thigh_L, LeftLeg to shin_L,
// LeftFoot to foot_L. Guessed 'shoulder.l / hip.l' patterns would
// have missed every one of those roles on the real rig.
// t3 and tripo patterns below are still PROVISIONAL (not yet
// verified against their full-file rigs) and are flagged as such
// in docs/research/OSS-LANE8-2026-10-24.md; 'custom' matches
// nothing and falls through to the correspondence-free path —
// it is still a supported rig.
export const RIG_TYPES = Object.freeze({
  't7-160': { bones: 160, patterns: { hips: 'Hips', spine: 'Spine', chest: 'Pectoral', neck: 'Neck', head: 'Head', shoulderL: 'LeftShoulder', elbowL: 'LeftForeArm', wristL: 'LeftHand', shoulderR: 'RightShoulder', elbowR: 'RightForeArm', wristR: 'RightHand', hipL: 'LeftUpLeg', kneeL: 'LeftLeg', ankleL: 'LeftFoot', hipR: 'RightUpLeg', kneeR: 'RightLeg', ankleR: 'RightFoot' } },
  't3': { bones: null, patterns: { hips: 'hips', spine: 'spine', chest: 'chest', neck: 'neck', head: 'head', shoulderL: 'shoulderl', elbowL: 'elbowl', wristL: 'wristl', shoulderR: 'shoulderr', elbowR: 'elbowr', wristR: 'wristr', hipL: 'hipl', kneeL: 'kneel', ankleL: 'anklel', hipR: 'hipr', kneeR: 'kneer', ankleR: 'ankler' } },
  'cape-94': { bones: 94, patterns: { hips: 'pelvis', spine: 'spine_1', chest: 'chest', neck: 'neck_1', head: 'head', shoulderL: 'clavicle_L', elbowL: 'forearm_L', wristL: 'hand_L', shoulderR: 'clavicle_R', elbowR: 'forearm_R', wristR: 'hand_R', hipL: 'thigh_L', kneeL: 'shin_L', ankleL: 'foot_L', hipR: 'thigh_R', kneeR: 'shin_R', ankleR: 'foot_R' } },
  'tripo': { bones: null, patterns: { hips: 'root', spine: 'spine', chest: 'chest', neck: 'neck', head: 'head', shoulderL: 'left_shoulder', elbowL: 'left_elbow', wristL: 'left_wrist', shoulderR: 'right_shoulder', elbowR: 'right_elbow', wristR: 'right_wrist', hipL: 'left_hip', kneeL: 'left_knee', ankleL: 'left_ankle', hipR: 'right_hip', kneeR: 'right_knee', ankleR: 'right_ankle' } },
  'custom': { bones: null, patterns: {} },
});

// Precedent hand map (Alisa -> Cape, 160/160 accounted, 2026-10-24):
// a hand map is a role -> { source, target } pair list. Kept as the
// documented shape other hand maps must follow; the live map lives
// in the rig-intake pipeline, not hard-coded here.
export const HAND_MAP_SHAPE = Object.freeze(['role', 'sourceBone', 'targetBone']);

export function resolveRig(boneNames) {
  // Normalized on BOTH sides (same norm as mapRigBones): the
  // Alisa-derived t7-160 patterns are capitalized ('LeftShoulder')
  // and scored zero before this fix, misidentifying Alisa as t3.
  const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  const names = (boneNames || []).map(norm);
  let best = 'custom', bestScore = 0;
  for (const [type, def] of Object.entries(RIG_TYPES)) {
    if (type === 'custom') continue;
    const pats = Object.values(def.patterns).map(norm);
    const score = pats.filter((p) => names.some((n) => n.includes(p))).length;
    if (score > bestScore) { bestScore = score; best = type; }
  }
  return bestScore >= 4 ? best : 'custom';
}

// Per-limb proportion scales: target length / source length, per
// role, from caller-measured bone lengths. Missing pairs -> 1
// (no scale, never NaN). All outputs finite and positive.
export function proportionScale(sourceLengths, targetLengths) {
  const out = {};
  for (const role of SEMANTIC_ROLES) {
    const s = sourceLengths[role], t = targetLengths[role];
    out[role] = (typeof s === 'number' && s > 0 && typeof t === 'number' && t > 0) ? t / s : 1;
  }
  return out;
}

// Map every semantic role present in a rig's bone list to a bone
// name, using that rig type's patterns first, then the generic
// correspondence-free match (retarget.js logic, inlined here to
// keep this module dependency-light for the creation suite).
export function mapRigBones(rigType, boneNames) {
  const norm = (s) => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  const def = RIG_TYPES[rigType] || RIG_TYPES.custom;
  const out = {};
  for (const role of SEMANTIC_ROLES) {
    const pat = norm(def.patterns[role] || '');
    const hit = pat && (boneNames || []).find((n) => norm(n).includes(pat));
    if (hit) out[role] = hit;
    else {
      const generic = (boneNames || []).find((n) => norm(n).includes(norm(role)));
      if (generic) out[role] = generic;
    }
  }
  return out;
}
