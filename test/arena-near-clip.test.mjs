// Floor edge rings never fill the bottom of a portrait phone screen (2026-11-02). Node, no browser.
// Run: node --test test/arena-near-clip.test.mjs
// In portrait the fight camera pulls back to fit both fighters and sat right over the near side of a stage's glowing
// edge ring, drawn as a thick orange band behind the touch controls (live screenshots, docs/proof/2026-11-02/arena-ring/).
// Flagged rings are cut by a plane NEAR_CLIP_M in front of the camera; the far edge keeps glowing.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = (rel) => readFileSync(join(ROOT, rel), 'utf8');

test('the arena clips flagged floor rings near the camera', () => {
  const s = src('game/js/scene.js');
  assert.match(s, /this\.renderer\.localClippingEnabled = true;/);
  assert.match(s, /if \(!o\.userData \|\| !o\.userData\.nearClip \|\| !o\.material\) return;/);
  assert.match(s, /this\._nearClip\.setFromNormalAndCoplanarPoint\(f, p\);/, 'the plane follows the camera every render');
});

test('every decorative floor edge ring is flagged', () => {
  const s = src('game/js/stages.js');
  const rings = s.match(/new THREE\.TorusGeometry\((8\.9|7\.6|def\.dims\.wallDistance),[^)]*\)/g) || [];
  assert.ok(rings.length >= 4, `${rings.length} floor rings`);
  const flagged = (s.match(/userData\.nearClip = true/g) || []).length;
  assert.ok(flagged >= 4, `${flagged} rings flagged nearClip`);
});
