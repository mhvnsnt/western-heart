/* ============================================================
   WESTERN HEART — Soul-Spirit Toggle (Nine Souls redesign)
   Owner directive 2026-10-22 ~23:02 CDT (refined ~23:03 CDT).

   The seven vesseled souls (RIN, BYOU, TOU, SHA, KAI, JIN, RETSU)
   are OFF the character-select grid as standalone fighters; only
   ZEN and GYOU (the unvesseled souls) stay selectable. In their
   place every fighter gets a TERTIARY soul-spirit toggle on the
   select screen — separate from the attire ladder:

     • ON/OFF switch for a soul spirit floating behind the fighter
     • Pick any of the nine souls while ON
     • Picking the soul that vessels INTO the chosen fighter
       (RIN on Demonio, BYOU on Zui, TOU on Pantera, SHA on
       Saku Ra / Kinpo / Awa Pop, KAI on King Tyrant / Star,
       JIN on Phantom, RETSU on Skull) EMPOWERS them (gameplay buff)

   The owner makes the spirit versions themselves — this module
   exposes the ATTACH POINT (fighter.soulSpirit) and renders a
   clearly-marked placeholder aura until the owner's spirit models
   land. No AI-generated stand-in spirit models, per the directive.

   Phonetic spellings from the owner's voice note, kept for the
   record: "Ren"=RIN, "Bayu"=BYOU, "two"=TOU, "Shaw"=SHA,
   "Sakura"=Saku Ra, "Gaiu"=GYOU.

   Distinct from:
     • SOUL KINDLE (soul-kindle.js) — T7 ki-charge port, the
       vessel focusing its OWN soul fragment's nature.
     • SOUL SURGE (canon Nine-Soul Meter) — channeling one of the
       OTHER eight souls for ten seconds mid-fight.
     • SOUL URGE (owner-locked 2026-10-22) — T8 Heat renamed.
   ============================================================ */

/* The nine souls, canon order (CANON.md §4). `vessels` are roster ids;
   ZEN and GYOU are unvesseled (selectable spirit fighters instead).
   JIN's roster key is 'jin_soul' everywhere except the select grid,
   where 'Jin' would collide with Jin Kazama confusion (EM-Jin law). */
export const NINE_SOULS = [
  { id: 'rin',      name: 'RIN',   kanji: '凛', nature: 'Dignified, cold, self-possessed', vessels: ['demonio'],                 color: 0x9fd8ff },
  { id: 'byou',     name: 'BYOU',  kanji: '病', nature: 'Sickness. Moves wrong. Unreadable', vessels: ['zui'],                     color: 0x8a9a3a },
  { id: 'tou',      name: 'TOU',   kanji: '闘', nature: 'Battle itself',                     vessels: ['pantera'],                 color: 0xff5a2a },
  { id: 'sha',      name: 'SHA',   kanji: '沙', nature: 'Sand. Flows, erodes, surrounds',    vessels: ['sakura', 'kinpo', 'awapop'], color: 0xd8b46b },
  { id: 'kai',      name: 'KAI',   kanji: '海', nature: 'The sea. Rhythmic, unstoppable',    vessels: ['kingtyrant', 'star'],     color: 0x3aa8cc },
  { id: 'jin_soul', name: 'JIN',   kanji: '刃', nature: 'The blade. Precise, ritual',        vessels: ['phantom'],                 color: 0xc0c8ff },
  { id: 'retsu',    name: 'RETSU', kanji: '烈', nature: 'Violence. Pure destructive force',  vessels: ['skull'],                   color: 0xff2a2a },
  { id: 'zen',      name: 'ZEN',   kanji: '禅', nature: 'Stillness. Unvesseled',             vessels: [],                          color: 0xe8e8e8 },
  { id: 'gyou',     name: 'GYOU',  kanji: '行', nature: 'Motion itself. Unvesseled',         vessels: [],                          color: 0x3aff8a },
];

/* Souls hidden from the select grid as standalone cards (the seven
   vesseled). ZEN and GYOU are NOT here — they stay selectable. */
export const VESSELED_SOUL_IDS = ['rin', 'byou', 'tou', 'sha', 'kai', 'jin_soul', 'retsu'];

export function soulById(id) {
  return NINE_SOULS.find((s) => s.id === id) || null;
}

/* One side's pick on the select screen. */
export const SOUL_SPIRIT_OFF = { enabled: false, soulId: null };
export function newSoulSpiritPick() {
  return { enabled: false, soulId: null };
}

/* True when the chosen fighter is a vessel of the picked soul.
   Non-vessel picks still show the spirit — they just don't empower. */
export function vesselMatch(fighterId, soulId) {
  const s = soulById(soulId);
  if (!s || !fighterId) return false;
  return s.vessels.includes(fighterId);
}

/* Empowerment buff for a MATCHING vessel+soul pick (owner: "it
   empowers them more or something like that"). Values are the
   v1 spec — owner-tunable, like every other fight number.
   power: damage dealt scales by attacker.stats.power (fighter.js).
   meterMult: soul-meter gain (Nine-Soul Meter / Surge charge rate). */
export const SOUL_MATCH_BUFF = {
  powerMult: 1.10,    // +10% damage on a vessel match
  defenseMult: 1.05,  // +5% defense — the soul shields its vessel
  meterMult: 1.25,    // +25% soul-meter gain — the soul feeds its vessel
};

/* Apply a select-screen pick to a char entry (main.js startFight).
   Returns a shallow-copied entry with boosted stats and a
   `soulSpirit: { soulId, matched }` marker the fight render reads.
   Pure — safe to call for CPU sides with a null pick (no-op). */
export function applySoulSpirit(charEntry, pick) {
  if (!charEntry || !pick || !pick.enabled || !pick.soulId) return charEntry;
  const soul = soulById(pick.soulId);
  if (!soul) return charEntry;
  const matched = vesselMatch(charEntry.id, pick.soulId);
  const out = { ...charEntry, soulSpirit: { soulId: pick.soulId, matched } };
  if (matched) {
    const s = { ...(charEntry.stats || {}) };
    if (typeof s.power === 'number') s.power *= SOUL_MATCH_BUFF.powerMult;
    if (typeof s.defense === 'number') s.defense *= SOUL_MATCH_BUFF.defenseMult;
    out.stats = s;
    out.soulMeterMult = (charEntry.soulMeterMult || 1) * SOUL_MATCH_BUFF.meterMult;
  }
  return out;
}

/* UI label for the select-screen toggle. */
export function soulSpiritLabel(pick) {
  if (!pick || !pick.enabled || !pick.soulId) return 'SOUL SPIRIT: OFF';
  const s = soulById(pick.soulId);
  return s ? `SOUL SPIRIT: ${s.name} ${s.kanji}` : 'SOUL SPIRIT: OFF';
}
