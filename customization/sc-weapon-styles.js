/* ============================================================
   WESTERN HEART — Soulcalibur weapon/style creation wiring
   From the soulcalibur-2 / soulcalibur-6 teardowns: SC's
   Create-a-Soul proves "any style on any body" — the WEAPON
   DISCIPLINE determines the fighting style. This module wires
   that model into the WH creation suite and the game:

   - Suite side: the WEAPON tab reads customization/data/sc-weapons.json
     (disciplines + modifiers). Picking a weapon writes
     `F.weapon = { id, ...modifiers }` onto the suite fighter JSON.
   - Game side: applyWeaponStyle() maps the weapon onto a roster-
     compatible fighter (custom-fighter.js): sets style/archetype,
     applies reach/damage/speed multipliers, keeps Tekken inputs
     as the language (INPUT-TO-MOVE FIDELITY LAW untouched).
   ============================================================ */

export const SC_WEAPONS_URL = 'customization/data/sc-weapons.json';

let _cache = null;
export async function loadWeaponDisciplines() {
  if (_cache) return _cache;
  const res = await fetch(SC_WEAPONS_URL);
  const data = await res.json();
  _cache = data.disciplines || [];
  return _cache;
}

export function getDiscipline(id, list) {
  const arr = list || _cache || [];
  return arr.find((d) => d.id === id) || arr.find((d) => d.id === 'unarmed') || null;
}

/* Suite: attach a weapon pick to the suite fighter JSON. */
export function setFighterWeapon(F, disciplineId, list) {
  const d = getDiscipline(disciplineId, list);
  if (!d) return F;
  F.weapon = {
    id: d.id, name: d.name, style: d.style, archetype: d.archetype,
    reach: d.reach, damage: d.damage, speed: d.speed,
    moveset_base: d.moveset_base,
  };
  // The suite's fighting_style block follows the weapon's archetype.
  F.fighting_style = F.fighting_style || {};
  F.fighting_style.archetype = d.archetype;
  return F;
}

/* Game: apply the suite weapon to a roster-compatible fighter object.
   Multipliers are read live by the fight feel tuner (game.feel);
   we stash them on fighter.weaponMods so nothing else has to change. */
export function applyWeaponStyle(rosterFighter, weapon) {
  if (!rosterFighter || !weapon) return rosterFighter;
  rosterFighter.style = weapon.archetype || rosterFighter.style;
  if (weapon.moveset_base) rosterFighter.moveset = weapon.moveset_base;
  rosterFighter.weaponMods = {
    reach: weapon.reach ?? 1.0,
    damage: weapon.damage ?? 1.0,
    speed: weapon.speed ?? 1.0,
    name: weapon.name || 'Unarmed',
    style: weapon.style || '',
  };
  return rosterFighter;
}
