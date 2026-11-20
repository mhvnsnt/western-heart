// Thor's own Ganryu 1 / 2 / 3 / 4 (2026-11-10). Node, no browser. Run: node --test test/thor-ganryu-own-moves.test.mjs
// Canon: "Ganryu is Thor, the literal norse god of lightning" (roster/thor/CANON.md). Ganryu is not in Tekken 3, so the
// T3 pass gave Thor Bryan's rows as stand-ins, and the 2026-10-20 T7 import (deduped by input) never added Ganryu's
// own 1, 2, 2,1, 2,1,2, 3, d/f+2. tools/moveset-merge/t7_sheet_fill.py put them back. Each Bryan stand-in is kept
// verbatim under '<key>~t3proxy'. The tool also made the sheet's '4 or f+4' row reachable on 4 and on f+4.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const json = (f) => JSON.parse(readFileSync(join(ROOT, f), 'utf8'));
const ms = json('game/assets/movesets/thor.json');
const old = json('docs/archive/movesets/thor-pre-t7-fill-2026-11-10.json');
const sheet = json('game/data/t7-frame-data/t7-ganryu-lp-rp-lk-rk.json');
const pack = json('game/assets/anim/t7/ganryu/moves.pack.json');
const FILLED = { '1': '1', '2': '2', '3': '3', 'd/f+2': 'd/f+2', '2,1': '2, 1', '2,1,2': '2, 1, 2', '4': '4 or f+4', 'f+4': '4 or f+4' };

test('Thor 1 / 2 / 3 / 4 / f+4 / d/f+2 / 2,1 / 2,1,2 are Ganryu\'s own T7 sheet rows, frame data verbatim', () => {
  const byCmd = Object.fromEntries(sheet.moves.map((r) => [r.notation_original, r]));
  for (const [key, cmd] of Object.entries(FILLED)) {
    const m = ms.moves[key], s = byCmd[cmd];
    assert.ok(m && s, key);
    assert.equal(m.t7_source, ms.t7_dataset, `${key} is a T7 sheet row`);
    assert.equal(m.t7_command, cmd, key);
    assert.equal(m.t7_damage_raw, s.damage, key);
    assert.equal(m.t7_startup_frames, s.speed, key);
    assert.equal(m.t7_hit_level, s.hit_level, key);
    assert.equal(m.input, key, key);
    assert.doesNotMatch(m.name, /ganryu|bryan|tekken/i, `${key}: no source names in player-facing text`);
  }
});

test('nothing is lost: every old key is still there, every displaced Bryan stand-in kept verbatim under ~t3proxy', () => {
  for (const k of Object.keys(old.moves)) assert.ok(k in ms.moves, `${k} kept`);
  const displaced = ms.t7_sheet_fill.displaced_to_t3proxy.map((d) => d.key);
  assert.deepEqual(displaced.sort(), ['1', '2', '2,1', '2,1,2', '3', '4', 'd/f+2']);
  for (const k of displaced) {
    assert.deepEqual(ms.moves[k + '~t3proxy'], old.moves[k], `${k}~t3proxy is the old row`);
    assert.equal(old.moves[k].t3_source, 'bryan', `${k} was a Bryan T3 stand-in`);
    assert.equal(ms.hit_words[k + '~t3proxy'], old.hit_words[k], `${k}~t3proxy keeps its own hit word`);
  }
  for (const k of Object.keys(old.moves)) if (!displaced.includes(k)) assert.deepEqual(ms.moves[k], old.moves[k], `${k} untouched`);
});

test('his 1, 2, 3, 4 and f+4 play Ganryu\'s own T7 moves (cancel graph + exact frame data)', () => {
  const want = { '1': 'Sm_lp00F', '2': 'Sm_rp00', '3': 'Km_lk00', '4': 'Km_rk00', 'f+4': 'Sm_rk00F' };
  for (const [key, motbin] of Object.entries(want)) {
    assert.ok(pack.moves[key], `${key} in the pack`);
    assert.equal(pack.moves[key].motbin_move, motbin, key);
    assert.ok(pack.clips[pack.moves[key].clip], `${key} clip`);
  }
  assert.match(pack.skipped['d/f+1+2__main'] || '', /multi-hit/, 'the two-slap d/f+1+2 stays out');
});

test('the move list and the AI never offer a displaced row', async () => {
  await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
  const M = await import(join(ROOT, 'game/js/movesets.js'));
  const U = await import(join(ROOT, 'game/js/movelist-ui.js'));
  M.registerMoveset('thor', json('game/assets/movesets/thor.json'));
  const rows = U.movelistRows('thor');
  assert.ok(rows.length > 300, `${rows.length} rows`);
  assert.equal(rows.filter((r) => /~t3proxy$/.test(r.key)).length, 0, 'no ~t3proxy row listed');
  const one = rows.filter((r) => r.notation === '1');
  assert.equal(one.length, 1); assert.equal(one[0].key, '1'); assert.equal(one[0].startupF, 12, 'Ganryu\'s i12 jab');
  assert.ok(!Object.keys(M.getFighterMoveset('thor').slots).some((k) => /~t3proxy$/.test(k)), 'not slotted');
});
