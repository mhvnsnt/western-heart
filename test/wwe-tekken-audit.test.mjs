// WWE + Tekken missing-material audit pins (2026-11-02). Node, no browser.
// Run: node --test test/wwe-tekken-audit.test.mjs
// Counts are recursive blob counts from the git tree (teardown/ is NOT on
// disk in CI's sparse checkout, so this reads the tree, never the worktree).
// Exact counts pin the small, stable dirs; the big dirs use >= so other
// lanes' additive work does not break this test. If a pinned count changes,
// update docs/handoffs/WWE-TEKKEN-AUDIT-2026-11-02.md in the same PR.
import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const blobs = (dir) => {
  try {
    const out = execFileSync('git', ['ls-tree', '-r', 'HEAD', '--', dir], { cwd: ROOT, maxBuffer: 1 << 28 }).toString().trim();
    return out ? out.split('\n').length : 0;
  } catch { return 0; }
};

test('WWE teardown states match the audit', () => {
  assert.ok(blobs('teardown/wwe2k19/') >= 1678, '2K19 batch 1 landed (1,677 files + README)');
  assert.equal(blobs('teardown/wwe2k20/'), 1, '2K20 is README-only');
  assert.equal(blobs('teardown/wwe2k22/'), 1, '2K22 is README-only');
  assert.equal(blobs('teardown/wwe2k24/'), 0, '2K24 has no directory');
});

test('Tekken teardown states match the audit', () => {
  assert.equal(blobs('teardown/tekken5/'), 43, 'T5 decoded: 43 blobs (236/242 DW files)');
  assert.ok(blobs('teardown/tekken3/') >= 19499, 'T3 teardown present');
  assert.equal(blobs('teardown/tekken-tag-tournament-2/'), 56, 'TTT2 container docs only');
  assert.ok(blobs('teardown/tekken7/') >= 173, 'T7 teardown present');
});
