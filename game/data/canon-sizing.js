/* CANON SIZING (owner 2026-10-23): every fighter, every version/transformation,
   gets a canon-driven height + girth. NOT one global roster height.
   height_cm = standing height of that version in canon (Tekken body's official
   profile height as the baseline, then the Western Heart canon/bio shifts it).
   girth = width/depth multiplier ON TOP of the model's authored bulk (1 = as built).
   Runtime (game/js/canon-sizing.js) measures each model's in-fight stance height once
   and scales the fighter root so stance height = height_cm * STANCE_PER_CM.
   STANCE_PER_CM is calibrated on Pantera (King body, 200 cm): his measured stance
   height 1.634 world units at scale 1 (docs/proof/canon-sizing/), so Pantera is unchanged.
   apply:false = documented, not yet switched on in-game (needs its own proof shot).
   Doc table: docs/roster/CANON-SIZING.md. Test: test/canon-sizing.test.mjs. */
export const STANCE_PER_CM = 1.634 / 200;
export const SCALE_CLAMP = [0.55, 2.2];
export const GIRTH_CLAMP = [0.75, 1.45];

const T = (h, src) => ({ height_cm: h, girth: 1, src });
export const CANON_SIZING = {
  burger: {
    body: 'Bob', apply: true,
    canon: 'roster/burger/CANON.md (Hunger Soul; "very fat"; most transformations, up AND down) + owner 2026-10-23: default is Bob-sized (big and wide), versions vary per canon. Bob T7/T8 profile 196 cm / 155 kg.',
    versions: {
      'burger':             { height_cm: 196, girth: 1.12, src: 'A1 Demon Mode default = Bob-sized, Bob-wide (owner 2026-10-23)' },
      'burger-attire2':     { height_cm: 190, girth: 1.10, src: 'Cursed Human: as chill as he gets, faster/weaker, still fat (CANON.md Forms)' },
      'burger-attire3':     { height_cm: 188, girth: 0.95, src: 'Feral Hunger: fastest human form, feral and lean (CANON.md Forms)' },
      'burger-attire4':     { height_cm: 192, girth: 1.12, src: 'Getting Hungry: stronger but slower than human (CANON.md Forms)' },
      'burger-attire5':     { height_cm: 212, girth: 1.35, src: 'Mini Tank: body giant, short legs, big head (CANON.md Forms)' },
      'burger-attire6':     { height_cm: 186, girth: 0.90, src: 'Speed Demon: human-sized demon, fastest, weakest demon (CANON.md Forms)' },
      'burger-attire7':     { height_cm: 202, girth: 1.18, src: 'The Mouth: head overgrows the body, clumsy (CANON.md Forms)' },
      'burger-speed-demon': { height_cm: 186, girth: 0.90, src: 'Speed Demon form (transform chain)' },
      'burger-the-mouth':   { height_cm: 202, girth: 1.18, src: 'The Mouth form (transform chain)' },
      'burger-demon':       { height_cm: 236, girth: 1.30, src: 'Final form: the biggest demon, mix of all smaller forms (CANON.md Forms)' },
    },
  },
};

/* Baseline for the rest of the roster: Tekken body official profile heights
   (T8 where T7/T8 differ, per lab/game/data/characters/heights.json), with the
   Western Heart canon cue noted. Each switches to apply:true in its own proof PR. */
const BASE = {
  rin: ['Jin Kazama', 180], byou: ['Lei Wulong', 176], tou: ['Paul Phoenix', 187], sha: ['Xiaoyu', 159],
  kai: ['Eddy Gordo', 188], retsu: ['Bryan Fury', 186], zen: ['Heihachi', 179], gyou: ['Hwoarang', 181],
  pantera: ['King', 200], demonio: ['Jin Kazama', 183], phantom: ['Yoshimitsu', 178], diablo: ['Heihachi', 179],
  skull: ['Bryan Fury', 186], samura1: ['Jack-7', 235, 1.15, 'Gun Jack mech (roster_canon: Gundam/Transformer mech mashup)'],
  sakura: ['Xiaoyu', 159], zui: ['Steve Fox', 184], kinpo: ['Asuka', 160], waterfall: ['Josie Rizal', 158, 1, 'roster_canon: Josie Rizal base'],
  kingtyrant: ['Eddy Gordo', 188], awapop: ['Nina', 161], scimitar: ['Shaheen', 182], purplerain: ['Lee', 180],
  nightwolf: ['Julia', 165], dio: ['Akuma', 178], cyborgx: ['Alisa', 160, 1, 'roster_canon: Alisa base android'],
  michiko: ['Katarina', 167], star: ['Christie', 168], torch: ['Anna', 163], bruno: ['Miguel', 189],
  negativo: ['Negan', 183], thor: ['Ganryu', 183, 1.3, 'roster/thor/CANON.md: sumo frame, Burger\'s sumo brother'],
  yukihyo: ['Armor King', 195], slice: ['Dragunov', 182], docfrank: ['Bosconovitch', 160],
  'baek-master-white': ['Baek', 184], 'mariposa-monarch': ['Zafina', 172], 'dxmmii-patchwork': ['Mokujin', 175],
  charger: ['Blanka', 192, 1.15, 'Blanka body (SF profile 192 cm), beast build'],
  dorowani: ['Gon', 120, 1.1, 'roster/dorowani/README.md: small, fast, goofy, short chompy'],
  chatur: ['True Ogre', 240, 1.25], pond: ['Raven', 185], ryusan: ['Lucky Chloe', 155], tobi: ['Hwoarang', 181],
  megami: ['Jun Kazama', 163], menajerii: ['Roger Jr.', 150], kronos: ['Zangief + Golem', 211, 1.25],
  deathfang: ['Iori Yagami', 182], ryuji: ['Ryuji Yamazaki', 185], koreshi: ['Kakashi', 181], rave: ['Lei Wulong', 176],
  'buffalo-bill': ['Marshall Law', 175], vainabel: ['Bass Armstrong', 188, 1.1], cainelias: ['Undertaker', 208],
  chordz: ['Lars', 186],
};
for (const [id, [body, h, girth = 1, cue]] of Object.entries(BASE)) {
  if (CANON_SIZING[id]) continue;
  CANON_SIZING[id] = { body, apply: false,
    canon: cue || `${body} official profile height (baseline; canon study pending)`,
    versions: { [id]: { height_cm: h, girth, src: cue || `${body} profile` } } };
}

/** Size entry for a model key ('burger-attire5', 'burger-demon', ...) or null. */
export function sizingFor(modelKey) {
  for (const f of Object.values(CANON_SIZING)) {
    const v = f.versions[modelKey];
    if (v) return f.apply ? v : null;
  }
  return null;
}
