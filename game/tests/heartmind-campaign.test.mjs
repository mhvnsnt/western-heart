/* heartmind-campaign.test.mjs — Lane 6 campaign layer tests.
 *
 * Covers game/js/heartmind-campaign.js (roads, party switching,
 * stage journal, ragdoll gate) and game/js/customization-t56.js
 * (T5/T6 slot taxonomy + validation), plus the stage-key match
 * against game/js/heartmind.js and the story-engine adapter
 * contract in both states of the world:
 *  - PR #1044 merged (yarn-parse.js / ink-loader.js / vendored
 *    ink.mjs present): the Yarn + Ink story files run end to end.
 *  - PR #1044 still open (engines absent): the adapter returns
 *    null instead of throwing, and callers keep the built-in
 *    heartmind.js beats.
 *
 * Run: node --test game/tests/heartmind-campaign.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  HM_STAGE_KEYS, HM_ROADS, roadInto, roadOutOf,
  createPartyState, switchPartyFighter, recordPartyStageClear, partyJournal,
  HM_RAGDOLL_CONTEXTS, ragdollAllowed, loadYarnDialogue, loadInkDialogue,
} from '../js/heartmind-campaign.js';
import { T56_SLOTS, slotById, validateCustomization } from '../js/customization-t56.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('roads join the five inner stages in descent order', () => {
  assert.deepStrictEqual(HM_STAGE_KEYS, ['threshold', 'masks', 'drowning', 'furnace', 'stillpoint']);
  assert.strictEqual(HM_ROADS.length, 4);
  for (let i = 0; i < HM_ROADS.length; i++) {
    assert.strictEqual(HM_ROADS[i].from, HM_STAGE_KEYS[i]);
    assert.strictEqual(HM_ROADS[i].to, HM_STAGE_KEYS[i + 1]);
    assert.ok(HM_ROADS[i].walk && HM_ROADS[i].canon);
  }
  assert.strictEqual(roadInto('threshold'), null);
  assert.strictEqual(roadOutOf('stillpoint'), null);
});

test('campaign stage keys match HEARTMIND_STAGES in heartmind.js', () => {
  const text = fs.readFileSync(join(ROOT, 'game', 'js', 'heartmind.js'), 'utf8');
  const block = text.slice(text.indexOf('HEARTMIND_STAGES = ['), text.indexOf('];', text.indexOf('HEARTMIND_STAGES = [')));
  const keys = [...block.matchAll(/key:\s*'(\w+)'/g)].map((m) => m[1]);
  assert.deepStrictEqual(keys, HM_STAGE_KEYS);
});

test('party switching keeps per-member progress; journal is idempotent', () => {
  const p = createPartyState(['demonio', 'thor', 'demonio']);
  assert.deepStrictEqual(p.members, ['demonio', 'thor']);
  assert.strictEqual(switchPartyFighter(p, 'thor').ok, true);
  assert.strictEqual(switchPartyFighter(p, 'nope').ok, false);
  assert.strictEqual(recordPartyStageClear(p, 'thor', 'masks'), true);
  recordPartyStageClear(p, 'thor', 'masks');
  assert.deepStrictEqual(partyJournal(p), [{ fighter: 'thor', stage: 'masks' }]);
});

test('ragdoll gate: listed contexts in adventure modes only', () => {
  assert.strictEqual(HM_RAGDOLL_CONTEXTS.length, 4);
  for (const id of ['launch', 'ko', 'wall-splat', 'floor-drop']) {
    assert.strictEqual(ragdollAllowed(id, 'heartmind'), true);
    assert.strictEqual(ragdollAllowed(id, 'versus'), false);
  }
  assert.strictEqual(ragdollAllowed('always', 'heartmind'), false);
});

test('T5/T6 slot taxonomy + validation', () => {
  assert.ok(T56_SLOTS.length >= 20);
  assert.strictEqual(slotById('head').era, 't5');
  assert.strictEqual(slotById('hairstyle').era, 't6');
  assert.strictEqual(slotById('aura').era, 't6'); // T6 PSP decrypted EBOOT item tables
  assert.strictEqual(slotById('effects').era, 't6');
  assert.strictEqual(slotById('hair-back').era, 't6');
  assert.strictEqual(slotById('hair-front').era, 't6');
  assert.strictEqual(slotById('eyes').canon, 'CANON-ANCHORED');
  assert.strictEqual(validateCustomization({ head: {}, face: {} }).ok, true);
  assert.strictEqual(validateCustomization({ 'full-head': {}, head: {} }).conflicts.length, 1);
  assert.deepStrictEqual(validateCustomization({ 'not-a-slot': {} }).unknown, ['not-a-slot']);
});

test('yarn story: Trial path, or null fallback when PR #1044 is unmerged', async () => {
  const yarnPath = join(ROOT, 'game', 'story', 'heartmind-trial.yarn');
  const enginePath = join(ROOT, 'game', 'js', 'yarn-parse.js');
  if (!fs.existsSync(enginePath) || !fs.existsSync(yarnPath)) {
    assert.strictEqual(await loadYarnDialogue('title: Start\n---\nHi\n', 'Start'), null);
    return;
  }
  const yarn = await loadYarnDialogue(fs.readFileSync(yarnPath, 'utf8'), 'Start');
  assert.ok(yarn && yarn.kind === 'yarn');
  const r = yarn.runner;
  const lines = [];
  let guard = 0;
  while (guard++ < 50) {
    const step = r.next();
    if (step.type === 'end') break;
    if (step.type === 'line') { lines.push(step.text); continue; }
    if (step.type === 'choices') {
      const pick = step.choices.findIndex((c) => c.target === 'TrialGate');
      r.choose(pick >= 0 ? pick : 0);
      continue;
    }
    break;
  }
  assert.ok(lines.some((l) => l.includes('Souls gathered: 3')));
  assert.strictEqual(r.vars.souls, 3);
  assert.strictEqual(r.vars.trial_done, true);
});

test('ink story: Trial path, or null fallback when PR #1044 is unmerged', async () => {
  const jsonPath = join(ROOT, 'game', 'story', 'heartmind-trial.ink.json');
  const enginePath = join(ROOT, 'game', 'js', 'ink-loader.js');
  const vendorPath = join(ROOT, 'game', 'vendor', 'inkjs', 'ink.mjs');
  if (!fs.existsSync(enginePath) || !fs.existsSync(vendorPath) || !fs.existsSync(jsonPath)) {
    assert.strictEqual(await loadInkDialogue('{}'), null);
    return;
  }
  const ink = await loadInkDialogue(fs.readFileSync(jsonPath, 'utf8'));
  assert.ok(ink && ink.kind === 'ink');
  const out = ink.run((choices) => {
    const ti = choices.findIndex((c) => c.text.includes('Trial gate'));
    return ti >= 0 ? ti : 0;
  });
  assert.ok(out.lines.some((l) => l.includes('Souls gathered: 3')));
  assert.strictEqual(out.vars.souls, 3);
  assert.strictEqual(out.vars.trial_done, true);
});
