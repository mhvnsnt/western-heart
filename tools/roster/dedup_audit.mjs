#!/usr/bin/env node
/* WESTERN HEART — character/stage select dedup audit (node regression test).
   Owner rule 2026-10-22: "attires ladder into their fighter — an attire must
   NOT appear as its own separate selectable model UNLESS the user explicitly
   said so."

   Run from the repo root:  node tools/roster/dedup_audit.mjs
   Exit 0 = all checks pass; non-zero = first failure (message on stderr).

   Checks:
   1. Roster ids unique; tiers (SOUL_IDS/MAIN_IDS/bonus) partition the roster.
   2. Every folded attire-card is gone from the roster AND its model lives in
      the target fighter's ATTIRE_VARIANTS ladder (re-homed, not deleted).
   3. No remaining roster entry duplicates another entry's name while its
      model sits in that entry's ladder (the fold invariant).
   4. Every ladder model is a wired MODEL_URLS key (no dangling entries).
   5. tripo-fighters.json ids are all live roster ids.
   6. Stage ids unique across all stage tiers (incl. computed id schemes).
   7. Doc Frank's per-attire forms map covers every folded attire model.
*/
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');

let failures = 0;
function check(name, cond, detail = '') {
  if (cond) console.log(`  ok  ${name}`);
  else { failures++; console.error(`  FAIL ${name}${detail ? ' — ' + detail : ''}`); }
}

const { FULL_ROSTER, SOUL_IDS, MAIN_IDS, getRosterByTier } =
  await import('../../game/js/roster-full.js');
const { ATTIRE_VARIANTS, attiresFor } =
  await import('../../game/js/attires.js');

console.log('== roster ==');
{
  const ids = FULL_ROSTER.map((f) => f.id);
  check('roster ids unique', new Set(ids).size === ids.length);
  const t = getRosterByTier();
  const tiered = [...t.souls, ...t.main, ...t.bonus].map((f) => f.id);
  check('tiers partition the roster',
    tiered.length === ids.length && new Set(tiered).size === ids.length &&
    tiered.every((id) => ids.includes(id)));
  check('souls tier matches SOUL_IDS',
    t.souls.map((f) => f.id).join(',') === SOUL_IDS.join(','));
  check('main tier matches MAIN_IDS',
    t.main.map((f) => f.id).join(',') === MAIN_IDS.join(','));
}

console.log('== folds (2026-10-22 audit) ==');
const FOLDED = {
  // removed card id -> fighter id whose ladder now carries its model
  jin_soul: 'phantom',
  'demonio-bloodline-ember': 'demonio',
  'demonio-winged': 'demonio',
  'demonio-human': 'demonio',
  'doc-frank-wowomomo': 'docfrank',
  'doc-frank-hood': 'docfrank',
  'doc-frank-frankenstein': 'docfrank',
  'doc-frank-machine-shop': 'docfrank',
  'charger-attire2': 'charger',
  'kronos-attire2': 'kronos',
};
// model each folded card carried (from the pre-fold roster)
const FOLDED_MODELS = {
  jin_soul: 'steve-fox',
  'demonio-bloodline-ember': 'demonio-bloodline-ember',
  'demonio-winged': 'demonio-winged',
  'demonio-human': 'demonio-human',
  'doc-frank-wowomomo': 'doc-frank-wowomomo',
  'doc-frank-hood': 'doc-frank-hood',
  'doc-frank-frankenstein': 'doc-frank-frankenstein',
  'doc-frank-machine-shop': 'doc-frank-machine-shop',
  'charger-attire2': 'charger-attire2',
  'kronos-attire2': 'kronos-attire2',
};
{
  const ids = new Set(FULL_ROSTER.map((f) => f.id));
  for (const [card, fighter] of Object.entries(FOLDED)) {
    check(`card '${card}' removed`, !ids.has(card));
    const f = FULL_ROSTER.find((x) => x.id === fighter);
    const ladder = attiresFor(f).map((a) => a.model);
    check(`model '${FOLDED_MODELS[card]}' re-homed in '${fighter}' ladder`,
      ladder.includes(FOLDED_MODELS[card]),
      `ladder=[${ladder.join(',')}]`);
  }
}

