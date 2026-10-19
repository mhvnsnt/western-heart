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
