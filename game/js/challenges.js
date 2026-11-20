/* ============================================================
   WESTERN HEART — ChallengeManager (daily challenges tracker)

   Tracks daily-challenge progress from REAL match data. Hooks in
   ADDITIVELY — no edits to game.js or modes.js:

   1. watch(game): chains game.onMatchEnd via a getter/setter pair.
      Every mode assigns game.onMatchEnd per fight; the setter captures
      the mode's handler and the getter returns our dispatcher, which
      records stats first (after the mode handler runs, so wave
      counters etc. are already updated) then calls through.
   2. hookModes(ModeController): wraps _timeAttackClear / _arcadeClear /
      _surgeClear on the prototype to capture clears + grades.

   Progress: localStorage 'wh_challenges_v1', keyed by date. Day
   rollover resets progress (dailies are per-day by design).
   Rewards: claimed manually -> grantUnlockable (js/unlockables.js).
   ============================================================ */
import { challengesFor, todayStr, CHALLENGE_MAP } from '../data/challenges.js';
import { grantUnlockable } from './unlockables.js';

const STORE_KEY = 'wh_challenges_v1';
const GRADE_RANK = { S: 0, A: 1, B: 2, C: 3 };

function loadStore() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY)) || null; }
  catch { return null; }
}
function saveStore(s) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(s)); } catch { /* private mode */ }
}

export class ChallengeManager {
  constructor(day = null) {
    this.day = day || todayStr();
    this._watched = false;
    this._modesHooked = false;
    this._listeners = [];
    const s = loadStore();
    if (s && s.date === this.day) this.store = s;
    else this.store = { date: this.day, progress: {}, claimed: {}, best: {} };
  }

  onChange(fn) { this._listeners.push(fn); return this; }
  _emit() {
    this._save();
    for (const fn of this._listeners) { try { fn(this); } catch (e) { console.error(e); } }
  }
  _save() { saveStore(this.store); }

  /** Today's rotation: { date, dailies[3], event }. */
  today() { return challengesFor(this.day); }

  progressOf(id) { return this.store.progress[id] || 0; }
  isComplete(id) {
    const c = CHALLENGE_MAP[id];
    return c ? this.progressOf(id) >= c.target : false;
  }
  isClaimed(id) { return !!this.store.claimed[id]; }

  /** Claim a completed challenge's reward. Returns the unlockable def or null. */
  claim(id) {
    const c = CHALLENGE_MAP[id];
    if (!c || !this.isComplete(id) || this.isClaimed(id)) return null;
    this.store.claimed[id] = Date.now();
    grantUnlockable(c.reward);
    this._emit();
    return c;
  }

  /* ---------------- engine hooks (additive) ---------------- */

  /** Chain game.onMatchEnd so every match feeds the tracker. */
  watch(game) {
    if (!game || this._watched) return this;
    this._watched = true;
    game._whChalWatched = true;
    const mgr = this;
    let userFn = (typeof game.onMatchEnd === 'function') ? game.onMatchEnd : null;
    const dispatch = (won) => {
      let r;
      try { if (userFn) r = userFn(won); } finally {
        try { mgr._onMatchEnd(won); } catch (e) { console.error(e); }
      }
      return r;
    };
    Object.defineProperty(game, 'onMatchEnd', {
      configurable: true, enumerable: true,
      get: () => (userFn ? dispatch : null),
      set: (fn) => { userFn = (typeof fn === 'function') ? fn : null; },
    });
    return this;
  }

  /** Wrap mode-clear methods to capture clears + time-attack grades. */
  hookModes(ModeController, timeAttackGrade) {
    if (!ModeController || this._modesHooked) return this;
    this._modesHooked = true;
    const mgr = this;
    const wrap = (proto, method, fn) => {
      const orig = proto[method];
      if (!orig || orig._whChalHooked) return;
      const wrapped = function (...args) {
        try { fn(this); } catch (e) { console.error(e); }
        return orig.apply(this, args);
      };
      wrapped._whChalHooked = true;
      proto[method] = wrapped;
    };
    wrap(ModeController.prototype, '_arcadeClear', () => mgr._add('mode_clear', 'arcade', 1));
    wrap(ModeController.prototype, '_surgeClear', () => mgr._add('mode_clear', 'surge', 1));
    wrap(ModeController.prototype, '_storyComplete', () => mgr._add('mode_clear', 'story', 1));
    wrap(ModeController.prototype, '_timeAttackClear', function (ctrl) {
      const ms = ctrl && ctrl.timeattack ? ctrl.timeattack.totalMs : 0;
      const grade = timeAttackGrade ? timeAttackGrade(ms) : '?';
      mgr._onTimeAttack(grade);
    });
    return this;
  }

