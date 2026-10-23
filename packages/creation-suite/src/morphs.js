/* morphs.js — Creation Suite body-morph pipeline module.
   Source: MPFB2 v2.0.18 (makehumancommunity/mpfb2), pulled into
   mhvnsnt/cape-jones production/tools/mpfb2 (PR #128 merged).
   Real morphs bake as MPFB_<id> shape keys via
   customization/body-morphs/apply_mpfb_morphs.py (headless Blender,
   KD-tree target transfer). The three.js proxies below are live-preview
   approximations; the baked shape keys are the ground truth. */

export const BODY_MORPHS = [
  { id:'height',    label:'Height',    range:[-1,1], cat:'body', mpfb:'macrodetails/height/*' },
  { id:'bulk',      label:'Bulk',      range:[-1,1], cat:'body', mpfb:['torso/*pectoral*','arms/*muscle*','stomach/*tone*'] },
  { id:'muscle',    label:'Muscle',    range:[-1,1], cat:'body', mpfb:'arms/*muscle*,legs/*muscle*,torso/*pectoral*' },
  { id:'fat',       label:'Body Fat',  range:[-1,1], cat:'body', mpfb:'stomach/*tone*,arms/*fat*,legs/*fat*' },
  { id:'shoulders', label:'Shoulders', range:[-1,1], cat:'body', mpfb:'torso/measure-shoulder-dist-decr-incr' },
  { id:'belly',     label:'Belly',     range:[-1,1], cat:'body', mpfb:'stomach/*' },
  { id:'limbs',     label:'Limb Length',range:[-1,1],cat:'body', mpfb:'arms/measure-*,legs/measure-*' },
  { id:'chest',     label:'Chest',     range:[-1,1], cat:'body', mpfb:'torso/*,breast/*' },
  { id:'waist',     label:'Waist',     range:[-1,1], cat:'body', mpfb:'torso/measure-*waist*,hip/hip-waist-*' },
  { id:'hips',      label:'Hips',      range:[-1,1], cat:'body', mpfb:'hip/*,buttocks/*' },
  { id:'neck',      label:'Neck',      range:[-1,1], cat:'body', mpfb:'neck/measure-*' },
  { id:'hands',     label:'Hands',     range:[-1,1], cat:'body', mpfb:'hands/hand-scale-*' },
  { id:'feet',      label:'Feet',      range:[-1,1], cat:'body', mpfb:'feet/foot-scale-*' },
];

/* ---------------------------------------------------------------------------
   ANATOMY LAYER MORPHS — deep per-body-part morphing from separable
   volumetric layers (BONE / MUSCLE / FAT / SKIN).
   Source: docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md.
   Generated per fighter by tools/anatomy/generate_layers.py into
   roster/<fighter>/anatomy/anatomy-layers.json (schema wh.anatomy-layers/1);
   this registry is the fighter-independent dial contract the morphing UI
   crew builds on. Daz-style composition with BODY_MORPHS:
     final = base + Σ dial·delta
   Anatomy dials bake to per-vertex displacement along skin normals (skin
   rides the muscle surface; fat thickens/thins the shell) via the
   bake_displacement() primitive in tools/anatomy/generate_layers.py —
   additive with MPFB shape keys, never replacing them. The morphing UI
   itself is owned by another crew; this file only exposes the data. */
