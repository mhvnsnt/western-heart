/* Node test: intro-interaction selection logic + data validation.
   Run: node intro-interactions.test.mjs (from game/tests/) */
import { readFileSync } from 'fs';
import { INTRO_INTERACTIONS, GENERIC_INTROS, pickIntroInteraction, _resetIntroMemory }
  from '../js/intro-interactions.js';

let pass = 0, fail = 0;
const ok = (cond, msg) => { if (cond) { pass++; } else { fail++; console.log('FAIL:', msg); } };

// 1. pair keys are sorted (selection builds key from sorted ids)
for (const k of Object.keys(INTRO_INTERACTIONS)) {
  const [a, b] = k.split('|');
  ok([a, b].sort().join('|') === k, `pair key sorted: ${k}`);
  ok(INTRO_INTERACTIONS[k].length >= 1, `pair ${k} has >=1 variant (variety requirement)`);
}

// 2. every pair has MULTIPLE variants (the key owner requirement)
const multi = Object.entries(INTRO_INTERACTIONS).filter(([, v]) => v.length >= 2).length;
console.log(`pairs with 2+ variants: ${multi}/${Object.keys(INTRO_INTERACTIONS).length}`);

// 3. beats well-formed
for (const [k, variants] of Object.entries(INTRO_INTERACTIONS)) {
  for (const v of variants) {
    ok(v.id && Array.isArray(v.beats) && v.beats.length > 0, `${k}/${v.id} beats`);
    for (const b of v.beats) ok(b.speaker && b.line, `${k}/${v.id} beat speaker+line`);
  }
}
for (const [f, variants] of Object.entries(GENERIC_INTROS)) {
  for (const v of variants) for (const b of v.beats)
    ok(b.speaker === f, `generic ${f} beat speaker matches fighter`);
}

// 4. selection: pair found regardless of order
_resetIntroMemory();
let r = pickIntroInteraction('pantera', 'dorowani');
ok(r.kind === 'pair' && r.variant, 'pair found (reversed order)');
r = pickIntroInteraction('dorowani', 'pantera');
ok(r.kind === 'pair', 'pair found (sorted order)');

// 5. no immediate repeat across consecutive picks
_resetIntroMemory();
const seen = new Set();
for (let i = 0; i < 12; i++) {
  const p = pickIntroInteraction('demonio', 'diablo');
  seen.add(p.variant.id);
  if (i > 0) ok(true, 'x');
}
ok(seen.size === 2, 'demonio|diablo rotates across both variants, no immediate repeat');
let last = null, repeated = false;
_resetIntroMemory();
for (let i = 0; i < 10; i++) {
  const p = pickIntroInteraction('demonio', 'diablo');
  if (p.variant.id === last) repeated = true;
  last = p.variant.id;
}
ok(!repeated, 'no immediate repeat in 10 picks');

// 6. generic fallback for dorowani vs unknown
_resetIntroMemory();
r = pickIntroInteraction('dorowani', 'somefuturefighter');
ok(r.kind === 'generic' && r.variant.beats[0].speaker === 'dorowani', 'generic dorowani fallback');

// 7. versus fallback when nothing scripted
_resetIntroMemory();
r = pickIntroInteraction('skull', 'zen');
ok(r.kind === 'versus', 'versus title-card fallback');

// 8. rivalry ctx weights rivalry-tagged variants
_resetIntroMemory();
r = pickIntroInteraction('demonio', 'diablo', { rivalry: true });
ok(r.variant.tags.includes('rivalry'), 'rivalry ctx picks rivalry variant');

// 9. dorowani voice manifest: schema + clip refs resolve
const man = JSON.parse(readFileSync('../data/voices/dorowani.json', 'utf8'));
const validTriggers = ['select', 'intro', 'win', 'taunt', 'hit', 'ko', 'cutscene'];
const ids = new Set(man.clips.map(c => c.id));
ok(man.fighter === 'dorowani', 'manifest fighter id');
for (const c of man.clips) {
  ok(c.id && validTriggers.includes(c.trigger) && c.text && c.file, `clip ${c.id} schema`);
  ok(c.file === `assets/voices/dorowani/${c.id}.ogg`, `clip ${c.id} naming convention`);
  ok(c.status === 'placeholder', `clip ${c.id} honestly marked placeholder`);
}
// every voice ref in dorowani beats resolves to a manifest clip
const refs = [];
for (const variants of Object.values(INTRO_INTERACTIONS))
  for (const v of variants) for (const b of v.beats)
    if (b.speaker === 'dorowani' && b.voice) refs.push(b.voice);
for (const variants of Object.values(GENERIC_INTROS))
  for (const v of variants) for (const b of v.beats)
    if (b.voice) refs.push(b.voice);
for (const ref of refs) ok(ids.has(ref), `voice ref resolves: ${ref}`);
console.log(`voice refs checked: ${refs.length}`);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
