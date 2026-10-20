/* ============================================================
   WESTERN HEART — Full Roster (36 named fighters)
   Every fighter traces to a real Tekken/model source.
   Models wired from teardown extractions; stats from CANON.md
   and ROSTER.md. No invented fighters.
   ============================================================ */

export const FULL_ROSTER = [
  // ——— THE NINE SOULS ———
  { id: 'rin', name: 'RIN', title: 'The Protagonist Soul', base: 'Jin Kazama', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a3a6b, trim: 0x9fd8ff }, style: 'Mishima Karate', archetype: 'Balanced' },
  { id: 'byou', name: 'BYOU', title: 'The Sick Soul', base: 'Lei Wulong', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x4a5a1a, trim: 0x8a9a3a }, style: 'Five Animals', archetype: 'Trickster' },
  { id: 'tou', name: 'TOU', title: 'The Fighting Soul', base: 'Paul Phoenix', moveset: 'heihachi', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x8a1a1a, trim: 0xcc4400 }, style: 'Power Karate', archetype: 'Power' },
  { id: 'sha', name: 'SHA', title: 'The Sand Soul', base: 'Xiaoyu', moveset: 'xiaoyu', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xc2a36b, trim: 0x8a6a3a }, style: 'Hakkesho', archetype: 'Evasive' },
  { id: 'kai', name: 'KAI', title: 'The Sea Soul', base: 'Eddy Gordo', moveset: 'demonio', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x1a4a6b, trim: 0x3a8acc }, style: 'Capoeira', archetype: 'Rushdown' },
  { id: 'jin_soul', name: 'JIN', title: 'The Blade Soul', base: 'Yoshimitsu', moveset: 'yoshimitsu', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a2a3a, trim: 0x8a2be2 }, style: 'Sword Style', archetype: 'Tricky' },
  { id: 'retsu', name: 'RETSU', title: 'The Violent Soul', base: 'Bryan Fury', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x3a1a1a, trim: 0xcc2222 }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'zen', name: 'ZEN', title: 'The Still Soul', base: 'Heihachi', moveset: 'heihachi', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xd0d0d0, trim: 0x8a8a8a }, style: 'Mishima', archetype: 'Defensive' },
  { id: 'gyou', name: 'GYOU', title: 'The Moving Soul', base: 'Hwoarang', moveset: 'demonio', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x1a5a3a, trim: 0x3acc6a }, style: 'Tae Kwon Do', archetype: 'Pressure' },

  // ——— MAIN ROSTER ———
  { id: 'pantera', name: 'PANTERA', title: 'The Panther Soul', base: 'King', moveset: 'king', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x6b2d8f, trim: 0xcc0000 }, style: 'Grappler',
    surge: { name: "PANTHER'S WRATH", color: 0x8b2bd8, accent: 0xff2222 },
    stats: { speed: 4.0, jump: 6.8, power: 1.3, defense: 1.2 },
    ai: { aggression: 0.85, grabBias: 0.45, reaction: 0.55 } },
  { id: 'demonio', name: 'DEMONIO', title: 'The Demon Soul', base: 'Jin Kazama', moveset: 'demonio', model: 'demonio-a1', tintStrength: 0.25,
    colors: { suit: 0x1a3a6b, trim: 0x9fd8ff }, style: 'Mishima Karate',
    surge: { name: 'COLD FLAME', color: 0x9fd8ff, accent: 0xffffff },
    // Attire 1 = Tripo unwinged demon (owner 2026-10-19). Three forms, transform both directions (Roshi-style).
    // TRANSFORM touch button = up, tap while crouching = down (rare). Full meter required.
    forms: {
      'demonio-a1': {
        up: { target: 'demonio-winged', label: 'DEVIL ASCENSION', powerMult: 1.5, speedMult: 1.05, defenseMult: 1.2, bodyScale: 1.22, moveset: 'demonio-winged' },
        down: { target: 'demonio-human', label: 'DEPOWER', powerMult: 0.7, speedMult: 1.1, defenseMult: 0.9, bodyScale: 0.95, moveset: 'demonio' },
      },
      'demonio-winged': {
        down: { target: 'demonio-a1', label: 'REVERT', powerMult: 0.67, speedMult: 0.95, defenseMult: 0.83, bodyScale: 0.82, moveset: 'demonio' },
      },
      'demonio-human': {
        up: { target: 'demonio-a1', label: 'REPOWER', powerMult: 1.43, speedMult: 0.91, defenseMult: 1.11, bodyScale: 1.05, moveset: 'demonio' },
      },
    },
    stats: { speed: 4.8, jump: 7.6, power: 1.05, defense: 1.0 },
    ai: { aggression: 0.6, grabBias: 0.05, reaction: 0.6 } },
  { id: 'phantom', name: 'PHANTOM', title: 'The Ghost Blade Soul', base: 'Yoshimitsu', moveset: 'yoshimitsu', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a1a2a, trim: 0x00ffcc }, style: 'Sword Style', archetype: 'Tricky' },
  { id: 'diablo', name: 'DIABLO', title: 'The Devil Soul', base: 'Heihachi', moveset: 'heihachi', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x5a0a0a, trim: 0xff4400 }, style: 'Mishima', archetype: 'Boss' },
  { id: 'skull', name: 'SKULL', title: 'The Punisher Soul', base: 'Bryan Fury', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x2a2a2a, trim: 0xcccccc }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'samura1', name: 'SAM-UR-A1', title: 'The Mech Soul', base: 'Jack-7', moveset: 'gunjack', model: 'sam-ur-a1', tintStrength: 0.25,
    colors: { suit: 0x3a3a4a, trim: 0x00aaff }, style: 'Power Robot', archetype: 'Zoner' },
    // Attire 1 = Tripo pull 2026-10-19 (owner: 'SAM-UR-A1 model attire 1'). Former pantera base retired to docs.
  { id: 'sakura', name: 'SAKU RA', title: 'The Idol Soul', base: 'Xiaoyu', moveset: 'xiaoyu', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xff6b9d, trim: 0xffd700 }, style: 'Hakkesho', archetype: 'Evasive' },

  // ——— BONUS ROSTER ———
  { id: 'zui', name: 'ZUI', title: 'Drunken Master', base: 'Steve Fox', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a4a2a, trim: 0x6acc3a }, style: 'Boxing/Drunken', archetype: 'Tricky' },
  { id: 'kinpo', name: 'KINPO', title: 'Splinter of SHA', base: 'Asuka', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xd44d8a, trim: 0xffd700 }, style: 'Kazama Style', archetype: 'Counter' },
  { id: 'waterfall', name: 'WATERFALL', title: "Grief of Nine", base: 'Josie', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x3a6acc, trim: 0x9fd8ff }, style: 'Eskrima', archetype: 'Rushdown' },
  { id: 'kingtyrant', name: 'KING TYRANT', title: 'Showman King', base: 'Eddy Gordo', moveset: 'xiaoyu', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x8a6a1a, trim: 0xffd700 }, style: 'Capoeira', archetype: 'Showman' },
  { id: 'burger', name: 'BURGER', title: 'Hunger is a Curse', base: 'Bob', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0xcc8833, trim: 0xff4400 }, style: 'Sumo/Brawler', archetype: 'Power',
    // Burger demon transformation chain (owner 2026-10-19): Kusaregedo kit per form.
    // Chain: base -> speed-demon -> the-mouth -> demon (final). Demon form gets FULL kit
    // + mix of smaller forms' abilities + exclusives. Extensible for new forms.
    forms: {
      'pantera': {
        up: { target: 'burger-speed-demon', label: 'SPEED DEMON', powerMult: 1.1, speedMult: 1.3, defenseMult: 0.9, moveset: 'burger-speed-demon' },
      },
      'burger-speed-demon': {
        up: { target: 'burger-the-mouth', label: 'THE MOUTH', powerMult: 1.18, speedMult: 0.65, defenseMult: 1.22, bodyScale: 1.1, moveset: 'burger-the-mouth' },
        down: { target: 'pantera', label: 'POWER DOWN', powerMult: 0.91, speedMult: 0.77, defenseMult: 1.11, moveset: 'bryan' },
      },
      'burger-the-mouth': {
        up: { target: 'burger-demon', label: 'DEMON ASCENSION', powerMult: 1.23, speedMult: 1.06, defenseMult: 1.18, bodyScale: 1.14, moveset: 'burger-demon' },
        down: { target: 'burger-speed-demon', label: 'POWER DOWN', powerMult: 0.85, speedMult: 1.54, defenseMult: 0.82, bodyScale: 0.91, moveset: 'burger-speed-demon' },
      },
      'burger-demon': {
        down: { target: 'burger-the-mouth', label: 'POWER DOWN', powerMult: 0.81, speedMult: 0.94, defenseMult: 0.85, bodyScale: 0.88, moveset: 'burger-the-mouth' },
      },
    } },
  { id: 'awapop', name: 'AWA POP', title: 'Bubbles', base: 'Nina', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xff9dcc, trim: 0xffffff }, style: 'Assassin', archetype: 'Rushdown' },
  { id: 'scimitar', name: 'SCIMITAR', title: 'Desert Blade', base: 'Shaheen', moveset: 'demonio', model: 'scimitar', tintStrength: 0.6,
    colors: { suit: 0x2a2a3a, trim: 0xc2a36b }, style: 'Military', archetype: 'Balanced' },
  { id: 'purplerain', name: 'PURPLE RAIN', title: 'MJ x Prince x Pimp', base: 'Lee', moveset: 'demonio', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x6b2d8f, trim: 0xff00ff }, style: 'Martial Arts', archetype: 'Stylish' },
  { id: 'nightwolf', name: 'NIGHTWOLF', title: 'Storm Shadow', base: 'Julia', moveset: 'xiaoyu', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x1a3a5a, trim: 0x6accff }, style: 'Xinyi Liuhe', archetype: 'Balanced' },
  { id: 'dio', name: 'DIO', title: 'Raging Demon', base: 'Akuma', moveset: 'heihachi', model: 'dio', tintStrength: 0.6,
    colors: { suit: 0x1a1a1a, trim: 0xff0000 }, style: 'Satsui no Hado', archetype: 'Shoto' },
  { id: 'cyborgx', name: 'CYBORG X', title: 'GYOU Splinter', base: 'Alisa', moveset: 'gunjack', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0xcccccc, trim: 0x00ffcc }, style: 'Robot Combat', archetype: 'Zoner' },
  { id: 'michiko', name: 'MICHIKO', title: 'Savate Queen', base: 'Katarina', moveset: 'demonio', model: 'michiko', tintStrength: 0.6,
    colors: { suit: 0x8a1a4a, trim: 0xff6b9d }, style: 'Savate', archetype: 'Rushdown' },
  { id: 'star', name: 'STAR', title: 'KAI Splinter', base: 'Christie', moveset: 'xiaoyu', model: 'star', tintStrength: 0.25,
    colors: { suit: 0xffd700, trim: 0xff6b00 }, style: 'Capoeira', archetype: 'Rushdown' },
  { id: 'torch', name: 'TORCH', title: 'Fire Assassin', base: 'Anna', moveset: 'demonio', model: 'torch', tintStrength: 0.6,
    colors: { suit: 0x8a1a1a, trim: 0xff8800 }, style: 'Assassin', archetype: 'Tricky' },
  { id: 'bruno', name: 'BRUNO', title: 'Matador', base: 'Miguel', moveset: 'bryan', model: 'bruno', tintStrength: 0.25,
    colors: { suit: 0x5a1a1a, trim: 0xcc3333 }, style: 'Brawler', archetype: 'Power' },
  { id: 'negativo', name: 'N3GΔTIV0', title: 'Galactic Bounty Hunter', base: 'Negan', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x0a0a0a, trim: 0x00ff00 }, style: 'Brawler', archetype: 'Intimidation' },
  { id: 'thor', name: 'THOR', title: 'Norse God', base: 'Ganryu', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x4a3a2a, trim: 0xffd700 }, style: 'Sumo', archetype: 'Power' },
  { id: 'yukihyo', name: 'YUKIHYŌ', title: 'Snow Leopard Ninja', base: 'Armor King', moveset: 'king', model: 'yukihyo', tintStrength: 0.25,
    colors: { suit: 0xd0d0d0, trim: 0x6accff }, style: 'Grappler', archetype: 'Ninja' },
  { id: 'slice', name: 'SLICE', title: 'Maniacal Agent', base: 'Dragunov', moveset: 'bryan', model: 'steve-fox', tintStrength: 0.6,
    colors: { suit: 0x2a2a2a, trim: 0xcc0000 }, style: 'Commando Sambo', archetype: 'Grappler' },
  { id: 'docfrank', name: 'DOC FRANK', title: 'Father of Machines', base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-machine-shop', tintStrength: 0.6,
    colors: { suit: 0x6a6a7a, trim: 0x00ffcc }, style: 'Inventor', archetype: 'Tricky',
    // Mid-match Roshi-style transformation (owner 2026-10-19):
    // old-man Attire 1 -> bigger Tripo form (2c6cff79, the true transform target). TRANSFORM touch button.
    transform: { targetModel: 'doc-frank-big', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 } },
  // ——— RESKIN WAVE (2026-10-19): first custom attires as selectable fighters ———
  { id: 'demonio-bloodline-ember', name: 'DEMONIO', title: 'Bloodline Ember', base: 'Jin Kazama', moveset: 'demonio', model: 'demonio-bloodline-ember', tintStrength: 0.25,
    colors: { suit: 0x8a1a0a, trim: 0xff4400 }, style: 'Mishima Karate', archetype: 'Balanced' },
  // ——— WAVE 2 (2026-10-19): Demonio forms (dual access) + Doc Frank attires ———
  { id: 'demonio-winged', name: 'DEMONIO', title: 'Devil Ascendant', base: 'Jin Kazama', moveset: 'demonio-winged', model: 'demonio-winged', tintStrength: 0.25,
    colors: { suit: 0x2a0a2a, trim: 0xff00ff }, style: 'Devil Mishima', archetype: 'Boss',
    forms: {
      'demonio-winged': {
        down: { target: 'demonio-a1', label: 'REVERT', powerMult: 0.67, speedMult: 0.95, defenseMult: 0.83, bodyScale: 0.82, moveset: 'demonio' },
      },
    } },
  { id: 'demonio-human', name: 'DEMONIO', title: 'The Possessed', base: 'Jin Kazama', moveset: 'demonio', model: 'demonio-human', tintStrength: 0.25,
    colors: { suit: 0x3a3a3a, trim: 0x9fd8ff }, style: 'Mishima Karate', archetype: 'Balanced',
    forms: {
      'demonio-human': {
        up: { target: 'demonio-a1', label: 'REPOWER', powerMult: 1.43, speedMult: 0.91, defenseMult: 1.11, bodyScale: 1.05, moveset: 'demonio' },
      },
    } },
  { id: 'doc-frank-wowomomo', name: 'DOC FRANK', title: 'Wowomomo', base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-wowomomo', tintStrength: 0.25,
    colors: { suit: 0x4a4a5a, trim: 0xff8800 }, style: 'Inventor', archetype: 'Tricky',
    // Attire 2 "Wowomomo" (owner 2026-10-19): Dr gero meets mojo Jojo meets bosconovitch meets Dr wierd.
    transform: { targetModel: 'doc-frank-wowomomo-big', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 } },
  { id: 'doc-frank-hood', name: 'DOC FRANK', title: 'Hood Scientist', base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-hood', tintStrength: 0.25,
    colors: { suit: 0x2a2a3a, trim: 0xcccccc }, style: 'Inventor', archetype: 'Tricky',
    // Attire 3 "Hood scientist" (owner 2026-10-19): old mob boss scientist, club night.
    transform: { targetModel: 'doc-frank-hood-big', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 } },
  { id: 'doc-frank-frankenstein', name: 'DOC FRANK', title: "Frankenstein's Cyborg", base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-frankenstein', tintStrength: 0.25,
    colors: { suit: 0x3a4a3a, trim: 0x88cc88 }, style: 'Inventor', archetype: 'Tricky',
    // Attire 4 "Frankenstein's Cyborg" (owner 2026-10-19): two-form transform attire.
    transform: { targetModel: 'doc-frank-frankenstein-big', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 } },
  { id: 'doc-frank-machine-shop', name: 'DOC FRANK', title: 'Machine Shop', base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-machine-shop', tintStrength: 0.25,
    colors: { suit: 0x4a4a5a, trim: 0xff8800 }, style: 'Inventor', archetype: 'Tricky' },
  { id: 'baek-master-white', name: 'BAEK', title: "Master's White", base: 'Baek', moveset: 'bryan', model: 'baek-master-white', tintStrength: 0.25,
    colors: { suit: 0xf0f0f0, trim: 0x8a1a1a }, style: 'Tae Kwon Do', archetype: 'Pressure' },
  { id: 'mariposa-monarch', name: 'MARIPOSA', title: 'Monarch', base: 'Zafina', moveset: 'xiaoyu', model: 'mariposa-monarch', tintStrength: 0.25,
    colors: { suit: 0x2a1a3a, trim: 0xff8800 }, style: 'Azazel Arts', archetype: 'Tricky' },
  { id: 'dxmmii-patchwork', name: 'DXMMII', title: 'Patchwork DJ', base: 'Mokujin', moveset: 'demonio', model: 'dxmmii-patchwork', tintStrength: 0.25,
    colors: { suit: 0x3a2a5a, trim: 0x00ffcc }, style: 'Mimicry', archetype: 'Trickster' },
  // Sketchfab intake (owner 2026-10-19): working names, WH names pending owner pick.
  // Licenses: Zangief CC-BY (johnny136), Blanka Free Standard (allanromanreyes),
  // Vega CC-BY (pierodsoto01), Iori CC-BY (0xo), Armor King CC-BY (theamazingdonovan207).
  { id: 'zangief', name: 'ZANGIEF', title: 'The Red Cyclone', base: 'Zangief', moveset: 'zangief', model: 'zangief', tintStrength: 0.25,
    colors: { suit: 0x8a1a1a, trim: 0x000000 }, style: 'Grappler', archetype: 'Power',
    surge: { name: "CYCLONE'S WRATH", color: 0xcc2222, accent: 0xff8800 } },
  { id: 'blanka', name: 'BLANKA', title: 'The Beast', base: 'Blanka', moveset: 'blanka', model: 'blanka', tintStrength: 0.25,
    colors: { suit: 0x2a8a2a, trim: 0xff8800 }, style: 'Beast', archetype: 'Rushdown',
    surge: { name: 'ELECTRIC STORM', color: 0x88ccff, accent: 0xffff00 } },
  { id: 'vega', name: 'VEGA', title: 'The Claw', base: 'Vega', moveset: 'vega', model: 'vega', tintStrength: 0.25,
    colors: { suit: 0x8a2a6b, trim: 0xffd700 }, style: 'Claw', archetype: 'Evasive',
    surge: { name: "MATADOR'S FURY", color: 0xcc2288, accent: 0xffffff } },
  { id: 'iori', name: 'IORI', title: 'The Flame', base: 'Iori Yagami', moveset: 'iori', model: 'iori', tintStrength: 0.25,
    colors: { suit: 0x6b1a8a, trim: 0xff2222 }, style: 'Flames', archetype: 'Rushdown',
    surge: { name: 'CRIMSON INFERNO', color: 0xaa22ff, accent: 0xff4400 } },
  { id: 'armor-king', name: 'ARMOR KING', title: 'The Chain', base: 'Armor King', moveset: 'armor-king', model: 'armor-king', tintStrength: 0.25,
    colors: { suit: 0x1a1a2a, trim: 0xccaa00 }, style: 'Grappler', archetype: 'Power',
    surge: { name: "JAGUAR'S GRIP", color: 0x888800, accent: 0xffcc00 } },
  // Custom fighters (owner 2026-10-19): KRONOS + DEATHFANG + Ryuji/Rock hybrid.
  { id: 'kronos', name: 'KRONOS', title: 'The Titan Cyclone', base: 'Zangief + Golem', moveset: 'kronos', model: 'kronos', tintStrength: 0.25,
    colors: { suit: 0x8a1a1a, trim: 0xccaa00 }, style: 'Grappler/Wrestler', archetype: 'Power',
    surge: { name: "TITAN'S WRATH", color: 0xcc2222, accent: 0xffd700 },
    stats: { speed: 3.2, jump: 5.5, power: 1.5, defense: 1.35 },
    ai: { aggression: 0.7, grabBias: 0.6, reaction: 0.5 },
    // Attire 2 "TimberWolf" (Wolverine inspired) — selectable via attires list.
    attires: ['kronos', 'kronos-attire2'] },
  { id: 'kronos-attire2', name: 'KRONOS', title: 'TimberWolf', base: 'Zangief + Golem', moveset: 'kronos', model: 'kronos-attire2', tintStrength: 0.25,
    colors: { suit: 0x3a4a5a, trim: 0xffcc00 }, style: 'Grappler/Wrestler', archetype: 'Power',
    surge: { name: "TIMBERWOLF RAGE", color: 0x4466aa, accent: 0xffcc00 },
    stats: { speed: 3.6, jump: 6.0, power: 1.45, defense: 1.3 },
    ai: { aggression: 0.8, grabBias: 0.55, reaction: 0.55 } },
  // DEATHFANG (owner 2026-10-19): proprietary character based on Iori Yagami — keeps Iori's
  // moves, stance and animations. Prisoner/slave to his own grief and emotions: chained and
  // shackled, emo styling, NO FUTURE face tattoo (Soul Eater). Transforms into a chained
  // prisoner werewolf (attire 2). (Merged entry: canon fields from the reskin lane,
  // stats/ai from the parallel wiring lane.)
  { id: 'deathfang', name: 'DEATHFANG', title: 'The Chained Prisoner', base: 'Iori Yagami', moveset: 'deathfang', model: 'deathfang', tintStrength: 0.25,
    colors: { suit: 0x0a0a0f, trim: 0x8a0f1a }, style: 'Grief Flames', archetype: 'Rushdown',
    surge: { name: 'NO FUTURE', color: 0x5a0f8a, accent: 0xff2222 },
    // Werewolf transform (owner 2026-10-20): Attire 2 = his real Tripo werewolf model
    // (b4094ecf). TRANSFORM touch button + full nine-soul meter, both directions
    // (tap while crouching = revert). The wolf keeps Iori's stance + locomotion and the
    // FULL DEATHFANG kit; beast flavor is attack-only (deathfang-werewolf.json mix-ins).
    forms: {
      'deathfang': {
        up: { target: 'deathfang-werewolf', label: 'WEREWOLF UNLEASHED', powerMult: 1.35, speedMult: 1.08, defenseMult: 1.15, bodyScale: 1.12, moveset: 'deathfang-werewolf' },
      },
      'deathfang-werewolf': {
        down: { target: 'deathfang', label: 'CHAINED AGAIN', powerMult: 0.74, speedMult: 0.93, defenseMult: 0.87, bodyScale: 0.89, moveset: 'deathfang' },
      },
    },
    stats: { speed: 5.2, jump: 7.8, power: 1.15, defense: 0.95 },
    ai: { aggression: 0.85, grabBias: 0.3, reaction: 0.6 } },
  { id: 'ryuji', name: 'RYUJI', title: 'The Wicked Heretic', base: 'Ryuji Yamazaki', moveset: 'ryuji', model: 'steve-fox', tintStrength: 0.25,
    colors: { suit: 0x111111, trim: 0xd8b25a }, style: 'Hebi Tsukai / Wrestling', archetype: 'Zoner/Grappler',
    surge: { name: 'SERPENT DRILL', color: 0x224411, accent: 0xffcc00 } },
  { id: 'ryuji-rock', name: 'RYUJI ROCK', title: 'The Obnoxious One', base: 'Ryuji Yamazaki + The Rock', moveset: 'ryuji-rock', model: 'ryuji-rock', tintStrength: 0.25,
    colors: { suit: 0x1a1a1a, trim: 0xffd700 }, style: 'Wrestler/Brawler', archetype: 'Power',
    surge: { name: "PEOPLE'S CHAMPION", color: 0xffd700, accent: 0xffffff },
    stats: { speed: 4.0, jump: 6.5, power: 1.35, defense: 1.2 },
    ai: { aggression: 0.75, grabBias: 0.5, reaction: 0.55 } },
  { id: 'koreshi', name: 'KORESHI', title: 'The Shadow Ninja', base: 'Kakashi + Super Saiyan', moveset: 'koreshi', model: 'koreshi', tintStrength: 0.25,
    colors: { suit: 0x2a3a4a, trim: 0xcc2222 }, style: 'Ninja/Samurai', archetype: 'Trickster',
    surge: { name: 'SHARINGAN AWAKENING', color: 0xcc2222, accent: 0xffffff },
    stats: { speed: 5.5, jump: 8.0, power: 1.1, defense: 0.95 },
    ai: { aggression: 0.7, grabBias: 0.25, reaction: 0.7 } },
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
