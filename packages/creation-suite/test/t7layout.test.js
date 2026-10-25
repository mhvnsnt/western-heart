import test from 'node:test';
import assert from 'node:assert/strict';
import { T7_SLOTS, T7_REGION_TABS, T7_SLOT_BY_CODE, groupForMenu, regionTabOf } from '../src/t7layout.js';
import { SPINE, SPINE_BY_ID } from '../src/slotmap.js';

test('every T7 slot code maps onto a spine slot with the same t7 id', () => {
  for (const s of T7_SLOTS) {
    const sp = SPINE_BY_ID[s.spine];
    assert.ok(sp, `spine missing ${s.spine}`);
    assert.equal(sp.t7, s.code, `${s.spine} t7 id`);
  }
});
test('region tabs cover every slot code exactly once', () => {
  const codes = T7_REGION_TABS.flatMap((t) => t.codes).sort((a, b) => a - b);
  assert.deepEqual(codes, T7_SLOTS.map((s) => s.code).sort((a, b) => a - b));
  assert.equal(new Set(codes).size, codes.length);
});
test('record counts sum to the parsed item table (23,548 minus untokened rows)', () => {
  const n = T7_SLOTS.reduce((a, s) => a + s.records, 0);
  assert.ok(n > 23000 && n <= 23548, String(n));
});
test('groupForMenu groups by tab/slot', () => {
  const g = groupForMenu([{ id: 'a', s: 'upper' }, { id: 'b', s: 'hair' }], (e) => e.s);
  assert.equal(g.find((t) => t.id === 'upper').slots.find((s) => s.code === 9).entries.length, 1);
  assert.equal(regionTabOf('hair').id, 'head');
  assert.equal(T7_SLOT_BY_CODE[11].spine, 'lower');
  assert.ok(SPINE.length >= 25);
});
