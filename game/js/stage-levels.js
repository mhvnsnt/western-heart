/* ============================================================
   WESTERN HEART — Stage levels (Lane 5: stages, geometry side)
   Pure data, no imports, no DOM: given a stage def (the shape in
   game/js/stages.js) it derives the fight's LEVELS — the upper
   arena plus every destination a break can move the fight to.

   Sourcing (no guesses, no invented geometry):
   • Every stage's upper level is its def: dims.wallDistance,
     groundY 0, spawns unchanged.
   • Wall breaks: stagebreaks.js adds a breakable wall at
     ±wallDistance to EVERY stage unless the def sets noWallBreak,
     and extends bounds by WALL_EXTEND on a break. The
     wall-broken level below mirrors that exactly.
   • Floor / balcony breaks: only where the def already declares
     a breakable (shrine floor, plains-of-chi-u floor, helix-palace
     balcony on main). The lower level's groundY is -depth from
     that same breakable — nothing else is assumed about what is
     below; the builder / combat lane owns what it looks like.
   • Tekken archetypes (stagebreaks.js header): T7 floor breaks
     (Forgotten Realm, Brimstone & Fire, Devil's Pit) and the T7
     Jungle Outpost 2 balcony break are the MODELS for these
     shapes. WH ships no T7 stage geometry for them (the one T7
     stage in the repo, Mishima Dojo, is a private-build GLB with
     no declared breakables), so no T7 level is claimed as a WH
     file extraction — T7/T6/T5 multi-level structures beyond
     these archetypes are UNVERIFIED for WH stages.
   • T3 retro + No Mercy stages declare no breakables: they get
     upper + wall-broken only. Whether the T3 originals had floor
     breaks is UNVERIFIED (their WH form is a panorama shell).

   This module owns GEOMETRY only. Break STATE (which breakables
   are broken, splat routing, damage bonuses) belongs to the
   combat lane's stagebreaks.js — it must not be duplicated here,
   and this module never mutates a stage def.
   ============================================================ */

// Mirrors stagebreaks.js WALL_EXTEND (bounds growth past a broken
// wall). If that constant ever changes, this must change with it
// (test/stage-levels.test.mjs pins the value against this file's
// export, and the audit doc names both sites).
export const WALL_BREAK_EXTEND = 4.5;

function _drop(b) {
  const d = Number(b && b.depth);
  return Number.isFinite(d) && d > 0 ? d : 6;
}

/* Full level list for one stage def, in play order: upper first,
   then the wall-broken level, then one lower level per declared
   floor / balcony breakable. Levels are plain data:
     { id, groundY, wallDistance, via, zone }
   via is null (upper), 'wall', 'floor' or 'balcony'; zone carries
   the triggering breakable's footprint (x, z, r, w) when known. */
export function resolveStageLevels(stageDef) {
  if (!stageDef || !stageDef.dims || !Number.isFinite(stageDef.dims.wallDistance)) return [];
  const wall = stageDef.dims.wallDistance;
  const levels = [{ id: 'upper', groundY: 0, wallDistance: wall, via: null, zone: null }];
  if (!stageDef.noWallBreak) {
    levels.push({ id: 'wall-broken', groundY: 0, wallDistance: wall + WALL_BREAK_EXTEND, via: 'wall', zone: null });
  }
  for (const b of stageDef.breakables || []) {
    if (b.type === 'floor') {
      levels.push({
        id: `floor-below-${b.x ?? 0}-${b.z ?? 0}`, groundY: -_drop(b),
        wallDistance: wall, via: 'floor',
        zone: { x: b.x ?? 0, z: b.z ?? 0, r: b.r ?? 2.5 },
      });
    } else if (b.type === 'balcony') {
      levels.push({
        id: `balcony-below-${b.x ?? 0}`, groundY: -_drop(b),
        wallDistance: wall, via: 'balcony',
        zone: { x: b.x ?? 0, z: b.z ?? 0, r: b.r ?? 2.5, w: b.w ?? null },
      });
    }
  }
  return levels;
}

/* Destination level for ONE break, from the upper level.
   Returns the level object, or null when the breakable type is
   unknown or the stage has no such destination (e.g. a wall break
   on a noWallBreak stage). Pure: no state is read or written. */
export function levelAfterBreak(stageDef, breakable) {
  if (!breakable || typeof breakable.type !== 'string') return null;
  const levels = resolveStageLevels(stageDef);
  if (breakable.type === 'wall') return levels.find((l) => l.via === 'wall') || null;
  if (breakable.type === 'floor' || breakable.type === 'balcony') {
    return levels.find((l) => l.via === breakable.type
      && (breakable.x === undefined || !l.zone || l.zone.x === breakable.x)) || null;
  }
  return null;
}

/* Geometry after a SET of breaks (combat-lane composition aid):
   groundY is the deepest declared drop among the broken
   floor / balcony breakables (0 when none broke), wallDistance
   is the wall-broken bound when a wall broke, else the upper
   bound. `broken` is an array of breakable objects (same shape
   as stageDef.breakables entries). */
export function composeLevel(stageDef, broken) {
  const levels = resolveStageLevels(stageDef);
  const upper = levels.find((l) => l.via === null);
  if (!upper) return null;
  let groundY = 0;
  let wallDistance = upper.wallDistance;
  for (const b of broken || []) {
    if (b.type === 'wall' && !stageDef.noWallBreak) wallDistance = upper.wallDistance + WALL_BREAK_EXTEND;
    if (b.type === 'floor' || b.type === 'balcony') groundY = Math.min(groundY, -_drop(b));
  }
  return { groundY, wallDistance };
}
