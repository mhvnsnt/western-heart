/* brawler-surge.test.mjs — surgeName dead-reference fix (follow-up to
 * PR #1134, which converted mid-fight banners to ui.hudNote).
 *
 * #1078 removed ui.surgeName() (writer + #surge-name element) from
 * game/js/main.js, but game/js/brawler.js kept calling it at two sites:
 * the 'surge' attack branch and the 'transform' (surge-form) branch.
 * The real game UI has no surgeName method, so both calls throw
 * TypeError at surge time — the transform-branch throw lands BEFORE
 * the hudNote on the next line, so the SOUL SURGE note never posted.
 *
 * This test drives BOTH branches through the REAL game/js/brawler.js
 * (same data:-URL + stub-redirect harness as brawler-sim.test.mjs)
 * with a ui mock shaped like the REAL main.js ui: surgeFlash +
 * hudNote, and DELIBERATELY NO surgeName. If brawler.js ever calls
 * surgeName again, B.frame() throws and the test fails — the mock
 * cannot mask it the way the old sim mock (surgeName(){}) did.
 *
 * Expected after the fix (exactly one HUD note per surge event):
 *   'surge' attack branch -> hudNote('SOUL SURGE — ' + surge name)
 *     (this branch had NO other text display, so the note replaces
 *     the dead call instead of deleting it)
 *   'transform' branch -> the pre-existing hudNote on the next line
 *     (the dead call is deleted, NOT duplicated: a second identical
 *     hudNote in the same tick would double-post the same note)
 * Neither branch may call banner() (owner immersion law, closed
 * 2026-10-25: no center-screen text during fights).
 *
 * Run: node --test game/tests/brawler-surge.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const TESTDIR = dirname(fileURLToPath(import.meta.url));
const ROOT = join(TESTDIR, '..', '..');

register('./brawler-sim-hooks.mjs', import.meta.url);

/* ---- DOM / browser globals (same shape as the sim harness) ---- */
const statusEl = { style: {}, textContent: '' };
globalThis.document = {
  getElementById: (id) => (id === 'brawler-status' ? statusEl : null),
  createElement: (tag) => {
    if (tag === 'canvas') return { width: 64, height: 64,
      getContext: () => ({ createRadialGradient: () => ({ addColorStop(){} }),
        fillRect(){}, set fillStyle(v){} }) };
    return { style: {} };
  },
};
globalThis.requestAnimationFrame = (fn) => setTimeout(fn, 0);

/* ---- the real module under test, byte for byte ---- */
const brawlerSrc = readFileSync(join(ROOT, 'game/js/brawler.js'), 'utf8');
const BRAWLER_URL = 'data:text/javascript;base64,' + Buffer.from(brawlerSrc).toString('base64');
const { BrawlerGame } = await import(BRAWLER_URL);

