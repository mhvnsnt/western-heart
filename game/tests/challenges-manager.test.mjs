// challenges-manager.test.mjs -- ChallengeManager progress/claim logic.
// Run: node --test game/tests/challenges-manager.test.mjs   (from repo root)
import test from 'node:test';
import assert from 'node:assert/strict';

// ---- stub browser globals ----
const store = {};
globalThis.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: (k) => { delete store[k]; },
};
globalThis.window = {};

const { ChallengeManager } = await import('../js/challenges.js');
const { challengesFor } = await import('../data/challenges.js');

function freshManager() {
  for (const k of Object.keys(store)) delete store[k];
  // pin to a date whose rotation includes wins + damage dailies
  return new ChallengeManager('2026-10-05');
}

test('manager: today() matches the deterministic rotation', () => {
  const m = freshManager();
  const t = m.today();
  assert.deepEqual(t.dailies.map((c) => c.id), challengesFor(m.day).dailies.map((c) => c.id));
  assert.equal(t.dailies.length, 3);
});

test('manager: wins accumulate and complete', () => {
  const m = freshManager();
  const winChal = m.today().dailies.find((c) => c.type === 'wins');
  assert.ok(winChal, 'a wins challenge is usually in the rotation');
  // find via direct _add (simulates recorded matches)
  for (let i = 0; i < winChal.target; i++) m._add('wins', null, 1);
  assert.ok(m.isComplete(winChal.id));
  assert.equal(m.isClaimed(winChal.id), false);
  const claimed = m.claim(winChal.id);
  assert.ok(claimed, 'claim returns the challenge');
  assert.equal(m.isClaimed(winChal.id), true);
  assert.equal(m.claim(winChal.id), null, 'double claim refused');
});

test('manager: damage and best-of-single-fight tracking', () => {
  const m = freshManager();
  const dmg = m.today().dailies.find((c) => c.type === 'damage');
  const oneFight = m.today().dailies.find((c) => c.type === 'damage_one_fight');
  if (dmg) {
    m._add('damage', null, 100);
    m._add('damage', null, 150);
    assert.equal(m.progressOf(dmg.id), 250);
  }
  if (oneFight) {
    m._best('damage_one_fight', 80);
    m._best('damage_one_fight', 60);
    assert.equal(m.progressOf(oneFight.id), 80, 'best keeps the max, not the sum');
    m._best('damage_one_fight', 120);
    assert.equal(m.progressOf(oneFight.id), 120);
  }
});

test('manager: event multiplier boosts the matching type', () => {
  const m = freshManager();
  const event = m.today().event;
  const bonusType = event.bonus.type;
  // pick any daily of the bonus type, or simulate via _add with mult
  const before = {};
  for (const d of m.today().dailies) before[d.id] = m.progressOf(d.id);
  m._add(bonusType, null, 10, event.bonus.mult);
  let boosted = false;
  for (const d of m.today().dailies) {
    if (d.type === bonusType && m.progressOf(d.id) === (before[d.id] || 0) + 10 * event.bonus.mult) boosted = true;
  }
  // (no daily of that type today -> nothing to boost; that's fine)
  assert.ok(boosted || !m.today().dailies.some((d) => d.type === bonusType));
});

test('manager: mode clears complete mode_clear dailies', () => {
  const m = freshManager();
  const mc = m.today().dailies.find((c) => c.type === 'mode_clear');
  if (!mc) return; // not in today's rotation
  m._onModeClear('other-mode');
  assert.ok(!m.isComplete(mc.id), 'wrong mode does not complete');
  m._onModeClear(mc.target);
  assert.ok(m.isComplete(mc.id), 'matching mode_clear completes');
});

test('manager: timeattack grade gate', () => {
  const m = freshManager();
  const ta = m.today().dailies.find((c) => c.type === 'timeattack');
  if (!ta) return;
  m._onTimeAttack('C');
  const needRank = { S: 0, A: 1, B: 2, C: 3 }[ta.target];
  const gotRank = 3;
  assert.equal(m.isComplete(ta.id), gotRank <= needRank);
  m._onTimeAttack('S');
  assert.ok(m.isComplete(ta.id), 'S clears any grade gate');
});

test('manager: claim grants the unlockable', async () => {
  const m = freshManager();
  const { hasUnlockable } = await import('../js/unlockables.js');
  const winChal = m.today().dailies.find((c) => c.type === 'wins');
  assert.ok(winChal);
  assert.equal(hasUnlockable(winChal.reward), false);
  for (let i = 0; i < winChal.target; i++) m._add('wins', null, 1);
  m.claim(winChal.id);
  assert.equal(hasUnlockable(winChal.reward), true, 'reward granted on claim');
});

test('manager: progress persists across instances (same day)', () => {
  const m1 = freshManager();
  const winChal = m1.today().dailies.find((c) => c.type === 'wins');
  m1._add('wins', null, 2);
  m1._save();
  const m2 = new ChallengeManager('2026-10-05');
  assert.equal(m2.day, m1.day);
  assert.equal(m2.progressOf(winChal.id), 2);
});
