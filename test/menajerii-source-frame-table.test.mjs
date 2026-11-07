// MENAJERII source frame table (2026-11-03): her source kit (Roger Jr., TTT2) as exact
// move + frame data from wavu.wiki (CC0), cross-checked against RBNorway (MIT via harounb),
// the Tekken 5/DR wavu page and our own TTT2 MVLT / T6 PSP COM decodes. Animation PENDING.
// Node, no browser. Run: node --test test/menajerii-source-frame-table.test.mjs
// Regenerate the table with: python3 tools/frame-data/build_menajerii_source_table.py
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as F from '../game/js/frame-data-schema.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout: a file not on disk is read from git's object store.
const src = (rel) => (existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 })).toString('utf8');

const T = JSON.parse(src('game/data/menajerii_source_frame_table.json'));
const MEN = JSON.parse(src('game/assets/movesets/menajerii.json'));
const row = (cmd) => T.rows.find((r) => r.command === cmd);

test('table header: wh-frame-row/1 at 60 fps, for menajerii, animation pending', () => {
  assert.equal(T.schema, 'wh-frame-row/1');
  assert.equal(T.fps, 60);
  assert.equal(T.fighter, 'menajerii');
  assert.match(T.animation, /^pending/);
  assert.equal(T.provenance.primary.license, 'CC0-1.0 (wavu.wiki)');
  assert.ok(T.provenance.primary.revid > 0, 'pinned wavu revision');
});

test('every row validates against game/js/frame-data-schema.js (nothing coerced)', () => {
  assert.equal(T.rows.length, T.counts.source_rows);
  assert.ok(T.rows.length >= 110, `source rows ${T.rows.length}`);
  for (const r of T.rows) {
    assert.deepEqual(F.validateFrameRow(r), [], `${r.command}: ${JSON.stringify(F.validateFrameRow(r))}`);
    assert.deepEqual(F.normalizeFrameRow(r).flags, [], `${r.command} normalises without flags`);
    assert.ok(r.source_values && r.source_values.input !== undefined, `${r.command} keeps verbatim source values`);
  }
});

test('no motion is bound: every row is animation pending, no clip reference on any row', () => {
  for (const r of T.rows) {
    assert.equal(r.animation, 'pending', r.command);
    for (const k of ['anim_ref', 'anim_t3', 't3_row', 'clip', 'bank']) assert.ok(!(k in r), `${r.command} has no ${k}`);
  }
});

test('exact source values (spot checks against the wavu TTT2 page)', () => {
  const jab = row('1');
  assert.equal(jab.name, 'Jab'); assert.equal(jab.damage, '9'); assert.equal(jab.startup, 'i10');
  assert.equal(jab.on_block, '+1'); assert.equal(jab.on_hit, '+8');
  const wup = row('b+1+4');
  assert.equal(wup.name, 'Wind Up Punch'); assert.equal(wup.damage, '81'); assert.equal(wup.startup, 'i69');
  const gs = row('f,hcf+1');
  assert.equal(gs.name, 'Giant Swing'); assert.equal(gs.damage, '45,20'); assert.equal(gs.startup, 'i10');
  const tomb = row('db,f+2+4');
  assert.equal(tomb.damage, '58'); assert.equal(tomb.startup, 'i11');
  const aks = row('db+4,3,4,3,4');
  assert.equal(aks.damage, '13,12,10,9,8'); assert.equal(aks.on_block, '-29');
  // input-buffer note dropped, raw kept
  const sh = row('f,F+2');
  assert.equal(sh.startup, 'i15'); assert.equal(sh.source_values.startup, 'i15(16~)');
});

test('join to menajerii is consistent with her file (file itself untouched)', () => {
  assert.equal(Object.keys(MEN.moves).length, T.counts.menajerii_moves_total);
  const c = { same_move: 0, input_conflict: 0, absent: 0 };
  for (const r of T.rows) {
    c[r.menajerii.status] += 1;
    if (r.menajerii.status === 'absent') assert.equal(r.menajerii.key, null, r.command);
    else assert.ok(r.menajerii.key in MEN.moves, `${r.command} -> ${r.menajerii.key}`);
  }
  assert.equal(c.same_move, T.counts.same_move);
  assert.equal(c.input_conflict, T.counts.input_conflict);
  assert.equal(c.absent, T.counts.absent);
  // the audit's 2026-11-02 known gaps are still absent from her file and now carry sourced frames
  for (const [cmd, dmg, st] of [['FC.df+2', '31', 'i16'], ['FC.df+4', '27', 'i21'], ['f+2+4', '35', 'i15~17']]) {
    const r = row(cmd);
    assert.ok(r, cmd); assert.equal(r.damage, dmg, cmd); assert.equal(r.startup, st, cmd);
  }
  assert.equal(row('f+2+4').menajerii.status, 'absent');
  assert.equal(row('f,n,d,df').menajerii.status, 'absent');
});

test('Roger inputs held by Kuma-sourced moves are reported, not hidden', () => {
  const conflicts = T.rows.filter((r) => r.menajerii.status === 'input_conflict');
  assert.equal(conflicts.length, T.counts.input_conflict);
  for (const r of conflicts) {
    const cur = MEN.moves[r.menajerii.key];
    assert.match(cur.tekken_base || '', /Kuma/, `${r.command} conflict is with a Kuma-sourced move`);
  }
  assert.equal(T.counts.conflicts_with_kuma_sourced_move, conflicts.length);
});
