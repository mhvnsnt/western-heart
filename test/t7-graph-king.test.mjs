// King T7 FULL graph (wh-t7-graph/2) + runtime interpreter (game/js/t7graph.js). Node only: no browser, no touch,
// no model proof. Run: node --test test/t7-graph-king.test.mjs
// Every expectation below was verified independently from the source tables in earlier passes (dash/run/KBD/strings/
// motions) or is a direct table fact; the interpreter must reproduce them from the imported graph alone, in source
// priority order, without hand-written rows, and must never satisfy an unknown requirement.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const G = await import(join(ROOT, 'game/js/t7graph.js'));
const g = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t7/king/graph.json'), 'utf8'));
const cov = JSON.parse(readFileSync(join(ROOT, 'game/assets/anim/t7/king/graph.coverage.json'), 'utf8'));
const id = (n) => G.moveByName(g, n);
const name = (i) => (i == null ? null : g.moves[i].name);
const ev = G.makeEvalCond({});
const step = (from, ctx) => G.stepCancel(g, id(from), { evalCond: ev, down: [], held: [], ...ctx });
const H = (a) => a.map(([dir, down]) => ({ dir, down: down || [] }));

test('whole graph imported: every move, cancel (groups inlined), sequence, requirement; source ids kept', () => {
  assert.equal(g.format, 'wh-t7-graph/2');
  assert.equal(g.moves.length, 2787);
  assert.equal(g.moves.reduce((n, m) => n + m.cancels.length, 0), 42621);
  assert.equal(g.sequences.length, 259);
  assert.equal(name(g.stance), 'Kg_sKAM00_');
  assert.equal(name(g.aliases[2]), 'cKAM__00_');
  for (const [i, m] of g.moves.entries()) assert.equal(m.id, i);
  assert.match(g.source.json_sha256, /^[0-9a-f]{64}$/);
});

test('dash -> run is the f STATE at exactly frame 12 (requirement 0); 11 and 13 do not run', () => {
  assert.equal(name(step('Kg_sDASHF', { frame: 12, dir: 'f' }).to), 'sRUN__00F');
  assert.equal(step('Kg_sDASHF', { frame: 11, dir: 'f' }).to, null);
  assert.equal(step('Kg_sDASHF', { frame: 13, dir: 'f' }).to, null);
});

test('the re-dash (requirement with unknown condition 124) is skipped and reported, never taken', () => {
  const r = step('Kg_sDASHF', { frame: 12, dir: 'f' });
  assert.ok(r.skipped.some((s) => s.unknown.includes(124)));
  assert.notEqual(name(r.to), 'Kg_sDASHF');
});

test('dash attacks from the graph: f+1, n+2, f+3+4 (press edges)', () => {
  assert.equal(name(step('Kg_sDASHF', { frame: 5, dir: 'f', down: ['1'] }).to), 'Kg_lygerlp00');
  assert.equal(name(step('Kg_sDASHF', { frame: 5, dir: 'n', down: ['2'] }).to), 'Kg_p01');
  assert.equal(name(step('Kg_sDASHF', { frame: 5, dir: 'f', down: ['3', '4'] }).to), 'Kg_dki10');
});

test('run attacks come from the REAL run state links (sRUN__02F), not frontend rows', () => {
  assert.equal(name(step('sRUN__02F', { frame: 5, dir: 'f', down: ['3'] }).to), 'Kg_666lk');
  assert.equal(name(step('sRUN__02F', { frame: 5, dir: 'f', down: ['4'] }).to), 'Kg_runrk00');
  assert.equal(name(step('sRUN__02F', { frame: 5, dir: 'b' }).to), 'sWALK_00B');
});

test('held vs pressed: a held button is not a press; a button-less state link does not eat a press', () => {
  assert.notEqual(name(step('Kg_sDASHF', { frame: 5, dir: 'f', held: ['1'] }).to), 'Kg_lygerlp00');
  assert.notEqual(name(step('Kg_sDASHF', { frame: 12, dir: 'f', down: ['1'] }).to), 'sRUN__00F');
});

test('KBD: backdash d/b -> crouch transition; stance jab; stance d/f+1', () => {
  assert.equal(name(step('sDASH_00B', { frame: 3, dir: 'd/b' }).to), 'Kg_st2cr00B');
  assert.equal(name(step('Kg_sKAM00_', { frame: 1, dir: 'n', down: ['1'] }).to), 'Kg_lp00F');
  assert.equal(name(step('Kg_sKAM00_', { frame: 1, dir: 'd/f', down: ['1'] }).to), 'Kg_t_slpF');
});

test('input sequences: f,n,b,d/b,d,f+1 from stance -> Thrmv_B0_00 (throw); a wrong order does not', () => {
  const ok = step('Kg_sKAM00_', { frame: 1, dir: 'f', down: ['1'], history: H([['f'], ['n'], ['b'], ['d/b'], ['d'], ['d/f'], ['f', ['1']]]) });
  assert.equal(name(ok.to), 'Thrmv_B0_00');
  const bad = step('Kg_sKAM00_', { frame: 1, dir: 'f', down: ['1'], history: H([['d'], ['b'], ['f', ['1']]]) });
  assert.notEqual(name(bad.to), 'Thrmv_B0_00');
});

test('requirement evaluator: only labelled + WH-known conditions decide; everything else is unknown', () => {
  assert.equal(ev(35, 1800, {}), null, 'distance needs T7-unit distance');
  assert.equal(G.makeEvalCond({ oppDistT7: 1000 })(35, 1800), true);
  assert.equal(ev(558, 1), false, 'story battle is false in WH');
  assert.equal(ev(217, 2), null, 'character id stays unknown (no source id table)');
  assert.equal(ev(124, 0), null);
});

test('coverage is generated from the source graph (not the 643 frontend rows)', () => {
  assert.equal(cov.moves_total, 2787);
  assert.equal(cov.reachable_moves.length, cov.reachable_any_requirement);
  assert.ok(cov.reachable_unique_clips >= 700);
});
