/* ============================================================
   WESTERN HEART — Full Roster (36 named fighters)
   Every fighter traces to a real Tekken/model source.
   Models wired from teardown extractions; stats from CANON.md
   and ROSTER.md. No invented fighters.
   ============================================================ */

export const FULL_ROSTER = [
  // ——— THE NINE SOULS ———
  { id: 'rin', name: 'RIN', title: 'The Protagonist Soul', base: 'Jin Kazama', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a3a6b, trim: 0x9fd8ff }, style: 'Mishima Karate', archetype: 'Balanced' },
  { id: 'byou', name: 'BYOU', title: 'The Sick Soul', base: 'Lei Wulong', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x4a5a1a, trim: 0x8a9a3a }, style: 'Five Animals', archetype: 'Trickster' },
  { id: 'tou', name: 'TOU', title: 'The Fighting Soul', base: 'Paul Phoenix', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x8a1a1a, trim: 0xcc4400 }, style: 'Power Karate', archetype: 'Power' },
  { id: 'sha', name: 'SHA', title: 'The Sand Soul', base: 'Xiaoyu', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xc2a36b, trim: 0x8a6a3a }, style: 'Hakkesho', archetype: 'Evasive' },
  { id: 'kai', name: 'KAI', title: 'The Sea Soul', base: 'Eddy Gordo', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x1a4a6b, trim: 0x3a8acc }, style: 'Capoeira', archetype: 'Rushdown' },
  { id: 'jin_soul', name: 'JIN', title: 'The Blade Soul', base: 'Yoshimitsu', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a2a3a, trim: 0x8a2be2 }, style: 'Sword Style', archetype: 'Tricky' },
  { id: 'retsu', name: 'RETSU', title: 'The Violent Soul', base: 'Bryan Fury', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x3a1a1a, trim: 0xcc2222 }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'zen', name: 'ZEN', title: 'The Still Soul', base: 'Heihachi', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xd0d0d0, trim: 0x8a8a8a }, style: 'Mishima', archetype: 'Defensive' },
  { id: 'gyou', name: 'GYOU', title: 'The Moving Soul', base: 'Hwoarang', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x1a5a3a, trim: 0x3acc6a }, style: 'Tae Kwon Do', archetype: 'Pressure' },

  // ——— MAIN ROSTER ———
  { id: 'pantera', name: 'PANTERA', title: 'The Panther Soul', base: 'King', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x6b2d8f, trim: 0xcc0000 }, style: 'Grappler',
    surge: { name: "PANTHER'S WRATH", color: 0x8b2bd8, accent: 0xff2222 },
    stats: { speed: 4.0, jump: 6.8, power: 1.3, defense: 1.2 },
    ai: { aggression: 0.85, grabBias: 0.45, reaction: 0.55 } },
  { id: 'demonio', name: 'DEMONIO', title: 'The Demon Soul', base: 'Jin Kazama', moveset: 'jin', model: 'jin', tintStrength: 0.6,
    colors: { suit: 0x1a3a6b, trim: 0x9fd8ff }, style: 'Mishima Karate',
    surge: { name: 'COLD FLAME', color: 0x9fd8ff, accent: 0xffffff },
    stats: { speed: 4.8, jump: 7.6, power: 1.05, defense: 1.0 },
    ai: { aggression: 0.6, grabBias: 0.05, reaction: 0.6 } },
  { id: 'phantom', name: 'PHANTOM', title: 'The Ghost Blade Soul', base: 'Yoshimitsu', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a1a2a, trim: 0x00ffcc }, style: 'Sword Style', archetype: 'Tricky' },
  { id: 'diablo', name: 'DIABLO', title: 'The Devil Soul', base: 'Heihachi', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x5a0a0a, trim: 0xff4400 }, style: 'Mishima', archetype: 'Boss' },
  { id: 'skull', name: 'SKULL', title: 'The Punisher Soul', base: 'Bryan Fury', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x2a2a2a, trim: 0xcccccc }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'samura1', name: 'SAM-UR-A1', title: 'The Mech Soul', base: 'Jack-7', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x3a3a4a, trim: 0x00aaff }, style: 'Power Robot', archetype: 'Zoner' },
  { id: 'sakura', name: 'SAKU RA', title: 'The Idol Soul', base: 'Xiaoyu', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xff6b9d, trim: 0xffd700 }, style: 'Hakkesho', archetype: 'Evasive' },

  // ——— BONUS ROSTER ———
  { id: 'zui', name: 'ZUI', title: 'Drunken Master', base: 'Steve Fox', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a4a2a, trim: 0x6acc3a }, style: 'Boxing/Drunken', archetype: 'Tricky' },
  { id: 'kinpo', name: 'KINPO', title: 'Splinter of SHA', base: 'Asuka', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xd44d8a, trim: 0xffd700 }, style: 'Kazama Style', archetype: 'Counter' },
  { id: 'waterfall', name: 'WATERFALL', title: "Grief of Nine", base: 'Josie', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x3a6acc, trim: 0x9fd8ff }, style: 'Eskrima', archetype: 'Rushdown' },
  { id: 'kingtyrant', name: 'KING TYRANT', title: 'Showman King', base: 'Eddy Gordo', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x8a6a1a, trim: 0xffd700 }, style: 'Capoeira', archetype: 'Showman' },
  { id: 'burger', name: 'BURGER', title: 'Hunger is a Curse', base: 'Bob', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0xcc8833, trim: 0xff4400 }, style: 'Sumo/Brawler', archetype: 'Power' },
  { id: 'awapop', name: 'AWA POP', title: 'Bubbles', base: 'Nina', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xff9dcc, trim: 0xffffff }, style: 'Assassin', archetype: 'Rushdown' },
  { id: 'scimitar', name: 'SCIMITAR', title: 'Desert Blade', base: 'Shaheen', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a2a3a, trim: 0xc2a36b }, style: 'Military', archetype: 'Balanced' },
  { id: 'purplerain', name: 'PURPLE RAIN', title: 'MJ x Prince x Pimp', base: 'Lee', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x6b2d8f, trim: 0xff00ff }, style: 'Martial Arts', archetype: 'Stylish' },
  { id: 'nightwolf', name: 'NIGHTWOLF', title: 'Storm Shadow', base: 'Julia', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a3a5a, trim: 0x6accff }, style: 'Xinyi Liuhe', archetype: 'Balanced' },
  { id: 'dio', name: 'DIO', title: 'Raging Demon', base: 'Akuma', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a1a1a, trim: 0xff0000 }, style: 'Satsui no Hado', archetype: 'Shoto' },
  { id: 'cyborgx', name: 'CYBORG X', title: 'GYOU Splinter', base: 'Alisa', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xcccccc, trim: 0x00ffcc }, style: 'Robot Combat', archetype: 'Zoner' },
  { id: 'michiko', name: 'MICHIKO', title: 'Savate Queen', base: 'Katarina', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x8a1a4a, trim: 0xff6b9d }, style: 'Savate', archetype: 'Rushdown' },
  { id: 'star', name: 'STAR', title: 'KAI Splinter', base: 'Christie', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0xffd700, trim: 0xff6b00 }, style: 'Capoeira', archetype: 'Rushdown' },
  { id: 'torch', name: 'TORCH', title: 'Fire Assassin', base: 'Anna', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x8a1a1a, trim: 0xff8800 }, style: 'Assassin', archetype: 'Tricky' },
  { id: 'bruno', name: 'BRUNO', title: 'Matador', base: 'Miguel', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x5a1a1a, trim: 0xcc3333 }, style: 'Brawler', archetype: 'Power' },
  { id: 'negativo', name: 'N3GΔTIV0', title: 'Galactic Bounty Hunter', base: 'Negan', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x0a0a0a, trim: 0x00ff00 }, style: 'Brawler', archetype: 'Intimidation' },
  { id: 'thor', name: 'THOR', title: 'Norse God', base: 'Ganryu', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x4a3a2a, trim: 0xffd700 }, style: 'Sumo', archetype: 'Power' },
  { id: 'yukihyo', name: 'YUKIHYŌ', title: 'Snow Leopard Ninja', base: 'Armor King', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0xd0d0d0, trim: 0x6accff }, style: 'Grappler', archetype: 'Ninja' },
  { id: 'slice', name: 'SLICE', title: 'Maniacal Agent', base: 'Dragunov', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a2a2a, trim: 0xcc0000 }, style: 'Commando Sambo', archetype: 'Grappler' },
  { id: 'docfrank', name: 'DOC FRANK', title: 'Father of Machines', base: 'Bosconovitch', moveset: 'jin', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x6a6a7a, trim: 0x00ffcc }, style: 'Inventor', archetype: 'Tricky' },
];

export function getFighter(id) {
  return FULL_ROSTER.find(f => f.id === id) || FULL_ROSTER[9]; // default Pantera
}

export function getRosterByTier() {
  return {
    souls: FULL_ROSTER.slice(0, 9),
    main: FULL_ROSTER.slice(9, 16),
    bonus: FULL_ROSTER.slice(16),
  };
}
