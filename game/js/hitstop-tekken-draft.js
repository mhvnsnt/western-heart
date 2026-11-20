/* hitstop-tekken-draft.js — Tekken-anchored hit-stop DRAFT (2026-11-02).
 *
 * DRAFT ONLY — NOT WIRED. Nothing imports this module. game.js and
 * combat-systems.js still run the live FX table (hit 6f, block 4f,
 * wall_splat 14f, counter +3f). Do NOT import this into game.js or
 * combat-systems.js until the owner approves the draft in chat.
 *
 * Why generic is 0: no Tekken 7 or Tekken 8 source searched publishes a
 * generic, weight-tiered hit-stop. Frame-data rows carry startup /
 * block / hit / counter-hit advantage, not a freeze column (see
 * docs/handoffs/HITSTOP-TEKKEN-DRAFT-20261102.md §1, §5). The only
 * published Tekken freeze values are special-case: 20f timestop /
 * hitstop on Heat-Burst-equivalent and named super-style moves.
 * Parry-success hit-stop is noted in Wavu with NO duration stated, so
 * it is null here — do not copy the 20f special value onto it.
 * Frames are at 60 fps: ms = frames * 1000 / 60.
 */
export const FRAME_SEC = 1 / 60;
export const NOT_WIRED = true;

export const HITSTOP_TEKken_DRAFT = {
  // Generic reactions: no published Tekken value — draft is 0, not a
  // claimed Tekken constant for that reaction.
  hit: 0,
  block: 0,
  juggle: 0,
  spin: 0,
  stagger: 0,
  screw: 0,
  knockdown: 0,
  guard_break: 0,
  floor_bound: 0,
  crumple: 0,
  launch: 0,
  wall_splat: 0,
  throw: 0,
  throw_break: 0,
  wakeup: 0,
  counter_bonus: 0,
  // Special-case only, NOT generic: Heat-Burst-equivalent system move
  // and named super-style / unblockable-style moves.
  special_timestop: 20,
  // Duration NOT FOUND in any source searched — intentionally null.
  parry_success: null,
};

export function draftStopSec(reaction) {
  const f = HITSTOP_TEKken_DRAFT[reaction];
  return f === null || f === undefined ? null : f * FRAME_SEC;
}
export function draftStopMs(reaction) {
  const s = draftStopSec(reaction);
  return s === null ? null : s * 1000;
}
