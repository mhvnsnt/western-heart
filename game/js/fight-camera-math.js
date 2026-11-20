/* ============================================================
   WESTERN HEART — Fight-camera framing math (pure)
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

   RULE (camera stays readable at arena edges — owner t374u
   2026-11-05): never shove the camera through / behind arena
   walls. Industry FG pattern (also noted in FightingEngine
   public camera/occlusion notes): cap dolly distance inside
   the stage shell; when the fighter span no longer fits,
   widen FOV instead of pulling the camera through geometry.
   Portrait already did this (maxD 10.5); landscape used to
   force min distance 10.5 and could keep pulling back — that
   is the edge shove / wall-block glitch.
   ============================================================ */

export const FIGHT_CAM_HEIGHT = 1.75; // camera height above the fighting ground
export const FIGHT_CAM_LOOK = 1.0; // look-target height above the fighting ground
export const FIGHT_CAM_HEIGHT_TRACK = 0.45; // fraction of airborne height added to camera height
export const FIGHT_CAM_LOOK_TRACK = 0.25; // fraction of airborne height added to look target

/** Default max dolly (m) before FOV widen — past this the stage shell occludes. */
export const FIGHT_CAM_MAX_DIST = 10.5;
/** Landscape minimum dolly (m). Was 10.5 (shoved into walls); Tekken-like default ~7. */
export const FIGHT_CAM_MIN_DIST_LANDSCAPE = 7.0;
/** Portrait minimum dolly (m). */
export const FIGHT_CAM_MIN_DIST_PORTRAIT = 6.0;
/** Max vertical FOV (deg) when widening to keep fighters framed inside maxDist. */
export const FIGHT_CAM_MAX_FOV = 80;

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

/**
 * Dolly distance + FOV so the camera stays inside the arena shell.
 * @param {object} o
 * @param {number} o.span  smoothed fighter span (m)
 * @param {number} o.aspect  camera aspect (w/h)
 * @param {number} o.baseFov  authored vertical FOV degrees
 * @param {number} [o.camScale=1]  stage camDist/7
 * @param {number} [o.maxDist=FIGHT_CAM_MAX_DIST]
 * @returns {{ dist: number, fov: number, fitDist: number, clamped: boolean }}
 */
export function fightCameraDolly({
  span,
  aspect,
  baseFov,
  camScale = 1,
  maxDist = FIGHT_CAM_MAX_DIST,
} = {}) {
  const a = Number.isFinite(aspect) && aspect > 0.05 ? aspect : 1;
  const portrait = a < 1;
  const pad = portrait ? 1.8 : 3.0;
  const fov0 = Number.isFinite(baseFov) && baseFov > 1 ? baseFov : 45;
  const spanN = Number.isFinite(span) ? Math.max(span, portrait ? 2.6 : 4.5) : (portrait ? 2.6 : 4.5);
  const vFov = (fov0 * Math.PI) / 180;
  const hFov = 2 * Math.atan(Math.tan(vFov / 2) * a);
  const fitDist = (spanN + pad) / (2 * Math.tan(hFov / 2));
  const minD = portrait ? FIGHT_CAM_MIN_DIST_PORTRAIT : FIGHT_CAM_MIN_DIST_LANDSCAPE;
  const maxD = Number.isFinite(maxDist) && maxDist > 0 ? maxDist : FIGHT_CAM_MAX_DIST;
  const scale = Number.isFinite(camScale) && camScale > 0 ? camScale : 1;

  let dist = Math.max(minD, fitDist) * scale;
  let fov = fov0;
  let clamped = false;
  const cap = maxD * scale;
  if (dist > cap) {
    clamped = true;
    const needH = 2 * Math.atan((spanN + pad) / (2 * maxD));
    fov = Math.min(
      FIGHT_CAM_MAX_FOV,
      (2 * Math.atan(Math.tan(needH / 2) / a) * 180) / Math.PI,
    );
    dist = cap;
  }
  return { dist, fov, fitDist: fitDist * scale, clamped };
}

/**
 * Soft lateral clamp: keep the look-center from driving the camera
 * into the side walls when both fighters are piled on an edge.
 * Returns a eased centerX.
 */
export function fightCameraCenterX(centerX, wallDistance = 8.4, margin = 1.2) {
  const w = Number.isFinite(wallDistance) ? Math.abs(wallDistance) : 8.4;
  const m = Number.isFinite(margin) ? Math.max(0, margin) : 1.2;
  const lim = Math.max(0.5, w - m);
  const c = Number.isFinite(centerX) ? centerX : 0;
  return Math.max(-lim, Math.min(lim, c));
}
