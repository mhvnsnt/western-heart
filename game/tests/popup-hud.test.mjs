/* popup-hud.test.mjs — popup fix (owner priority #1, 2026-10-24).
 *
 * Regression tests for the UI IMMERSION LAW: no big center-screen text
 * mid-fight, no TBD anywhere in fight UI. Tekken rule: round-boundary
 * announcements (ROUND / FIGHT / K.O.) stay at boundaries; every
 * mid-fight system trigger is a HUD indicator (glow / bar / aura).
 *
 * Static source tests (no DOM/THREE needed) + one pure-rules import.
 * Run: node --test game/tests/popup-hud.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');
const src = (p) => readFileSync(join(root, p), 'utf-8');

const FIGHT_UI = [
  'game/js/main.js', 'game/js/rage.js', 'game/js/soulurge.js',
  'game/js/soul-systems.js', 'game/js/stagebreaks.js',
  'game/js/spirit-actions.js', 'game/js/finisher.js', 'game/js/game.js',
  'game/js/v-system.js', 'game/js/fighter.js',
  'game/js/tournament-ui.js', 'game/js/tournament.js',
];

/* Mid-fight files must never call the big center-screen banner. */
const NO_BANNER = [
  'game/js/rage.js', 'game/js/soulurge.js', 'game/js/stagebreaks.js',
  'game/js/spirit-actions.js', 'game/js/finisher.js',
];

test('no TBD anywhere in fight UI paths', () => {
  for (const f of FIGHT_UI) {
    assert.ok(!src(f).includes('TBD'), `${f} still contains TBD`);
  }
  assert.ok(!src('game/js/v-system.js').includes('«name TBD»'),
    'v-system.js still contains the «name TBD» marker');
});

test('no banner() calls in any mid-fight file', () => {
  for (const f of NO_BANNER) {
    assert.ok(!/\.banner\(/.test(src(f)), `${f} still calls banner()`);
  }
});

test('game.js banners are boundary-only', () => {
  const calls = [...src('game/js/game.js').matchAll(/\.banner\(([^)]*)\)/g)]
    .map((m) => m[1]);
  assert.ok(calls.length > 0, 'expected boundary banner calls in game.js');
  for (const c of calls) {
    assert.match(c, /ROUND|FIGHT|K\.O\.|DOUBLE K\.O\.|RESET/,
      `game.js banner call is not a boundary announcement: banner(${c})`);
  }
});

test('V-System UI methods are glow-only, surgeName is gone', () => {
  const main = src('game/js/main.js');
  for (const m of ['vTrigger', 'vReversal', 'vShiftBreak', 'vParry']) {
    const body = main.slice(main.indexOf(`  ${m}(`));
    const chunk = body.slice(0, body.indexOf('},') + 2);
    assert.ok(!chunk.includes('banner'), `${m} still calls banner`);
    assert.ok(chunk.includes('surgeFlash'), `${m} lost its glow indicator`);
  }
  assert.ok(!main.includes('surgeName'), 'main.js still defines surgeName');
  assert.ok(main.includes('setSoulReady'), 'main.js lacks setSoulReady');
  assert.ok(!src('game/js/game.js').includes('surgeName'),
    'game.js still calls surgeName');
});

test("Trial's Seal boundary banner is kept", () => {
  const soul = src('game/js/soul-systems.js');
  assert.ok(soul.includes("_banner(LABELS.seal)"),
    'seal boundary banner was removed; it must stay (round boundary)');
  assert.ok(!soul.includes('_banner(LABELS.release)'),
    'release still banners mid-fight');
  assert.ok(!soul.includes('_banner(LABELS.reihou)'),
    'reihou still banners mid-fight');
  assert.ok(!soul.includes('_banner(LABELS.ready)'),
    'ready still banners mid-fight (must be meter glow only)');
});

test('HUD markup: no surge-name element, nameless rage tags', () => {
  const html = src('game/index.html');
  assert.ok(!html.includes('surge-name'), 'index.html still has surge-name');
  for (const id of ['p1-rage', 'p2-rage']) {
    const m = html.match(new RegExp(`id="${id}"[^>]*>([^<]*)<`));
    assert.ok(m, `rage tag ${id} missing`);
    assert.equal(m[1].trim(), '', `rage tag ${id} still carries text`);
  }
});

test('HUD CSS: soul-ready meter glow, no surge-name rule', () => {
  const css = src('game/styles.css');
  assert.ok(!css.includes('.surge-name'), 'styles.css still has .surge-name');
  assert.ok(css.includes('.meter-wrap.soul-ready'),
    'styles.css lacks the soul-ready meter glow');
  const rageOn = css.slice(css.indexOf('.rage-tag.on'));
  assert.ok(rageOn.slice(0, 300).includes('height'),
    'rage-tag.on is not a visible nameless bar');
});

test('V-Skill catalog: no TBD names, EX variant appends EX', async () => {
  const vs = await import(join(here, '..', 'js', 'v-system.js'));
  for (const [id, v] of Object.entries(vs.VSKILLS)) {
    assert.ok(!v.name.includes('TBD'), `VSKILLS.${id} name has TBD`);
  }
  const ex = vs.vtriggerEnhance(vs.VSKILLS.default);
  assert.ok(ex.name.endsWith(' EX'), `EX name wrong: ${ex.name}`);
  assert.ok(!ex.name.includes('TBD'), 'EX name has TBD');
});
