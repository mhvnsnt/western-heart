/* ============================================================
   WESTERN HEART — Daily challenges & rotating events (data)

   Challenge definitions are DATA, not code: each challenge is a
   { id, name, flavor, type, target, difficulty, reward } record.
   Rotation is deterministic: challengesFor(dateStr) seeds from the
   calendar date, so every player worldwide gets the same dailies.

   Reward hooks: completing a challenge grants an unlockable via
   js/unlockables.js (titles, portrait frames, menu flourishes).
   Progress tracking lives in js/challenges.js (ChallengeManager).

   Difficulty: 'ember' (easy) / 'flame' (medium) / 'inferno' (hard).
   ============================================================ */

/** Challenge event types the tracker understands.
   Honest mapping to engine stats (game/js/game.js matchStats):
   - wins / wins_no_block: from onMatchEnd(playerWon) + matchStats.blockTime
   - damage / damage_one_fight: from matchStats.dmgDealt (no landed-hit
     counter exists in the engine, so hit-count challenges are phrased
     as damage — documented, not fudged)
   - perfects: playerWon && matchStats.dmgTaken === 0 (flawless victory)
   - grabs / surges: from matchStats.attacks.grab / .surge (attack startups)
   - survival_wave / qombat_wave: from the ModeController's run state
   - timeattack: grade captured by wrapping _timeAttackClear (additive)
   - mode_clear: arcade/surge clears captured by wrapping _arcadeClear /
     _surgeClear (additive prototype hooks — no modes.js edit)
   - fighter_wins: playerWon + fighter id read from the mode's state */
export const CHALLENGE_TYPES = Object.freeze([
  'wins',            // win N fights (any mode)
  'wins_no_block',   // win N fights with blockTime == 0
  'damage',          // deal N total damage across fights
  'damage_one_fight',// deal N damage in a single fight
  'perfects',        // win N matches taking zero damage
  'grabs',           // start N throws
  'surges',          // activate N Soul Surges
  'survival_wave',   // reach wave N in Survival
  'timeattack',      // clear Time Attack with grade S/A/B...
  'qombat_wave',     // reach wave N in Immortal Qombat
  'fighter_wins',    // win N fights AS a specific fighter
  'mode_clear',      // clear a specific mode (arcade/surge...)
]);

/* ---------------- challenge catalog ----------------
   reward: unlockable id granted on completion (see js/unlockables.js). */
export const CHALLENGES = [
  // ---- ember (easy) ----
  { id: 'win3', name: 'FIRST BLOOD', flavor: 'The shrine notices those who show up. Win 3 fights.',
    type: 'wins', target: 3, difficulty: 'ember', reward: 'title_firstblood' },
  { id: 'hit50', name: 'THOUSAND CUTS', flavor: 'Deal 400 damage. The mountain is worn by rain, not thunder.',
    type: 'damage', target: 400, difficulty: 'ember', reward: 'frame_ember' },
  { id: 'grab5', name: 'FIND THE THROAT', flavor: 'Land 5 throws. Kingtyrant would approve.',
    type: 'grabs', target: 5, difficulty: 'ember', reward: 'title_grappler' },
  { id: 'surge1', name: 'NINE BECOME ONE', flavor: 'Unleash 1 Soul Surge.',
    type: 'surges', target: 1, difficulty: 'ember', reward: 'title_surged' },
  { id: 'surv3', name: 'THREE WAVES', flavor: 'Reach wave 3 in Survival.',
    type: 'survival_wave', target: 3, difficulty: 'ember', reward: 'title_survivor' },
  { id: 'qombat3', name: 'FEED THE SUN', flavor: 'Reach wave 3 in Immortal Qombat. Sun Rā is watching.',
    type: 'qombat_wave', target: 3, difficulty: 'ember', reward: 'title_suneater' },
  // ---- flame (medium) ----
  { id: 'win8', name: 'EIGHTFOLD PATH', flavor: 'Win 8 fights. The Trial respects persistence.',
    type: 'wins', target: 8, difficulty: 'flame', reward: 'frame_flame' },
  { id: 'hit150', name: 'STORM OF FISTS', flavor: 'Deal 1200 damage across your fights.',
    type: 'damage', target: 1200, difficulty: 'flame', reward: 'title_stormfist' },
  { id: 'hit25one', name: 'RELENTLESS', flavor: 'Deal 200 damage in a single fight. Do not let them breathe.',
    type: 'damage_one_fight', target: 200, difficulty: 'flame', reward: 'title_relentless' },
  { id: 'noblck3', name: 'NO SHIELD', flavor: 'Win 3 fights without blocking once. Footwork is a shield.',
    type: 'wins_no_block', target: 3, difficulty: 'flame', reward: 'title_noshield' },
  { id: 'grab12', name: 'CLINCH MASTER', flavor: 'Land 12 throws.',
    type: 'grabs', target: 12, difficulty: 'flame', reward: 'frame_grapple' },
  { id: 'surge5', name: 'CHANNELER', flavor: 'Unleash 5 Soul Surges.',
    type: 'surges', target: 5, difficulty: 'flame', reward: 'title_channeler' },
  { id: 'surv8', name: 'WAVE RIDER', flavor: 'Reach wave 8 in Survival.',
    type: 'survival_wave', target: 8, difficulty: 'flame', reward: 'title_waverider' },
  { id: 'ta_b', name: 'AGAINST THE CLOCK', flavor: 'Clear Time Attack with grade B or better.',
    type: 'timeattack', target: 'B', difficulty: 'flame', reward: 'title_swift' },
  { id: 'arcade_clear', name: 'LADDER CLIMBER', flavor: 'Clear Arcade mode. Diablo waits near the top.',
    type: 'mode_clear', target: 'arcade', difficulty: 'flame', reward: 'title_ladder' },
  // ---- inferno (hard) ----
  { id: 'win15', name: 'WAR GOD', flavor: 'Win 15 fights in a day. The shrine carves your name deep.',
    type: 'wins', target: 15, difficulty: 'inferno', reward: 'frame_inferno' },
  { id: 'perfect3', name: 'UNTOUCHED', flavor: 'Win 3 matches without taking a single point of damage.',
    type: 'perfects', target: 3, difficulty: 'inferno', reward: 'title_untouched' },
  { id: 'noblck8', name: 'FLESH IS ARMOR', flavor: 'Win 8 fights without blocking. Become the dodge.',
    type: 'wins_no_block', target: 8, difficulty: 'inferno', reward: 'title_fleshy' },
  { id: 'surv15', name: 'IMMORTAL', flavor: 'Reach wave 15 in Survival.',
    type: 'survival_wave', target: 15, difficulty: 'inferno', reward: 'title_immortal' },
  { id: 'ta_s', name: 'LIGHTNING', flavor: 'Clear Time Attack with grade S. Under four minutes.',
    type: 'timeattack', target: 'S', difficulty: 'inferno', reward: 'frame_lightning' },
  { id: 'surge_clear', name: 'NINE SOULS, ONE VESSEL', flavor: 'Clear the Soul Surge Gauntlet — all nine souls.',
    type: 'mode_clear', target: 'surge', difficulty: 'inferno', reward: 'title_ninesouls' },
  { id: 'qombat10', name: 'SUN EATER', flavor: 'Reach wave 10 in Immortal Qombat. The sun fears you now.',
    type: 'qombat_wave', target: 10, difficulty: 'inferno', reward: 'title_suneater2' },
  // ---- fighter-specific (rotating cast) ----
  { id: 'pantera3', name: "KING'S TRIBUTE", flavor: 'Win 3 fights as Pantera. The sole exception roars.',
    type: 'fighter_wins', target: 3, fighter: 'pantera', difficulty: 'flame', reward: 'title_pantera' },
  { id: 'torch3', name: 'TRIAL BY FIRE', flavor: 'Win 3 fights as Torch. Burn bright.',
    type: 'fighter_wins', target: 3, fighter: 'torch', difficulty: 'flame', reward: 'title_torch' },
  { id: 'dorowani3', name: 'MUD AMBUSH', flavor: 'Win 3 fights as Dorowani. Konnichiwa, arigato, bankai.',
    type: 'fighter_wins', target: 3, fighter: 'dorowani', difficulty: 'flame', reward: 'title_dorowani' },
];

