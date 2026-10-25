/* ============================================================
   WESTERN HEART — hit-bones.js (lane C, 2026-10-24)
   Canonical bone aliases for the hit/hurt shapes and the procedural layer.
   assets.js createInstance builds the bones dict from raw node names; a rig
   that spells them differently (WH-Canonical-22 has Chest but no Spine1 /
   Spine2, Bruno has no Head, the T7-extraction rigs say arm_right_elbow,
   Rigify says DEF-forearm.L) left fighter.js reading undefined bones, and the
   hurt shapes fell back to root-anchored guesses. This adds the canonical
   names as dict ALIASES (never overriding a name already there; node names,
   mixer binding and skinning untouched), using the same map the T3 retarget
   binds by (t3anims.js canonBoneName) plus the rig families it lacks.
   Pure (no THREE): node tests + tools/hit-contact/bone_audit.mjs use it.
   ============================================================ */
import { canonBoneName } from './t3anims.js';

const T7X = { shoulder_1: 'Shoulder', shoulder_2: 'Arm', elbow: 'ForeArm', wrist: 'Hand',
  thigh: 'UpLeg', knee: 'Leg', ankle: 'Foot', toes: 'ToeBase' };
const RIGIFY = { shoulder: 'Shoulder', upper_arm: 'Arm', forearm: 'ForeArm', hand: 'Hand',
  thigh: 'UpLeg', shin: 'Leg', foot: 'Foot', toe: 'ToeBase' };
const RIGIFY_SPINE = { spine: 'Hips', spine001: 'Spine', spine002: 'Spine1', spine003: 'Spine2',
  spine004: 'Neck', spine005: 'Neck', spine006: 'Head' };
const UE = { clavicle: 'Shoulder', upperarm: 'Arm', lowerarm: 'ForeArm', hand: 'Hand',
  thigh: 'UpLeg', calf: 'Leg', foot: 'Foot', ball: 'ToeBase' };
const PLAIN = { root_hips: 'Hips', pelvis: 'Hips', spine_lower: 'Spine', spine_upper: 'Spine2',
  head: 'Head', head_neck_lower: 'Neck', spine_01: 'Spine', spine_02: 'Spine1', spine_03: 'Spine2',
  neck_01: 'Neck', Chest: 'Chest' };

/* Canonical name of a (GLTFLoader-sanitized) bone name, or null. */
export function hitBoneName(name) {
  const c = canonBoneName(name);
  if (c) return c;
  const n = String(name).replace(/^mixamorig[:_]?/i, '');
  if (PLAIN[n]) return PLAIN[n];
  let m = n.match(/^(arm|leg)_(left|right)_(shoulder_[12]|elbow|wrist|thigh|knee|ankle|toes)$/);
  if (m) return (m[2] === 'left' ? 'Left' : 'Right') + T7X[m[3]];
  m = n.match(/^DEF-(shoulder|upper_arm|forearm|hand|thigh|shin|foot|toe)\.?([LR])$/);
  if (m) return (m[2] === 'L' ? 'Left' : 'Right') + RIGIFY[m[1]];
  m = n.match(/^DEF-(spine(?:00[1-6])?)$/);
  if (m) return RIGIFY_SPINE[m[1]];
  m = n.match(/^(clavicle|upperarm|lowerarm|hand|thigh|calf|foot|ball)_([lr])$/);
  if (m) return (m[2] === 'l' ? 'Left' : 'Right') + UE[m[1]];
  return null;
}

export const HIT_BONES_REQUIRED = ['Hips', 'Spine1', 'Head', 'LeftArm', 'LeftForeArm', 'LeftHand',
  'RightArm', 'RightForeArm', 'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot'];

/* Add canonical aliases to a { name: bone } dict; `list` = [[rawName, bone], ...] in traversal
   order. Never overrides an existing name. Returns the names added. */
export function addCanonicalAliases(dict, list) {
  const added = [];
  for (const [raw, bone] of list) {
    const c = hitBoneName(raw);
    if (c && !dict[c]) { dict[c] = bone; added.push(c); }
  }
  const fb = (k, ...alts) => {
    if (dict[k]) return;
    const a = alts.find(x => dict[x]);
    if (a) { dict[k] = dict[a]; added.push(k + '<-' + a); }
  };
  fb('Spine2', 'Chest', 'Spine1', 'Spine');
  fb('Spine1', 'Spine', 'Spine2', 'Chest');
  fb('Spine', 'Spine1', 'Hips');
  fb('Neck', 'Head');
  fb('Head', 'Neck');
  return added;
}

/* Required names a rig (list of raw bone names) still lacks after aliasing. */
export function missingHitBones(names) {
  const d = {};
  for (const n of names) d[n] = n;
  addCanonicalAliases(d, names.map(n => [n, n]));
  return HIT_BONES_REQUIRED.filter(n => !d[n]);
}