export const ANATOMY_LAYER_MORPHS = [
  // Muscle layer — bulk per group; group radii *= 1 + 0.55*v, v in [-1,1].
  { id:'muscle_trapezius',     label:'Trapezius bulk',      range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['trapezius'] },
  { id:'muscle_neck',          label:'Neck bulk',           range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['neck'] },
  { id:'muscle_deltoid_L',     label:'Deltoid bulk (L)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['deltoid.L'] },
  { id:'muscle_deltoid_R',     label:'Deltoid bulk (R)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['deltoid.R'] },
  { id:'muscle_biceps_L',      label:'Biceps bulk (L)',     range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['biceps.L'] },
  { id:'muscle_biceps_R',      label:'Biceps bulk (R)',     range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['biceps.R'] },
  { id:'muscle_triceps_L',     label:'Triceps bulk (L)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['triceps.L'] },
  { id:'muscle_triceps_R',     label:'Triceps bulk (R)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['triceps.R'] },
  { id:'muscle_forearm_L',     label:'Forearm bulk (L)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['forearm.L'] },
  { id:'muscle_forearm_R',     label:'Forearm bulk (R)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['forearm.R'] },
  { id:'muscle_pectoralis_L',  label:'Pectoralis bulk (L)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['pectoralis.L'] },
  { id:'muscle_pectoralis_R',  label:'Pectoralis bulk (R)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['pectoralis.R'] },
  { id:'muscle_latissimus_L',  label:'Latissimus bulk (L)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['latissimus.L'] },
  { id:'muscle_latissimus_R',  label:'Latissimus bulk (R)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['latissimus.R'] },
  { id:'muscle_abdominals',    label:'Abdominals bulk',     range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['abdominals'] },
  { id:'muscle_obliques_L',    label:'Obliques bulk (L)',   range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['obliques.L'] },
  { id:'muscle_obliques_R',    label:'Obliques bulk (R)',   range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['obliques.R'] },
  { id:'muscle_gluteus_L',     label:'Gluteus bulk (L)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['gluteus.L'] },
  { id:'muscle_gluteus_R',     label:'Gluteus bulk (R)',    range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['gluteus.R'] },
  { id:'muscle_quadriceps_L',  label:'Quadriceps bulk (L)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['quadriceps.L'] },
  { id:'muscle_quadriceps_R',  label:'Quadriceps bulk (R)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['quadriceps.R'] },
  { id:'muscle_hamstrings_L',  label:'Hamstrings bulk (L)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['hamstrings.L'] },
  { id:'muscle_hamstrings_R',  label:'Hamstrings bulk (R)', range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['hamstrings.R'] },
  { id:'muscle_calves_L',      label:'Calves bulk (L)',     range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['calves.L'] },
  { id:'muscle_calves_R',      label:'Calves bulk (R)',     range:[-1,1], cat:'anatomy-muscle', layer:'muscle', applies_to:['calves.R'] },
  // Fat layer — subcutaneous thickness; region/global *= 1 + 0.80*v.
  { id:'fat_head',       label:'Fat: head',     range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['head'] },
  { id:'fat_torso',      label:'Fat: torso',    range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['torso'] },
  { id:'fat_arm_L',      label:'Fat: arm (L)',  range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['arm.L'] },
  { id:'fat_arm_R',      label:'Fat: arm (R)',  range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['arm.R'] },
  { id:'fat_leg_L',      label:'Fat: leg (L)',  range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['leg.L'] },
  { id:'fat_leg_R',      label:'Fat: leg (R)',  range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['leg.R'] },
  { id:'fat_thickness',  label:'Fat (global)',  range:[-1,1], cat:'anatomy-fat', layer:'fat', applies_to:['head','torso','arm.L','arm.R','leg.L','leg.R'] },
  // Bone layer — bone scale; radii *= 1 + 0.25*v.
  { id:'bone_scale_limbs',   label:'Bone: limbs',   range:[-1,1], cat:'anatomy-bone', layer:'bone', applies_to:['limb capsules'] },
  { id:'bone_scale_spine',   label:'Bone: spine',   range:[-1,1], cat:'anatomy-bone', layer:'bone', applies_to:['axial capsules'] },
  { id:'bone_scale_skull',   label:'Bone: skull',   range:[-1,1], cat:'anatomy-bone', layer:'bone', applies_to:['bone_skull'] },
  { id:'bone_scale_ribcage', label:'Bone: ribcage', range:[-1,1], cat:'anatomy-bone', layer:'bone', applies_to:['bone_ribcage'] },
  { id:'bone_scale_pelvis',  label:'Bone: pelvis',  range:[-1,1], cat:'anatomy-bone', layer:'bone', applies_to:['bone_pelvis'] },
];

/* Look up an anatomy dial definition by id. */
export function anatomyMorphById(id){
  return ANATOMY_LAYER_MORPHS.find(m => m.id === id) || null;
}

/* Compose anatomy dial values with BODY_MORPH values into one dial vector.
   Anatomy dials are additive with the Daz-style BODY_MORPHS, so the UI just
   merges both dicts; the bake path (tools/anatomy/generate_layers.py
   bake_displacement) applies anatomy deltas along skin normals. */
export function composeMorphVector(bodyValues, anatomyValues){
  return { ...(bodyValues || {}), ...(anatomyValues || {}) };
}

/* Face-shape morphs (MPFB regional targets) — eyes/nose/mouth/face shapes. */
export const FACE_SHAPE_MORPHS = [
  { id:'eye_size',   label:'Eye Size',   range:[-1,1], cat:'face', mpfb:'eyes/eye-scale-decr-incr' },
  { id:'eye_tilt',   label:'Eye Tilt',   range:[-1,1], cat:'face', mpfb:'eyes/eye-corner1-down-up' },
  { id:'eye_height', label:'Eye Height', range:[-1,1], cat:'face', mpfb:'eyes/eye-height1-decr-incr' },
  { id:'nose_width', label:'Nose Width', range:[-1,1], cat:'face', mpfb:'nose/nose-width1-decr-incr' },
  { id:'nose_tip',   label:'Nose Tip',   range:[-1,1], cat:'face', mpfb:'nose/nose-point-width-decr-incr' },
  { id:'nose_length',label:'Nose Length',range:[-1,1], cat:'face', mpfb:'nose/nose-scale-vert-decr-incr' },
  { id:'mouth_width',label:'Mouth Width',range:[-1,1], cat:'face', mpfb:'mouth/mouth-scale-horiz-decr-incr' },
  { id:'lip_fullness',label:'Lips',      range:[-1,1], cat:'face', mpfb:'mouth/mouth-lowerlip-height-decr-incr' },
  { id:'face_oval',  label:'Face Shape', range:[-1,1], cat:'face', mpfb:'head/head-oval' },
  { id:'cheekbones', label:'Cheekbones', range:[-1,1], cat:'face', mpfb:'cheek/cheek-bones-decr-incr' },
  { id:'jaw_width',  label:'Jaw Width',  range:[-1,1], cat:'face', mpfb:'chin/chin-width-decr-incr' },
  { id:'forehead_height',label:'Forehead',range:[-1,1],cat:'face', mpfb:'forehead/forehead-scale-vert-decr-incr' },
];

/* Mirrors GNM's blend_expressions: weighted mix of morph values -> vector. */
export function blendMorphs(weights){
  const vec = {};
  const total = Object.values(weights).reduce((a,b)=>a+b,0) || 1;
  for(const [id,w] of Object.entries(weights)) vec[id] = (vec[id]||0) + w/total;
  return vec;
}

/* Live-preview proxy for three.js: apply morph vector to a skinned character.
   Shape keys (baked) are the truth; this scales bone chains for instant feedback. */
export function applyMorphProxies(character, values){
  const set = (name, sx, sy, sz)=>{
    const o = character.getObjectByName(name);
    if(o) o.scale.set(sx, sy, sz);
  };
  const v = id => values[id] || 0;
  const s = x => 1 + 0.15 * x;
  // height: whole-body Y
  if(v('height')) set('Hips', s(v('height'))*0+1, s(v('height')), 1);
  // bulk/muscle/fat: torso + limb girth proxies
  const girth = 1 + 0.12*(v('bulk')+v('muscle')) + 0.10*v('fat');
  if(girth !== 1){ set('Spine', girth, 1, girth); set('Spine1', girth, 1, girth); }
  if(v('shoulders')){ set('LeftShoulder', 1+v('shoulders')*0.2, 1, 1); set('RightShoulder', 1+v('shoulders')*0.2, 1, 1); }
  if(v('belly')) set('Spine1', 1, 1, 1 + v('belly')*0.25);
  if(v('limbs')){ const l = 1 + v('limbs')*0.15;
    for(const b of ['LeftUpperLeg','RightUpperLeg','LeftLowerLeg','RightLowerLeg','LeftUpperArm','RightUpperArm']) set(b, 1, l, 1); }
  if(v('neck')) set('Neck', 1+v('neck')*0.15, 1, 1+v('neck')*0.15);
  return character;
}
