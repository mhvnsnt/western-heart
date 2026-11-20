/* ============================================================
   WESTERN HEART — FightingEngine public air-reaction blend
   ------------------------------------------------------------
   Public FE combat rule only (FightingEngine.com / Hanmin Cho
   public notes). FE GitHub + playable builds stay PRIVATE until
   the official free OSS launch on 2026-12-25 — do not hunt for
   a leaked repo; do not vendor unpublished FE source.

   Formula (public):
     offset = catchHeight - clipStartHeight
     visualHeight = clipHeight + offset * weight
   Default weight 0.758 (FE public catch-height blend).

   WH owns the integration. This module is pure math + constants
   so Muse / any agent can wire it without guessing. Tag Battle
   demo characters (Hwoarang, Jin Kazama, Yugo the Wolf, Siegfried
   Schtauffen) are FE importer demos ONLY — never WH roster/canon.
   ============================================================ */

/** FE public catch-height blend weight (FightingEngine public rules). */
export const FE_AIR_BLEND_WEIGHT = 0.758;

/**
 * Catch-height offset: how far the authored clip's first frame sits
 * from the defender's height at the moment of the hit.
 * @param {number} catchHeight  defender height at hit (WH: root.y)
 * @param {number} clipStartHeight  first-frame height of the reaction clip
 * @returns {number} offset (0 when inputs are non-finite)
 */
export function airCatchOffset(catchHeight, clipStartHeight) {
  if (!Number.isFinite(catchHeight) || !Number.isFinite(clipStartHeight)) return 0;
  return catchHeight - clipStartHeight;
}

/**
 * Blended air height for the current clip sample.
 * visualHeight = clipHeight + offset * weight
 * @param {number} clipHeight
 * @param {number} offset  from airCatchOffset
 * @param {number} [weight=FE_AIR_BLEND_WEIGHT]
 * @returns {number}
 */
export function blendedAirHeight(clipHeight, offset, weight = FE_AIR_BLEND_WEIGHT) {
  if (!Number.isFinite(clipHeight)) return clipHeight;
  const o = Number.isFinite(offset) ? offset : 0;
  const w = Number.isFinite(weight) ? weight : FE_AIR_BLEND_WEIGHT;
  return clipHeight + o * w;
}

/**
 * Optional decay of blend weight toward the authored clip
 * (keeps FE weight as the starting value; WH may fade after).
 * @param {number} weight
 * @param {number} dt  seconds
 * @param {number} [rate=1.6]  per-second approach toward 0
 * @returns {number} weight in [0, 1]
 */
export function decayAirBlendWeight(weight, dt, rate = 1.6) {
  if (!Number.isFinite(weight)) return 0;
  if (!Number.isFinite(dt) || dt <= 0) return Math.min(1, Math.max(0, weight));
  const r = Number.isFinite(rate) ? Math.max(0, rate) : 1.6;
  return Math.min(1, Math.max(0, weight - r * dt));
}

/**
 * One-shot state helper for a fighter tick.
 * Call beginAirCatch on airborne hit; call sampleAirBlend each
 * physics frame (after integrating unblended Y, before ground clamp).
 */
export function beginAirCatch(catchHeight, weight = FE_AIR_BLEND_WEIGHT) {
  return {
    catchY: Number.isFinite(catchHeight) ? catchHeight : 0,
    clipStartY: null,
    weight: Number.isFinite(weight) ? weight : FE_AIR_BLEND_WEIGHT,
    boost: 0,
  };
}

/**
 * Apply FE blend for one frame.
 * Contract: `unblendedY` must NOT include a previous frame's boost.
 * @returns {{ y: number, state: object }}
 */
export function sampleAirBlend(state, unblendedY) {
  if (!state || !Number.isFinite(unblendedY)) {
    return { y: unblendedY, state };
  }
  const next = { ...state };
  if (next.clipStartY == null) next.clipStartY = unblendedY;
  const offset = airCatchOffset(next.catchY, next.clipStartY);
  const y = blendedAirHeight(unblendedY, offset, next.weight);
  next.boost = y - unblendedY;
  return { y, state: next };
}
