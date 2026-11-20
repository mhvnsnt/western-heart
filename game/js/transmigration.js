/* ============================================================
   WESTERN HEART — Transmigration Sequences (Tong-Nou)
   Phase 2 lane: sato / tongnou-transmigration, 2026-11-20.

   The playable transmigration sequence from Eastern Mind: The Lost
   Souls of Tong-Nou (1994, Osamu Sato), wired into Western Heart
   with WH canon + WH characters (never clones).

   WHAT THIS IS: die + reincarnate 9 times; death is progression,
   not game-over. On each death the player picks the next life on
   the D_FACE face-pick screen (3 eyes x 3 noses x 3 mouths); the
   face calls the vessel. Each of the 8 creature lives is one
   mission; finishing it earns that creature's Nameplate. With all
   8 Nameplates the seal unlocks, the 5 Magatamas are gathered, they
   forge the Katana of Five Forces, and the soul is recovered at the
   Octagonal Shrine Par-fang on Central Mountain.

   WHAT THIS IS NOT: a reimplementation of the original game. The
   working pieces are pulled in whole (PULL-WORKING-COMPLETE law):
   - Face art: game/js/modes.js EM_FACE — the original D_FACE
     bitmaps, already in-repo under teardown/eastern-mind/. The
     FACE_ART table below MUST match EM_FACE; the test asserts it
     by reading modes.js as text (same pattern as the heartmind
     stage-key test), so the two can never drift apart silently.
   - Vessels / forces / Trial ladder: modes.js (VESSEL_AFFINITY,
     FORCES, STORY_STAGES). Vessel ids here match VESSEL_AFFINITY
     exactly (jin_soul, not jin — WH's Jin vessel id).
   - Sound slots: game/data/eastern-mind-sfx.json
     (reincarn.death, reincarn.rebirth, ui.click).
   - Stages/lands: game/js/stages.js defs + modes.js STORY_STAGES.
   This module is the SEQUENCE layer that wires those working
   pieces into one playable 9-life run. It imports nothing and is
   DOM-free, so it unit-tests in node like the top half of modes.js.

   SOURCES (read live 2026-11-20; story beats summarised only to
   describe the mechanic — WH story is separate, owner order):
   - Face -> creature map + missions + endgame: GameFAQs
     "Eastern Mind: The Lost Souls of Tong Nou — Guide and
     Walkthrough" by lordgod666 v1.02, §2 Characters + §3
     Walkthrough + §4 Items
     (gamefaqs.gamespot.com/mac/355275-eastern-mind-the-lost-souls-of-tong-nou/faqs/64346)
     and walkthroughking.com/text/easternmind.aspx (same mapping).
   - Kai: compu-lsd.com Osamu Sato Wiki, Kai page.
   - Plot frame (49-day temporary soul, 9 lives, 5 Magatamas):
     Wikipedia, "Eastern Mind: The Lost Souls of Tong Nou".
   - Phase 1 mechanic note: game-reverse-engineering
     sato/eastern-mind/TRANSMIGRATION-MECHANIC.md.

   HONEST GAPS (flagged, never silently filled):
   - The original documents TWO options per face part (Left/Right:
     8 combos = 8 creatures). WH offers THREE per part (EM_FACE
     art + the brief's 3x3x3 screen). The rule for the third
     option (index 2) is WH-AUTHORED, not original: any index-2
     part is Rin's own face — rebirth as the self — and the self
     is gated until all 8 creature Nameplates are held. The 8
     verified combos use indices 0 (=Left) and 1 (=Right).
   - The Earth Magatama's exact original pickup is not spelled
     out in the walkthrough text read; it is placed at Central
     Mountain here, one Magatama per land (Phase 1 doc structure).
   - Chu-Teng DROPS transmigration (fetch-the-parts instead) —
     out of scope here by design; the mechanic WH carries forward
     lives in Tong-Nou.
   ============================================================ */

/* Face art — MUST match modes.js EM_FACE exactly (test enforces).
   Paths are relative to game/js/ (modes.js) AND work unchanged
   from game/transmigration.html: game/js/../teardown ==
   game/../teardown == repo-root/teardown. */
