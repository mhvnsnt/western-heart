/* ============================================================
   WESTERN HEART — MCTS Move Selection + Live Opponent Model
   Two FightingICE lessons in one module:

   1) MCTS THROUGH A FORWARD MODEL. The sample MCTS agents that
      defined the competition simulate action sequences through the
      platform's forward model, backpropagate the score, and play the
      best first action. We do the same with OUR forward model —
      frame data (ai/frame-data.js): given my candidate move and a
      predicted foe response, frame math says who lands what. Depth 2,
      UCB1 over the candidate set, hard time budget (FightingICE gives
      agents 16.67ms a frame; the AI's slice of that must stay tiny).

   2) A LIVE OPPONENT MODEL. ERHEAPI — the 2020 champion (Tang, Zhu,
      Zhao, Lucas, IEEE Trans. on Games) — paired search with a model
      of the foe learned LIVE from history observations, so its plans
      used what the opponent was likely to do instead of assuming the
      worst. Ours is a frequency table instead of a neural net: cheap,
      explainable, and it learns within a round.

   Pure logic: no fighter handles, no DOM, no THREE. The controller
   feeds observations; select() returns the winning move (or null —
   the caller falls back to its heuristic).
   ============================================================ */
import { bestPunish } from './frame-data.js';

/* Foe responses the model tracks. 'whiff' = foe does nothing useful
   (walks, whiffs, freezes) — my move lands clean. */
export const RESPONSES = ['blockHigh', 'blockLow', 'attack', 'sidestep', 'whiff'];
export const SITUATIONS = ['neutral', 'afterBlocked', 'wakeup', 'pressure'];

/* ---------------- live opponent model ---------------- */

export class OpponentModel {
  /**
   * @param {number} memory - max observations kept per situation
   *   (older ones decay away so the model adapts mid-match).
   */
  constructor(memory = 40) {
    this.memory = Math.max(5, memory);
    this._counts = {};
    for (const s of SITUATIONS) {
      this._counts[s] = { blockHigh: 0, blockLow: 0, attack: 0, sidestep: 0, whiff: 0 };
    }
    this._foeFastestF = 12; // fastest foe button seen (frames); default = generic jab
    this._foeDmgSum = 0;
    this._foeDmgN = 0;
  }

  _situ(s) { return SITUATIONS.includes(s) ? s : 'neutral'; }

  /** Record one observed foe response in a situation. */
  observe(action, situation = 'neutral') {
    if (!RESPONSES.includes(action)) return;
    const c = this._counts[this._situ(situation)];
    c[action] += 1;
    let total = 0;
    for (const k of RESPONSES) total += c[k];
    if (total > this.memory) {
      // Decay: halve everything so recent reads dominate.
      for (const k of RESPONSES) c[k] = Math.floor(c[k] / 2);
    }
  }

  /** Record a foe attack's startup (frames) — learns their fastest button. */
  observeFoeAttack(startupF, damage = 0) {
    if (startupF > 0 && startupF < this._foeFastestF) this._foeFastestF = Math.round(startupF);
    if (damage > 0) { this._foeDmgSum += damage; this._foeDmgN += 1; }
  }

  /** Laplace-smoothed distribution over RESPONSES for a situation. */
  predict(situation = 'neutral') {
    const c = this._counts[this._situ(situation)];
    let total = 0;
    for (const k of RESPONSES) total += c[k];
    const out = {};
    for (const k of RESPONSES) out[k] = (c[k] + 1) / (total + RESPONSES.length);
    return out;
  }

  /** Sample one response from the distribution (injectable rng). */
  sample(situation = 'neutral', rng = Math.random) {
    const p = this.predict(situation);
    let r = rng(), acc = 0;
    for (const k of RESPONSES) { acc += p[k]; if (r <= acc) return k; }
    return 'whiff';
  }

  get foeFastestF() { return this._foeFastestF; }
  get foeAvgDmg() { return this._foeDmgN ? this._foeDmgSum / this._foeDmgN : 14; }

  /** Convenience reads for the controller's heuristic lanes. */
  lowBlockBias(situation = 'neutral') { return this.predict(situation).blockLow; }
  guardRate(situation = 'neutral') {
    const p = this.predict(situation);
    return p.blockHigh + p.blockLow;
  }
  mashRate(situation = 'neutral') { return this.predict(situation).attack; }
}

/* ---------------- MCTS selector ---------------- */

/**
 * Rollout count by difficulty (0..1). Below 0.35 the CPU uses the
 * plain heuristic — MCTS is a higher-tier brain, Tekken-style.
 */
