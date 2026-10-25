/* ============================================================
   WESTERN HEART — Fight-camera vertical framing math (pure)
   Extracted from the Arena fight camera in game/js/scene.js
   (Tekken CameraRig port) so the level-following rule is
   unit-testable without a renderer or DOM.

   RULE (camera follows the fighting level — owner report
   2026-10-25: the camera stayed up top after a floor/balcony
   break while the fight continued on the level below):
   the camera's height and look target anchor to the CURRENT
   GROUND LEVEL (stageBreaks.groundY: 0 up top, -depth below),
   and the partial tracking factors (0.45 height / 0.25 look)
   apply ONLY to height ABOVE that ground (jumps, launches).
   The old scene.js math applied the factors to the fighters'
   ABSOLUTE root Y, which already includes the ground offset —
   so after a 6 m drop the camera sat 3.3 m too high and the
   look target 4.5 m too high, and the fighters fell out of
   frame below. On the upper level (groundY 0) this function
   reproduces the old values exactly.
   Wall breaks never change groundY, so wall-break framing is
   untouched. Stages with explicit camPos/camTgt overrides
   (nm-parking-lot, nm-lobby-glb — neither declares a floor or
   balcony breakable) bypass this math entirely, as before.
   ============================================================ */

export const FIGHT_CAM_HEIGHT = 1.75; // camera height above the fighting ground
export const FIGHT_CAM_LOOK = 1.0; // look-target height above the fighting ground
export const FIGHT_CAM_HEIGHT_TRACK = 0.45; // fraction of airborne height added to camera height
export const FIGHT_CAM_LOOK_TRACK = 0.25; // fraction of airborne height added to look target

/* groundY: current fighting ground (0 upper level, -depth below).
   maxY: highest fighter root Y (ground + airborne height).
   Returns { baseY, lookY } in world Y. */
export function fightCameraY(groundY, maxY) {
  const g = Number.isFinite(groundY) ? groundY : 0;
  const m = Number.isFinite(maxY) ? maxY : g;
  const airH = Math.max(0, m - g); // height above the current ground; never below it
  return {
    baseY: g + FIGHT_CAM_HEIGHT + airH * FIGHT_CAM_HEIGHT_TRACK,
    lookY: g + FIGHT_CAM_LOOK + airH * FIGHT_CAM_LOOK_TRACK,
  };
}
