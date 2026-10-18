/* ============================================================
   WESTERN HEART — Game Modes
   VERSUS · ARCADE · STORY (reincarnation) · TRAINING

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
    this._el = (id) => document.getElementById(id);
  }

  /* ---------- mode entry (called from menu buttons) ---------- */
  startMode(mode) {
    this.mode = mode;
    this.vsStep = 0; this.vsP1 = null;
    this.arcade = null; this.story = null; this.training = null;
    this.game.onMatchEnd = null;
    this.game.training = false;
    this._badge('');
    this._showQuit(false);
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
      this.game.leaveFight(); this.game.training = false;
      this.mode = null; this._badge(''); this._showQuit(false);
      this.show('menu'); this.audio && this.audio.stopMusic && this.audio.stopMusic();
    });
    this.show('modewin');
  }
}
