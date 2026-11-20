
/* ---------------- AIController wiring (mock-fighter integration) ---------------- */

/* fighting-ai-integration.test.mjs — AIController wiring (2026-10-23).
 *
 * Mock-fighter integration for game/js/ai.js: the FightingICE-methodology
 * wiring (reaction delay, opponent model, MCTS, frame-data punishes)
 * exercised through AIController.update(). No DOM/THREE.
 *
 * Run: node --test game/tests/fighting-ai-integration.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const js = join(here, '..', 'js');

const mc = await import(join(js, 'ai', 'mcts-select.js'));
const rd = await import(join(js, 'ai', 'reaction-delay.js'));
const aiMod = await import(join(js, 'ai.js'));

function mockFighter(over = {}) {
  return {
    state: 'idle', dead: false, onGround: true, stun: 0, meter: 0,
    lockMove: null, _rageOn: false, _urgeOn: false, _urgePips: 0,
    _urgeUsed: false, _movesetId: 'pantera', char: { id: 'pantera' },
    root: { position: { x: 0 } },
    _attackPhase: null, attack: null, lastAttack: null,
    _blocked: false,
    canAct() { return this.state === 'idle'; },
    isBlocking() { return this._blocked; },
    tryMove() { return true; },
    tryBlock(on) { this._blocked = !!on; if (on) this.state = 'block'; return true; },
    tryVTrigger() { return true; },
    tryVReversal() { return true; },
    tryVShift() { return true; },
    trySidestep() { return true; },
    tryDodge() { return true; },
    tryVSkill() { return true; },
    tryJump() { return true; },
    tryCrouch() { return true; },
    tryThrowBreak() { return true; },
    tryAttack(n) {
      this.lastAttack = n; this.state = 'attack'; this._attackPhase = 'startup';
      return true;
    },
    ...over,
  };
}

function mockPlayer(over = {}) {
  return {
    state: 'idle', _attackPhase: null, attack: null,
    root: { position: { x: 3 } },
    ...over,
  };
}

test('AIController: boots with delay + opponent model + MCTS at high difficulty', () => {
  const c = new aiMod.AIController(mockFighter(), { difficulty: 1 });
  assert.equal(c.reactionDelayFrames, 8);
  assert.ok(c.mcts instanceof mc.MCTSSelector);
  assert.ok(c.foeModel instanceof mc.OpponentModel);
  assert.ok(c._delay instanceof rd.ReactionDelay);
});

test('AIController: rookie gets 15f delay and heuristic-only brain', () => {
  const c = new aiMod.AIController(mockFighter(), { difficulty: 0 });
  assert.equal(c.reactionDelayFrames, 15);
  assert.equal(c.mcts, null);
});

test('AIController: update() runs many ticks without throwing', () => {
  const f = mockFighter();
  const p = mockPlayer();
  const c = new aiMod.AIController(f, { difficulty: 0.8, aggression: 0.7, reaction: 0.7 });
  for (let i = 0; i < 300; i += 1) {
    // The foe dances: approach, attack with a real frame-data move, block.
    p.root.position.x = 3 - (i % 60) * 0.05;
    if (i % 50 === 25) {
      p.state = 'attack'; p._attackPhase = 'startup';
      p.attack = { startup: 0.25, recovery: 0.5, damage: 12, hit_level: 'mid' };
    } else if (i % 50 === 40) {
      p.state = 'block'; p._attackPhase = null; p.attack = null;
    } else if (i % 50 === 0) {
      p.state = 'idle'; p._attackPhase = null; p.attack = null;
    }
    if (f.state === 'attack' && i % 7 === 0) { f.state = 'idle'; f._attackPhase = null; }
    c.update(1 / 60, p);
  }
  assert.ok(true, 'survived 300 ticks');
});

test('AIController: observes the foe fastest button and guard height', () => {
  const f = mockFighter();
  const c = new aiMod.AIController(f, { difficulty: 0.8 });
  const p = mockPlayer({ state: 'attack', _attackPhase: 'startup',
    attack: { startup: 0.1667, damage: 10, hit_level: 'mid' } });
  for (let i = 0; i < 5; i += 1) c.update(1 / 60, p);
  assert.equal(c.foeModel.foeFastestF, 10, 'learned the 10f jab');
  // Now the foe blocks my low: guard-height read.
  c._lastMyMove = { input: 'd+3', isLow: true };
  c._blockCounted = false;
  const pb = mockPlayer({ state: 'block' });
  c.update(1 / 60, pb);
  assert.ok(c.foeModel.lowBlockBias() > 0.2, 'logged the low block');
});

test('AIController: foeStartupFrames reaches the brains in FRAMES', () => {
  const f = mockFighter();
  const c = new aiMod.AIController(f, { difficulty: 0.5 });
  const p = mockPlayer({ state: 'attack', _attackPhase: 'startup',
    attack: { startup: 0.433, damage: 21, hit_level: 'mid' } }); // 26f
  const snap = c._snapshot(p);
  assert.equal(snap.foeStartupFrames, 26, 'seconds converted to frames');
});

test('AIController: whiff punish uses the frame window, not a random draw', () => {
  const f = mockFighter();
  const c = new aiMod.AIController(f, { difficulty: 0.9, reaction: 1 });
  // Foe in recovery with a long-recovery move: 30f window.
  const p = mockPlayer({ state: 'attack', _attackPhase: 'recovery',
    attack: { startup: 0.2, recovery: 0.5, damage: 15, hit_level: 'mid' } });
  p.root.position.x = 1.5;
  c._whiffPunish(f, p);
  assert.ok(f.lastAttack, 'threw a punish');
});

test('AIController: _smartAttack falls back to limbs when no moveset loaded', () => {
  const f = mockFighter();
  const c = new aiMod.AIController(f, { difficulty: 0.9 });
  c._smartAttack(f, 'mid'); // playedMoveset null in Node -> fallback path
  assert.ok(['1', '2', '3', '4'].includes(String(f.lastAttack)), `fell back to limb: ${f.lastAttack}`);
});