/* ---- harness: real-ui-shaped ui (NO surgeName, on purpose) ---- */
function makeHarness() {
  const hudNotes = [];
  const flashes = [];
  const input = {
    brawlerMode: false, axisX: 0, axisY: 0, joyY: 0, enabled: false,
    held: { block: false }, _q: [],
    enable(on){ this.enabled = on; },
    reset(){ this.axisX=0; this.axisY=0; this.joyY=0; this._q.length=0; this.held.block=false; },
    consume(){ const q=this._q.slice(); this._q.length=0; return q; },
  };
  // Mirrors the live main.js ui surface brawler.js actually uses.
  // surgeName is ABSENT here exactly as it is absent in main.js.
  const ui = {
    setNames(){}, setRounds(){}, setStageName(){}, updateHP(){}, updateMeter(){},
    setTimer(){}, combo(){}, throwBreakPrompt(){}, throwEscape(){}, matchOver(){},
    surgeFlash(c, a){ flashes.push([c, a]); },
    hudNote(m){ hudNotes.push(m); },
  };
  const sceneStub = { add(){}, remove(){} };
  const game = {
    arena: { scene: sceneStub, setStage(){}, camOverride: null, shake(){} },
    input, _hitStop: 0, brawler: null,
    resetFightState(){ this.brawler = null; },
  };
  const char = { id: 'f0', name: 'F0', model: 'pantera',
    maxHp: 20000, dmgMul: 10,
    colors: { suit: 0x111111, trim: 0xffffff },
    surge: { color: 0xff2222, accent: 0xffffff, name: 'TEST SURGE' },
    ai: { aggression: 0.6, grabBias: 0.15, reaction: 0.55 },
    stats: { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 } };
  const roster = [char];
  const getChar = (id) => (id === 'f0' ? char : null);
  const content = {
    stages: [
      { n:1, key:'threshold', name:'THE THRESHOLD', stage:'test', sub:'', diff:0.45 },
    ],
    makeEcho: (c, d) => ({ ...c, id: c.id + '-echo' }),
    buildShadowSelf: (c) => ({ ...c, id: c.id + '-shadow' }),
  };
  const hooks = {
    onStageIntro: (i, done) => done(),
    onBossIntro: (s, k, l, done) => done(),
    onStageClear: (i, r, done) => done(),
    onVictory: (done) => done(),
    onDeath: () => {},
  };
  return { hudNotes, flashes, input, ui, game, getChar, roster, content, hooks };
}

async function startRun(h) {
  const B = new BrawlerGame({ game: h.game, input: h.input, ui: h.ui,
    getChar: h.getChar, roster: h.roster, content: h.content });
  await B.begin('f0', h.hooks);
  assert.ok(B.player, 'brawler run started with a player');
  assert.equal(B.state, 'play', 'brawler run is live');
  return B;
}

const SURGE_NOTE = 'SOUL SURGE — TEST SURGE';
const countSurgeNotes = (notes) => notes.filter((m) => m === SURGE_NOTE).length;

test("'surge' attack posts exactly one SOUL SURGE HUD note, no throw", async () => {
  const h = makeHarness();
  const B = await startRun(h);
  const before = countSurgeNotes(h.hudNotes);
  h.input._q.push('surge');
  assert.doesNotThrow(() => { for (let i = 0; i < 10; i++) B.frame(1 / 60); },
    'surge attack must not throw on the real-ui-shaped mock (no surgeName)');
  assert.equal(h.flashes.length, 1, 'surge glow (surgeFlash) still fires');
  assert.equal(countSurgeNotes(h.hudNotes), before + 1,
    `expected exactly one new '${SURGE_NOTE}' note, got notes=${JSON.stringify(h.hudNotes)}`);
});

test("'transform' surge-form posts exactly one SOUL SURGE HUD note, no throw", async () => {
  const h = makeHarness();
  const B = await startRun(h);
  B.player.meter = B.player.maxMeter;
  assert.equal(B.player.surgeForm, false, 'precondition: not yet in surge form');
  const before = countSurgeNotes(h.hudNotes);
  h.input._q.push('transform');
  assert.doesNotThrow(() => { for (let i = 0; i < 10; i++) B.frame(1 / 60); },
    'transform surge-form must not throw on the real-ui-shaped mock (no surgeName)');
  assert.equal(B.player.surgeForm, true, 'surge form actually engaged');
  assert.equal(h.flashes.length, 1, 'surge glow (surgeFlash) still fires');
  assert.equal(countSurgeNotes(h.hudNotes), before + 1,
    `expected exactly one new '${SURGE_NOTE}' note (no duplicate), got notes=${JSON.stringify(h.hudNotes)}`);
});

test('brawler.js contains no surgeName call and no banner call', () => {
  assert.ok(!/\.surgeName\(/.test(brawlerSrc), 'brawler.js still calls surgeName()');
  assert.ok(!/\.banner\(/.test(brawlerSrc), 'brawler.js calls banner() (center-screen text)');
});
