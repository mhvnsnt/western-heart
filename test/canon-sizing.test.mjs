// Canon sizing must cover every fighter and every version, and not regress.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { CANON_SIZING, sizingFor, STANCE_PER_CM } from '../game/data/canon-sizing.js';
const ids = [...readFileSync(new URL('../game/js/roster-full.js', import.meta.url), 'utf8').matchAll(/\bid: '([a-z0-9_-]+)', name:/g)].map(m => m[1]);
assert.ok(ids.length >= 50, 'roster parse');
for (const id of ids) {
  const f = CANON_SIZING[id]; assert.ok(f, `no canon sizing for ${id}`);
  assert.ok(f.canon && f.body, `${id}: canon source + body required`);
  for (const [k, v] of Object.entries(f.versions)) {
    assert.ok(v.height_cm >= 40 && v.height_cm <= 400, `${id}/${k} height`);
    assert.ok(v.girth >= 0.75 && v.girth <= 1.45, `${id}/${k} girth`);
    assert.ok(v.src, `${id}/${k} src`);
  }
}
// Locked owner rules (2026-10-23): Burger default is Bob-sized (196 cm) and Bob-wide.
const b = CANON_SIZING.burger.versions;
assert.equal(b.burger.height_cm, 196); assert.ok(b.burger.girth > 1);
assert.ok(b['burger-demon'].height_cm > b.burger.height_cm, 'final demon is the biggest');
assert.ok(b['burger-attire6'].height_cm < b.burger.height_cm, 'speed demon is human-sized');
assert.ok(Object.keys(b).length >= 10, 'every Burger version sized');
assert.ok(sizingFor('burger')); assert.equal(Math.abs(STANCE_PER_CM * 200 - 1.634) < 1e-9, true);
console.log(`canon-sizing: ${ids.length} fighters ok`);
