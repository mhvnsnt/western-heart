/* ============================================================
   WESTERN HEART — Game Modes
   Round-1: VERSUS · ARCADE · STORY (reincarnation) · TRAINING
   Round-2 (Lane G): SURVIVAL · TIME ATTACK · TEAM BATTLE (Tekken,
   researched — docs/modes/TEKKEN-MODES-RESEARCH.md) ·
   不死クォンバット · SOUL SURGE GAUNTLET · TRADER'S MIMIC
   (WH originals, grounded in CANON.md — cited per mode)

   Canon grounding (CANON.md):
   • Versus = no reincarnation.
   • Story/career = death forces REINCARNATION — "death is not
     failure. It is the mechanism." Your actions influence who you
     become next — "that is the entire game."
   • The nine souls: RIN, BYOU, TOU, SHA, KAI, JIN, RETSU, ZEN, GYOU.
   • Diablo is an INTRUDER (not one of the nine). He may take an
     interest in a soul that keeps dying.
   • Final boss = the Assembled Soul — "It is you, assembled."
     A composite of all nine fighting styles, including yours.
   • The Trial ladder: Tree of Life (Wood) → Plains of Chi-U (Fire) →
     Octagonal Shrine (Earth) → Helix Palace (Metal) → Palace of
     Dreaming (Water) → Phantom Marketplace (the Trader: trade one
     force for another) → the Shrine (final ascent).

   The top half of this file (FORCES, ladders, reincarnation math) is
   DOM-free and unit-testable in node. ModeController wires it to the
   DOM and the Game.
   ============================================================ */

/* ---------------- The Five Forces ----------------
   Canon rewards for claiming each land. Engine translation is honest:
   • WOOD  — "your reach extends"      → hitbox radius × 1.30
   • FIRE  — "strikes chip through guard" → chip damage × 2.2
   • EARTH — "your defense solidifies" → defense × 1.30
   • METAL — "you regenerate"           → +1 HP/s in-fight regen
     (rounds already reset HP to full, so the Trial's between-rounds
     healing becomes wounds closing as you fight)
   • WATER — "your movement quickens"  → walk speed × 1.25          */
export const FORCES = {
  wood:  { key: 'wood',  name: 'WOOD',  land: 'TREE OF LIFE',
           desc: 'Reach extends — your strikes land from further out.',
           apply: (s) => ({ ...s, reachMult: (s.reachMult || 1) * 1.30 }) },
  fire:  { key: 'fire',  name: 'FIRE',  land: 'PLAINS OF CHI-U',
           desc: 'Strikes chip through guard — blocking bleeds.',
           apply: (s) => ({ ...s, chipMult: (s.chipMult || 1) * 2.2 }) },
  earth: { key: 'earth', name: 'EARTH', land: 'OCTAGONAL SHRINE',
           desc: 'Defense solidifies — you take less damage.',
           apply: (s) => ({ ...s, defense: s.defense * 1.30 }) },
  metal: { key: 'metal', name: 'METAL', land: 'HELIX PALACE',
           desc: 'Regenerate — wounds close as you fight (+1 HP/s).',
           apply: (s) => ({ ...s, regenPerSec: (s.regenPerSec || 0) + 1 }) },
  water: { key: 'water', name: 'WATER', land: 'PALACE OF DREAMING',
           desc: 'Movement quickens — walk speed surges.',
           apply: (s) => ({ ...s, speed: Math.min(3.5, s.speed * 1.25) }) },
};
export const FORCE_ORDER = ['wood', 'fire', 'earth', 'metal', 'water'];

/* Default stats mirror Fighter's fallback (fighter.js). */
export const BASE_STATS = { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 };

/* Apply a list of claimed force keys onto a base stats object.
   Returns a NEW object — never mutates the roster entry. */
export function applyForces(baseStats, forceKeys) {
  let s = { ...(baseStats || BASE_STATS) };
  for (const k of forceKeys || []) {
    const f = FORCES[k];
    if (f) s = f.apply(s);
  }
  return s;
}

/* ---------------- Story ladder (canon: The Trial) ---------------- */
export const STORY_STAGES = [
  { n: 1, key: 'wood', title: 'STAGE 1 — TREE OF LIFE',
    sub: 'Where souls begin. The Trial opens its eyes.',
    pool: ['pantera', 'demonio', 'skull', 'zui', 'sakura', 'michiko'], diff: 0.55 },
  { n: 2, key: 'fire', title: 'STAGE 2 — PLAINS OF CHI-U',
    sub: 'Confrontation under a burning sky.',
    pool: ['tou', 'retsu', 'bruno', 'thor', 'kingtyrant', 'slice'], diff: 0.62 },
  { n: 3, key: 'earth', title: 'STAGE 3 — OCTAGONAL SHRINE',
    sub: 'The source. The shrine stones are watching.',
    pool: ['zen', 'demonio', 'yukihyo', 'docfrank', 'purplerain'], diff: 0.68 },
  { n: 4, key: 'metal', title: 'STAGE 4 — HELIX PALACE',
    sub: 'Desire has five glowing rooms. Walk through all of them.',
    pool: ['samura1', 'cyborgx', 'burger', 'scimitar', 'negativo'], diff: 0.74 },
  { n: 5, key: 'water', title: 'STAGE 5 — PALACE OF DREAMING',
    sub: 'Change is the only law. The walls will not stay still.',
    pool: ['phantom', 'dio', 'nightwolf', 'star', 'awapop', 'kinpo'], diff: 0.80 },
  { n: 6, key: 'trade', title: 'STAGE 6 — PHANTOM MARKETPLACE',
    sub: 'The Trader buys and sells elemental forces. All transactions are final.',
    pool: ['scimitar', 'burger', 'awapop', 'slice'], diff: 0.85, trader: true },
  { n: 7, key: 'boss', title: 'FINAL — THE SHRINE',
    sub: 'The Assembled Soul waits. It is you, assembled.',
    pool: [], diff: 0.95, boss: true },
];

/* ---------------- Arcade ladder ----------------
   6 fights. No reincarnation — one life, classic rules. */
export const ARCADE_LADDER = [
  { n: 1, diff: 0.50, boss: false },
  { n: 2, diff: 0.58, boss: false },
  { n: 3, diff: 0.66, boss: false },
  { n: 4, diff: 0.74, boss: false },
  { n: 5, diff: 0.85, boss: false, fixed: 'diablo', name: 'DIABLO — SUB-BOSS' },
  { n: 6, diff: 0.95, boss: true, name: 'ASSEMBLED SOUL — FINAL' },
];

/* ---------------- Reincarnation ----------------
   Canon: "death is not failure. It is the mechanism." When a soul
   loses, it dies and returns in a new vessel. The new vessel is
   INFLUENCED BY the soul's actions — that is the entire game.

   We track a style profile per story run and score every roster
   vessel against it. Diablo (the intruder) only offers himself to
   souls that have died 3+ times — "the membrane let him in."  */
