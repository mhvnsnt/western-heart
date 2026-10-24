/* ============================================================
   WESTERN HEART — Roster (full 36-fighter build)
   Imports the complete named roster. Legacy ROSTER kept for
   backwards compat with existing game code.
   ============================================================ */
import { FULL_ROSTER, getFighter } from './roster-full.js';

export const ROSTER = FULL_ROSTER;
export { getFighter };
export function getCharacter(id) {
  return getFighter(id);
}
