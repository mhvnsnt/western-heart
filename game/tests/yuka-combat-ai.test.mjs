/* yuka-combat-ai.test.mjs — Yuka-driven combat AI (2026-10-23).
 *
 * Covers the pure logic in game/js/ai/combat-state.js,
 * game/js/ai/grapple-chains.js, game/js/ai/reversal-logic.js and the
 * Yuka hook in game/js/ghost-ai.js. All randomness is injected, so
 * every test is deterministic. Wiring inside AIController.update is
 * exercised through these same brains; DOM/THREE paths are not
 * unit-tested here.
 *
 * Run: node --test game/tests/yuka-combat-ai.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const js = join(here, '..', 'js');

const cs = await import(join(js, 'ai', 'combat-state.js'));
const gc = await import(join(js, 'ai', 'grapple-chains.js'));
const rl = await import(join(js, 'ai', 'reversal-logic.js'));
const gh = await import(join(js, 'ghost-ai.js'));

const ZERO = () => 0;       // every roll succeeds
const ONE = () => 0.99999;  // every roll fails

function snap(over = {}) {
  return {
    dist: 2.0, dir: 1, myState: 'idle', foeState: 'idle',
    foeAttacking: false, foeAttackPhase: null, foeStartupFrames: null,
    onGround: true, canAct: true, stun: 0, meter: 0,
    launched: false, downed: false, foeDowned: false,
    rageOn: false, urgeOn: false, urgePips: 0, urgeReady: false,
    inBlockstun: false, lockMove: null,
    aggression: 0.7, reaction: 1.0, grabBias: 0.1, roundOver: false,
    ...over,
  };
}

/* ---------------- CombatBrain ---------------- */

test('brain boots in ground/neutral', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  assert.equal(b.region, 'ground');
  assert.equal(b.currentStateId(), 'neutral');
});

test('brain: foe attacking in range -> block (reaction 1, rolls pass)', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  b.think(snap({ foeAttacking: true, foeAttackPhase: 'startup', dist: 2.0 }), ZERO);
  assert.equal(b.currentStateId(), 'block');
  const d = b.think(snap({ foeAttacking: true, foeAttackPhase: 'startup', dist: 2.0 }), ZERO);
  assert.equal(d.state, 'block');
  assert.equal(d.move, 'hold');
});

test('brain: no threat, rolls fail -> neutral spacing', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  const d = b.think(snap({ dist: 5.0 }), ONE);
  assert.equal(b.currentStateId(), 'neutral');
  assert.equal(d.state, 'neutral');
  assert.equal(d.move, 'approach');
});

test('brain: stun -> hit state, recovers to neutral', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  b.think(snap({ myState: 'hit', stun: 0.5, canAct: false }), ZERO);
  assert.equal(b.currentStateId(), 'hit');
  const d = b.think(snap({ myState: 'idle', stun: 0, canAct: true }), ZERO);
  assert.equal(b.currentStateId(), 'neutral');
  assert.equal(d.state, 'neutral');
});

test('brain: launched -> air region, launch state; landing recovers', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  const d1 = b.think(snap({ onGround: false, launched: true, myState: 'hit', canAct: false }), ZERO);
  assert.equal(b.region, 'air');
  assert.equal(b.currentStateId(), 'launch');
  assert.equal(d1.state, 'launch');
  assert.equal(d1.move, 'tech');
  const d2 = b.think(snap({ onGround: true, canAct: true, myState: 'idle' }), ONE);
  assert.equal(b.region, 'ground');
  assert.equal(b.currentStateId(), 'neutral');
  assert.equal(d2.state, 'neutral');
});

test('brain: knockdown -> air/down state with wakeup directive', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  const d = b.think(snap({ onGround: true, downed: true, canAct: false, myState: 'down' }), ZERO);
  assert.equal(b.region, 'air');
  assert.equal(b.currentStateId(), 'down');
  assert.equal(d.move, 'wakeup');
});

test('brain: round over freezes the directive', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.7, reaction: 1 });
  const d = b.think(snap({ roundOver: true }), ZERO);
  assert.equal(d.move, 'idle');
});

test('brain: decideFromGhostSnap maps foe pressure to block', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.6, reaction: 1, grabBias: 0.1 });
  const gsnap = { dist: 2, myStance: 'standing', foeState: 'attack', myHpFrac: 1, foeHpFrac: 1, foeAttackStartup: true };
  b.decideFromGhostSnap(gsnap, ZERO); // tick 1: transitions to block
  assert.equal(b.decideFromGhostSnap(gsnap, ZERO), 'block'); // tick 2: settled
});

test('brain: decideFromGhostSnap far -> walk_in', () => {
  const b = new cs.CombatBrain(null, { aggression: 0.6, reaction: 1, grabBias: 0.1 });
  const gsnap = { dist: 8, myStance: 'standing', foeState: 'neutral', myHpFrac: 1, foeHpFrac: 1, foeAttackStartup: false };
  assert.equal(b.decideFromGhostSnap(gsnap, ONE), 'walk_in');
});

/* ---------------- GrappleChain ---------------- */

test('grapple: far away -> idle, no intent', () => {
  const g = new gc.GrappleChain(null, { grabBias: 0.1 });
  assert.equal(g.think({ dist: 5 }, ZERO), null);
  assert.equal(g.currentStateId(), 'idle');
});

test('grapple: clinch range -> tie-up, then commit-throw', () => {
  const g = new gc.GrappleChain(null, { grabBias: 0.1 });
  const first = g.think({ dist: 1.5, onGround: true, canAct: true }, ZERO);
  assert.equal(g.currentStateId(), 'clinch');
  assert.equal(first, 'tie-up');
  let intent = null;
  for (let i = 0; i < 20; i++) intent = g.think({ dist: 1.5, onGround: true, canAct: true }, ZERO);
  assert.equal(intent, 'commit-throw');
});

