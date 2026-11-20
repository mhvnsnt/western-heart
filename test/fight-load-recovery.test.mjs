// Fight-load recovery v2 (2026-11-01). Node, no browser. Run: node --test test/fight-load-recovery.test.mjs
// Owner: "the loading when you pick an arena ... it keeps kicking me back out to the arena select menu and then I have
// to end up reloading the game ... over and over ... that needs to be fixed 100%".
// game/js/fight-recovery.js holds the rules main.js startFight follows: retry, SAFE LOAD, reload straight back into the
// same fight (one automatic reload per 60 s), and only then the stage screen. The browser proof (a model that will
// not download, a module that will not import, a fight that will not build) is
// tools/proof-harness/fight_load_recovery_probe.mjs.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  isModuleLoadError, claimReload, resumable, saveResume, takeResume, fightStarted, nextStep,
  RESUME_KEY, RELOAD_GUARD_KEY, RELOAD_GUARD_MS, RESUME_MAX_AGE_MS,
} from '../game/js/fight-recovery.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (rel) => readFileSync(join(ROOT, rel), 'utf8');

class MemStorage {
  constructor() { this.m = new Map(); }
  getItem(k) { return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { this.m.set(k, String(v)); }
  removeItem(k) { this.m.delete(k); }
}
const throwing = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('denied'); }, removeItem() { throw new Error('denied'); } };

test('module-load errors are recognised in every browser wording', () => {
  for (const msg of [
    'Failed to fetch dynamically imported module: https://x/game/js/fighter.js',      // Chrome
    'error loading dynamically imported module: https://x/game/js/fighter.js',        // Firefox
    'Importing a module script failed.',                                              // Safari
    "The requested module './t3anims.js' does not provide an export named 'loadT7'",  // Chrome link error
    "Importing binding name 'loadT7' is not found.",                                  // Safari link error
  ]) assert.ok(isModuleLoadError(msg), msg);
  for (const msg of ['model pantera: HTTP 404', 'stalled: no bytes for 45s', 'TypeError: x is undefined', ''])
    assert.ok(!isModuleLoadError(msg), msg);
});

test('a failure is retried, then retried in SAFE LOAD, then reloaded into, never bounced first', () => {
  assert.equal(nextStep({ moduleFailed: false, retry: 0 }), 'retry');
  assert.equal(nextStep({ moduleFailed: false, retry: 1 }), 'safe');
  assert.equal(nextStep({ moduleFailed: false, retry: 2 }), 'reload');
  // a failed import can only be fixed by a reload: no in-page retry
  assert.equal(nextStep({ moduleFailed: true, retry: 0 }), 'reload');
});

test('at most one automatic reload per minute (no reload loop), re-armed when a fight starts', () => {
  const ss = new MemStorage();
  const t = 1_000_000;
  assert.equal(claimReload(ss, t), true);
  assert.equal(ss.getItem(RELOAD_GUARD_KEY), String(t));
  assert.equal(claimReload(ss, t + 1000), false, 'a second reload inside the guard is refused');
  assert.equal(claimReload(ss, t + RELOAD_GUARD_MS - 1), false);
  assert.equal(claimReload(ss, t + RELOAD_GUARD_MS), true, 'allowed again after the guard');
  fightStarted(ss);
  assert.equal(ss.getItem(RELOAD_GUARD_KEY), null, 'a fight that started clears the guard');
  assert.equal(claimReload(ss, t + RELOAD_GUARD_MS + 10), true);
  assert.equal(claimReload(throwing, t), false, 'no storage: never reload automatically (could not stop a loop)');
});

test('the resume token brings back the same fight once, and only while fresh', () => {
  const ss = new MemStorage();
  const t = 5_000_000;
  const spirit = { p1: { enabled: true, soulId: 'rin' }, p2: null };
  assert.ok(saveResume(ss, { p1: 'pantera', p2: 'negativo', stage: 'shrine', mode: 'versus', spirit }, t));
  const r = takeResume(ss, t + 4000);
  assert.deepEqual({ ...r }, { p1: 'pantera', p2: 'negativo', stage: 'shrine', mode: 'versus', spirit, t });
  assert.equal(ss.getItem(RESUME_KEY), null, 'one use: the token is cleared when read');
  assert.equal(takeResume(ss, t + 5000), null);
  saveResume(ss, { p1: 'pantera', p2: 'negativo', stage: 'shrine' }, t);
  assert.equal(takeResume(ss, t + RESUME_MAX_AGE_MS + 1), null, 'stale token: boot normally');
  assert.equal(ss.getItem(RESUME_KEY), null, 'a stale token is cleared too');
  ss.setItem(RESUME_KEY, '{not json');
  assert.equal(takeResume(ss, t), null);
  assert.equal(takeResume(throwing, t), null);
});