export const FACE_ART = {
  eyes: [
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b011_40x39.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b012_40x39.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b042_88x61.png',
  ],
  nose: [
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b009_92x94.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b025_51x64.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b033_59x68.png',
  ],
  mouth: [
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b004_108x93.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b002_113x108.png',
    '../teardown/eastern-mind/prologue-ending/bitmaps/D_FACE/D_FACE_b008_72x58.png',
  ],
};

/* Sound slots in game/data/eastern-mind-sfx.json (names only here;
   the page / audio lane resolves them — this module plays nothing). */
export const TRANSMIGRATION_SFX = {
  death: 'reincarn.death',
  rebirth: 'reincarn.rebirth',
  click: 'ui.click',
};

/* ---------------- The five lands (wuxing) ----------------
   Keys match modes.js FORCES / STORY_STAGES. Earth holds no
   creature — Central Mountain is the endgame, not a life. */
export const LANDS = {
  wood:  { key: 'wood',  name: 'Ming-ken',      title: 'Land of Life',    element: 'Wood',  stage: 'tree-of-life',       force: 'wood' },
  fire:  { key: 'fire',  name: 'Shi-chieng',    title: 'Land of Time',    element: 'Fire',  stage: 'plains-of-chi-u',    force: 'fire' },
  earth: { key: 'earth', name: 'Tong-nou',      title: 'Central Mountain', element: 'Earth', stage: 'octagonal-shrine',   force: 'earth' },
  metal: { key: 'metal', name: 'Yui-wang',      title: 'Land of Desire',  element: 'Metal', stage: 'helix-palace',        force: 'metal' },
  water: { key: 'water', name: 'Mon-chien',     title: 'Land of Dreaming', element: 'Water', stage: 'palace-of-dreaming', force: 'water' },
};
export const LAND_ORDER = ['wood', 'fire', 'earth', 'metal', 'water']; // generating-cycle order, modes.js FORCE_ORDER
export const MAGATAMA_LANDS = ['earth', 'metal', 'water', 'wood', 'fire']; // one Magatama per land

/* ---------------- The eight creatures ----------------
   face: [eye, nose, mouth] with 0 = Left, 1 = Right — the verified
   map (GameFAQs §2). vessel: the WH vessel id in modes.js
   VESSEL_AFFINITY. steps: the mission beats, in walkthrough order.
   magatamas: Magatamas earned by finishing this creature's mission
   (Byou's segment yields Water + Wood; the rest come in the
   endgame). linear: the walkthrough's "[*] linear" stages — short,
   few-step missions, as the original has them. */
