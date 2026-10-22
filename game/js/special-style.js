/* ============================================================
   WESTERN HEART — Special Style (simplified input mode)
   Owner-approved 2026-10-22 (learning tools: YES, ALL).
   Teardown source: Tekken 8 Special Style — one-button bread-and-butter:
   single buttons fire curated strings, easy combos, and simplified
   specials so a new player can FIGHT on day one. Faithful port:
     • toggle per player (not per fighter); readable HUD badge;
     • 1/2/3/4 map to curated per-fighter strings (data table, Tekken
       notations) instead of single limbs;
     • complex motions (qcf etc.) collapse to their Special entries;
     • throws stay manual (Tekken keeps throws honest).
   WH canon mapping (PROPOSED — needs owner approval):
     "GUIDED HANDS" — the Trial guides a lost soul's hands. The call
     draws every lost soul; the Trial steadies the newest ones until
     their own hands remember. Alternative: "Soul Guidance" — flagged.
   ============================================================ */

export const SPECIAL_STYLE_FLAG = 'wh_special_style';

/* Per-fighter curated one-button strings. Notation must exist in the
   fighter's moveset; resolveSpecial() falls back gracefully. */
export const SPECIAL_STRINGS = {
  // [button1, button2, button3, button4]
  pantera:  ['1', '2', '2,1', '1+2'],
  demonio:  ['1', '2', '1', '1+2'],
  dorowani: ['1', '2', '1', '2,1'],
  skull:    ['1', '2', '2,1', '1+2'],
  phantom:  ['1', '2', '1', '2,1'],
  diablo:   ['1', '2', '2,1', '1+2'],
};
const _fallback = ['1', '2', '3', '4'];

export function specialStringsFor(fighterId) {
  return SPECIAL_STRINGS[fighterId] || _fallback;
}

/* Map a raw button ('1'..'4') through Special Style. Returns the notation
   the game should fire, or the original button when disabled/unknown. */
export function mapSpecialInput(fighterId, button, enabled) {
  if (!enabled) return button;
  if (!['1', '2', '3', '4'].includes(button)) return button; // throws/motions stay manual
  const table = specialStringsFor(fighterId);
  return table[Number(button) - 1] || button;
}

export function isSpecialStyleOn(player = 'p1') {
  try {
    if (typeof localStorage !== 'undefined') return localStorage.getItem(SPECIAL_STYLE_FLAG + ':' + player) === '1';
  } catch {}
  return !!_memFlag[player];
}
const _memFlag = {};
export function setSpecialStyle(player, on) {
  _memFlag[player] = !!on;
  try { if (typeof localStorage !== 'undefined') localStorage.setItem(SPECIAL_STYLE_FLAG + ':' + player, on ? '1' : '0'); } catch {}
}

/* HUD badge text for the versus HUD. */
export function specialStyleBadge(player, fighterId) {
  return isSpecialStyleOn(player) ? '✦ GUIDED HANDS' : '';
}