test('only fights a reload can rebuild are resumed (versus / quick fights by roster id)', () => {
  assert.ok(resumable('pantera', 'negativo', { mode: 'versus' }));
  assert.ok(resumable('pantera', 'negativo', {}));
  assert.ok(!resumable('pantera', null, { mode: 'arcade', enemyChar: {} }), 'arcade ladder state lives in memory');
  assert.ok(!resumable('pantera', 'negativo', { mode: 'versus', tagTeams: { p1: [], p2: [] } }));
  assert.ok(!resumable({ id: 'x' }, 'negativo', {}));
});

test('main.js startFight follows the recovery rules (wiring guard)', () => {
  const m = src('game/js/main.js');
  assert.match(m, /from '\.\/fight-recovery\.js'/);
  assert.match(m, /const step = nextStep\(\{ moduleFailed, retry: opts\._retry \|\| 0 \}\)/, 'load catch asks nextStep');
  assert.match(m, /_safe: !!opts\._safe \|\| step === 'safe'/, 'SAFE LOAD retry');
  assert.match(m, /if \(opts\._safe\) \{[\s\S]{0,400}transform: null, forms: null/, 'SAFE LOAD drops transform models');
  assert.match(m, /_buildRetry: 1, _safe: true/, 'a fight that fails to build is rebuilt once');
  assert.match(m, /\(function resumeFight\(\) \{[\s\S]{0,200}takeResume\(ss\)/, 'boot resumes a reloaded fight');
  assert.match(m, /modes\.resumeVersus\(r\.p1, r\.p2, r\.stage, r\.spirit \|\| null\)/, 'versus resumes through the mode controller');
  // the stage screen comes back only after the rebuild and the reload were both tried
  const i = m.indexOf("console.error('[WH] startMatch failed:', err);");
  const j = m.indexOf("show('stage');", i);
  assert.ok(i > 0 && j > i, 'startMatch catch exists');
  const seg = m.slice(i, j);
  assert.ok(seg.includes('_buildRetry') && seg.includes('reloadIntoFight('), 'rebuild + reload before the stage screen');
});

test('the loading overlay stays up while the fight is still loading; versus can resume; failed imports are not cached', () => {
  const menus = src('game/js/menus.js');
  assert.match(menus, /export function keepLoading\(status\)/);
  assert.match(menus, /window\.__whFightLoading/);
  assert.match(menus, /Date\.now\(\) - t0 < 240000/, 'kept up to 4 minutes, never forever');
  const modes = src('game/js/modes.js');
  assert.match(modes, /resumeVersus\(p1id, p2id, stage, spirit = null\)/);
  assert.match(modes, /if \(resume && resume\.stage\) \{ opts\.stage = resume\.stage; opts\.skipStage = true; \}/);
  const lazy = src('game/js/lazy.js');
  assert.match(lazy, /import\(path\)\.catch\(\(e\) => \{ delete _cache\[name\]; throw e; \}\)/);
});

test('transform / form models no longer hold the fight start (LOADSPEED)', () => {
  const m = src('game/js/main.js');
  const needDecl = m.indexOf('const need = [...new Set([player.model, enemy.model].filter(Boolean))];');
  const loadCall = m.indexOf('await assets.loadModels(need,');
  assert.ok(needDecl > 0 && loadCall > needDecl);
  assert.ok(!/need\.push\([^)]*(targetModel|t\.target)/.test(m.slice(needDecl, loadCall)), 'form targets are not in the blocking list');
  assert.match(m, /assets\.loadModels\(forms, null, \{ lane: 'forms' \}\)/, 'they stream in after startMatch');
  const f = src('game/js/fighter.js');
  assert.match(f, /if \(t\.target && assets\.gltfs && !assets\.gltfs\[t\.target\]\) \{/, 'tryTransform waits for a missing form model');
});