export const VESSEL_AFFINITY = {
  pantera:   { aggro: .7, grapple: 1,  defense: 0,  trick: 0,  surge: 0  },
  skull:     { aggro: 1,  grapple: .3, defense: 0,  trick: 0,  surge: 0  },
  dio:       { aggro: 1,  grapple: 0,  defense: 0,  trick: .2, surge: .4 },
  tou:       { aggro: .9, grapple: .4, defense: 0,  trick: 0,  surge: 0  },
  retsu:     { aggro: .8, grapple: .2, defense: 0,  trick: 0,  surge: 0  },
  negativo:  { aggro: .9, grapple: .2, defense: 0,  trick: .2, surge: 0  },
  kingtyrant:{ aggro: .5, grapple: .8, defense: 0,  trick: .3, surge: 0  },
  burger:    { aggro: .6, grapple: .5, defense: 0,  trick: 0,  surge: 0  },
  yukihyo:   { aggro: 0,  grapple: .6, defense: .6, trick: 0,  surge: 0  },
  demonio:   { aggro: .5, grapple: 0,  defense: .6, trick: .2, surge: .2 },
  rin:       { aggro: .4, grapple: .2, defense: .4, trick: .4, surge: .2 },
  thor:      { aggro: .2, grapple: .3, defense: .7, trick: 0,  surge: 0  },
  bruno:     { aggro: .3, grapple: .3, defense: .6, trick: 0,  surge: 0  },
  michiko:   { aggro: .3, grapple: 0,  defense: .5, trick: .3, surge: 0  },
  zen:       { aggro: 0,  grapple: 0,  defense: 1,  trick: .2, surge: 0  },
  waterfall: { aggro: .3, grapple: 0,  defense: .7, trick: .3, surge: 0  },
  samura1:   { aggro: .4, grapple: .2, defense: .6, trick: 0,  surge: 0  },
  zui:       { aggro: .3, grapple: 0,  defense: .4, trick: 1,  surge: 0  },
  byou:      { aggro: .2, grapple: 0,  defense: .3, trick: .8, surge: 0  },
  phantom:   { aggro: .3, grapple: 0,  defense: .2, trick: .8, surge: .5 },
  jin_soul:  { aggro: .3, grapple: 0,  defense: .2, trick: .7, surge: .2 },
  sakura:    { aggro: .3, grapple: 0,  defense: .3, trick: .7, surge: 0  },
  kinpo:     { aggro: .4, grapple: 0,  defense: .3, trick: .7, surge: 0  },
  awapop:    { aggro: .2, grapple: 0,  defense: .3, trick: .7, surge: .2 },
  sha:       { aggro: .2, grapple: 0,  defense: .4, trick: .8, surge: 0  },
  star:      { aggro: .3, grapple: 0,  defense: .2, trick: .7, surge: 0  },
  nightwolf: { aggro: .4, grapple: .2, defense: 0,  trick: .6, surge: 0  },
  purplerain:{ aggro: .3, grapple: 0,  defense: .2, trick: .6, surge: 0  },
  scimitar:  { aggro: .5, grapple: .2, defense: 0,  trick: .5, surge: 0  },
  slice:     { aggro: .5, grapple: .2, defense: 0,  trick: .4, surge: 0  },
  docfrank:  { aggro: .2, grapple: 0,  defense: .3, trick: .5, surge: 0  },
  kai:       { aggro: .6, grapple: .2, defense: 0,  trick: .4, surge: 0  },
  gyou:      { aggro: .4, grapple: 0,  defense: 0,  trick: .9, surge: .3 },
  cyborgx:   { aggro: .3, grapple: 0,  defense: .4, trick: .5, surge: .2 },
  torch:     { aggro: .5, grapple: 0,  defense: .2, trick: .3, surge: 0  },
  diablo:    { aggro: 1,  grapple: .3, defense: .3, trick: 0,  surge: .3 }, // intruder: deaths>=3 gate
};

/* Build a style profile (all 0..1) from accumulated match stats. */
export function styleProfile(acc) {
  const a = acc || {};
  const attacks = (a.punch || 0) + (a.kick || 0) + (a.grab || 0) + (a.surge || 0);
  const t = Math.max(1, a.time || 1);
  const clamp01 = (x) => Math.max(0, Math.min(1, x));
  return {
    aggro:   clamp01((attacks / t) / 3),                 // ~3 attacks/sec = full aggro
    grapple: clamp01((a.grab || 0) / Math.max(1, attacks)),
    defense: clamp01((a.blockTime || 0) / t),
    trick:   clamp01((a.dodge || 0) / Math.max(1, attacks)) * 0.7
           + clamp01(((a.blockTime || 0) / t)) * 0.3,
    surge:   clamp01((a.surge || 0) / 3),                // 3 surges in a run = surge-hungry
  };
}

/* Pick 3 reincarnation candidates. Pure: (profile, rosterIds, currentId, deaths) -> [ids].
   The soul's actions weight the draw; a small deterministic jitter
   (seeded by deaths) breaks ties without pure randomness. */
export function chooseReincarnation(profile, rosterIds, currentId, deaths) {
  const scored = [];
  for (const id of rosterIds) {
    if (id === currentId) continue;               // the old vessel is gone
    const aff = VESSEL_AFFINITY[id];
    if (!aff) continue;
    if (id === 'diablo' && (deaths || 0) < 3) continue; // the intruder waits
    let s = 0;
    for (const k of ['aggro', 'grapple', 'defense', 'trick', 'surge']) {
      s += (profile[k] || 0) * (aff[k] || 0);
    }
    // tie-break jitter seeded by deaths — stable per death, not per frame
    const j = (((id.length * 37 + (deaths || 0) * 91) % 100) / 100) * 0.05;
    scored.push({ id, s: s + j });
  }
  scored.sort((a, b) => b.s - a.s);
  return scored.slice(0, 3).map((x) => x.id);
}

/* Explain (canon-flavored) WHY a vessel is offered for a profile. */
export function reincarnationReason(id, profile) {
  const aff = VESSEL_AFFINITY[id] || {};
  if (id === 'diablo') return 'The intruder has been watching you die. He offers his strength — at a price the shrine stones will not name.';
  const best = Object.entries(aff).sort((a, b) => b[1] - a[1])[0];
  const map = {
    aggro:   'You fought like battle itself. This vessel remembers nothing but the clinch.',
    grapple: 'Your hands kept finding throats. This vessel was built for the hold.',
    defense: 'You endured. You outlasted. This vessel is a wall that learned to punch.',
    trick:   'You were never where the blow landed. This vessel moves wrong on purpose.',
    surge:   'You reached for the other souls mid-fight. This vessel reaches back.',
  };
  return map[best ? best[0] : 'aggro'] || map.aggro;
}

/* ---------------- The Assembled Soul (final boss) ----------------
   Canon: "a composite of all nine fighting styles — including yours.
   It is every vessel at once. It is you, assembled."
   Built at runtime from the PLAYER's entry: your model, your moveset,
   darkened colors, boosted stats, merciless AI. No new assets. */
export function buildAssembledSoul(playerChar) {
  const stats = { ...(playerChar.stats || BASE_STATS) };
  stats.power = (stats.power || 1.1) * 1.35;
  stats.defense = (stats.defense || 1.05) * 1.20;
  stats.speed = Math.min(3.5, (stats.speed || 2.8) * 1.15);
  return {
    id: 'assembled-soul',
    name: 'ASSEMBLED SOUL',
    title: 'Yourself, Assembled',
    base: playerChar.base || 'You',
    moveset: playerChar.moveset || 'jin',
    model: playerChar.model || 'pantera',
    tintStrength: 0.65,
    colors: { suit: 0x0a0a14, trim: 0xb28dff },
    style: 'All Nine Styles',
    surge: { name: 'BECOME WHOLE', color: 0xb28dff, accent: 0xffffff },
    stats,
    ai: { aggression: 0.95, grabBias: 0.30, reaction: 0.90 },
  };
}

/* CPU personality scaled by ladder difficulty (0..1). */
export function scaledAi(char, diff) {
  const base = char.ai || { aggression: 0.6, grabBias: 0.15, reaction: 0.55 };
  const d = Math.max(0.15, Math.min(1, diff));
  return {
    aggression: Math.min(1, base.aggression * (0.6 + d * 0.7)),
    grabBias: base.grabBias ?? 0.15,
    reaction: Math.min(1, base.reaction * (0.5 + d * 0.8)),
  };
}

/* ============================================================
   ModeController — DOM + Game wiring. Constructed once in main.js.
   ============================================================ */