export function mctsRolloutsForDifficulty(diff) {
  const d = Math.min(1, Math.max(0, diff ?? 0.5));
  if (d < 0.35) return 0;
  return Math.round(8 + ((d - 0.35) / 0.65) * 16); // 8 -> 24
}

const UCB_C = 1.4;

export class MCTSSelector {
  /**
   * @param {object} o - { rollouts, budgetMs, horizon }
   *   budgetMs: hard wall-clock cap per select() call (default 3ms —
   *   a fraction of FightingICE's 16.67ms frame budget).
   */
  constructor({ rollouts = 16, budgetMs = 3, horizon = 2 } = {}) {
    this.rollouts = rollouts;
    this.budgetMs = budgetMs;
    this.horizon = Math.max(1, horizon);
  }

  /**
   * @param {object} ctx
   *   { candidates: frameMove[], foe: {startupF, avgDmg},
   *     foeModel: OpponentModel|null, situation, myFollowups: frameMove[] }
   * @param {function} rng - injectable RNG.
   * @param {function} now - injectable clock (ms).
   * @returns {object|null} the winning frameMove, or null.
   */
  select(ctx, rng = Math.random, now = () => Date.now()) {
    const cands = (ctx.candidates || []).filter((m) => m && m.damage > 0);
    if (!cands.length) return null;
    if (cands.length === 1) return cands[0];

    const deadline = now() + Math.max(0.5, this.budgetMs);
    const stats = cands.map(() => ({ n: 0, sum: 0 }));
    let total = 0, ran = 0;

    while (ran < this.rollouts && now() < deadline) {
      ran += 1;
      // UCB1 pick.
      let bi = 0, bv = -Infinity;
      for (let i = 0; i < cands.length; i += 1) {
        const s = stats[i];
        const mean = s.n ? s.sum / s.n : 0;
        const ucb = mean + (s.n ? UCB_C * Math.sqrt(Math.log(Math.max(1, total)) / s.n) : 1e9);
        if (ucb > bv) { bv = ucb; bi = i; }
      }
      const v = this._rollout(cands[bi], ctx, rng);
      stats[bi].n += 1; stats[bi].sum += v; total += 1;
    }

    let best = 0, bestMean = -Infinity;
    for (let i = 0; i < cands.length; i += 1) {
      const s = stats[i];
      const mean = s.n ? s.sum / s.n : -Infinity;
      if (mean > bestMean) { bestMean = mean; best = i; }
    }
    return cands[best];
  }

  /* One simulated exchange through the frame-data forward model. */
  _rollout(m, ctx, rng) {
    const foeModel = ctx.foeModel;
    const foeStartupF = Math.max(6, Math.round(ctx.foe?.startupF ?? foeModel?.foeFastestF ?? 12));
    const foeDmg = Math.max(4, ctx.foe?.avgDmg ?? foeModel?.foeAvgDmg ?? 14);
    const situation = ctx.situation || 'neutral';
    const resp = foeModel ? foeModel.sample(situation, rng) : 'blockHigh';

    let net = 0;   // expected damage, mine minus theirs
    let myAdv = 0; // my frame advantage after the exchange

    if (resp === 'whiff') {
      net = m.damage; myAdv = m.onHit ?? 4;
    } else if (resp === 'attack') {
      // Startup race: faster button wins clean (counter-hit bonus).
      if (m.startupF < foeStartupF) { net = m.damage * 1.2; myAdv = m.onHit ?? 4; }
      else if (m.startupF === foeStartupF) { net = m.damage - foeDmg * 0.6; myAdv = 0; }
      else { net = -foeDmg * 1.2; myAdv = -6; }
    } else if (resp === 'sidestep') {
      // Linear move whiffs; foe takes their turn.
      if (rng() < 0.25) { net = m.damage * 0.5; myAdv = 0; } // clipped them anyway
      else { net = -foeDmg * 1.2; myAdv = -8; }
    } else {
      // Blocked high/low: lows beat high guard, mids/highs beat low guard.
      const blockedHigh = resp === 'blockHigh';
      const lands = m.isLow ? blockedHigh : !blockedHigh;
      if (lands) { net = m.damage; myAdv = m.onHit ?? 4; }
      else {
        myAdv = m.onBlock ?? -7;
        if (myAdv <= -10) net = -foeDmg * (1 + (-myAdv - 10) * 0.05); // launch-punished
      }
    }

    // Depth 2: the exchange's frame advantage buys (or costs) a followup.
    if (this.horizon >= 2) {
      const followups = ctx.myFollowups || [];
      if (myAdv > 1 && followups.length) {
        const p = bestPunish(followups, myAdv);
        if (p) net += p.damage * 0.4;
      } else if (myAdv <= -10) {
        net -= foeDmg * 0.4; // they get their turn
      }
    }
    return net;
  }
}
