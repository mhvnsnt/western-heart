/* no-wrong-body.test.mjs — CI gate (owner order 2026-10-23, issue #866).
 * No fighter may load ANOTHER character's body: not on the raw roster
 * `model:` path (enemy / prefetch / fight), not on the attire-1 path
 * (select card + 3D preview), and not through a loader fallback
 * (`|| 'pantera'`, `|| 'steve-fox'`). A fighter with no own model yet is
 * `modelPending: true, model: null` and shows the neutral MODEL PENDING
 * card instead. Run: node test/no-wrong-body.test.mjs
 */
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
globalThis.localStorage ??= { getItem: () => null, setItem() {} };
const { FULL_ROSTER } = await import('../game/js/roster-full.js');
const { attiresFor } = await import('../game/js/attires.js');

function parseObj(file, name) {
  const src = readFileSync(join(ROOT, file), 'utf8');
  const start = src.indexOf(`export const ${name} = `);
  const end = src.indexOf('\n};', start);
  const block = src.slice(start + `export const ${name} = `.length, end + 2).replace(/\/\/[^\n]*/g, '');
  return Function('return (' + block + ')')();
}
const MODEL_URLS = parseObj('game/js/assets.js', 'MODEL_URLS');
// Shared starter bodies that riders used to fall back onto.
const SHARED_BODIES = { 'steve-fox': null, pantera: 'pantera' }; // key -> the one fighter allowed to own it
const SHARED_FILES = ['assets/models/steve-fox.glb', 'assets/models/pantera.glb'];
const { MATERIAL_STATUS } = await import('../game/js/material-status.js');
const MATERIAL_QUARANTINE = new Set(Object.keys(MATERIAL_STATUS.quarantine));
const ids = new Set(FULL_ROSTER.map(f => f.id));
const fails = [];

function checkKey(f, key, path) {
  if (!key) { fails.push(`${f.id}: ${path} resolves no model but is not modelPending`); return; }
  if (key in SHARED_BODIES && SHARED_BODIES[key] !== f.id) fails.push(`${f.id}: ${path} -> shared fallback body '${key}'`);
  if (ids.has(key) && key !== f.id) fails.push(`${f.id}: ${path} -> another fighter's model key '${key}'`);
  const url = MODEL_URLS[key];
  if (!url) { fails.push(`${f.id}: ${path} key '${key}' missing from MODEL_URLS`); return; }
  const owner = (url.match(/^\.\.\/roster\/([^/]+)\//) || [])[1];
  if (owner && ids.has(owner) && owner !== f.id && !key.startsWith(owner) && !f.id.startsWith(owner))
    fails.push(`${f.id}: ${path} '${key}' -> ${url} lives in another fighter's roster folder`);
  if (SHARED_FILES.includes(url) && SHARED_BODIES[key] !== f.id) fails.push(`${f.id}: ${path} '${key}' -> shared body file ${url}`);
}
for (const f of FULL_ROSTER) {
  if (f.modelPending) {
    if (f.model) fails.push(`${f.id}: modelPending but model='${f.model}'`);
    if (attiresFor(f).length) fails.push(`${f.id}: modelPending but has attires`);
    continue;
  }
  checkKey(f, f.model, 'roster model');
  const a1 = attiresFor(f)[0];
  // Material gate: every attire quarantined -> fighter is hidden from select/fight (characters.js ROSTER).
  if (!a1 && MATERIAL_QUARANTINE.has(f.model)) continue;
  checkKey(f, a1 && a1.model, 'attire 1');
}
// Loader fallbacks onto a starter body are banned in game/js.
for (const file of readdirSync(join(ROOT, 'game/js')).filter(n => n.endsWith('.js'))) {
  const src = readFileSync(join(ROOT, 'game/js', file), 'utf8');
  for (const m of src.matchAll(/\.model\s*(\|\||\?\?)\s*['"](pantera|steve-fox)['"]/g))
    fails.push(`game/js/${file}: loader fallback '${m[0]}'`);
}
// No attire ladder rung may borrow a shared starter body (Phantom/Zui steve-fox, t183u).
for (const f of FULL_ROSTER) for (const a of attiresFor(f))
  if (a && a.model in SHARED_BODIES && SHARED_BODIES[a.model] !== f.id) fails.push(`${f.id}: attire ladder -> shared body '${a.model}'`);
// No id-level default onto Pantera (getFighter / bridge / menus).
for (const file of readdirSync(join(ROOT, 'game/js')).filter(n => n.endsWith('.js'))) {
  const src = readFileSync(join(ROOT, 'game/js', file), 'utf8');
  for (const m of src.matchAll(/(\|\||\?\?)\s*(ROSTER|FULL_ROSTER)\.find\([^\n]{0,60}?['"]pantera['"]|charId\s*(\|\||\?\?)\s*['"]pantera['"]/g))
    fails.push(`game/js/${file}: id fallback onto pantera '${m[0]}'`);
}
if (fails.length) { console.error('WRONG-BODY GATE FAILED:\n  ' + fails.join('\n  ')); process.exit(1); }
console.log(`no-wrong-body: ${FULL_ROSTER.length} fighters OK (${FULL_ROSTER.filter(f => f.modelPending).length} model-pending)`);