export const CREATURES = {
  tou: {
    id: 'tou', vessel: 'tou', face: [0, 0, 0], name: 'TOU', land: 'wood',
    home: 'Ming-ken · Land of Life — Guardian of the Tree of Life',
    mission: 'Register new life. Travel to Shi-chieng (Land of Time) and enter the names.',
    bornWith: 'Disc of Wood',
    steps: [
      'Tree of Life, Land of Life — speak with the King of Life',
      'Land of Time — climb the Fire Tower of Time to the computer room',
      'Use the Disc of Wood: enter ZO-U-GA-E-RE, ZO-U-GA-E-RI, ZO-U-GA-E-RO, ZO-U-GA-E-RA, TO-U',
      'Take the registration card from the computer',
      'Return the card to the King of Life at the Tree of Life',
    ],
    magatamas: [],
  },
  jin: {
    id: 'jin_soul', vessel: 'jin_soul', face: [0, 0, 1], name: 'JIN', land: 'metal',
    home: 'Yui-wang · Land of Desire — faithful subordinate of King-gyou',
    mission: 'Serve King-gyou, whose body is gold. Jin wishes he were born of gold — and detests water, which would corrode his bronze body.',
    bornWith: 'Bronze body',
    linear: true,
    steps: [
      'Land of Desire — present yourself to King-gyou',
      'Serve faithfully, as a subordinate of gold must',
    ],
    magatamas: [],
  },
  sha: {
    id: 'sha', vessel: 'sha', face: [0, 1, 0], name: 'SHA', land: 'metal',
    home: 'Yui-wang · Land of Desire — the chosen one; only Sha can play the instruments',
    mission: 'Collect all four musical instruments of the Tong-Nou World and play them in the Land of Desire.',
    bornWith: 'Bell of Gold',
    instruments: ['Bell of Gold', 'Drum of Fire', 'Koto of Wood', 'Flute of Water'],
    steps: [
      'Born with the Bell of Gold',
      'Drum of Fire — the tower stairs, Land of Time',
      'Koto of Wood — play the drums at the Tree of Life',
      'Flute of Water — the Palace of Dreaming, second door of the right corridor',
      'Land of Desire — play all four instruments together',
    ],
    magatamas: [],
  },
  gyou: {
    id: 'gyou', vessel: 'gyou', face: [0, 1, 1], name: 'GYOU', land: 'fire',
    home: 'Shi-chieng · Land of Time — born to perform the Ritual of Time',
    mission: 'Feed flames to the Candles of Time. Gyou would rather be freestyle flying — the task annoys him.',
    bornWith: 'Wings for hazardous aviation',
    linear: true,
    steps: [
      'Land of Time — take up the Ritual of Time',
      'Feed flames to the Candles of Time',
      'The ritual is done — the candles burn on',
    ],
    magatamas: [],
  },
  zen: {
    id: 'zen', vessel: 'zen', face: [1, 0, 0], name: 'ZEN', land: 'water',
    home: 'Mon-chien · Land of Dreaming — Guard of the Ice Wall',
    mission: 'Guard the Ice Wall. Born with the words of duty: "notify all change." To break the ice someday — that is the hope.',
    bornWith: 'Words of duty',
    linear: true,
    steps: [
      'Land of Dreaming — take your post inside the Ice Wall',
      'Turn, watch the river flow and the Magatamas cross — until something shows at the top',
      'Break the ice: the duty is done',
    ],
    magatamas: [],
  },
  byou: {
    id: 'byou', vessel: 'byou', face: [1, 0, 1], name: 'BYOU', land: 'water',
    home: 'Mon-chien · Land of Dreaming — under orders of Sui-syou, King of Dreaming',
    mission: 'Head to Ming-ken (Land of Life) and collect the Eyeball of Dreaming. Born with a wrench; body decorated with leaves.',
    bornWith: 'Wrench',
    steps: [
      'Palace of Dreaming — answer the King of Dreaming: "Ying", take the peach',
      'Feed the peach to the monster — take the Water Magatama',
      'Land of Life — the ant, the King of Life, the word "Tou-Gyou" — take the Wood Magatama',
      'The tree roots — collect the Eyeball of Dreaming',
      'Palace of Dreaming — the wrench, the King: the segment is done',
    ],
    magatamas: ['water', 'wood'],
  },
  retsu: {
    id: 'retsu', vessel: 'retsu', face: [1, 1, 0], name: 'RETSU', land: 'wood',
    home: 'Ming-ken · Land of Life — a vermin, dwelling around the Tree of Life',
    mission: 'Help the troubled. Keep hidden in the shrubs; gnaw at grass and trees; beware the birds and Moku-gyou, King of Life, who dislikes vermin.',
    bornWith: 'Words of duty: "help the troubled"',
    linear: true,
    steps: [
      'Land of Life — hide in the shrubs around the Tree of Life',
      'Turn, keep turning — help the troubled until the segment is complete',
    ],
    magatamas: [],
  },
  kai: {
    id: 'kai', vessel: 'kai', face: [1, 1, 1], name: 'KAI', land: 'fire',
    home: 'Shi-chieng · Land of Time — Guard of the Candle of Life',
    mission: 'Draw the Water of Dreams and extinguish one particular candle. The candle is your own life.',
    bornWith: 'Leaf Sack',
    steps: [
      'Computer room — the glasses, the computer: enter KA-GI-YO-U',
      'Palace of Dreaming — fill the Leaf Sack with the Water of Dreams',
      'Land of Time — from the tower stairs: one step forward, right, one step forward, right, three steps forward',
      'Use the Leaf Sack — extinguish the candle',
    ],
    magatamas: [],
  },
};
export const CREATURE_IDS = Object.keys(CREATURES); // tou, jin, sha, gyou, zen, byou, retsu, kai
export const SELF_ID = 'rin';

/* Face -> creature, from the verified 2x2x2 map. Any index-2 part
   is Rin's own face (WH-authored rule — see header). Returns the
   vessel id, or 'rin' for the self. Pure. */
