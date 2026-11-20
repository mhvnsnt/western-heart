// Owner pt213u: the owner's own model must be attire 1 (select card, hero
// render, fights). Source-game ports / reskins / retextures go later.
// Only exception: Pantera (roster/TRIPO-REGISTRY.md EXCEPTION marker).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
globalThis.localStorage ??= { getItem: () => null, setItem() {} };
const { FULL_ROSTER } = await import('../game/js/roster-full.js');
const { ATTIRE_VARIANTS, resolveFighterAttire } = await import('../game/js/attires.js');
const REG = JSON.parse(readFileSync(new URL('../game/data/owner-models.json', import.meta.url)));
const src = readFileSync(new URL('../game/js/assets.js', import.meta.url), 'utf8');
const s = src.indexOf('export const MODEL_URLS = '), e = src.indexOf('\n};', s);
const MU = Function('return (' + src.slice(s + 26, e + 2).replace(/\/\/[^\n]*/g, '') + ')')();
const ladder = f => ATTIRE_VARIANTS[f.model] || ATTIRE_VARIANTS[f.id] || [];
const EXEMPT = new Set(Object.keys(REG.exempt || {}));

test('registered owner models lead every non-exempt fighter', () => {
  const bad = [];
  for (const f of FULL_ROSTER) {
    if (EXEMPT.has(f.id)) continue;
    const own = REG.fighters[f.id]; if (!own?.length) continue;
    const first = ladder(f)[0]?.model ?? f.model;
    if (!own.includes(first)) bad.push(`${f.id}: attire1=${first}`);
    // roster key may be the ladder alias; it must point at an owner GLB
    const fight = resolveFighterAttire(f).model;
    if (!own.includes(fight)) bad.push(`${f.id}: fight model=${fight}`);
  }
  assert.deepEqual(bad, [], 'non-owner model defaulted while owner model exists');
});

test('user-provided Tripo manifests are registered as owner models', () => {
  const bad = [];
  for (const [k, u] of Object.entries(MU)) {
    const m = u.match(/roster\/([^/]+)\/attires\//); if (!m) continue;
    const man = join('game', dirname(u), 'manifest.json');
    const alt = join('game', dirname(u), 'source', 'manifest.json');
    const p = existsSync(man) ? man : existsSync(alt) ? alt : null; if (!p) continue;
    if (!/user-provided|tripo/i.test(readFileSync(p, 'utf8'))) continue;
    const f = FULL_ROSTER.find(r => r.id === m[1] || ladder(r).some(a => a.model === k));
    if (!f || EXEMPT.has(f.id) || REG.unconfirmed?.[f.id]) continue;
    if (!ladder(f).some(a => a.model === k)) continue; // not wired to a ladder
    if (!(REG.fighters[f.id] || []).includes(k)) bad.push(`${f.id}: ${k}`);
  }
  assert.deepEqual(bad, [], 'owner Tripo key wired but not in game/data/owner-models.json');
});

test('Negativo defaults to his own model; Negan reskin kept in ladder', () => {
  const f = FULL_ROSTER.find(r => r.id === 'negativo');
  assert.equal(ladder(f)[0].model, 'negativo-attire1');
  assert.ok(ladder(f).some(a => a.model === 'n3g4tiv0'));
});

test('fight path resolves enemies through the attire ladder', () => {
  const m = readFileSync(new URL('../game/js/main.js', import.meta.url), 'utf8');
  assert.match(m, /return resolveFighterAttire\(pool\[/);
  assert.match(m, /resolveFighterAttire\(getCharacterWithCustom\(enemyId\)\)/);
});
