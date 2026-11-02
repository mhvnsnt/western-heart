// Roger Jr. bank coverage (2026-11-02): the kit lives as MENAJERII, not as a
// new file. Node, no browser. Run: node --test test/roger-bank-coverage.test.mjs
// Proves the bank exists, is wired into the moveset list + roster, carries the
// TTT2 kit markers, and documents the 6 known gaps. If a gap is filled, update
// this test AND docs/movesets/ROGER-BANK-AUDIT-2026-11-02.md together.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job is a sparse checkout without game/assets/movesets/: a
// file that is not on disk is read from git's object store (the commit under
// test), like test/creation-suite-templates.test.mjs does.
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
const src = (rel) => bytes(rel).toString('utf8');

const MEN = JSON.parse(src('game/assets/movesets/menajerii.json'));

test('the Roger Jr. kit exists as menajerii, schema v2, not a proxy', () => {
  assert.equal(MEN.fighter, 'menajerii');
  assert.equal(MEN.display, 'MENAJERII');
  assert.equal(MEN.schema_version, 2);
  assert.equal(MEN.proxy, false);
  assert.equal(Object.keys(MEN.moves).length, 193, 'menajerii move count');
});

test('menajerii is wired: moveset list + roster entry', () => {
  const ms = src('game/js/movesets.js');
  assert.match(ms, /'menajerii',/, 'menajerii is in MOVESET_IDS');
  const roster = src('game/js/roster-full.js');
  assert.match(roster, /id: 'menajerii', name: 'MENAJERII'/, 'roster entry');
  assert.match(roster, /moveset: 'menajerii', model: 'menajerii'/, 'roster moveset + model');
});

test('TTT2 kit markers are present (stance-prefixed keys resolved)', () => {
  const m = MEN.moves;
  assert.equal(m['ROS 1'].name, 'Wind-up Hook', 'Rocket follow-up ROS 1');
  assert.equal(m['ROS 1+2'].name, 'Road Roller', 'Rocket follow-up ROS 1+2');
  assert.equal(m['BOB 1'].name, 'Windmill Punch', 'Bobbin follow-up BOB 1');
  assert.equal(m['d/b+4'].name, 'Animal Kick Rush start', 'AKS entry');
  assert.equal(m['d/b+4,3,4,3,4'].name, 'Animal Kick Rush', 'AKS chain');
  assert.equal(m['b+1+4'].name, 'Wind Up Punch', 'unblockable');
  assert.equal(m['b+1+4'].hit_range, 'unblockable');
  assert.ok(m['f,b,d/b,d,d/f,f+1'], 'Giant Swing under its full input');
  assert.ok(m['d,d/f,f+1'], 'Pile Driver under d,d/f,f+1');
  assert.ok(m['u+4'].input_slots.includes('u/f+4'), 'hopkick via u+4 slots');
  const tenA = (MEN.combos || []).find((c) => c.name === 'Tenstring A');
  assert.ok(tenA, 'Tenstring A combo');
  assert.equal(tenA.input, 'b+1,2,1,4,3,3,3,4,3,2');
});

test('frame coverage: at least 154/193 moves carry a startup', () => {
  const withStartup = Object.values(MEN.moves).filter((v) => v.startup != null).length;
  assert.ok(withStartup >= 154, `startup coverage ${withStartup}/193`);
});

test('known gaps are documented absent (update test + doc when filled)', () => {
  const m = MEN.moves;
  for (const gap of ['d+1', 'FC.df+2', 'FC.df+4', '1+2+3+4', 'f,n,d,df']) {
    assert.ok(!(gap in m), `gap still open (expected absent): ${gap}`);
  }
  const tenB = (MEN.combos || []).find((c) => c.input === 'b+1,2,1,4,3,3,3+4,2,1+2');
  assert.ok(!tenB, 'gap still open (expected absent): Tenstring B');
});