/* ---------------- Mode registry (Round-2: Lane G) ----------------
   Every playable mode, one entry. origin: 'tekken' = researched from
   the Tekken series (see docs/modes/TEKKEN-MODES-RESEARCH.md);
   'wh' = original Western Heart mode grounded in CANON.md (cited). */
export const MODE_LIST = [
  { key: 'arcade',    name: 'ARCADE',              origin: 'tekken', debut: 'Tekken',
    desc: 'Climb the 6-fight ladder. One life. Diablo waits near the top.' },
  { key: 'versus',    name: 'VERSUS',              origin: 'tekken', debut: 'Tekken',
    desc: 'Two players, best of 3. No reincarnation.' },
  { key: 'story',     name: 'STORY',               origin: 'wh', canon: 'CANON.md §5 The Trial',
    desc: 'Walk the Trial. Death is not the end — it is reincarnation.' },
  { key: 'training',  name: 'TRAINING',            origin: 'tekken', debut: 'Tekken (Practice)',
    desc: 'Endless rounds vs a passive dummy. H toggles hints.' },
  { key: 'survival',  name: 'SURVIVAL',            origin: 'tekken', debut: 'Tekken 2',
    desc: 'Endless one-round fights. Health carries over — a little back per win. How many can you beat?' },
  { key: 'timeattack', name: 'TIME ATTACK',        origin: 'tekken', debut: 'Tekken 2',
    desc: '8 fights against the clock. Fastest total time wins. Graded S/A/B/C.' },
  { key: 'team',      name: 'TEAM BATTLE',         origin: 'tekken', debut: 'Tekken 2',
    desc: '3v3. Winner stays on with carried health. Last team standing.' },
  { key: 'qombat',    name: '不死クォンバット',        origin: 'wh', canon: 'CANON.md § SUN RĀ',
    desc: "Sun Rā's pocket realm. Endless waves, no reincarnation — win and eat, lose and be eaten." },
  { key: 'surge',     name: 'SOUL SURGE GAUNTLET', origin: 'wh', canon: 'CANON.md §4 The Nine-Soul Meter',
    desc: '9 fights — each one channeling a different soul of the nine through you.' },
  { key: 'trader',    name: "TRADER'S MIMIC",      origin: 'wh', canon: 'CANON.md §5 The Trader',
    desc: "A 3-bout duel at the Phantom Marketplace. The Trader wears your moveset like a borrowed coat." },
];

/* ---------------- Records (localStorage, guarded) ---------------- */
const REC_KEY = 'wh_records';
export function whGetRecords() {
  try { return JSON.parse(localStorage.getItem(REC_KEY)) || {}; }
  catch { return {}; }
}
export function whSetRecord(k, v) {
  try {
    const r = whGetRecords();
    r[k] = v;
    localStorage.setItem(REC_KEY, JSON.stringify(r));
  } catch { /* private mode — records just don't persist */ }
}

/* ---------------- Survival (Tekken 2+) ----------------
   One round per fight, HP carries over, small restore per win. */
export const SURVIVAL_CFG = { restore: 0.25, roundsToWin: 1 };
export function survivalCarry(hpLeft, maxHp) {
  return Math.min(maxHp, hpLeft + maxHp * SURVIVAL_CFG.restore);
}

/* ---------------- Time Attack (Tekken 2+) ----------------
   8 single-round fights, total wall-clock time, S/A/B/C grades. */