  /* ---------------- progress ---------------- */

  _onMatchEnd(won) {
    const g = this._game();
    const stats = (g && g.matchStats) || {};
    const attacks = stats.attacks || {};
    const modes = this._modes();
    const mode = modes ? modes.mode : null;
    const fighterId = this._fighterId(modes, mode);
    const event = this.today().event;
    const mult = (type) => (event && event.bonus && event.bonus.type === type) ? event.bonus.mult : 1;

    if (won) {
      this._add('wins', null, 1);
      if ((stats.blockTime || 0) === 0) this._add('wins_no_block', null, 1);
      if ((stats.dmgTaken || 0) === 0) this._add('perfects', null, 1);
      if (fighterId) this._add('fighter_wins', fighterId, 1);
    }
    this._add('damage', null, Math.round(stats.dmgDealt || 0));
    this._best('damage_one_fight', Math.round(stats.dmgDealt || 0));
    this._add('grabs', null, attacks.grab || 0, mult('grabs'));
    this._add('surges', null, attacks.surge || 0, mult('surges'));
    // wave modes: read the run state the mode handler just updated
    if (modes) {
      if (modes.survival) this._best('survival_wave', modes.survival.wave || 0);
      if (modes.qombat) this._best('qombat_wave', modes.qombat.wave || 0, mult('qombat_wave'));
    }
    this._emit();
  }

  _onTimeAttack(grade) {
    const rank = GRADE_RANK[grade];
    if (rank == null) return;
    for (const d of this.today().dailies) {
      if (d.type !== 'timeattack') continue;
      if (rank <= GRADE_RANK[d.target]) this._setComplete(d.id);
    }
    this._emit();
  }

  _onModeClear(modeKey) {
    for (const d of this.today().dailies) {
      if (d.type === 'mode_clear' && d.target === modeKey) this._setComplete(d.id);
    }
    this._emit();
  }

  /** Add n (x event multiplier) to every active daily of a type. */
  _add(type, qualifier, n, mult = 1) {
    if (!n) return;
    for (const d of this.today().dailies) {
      if (d.type !== type) continue;
      if (qualifier && d.fighter !== qualifier && d.target !== qualifier) continue;
      if (type === 'fighter_wins' && d.fighter !== qualifier) continue;
      this.store.progress[d.id] = (this.store.progress[d.id] || 0) + n * mult;
    }
  }

  /** Track a best (max) value for a type. */
  _best(type, value, mult = 1) {
    if (!value) return;
    const v = value * mult;
    for (const d of this.today().dailies) {
      if (d.type !== type) continue;
      if (v > (this.store.progress[d.id] || 0)) this.store.progress[d.id] = v;
    }
  }

  _setComplete(id) {
    const c = CHALLENGE_MAP[id];
    if (c) this.store.progress[id] = Math.max(this.store.progress[id] || 0, c.target);
  }

  _game() { return (typeof window !== 'undefined' && window.__game) || null; }
  _modes() { return (typeof window !== 'undefined' && window.__modes) || null; }

  /** Which fighter the human used, per mode state. */
  _fighterId(modes, mode) {
    if (!modes || !mode) return null;
    const m = modes;
    try {
      if (mode === 'versus' && m._lastVersus) return m._lastVersus[0];
      if (mode === 'arcade' && m.arcade) return m.arcade.fighterId;
      if (mode === 'story' && m.story) return m.story.vesselId;
      if (mode === 'training' && m.training) return m.training.fighterId;
      if (mode === 'survival' && m.survival) return m.survival.fighterId;
      if (mode === 'timeattack' && m.timeattack) return m.timeattack.fighterId;
      if (mode === 'team' && m.team) return m.team.pTeam[m.team.pIdx];
      if (mode === 'qombat' && m.qombat) return m.qombat.fighterId;
      if (mode === 'surge' && m.surge) return m.surge.fighterId;
      if (mode === 'trader' && m.trader) return m.trader.fighterId;
    } catch { /* mode state mid-transition */ }
    return null;
  }
}
