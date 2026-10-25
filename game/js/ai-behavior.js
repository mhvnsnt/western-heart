/* ============================================================
   WESTERN HEART — Behavior-tree AI (U10) + strategy/execution
   split (U9) + AI style pool (U8 pattern)
   Sources (patterns, not code): Glasheer AI Combat prototype
   (behavior trees, perception sections, dodge/counter, closest-
   attacker-only rule); Slay-the-Spire-2 net lesson (strategy net
   separate from execution net; small nets train on CPU); Neural
   MMO RL pattern (a POOL of AI fighters with different styles,
   trained/evaluated in sim, not one generic AI).
   This module does NOT replace game/js/ai.js (utility/MCTS brain)
   — it is the structured tree layer ai.js can call for CPU
   decisions, and the pool that sim-match.js training consumes.
   Tree node contract: every node is a function (ctx) -> one of
   'success' | 'failure' | 'running'. ctx is caller-supplied and
   carries perceive()/act() helpers; this module never reads game
   state directly, so it stays Node-testable.
   ============================================================ */

export function sequence(children) {
  return (ctx) => {
    for (const child of children) {
      const r = child(ctx);
      if (r !== 'success') return r;
    }
    return 'success';
  };
}

export function selector(children) {
  return (ctx) => {
    for (const child of children) {
      const r = child(ctx);
      if (r !== 'failure') return r;
    }
    return 'failure';
  };
}

export function condition(fn) {
  return (ctx) => (fn(ctx) ? 'success' : 'failure');
}

export function action(fn) {
  return (ctx) => { fn(ctx); return 'success'; };
}

// Perception sections (Glasheer pattern): foe position relative to
// the fighter's facing. front = foe ahead, back = foe behind,
// left/right = lateral. Dodge response: front -> roll to
// disengage, back -> roll to close, sides -> sidestep.
export function sectionOf(dx, dz, facing = 1) {
  const forward = dx * facing;
  if (Math.abs(dz) > Math.abs(forward) * 1.2) return dz > 0 ? 'right' : 'left';
  return forward >= 0 ? 'front' : 'back';
}

export function dodgeForSection(section) {
  if (section === 'front') return 'roll-disengage';
  if (section === 'back') return 'roll-close';
  return 'sidestep';
}

// Closest-attacker-only rule (anti-overwhelm, GDC Spider-Man AI
// reference via Glasheer): in multi-opponent modes only the
// closest CPU attacks; the rest hold. Returns the attacker or null.
export function pickAttacker(attackers) {
  if (!attackers || attackers.length === 0) return null;
  let best = attackers[0];
  for (const a of attackers) if (a.distance < best.distance) best = a;
  return best;
}

// Fighter behavior tree: stunned -> recover; foe attacking in
// range -> dodge/counter by section; in range -> attack; else
// approach. ctx: { stunned, foeAttacking, foeSection, inRange,
// act(name) }.
export function buildFighterBT() {
  return selector([
    sequence([condition((c) => c.stunned), action((c) => c.act('recover'))]),
    sequence([
      condition((c) => c.foeAttacking && c.inRange),
      action((c) => c.act('counter-' + dodgeForSection(c.foeSection || 'front'))),
    ]),
    sequence([condition((c) => c.inRange), action((c) => c.act('attack'))]),
    action((c) => c.act('approach')),
  ]);
}

// U9 — strategy (WHAT to do) separate from execution (WHEN/HOW).
// Pure functions, deterministic, CPU-cheap: no GPU needed.
export function chooseStrategy(state) {
  // state: { hp (0..1), meter (0..1), distance ('close'|'mid'|'far'),
  //   foeHp (0..1), style ('aggressive'|'balanced'|'defensive') }
  if (state.hp < 0.25 && state.meter >= 1) return 'rage-finisher';
  if (state.style === 'aggressive') return state.distance === 'close' ? 'pressure' : 'close-distance';
  if (state.style === 'defensive') return state.distance === 'close' ? 'retreat' : 'space-and-punish';
  return state.distance === 'far' ? 'close-distance' : 'mixup';
}

export function chooseExecution(state) {
  // Timing layer: reaction delay in frames (never 0 — human rule
  // from ai.js methodology), plus a punish window check.
  const base = state.difficulty === 'boss' ? 8 : state.difficulty === 'rookie' ? 15 : 12;
  return { delayFrames: base, punishable: (state.foeRecoveryFrames || 0) >= base };
}

// U8 — pool of AI fighters with different styles. Records wins so
// sim training can promote winning styles; this is bookkeeping +
// selection, NOT a claim of RL training (that runs in sim-match.js).
export class AIPool {
  constructor() { this.styles = new Map(); }
  register(name, style) { this.styles.set(name, { style, wins: 0, games: 0 }); }
  record(name, won) {
    const s = this.styles.get(name);
    if (!s) return;
    s.games++; if (won) s.wins++;
  }
  winRate(name) {
    const s = this.styles.get(name);
    return s && s.games > 0 ? s.wins / s.games : 0;
  }
  best() {
    let bestName = null, bestRate = -1;
    for (const [name] of this.styles) {
      const r = this.winRate(name);
      if (r > bestRate) { bestRate = r; bestName = name; }
    }
    return bestName;
  }
  names() { return [...this.styles.keys()]; }
}