export const TIME_ATTACK_CFG = { fights: 8, roundsToWin: 1 };
export function timeAttackGrade(totalMs) {
  if (totalMs < 4 * 60 * 1000) return 'S';
  if (totalMs < 6 * 60 * 1000) return 'A';
  if (totalMs < 9 * 60 * 1000) return 'B';
  return 'C';
}
export function fmtTime(ms) {
  const s = Math.floor(ms / 1000);
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}.${Math.floor((ms % 1000) / 100)}`;
}

/* ---------------- Team Battle (Tekken 2–TTT2) ----------------
   3v3, winner stays on, winner's HP carries with a small recovery. */
export const TEAM_CFG = { size: 3, restore: 0.15 };
export function teamCarry(hpLeft, maxHp) {
  return Math.min(maxHp, hpLeft + maxHp * TEAM_CFG.restore);
}

/* ---------------- Immortal Qombat / 不死クォンバット (WH original) ----------------
   Canon (SUN RĀ): endless death-tournament waves in the pocket realm
   "where the trial's rules don't apply" — no reincarnation. Win: you
   eat (HP restore + stacking power — the eater grows). Lose: absorbed. */
export const QOMBAT_CFG = { restore: 0.35, absorbPower: 0.05, roundsToWin: 1, stage: 'plains-of-chi-u' };
export function qombatCarry(hpLeft, maxHp) {
  return Math.min(maxHp, hpLeft + maxHp * QOMBAT_CFG.restore);
}
export function qombatBuff(stats, wave) {
  const s = { ...(stats || BASE_STATS) };
  s.power = (s.power || 1.1) * (1 + QOMBAT_CFG.absorbPower * wave);
  return s;
}
export function qombatDiff(wave) {
  return Math.min(0.98, 0.50 + wave * 0.06);
}

/* ---------------- Soul Surge Gauntlet (WH original) ----------------
   Canon (§4 The Nine-Soul Meter): "a fighter can invoke a Soul Surge —
   channeling one of the other eight souls for ten seconds, borrowing its
   signature techniques." The gauntlet walks all nine souls — each fight
   opens with one soul channeling through you for the whole bout.
   Engine translations are drawn from each soul's canon nature. */
export const SURGE_BLESSINGS = [
  { soul: 'rin',   kanji: '凛', apply: (s) => ({ ...s, defense: s.defense * 1.25 }),
    line: 'RIN channels through you — dignified, cold, self-possessed. Your guard hardens.' },
  { soul: 'byou',  kanji: '病', apply: (s) => ({ ...s, speed: Math.min(3.5, s.speed * 1.20) }),
    line: 'BYOU channels through you — sickness moves wrong. So do you.' },
  { soul: 'tou',   kanji: '闘', apply: (s) => ({ ...s, power: s.power * 1.25 }),
    line: 'TOU channels through you — battle itself. Your strikes are the argument.' },
  { soul: 'sha',   kanji: '沙', apply: (s) => ({ ...s, chipMult: (s.chipMult || 1) * 2 }),
    line: 'SHA channels through you — sand erodes mountains. Even blocked strikes wear them down.' },
  { soul: 'kai',   kanji: '海', apply: (s) => ({ ...s, speed: Math.min(3.5, s.speed * 1.10), regenPerSec: (s.regenPerSec || 0) + 0.5 }),
    line: 'KAI channels through you — the sea does not stop. Your wounds close as you move.' },
  { soul: 'jin',   kanji: '刃', apply: (s) => ({ ...s, power: s.power * 1.15, reachMult: (s.reachMult || 1) * 1.15 }),
    line: 'JIN channels through you — the blade. Precise, ritual, terrifying.' },
  { soul: 'retsu', kanji: '烈', apply: (s) => ({ ...s, power: s.power * 1.30, defense: s.defense * 0.90 }),
    line: 'RETSU channels through you — pure violence. Hit harder. Bleed easier.' },
  { soul: 'zen',   kanji: '禅', apply: (s) => ({ ...s, defense: s.defense * 1.30, speed: s.speed * 0.95 }),
    line: 'ZEN channels through you — stillness. Barely move. Do not need to.' },
  { soul: 'gyou',  kanji: '行', apply: (s) => ({ ...s, speed: Math.min(3.5, s.speed * 1.25) }),
    line: 'GYOU channels through you — motion itself. Cannot stop moving.' },
];
export function surgeBlessing(idx) { return SURGE_BLESSINGS[idx % SURGE_BLESSINGS.length]; }

/* ---------------- Trader's Mimic (WH original) ----------------
   Canon (§5 The Trader): "The Trader's fighting style is mimicry — it
   wears the opponent's moveset like a borrowed coat." 3 single-round
   bouts at the Phantom Marketplace: bout 1 a borrowed coat, bout 2 YOUR
   coat, bout 3 your coat worn better (buffed). */
export const TRADER_CFG = { bouts: 3, roundsToWin: 1, stage: 'phantom-marketplace' };
export function traderFoe(playerChar, bout, randomMoveset) {
  const buff = bout === 2 ? 1.15 : 1.0;
  const stats = { ...(playerChar.stats || BASE_STATS) };
  stats.power = (stats.power || 1.1) * buff;
  stats.defense = (stats.defense || 1.05) * buff;
  return {
    id: 'trader',
    name: 'THE TRADER',
    title: 'The Marketplace',
    base: 'Wears your coat',
    moveset: bout === 0 ? randomMoveset : (playerChar.moveset || 'jin'),
    model: 'scimitar', // marketplace-born vizier's frame; the Trader was already there
    colors: { suit: 0x1a0a2a, trim: 0xffd700 },
    style: 'Mimicry',
    stats,
    ai: { aggression: 0.70 + bout * 0.10, grabBias: 0.20, reaction: 0.75 + bout * 0.08 },
  };
}
export class ModeController {
  constructor(deps) {
    this.game = deps.game;
    this.ui = deps.ui;
    this.show = deps.show;
    this.startFight = deps.startFight;
    this.roster = deps.roster;
    this.getChar = deps.getChar;
    this.audio = deps.audio;
    this.mode = null;          // 'versus' | 'arcade' | 'story' | 'training'
    this.vsStep = 0;           // versus: 0 = P1 picks, 1 = P2 picks
    this.vsP1 = null;
    this.arcade = null;        // { idx, fighterId, wins }
    this.story = null;         // { stage, forces, deaths, vesselId, acc, startTime }
    this.training = null;      // { fighterId }
    // Round-2 (Lane G): tekken modes + canon-original modes
    this.survival = null;      // { wave, fighterId, hp }
    this.timeattack = null;    // { idx, fighterId, totalMs, fightStart, _watch }
    this.team = null;          // { pTeam, cTeam, pIdx, cIdx, pHp, cHp }
    this.qombat = null;        // { wave, fighterId, hp, powerMult }
    this.surge = null;         // { idx, fighterId }
    this.trader = null;        // { bout, fighterId }
    this._teamTray = null;
    this._teamPending = [];
    this._el = (id) => document.getElementById(id);
  }

  /* ---------- mode entry (called from menu buttons) ---------- */
  clearState() {
    if (this.timeattack && this.timeattack._watch) { clearInterval(this.timeattack._watch); }
    this.mode = null;
    this.vsStep = 0; this.vsP1 = null; this._lastVersus = null;
    this.arcade = null; this.story = null; this.training = null;
    this.survival = null; this.timeattack = null; this.team = null;
    this.qombat = null; this.surge = null; this.trader = null;
    this._teamPending = [];
    if (this._teamTray) { this._teamTray.remove(); this._teamTray = null; }
    this.game.onMatchEnd = null;
    this.game.training = false;
    this._badge('');
    this._showQuit(false);
  }
  startMode(mode) {
    this.clearState();
    this.mode = mode;
    const hint = this._el('select-hint');
    this.show('select');
    if (!hint) return;
    if (mode === 'versus') {
      hint.textContent = 'VERSUS — no reincarnation. Player 1: choose your soul.';
    } else if (mode === 'arcade') {
      hint.textContent = 'ARCADE — climb the 6-fight ladder. One life. Diablo waits at the top… almost.';
    } else if (mode === 'story') {
      hint.textContent = 'STORY — choose your soul. Death is not the end. It is reincarnation.';
    } else if (mode === 'training') {
      hint.textContent = 'TRAINING — pick your fighter. The dummy will not fight back. H toggles hints.';
    } else if (mode === 'survival') {
      hint.textContent = 'SURVIVAL — pick your fighter. One round each, health carries over. How many can you beat?';
    } else if (mode === 'timeattack') {
      hint.textContent = 'TIME ATTACK — pick your fighter. 8 fights, one round each, against the clock. Go fast.';
    } else if (mode === 'team') {
      hint.textContent = 'TEAM BATTLE — pick 3 fighters for your team. Winner stays on.';
      this._teamTrayBuild();
    } else if (mode === 'qombat') {
      hint.textContent = '不死クォンバット — pick your soul. Sun Rā\'s realm. No reincarnation here. Win and eat — or be eaten.';
    } else if (mode === 'surge') {
      hint.textContent = 'SOUL SURGE GAUNTLET — pick your vessel. Nine fights. Nine souls will channel through you.';
    } else if (mode === 'trader') {
      hint.textContent = 'TRADER\'S MIMIC — pick your fighter. Three bouts. The Trader wears your moveset like a borrowed coat.';
    }
  }

  /* ---------- character-select confirm routing ---------- */
  onConfirm(selectedId) {
    if (!selectedId) return false;
    if (this.mode === 'versus' && this.vsStep === 0) {
      this.vsP1 = selectedId;
      this.vsStep = 1;
      document.querySelectorAll('.char-card').forEach((x) => x.classList.remove('selected'));
      const confirmBtn = this._el('confirm-fighter');
      if (confirmBtn) confirmBtn.disabled = true;
      const hint = this._el('select-hint');
      if (hint) hint.textContent = 'VERSUS — Player 2: choose your soul.';
      this.audio && this.audio.uiClick && this.audio.uiClick();
      return false; // flow continues; main.js must clear its selectedChar
    }
    if (this.mode === 'versus') {
      const p1 = this.vsP1, p2 = selectedId;
      this.vsStep = 0; this.vsP1 = null;
      this._beginVersus(p1, p2);
      return true;
    }
    if (this.mode === 'arcade') {
      this.arcade = { idx: 0, fighterId: selectedId, wins: 0 };
      this._arcadeNext();
      return true;
    }
    if (this.mode === 'story') {
      this.story = { stage: 0, forces: [], deaths: 0, vesselId: selectedId, acc: this._newAcc(), startTime: Date.now() };
      this._storyStageIntro();
      return true;
    }
    if (this.mode === 'training') {
      this.training = { fighterId: selectedId };
      this._beginTraining(selectedId);
      return true;
    }
    if (this.mode === 'survival') {
      this.survival = { wave: 0, fighterId: selectedId, hp: null };
      this._survivalNext();
      return true;
    }
    if (this.mode === 'timeattack') {
      this.timeattack = { idx: 0, fighterId: selectedId, totalMs: 0, fightStart: 0, _watch: null };
      this._timeAttackNext();
      return true;
    }
    if (this.mode === 'team') {
      // 3-pick flow: collect the team, then start. Duplicates refused.
      if (!this._teamPending.includes(selectedId)) this._teamPending.push(selectedId);
      this._teamTrayRender();
      this.audio && this.audio.uiClick && this.audio.uiClick();
      if (this._teamPending.length >= TEAM_CFG.size) {
        const pTeam = this._teamPending.slice(0, TEAM_CFG.size);
        const cTeam = this._teamBuildCpu(pTeam);
        this.team = { pTeam, cTeam, pIdx: 0, cIdx: 0, pHp: null, cHp: null };
        if (this._teamTray) { this._teamTray.remove(); this._teamTray = null; }
        this._teamFight();
        return true;
      }
      const hint = this._el('select-hint');
      if (hint) hint.textContent = `TEAM BATTLE — pick fighter ${this._teamPending.length + 1} of ${TEAM_CFG.size}.`;
      document.querySelectorAll('.char-card').forEach((x) => x.classList.remove('selected'));
      const confirmBtn = this._el('confirm-fighter');
      if (confirmBtn) confirmBtn.disabled = true;
      return false; // flow continues; main.js must clear its selectedChar
    }
    if (this.mode === 'qombat') {
      this.qombat = { wave: 0, fighterId: selectedId, hp: null, powerMult: 1 };
      this._qombatNext();
      return true;
    }
    if (this.mode === 'surge') {
      this.surge = { idx: 0, fighterId: selectedId };
      this._surgeNext();
      return true;
    }
    if (this.mode === 'trader') {
      this.trader = { bout: 0, fighterId: selectedId };
      this._traderNext();
      return true;
    }
    return false;
  }

  /* ---------- VERSUS: no reincarnation, best of 3 ---------- */
  _beginVersus(p1id, p2id) {
    const p1 = this.getChar(p1id), p2 = this.getChar(p2id);
    if (!p1 || !p2) return;
    this._lastVersus = [p1id, p2id];
    this._badge(`VERSUS · ${p1.name} VS ${p2.name}`);
    this.game.onMatchEnd = (won) => this._versusEnd(won);
    this.startFight(p1id, p2id, { mode: 'versus' });
  }
  _versusEnd(playerWon) {
    this.game.onMatchEnd = null;
    this.ui.matchOver(playerWon); // classic result screen: REMATCH / MENU
  }
  rematch() {
    // Re-run the current mode's fight setup.
    if (this.mode === 'versus' && this._lastVersus) {
      this._beginVersus(this._lastVersus[0], this._lastVersus[1]);
    } else if (this.mode === 'arcade' && this.arcade) {
      this._arcadeFight();
    } else if (this.mode === 'story' && this.story) {
      this._storyFight();
    } else if (this.mode === 'training' && this.training) {
      this._beginTraining(this.training.fighterId);
    }
  }

  /* ---------- ARCADE: 6-fight ladder, one life ---------- */
  _arcadeNext() {
    const rung = ARCADE_LADDER[this.arcade.idx];
    if (!rung) { this._arcadeClear(); return; }
    const player = this.getChar(this.arcade.fighterId);
    let foe, foeName;
    if (rung.boss) {
      foe = buildAssembledSoul(player);
      foeName = 'ASSEMBLED SOUL';
    } else if (rung.fixed) {
      foe = this.getChar(rung.fixed);
      foeName = (rung.name || foe.name);
    } else {
      foe = this._pickFoe(this.arcade.fighterId, null, rung.diff);
      foeName = foe.name;
    }
    const foeEntry = { ...foe, ai: scaledAi(foe, rung.diff) };
    this._badge(`ARCADE · FIGHT ${rung.n}/6 · ${foeName}`);
    this.ui.banner(`FIGHT ${rung.n} — ${foeName}`);
    this.game.onMatchEnd = (won) => this._arcadeEnd(won);
    this._arcadeFoe = foeEntry;
    this.startFight(this.arcade.fighterId, null, { mode: 'arcade', enemyChar: foeEntry });
  }
  _arcadeFight() { // rematch current rung
    const rung = ARCADE_LADDER[this.arcade.idx];
    this._badge(`ARCADE · FIGHT ${rung.n}/6`);
    this.game.onMatchEnd = (won) => this._arcadeEnd(won);
    this.startFight(this.arcade.fighterId, null, { mode: 'arcade', enemyChar: this._arcadeFoe });
  }
  _arcadeEnd(won) {
    if (won) {
      this.arcade.wins++;
      this.arcade.idx++;
      this._arcadeNext();
    } else {
      this._modeWin(false, 'GAME OVER', 'The ladder stands. The shrine is silent. Climb again.',
        [{ label: 'RETRY LADDER', fn: () => { this.arcade.idx = 0; this.arcade.wins = 0; this._arcadeNext(); } }]);
    }
  }
  _arcadeClear() {
    this._modeWin(true, 'ARCADE CLEARED', 'Six fights. One soul. The shrine remembers your name.', []);
  }

  /* ---------- STORY: the Trial + reincarnation ---------- */
  _storyStageIntro() {
    const st = STORY_STAGES[this.story.stage];
    if (!st) { this._storyComplete(); return; }
    this._el('stage-kicker').textContent = this.story.deaths > 0
      ? `DEATH ${this.story.deaths} BEHIND YOU · THE SOUL CONTINUES` : 'THE TRIAL BEGINS';
    this._el('stage-title').textContent = st.title;
    this._el('stage-sub').textContent = st.sub;
    const reward = st.key === 'trade' ? 'THE TRADER — trade one force for another'
      : st.key === 'boss' ? 'THE KATANA OF FIVE FORCES — become whole'
      : `CLAIM ${FORCES[st.key].name} — ${FORCES[st.key].desc}`;
    this._el('stage-reward').textContent = reward;
    const foeName = st.boss ? 'ASSEMBLED SOUL' : 'A VESSEL OF THE TRIAL';
    this._el('stage-foe').textContent = 'Opponent: ' + foeName;
    const fl = document.getElementById('stage-forces');
    if (fl) fl.textContent = 'FORCES HELD: ' + (this.story.forces.length ? this.story.forces.map((k) => FORCES[k].name).join(' · ') : 'none yet');
    this._badge(`STORY · ${st.title}`);
    this.show('stage');
    const btn = this._el('stage-fight');
    if (btn) btn.onclick = () => {
      this.audio && this.audio.uiClick && this.audio.uiClick();
      if (st.trader) this._traderScreen();
      else this._storyFight();
    };
  }
  _storyFight() {
    const st = STORY_STAGES[this.story.stage];
    const vessel = this.getChar(this.story.vesselId);
    const buffed = { ...vessel, stats: applyForces(vessel.stats, this.story.forces) };
    let foeEntry;
    if (st.boss) foeEntry = { ...buildAssembledSoul(vessel), ai: scaledAi(buildAssembledSoul(vessel), st.diff) };
    else {
      const foe = this._pickFoe(this.story.vesselId, st.pool, st.diff);
      foeEntry = { ...foe, ai: scaledAi(foe, st.diff) };
    }
    this.game.onMatchEnd = (won) => this._storyEnd(won);
    this.startFight(this.story.vesselId, null, { mode: 'story', playerChar: buffed, enemyChar: foeEntry });
  }
  _storyEnd(won) {
    // fold this match's stats into the soul's accumulated actions
    const ms = this.game.matchStats;
    if (ms) this._foldStats(this.story.acc, ms);
    const st = STORY_STAGES[this.story.stage];
    if (won) {
      if (st.key !== 'trade' && st.key !== 'boss' && !this.story.forces.includes(st.key)) {
        this.story.forces.push(st.key);
        this.ui.banner(`${FORCES[st.key].name} CLAIMED — ${FORCES[st.key].desc}`);
      }
      // Trader stage: the trade happened on the trader screen; the fight is the toll.
      setTimeout(() => {
        this.story.stage++;
        this._storyStageIntro();
      }, 1600);
    } else {
      this.story.deaths++;
      setTimeout(() => this._reincarnateScreen(), 1200);
    }
  }
  _storyComplete() {
    const mins = Math.round((Date.now() - this.story.startTime) / 60000);
    this._modeWin(true, 'THE KATANA IS FORGED',
      `Five forces claimed. The Assembled Soul faced — and it was you. ` +
      `Deaths: ${this.story.deaths}. Time: ${mins} min. The soul is nearly whole.`, []);
  }

  /* ---------- Reincarnation screen ---------- */
  _reincarnateScreen() {
    const profile = styleProfile(this.story.acc);
    const ids = this.roster.map((c) => c.id);
    const picks = chooseReincarnation(profile, ids, this.story.vesselId, this.story.deaths);
    this._el('reinc-deaths').textContent = `DEATH ${this.story.deaths} — THE SOUL CONTINUES`;
    this._el('reinc-flavor').textContent =
      'When a soul loses, it dies — and is reborn before the next fight. ' +
      'The Trial has watched how you fight. These are the vessels your actions have earned.';
    const fl = this._el('reinc-forces');
    if (fl) fl.textContent = 'FORCES CARRIED OVER: ' + (this.story.forces.length ? this.story.forces.map((k) => FORCES[k].name).join(' · ') : 'none');
    const wrap = this._el('reinc-cards');
    wrap.innerHTML = '';
    picks.forEach((id) => {
      const c = this.getChar(id);
      if (!c) return;
      const card = document.createElement('button');
      card.className = 'reinc-card';
      card.innerHTML =
        `<div class="portrait"><img src="assets/portraits/${c.id}.png" alt="${c.name}" loading="lazy" ` +
        `onerror="this.style.display='none'"></div>` +
        `<div class="cname">${c.name}</div><div class="cstyle">${c.style || ''}</div>` +
        `<div class="rwhy">${reincarnationReason(id, profile)}</div>`;
      card.addEventListener('click', () => {
        this.audio && this.audio.uiClick && this.audio.uiClick();
        this.story.vesselId = id;
        this.ui.banner('REBORN AS ' + c.name);
        setTimeout(() => this._storyStageIntro(), 900);
      });
      wrap.appendChild(card);
    });
    this.show('reincarnate');
  }

  /* ---------- Trader screen (stage 6) ---------- */
  _traderScreen() {
    const have = this.story.forces.slice();
    let give = null, take = null;
    const render = () => {
      const gh = this._el('trade-give'), tk = this._el('trade-take');
      gh.innerHTML = ''; tk.innerHTML = '';
      const mk = (key, label, sel, fn) => {
        const b = document.createElement('button');
        b.className = 'trade-opt' + (sel === key ? ' sel' : '');
        b.innerHTML = `<b>${FORCES[key].name}</b><span>${FORCES[key].desc}</span>`;
        b.addEventListener('click', () => { fn(key); render(); });
        return b;
      };
      if (!have.length) gh.innerHTML = '<p class="trade-note">You hold no forces yet — the Trader will still let you fight for passage.</p>';
      have.forEach((k) => gh.appendChild(mk(k, 0, give, (key) => { give = (give === key ? null : key); })));
      FORCE_ORDER.forEach((k) => tk.appendChild(mk(k, 0, take, (key) => { take = (take === key ? null : key); })));
      const ok = this._el('trade-confirm');
      ok.disabled = !(give && take && give !== take);
      ok.textContent = (give && take && give !== take)
        ? `TRADE ${FORCES[give].name} → ${FORCES[take].name}` : 'CHOOSE A FORCE TO GIVE AND ONE TO TAKE';
    };
    render();
    this._el('trade-confirm').onclick = () => {
      if (!(give && take && give !== take)) return;
      this.story.forces = this.story.forces.filter((k) => k !== give);
      this.story.forces.push(take);
      this.ui.banner(`TRADED ${FORCES[give].name} FOR ${FORCES[take].name}`);
      setTimeout(() => this._storyFight(), 900);
    };
    const skip = this._el('trade-skip');
    if (skip) skip.onclick = () => { this.audio && this.audio.uiClick && this.audio.uiClick(); this._storyFight(); };
    this._badge('STORY · PHANTOM MARKETPLACE');
    this.show('trader');
  }

  /* ---------- TRAINING: endless round vs a passive dummy ---------- */
  _beginTraining(fighterId) {
    const foe = this._pickFoe(fighterId, null, 0.3);
    const dummy = { ...foe, ai: { aggression: 0, grabBias: 0, reaction: 0, passive: true } };
    this._badge('TRAINING · DUMMY WILL NOT FIGHT BACK');
    this._showQuit(true);
    this.game.training = true;
    this.game.onMatchEnd = null; // training never "ends" — rounds auto-reset
    this.startFight(fighterId, null, { mode: 'training', enemyChar: dummy });
  }

  /* ---------- SURVIVAL (Tekken 2+): endless, HP carries, small restore ----------
     Canon note: none — this is pure Tekken. One round, lose once = run over. */
  _survivalNext() {
    const s = this.survival;
    const foe = this._pickFoe(s.fighterId, null, Math.min(0.95, 0.45 + s.wave * 0.05));
    const foeEntry = { ...foe, ai: scaledAi(foe, Math.min(0.95, 0.45 + s.wave * 0.05)) };
    this._survivalFoe = foeEntry;
    this._badge(`SURVIVAL · WAVE ${s.wave + 1} · ${foe.name}`);
    this.ui.banner(`WAVE ${s.wave + 1} — ${foe.name}`);
    this.game.onMatchEnd = (won) => this._survivalEnd(won);
    this._survivalFight();
  }
  _survivalFight() { // (re)start current wave — used by rematch
    const s = this.survival;
    const opts = { mode: 'survival', roundsToWin: SURVIVAL_CFG.roundsToWin, enemyChar: this._survivalFoe };
    if (s.hp != null) opts.hpCarry = s.hp;
    this.startFight(s.fighterId, null, opts);
  }
  _survivalEnd(won) {
    const s = this.survival;
    if (won) {
      s.wave++;
      const g = this.game;
      s.hp = survivalCarry(g.p1.hp, g.p1.maxHp);
      const rec = whGetRecords();
      if (s.wave > (rec.survival || 0)) whSetRecord('survival', s.wave);
      this.ui.banner(`WAVE ${s.wave} CLEARED — +${Math.round(SURVIVAL_CFG.restore * 100)}% health restored`);
      setTimeout(() => this._survivalNext(), 1400);
    } else {
      const rec = whGetRecords();
      this._modeWin(false, 'SURVIVAL — RUN OVER',
        `Fell at wave ${s.wave + 1}. Best run: ${rec.survival || s.wave} waves. The shrine is silent. Run it back.`,
        [{ label: 'RETRY SURVIVAL', fn: () => { this.survival = { wave: 0, fighterId: s.fighterId, hp: null }; this._survivalNext(); } }]);
    }
  }

  /* ---------- TIME ATTACK (Tekken 2+): 8 fights vs the clock ---------- */
  _timeAttackNext() {
    const t = this.timeattack;
    if (t.idx >= TIME_ATTACK_CFG.fights) { this._timeAttackClear(); return; }
    const diff = 0.50 + (t.idx / TIME_ATTACK_CFG.fights) * 0.40;
    const foe = this._pickFoe(t.fighterId, null, diff);
    const foeEntry = { ...foe, ai: scaledAi(foe, diff) };
    this._timeAttackFoe = foeEntry;
    this._badge(`TIME ATTACK · FIGHT ${t.idx + 1}/${TIME_ATTACK_CFG.fights} · ${fmtTime(t.totalMs)}`);
    this.ui.banner(`FIGHT ${t.idx + 1} — ${foe.name}`);
    this.game.onMatchEnd = (won) => this._timeAttackEnd(won);
    this._timeAttackFight();
  }
  _timeAttackFight() {
    const t = this.timeattack;
    this.startFight(t.fighterId, null, {
      mode: 'timeattack', roundsToWin: TIME_ATTACK_CFG.roundsToWin, enemyChar: this._timeAttackFoe,
    });
    // Clock starts when the round actually begins — not during model loads.
    if (t._watch) clearInterval(t._watch);
    t._watch = setInterval(() => {
      if (this.game.roundState === 'fight') { clearInterval(t._watch); t._watch = null; t.fightStart = Date.now(); }
    }, 250);
  }
  _timeAttackEnd(won) {
    const t = this.timeattack;
    if (t._watch) { clearInterval(t._watch); t._watch = null; }
    if (won) {
      t.totalMs += Date.now() - (t.fightStart || Date.now());
      t.idx++;
      setTimeout(() => this._timeAttackNext(), 1200);
    } else {
      this._modeWin(false, 'TIME ATTACK — CLOCK STOPS',
        `Fell at fight ${t.idx + 1} of ${TIME_ATTACK_CFG.fights} with ${fmtTime(t.totalMs)} on the clock. ` +
        `Best clear: ${whGetRecords().timeattack ? fmtTime(whGetRecords().timeattack) : 'none yet'}.`,
        [{ label: 'RETRY TIME ATTACK', fn: () => { this.timeattack = { idx: 0, fighterId: t.fighterId, totalMs: 0, fightStart: 0, _watch: null }; this._timeAttackNext(); } }]);
    }
  }
  _timeAttackClear() {
    const t = this.timeattack;
    const grade = timeAttackGrade(t.totalMs);
    const rec = whGetRecords();
    const best = rec.timeattack;
    if (!best || t.totalMs < best) whSetRecord('timeattack', t.totalMs);
    this._modeWin(true, `TIME ATTACK CLEARED — GRADE ${grade}`,
      `8 fights in ${fmtTime(t.totalMs)}. ${!best || t.totalMs < best ? 'NEW RECORD.' : `Best: ${fmtTime(best)}.`} ` +
      `S < 4:00 · A < 6:00 · B < 9:00.`,
      [{ label: 'RUN IT BACK', fn: () => { this.timeattack = { idx: 0, fighterId: t.fighterId, totalMs: 0, fightStart: 0, _watch: null }; this._timeAttackNext(); } }]);
  }

  /* ---------- TEAM BATTLE (Tekken 2–TTT2): 3v3, winner stays on ---------- */
  _teamTrayBuild() {
    const screen = this._el('screen-select');
    if (!screen || this._teamTray) return;
    const tray = document.createElement('div');
    tray.id = 'team-tray';
    tray.style.cssText = 'display:flex;gap:8px;justify-content:center;padding:8px;flex-wrap:wrap;';
    screen.appendChild(tray);
    this._teamTray = tray;
    this._teamTrayRender();
  }
  _teamTrayRender() {
    if (!this._teamTray) return;
    this._teamTray.innerHTML = '';
    for (let i = 0; i < TEAM_CFG.size; i++) {
      const id = this._teamPending[i];
      const c = id ? this.getChar(id) : null;
      const slot = document.createElement('div');
      slot.style.cssText = 'min-width:120px;padding:8px 12px;border:1px solid #8a6cff;border-radius:8px;' +
        'background:' + (c ? 'rgba(138,108,255,.18)' : 'rgba(255,255,255,.04)') + ';text-align:center;font-size:12px;';
      slot.textContent = c ? `P${i + 1} · ${c.name}` : `P${i + 1} · — pick —`;
      this._teamTray.appendChild(slot);
    }
  }
  _teamBuildCpu(pTeam) {
    const pool = this.roster.map((c) => c.id).filter((id) => !pTeam.includes(id) && id !== 'custom');
    const team = [];
    while (team.length < TEAM_CFG.size && pool.length) {
      team.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
    }
    return team;
  }
  _teamFight() {
    const t = this.team;
    const pId = t.pTeam[t.pIdx], cId = t.cTeam[t.cIdx];
    const pc = this.getChar(pId), cc = this.getChar(cId);
    const diff = 0.55 + (t.pIdx + t.cIdx) * 0.05;
    const foeEntry = { ...cc, ai: scaledAi(cc, Math.min(0.95, diff)) };
    this._teamFoe = foeEntry;
    this._badge(`TEAM BATTLE · YOU ${t.pIdx + 1}/3 (${pc.name}) VS CPU ${t.cIdx + 1}/3 (${cc.name})`);
    this.ui.banner(`${pc.name} VS ${cc.name}`);
    this.game.onMatchEnd = (won) => this._teamEnd(won);
    const opts = { mode: 'team', roundsToWin: 1, enemyChar: foeEntry };
    if (t.pHp != null) opts.hpCarry = t.pHp;
    this.startFight(pId, null, opts);
  }
  _teamEnd(playerWon) {
    const t = this.team;
    const g = this.game;
    if (playerWon) {
      t.pHp = teamCarry(g.p1.hp, g.p1.maxHp);
      t.cIdx++; t.cHp = null;
    } else {
      // CPU winner keeps ITS health: p2 is the cpu fighter here.
      t.cHp = teamCarry(g.p2.hp, g.p2.maxHp);
      t.pIdx++; t.pHp = null;
    }
    if (t.cIdx >= TEAM_CFG.size) {
      const left = TEAM_CFG.size - t.pIdx;
      this._modeWin(true, 'TEAM BATTLE — YOUR TEAM STANDS',
        `CPU team wiped. ${left} of your ${TEAM_CFG.size} fighters still standing. The shrine remembers the team.`, []);
    } else if (t.pIdx >= TEAM_CFG.size) {
      const left = TEAM_CFG.size - t.cIdx;
      this._modeWin(false, 'TEAM BATTLE — TEAM WIPED',
        `Your team fell. CPU has ${left} fighter${left === 1 ? '' : 's'} left. Draft again.`,
        [{ label: 'REMATCH TEAMS', fn: () => { this._teamPending = []; this.startMode('team'); } }]);
    } else {
      const who = playerWon ? 'CPU sends its next fighter.' : 'You send your next fighter.';
      this.ui.banner(who);
      setTimeout(() => this._teamFight(), 1400);
    }
  }

  /* ---------- IMMORTAL QOMBAT / 不死クォンバット (WH original, CANON.md § SUN RĀ) ----------
     The pocket realm "where the trial's rules don't apply": no reincarnation.
     Win a wave = you eat (+HP, +power). Lose = the sun eats you. */
  _qombatNext() {
    const q = this.qombat;
    const diff = qombatDiff(q.wave);
    const foe = this._pickFoe(q.fighterId, null, diff);
    const foeEntry = { ...foe, ai: scaledAi(foe, diff) };
    this._qombatFoe = foeEntry;
    const player = this.getChar(q.fighterId);
    const buffed = { ...player, stats: qombatBuff(player.stats, q.wave) };
    this._badge(`不死クォンバット · WAVE ${q.wave + 1} · ${foe.name}`);
    if (q.wave === 0) {
      // The naming law (CANON.md): only Sun Rā gets the English version.
      this.ui.banner('SUN RĀ: "IMMORTAL QOMBAT."');
      setTimeout(() => this.ui.banner(`WAVE 1 — ${foe.name}. The sun is watching.`), 1500);
    } else {
      this.ui.banner(`WAVE ${q.wave + 1} — ${foe.name}. The sun is watching.`);
    }
    this.game.onMatchEnd = (won) => this._qombatEnd(won);
    const opts = {
      mode: 'qombat', roundsToWin: QOMBAT_CFG.roundsToWin,
      stage: QOMBAT_CFG.stage, playerChar: buffed, enemyChar: foeEntry,
    };
    if (q.hp != null) opts.hpCarry = q.hp;
    this._qombatOpts = opts;
    this.startFight(q.fighterId, null, opts);
  }
  _qombatFight() { // rematch current wave
    const q = this.qombat;
    const opts = { ...this._qombatOpts };
    if (q.hp != null) opts.hpCarry = q.hp; else delete opts.hpCarry;
    this.startFight(q.fighterId, null, opts);
  }
  _qombatEnd(won) {
    const q = this.qombat;
    if (won) {
      q.wave++;
      q.powerMult = 1 + QOMBAT_CFG.absorbPower * q.wave;
      const g = this.game;
      q.hp = qombatCarry(g.p1.hp, g.p1.maxHp);
      const rec = whGetRecords();
      if (q.wave > (rec.qombat || 0)) whSetRecord('qombat', q.wave);
      this.ui.banner(`YOU EAT — WAVE ${q.wave}. +power. The sun feeds the survivor.`);
      setTimeout(() => this._qombatNext(), 1400);
    } else {
      const rec = whGetRecords();
      const eaten = (rec.qombatEaten || 0) + 1;
      whSetRecord('qombatEaten', eaten);
      const vessel = this.getChar(q.fighterId);
      this._modeWin(false, 'THE SUN EATS',
        `${vessel ? vessel.name : 'Your soul'} is absorbed at wave ${q.wave + 1}. ` +
        `${eaten} soul${eaten === 1 ? '' : 's'} now burn inside Sun Rā. Best run: ${rec.qombat || q.wave} waves.`,
        [{ label: 'FEED THE SUN AGAIN', fn: () => { this.qombat = { wave: 0, fighterId: q.fighterId, hp: null, powerMult: 1 }; this._qombatNext(); } }]);
    }
  }

  /* ---------- SOUL SURGE GAUNTLET (WH original, CANON.md §4) ----------
     9 fights, one per soul. Each fight opens with that soul channeling
     through you — the canon Soul Surge, bout-long. */
  _surgeNext() {
    const s = this.surge;
    if (s.idx >= SURGE_BLESSINGS.length) { this._surgeClear(); return; }
    const blessing = surgeBlessing(s.idx);
    const player = this.getChar(s.fighterId);
    const buffed = { ...player, stats: blessing.apply(player.stats || BASE_STATS) };
    const diff = Math.min(0.95, 0.50 + s.idx * 0.05);
    const foe = this._pickFoe(s.fighterId, null, diff);
    const foeEntry = { ...foe, ai: scaledAi(foe, diff) };
    this._surgeFoe = foeEntry;
    this._badge(`SOUL SURGE GAUNTLET · ${blessing.soul.toUpperCase()} ${blessing.kanji} · FIGHT ${s.idx + 1}/9`);
    this.ui.banner(blessing.line);
    this.game.onMatchEnd = (won) => this._surgeEnd(won);
    this._surgePlayer = buffed;
    this.startFight(s.fighterId, null, { mode: 'surge', roundsToWin: 1, playerChar: buffed, enemyChar: foeEntry });
  }
  _surgeFight() { // rematch current soul
    this.startFight(this.surge.fighterId, null,
      { mode: 'surge', roundsToWin: 1, playerChar: this._surgePlayer, enemyChar: this._surgeFoe });
  }
  _surgeEnd(won) {
    const s = this.surge;
    if (won) {
      s.idx++;
      setTimeout(() => this._surgeNext(), 1300);
    } else {
      const b = surgeBlessing(s.idx);
      this._modeWin(false, 'THE CHANNEL BREAKS',
        `${b.soul.toUpperCase()} ${b.kanji} withdraws at fight ${s.idx + 1} of 9. The souls are patient. Channel again.`,
        [{ label: 'CHANNEL AGAIN', fn: () => { this.surge = { idx: 0, fighterId: s.fighterId }; this._surgeNext(); } }]);
    }
  }
  _surgeClear() {
    this._modeWin(true, 'NINE SOULS, ONE VESSEL',
      'All nine channeled. Rin, Byou, Tou, Sha, Kai, Jin, Retsu, Zen, Gyou — remembered, not borrowed. You are nearly whole.', []);
  }

  /* ---------- TRADER'S MIMIC (WH original, CANON.md §5) ----------
     "The Trader's fighting style is mimicry — it wears the opponent's
     moveset like a borrowed coat." 3 single-round bouts at the Phantom
     Marketplace. Lose one and the Trader keeps your coat. */
  _traderNext() {
    const t = this.trader;
    if (t.bout >= TRADER_CFG.bouts) { this._traderClear(); return; }
    const player = this.getChar(t.fighterId);
    if (t.bout === 0) {
      // A borrowed coat: some other vessel's moveset.
      const donor = this._pickFoe(t.fighterId, null, 0.5);
      t._donorMoveset = (donor && donor.moveset) || 'jin';
    }
    const foeEntry = traderFoe(player, t.bout, t._donorMoveset);
    this._traderFoe = foeEntry;
    const lines = [
      'BOUT 1 — the Trader wears a borrowed coat.',
      'BOUT 2 — the Trader tries on YOUR coat.',
      'BOUT 3 — the Trader wears it better.',
    ];
    this._badge(`TRADER'S MIMIC · ${lines[t.bout].split(' — ')[0]}`);
    this.ui.banner(lines[t.bout] + ' Nothing here is real, but the prices are.');
    this.game.onMatchEnd = (won) => this._traderEnd(won);
    this._traderOpts = {
      mode: 'trader', roundsToWin: TRADER_CFG.roundsToWin,
      stage: TRADER_CFG.stage, enemyChar: foeEntry,
    };
    this.startFight(t.fighterId, null, this._traderOpts);
  }
  _traderFight() { // rematch current bout
    this.startFight(this.trader.fighterId, null, this._traderOpts);
  }
  _traderEnd(won) {
    const t = this.trader;
    if (won) {
      t.bout++;
      setTimeout(() => this._traderNext(), 1300);
    } else {
      this._modeWin(false, 'THE TRADER KEEPS YOUR COAT',
        `Fell at bout ${t.bout + 1} of ${TRADER_CFG.bouts}. The Trader smiles with its mouth. Its eyes smile only when it has already won.`,
        [{ label: 'TAKE IT BACK', fn: () => { this.trader = { bout: 0, fighterId: t.fighterId }; this._traderNext(); } }]);
    }
  }
  _traderClear() {
    const n = (whGetRecords().traderWins || 0) + 1;
    whSetRecord('traderWins', n);
    this._modeWin(true, 'THE TRADER PAYS UP',
      `Three bouts, one coat — yours. The Trader settles in forces and favors. Mimicries survived: ${n}.`, []);
  }

  /* ---------- shared helpers ---------- */
  _newAcc() { return { punch: 0, kick: 0, grab: 0, surge: 0, dodge: 0, blockTime: 0, time: 0 }; }
  _foldStats(acc, ms) {
    const at = (ms && ms.attacks) || {};
    for (const k of ['punch', 'kick', 'grab', 'surge', 'dodge']) acc[k] += at[k] || 0;
    acc.blockTime += (ms && ms.blockTime) || 0;
    acc.time += (ms && ms.time) || 0;
  }
  _pickFoe(excludeId, pool, diff) {
    let ids = (pool && pool.length ? pool : this.roster.map((c) => c.id));
    ids = ids.filter((id) => id !== excludeId && id !== 'custom');
    const avail = ids.map((id) => this.getChar(id)).filter(Boolean);
    const list = avail.length ? avail : this.roster.filter((c) => c.id !== excludeId);
    return list[Math.floor(Math.random() * list.length)];
  }
  _badge(text) {
    const b = this._el('mode-badge');
    if (b) { b.textContent = text; b.style.display = text ? 'block' : 'none'; }
  }
  _showQuit(on) {
    const q = this._el('training-quit');
    if (q) q.style.display = on ? 'block' : 'none';
  }
  _modeWin(won, title, sub, extraButtons) {
    this.game.onMatchEnd = null;
    this._el('modewin-title').textContent = title;
    this._el('modewin-title').className = won ? 'win' : 'lose';
    this._el('modewin-sub').textContent = sub;
    const wrap = this._el('modewin-buttons');
    wrap.innerHTML = '';
    const mk = (label, cls, fn) => {
      const b = document.createElement('button');
      b.className = cls; b.textContent = label;
      b.addEventListener('click', () => { this.audio && this.audio.uiClick && this.audio.uiClick(); fn(); });
      wrap.appendChild(b);
    };
    (extraButtons || []).forEach((e) => mk(e.label, 'btn-primary', e.fn));
    mk('MAIN MENU', 'btn-ghost', () => {
      this.game.leaveFight();
      this.clearState();
      this.show('menu'); this.audio && this.audio.stopMusic && this.audio.stopMusic();
    });
    this.show('modewin');
  }
}
