/* ============================================================
   WESTERN HEART — Match Rules (Tekken 7 GAME OPTION)
   The single source of truth for fight rules, pulled from the
   arcade/T7 GAME OPTION table (manuals.plus TTT operators manual):
     DIFFICULTY LEVEL: EASY, MEDIUM, HARD, VERY HARD, ULTRA HARD
     FIGHT COUNT <1P GAME>: 1-5
     FIGHT COUNT <VS GAME>: 1-5
     ROUND TIME: 30, 40, 60, 80, 90, 99
     GUARD DAMAGE: ON (a little), OFF (none)
   T7 console adds INFINITY round time and VERY EASY. Every value
   here is REAL: game.js honors roundsToWin/roundTime/guardDamage
   per match; modes.js scales CPU AI by difficulty; versus-setup.js
   and the OPTIONS screen write here and nowhere else.

   Standalone — no imports, so game.js / modes.js / menus can all
   read it without import cycles.
   ============================================================ */

const KEY = 'wh_rules_v1';

/* T7 arcade ladder, console names. mult scales the mode's base AI
   difficulty (modes.js scaledAi): 1.0 = the ladder as authored. */
export const DIFFICULTIES = [
  { id: 'veryeasy', name: 'VERY EASY', mult: 0.55 },
  { id: 'easy',     name: 'EASY',      mult: 0.75 },
  { id: 'normal',   name: 'NORMAL',    mult: 1.0 },
  { id: 'hard',     name: 'HARD',     mult: 1.20 },
  { id: 'veryhard', name: 'VERY HARD', mult: 1.40 },
  { id: 'ultra',    name: 'ULTRA HARD',mult: 1.60 },
];

export const ROUND_COUNTS = [1, 2, 3, 4, 5];
/* 0 = INFINITY (T7 console). JSON-safe: no Infinity literal stored. */
export const ROUND_TIMES = [30, 40, 60, 90, 99, 0];

export const RULE_DEFAULTS = {
  difficulty: 'normal',
  rounds1p: 2,        // FIGHT COUNT <1P GAME> — arcade/story ladders
  roundsVs: 2,        // FIGHT COUNT <VS GAME> — versus bouts
  roundTime: 60,      // seconds; 0 = INFINITY
  guardDamage: true,  // chip damage on block
  stageMode: 'select',// versus: 'select' | 'random'
};

export function getRules() {
  try {
    return { ...RULE_DEFAULTS, ...(JSON.parse(localStorage.getItem(KEY)) || {}) };
  } catch { return { ...RULE_DEFAULTS }; }
}

export function setRules(patch) {
  try {
    localStorage.setItem(KEY, JSON.stringify({ ...getRules(), ...patch }));
  } catch { /* private mode — rules just don't persist */ }
}

export function difficultyMult(id) {
  const d = DIFFICULTIES.find((x) => x.id === (id || getRules().difficulty));
  return d ? d.mult : 1.0;
}

export function fmtRoundTime(t) {
  return t === 0 ? '∞' : `${t}s`;
}
