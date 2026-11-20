/* frame-step.test.mjs — fixed-step catch-up guard (2026-11-02).
 * WHAT THIS GUARDS: the fight loop must never run an unbounded number
 * of sim steps in one render frame. Before this fix, game.js _loop ran
 * `while (acc >= FIXED_DT) _update(FIXED_DT)` with no cap, so a 50 ms
 * hitch frame ran 6 sim steps (at FIXED_DT = 1/120) and a 100 ms hitch
 * ran 12 — each step doing fighter updates, hitbox tests and DOM HP
 * writes, which made the next frame longer still (spiral of death).
 * That spiral is what turns a designed 100-233 ms hitstop freeze into
 * multi-frame visual + input lag on a phone.
 * Run: node --test test/frame-step.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { drainFixedSteps, MAX_FIXED_STEPS } from '../game/js/frame-step.js';

const FIXED_DT = 1 / 120;

test('a normal 16.7 ms frame drains 2 steps and keeps the remainder', () => {
  const { steps, acc } = drainFixedSteps(1 / 60, FIXED_DT);
  assert.equal(steps, 2);
  assert.ok(acc >= 0 && acc < FIXED_DT, `remainder ${acc} must stay under one step`);
});

test('a 50 ms hitch frame is capped, not 6 steps (before: 6, after: 4)', () => {
  const uncapped = Math.floor(0.05 / FIXED_DT); // 6
  assert.equal(uncapped, 6);
  const { steps, acc } = drainFixedSteps(0.05, FIXED_DT);
  assert.equal(steps, MAX_FIXED_STEPS);
  assert.equal(acc, 0, 'excess accumulator is dropped, not carried over');
});

test('a 100 ms hitch frame is capped, not 12 steps (before: 12, after: 4)', () => {
  const uncapped = Math.floor(0.1 / FIXED_DT); // 12
  assert.equal(uncapped, 12);
  const { steps, acc } = drainFixedSteps(0.1, FIXED_DT);
  assert.equal(steps, MAX_FIXED_STEPS);
  assert.equal(acc, 0);
});

test('no steps when less than one fixed step is owed', () => {
  const { steps, acc } = drainFixedSteps(FIXED_DT / 2, FIXED_DT);
  assert.equal(steps, 0);
  assert.equal(acc, FIXED_DT / 2);
});

test('hitstop frames drain nothing (loop skips drain while frozen)', () => {
  // The loop only calls drainFixedSteps when _hitStop <= 0; this test
  // documents that the cap does not change hitstop itself — hitstop
  // durations in game.js (0.08-0.14 s base, up to 0.233 s wall-splat
  // via combat-systems feelFor) are a designed Tekken mechanic, and
  // tuning them is a separate owner decision, not this fix.
  const { steps } = drainFixedSteps(0, FIXED_DT);
  assert.equal(steps, 0);
});
