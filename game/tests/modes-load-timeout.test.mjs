/* modes-load-timeout.test.mjs — modes.js import timeout + retry (2026-11-15).
 * WHAT THIS GUARDS: game/js/main.js getModes() must never hang forever
 * on a wedged dynamic import. Observed live 2026-11-15 (main 528aeea8):
 * the first mode tap's modes.js import hung, window.__modes never became
 * true, no menuFail toast appeared, and re-clicks shared the same hung
 * promise — 5 Menajerii attempts in a row, all dead before any fight.
 * The fix (lazy.js loadWithRetry + dropLazy, wired into getModes) bounds
 * every import wait with a timeout, retries once with a fresh promise,
 * and lets the call sites' existing .catch(() => menuFail(...)) surface
 * a visible error. These tests cover the mechanism in lazy.js: main.js
 * itself is the boot bundle and is not importable in node.
 * Run: node --test game/tests/modes-load-timeout.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadWithRetry, dropLazy } from '../js/lazy.js';

const never = () => new Promise(() => {});

test('loadWithRetry resolves with the loader value, loader called once', async () => {
  let calls = 0;
  const value = await loadWithRetry(() => { calls += 1; return Promise.resolve('modes-ok'); }, { timeoutMs: 500, label: 'modes.js' });
  assert.equal(value, 'modes-ok');
  assert.equal(calls, 1);
});

test('loadWithRetry rejects with a timeout error when the loader never settles', async () => {
  let calls = 0;
  await assert.rejects(
    loadWithRetry(() => { calls += 1; return never(); }, { timeoutMs: 50, retryDelayMs: 5, label: 'modes.js' }),
    (err) => {
      assert.match(err.message, /modes\.js timed out after 50ms/);
      return true;
    },
  );
  // First attempt + one retry, then the timeout error is thrown.
  assert.equal(calls, 2);
});

test('loadWithRetry retries once after a rejection and succeeds', async () => {
  let calls = 0;
  const value = await loadWithRetry(() => {
    calls += 1;
    return calls === 1 ? Promise.reject(new Error('first fetch dropped')) : Promise.resolve('second try ok');
  }, { timeoutMs: 500, retryDelayMs: 5, label: 'modes.js' });
  assert.equal(value, 'second try ok');
  assert.equal(calls, 2);
});

test('loadWithRetry retries once after a timeout and succeeds', async () => {
  let calls = 0;
  const value = await loadWithRetry(() => {
    calls += 1;
    return calls === 1 ? never() : Promise.resolve('late fetch landed');
  }, { timeoutMs: 50, retryDelayMs: 5, label: 'modes.js' });
  assert.equal(value, 'late fetch landed');
  assert.equal(calls, 2);
});

test('loadWithRetry throws the last error when the retry also fails', async () => {
  let calls = 0;
  await assert.rejects(
    loadWithRetry(() => {
      calls += 1;
      return Promise.reject(new Error(`fail #${calls}`));
    }, { timeoutMs: 500, retryDelayMs: 5, label: 'modes.js' }),
    (err) => {
      assert.equal(err.message, 'fail #2');
      return true;
    },
  );
  assert.equal(calls, 2);
});

test('loadWithRetry treats a synchronous loader throw as a failure and retries', async () => {
  let calls = 0;
  const value = await loadWithRetry(() => {
    calls += 1;
    if (calls === 1) throw new Error('sync boom');
    return Promise.resolve('recovered');
  }, { timeoutMs: 500, retryDelayMs: 5, label: 'modes.js' });
  assert.equal(value, 'recovered');
  assert.equal(calls, 2);
});

test('loadWithRetry with retries: 0 does not retry', async () => {
  let calls = 0;
  await assert.rejects(
    loadWithRetry(() => { calls += 1; return Promise.reject(new Error('nope')); }, { timeoutMs: 500, retries: 0, label: 'modes.js' }),
    /nope/,
  );
  assert.equal(calls, 1);
});

test('dropLazy is a safe no-op for names that were never cached', () => {
  assert.doesNotThrow(() => dropLazy('modes'));
  assert.doesNotThrow(() => dropLazy('no-such-module'));
});