console.log('== no attire standing alone ==');
{
  // Invariant: no two roster entries share a display name where one entry's
  // model appears in the other's attire ladder (that is the fold shape).
  const problems = [];
  for (const a of FULL_ROSTER) {
    for (const b of FULL_ROSTER) {
      if (a.id === b.id || a.name !== b.name) continue;
      const ladder = attiresFor(b).map((x) => x.model);
      if (ladder.includes(a.model)) problems.push(`${a.id} duplicates ${b.id}`);
    }
  }
  check('no duplicate selectable attires', problems.length === 0, problems.join('; '));
}

console.log('== ladder models wired ==');
{
  const src = read('game/js/assets.js');
  const keys = new Set([...src.matchAll(/^\s*'?([\w-]+)'?\s*:\s*'[^']*\.glb'/gm)]
    .map((m) => m[1]));
  const dangling = [];
  for (const [k, list] of Object.entries(ATTIRE_VARIANTS))
    for (const a of list) if (!keys.has(a.model)) dangling.push(`${k}->${a.model}`);
  check('every ladder model has a MODEL_URLS key', dangling.length === 0,
    dangling.join('; '));
}

console.log('== tripo strip list ==');
{
  const doc = JSON.parse(read('game/data/tripo-fighters.json'));
  const ids = new Set(FULL_ROSTER.map((f) => f.id));
  const orphans = doc.ids.filter((id) => !ids.has(id));
  check('tripo-fighters.json ids all live roster ids', orphans.length === 0,
    orphans.join(','));
  const foldedLeft = Object.keys(FOLDED).filter((id) => doc.ids.includes(id));
  check('folded cards not in tripo strip', foldedLeft.length === 0,
    foldedLeft.join(','));
}

console.log('== stages ==');
{
  const src = read('game/js/stages.js');
  const ids = [...src.matchAll(/^\s*id:\s*'([^']+)'/gm)].map((m) => m[1]);
  const t3Block = src.slice(src.indexOf('const T3_RETRO = ['));
  const t3 = [...t3Block.matchAll(/^\s*\['([a-z])',\s*'/gm)].map((m) => 't3-' + m[1]);
  const nmBlock = src.slice(src.indexOf('const NO_MERCY = ['),
    src.indexOf('];', src.indexOf('const NO_MERCY = [')));
  const nm = [...nmBlock.matchAll(/^\s*\['([a-z_]+)'/gm)]
    .map((m) => 'nm-' + m[1].replace(/_/g, '-'));
  const glbBlock = src.slice(src.indexOf('const NM_ARENAS = ['),
    src.indexOf('];', src.indexOf('const NM_ARENAS = [')));
  const glb = [...glbBlock.matchAll(/^\s*\[\s*'(nm-[a-z-]+)'/gm)].map((m) => m[1]);
  const all = [...ids, ...t3, ...nm, ...glb];
  const dupes = [...new Set(all.filter((x, i) => all.indexOf(x) !== i))];
  check(`stage ids unique (${all.length} stages)`, dupes.length === 0,
    dupes.join(','));
}

console.log('== doc frank transforms preserved ==');
{
  const df = FULL_ROSTER.find((f) => f.id === 'docfrank');
  const targets = {
    'doc-frank-big': 'doc-frank-big',
    'doc-frank-wowomomo': 'doc-frank-wowomomo-big',
    'doc-frank-hood': 'doc-frank-hood-big',
    'doc-frank-frankenstein': 'doc-frank-frankenstein-big',
  };
  check('docfrank uses per-model forms', !!df.forms && !df.transform);
  for (const [model, target] of Object.entries(targets)) {
    check(`transform ${model} -> ${target}`,
      df.forms?.[model]?.target === target,
      `got ${df.forms?.[model]?.target}`);
  }
}

if (failures) { console.error(`\n${failures} check(s) FAILED`); process.exit(1); }
console.log('\nall dedup audit checks passed');