export function faceToCreature(eye, nose, mouth) {
  if (![eye, nose, mouth].every((v) => v === 0 || v === 1 || v === 2)) return null;
  if (eye === 2 || nose === 2 || mouth === 2) return SELF_ID;
  for (const id of CREATURE_IDS) {
    const f = CREATURES[id].face;
    if (f[0] === eye && f[1] === nose && f[2] === mouth) return CREATURES[id].vessel;
  }
  return null; // unreachable for 0/1 inputs — the 8 combos cover 2x2x2
}

/* All 27 face combinations and what each calls — for the face-pick
   screen. Each entry: { eye, nose, mouth, vessel } where vessel is
   a creature vessel id or 'rin'. */
export function allFaceCombinations() {
  const out = [];
  for (let eye = 0; eye < 3; eye++) {
    for (let nose = 0; nose < 3; nose++) {
      for (let mouth = 0; mouth < 3; mouth++) {
        out.push({ eye, nose, mouth, vessel: faceToCreature(eye, nose, mouth) });
      }
    }
  }
  return out;
}

/* ---------------- The 9-life run ----------------
   Phases: 'rin-life' -> (die) 'face-pick' -> (reincarnate)
   'mission' -> (mission done) 'face-pick' ... -> after the 8th
   creature plate: 'seal' -> (unlock) 'magatamas' -> (5 gathered)
   'katana' -> (forged) 'shrine' -> (recover) 'done'.
   lives counts completed lives (Rin = life 1 once his plate is
   earned); deaths counts deaths. A run is 9 lives total. */
export function createRun() {
  return {
    phase: 'rin-life',
    current: SELF_ID, // Rin, first life
    lives: 0,
    deaths: 0,
    nameplates: [], // vessel ids, Rin first, then creatures in play order
    magatamas: [], // land keys
    katana: false,
    sealUnlocked: false,
    soulRecovered: false,
    missionStep: 0, // index into the current creature's steps
    missionCreature: null,
    log: [],
  };
}

function cloneRun(r) {
  return {
    ...r,
    nameplates: [...r.nameplates],
    magatamas: [...r.magatamas],
    log: [...r.log],
  };
}
function say(r, text) {
  r.log.push(text);
  return r;
}

/* Die. Death is progression: in 'rin-life' it earns the Rin
   Nameplate (walkthrough: the left flame, the amulet saves you);
   in a creature mission it ends that life — but the Nameplate is
   only earned by FINISHING the mission, so dying mid-mission
   forfeits the mission and the soul must pick that vessel again.
   Returns { ok, run, earned }. */
export function die(run) {
  if (run.phase !== 'rin-life' && run.phase !== 'mission') {
    return { ok: false, run, reason: 'Nothing to die from in this phase — the soul is between lives.' };
  }
  const r = cloneRun(run);
  r.deaths += 1;
  if (run.phase === 'rin-life') {
    r.lives += 1;
    r.nameplates.push(SELF_ID);
    say(r, 'RIN died in the left flame — and the amulet saved him. The Rin Nameplate is yours.');
  } else {
    say(r, `${nameOf(run.missionCreature)} died mid-mission — the life is spent, the mission undone. Pick the face again.`);
    r.missionCreature = null;
    r.missionStep = 0;
  }
  r.phase = 'face-pick';
  return { ok: true, run: r, earned: run.phase === 'rin-life' ? SELF_ID : null };
}

/* Pick the next life on the D_FACE screen. Rules (canon):
   - Only from the face-pick phase (after a death).
   - A creature whose Nameplate you already hold is spent — the
     old vessel is never re-offered (modes.js chooseReincarnation).
   - The self ('rin', any index-2 part) is gated until all 8
     creature Nameplates are held — the ninth life is the return.
   Returns { ok, run, vessel } or { ok:false, run, reason }. */
