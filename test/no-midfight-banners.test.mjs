// No mid-fight center-screen banners (owner immersion law, CLOSED 2026-10-25):
// if text pops up in the middle of the screen during a fight, it is removed,
// no matter what it says. Only round-boundary ROUND / FIGHT! / K.O. /
// DOUBLE K.O. stay center-screen. Everything else that mattered moved to
// ui.hudNote() — small HUD-side text under the health bars.
//
// Static source test (no DOM/THREE needed), in the style of
// test/overlay-pointer-events.test.mjs (plain asserts, repo-root relative).
// Run: node test/no-midfight-banners.test.mjs   (from repo root)
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';

const src = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');

/* Files whose banner calls were converted to hudNote in this lane. */
const CONVERTED = {
  'game/js/team-battle.js': 8,
  'game/js/brawler.js': 11,
  'game/js/training.js': 7,
  'game/js/modes.js': 18,
  'game/js/episodes.js': 1,
  'game/js/ranks.js': 1,
  'game/js/replay.js': 2,
  'game/js/soul-systems.js': 1,
};

for (const [f, min] of Object.entries(CONVERTED)) {
  const s = src(f);
  assert.ok(!/\.banner\(/.test(s), `${f} still calls banner()`);
  assert.ok(!/\.surgeName\(/.test(s), `${f} still calls surgeName() (dead since #1078)`);
  const notes = (s.match(/hudNote\(/g) || []).length;
  assert.ok(notes >= min,
    `${f} has ${notes} hudNote calls, expected >= ${min} (info must survive as a HUD note, not vanish)`);
}

/* game.js: only round-boundary calls may remain center-screen. */
{
  const s = src('game/js/game.js');
  const calls = [...s.matchAll(/\.banner\(([^)]*)\)/g)].map((m) => m[1]);
  assert.ok(calls.length === 5,
    `game.js has ${calls.length} banner calls, expected exactly 5 (ROUND, FIGHT!, K.O. x2, DOUBLE K.O.)`);
  for (const c of calls) {
    assert.match(c, /ROUND|FIGHT|K\.O\.|DOUBLE K\.O\./,
      `game.js banner call is not a boundary announcement: banner(${c})`);
  }
  assert.ok(s.includes("hudNote('RESET — DUMMY RESTORED')"),
    'game.js RESET — DUMMY RESTORED did not move to hudNote');
}

/* The banner definition itself stays (game.js keeps using it); the HUD note exists. */
{
  const main = src('game/js/main.js');
  assert.ok(main.includes('banner(text)'), 'main.js lost the banner() definition');
  assert.ok(main.includes('hudNote(text)'), 'main.js lacks hudNote()');
  const html = src('game/index.html');
  assert.ok(html.includes('id="hud-note"'), 'index.html lacks the #hud-note element');
  const css = src('game/styles.css');
  assert.ok(/\.hud-note\s*\{[^}]*top:\s*104px/.test(css),
    'styles.css lacks the top-HUD .hud-note rule');
  assert.ok(!/\.hud-note\s*\{[^}]*inset:\s*0/.test(css),
    '.hud-note must not be fullscreen/centered');
}

/* WebGL context-lost error path is kept, not a fight popup: the renderer is
   dead in that state, so the message is an error screen, not mid-fight text. */
assert.ok(src('game/js/scene.js').includes('GRAPHICS PAUSED'),
  'scene.js lost the WebGL context-lost error message');

console.log('no-midfight-banners: ok (0 banner calls in converted files, game.js boundary-only, hudNote wired)');
