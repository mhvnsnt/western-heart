/* fighting-ai.test.mjs — FightingICE-methodology AI modules (2026-10-23).
 *
 * Covers the pure logic in game/js/ai/frame-data.js,
 * game/js/ai/reaction-delay.js and game/js/ai/mcts-select.js.
 * All randomness and clocks are injected, so every test is deterministic.
 *
 * Run: node --test game/tests/fighting-ai.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const js = join(here, '..', 'js');

const fd = await import(join(js, 'ai', 'frame-data.js'));
const rd = await import(join(js, 'ai', 'reaction-delay.js'));
const mc = await import(join(js, 'ai', 'mcts-select.js'));

const ZERO = () => 0;
const SEQ = (vals) => { let i = 0; return () => vals[i++ % vals.length]; };

/* ---------------- frame-data.js ---------------- */

test('secsToFrames / framesToSecs round-trip at 60fps', () => {
  assert.equal(fd.secsToFrames(0.1667), 10);
  assert.equal(fd.secsToFrames(0.217), 13);
  assert.equal(fd.framesToSecs(15), 0.25);
});

test('startupFramesOf: seconds become frames, frames pass through', () => {
  assert.equal(fd.startupFramesOf(0.1667), 10); // moveset seconds
  assert.equal(fd.startupFramesOf(0.217), 13);
  assert.equal(fd.startupFramesOf(26), 26);     // t7_startup_frames
  assert.equal(fd.startupFramesOf(10), 10);
  assert.equal(fd.startupFramesOf(null), null);
  assert.equal(fd.startupFramesOf(undefined), null);
});

test('parseAdvantage reads T7 strings', () => {
  assert.equal(fd.parseAdvantage('-9'), -9);
  assert.equal(fd.parseAdvantage('+4'), 4);
  assert.equal(fd.parseAdvantage('-6 (OC)'), -6);
  assert.equal(fd.parseAdvantage('KND'), null);
  assert.equal(fd.parseAdvantage('STUN'), null);
  assert.equal(fd.parseAdvantage(null), null);
});

test('frameMove normalizes a T7-sourced move record', () => {
  const m = fd.frameMove({
    input: '1', damage: 7, startup: 0.1667,
    t7_startup_frames: 10, t7_on_block: '+1', t7_on_hit: '+8',
    t7_hit_level: 'high',
  }, '1');
  assert.equal(m.startupF, 10);
  assert.equal(m.onBlock, 1);
  assert.equal(m.onHit, 8);
  assert.equal(m.isLow, false);
  assert.equal(m.damage, 7);
});

test('frameMove flags lows from hit level', () => {
  const m = fd.frameMove({ damage: 12, startup: 0.2, hit_level: 'low' }, 'd+3');
  assert.equal(m.isLow, true);
  assert.equal(m.startupF, 12);
});

test('bestPunish: max damage that fits the window, 1f margin', () => {
  const mk = (startupF, damage) => ({ startupF, damage, input: `${startupF}f` });
  const moves = [mk(10, 20), mk(14, 35), mk(16, 60)];
  // -15 punishable: 14f fits (15-1), 16f does not.
  assert.equal(fd.bestPunish(moves, 15).damage, 35);
  // -12: only the 10f fits.
  assert.equal(fd.bestPunish(moves, 12).damage, 20);
  // -10: nothing guaranteed (10f needs 11f window).
  assert.equal(fd.bestPunish(moves, 10), null);
  assert.equal(fd.bestPunish([], 15), null);
});

test('frameTrapWins: plus frames beat their fastest button', () => {
  assert.equal(fd.frameTrapWins(4, 12, 10), true);   // 12-4=8 < 10
  assert.equal(fd.frameTrapWins(-2, 12, 10), false); // 12+2=14 > 10
  assert.equal(fd.frameTrapWins(null, 12, 10), false);
});

/* ---------------- reaction-delay.js ---------------- */

test('ReactionDelay: brains see the N-frames-ago snapshot', () => {
  const d = new rd.ReactionDelay(15);
  for (let i = 0; i < 20; i += 1) d.push({ tick: i });
  assert.equal(d.delayed().tick, 4); // 20 pushes, 15f delay -> 5th snapshot
  assert.equal(d.live().tick, 19);
});

test('ReactionDelay: before the buffer fills, oldest held (never null)', () => {
  const d = new rd.ReactionDelay(15);
  d.push({ tick: 0 });
  d.push({ tick: 1 });
  assert.equal(d.delayed().tick, 0);
});

test('ReactionDelay: zero delay sees live', () => {
  const d = new rd.ReactionDelay(0);
  d.push({ tick: 7 });
  assert.equal(d.delayed().tick, 7);
});

test('delayFramesForDifficulty: 15f rookie -> 8f boss, humanlike floor', () => {
  assert.equal(rd.delayFramesForDifficulty(0), 15);
  assert.equal(rd.delayFramesForDifficulty(1), 8);
  const mid = rd.delayFramesForDifficulty(0.5);
  assert.ok(mid > 8 && mid < 15, `mid difficulty delay ${mid} in (8,15)`);
});

