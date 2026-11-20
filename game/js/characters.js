/* ============================================================
   WESTERN HEART — Roster (full 36-fighter build)
   Imports the complete named roster. Legacy ROSTER kept for
   backwards compat with existing game code.
   ============================================================ */
import { FULL_ROSTER, getFighter } from './roster-full.js';

import { attiresFor } from './attires.js';
// Material gate: a fighter with no attire that passes the material audit is not
// selectable (game/js/material-runtime.js; list in game/js/material-status.js).
// A fighter whose roster model is gated plays their first passing attire (own ladder).
export const ROSTER = FULL_ROSTER.filter(f => attiresFor(f).length > 0).map((f) => {
  const ok = attiresFor(f);
  return ok.some(a => a.model === f.model) ? f : { ...f, model: ok[0].model };
});
export { getFighter };
export function getCharacter(id) {
  return getFighter(id);
}
