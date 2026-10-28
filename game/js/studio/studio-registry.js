/* Front-end labels live in ONE constant so the owner's naming is a one-line swap.
   Owner's final choice (2026-10-23): main menu "CREATION SUITE", poser "Stance Editor".
   Section names follow the real games: WWE 2K19 Creation Suite (Create a Superstar /
   Create a Move-set / Custom Entrance / Custom Arena) and Tekken 7 Customization. */
export const LABELS_UI = {
  suite: 'CREATION SUITE',
  suiteSub: 'Stance Editor · Create a Fighter · Moveset · Entrance · Arena',
  standalone: 'CREATION SUITE · ALL GAMES',
  stance: 'Stance Editor',
  creation: 'Create a Fighter', deform: 'Body Morph', forge: 'Create a Move', moveset: 'Moveset',
  strike: 'Strike Lab', dive: 'Dive Lab', mocap: 'Mocap', bannon: 'Animation Studio',
  entrance: 'Entrance', arena: 'Arena', library: 'Library',
};
const L = LABELS_UI;
/* `live` flips as each editor lands. base = real game system it writes into; bannon = port source. */
export const STUDIOS = [
  { id: 'pose', group: 'SUPERSTAR', icon: '🧍', name: L.stance, desc: 'Select, fight, win & entrance poses', live: true, mount: 'pose',
    base: 'select-screen.js + fighter.js stance', bannon: 'Fighter.prototype.poseStudio (index.html)' },
  { id: 'creation', group: 'SUPERSTAR', icon: '🎭', name: L.creation, desc: 'Body, face, hair, attire, AI', live: true, href: '../customization/creation-suite-ui/index.html',
    base: 'customization/creation-suite-ui', bannon: 'src/pages/CreationSuite.tsx' },
  { id: 'deform', group: 'SUPERSTAR', icon: '💪', name: L.deform, desc: 'Live deformation, flex', live: false,
    base: 'jiggle.js / softbody.js', bannon: 'grab-event volumetric deformation' },
  { id: 'forge', group: 'MOVES', icon: '⚒️', name: L.forge, desc: 'Build a move, assign a command', live: false,
    base: 'movesets.js + combat-core.js', bannon: 'FORGE / MOVE CREATOR' },
  { id: 'strike', group: 'MOVES', icon: '👊', name: L.strike, desc: 'Damage, frames, reach', live: false,
    base: 'frame-tables.js + hitdetect.js', bannon: 'STRIKE LAB' },
  { id: 'dive', group: 'LABS', icon: '🪂', name: L.dive, desc: 'Aerials and dives', live: false,
    base: 'physics.js aerial', bannon: 'DIVE LAB' },
  { id: 'moveset', group: 'MOVES', icon: '📋', name: L.moveset, desc: 'Assign moves to every command', live: false,
    base: 'movesets.js', bannon: 'MOVE CREATOR assign' },
  { id: 'entrance', group: 'SHOW', icon: '🚪', name: L.entrance, desc: 'Walk-out, lights, entrance pose', live: false,
    base: 'entrance scene', bannon: 'BANNON STUDIO Presets' },
  { id: 'arena', group: 'SHOW', icon: '🏟️', name: L.arena, desc: 'Build a stage', live: false,
    base: 'arena loader (sky/light locked)', bannon: 'CreationSuite arena builder' },
  { id: 'bannon', group: 'SHOW', icon: '🎬', name: L.bannon, desc: 'Anim · Build · Clips · Scan', live: false,
    base: 't3anims.js banks', bannon: 'BANNON STUDIO (v78)' },
  { id: 'mocap', group: 'LABS', icon: '🎥', name: L.mocap, desc: 'BVH/FBX motion onto a fighter', live: false,
    base: 'stance-aim.js retarget', bannon: 'MOCAP STUDIO (v78)' },
  { id: 'library', group: 'LABS', icon: '🗂️', name: L.library, desc: 'T8 · T7 · 2K19 · Fire Pro · Gang Beasts', live: false,
    base: '__WH_PRIVATE_ASSETS', bannon: 'BANNON STUDIO Scan/Memory' },
];
