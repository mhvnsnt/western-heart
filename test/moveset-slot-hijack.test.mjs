// A slot never fires a longer input on its plain one (2026-11-01). Node, no browser.
// Run: node --test test/moveset-slot-hijack.test.mjs
// The merge tool's old notation reading (tools/moveset-merge/merge_sources.py notation_of) did three things:
//   * read real tilde inputs as source tags: '3~4' -> '3';
//   * dropped while-running: 'WR 4' -> '4';
//   * slotted unparsed strings on their first hit: '1,2,&amp;#58;4' -> '1'.
// So Purple Rain's 1 played the 3-hit string 1,2,:4, Phantom's 3 played 3~4, and Negativo's 4 played WR 4.
// tools/moveset-merge/repair_slots.py re-pointed them. This guard uses the game's own canonNotation: a slot on a
// button input must not fire a move whose input EXTENDS it (a tilde, just-frame or string continuation) or is its
// while-running form, when a move answering to exactly that input exists. With no such move the slot stays (the
// game's no-dead-buttons rule).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const MS_DIR = join(ROOT, 'game/assets/movesets');
const SRC_TAG = /~(?:t\d|donor)\.[\w.]+$/;

test('no moveset slot fires a longer or while-running input on its plain button input', async () => {
  await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
  const { canonNotation } = await import(join(ROOT, 'game/js/movesets.js'));
  const canon = (k, m) => {
    const raw = (m && typeof m.input === 'string' && m.input) || String(k).replace(SRC_TAG, '');
    try { return canonNotation(raw); } catch (e) { return null; }
  };
  const bad = [];
  let checked = 0;
  for (const f of readdirSync(MS_DIR).filter((x) => x.endsWith('.json'))) {
    let d;
    try { d = JSON.parse(readFileSync(join(MS_DIR, f), 'utf8')); } catch (e) { continue; }
    if (!d || typeof d.slots !== 'object' || typeof d.moves !== 'object' || !d.slots || !d.moves) continue;
    const exact = new Set();
    for (const [k, m] of Object.entries(d.moves)) { const c = canon(k, m); if (c) exact.add(c); }
    for (const [nt, k] of Object.entries(d.slots)) {
      if (!/[1-4]/.test(nt) || !d.moves[k]) continue;
      checked++;
      const c = canon(k, d.moves[k]);
      if (!c || c === nt || !exact.has(nt)) continue;
      if ([nt + '~', nt + ':', nt + ','].some((p) => c.startsWith(p)) || c === 'WR.' + nt) bad.push(`${f}: '${nt}' fires '${k}' (${c})`);
    }
  }
  assert.ok(checked > 1000, `checked ${checked} button slots`);
  assert.deepEqual(bad, [], 'fix with: python3 tools/moveset-merge/repair_slots.py --write');
});

test('Purple Rain, Phantom and Negativo plain buttons fire their single hits', () => {
  const slot = (f, n) => {
    const d = JSON.parse(readFileSync(join(MS_DIR, f + '.json'), 'utf8'));
    return { key: d.slots[n], input: d.moves[d.slots[n]].input };
  };
  for (const n of ['1', '2', '3', '4']) assert.equal(slot('purplerain', n).input, n, `purplerain ${n}`);
  for (const n of ['3', '4']) assert.equal(slot('phantom', n).input, n, `phantom ${n}`);
  assert.equal(slot('negativo', '4').input, '4', 'negativo 4');
});
