export * from './dna.js';
export * from './regions.js';
export * from './body.js';
export * from './secondary.js';
export * from './attire.js';
import { applySliders } from './body.js';
import { buildSecondaryRig } from './secondary.js';
// One-call: reshape a character from DNA and build its jiggle rig.
export function applyDNA(root, dna) {
  applySliders(root, dna.sliders || {});
  return dna.physics?.enabled === false ? null : buildSecondaryRig(root, { sliders: dna.sliders || {} });
}
export * from './menu.js';
export * from './parts.js';
export * from './rigpose.js';
