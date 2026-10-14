/* ============================================================
   WESTERN HEART — Roster (playable build v1)
   Two souls. The rest of the 28 wait in the dark.

   PANTERA — colors, stats and Soul Surge straight from
   prototype/fighters/pantera.json (purple #6B2D8F, black #1a1a1a,
   red trim #CC0000; Grappler archetype).

   DEMONIO — ROSTER.md lists him ("The Demon Soul", Jin-style
   Mishima karate, precise fundamental "honest" style) but gives
   NO stats or colors, so this build assigns balanced-attacker
   numbers and a cold blue-white palette. Tune later.
   ============================================================ */
export const ROSTER = [
  {
    id: 'pantera', name: 'PANTERA', style: 'Grappler',
    soul: 'Tou — the battle itself',
    colors: { suit: 0x6b2d8f, trim: 0xcc0000 },
    bodyScale: 1.05,
    stats: { speed: 4.0, jump: 6.8, power: 1.3, defense: 1.2 },
    ai: { aggression: 0.85, grabBias: 0.45, reaction: 0.55 },
    surge: { name: "PANTHER'S WRATH", color: 0x8b2bd8, accent: 0xff2222 },
  },
  {
    id: 'demonio', name: 'DEMONIO', style: 'Mishima Karate',
    soul: 'The Demon Soul',
    colors: { suit: 0x1a3a6b, trim: 0x9fd8ff },
    bodyScale: 1.0,
    stats: { speed: 4.8, jump: 7.6, power: 1.05, defense: 1.0 },
    ai: { aggression: 0.6, grabBias: 0.05, reaction: 0.6 },
    surge: { name: 'COLD FLAME', color: 0x9fd8ff, accent: 0xffffff },
  },
];

export function getCharacter(id) {
  return ROSTER.find(c => c.id === id) || ROSTER[0];
}
