/* fighter-completeness.test.mjs — Regression guard for the wiring-gap class
 * found by the fighter-completeness audit (docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md):
 *
 *   1. A fighter's per-fighter moveset file exists but is never loaded,
 *      because the loader (movesets.js loadFighterMovesets) keys by roster id
 *      and only loads ids in MOVESET_IDS. The fighter silently fights on the
 *      legacy T3 aggregate — or, with no aggregate entry, on nothing.
 *   2. A roster forms/transform target is not a MODEL_URLS key, so
 *      fighter.js _doTransform throws inside its catch and the fighter can
 *      never transform (Burger, found in the wild by this audit).
 *   3. A canon attire has a GLB + key but no ATTIRE_VARIANTS entry, so the
 *      picker can never offer it (Diablo A2, Kronos A2/A3, Awa Pop A2).
 *
 * The KNOWN_GAPS set below is the audit's owned-elsewhere list. It must
 * match reality EXACTLY: a new gap fails this test, and closing one of
 * these without removing it here also fails (update the audit doc too).
 *
 * Run: node --test game/tests/fighter-completeness.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, mkdtempSync, cpSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

// --- Load the real chain modules (sandbox copy: same pattern as
// --- model-key-guard.test.mjs; these modules are pure ESM).
const sandbox = mkdtempSync(join(process.env.TMPDIR || '/tmp', 'wh-fighter-completeness-'));
for (const f of ['roster-full.js', 'attires.js', 'movesets.js', 'material-status.js'])
  cpSync(join(ROOT, 'game/js', f), join(sandbox, f));
writeFileSync(join(sandbox, 'package.json'), '{"type":"module"}');
const { FULL_ROSTER } = await import(pathToFileURL(join(sandbox, 'roster-full.js')).href);
const { attiresFor } = await import(pathToFileURL(join(sandbox, 'attires.js')).href);
const { MOVESET_IDS } = await import(pathToFileURL(join(sandbox, 'movesets.js')).href);

function parseExportedObject(file, name) {
  const src = readFileSync(file, 'utf8');
  const start = src.indexOf(`export const ${name} = {`);
  assert.notEqual(start, -1, `${name} not found in ${file}`);
  const end = src.indexOf('\n};', start);
  const block = src.slice(start + `export const ${name} = `.length, end + 2).replace(/\/\/[^\n]*/g, '');
  return Function('return (' + block + ')')();
}
const MODEL_URLS = parseExportedObject(join(ROOT, 'game/js/assets.js'), 'MODEL_URLS');
const OVERRIDES = parseExportedObject(join(ROOT, 'game/js/attire-customizations.js'), 'ATTIRE_CUSTOMIZATIONS');
for (const [k, u] of Object.entries(OVERRIDES || {})) if (u) MODEL_URLS[k] = u;

/* Audit-owned-elsewhere gaps (docs/FIGHTER-COMPLETENESS-AUDIT-2026-10-21.md):
 * ryuji = stale pre-rename entry owned by the CornerStone lane.
 * (doc-frank-wowomomo/hood removed 2026-10-22: the dedup lane folded those
 * standalone cards into the docfrank ladder, so they are no longer roster ids
 * and cannot be moveset gaps.) */
const KNOWN_GAPS = {
  'ryuji': 'file exists, not in MOVESET_IDS (CornerStone lane)',
};

test('every roster fighter\'s own moveset file is actually loaded (or a documented gap)', () => {
  const gaps = {};
  for (const f of FULL_ROSTER) {
    const hasFile = existsSync(join(ROOT, 'game/assets/movesets', f.id + '.json'));
    const loaded = MOVESET_IDS.includes(f.id);
    if (!(hasFile && loaded)) gaps[f.id] = `file=${hasFile} loaded=${loaded}`;
  }
  assert.deepEqual(Object.keys(gaps).sort(), Object.keys(KNOWN_GAPS).sort(),
    'moveset wiring gaps changed — update the fix or KNOWN_GAPS + the audit doc:\n' +
    Object.entries(gaps).map(([k, v]) => `${k}: ${v}`).join('\n'));
});

test('every transformation target resolves to a MODEL_URLS key', () => {
  const bad = [];
  const walk = (o, fid) => {
    if (!o || typeof o !== 'object') return;
    for (const v of Object.values(o)) {
      if (v && typeof v === 'object') {
        if (v.target && !MODEL_URLS[v.target]) bad.push(`${fid}: form target '${v.target}' has no MODEL_URLS key`);
        if (v.targetModel && !MODEL_URLS[v.targetModel]) bad.push(`${fid}: transform targetModel '${v.targetModel}' has no MODEL_URLS key`);
        walk(v, fid);
      }
    }
  };
  for (const f of FULL_ROSTER) { walk(f.forms, f.id); if (f.transform) walk({ t: f.transform }, f.id); }
  assert.deepEqual(bad, [], 'unresolvable transformation targets:\n' + bad.join('\n'));
});

test('burger form keys land on the canon attire files (ATTIRE-SLOTS.md)', () => {
  assert.equal(MODEL_URLS['burger-speed-demon'], '../roster/burger/attires/attire6/model.glb');
  assert.equal(MODEL_URLS['burger-the-mouth'], '../roster/burger/attires/attire7/model.glb');
  assert.equal(MODEL_URLS['burger-demon'], '../roster/burger/attires/attire1/model.glb');
});

test('newly wired attire ladders keep the current default and resolve every variant', () => {
  for (const id of ['diablo', 'kronos', 'awapop']) {
    const f = FULL_ROSTER.find(r => r.id === id);
    const list = attiresFor(f);
    assert.ok(list.length > 1, `${id}: expected a multi-attire ladder`);
    assert.equal(list[0].model, f.model, `${id}: first variant must stay the current default model`);
    for (const v of list) assert.ok(MODEL_URLS[v.model], `${id}: variant '${v.model}' has no MODEL_URLS key`);
  }
});
