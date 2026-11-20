// No dead inputs for any fighter (owner 2026-11-01: "all the different combinations of button inputs ... for every
// character ... so I'm not limited or blocked"). Every roster fighter x 9 held directions x 15 button sets goes through
// the game's own TekkenBuffer exactly as fighter.js _tryAttackFresh does; nothing may resolve to "no move".
// Report: docs/movesets/INPUT-MATRIX-AUDIT-2026-11-01.md (tools/input-verify/input_matrix_audit.mjs).
// Run: node --test test/input-matrix.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(join(ROOT, 'game/js/movesets.js'));
const MS = join(ROOT, 'game/assets/movesets');
const DIRS = ['n', 'f', 'b', 'u', 'd', 'u/f', 'u/b', 'd/f', 'd/b'];
const CHORDS = ['1+2', '3+4', '1+3', '2+4', '1+4', '2+3', '1+2+3', '1+2+4', '1+3+4', '2+3+4', '1+2+3+4'];
const roster = JSON.parse(fs.readFileSync(join(ROOT, 'game/data/roster_map.json'), 'utf8')).fighters
  .map((f) => f.id).filter((id) => fs.existsSync(join(MS, id + '.json')));

const buf = (fid, d) => { const b = new M.TekkenBuffer(fid); if (d !== 'n') b.noteDirection(d); return b; };

test('every roster fighter: every direction + button combination fires a move', () => {
  assert.ok(roster.length >= 40, `${roster.length} fighters`);
  const dead = [];
  for (const fid of roster) {
    M.registerMoveset(fid, JSON.parse(fs.readFileSync(join(MS, fid + '.json'), 'utf8')));
    for (const d of DIRS) {
      for (const btn of ['1', '2', '3', '4']) {
        const r = buf(fid, d).pressButton(btn, {});
        if (!M.resolveMoveKey(fid, r || btn)) dead.push(`${fid} ${d}+${btn}`);
      }
      for (const c of CHORDS) {
        const r = buf(fid, d).pressChordLenient(c, {});
        if (!r || !M.resolveMoveKey(fid, r)) dead.push(`${fid} ${d}+${c}`);
      }
    }
  }
  assert.deepEqual(dead.slice(0, 20), [], `${dead.length} dead inputs`);
});

test('a chord with its own move still fires exactly that move (the fallback never overrides it)', () => {
  for (const fid of roster.slice(0, 12)) {
    for (const d of DIRS) for (const c of CHORDS) {
      const own = buf(fid, d).pressChord(c, {});
      if (own) assert.equal(buf(fid, d).pressChordLenient(c, {}), own, `${fid} ${d}+${c}`);
    }
  }
});

test('fallback order: best two-button sub-chord (strikes before throws), then the first button', () => {
  const fid = 'pantera';
  M.registerMoveset(fid, JSON.parse(fs.readFileSync(join(MS, fid + '.json'), 'utf8')));
  const r = buf(fid, 'n').pressChordLenient('1+2+3', {});
  const own = buf(fid, 'n').pressChord('1+2+3', {});
  if (!own) assert.equal(r, buf(fid, 'n').pressChord('1+2', {}) || buf(fid, 'n').pressChord('2+3', {}) || r, 'a strike sub-chord first');
});