export const CHALLENGE_MAP = Object.fromEntries(CHALLENGES.map((c) => [c.id, c]));

/* ---------------- weekly rotating events ----------------
   One event runs each week (Monday 00:00 local). Events boost rewards
   and add a themed bonus challenge. */
export const WEEKLY_EVENTS = [
  { id: 'surge_week', name: 'SURGE WEEK', flavor: 'Soul Surges grant double progress toward surge challenges.',
    bonus: { type: 'surges', mult: 2 } },
  { id: 'qombat_frenzy', name: 'QOMBAT FRENZY', flavor: 'Immortal Qombat waves grant double progress.',
    bonus: { type: 'qombat_wave', mult: 2 } },
  { id: 'iron_trial', name: 'IRON TRIAL', flavor: 'No-block wins grant double progress. No shield. No mercy.',
    bonus: { type: 'wins_no_block', mult: 2 } },
  { id: 'grapple_gala', name: 'GRAPPLE GALA', flavor: 'Throws grant double progress. Find the throat.',
    bonus: { type: 'grabs', mult: 2 } },
];

/* ---------------- deterministic rotation ---------------- */

/** dateStr: 'YYYY-MM-DD'. Returns a stable 32-bit seed. */
export function dateSeed(dateStr) {
  let h = 2166136261;
  for (let i = 0; i < dateStr.length; i++) {
    h ^= dateStr.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function pick(rng, arr, n) {
  const pool = arr.slice();
  const out = [];
  while (out.length < n && pool.length) {
    out.push(pool.splice(Math.floor(rng() * pool.length), 1)[0]);
  }
  return out;
}

/**
 * challengesFor(dateStr) -> { date, dailies: [challenge x3], event }.
 * Deterministic: same date -> same dailies worldwide.
 * Composition: 1 ember + 1 flame + 1 inferno, no repeats.
 */
export function challengesFor(dateStr) {
  const rng = mulberry32(dateSeed(dateStr));
  const ember = pick(rng, CHALLENGES.filter((c) => c.difficulty === 'ember'), 1);
  const flame = pick(rng, CHALLENGES.filter((c) => c.difficulty === 'flame'), 1);
  const inferno = pick(rng, CHALLENGES.filter((c) => c.difficulty === 'inferno'), 1);
  return { date: dateStr, dailies: [...ember, ...flame, ...inferno], event: eventFor(dateStr) };
}

/** Monday-based week index -> event. */
export function eventFor(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  const monday = new Date(d);
  const dow = (d.getDay() + 6) % 7; // Monday = 0
  monday.setDate(d.getDate() - dow);
  const weekSeed = dateSeed(monday.toISOString().slice(0, 10));
  return WEEKLY_EVENTS[weekSeed % WEEKLY_EVENTS.length];
}

/** Today's date as 'YYYY-MM-DD' in local time. */
export function todayStr(d = new Date()) {
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}