/* ---------------- mcts-select.js: OpponentModel ---------------- */

test('OpponentModel: learns the foe habit live', () => {
  const om = new mc.OpponentModel();
  for (let i = 0; i < 8; i += 1) om.observe('blockLow', 'neutral');
  om.observe('attack', 'neutral');
  const p = om.predict('neutral');
  assert.ok(p.blockLow > p.attack, 'low-block bias learned');
  assert.ok(p.blockLow > 0.5, `blockLow dominates: ${p.blockLow}`);
});

test('OpponentModel: Laplace smoothing keeps unseen actions possible', () => {
  const om = new mc.OpponentModel();
  const p = om.predict('neutral');
  for (const k of mc.RESPONSES) assert.ok(p[k] > 0, `${k} has nonzero prior`);
  const sum = mc.RESPONSES.reduce((a, k) => a + p[k], 0);
  assert.ok(Math.abs(sum - 1) < 1e-9, 'distribution sums to 1');
});

test('OpponentModel: learns the foe fastest button', () => {
  const om = new mc.OpponentModel();
  om.observeFoeAttack(14, 12);
  om.observeFoeAttack(10, 8);
  om.observeFoeAttack(18, 20);
  assert.equal(om.foeFastestF, 10);
  assert.ok(Math.abs(om.foeAvgDmg - 13.33) < 0.01);
});

test('OpponentModel: situations are independent', () => {
  const om = new mc.OpponentModel();
  for (let i = 0; i < 6; i += 1) om.observe('attack', 'wakeup');
  assert.ok(om.mashRate('wakeup') > om.mashRate('neutral'), 'wakeup mash learned separately');
});

/* ---------------- mcts-select.js: MCTSSelector ---------------- */

const mkMove = (input, startupF, damage, extra = {}) => ({
  input, startupF, damage, activeF: 3, recoveryF: 20,
  hitLevel: 'mid', isLow: false, onBlock: -7, onHit: 4, ...extra,
});

test('mctsRolloutsForDifficulty: heuristic-only below 0.35, scales up', () => {
  assert.equal(mc.mctsRolloutsForDifficulty(0), 0);
  assert.equal(mc.mctsRolloutsForDifficulty(0.34), 0);
  assert.ok(mc.mctsRolloutsForDifficulty(0.5) > 0);
  assert.ok(mc.mctsRolloutsForDifficulty(1) >= mc.mctsRolloutsForDifficulty(0.5));
});

test('MCTS: returns null with no candidates', () => {
  const sel = new mc.MCTSSelector({ rollouts: 8, budgetMs: 50 });
  assert.equal(sel.select({ candidates: [] }, ZERO), null);
  assert.equal(sel.select({}, ZERO), null);
});

test('MCTS: single candidate short-circuits', () => {
  const sel = new mc.MCTSSelector({ rollouts: 8, budgetMs: 50 });
  const only = mkMove('1', 10, 7);
  assert.equal(sel.select({ candidates: [only] }, ZERO), only);
});

test('MCTS: punishes a chronic low-blocker with a mid', () => {
  const om = new mc.OpponentModel();
  for (let i = 0; i < 10; i += 1) om.observe('blockLow', 'neutral');
  const sel = new mc.MCTSSelector({ rollouts: 40, budgetMs: 200 });
  const low = mkMove('d+3', 12, 12, { isLow: true, hitLevel: 'low' });
  const mid = mkMove('df+1', 13, 14, { isLow: false, hitLevel: 'mid' });
  // Deterministic rng: 0.5 sits inside blockLow's probability mass once the
  // table dominates (blockHigh takes the first ~0.07, blockLow the next ~0.73).
  const win = sel.select(
    { candidates: [low, mid], foeModel: om, situation: 'neutral' },
    () => 0.5,
  );
  assert.equal(win.input, 'df+1', 'mid beats the low-block habit');
});

test('MCTS: respects the time budget', () => {
  const cands = [];
  for (let i = 0; i < 12; i += 1) cands.push(mkMove(`m${i}`, 10 + i, 5 + i));
  const sel = new mc.MCTSSelector({ rollouts: 100000, budgetMs: 5 });
  let t = 0;
  const win = sel.select({ candidates: cands }, SEQ([0.1, 0.5, 0.9]), () => { t += 2; return t; });
  assert.ok(win && win.input, 'returned a move before the deadline');
  assert.ok(t <= 9, `stopped near the 5ms budget (clock at ${t}ms)`);
});

test('MCTS: deterministic given the same rng stream', () => {
  const cands = [mkMove('a', 10, 8), mkMove('b', 15, 25), mkMove('c', 20, 40)];
  const sel = new mc.MCTSSelector({ rollouts: 30, budgetMs: 200 });
  const ctx = { candidates: cands, foe: { startupF: 12, avgDmg: 14 } };
  const r1 = sel.select(ctx, SEQ([0.2, 0.7, 0.4, 0.9, 0.1]));
  const r2 = sel.select(ctx, SEQ([0.2, 0.7, 0.4, 0.9, 0.1]));
  assert.equal(r1.input, r2.input);
});
