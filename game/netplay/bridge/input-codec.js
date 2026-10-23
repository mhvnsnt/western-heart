// input-codec.js -- Western Heart input -> netcode input word.
//
// Maps the game's real input shape (see game/js/input.js: axisX, up/down
// intents, pressed[] one-shot actions, held.block) onto a 16-bit word that
// fits lite-rollback's inputWords=1 wire codec (packInputs/unpackInputs).
//
// Bit layout (16 bits):
//   0 LEFT   1 RIGHT  2 UP  3 DOWN
//   4 LP(1)  5 RP(2)  6 LK(3)  7 RK(4)
//   8 BLOCK  9 GRAB   10 SURGE  11 DODGE
//   12 TRANSFORM  13 SS_UP  14 SS_DOWN  15 reserved
//
// DOM-free and node-testable: `node --test` on test-bridge.mjs.

export const NET = Object.freeze({
  LEFT: 1 << 0,
  RIGHT: 1 << 1,
  UP: 1 << 2,
  DOWN: 1 << 3,
  LP: 1 << 4,   // Tekken limb 1
  RP: 1 << 5,   // Tekken limb 2
  LK: 1 << 6,   // Tekken limb 3
  RK: 1 << 7,   // Tekken limb 4
  BLOCK: 1 << 8,
  GRAB: 1 << 9,
  SURGE: 1 << 10,
  DODGE: 1 << 11,
  TRANSFORM: 1 << 12,
  SS_UP: 1 << 13,   // sidestep tap up (Tekken 7 tap-vs-hold)
  SS_DOWN: 1 << 14, // sidestep tap down
});

// InputManager one-shot action names -> codec bits.
const ACTION_BIT = {
  '1': NET.LP, '2': NET.RP, '3': NET.LK, '4': NET.RK,
  punch: NET.LP, kick: NET.RK, // legacy P/K map to lead limbs
  grab: NET.GRAB,
  surge: NET.SURGE,
  dodge: NET.DODGE,
  transform: NET.TRANSFORM, 'transform-down': NET.TRANSFORM,
  'ss-up': NET.SS_UP, 'ss-down': NET.SS_DOWN,
  '1+3': NET.GRAB, '2+4': NET.GRAB, // Tekken throw chords
};

/**
 * encodeInput(state) -> uint16 word.
 * state: { axisX (-1..1), up (bool jump intent), down (bool crouch intent),
 *          block (bool held), pressed (array of one-shot action names) }.
 * Matches the InputManager's exposed state shape in game/js/input.js.
 */
export function encodeInput(state) {
  let w = 0;
  const s = state || {};
  const ax = s.axisX || 0;
  if (ax < -0.25) w |= NET.LEFT;
  else if (ax > 0.25) w |= NET.RIGHT;
  if (s.up) w |= NET.UP;
  else if (s.down) w |= NET.DOWN;
  if (s.block) w |= NET.BLOCK;
  const pressed = s.pressed || [];
  for (const a of pressed) {
    const bit = ACTION_BIT[a];
    if (bit) w |= bit;
  }
  // Chord specials ('1+2' / '3+4' specials, '1+4' / '2+3' command inputs)
  // have no netcode bit of their own: they ride as their limb bits, and the
  // sim resolves chords from limb history — same as the offline game.
  for (const a of pressed) {
    if (a === '1+2') w |= NET.LP | NET.RP;
    else if (a === '3+4') w |= NET.LK | NET.RK;
    else if (a === '1+4') w |= NET.LP | NET.RK;
    else if (a === '2+3') w |= NET.RP | NET.LK;
  }
  return w & 0xffff;
}

/**
 * decodeInput(word) -> { left, right, up, down, lp, rp, lk, rk, block,
 *                        grab, surge, dodge, transform, ssUp, ssDown }.
 * Inverse of encodeInput (lossy only for chord specials, by design).
 */
export function decodeInput(word) {
  const w = word >>> 0;
  return {
    left: !!(w & NET.LEFT),
    right: !!(w & NET.RIGHT),
    up: !!(w & NET.UP),
    down: !!(w & NET.DOWN),
    lp: !!(w & NET.LP),
    rp: !!(w & NET.RP),
    lk: !!(w & NET.LK),
    rk: !!(w & NET.RK),
    block: !!(w & NET.BLOCK),
    grab: !!(w & NET.GRAB),
    surge: !!(w & NET.SURGE),
    dodge: !!(w & NET.DODGE),
    transform: !!(w & NET.TRANSFORM),
    ssUp: !!(w & NET.SS_UP),
    ssDown: !!(w & NET.SS_DOWN),
  };
}

/**
 * inputWordToSimBits(word) -> the reference fighter-sim INPUT bits.
 * Lets the netplay demo / lobby versus drive the deterministic reference
 * sim (game/netplay/sim/fighter-sim.js) with real WH control feel:
 * LP->jab, RP->heavy punch, LK->kick, RK->heavy kick, block/away->block.
 */
export function inputWordToSimBits(word) {
  // Imported lazily to keep this module dependency-free for tests that
  // don't have the sim on the path. The bit constants are duplicated
  // here deliberately (documented mapping, not a hidden import).
  const SIM = { LEFT: 0x01, RIGHT: 0x02, UP: 0x04, DOWN: 0x08,
                LP: 0x10, HP: 0x20, LK: 0x40, HK: 0x80, BLOCK: 0x100 };
  const w = word >>> 0;
  let s = 0;
  if (w & NET.LEFT) s |= SIM.LEFT;
  if (w & NET.RIGHT) s |= SIM.RIGHT;
  if (w & NET.UP) s |= SIM.UP;
  if (w & (NET.DOWN | NET.BLOCK)) s |= SIM.BLOCK;
  if (w & NET.LP) s |= SIM.LP;
  if (w & NET.RP) s |= SIM.HP;
  if (w & NET.LK) s |= SIM.LK;
  if (w & NET.RK) s |= SIM.HK;
  if (w & NET.GRAB) s |= SIM.LP | SIM.LK; // throw reads as limb pair
  return s >>> 0;
}
