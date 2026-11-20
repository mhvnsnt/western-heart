// Pure-math body regions on the canonical skeleton (no three.js needed, so
// the same table drives the Godot port). Every region is an ellipsoid in the
// model's bind space anchored between canonical bones; "side" splits L/R,
// "front" keeps only z>0 (+Z forward) or z<0 (back) of the anchor.
// Canonical bone names come from western-heart Lab M1 (Root, Hips, Spine,
// Chest, Neck, Head, Left/Right Shoulder/Arm/ForeArm/Hand/UpLeg/Leg/Foot/ToeBase).
export const REGIONS = {
  belly:  { a: 'Hips', b: 'Spine', t: 0.6, radius: [0.26, 0.22, 0.28], front: +1, slider: ['belly', 'weight'], jiggle: true, parent: 'Spine' },
  chestL: { a: 'Chest', b: 'LeftShoulder', t: 0.35, drop: 0.1, radius: [0.14, 0.13, 0.2], front: +1, slider: ['chest', 'weight'], jiggle: true, parent: 'Chest' },
  chestR: { a: 'Chest', b: 'RightShoulder', t: 0.35, drop: 0.1, radius: [0.14, 0.13, 0.2], front: +1, slider: ['chest', 'weight'], jiggle: true, parent: 'Chest' },
  gluteL: { a: 'Hips', b: 'LeftUpLeg', t: 0.7, radius: [0.15, 0.15, 0.22], front: -1, slider: ['glutes', 'weight'], jiggle: true, parent: 'Hips' },
  gluteR: { a: 'Hips', b: 'RightUpLeg', t: 0.7, radius: [0.15, 0.15, 0.22], front: -1, slider: ['glutes', 'weight'], jiggle: true, parent: 'Hips' },
  thighL: { a: 'LeftUpLeg', b: 'LeftLeg', t: 0.4, radius: [0.22, 0.3, 0.22], slider: ['thighs', 'weight'], jiggle: true, parent: 'LeftUpLeg' },
  thighR: { a: 'RightUpLeg', b: 'RightLeg', t: 0.4, radius: [0.22, 0.3, 0.22], slider: ['thighs', 'weight'], jiggle: true, parent: 'RightUpLeg' },
  hipL:   { a: 'Hips', b: 'LeftUpLeg', t: 1.0, radius: [0.11, 0.13, 0.16], side: true, slider: ['hips'], jiggle: false },
  hipR:   { a: 'Hips', b: 'RightUpLeg', t: 1.0, radius: [0.11, 0.13, 0.16], side: true, slider: ['hips'], jiggle: false },
  armL:   { a: 'LeftArm', b: 'LeftForeArm', t: 0.5, radius: [0.3, 0.2, 0.2], slider: ['arms', 'muscle', 'weight'], jiggle: false },
  armR:   { a: 'RightArm', b: 'RightForeArm', t: 0.5, radius: [0.3, 0.2, 0.2], slider: ['arms', 'muscle', 'weight'], jiggle: false },
  neck:   { a: 'Neck', b: 'Head', t: 0.3, radius: [0.18, 0.12, 0.18], slider: ['neck', 'muscle'], jiggle: false },
};
// Regions with "front" ignore the z radius (they take the whole front/back
// surface half inside the x/y ellipse) because Tripo bodies vary a lot in depth.
// Region radius/drop are in units of the Hips->Head distance (torso unit) so they adapt to any model size.

// Size-adaptive physics tuning. girth = measured mean radial distance (m) of
// the region's vertices from its centre after sliders; mass grows with volume
// so heavy/curvy characters get looser, heavier, slower springs and slim
// characters get stiff or no jiggle at all.
export const PHYSICS_BASE = {
  belly:  { minGirth: 0.10, stiffness: 140, damping: 9,  maxOffset: 0.06 },
  chest:  { minGirth: 0.06, stiffness: 120, damping: 7,  maxOffset: 0.05 },
  glute:  { minGirth: 0.08, stiffness: 150, damping: 8,  maxOffset: 0.05 },
  thigh:  { minGirth: 0.07, stiffness: 220, damping: 12, maxOffset: 0.03 },
  hair:   { minGirth: 0,    stiffness: 60,  damping: 4,  maxOffset: 0.2 },
  cloth:  { minGirth: 0,    stiffness: 50,  damping: 5,  maxOffset: 0.25 },
};
export function familyOf(region) { return region.replace(/[LR]$/, ''); }

export function physicsFor(region, girth, refGirth) {
  const base = PHYSICS_BASE[familyOf(region)];
  if (!base) return null;
  if (girth < base.minGirth) return null; // too slim/flat: no jiggle bone
  const k = Math.max(0.5, Math.min(4, (girth / refGirth) ** 3)); // volume ratio
  return {
    mass: k,
    stiffness: base.stiffness / Math.sqrt(k),   // bigger = looser
    damping: base.damping / Math.cbrt(k),
    maxOffset: base.maxOffset * Math.min(2.5, Math.sqrt(k)),
  };
}

// slider value -> displacement amount (m per unit of region radius)
export function regionAmount(def, sliders) {
  let a = 0;
  for (const s of def.slider) a += (sliders[s] || 0) * (s === 'weight' ? 0.5 : 1);
  return a;
}