test('grapple: foe creates space in clinch -> back to idle', () => {
  const g = new gc.GrappleChain(null, { grabBias: 0.1 });
  g.think({ dist: 1.5, onGround: true, canAct: true }, ZERO);
  assert.equal(g.currentStateId(), 'clinch');
  g.think({ dist: 4, onGround: true, canAct: true }, ZERO);
  assert.equal(g.currentStateId(), 'idle');
});

test('grapple: stuffed in the clinch -> reversed, then idle', () => {
  const g = new gc.GrappleChain(null, { grabBias: 0.1 });
  g.think({ dist: 1.5, onGround: true, canAct: true }, ZERO);
  const intent = g.think({ dist: 1.5, onGround: true, canAct: false, myState: 'hit', stun: 0.5 }, ZERO);
  assert.equal(g.currentStateId(), 'reversed');
  assert.equal(intent, 'disengage');
});

test('grapple: throw executing -> ground chain on knockdown', () => {
  const g = new gc.GrappleChain(null, { grabBias: 0.1 });
  g.think({ dist: 1.5, onGround: true, canAct: true }, ZERO); // clinch
  g.think({ dist: 1.2, onGround: true, canAct: true, myState: 'throwing' }, ZERO);
  assert.equal(g.currentStateId(), 'throw');
  g.think({ dist: 1.2, onGround: true, canAct: true, myState: 'idle', foeDowned: true }, ZERO);
  assert.equal(g.currentStateId(), 'ground'); // transition tick: enter only
  const intent = g.think({ dist: 1.2, onGround: true, canAct: true, myState: 'idle', foeDowned: true }, ZERO);
  assert.equal(intent, 'chain-ground'); // next tick: ground state executes
});

/* ---------------- ReversalBrain ---------------- */

test('reversal: thrown -> throw-break with the arm read', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ myState: 'thrown', lockMove: { throw_break: '1|2' }, canAct: false }, ZERO);
  assert.equal(d.action, 'throw-break');
  assert.equal(d.breakInput, '1');
  assert.ok(d.confidence > 0.5);
});

test('reversal: blockstun + meter -> v-reversal', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, inBlockstun: true, meter: 60, myState: 'block', stun: 0.2 }, ZERO);
  assert.equal(d.action, 'v-reversal');
});

test('reversal: slow startup -> sidestep window', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, onGround: true, dist: 2, foeAttackPhase: 'startup', foeStartupFrames: 20 }, ZERO);
  assert.equal(d.action, 'sidestep');
});

test('reversal: fast startup -> block (the honest Tekken answer)', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, onGround: true, dist: 2, foeAttackPhase: 'startup', foeStartupFrames: 8 }, ONE);
  // ONE fails every gate -> 'none': the read failed, no fantasy parry.
  assert.equal(d.action, 'none');
  // ZERO passes the rare v-shift hard-callout gate first...
  assert.equal(r.decide({ canAct: true, onGround: true, dist: 2, foeAttackPhase: 'startup', foeStartupFrames: 8 }, ZERO).action, 'v-shift');
  // ...a mid roll skips the callout and lands the honest block.
  const d2 = r.decide({ canAct: true, onGround: true, dist: 2, foeAttackPhase: 'startup', foeStartupFrames: 8 }, () => 0.5);
  assert.equal(d2.action, 'block');
});

test('reversal: active frames in range -> block', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, dist: 2, foeAttackPhase: 'active' }, ZERO);
  assert.equal(d.action, 'block');
});

test('reversal: foe recovering in range -> punish', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, dist: 2, foeAttackPhase: 'recovery' }, ZERO);
  assert.equal(d.action, 'punish');
});

test('reversal: nothing happening -> none', () => {
  const r = new rl.ReversalBrain({ reaction: 0.8 });
  const d = r.decide({ canAct: true, dist: 5, foeAttackPhase: null }, ZERO);
  assert.equal(d.action, 'none');
});

/* ---------------- GhostAI Yuka hook ---------------- */

test('ghost: brain drives the fallback path when it has no data', () => {
  const model = new gh.GhostModel('t');
  const brain = new cs.CombatBrain(null, { aggression: 0.6, reaction: 1, grabBias: 0.1 });
  const g = new gh.GhostAI(model, () => 'fallback-action', 0.8, 0.75, brain, 1.0);
  const s = { dist: 2, myStance: 'standing', foeState: 'attack', myHpFrac: 1, foeHpFrac: 1, foeAttackStartup: true };
  g.decide(s, ZERO); // tick 1: brain transitions
  assert.equal(g.decide(s, ZERO), 'block'); // tick 2: brain drives
});

test('ghost: no brain -> old fallback path unchanged', () => {
  const model = new gh.GhostModel('t');
  const g = new gh.GhostAI(model, () => 'fallback-action');
  const s = { dist: 2, myStance: 'standing', foeState: 'neutral', myHpFrac: 1, foeHpFrac: 1, foeAttackStartup: false };
  assert.equal(g.decide(s, ZERO), 'fallback-action');
});

test('ghost: learned data still beats the brain', () => {
  const model = new gh.GhostModel('t');
  model.record('close|standing|neutral|okhp', '2');
  const brain = new cs.CombatBrain(null, { aggression: 0.6, reaction: 1, grabBias: 0.1 });
  const g = new gh.GhostAI(model, () => 'fallback-action', 0.8, 1.0, brain, 1.0);
  const s = { dist: 2, myStance: 'standing', foeState: 'neutral', myHpFrac: 1, foeHpFrac: 1, foeAttackStartup: false };
  assert.equal(g.decide(s, ZERO), '2'); // ghostMix=1, rand 0 -> ghost wins
});
