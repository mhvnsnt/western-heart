/* Every Bannon studio, ported. `live` flips as each studio's PR lands.
   Base = the real game system the studio writes into; Bannon = source. */
export const STUDIOS = [
  { id: 'pose', group: 'CHARACTER', icon: '🧍', name: 'POSE STUDIO', desc: 'Select pose, fight stance, keyframes', live: true, mount: 'pose',
    base: 'select-screen.js + fighter.js stance', bannon: 'Fighter.prototype.poseStudio (index.html)' },
  { id: 'creation', group: 'CHARACTER', icon: '🎭', name: 'CREATION SUITE', desc: 'Body, face, hair, attire, AI DNA', live: false,
    base: 'customization/creation-suite-ui + customization-consumer.js', bannon: 'src/pages/CreationSuite.tsx' },
  { id: 'deform', group: 'CHARACTER', icon: '💪', name: 'LIVE DEFORMATION', desc: 'Muscle flex, grip squash, impact', live: false,
    base: 'jiggle.js / softbody.js', bannon: 'index.html grab-event volumetric deformation' },
  { id: 'bannon', group: 'ANIMATION', icon: '🎬', name: 'BANNON STUDIO', desc: 'Anim · Build · Clips · Presets · Scan · Memory', live: false,
    base: 't3anims.js banks', bannon: 'openStudio/renderStudio (BANNON_v78)' },
  { id: 'mocap', group: 'ANIMATION', icon: '🎥', name: 'MOCAP STUDIO', desc: 'Import BVH/FBX motion onto a fighter', live: false,
    base: 'stance-aim.js CMU retarget', bannon: 'MOCAP STUDIO (BANNON_v78)' },
  { id: 'forge', group: 'MOVES', icon: '⚒️', name: 'MOVE FORGE', desc: 'Create moves, assign commands', live: false,
    base: 'movesets.js + combat-core.js', bannon: 'FORGE / MOVE CREATOR' },
  { id: 'strike', group: 'MOVES', icon: '👊', name: 'STRIKE LAB', desc: 'Damage, frames, reach, impact', live: false,
    base: 'frame-tables.js + hitdetect.js', bannon: 'STRIKE LAB' },
  { id: 'dive', group: 'MOVES', icon: '🪂', name: 'DIVE LAB', desc: 'Aerials and dives', live: false,
    base: 'physics.js aerial', bannon: 'DIVE LAB' },
  { id: 'library', group: 'ALL GAMES', icon: '🗂️', name: 'LIBRARY', desc: 'Import / export across T8 · T7 · TTT2 · 2K19 · Fire Pro · Gang Beasts', live: false, standaloneOnly: false,
    base: '__WH_PRIVATE_ASSETS + extracted libraries', bannon: 'BANNON STUDIO Scan/Memory' },
];
