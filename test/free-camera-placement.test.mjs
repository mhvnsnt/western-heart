// Free camera placement (owner 2026-10-31): the FREE CAMERA button "is always covering up stuff ... the main menu
// and the character select menu and in the fight in the arena select ... should only be there where it's
// appropriate". It lives behind the fight's PAUSE menu, never as a free-floating button over menus or the HUD,
// and it ends itself when the fight ends. Node, no browser. Run: node --test test/free-camera-placement.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (f) => readFileSync(join(ROOT, f), 'utf8');

test('no free-floating FREE CAMERA button is created at boot', () => {
  const fc = src('game/js/free-camera.js');
  const install = fc.slice(fc.indexOf('export function installFreeCamera'));
  assert.ok(install.length > 0, 'installFreeCamera exists');
  assert.doesNotMatch(install, /createElement\(\s*'button'\s*\)/, 'installFreeCamera must not create a button');
  assert.doesNotMatch(install, /document\.body\.appendChild/, 'installFreeCamera must not append UI to the page');
  assert.doesNotMatch(fc, /id\s*=\s*'free-cam-toggle'/, 'the old always-on toggle id is gone');
});

test('FREE CAMERA is an entry of the fight pause menu, and resumes the fight before taking the camera', () => {
  const m = src('game/js/menus.js');
  const pause = m.slice(m.indexOf('<div id="wh-pause"'), m.indexOf('<div id="wh-clothing"'));
  assert.match(pause, /data-wh="pause-freecam"[^>]*>FREE CAMERA</, 'pause menu entry');
  assert.match(m, /\[data-wh="pause-freecam"\]'\)\.addEventListener\('click'[\s\S]{0,200}resumeGame\(\);[\s\S]{0,120}freeCamera\.enter\(\)/,
    'the entry resumes, then enters the free camera');
});

test('the free camera ends itself when the fight is no longer running', () => {
  const fc = src('game/js/free-camera.js');
  const loop = fc.slice(fc.indexOf('  _loop() {'), fc.indexOf('  _loop() {') + 400);
  assert.match(loop, /!g\.running && !g\.brawler\) \{ this\.exit\(\); return; \}/);
});
