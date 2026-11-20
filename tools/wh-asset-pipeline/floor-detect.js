// floor-detect.js — Western Heart character grounding (side-chat pull, wired for game).
// Requirement (side chat "Cape Jones 3D work", user 2026-10-24): Alisa floats — "use a
// smart way of full stack open source way wire in a way to actually detect the floor like
// a grid sensor or anything else ... so you can get her feet on the [floor]".
// Design: raycast grid sensor. N sample rays (default 5: pelvis + 4 around feet box) cast
// down from the character root; ground height = median of hits (median rejects single-ray
// spikes on steps/props). Character root Y is snapped so the lowest foot bone sits on
// ground height; on no hit, keep last good height (never snap to void).
// Integration point: game/js/fighter.js — call groundSnap(fighter, scene) once per tick
// AFTER root-motion application, BEFORE arena clamp + body pushout, so grounding never
// fights root motion. Pure three.js Raycaster, no new dependency.
// Status: module written 2026-10-24, NOT yet merged into fighter.js (needs a game PR +
// live playtest: Alisa/Cape feet on floor on Jungle Outpost + flat arena, no jitter).
import * as THREE from 'three';

const _down = new THREE.Vector3(0, -1, 0);
const _ray = new THREE.Raycaster();
const _origin = new THREE.Vector3();

export function groundHeightAt(scene, x, z, opts = {}) {
  const rayLen = opts.rayLen ?? 10;
  const yTop = opts.yTop ?? 5;
  const offsets = opts.offsets ?? [[0, 0], [0.25, 0], [-0.25, 0], [0, 0.25], [0, -0.25]];
  const hits = [];
  for (const [ox, oz] of offsets) {
    _origin.set(x + ox, yTop, z + oz);
    _ray.set(_origin, _down);
    _ray.far = rayLen;
    const found = _ray.intersectObjects(scene.children, true)
      .find((h) => h.object.userData?.isFloor !== false && !h.object.userData?.isFighter);
    if (found) hits.push(found.point.y);
  }
  if (!hits.length) return null;
  hits.sort((a, b) => a - b);
  return hits[Math.floor(hits.length / 2)]; // median
}

// Snap a fighter root so its foot level rests on the ground. fighter = { root: Object3D,
// footOffsetY: number (root Y at which feet touch ground, from rig), lastGroundY }.
export function groundSnap(fighter, scene, opts = {}) {
  const g = groundHeightAt(scene, fighter.root.position.x, fighter.root.position.z, opts);
  if (g === null) return fighter.lastGroundY ?? null; // no hit: hold, never void-snap
  fighter.lastGroundY = g;
  fighter.root.position.y = g - (fighter.footOffsetY ?? 0);
  return g;
}