export function reincarnate(run, eye, nose, mouth) {
  if (run.phase !== 'face-pick') {
    return { ok: false, run, reason: 'The face-pick opens only after a death.' };
  }
  const vessel = faceToCreature(eye, nose, mouth);
  if (vessel === null) {
    return { ok: false, run, reason: 'That face is not a face at all — pick one eye, one nose, one mouth.' };
  }
  if (vessel === SELF_ID) {
    const creaturesDone = CREATURE_IDS.filter((id) => run.nameplates.includes(CREATURES[id].vessel)).length;
    if (creaturesDone < 8) {
      return { ok: false, run, reason: `Your own face — not yet. ${8 - creaturesDone} creature Nameplate${8 - creaturesDone === 1 ? '' : 's'} still to earn before the soul can come home.` };
    }
    const r = cloneRun(run);
    r.current = SELF_ID;
    r.missionCreature = null;
    r.missionStep = 0;
    r.phase = 'seal';
    say(r, 'The face you assembled is your own. Rin returns — ninth life. The seal waits.');
    return { ok: true, run: r, vessel };
  }
  if (run.nameplates.includes(vessel)) {
    return { ok: false, run, reason: `${nameOf(vessel)} is spent — its Nameplate is already yours. That vessel is never offered again.` };
  }
  const r = cloneRun(run);
  r.current = vessel;
  r.missionCreature = vessel;
  r.missionStep = 0;
  r.phase = 'mission';
  const c = creatureByVessel(vessel);
  say(r, `Reborn as ${c.name} — ${c.home}. Mission: ${c.mission}`);
  return { ok: true, run: r, vessel };
}

/* Advance one mission step. When the last step is done the mission
   completes: the creature's Nameplate is earned (and any Magatamas
   the segment yields), the life is counted, and the soul is ready
   to die again. Returns { ok, run, done, earned } — done=false
   means a step was taken but the mission continues. */
export function advanceMission(run) {
  if (run.phase !== 'mission' || !run.missionCreature) {
    return { ok: false, run, reason: 'No mission is running — die and pick a face first.' };
  }
  const c = creatureByVessel(run.missionCreature);
  const r = cloneRun(run);
  r.missionStep += 1;
  if (r.missionStep < c.steps.length) {
    say(r, `${c.name} — step ${r.missionStep + 1} of ${c.steps.length}: ${c.steps[r.missionStep]}`);
    return { ok: true, run: r, done: false, earned: null };
  }
  r.lives += 1;
  r.nameplates.push(c.vessel);
  for (const m of c.magatamas) if (!r.magatamas.includes(m)) r.magatamas.push(m);
  const magText = c.magatamas.length ? ` Magatama${c.magatamas.length === 1 ? '' : 's'} earned: ${c.magatamas.map((m) => LANDS[m].element).join(', ')}.` : '';
  say(r, `${c.name}'s mission is done. The ${c.name} Nameplate is yours.${magText}`);
  r.missionCreature = null;
  r.missionStep = 0;
  r.phase = 'face-pick-ready';
  return { ok: true, run: r, done: true, earned: c.vessel };
}

/* After a mission the soul must die again to pick the next face —
   one call, no new logic: dying from 'face-pick-ready' just opens
   the face-pick (no plate, no life counted — the life was already
   counted at mission completion). */
export function dieAgain(run) {
  if (run.phase !== 'face-pick-ready') {
    return { ok: false, run, reason: 'Finish the mission first — the soul dies when its work is done.' };
  }
  const r = cloneRun(run);
  r.deaths += 1;
  r.phase = 'face-pick';
  say(r, `${nameOf(run.nameplates[run.nameplates.length - 1])}'s life ends. The face-pick opens again.`);
  return { ok: true, run: r, earned: null };
}

/* Unlock the seal on Central Mountain with the 8 creature
   Nameplates (walkthrough endgame). Rin must be the current life
   (phase 'seal' — returned as the self). */
export function unlockSeal(run) {
  if (run.phase !== 'seal') {
    return { ok: false, run, reason: 'The seal opens only once Rin has returned, ninth life.' };
  }
  const missing = CREATURE_IDS.filter((id) => !run.nameplates.includes(CREATURES[id].vessel));
  if (missing.length) {
    return { ok: false, run, reason: `The seal holds — ${missing.length} Nameplate${missing.length === 1 ? '' : 's'} missing: ${missing.map((id) => CREATURES[id].name).join(', ')}.` };
  }
  const r = cloneRun(run);
  r.sealUnlocked = true;
  r.phase = 'magatamas';
  say(r, 'The eight Nameplates turn in the seal. It opens. Gather the five Magatamas.');
  return { ok: true, run: r };
}

