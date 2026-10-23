/* ============================================================
   WESTERN HEART — Full Roster (48 selectable fighters)
   Every fighter traces to a real Tekken/model source.
   Models wired from teardown extractions; stats from CANON.md
   and ROSTER.md. No invented fighters.
   Attire-variants ladder into their fighter's ATTIRE_VARIANTS
   (game/js/attires.js) and never stand alone as selectable cards
   (owner rule 2026-10-22).
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
  { id: 'retsu', name: 'RETSU', title: 'The Violent Soul', base: 'Bryan Fury', moveset: 'bryan', model: 'pantera', tintStrength: 0.25,
    colors: { suit: 0x3a1a1a, trim: 0xcc2222 }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'zen', name: 'ZEN', title: 'The Still Soul', base: 'Heihachi', moveset: 'heihachi', model: 'zen', tintStrength: 0.6,
    colors: { suit: 0xd0d0d0, trim: 0x8a8a8a }, style: 'Mishima', archetype: 'Defensive',
    // ZEN TRANSFORMATION MODES (owner canon 2026-10-21, roster/zen/CANON.md):
    // ALL of Zen's versions are modes WITHIN Attire 1 — not separate
    // attires. Spiritual/celestial class (Oversoul/Susanoo x JoJo Stand).
    // Chain: spirit body -> TENTACLE MODE (9460095d: the clothing tentacle
    // imagery becomes REAL tentacles busting out of him; NO Oversoul head;
    // his spirit entity rides higher + further back) -> OVERSOUL (2bbc8e88:
    // the spirit docks at the head position, TAKES THE HEAD'S PLACE, and
    // the combined form manifests; body tentacles stay imagery). TRANSFORM
    // touch button + full nine-soul meter, both directions. His moveset
    // stays his own ('zen') in every stage — the tentacle pastel-blast
    // specials are a moveset-stage design requirement (RIG-NOTES.md), not
    // a moveset key that exists yet. Keyed on BOTH 'zen' and 'zen-attire1'
    // like Demonio: the player-side formKey can resolve to either.
    forms: {
      'zen': {
        up: { target: 'zen-tentacle', label: 'TENTACLE MANIFESTATION', powerMult: 1.15, speedMult: 1.0, defenseMult: 1.05, moveset: 'zen' },
      },
      'zen-attire1': {
        up: { target: 'zen-tentacle', label: 'TENTACLE MANIFESTATION', powerMult: 1.15, speedMult: 1.0, defenseMult: 1.05, moveset: 'zen' },
      },
      'zen-tentacle': {
        up: { target: 'zen-oversoul', label: 'OVERSOUL', powerMult: 1.25, speedMult: 1.05, defenseMult: 1.15, moveset: 'zen' },
        down: { target: 'zen-attire1', label: 'WITHDRAW', powerMult: 0.87, speedMult: 1.0, defenseMult: 0.95, moveset: 'zen' },
      },
      'zen-oversoul': {
        down: { target: 'zen-tentacle', label: 'OVERSOUL RELEASE', powerMult: 0.8, speedMult: 0.95, defenseMult: 0.87, moveset: 'zen' },
      },
    } },
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
      // The player default resolves to the 'demonio' BASE attire (attires.js
      // list head), so the base form keys the same chain as A1 — without this
      // entry the player-side formKey ('demonio') dangles and he never
      // transforms as the player. Same targets/labels as A1; key alignment only.
      'demonio': {
        up: { target: 'demonio-winged', label: 'DEVIL ASCENSION', powerMult: 1.5, speedMult: 1.05, defenseMult: 1.2, bodyScale: 1.22, moveset: 'demonio-winged' },
        down: { target: 'demonio-human', label: 'DEPOWER', powerMult: 0.7, speedMult: 1.1, defenseMult: 0.9, bodyScale: 0.95, moveset: 'demonio' },
      },
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
  { id: 'phantom', name: 'PHANTOM', title: 'The Ghost Blade Soul', base: 'Yoshimitsu', moveset: 'yoshimitsu', model: 'phantom', tintStrength: 0.6,
    colors: { suit: 0x1a1a2a, trim: 0x00ffcc }, style: 'Sword Style', archetype: 'Tricky' },
  { id: 'diablo', name: 'DIABLO', title: 'The Devil Soul', base: 'Heihachi', moveset: 'heihachi', model: 'diablo', tintStrength: 0.6,
    colors: { suit: 0x5a0a0a, trim: 0xff4400 }, style: 'Mishima', archetype: 'Boss' },
  { id: 'skull', name: 'SKULL', title: 'The Punisher Soul', base: 'Bryan Fury', moveset: 'bryan', model: 'skull', tintStrength: 0.25,
    colors: { suit: 0x2a2a2a, trim: 0xcccccc }, style: 'Kickboxing', archetype: 'Rushdown' },
  { id: 'samura1', name: 'SAM-UR-A1', title: 'The Mech Soul', base: 'Jack-7', moveset: 'gunjack', model: 'sam-ur-a1', tintStrength: 0.25,
    colors: { suit: 0x3a3a4a, trim: 0x00aaff }, style: 'Power Robot', archetype: 'Zoner' },
    // Attire 1 = Tripo pull 2026-10-19 (owner: 'SAM-UR-A1 model attire 1'). Former pantera base retired to docs.
  { id: 'sakura', name: 'SAKU RA', title: 'The Idol Soul', base: 'Xiaoyu', moveset: 'xiaoyu', model: 'saku-ra', tintStrength: 0.6,
    colors: { suit: 0xff6b9d, trim: 0xffd700 }, style: 'Hakkesho', archetype: 'Evasive' },

  // ——— BONUS ROSTER ———
  { id: 'zui', name: 'ZUI', title: 'Drunken Master', base: 'Steve Fox', moveset: 'demonio', model: 'zui-attire1', tintStrength: 0.6,
    colors: { suit: 0x2a4a2a, trim: 0x6acc3a }, style: 'Boxing/Drunken', archetype: 'Tricky' },
  { id: 'kinpo', name: 'KINPO', title: 'Splinter of SHA', base: 'Asuka', moveset: 'demonio', model: 'kinpo', tintStrength: 0.6,
    colors: { suit: 0xd44d8a, trim: 0xffd700 }, style: 'Kazama Style', archetype: 'Counter' },
  { id: 'waterfall', name: 'WATERFALL', title: "Grief of Nine", base: 'Josie', moveset: 'demonio', model: 'waterfall', tintStrength: 0.6,
    colors: { suit: 0x3a6acc, trim: 0x9fd8ff }, style: 'Eskrima', archetype: 'Rushdown' },
  { id: 'kingtyrant', name: 'KING TYRANT', title: 'Showman King', base: 'Eddy Gordo', moveset: 'xiaoyu', model: 'king-tyrant', tintStrength: 0.25,
    colors: { suit: 0x8a6a1a, trim: 0xffd700 }, style: 'Capoeira', archetype: 'Showman' },
  { id: 'burger', name: 'BURGER', title: 'Hunger is a Curse', base: 'Bob', moveset: 'bryan', model: 'burger', tintStrength: 0.25,
    colors: { suit: 0xcc8833, trim: 0xff4400 }, style: 'Sumo/Brawler', archetype: 'Power',
    // Burger demon transformation chain (owner 2026-10-19): Kusaregedo kit per form.
    // Chain: base -> speed-demon -> the-mouth -> demon (final). Demon form gets FULL kit
    // + mix of smaller forms' abilities + exclusives. Extensible for new forms.
    forms: {
      'burger': {
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
  { id: 'awapop', name: 'AWA POP', title: 'Bubbles', base: 'Nina', moveset: 'demonio', model: 'awa-pop', tintStrength: 0.6,
    colors: { suit: 0xff9dcc, trim: 0xffffff }, style: 'Assassin', archetype: 'Rushdown' },
  { id: 'scimitar', name: 'SCIMITAR', title: 'Desert Blade', base: 'Shaheen', moveset: 'demonio', model: 'scimitar', tintStrength: 0.6,
    colors: { suit: 0x2a2a3a, trim: 0xc2a36b }, style: 'Military', archetype: 'Balanced' },
  { id: 'purplerain', name: 'PURPLE RAIN', title: 'MJ x Prince x Pimp', base: 'Lee', moveset: 'demonio', model: 'purple-rain', tintStrength: 0.6,
    colors: { suit: 0x6b2d8f, trim: 0xff00ff }, style: 'Martial Arts', archetype: 'Stylish' },
  { id: 'nightwolf', name: 'NIGHTWOLF', title: 'Storm Shadow', base: 'Julia', moveset: 'xiaoyu', model: 'nightwolf', tintStrength: 0.6,
    colors: { suit: 0x1a3a5a, trim: 0x6accff }, style: 'Xinyi Liuhe', archetype: 'Balanced' },
  { id: 'dio', name: 'DIO', title: 'Raging Demon', base: 'Akuma', moveset: 'heihachi', model: 'dio', tintStrength: 0.6,
    colors: { suit: 0x1a1a1a, trim: 0xff0000 }, style: 'Satsui no Hado', archetype: 'Shoto' },
  // CAPE JONES is the display name (owner 2026-10-23: "Start calling cyborg x as cape Jones
  // but leave cyborg x in the deep canon for him"). 'Cyborg X' stays as his deep-canon identity.
  { id: 'cyborgx', name: 'CAPE JONES', title: 'GYOU Splinter', base: 'Alisa', moveset: 'gunjack', model: 'cyborg-x', tintStrength: 0.6,
    // owner pt128u 2026-10-23: always the rig with the most bones -> cyborg-x.glb (160 joints incl. full
    // Mixamo-named core) over cape-jones.glb (49). Stance = CMU 13_17 boxing guard (CMU license, commercial-safe).
    stanceClip: 'assets/anim/oss/cyborgx/stance.glb',
    colors: { suit: 0xcccccc, trim: 0x00ffcc }, style: 'Robot Combat', archetype: 'Zoner' },
  { id: 'michiko', name: 'MICHIKO', title: 'Savate Queen', base: 'Katarina', moveset: 'demonio', model: 'michiko', tintStrength: 0.6,
    colors: { suit: 0x8a1a4a, trim: 0xff6b9d }, style: 'Savate', archetype: 'Rushdown' },
  { id: 'star', name: 'STAR', title: 'KAI Splinter', base: 'Christie', moveset: 'xiaoyu', model: 'star', tintStrength: 0.25,
    colors: { suit: 0xffd700, trim: 0xff6b00 }, style: 'Capoeira', archetype: 'Rushdown' },
  { id: 'torch', name: 'TORCH', title: 'Fire Assassin', base: 'Anna', moveset: 'demonio', model: 'torch-tripo-a1', tintStrength: 0.6,
    // Main entry model = ATTIRE 1 'Valkyrie of Flame' (owner ladder rule
    // 2026-10-21: the Tripo original at the forefront; the Anna base model
    // ('torch') ladders back as the fallback attire — see attires.js and
    // roster/torch/ATTIRE-SLOTS.md).
    colors: { suit: 0x8a1a1a, trim: 0xff8800 }, style: 'Assassin', archetype: 'Tricky' },
  { id: 'bruno', name: 'BRUNO', title: 'Matador', base: 'Miguel', moveset: 'bryan', model: 'bruno', tintStrength: 0.25,
    colors: { suit: 0x5a1a1a, trim: 0xcc3333 }, style: 'Brawler', archetype: 'Power' },
  { id: 'negativo', name: 'N3GΔTIV0', title: 'Galactic Bounty Hunter', base: 'Negan', moveset: 'bryan', model: 'n3g4tiv0', tintStrength: 0.25,
    colors: { suit: 0x0a0a0a, trim: 0x00ff00 }, style: 'Brawler', archetype: 'Intimidation' },
  { id: 'thor', name: 'THOR', title: 'Norse God', base: 'Ganryu', moveset: 'bryan', model: 'thor', tintStrength: 0.25,
    colors: { suit: 0x4a3a2a, trim: 0xffd700 }, style: 'Sumo', archetype: 'Power' },
  { id: 'yukihyo', name: 'YUKIHYŌ', title: 'Snow Leopard Ninja', base: 'Armor King', moveset: 'king', model: 'yukihyo', tintStrength: 0.25,
    colors: { suit: 0xd0d0d0, trim: 0x6accff }, style: 'Grappler', archetype: 'Ninja' },
  { id: 'slice', name: 'SLICE', title: 'Maniacal Agent', base: 'Dragunov', moveset: 'bryan', model: 'slice', tintStrength: 0.6,
    colors: { suit: 0x2a2a2a, trim: 0xcc0000 }, style: 'Commando Sambo', archetype: 'Grappler' },
  { id: 'docfrank', name: 'DOC FRANK', title: 'Father of Machines', base: 'Bosconovitch', moveset: 'gunjack', model: 'doc-frank-big', tintStrength: 0.6,
    colors: { suit: 0x6a6a7a, trim: 0x00ffcc }, style: 'Inventor', archetype: 'Tricky',
    // Main entry model = Attire 1's Tripo bigger form (owner override
    // 2026-10-21: "show the Tripo 3D models I made for him" — Tripo models
    // lead, Tekken-based models ladder back). Matches the picker default
    // (ATTIRE_VARIANTS 'docfrank' slot 1).
    // Mid-match Roshi-style transformation (owner 2026-10-19): TRANSFORM touch
    // button. Per-attire targets (dedup 2026-10-22): each folded attire card
    // keeps its own old transform target, keyed by model — Fighter resolves
    // via formKey = the selected attire's model. 'doc-frank-big' default:
    // big->big no-op, exactly the old main-card behavior.
    forms: {
      'doc-frank-a1': { target: 'doc-frank-big', label: 'TRANSFORM', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 },
      'doc-frank-big': { target: 'doc-frank-big', label: 'TRANSFORM', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 },
      'doc-frank-wowomomo': { target: 'doc-frank-wowomomo-big', label: 'TRANSFORM', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 },
      'doc-frank-hood': { target: 'doc-frank-hood-big', label: 'TRANSFORM', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 },
      'doc-frank-frankenstein': { target: 'doc-frank-frankenstein-big', label: 'TRANSFORM', powerMult: 1.4, speedMult: 0.88, defenseMult: 1.15, bodyScale: 1.18 },
    } },
  // ——— DEDUP 2026-10-22: the RESKIN WAVE / WAVE 2 standalone cards below were
  // folded into their fighters' ATTIRE_VARIANTS ladders (owner rule: an attire
  // must not stand alone as a selectable model). demonio-bloodline-ember,
  // demonio-winged, demonio-human -> 'demonio' ladder; doc-frank-wowomomo,
  // doc-frank-hood, doc-frank-frankenstein, doc-frank-machine-shop ->
  // 'docfrank' ladder. Models preserved, just re-homed.
  { id: 'baek-master-white', name: 'KEVIN', title: "The Master Soul", base: 'Kevin', moveset: 'bryan', model: 'baek', tintStrength: 0.25,
    colors: { suit: 0xf0f0f0, trim: 0x8a1a1a }, style: 'Tae Kwon Do', archetype: 'Pressure' },
  { id: 'mariposa-monarch', name: 'MARIPOSA', title: 'Monarch', base: 'Zafina', moveset: 'xiaoyu', model: 'mariposa-butterfly-default', tintStrength: 0.25,
    colors: { suit: 0x2a1a3a, trim: 0xff8800 }, style: 'Azazel Arts', archetype: 'Tricky' },
  // DEDUP (2026-10-22): default model = her owner-designated Slot 1
  // (Butterfly Default, owner 2026-10-19 exception to the Tripo-first law).
  // Entry id kept: EPISODES, HEARTMIND_STORIES, MOVESET_MAP, moveset files
  // and the portrait are keyed by it.
  { id: 'dxmmii-patchwork', name: 'DXMMII', title: 'Patchwork DJ', base: 'Mokujin', moveset: 'demonio', model: 'dxmmii-tripo', tintStrength: 0.25,
    colors: { suit: 0x3a2a5a, trim: 0x00ffcc }, style: 'Mimicry', archetype: 'Trickster' },
  // DEDUP (2026-10-22): default model = his Slot 1 Tripo Default
  // (roster/dxmmii/ATTIRE-SLOTS.md, owner 2026-10-19). Entry id kept
  // (MOVESET_MAP, moveset files, portrait keyed by it).
  // Sketchfab intake models (owner 2026-10-19). Licenses: Zangief CC-BY
  // (johnny136), Blanka Free Standard (allanromanreyes), Vega CC-BY
  // (pierodsoto01), Iori CC-BY (0xo), Armor King CC-BY (theamazingdonovan207).
  // OBSOLETE-ORIGINALS rule (owner 2026-10-23, docs/OBSOLETE-ORIGINALS-RULE.md):
  // Zangief, Vega, Iori and Armor King are NOT fighters in this universe and
  // get NO select entry — their movesets and identities became KRONOS,
  // KORESHI, DEATHFANG and YUKIHYŌ. Their standalone entries were removed
  // 2026-10-23 (landing wave 1); the models stay in the repo and ladder as
  // late attires of their successors (game/js/attires.js). Blanka never had
  // an entry; his model ladders behind CHARGER.
  // CHARGER (owner 2026-10-20): proprietary Blanka REPLACEMENT — "his name is
  // charger cause of blankas attacks and movesets will be attach to him but he's
  // got powers of ice and electricity". Blanka's roster slot is his now; his full
  // 199-move set lives in movesets/charger.json (data identical, signature names
  // given his ice+electric identity — see RENAME-MAP.md). Blanka's own files
  // (roster/blanka/, movesets/blanka.json, sf-blanka.json) stay in the repo.
  // Owner-made Tripo models: Attire 1 "ice monster", Attire 2 "green spiky creature".
  { id: 'charger', name: 'CHARGER', title: 'The Ice Monster', base: 'Blanka', moveset: 'charger', model: 'charger', tintStrength: 0.25,
    colors: { suit: 0x9fd8e8, trim: 0xffd23f }, style: 'Ice/Electric Beast', archetype: 'Rushdown',
    surge: { name: 'ABSOLUTE ZERO SURGE', color: 0x66ccff, accent: 0xffff66 },
    stats: { speed: 5.0, jump: 7.0, power: 1.2, defense: 1.05 },
    ai: { aggression: 0.8, grabBias: 0.45, reaction: 0.55 } },
  // DOROWANI (owner 2026-10-22): Gon's WH replacement — mud-croc kappa-yokai.
  // Small, fast, goofy, fire breath. Moveset: Gon's Tekken 3 kit (dorowani.json).
  // Voice: barks Japanese words, never sentences ("Konnichiwa arigato Ichiban Bankai").
  { id: 'dorowani', name: 'DOROWANI', title: 'The Mud-Croc Trickster', base: 'Gon', moveset: 'dorowani', model: 'dorowani', tintStrength: 0.25,
    colors: { suit: 0x2a7ac2, trim: 0xc22a2a }, style: 'Beast Brawler', archetype: 'Rushdown',
    surge: { name: 'DINO BREATH SURGE', color: 0xff6a00, accent: 0xffd23f },
    stats: { speed: 5.5, jump: 7.5, power: 1.1, defense: 0.95 },
    ai: { aggression: 0.85, grabBias: 0.35, reaction: 0.6 } },
  // CHATUR (owner 2026-10-23): True Ogre's WH replacement — four-armed Oversoul
  // spirit, temple dancer who refused to die. Anchors the spirit realm, GYOU-touched.
  // Moveset: True Ogre's Tekken 3 kit (chatur.json). "Stopping is dying. I already did that once."
  { id: 'chatur', name: 'CHATUR', title: 'The Bridge Soul', base: 'True Ogre', moveset: 'chatur', model: 'chatur', tintStrength: 0.25,
    colors: { suit: 0x3a2a5a, trim: 0xd8b46a }, style: 'Temple Dance / Oversoul', archetype: 'Power',
    surge: { name: 'FOURFOLD MUDRA SURGE', color: 0x8a5adf, accent: 0xffe9b0 },
    stats: { speed: 3.8, jump: 6.0, power: 1.45, defense: 1.15 },
    ai: { aggression: 0.7, grabBias: 0.4, reaction: 0.55 } },
  // POND (owner 2026-10-23): Raven's WH replacement — swamp boundary watcher,
  // found Dorowani as an egg. Moveset: Raven's Tekken 7 kit (pond.json). "The pond does not chase."
  { id: 'pond', name: 'POND', title: 'The Still Water Soul', base: 'Raven', moveset: 'pond', model: 'pond', tintStrength: 0.25,
    colors: { suit: 0x1a4a3a, trim: 0x7ad8b0 }, style: 'Ninjutsu / Still Water', archetype: 'Evasive',
    surge: { name: 'STILL WATER SURGE', color: 0x2a8a6a, accent: 0xb0ffe0 },
    stats: { speed: 5.2, jump: 7.2, power: 1.0, defense: 1.0 },
    ai: { aggression: 0.6, grabBias: 0.35, reaction: 0.7 } },
  // RYUSAN (owner 2026-10-23): Lucky Chloe's WH replacement — the Corrosion Soul,
  // acid punk mortal lost soul, sweats solvent and laughs about it. Jotei family crimes
  // survivor. Moveset: Lucky Chloe's Tekken 7 kit (ryusan.json). "You don't get to tell me to calm down."
  { id: 'ryusan', name: 'RYUSAN', title: 'The Corrosion Soul', base: 'Lucky Chloe', moveset: 'ryusan', model: 'ryusan', tintStrength: 0.25,
    colors: { suit: 0x7ac22a, trim: 0xe8ff4d }, style: 'Acid Punk Brawler', archetype: 'Rushdown',
    surge: { name: 'VITRIOL SURGE', color: 0x9dff00, accent: 0xfff200 },
    stats: { speed: 5.4, jump: 7.4, power: 1.05, defense: 0.95 },
    ai: { aggression: 0.85, grabBias: 0.3, reaction: 0.65 } },
  // TOBI (owner 2026-10-23): Hwoarang's WH replacement — the Escape Soul, rabbit
  // courier, fastest in the roster. Carries one letter she never delivered — left hand
  // never leaves the satchel strap. Moveset: Hwoarang's Tekken 3 kit (tobi.json). "Don't wait for it. Be already gone."
  { id: 'tobi', name: 'TOBI', title: 'The Escape Soul', base: 'Hwoarang', moveset: 'tobi', model: 'tobi', tintStrength: 0.25,
    colors: { suit: 0xe8e8f0, trim: 0xff6a9a }, style: 'Tae Kwon Do / Courier', archetype: 'Rushdown',
    surge: { name: 'LONGLEAP SURGE', color: 0xffffff, accent: 0xff6a9a },
    stats: { speed: 6.0, jump: 8.0, power: 0.95, defense: 0.9 },
    ai: { aggression: 0.75, grabBias: 0.25, reaction: 0.8 } },
  // MEGAMI (owner 2026-10-23): Jun Kazama's WH replacement — the Shrine Soul,
  // guardian of a sealed door that never opened. Trained Chatur. Moveset: Jun Kazama's
  // TTT2 kit + sealed-door canon forms (megami.json). "The shrine was here before you. It will be here after."
  { id: 'megami', name: 'MEGAMI', title: 'The Shrine Soul', base: 'Jun Kazama', moveset: 'megami', model: 'megami', tintStrength: 0.25,
    colors: { suit: 0xc22a2a, trim: 0xf0e8d8 }, style: 'Temple Guardian', archetype: 'Defensive',
    surge: { name: 'SEALED DOOR SURGE', color: 0xcc2222, accent: 0xffe9b0 },
    stats: { speed: 4.5, jump: 6.5, power: 1.1, defense: 1.2 },
    ai: { aggression: 0.55, grabBias: 0.4, reaction: 0.75 } },
  // MENAJERII (owner 2026-10-23, Japanese rendering owner's choice): Roger Jr.'s WH
  // replacement — the Menagerie Soul, spirit-walker carrying beast spirits; her shadow
  // doesn't always match her body. Moveset: Roger Jr.'s TTT2 kit + beast moves (menajerii.json).
  // "The herd decides. I just run."
  { id: 'menajerii', name: 'MENAJERII', title: 'The Menagerie Soul', base: 'Roger Jr.', moveset: 'menajerii', model: 'menajerii', tintStrength: 0.25,
    colors: { suit: 0x5a3a1a, trim: 0x8ad82a }, style: 'Beast Instinct / Spirit-Walk', archetype: 'Trickster',
    surge: { name: 'MENAGERIE SURGE', color: 0x7ac22a, accent: 0xffd23f },
    stats: { speed: 5.0, jump: 7.0, power: 1.15, defense: 1.0 },
    ai: { aggression: 0.7, grabBias: 0.45, reaction: 0.65 } },
  // Custom fighters (owner 2026-10-19): KRONOS + DEATHFANG + Ryuji/Rock hybrid.
  { id: 'kronos', name: 'KRONOS', title: 'The Titan Cyclone', base: 'Zangief + Golem', moveset: 'kronos', model: 'kronos', tintStrength: 0.25,
    colors: { suit: 0x8a1a1a, trim: 0xccaa00 }, style: 'Grappler/Wrestler', archetype: 'Power',
    surge: { name: "TITAN'S WRATH", color: 0xcc2222, accent: 0xffd700 },
    stats: { speed: 3.2, jump: 5.5, power: 1.5, defense: 1.35 },
    ai: { aggression: 0.7, grabBias: 0.6, reaction: 0.5 } },
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
  { id: 'koreshi', name: 'KORESHI', title: 'The Shadow Ninja', base: 'Kakashi + Super Saiyan', moveset: 'koreshi', model: 'koreshi', tintStrength: 0.25,
    colors: { suit: 0x2a3a4a, trim: 0xcc2222 }, style: 'Ninja/Samurai', archetype: 'Trickster',
    surge: { name: 'SHARINGAN AWAKENING', color: 0xcc2222, accent: 0xffffff },
    stats: { speed: 5.5, jump: 8.0, power: 1.1, defense: 0.95 },
    ai: { aggression: 0.7, grabBias: 0.25, reaction: 0.7 } },
  // RAVE = KIKO TANAKA = GHOST in Western Heart (owner 2026-10-19 / 2026-10-21: "Lei wulong is not byou, he is
  // Rave/Kiko tanaka ... rave already takes over leis character and slot and moves and personality").
  // RAVE is his MAIN game/display name (owner 2026-10-23). Kiko, Ghost, and Kiko Tanaka are all the
  // same person — all four names documented in repo/canon. Never split into separate fighters.
  // Model: his rigged Tripo pull (roster/TRIPO-REGISTRY.md: A1 hooded, A2 unrobed "ghost Tanaka",
  // A3+ rave.glb). Moves: game/assets/movesets/rave.json (Lei T7 + Lei T3 + Byou). Style from
  // roster/rave/CONCEPT.md; colors = the Great Muta red/green paint the concept names.
  { id: 'rave', name: 'RAVE', title: 'The Painted Soul', base: 'Lei Wulong', moveset: 'rave', model: 'kiko-tanaka',
    colors: { suit: 0x1f5e2c, trim: 0xc62828 }, style: 'Five Animals', archetype: 'Trickster' },
  // ——— LANDING WAVE 1 (2026-10-23, docs/CATCHUP-AUDIT-2026-10-23.md): fighters
  // whose models + movesets were already on main but who had no select entry.
  // BUFFALO BILL (owner canon: The Horned Messenger; Marshall/Forest Law base
  // moveset, game/assets/movesets/buffalo-bill.json). His only on-main model
  // is Attire 3 "Ashes" (roster/buffalo-bill/CANON.md) — the base model key
  // points there until his A1/A2 sources land in the repo.
  { id: 'buffalo-bill', name: 'BUFFALO BILL', title: 'The Horned Messenger', base: 'Marshall Law', moveset: 'buffalo-bill', model: 'buffalo-bill', tintStrength: 0.25,
    colors: { suit: 0x7a1220, trim: 0x4a2a7a }, style: 'Street Brawler', archetype: 'Balanced' },
  // VAIN ABEL ELIAS (owner canon: "The Brother", Cain Elias's brother; Bass
  // Armstrong base — game/assets/movesets/vainabel.json). Attire 1 Tripo is
  // not on disk (roster/TRIPO-REGISTRY.md); base model key = Attire 2.
  { id: 'vainabel', name: 'VAIN ABEL', title: 'The Brother', base: 'Bass Armstrong', moveset: 'vainabel', model: 'vainabel', tintStrength: 0.25,
    colors: { suit: 0x1a0f24, trim: 0x7a2bd8 }, style: 'Grappler', archetype: 'Power' },
  // CAIN ELIAS (owner 2026-10-19: Vain Abel's brother, the Deadman; moveset
  // id 'cainelias' per the shipped file + loader lists, model keys under
  // 'cain-elias'). Model + moveset + loader listing existed; only the
  // select entry was missing.
  { id: 'cainelias', name: 'CAIN ELIAS', title: 'The Deadman', base: 'Undertaker (WWE)', moveset: 'cainelias', model: 'cain-elias', tintStrength: 0.25,
    colors: { suit: 0x14141c, trim: 0x5a2a8a }, style: 'Grappler', archetype: 'Power' },
  // CHORDZ (owner 2026-10-15: Lars -> Chordz, the emo guitarist; moveset
  // file + loader listing existed, model sat in attires/attire1/source/).
  { id: 'chordz', name: 'CHORDZ', title: 'The Emo Guitarist', base: 'Lars', moveset: 'chordz', model: 'chordz', tintStrength: 0.25,
    colors: { suit: 0x1a1a2a, trim: 0x8a2a6b }, style: 'Emo Guitarist', archetype: 'Tricky' },
];

export function getFighter(id) {
  return FULL_ROSTER.find(f => f.id === id) || FULL_ROSTER.find(f => f.id === 'pantera'); // default Pantera
}

/* Tier membership (dedup 2026-10-22): explicit id lists, not positional
   slices — folding attire-cards out of FULL_ROSTER must not shift fighters
   between tiers. SOUL_IDS = the Nine Souls minus JIN (folded into Phantom's
   attire ladder per owner directive 2026-10-22: "Yoshimitsu is supposed to
   ladder into Phantom's attires, not stand alone"). MAIN_IDS = the original
   main-roster block. Everything else is bonus. */
export const SOUL_IDS = ['rin', 'byou', 'tou', 'sha', 'kai', 'retsu', 'zen', 'gyou'];
export const MAIN_IDS = ['pantera', 'demonio', 'phantom', 'diablo', 'skull', 'samura1', 'sakura'];

export function getRosterByTier() {
  const byId = new Map(FULL_ROSTER.map(f => [f.id, f]));
  const inTier = new Set([...SOUL_IDS, ...MAIN_IDS]);
  return {
    souls: SOUL_IDS.map(id => byId.get(id)).filter(Boolean),
    main: MAIN_IDS.map(id => byId.get(id)).filter(Boolean),
    bonus: FULL_ROSTER.filter(f => !inTier.has(f.id)),
  };
}