/* Gather a Magatama in the endgame. Water + Wood already come from
   Byou's mission and cannot be re-gathered; Metal (Helix Palace
   roof), Fire (Land of Time candle) and Earth (Central Mountain)
   are gathered here, in any order. */
export function collectMagatama(run, land) {
  if (run.phase !== 'magatamas') {
    return { ok: false, run, reason: 'The Magatamas are gathered only after the seal opens.' };
  }
  if (!MAGATAMA_LANDS.includes(land)) {
    return { ok: false, run, reason: `${land} holds no Magatama.` };
  }
  if (run.magatamas.includes(land)) {
    return { ok: false, run, reason: `The ${LANDS[land].element} Magatama is already yours.` };
  }
  const r = cloneRun(run);
  r.magatamas.push(land);
  say(r, `${LANDS[land].element} Magatama gathered — ${LANDS[land].name}, ${LANDS[land].title}. (${r.magatamas.length} of 5)`);
  if (r.magatamas.length === 5) r.phase = 'katana';
  return { ok: true, run: r };
}

/* The five Magatamas forge the Katana of Five Forces (walkthrough
   items list: "Given when you collect the five magatama"). The
   Tou-gyou emblems are consulted in the five lands in sequence on
   the way — Desire, Dreaming, Life, Time — before the blade is
   given on Central Mountain; that tour is narrated in the log. */
export function forgeKatana(run) {
  if (run.phase !== 'katana') {
    return { ok: false, run, reason: 'The Katana is forged only when all five Magatamas are gathered.' };
  }
  if (run.magatamas.length !== 5) {
    return { ok: false, run, reason: `${5 - run.magatamas.length} Magatama${5 - run.magatamas.length === 1 ? '' : 's'} still missing.` };
  }
  const r = cloneRun(run);
  say(r, 'Emblems consulted, in sequence — Desire, Dreaming, Life, Time — and back to Central Mountain.');
  r.katana = true;
  r.phase = 'shrine';
  say(r, 'The Katana of Five Forces is yours. Climb to the Octagonal Shrine Par-fang.');
  return { ok: true, run: r };
}

/* Enter the shrine through the window; use the katana, then the
   five Magatamas — and the soul is recovered. Tong-Nou is revealed
   not as a soul-devourer but as a purifier of souls. */
export function recoverSoul(run) {
  if (run.phase !== 'shrine') {
    return { ok: false, run, reason: 'The shrine waits at the top of Central Mountain — forge the Katana first.' };
  }
  if (!run.katana || run.magatamas.length !== 5) {
    return { ok: false, run, reason: 'The shrine needs the Katana of Five Forces and all five Magatamas.' };
  }
  const r = cloneRun(run);
  r.soulRecovered = true;
  r.phase = 'done';
  // No lives increment here: lives is already 9 (Rin + 8 creatures).
  // The ninth life is the return as Rin; recovering the soul ends it.
  say(r, 'The katana opens the way; the five Magatamas turn. RIN’S SOUL IS RECOVERED. Tong-Nou was never a devourer — it is a purifier of souls.');
  return { ok: true, run: r };
}

/* ---------------- Helpers ---------------- */
export function creatureByVessel(vessel) {
  for (const id of CREATURE_IDS) if (CREATURES[id].vessel === vessel) return CREATURES[id];
  return null;
}
export function nameOf(vessel) {
  if (vessel === SELF_ID) return 'RIN';
  const c = creatureByVessel(vessel);
  return c ? c.name : vessel;
}
export function creatureNameplates(run) {
  return CREATURE_IDS.filter((id) => run.nameplates.includes(CREATURES[id].vessel)).length;
}
export function livesRemaining(run) {
  return Math.max(0, 9 - run.lives);
}
export function runSummary(run) {
  return {
    phase: run.phase,
    current: run.current,
    lives: run.lives,
    livesRemaining: livesRemaining(run),
    deaths: run.deaths,
    nameplates: [...run.nameplates],
    creatureNameplates: creatureNameplates(run),
    magatamas: [...run.magatamas],
    katana: run.katana,
    sealUnlocked: run.sealUnlocked,
    soulRecovered: run.soulRecovered,
  };
}
