// Moveset template library + moveset editor (2026-11-08 lane).
// Node, no browser. Run: node --test test/moveset-editor.test.mjs
// What it proves, from real files (nothing stubbed):
//  - game/data/moveset-templates/index.json is consistent with the
//    banks it points at (per-template move counts, library prefixes)
//  - the editor slot catalog matches the library schema's position
//    enum and the measured T7 input set
//  - per-slot swap works: eligible moves assign, ineligible and
//    unknown moves are refused, claimed-bank moves are refused by
//    the same source law the assembler enforces
//  - a custom moveset built from a FREE template (t3-hwoarang)
//    assembles through the real assembler with the source law green
//  - Create Fighter carries the custom moveset instead of the jin
//    fallback when one is saved
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  POSITIONS, SITUATIONS, SLOT_INPUTS, WWE_CATEGORIES,
  slotKey, parseSlotKey, slotsForCategory,
  canBeBaseTemplate, canUseTemplate, createCustomMoveset,
  isEligible, listEligibleMoves, assignMove, removeMove, getMove,
  toManifest, validateMoveset, serializeMoveset, deserializeMoveset,
} from '../game/js/moveset-editor.js';
import { assembleFighter, loadLibrary, loadClaimedMap } from '../game/js/moveset-library.js';
import { customFighterToRoster, customMovesetFor } from '../game/js/custom-fighter.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (rel) => JSON.parse(readFileSync(join(ROOT, rel), 'utf8'));

const templates = readJson('game/data/moveset-templates/index.json').templates;
const byId = new Map(templates.map((t) => [t.id, t]));
const claimed = readJson('game/data/moveset-library/claimed-map.json');

test('template index: unique ids, slug-form ids, WH-only attached_to', () => {
  assert.equal(new Set(templates.map((t) => t.id)).size, templates.length, 'duplicate template id');
  for (const t of templates) {
    assert.match(t.id, /^[a-z0-9-]+$/, `${t.id} is not a slug-form id`);
    assert.ok(['template', 'pool', 'frame-data-only', 'pending-ingest', 'primary', 'attached-existing', 'reserved', 'library', 'pointer'].includes(t.status), `${t.id}: unknown status ${t.status}`);
    for (const a of t.attached_to || []) assert.match(a, /^[a-z0-9-]+$/, `${t.id}: attached_to ${a} is not a WH fighter id`);
  }
  // the 2026-11-05 hand-written rows survive the regeneration
  for (const id of ['t7-grappler-jaguar-mask', 't7-mishima-style-karate', 't3-ogre-bank', 'cam-moveset-string-lib']) {
    assert.ok(byId.has(id), `hand-written template ${id} was lost`);
  }
});

test('template index: bank-backed counts match the banks, prefixes resolve', () => {
  const banks = {};
  for (const bank of ['t3', 'doa', 'vf', 'vf5', 'wrestling', 'wmxix']) {
    banks[bank] = readJson(`game/data/moveset-library/banks/${bank}.json`);
  }
  let bankTotal = 0;
  for (const t of templates.filter((x) => x.status === 'template')) {
    const bank = banks[t.source_bank];
    const mine = bank.moves.filter((m) => m.id.startsWith(t.library_prefix + ':') || m.id === t.library_prefix);
    assert.equal(mine.length, t.moves, `${t.id}: index says ${t.moves} moves, bank has ${mine.length} under ${t.library_prefix}`);
    assert.ok(mine.length > 0, `${t.id}: no moves under ${t.library_prefix}`);
    bankTotal += t.moves;
  }
  // per-character templates cover the whole per-character banks
  assert.equal(bankTotal, 4648 + 146 + 48 + 96, 'per-character templates do not cover t3+doa+vf+vf5');
  for (const t of templates.filter((x) => x.status === 'pool')) {
    assert.equal(t.moves, banks[t.source_bank].moves.length, `${t.id}: pool count mismatch`);
  }
  // frame-data-only rows carry the measured counts
  const t7 = templates.filter((x) => x.source_bank === 't7-frame-data');
  assert.equal(t7.length, 44, 'T7 frame templates should be 44');
  assert.equal(t7.reduce((n, x) => n + x.moves, 0), 6909, 'T7 frame moves should total 6909');
  const t8 = templates.filter((x) => x.source_bank === 't8-frame-tables');
  assert.equal(t8.length, 41, 'T8 frame templates should be 41');
  assert.equal(t8.reduce((n, x) => n + x.moves, 0), 6411, 'T8 frame moves should total 6411');
});

test('slot catalog: positions match the library schema, inputs are Tekken notation', () => {
  const schema = readJson('game/data/moveset-library/schema.json');
  assert.deepEqual(POSITIONS, schema.properties.position.enum);
  assert.ok(SITUATIONS.length >= 8, 'too few situations');
  for (const input of SLOT_INPUTS) {
    assert.match(input, /^[dfbuqhc\/0-9+,]+$/, `input ${input} is not Tekken notation`);
    assert.ok(/[1234]/.test(input), `input ${input} names no limb button`);
  }
  assert.equal(new Set(SLOT_INPUTS).size, SLOT_INPUTS.length, 'duplicate slot input');
  for (const cat of WWE_CATEGORIES) {
    for (const p of cat.positions) assert.ok(POSITIONS.includes(p), `${cat.id}: unknown position ${p}`);
    for (const s of cat.situations) assert.ok(SITUATIONS.includes(s), `${cat.id}: unknown situation ${s}`);
    assert.ok(slotsForCategory(cat.id).length > 0, `${cat.id}: no slots`);
  }
  assert.equal(slotKey('standing', 'neutral', 'df+2'), 'standing|neutral|df+2');
  assert.deepEqual(parseSlotKey('grounded|neutral|d+1'), { position: 'grounded', situation: 'neutral', input: 'd+1' });
  assert.throws(() => slotKey('standing', 'neutral', 'LP'), /unknown input/);
  assert.throws(() => slotKey('ring', 'neutral', '1'), /unknown position/);
});

test('eligibility: position + input gate, input-less moves fit by position only', () => {
  const moves = [
    { id: 't3:hwoarang:row:31', position: 'standing', input: null },
    { id: 'doa:bass:1', position: 'standing', input: '1' },
    { id: 'doa:bass:3', position: 'crouching', input: 'd+1' },
  ];
  assert.ok(isEligible(moves[0], 'standing|neutral|df+2'), 'input-less standing move should fit any standing input slot');
  assert.ok(!isEligible(moves[0], 'crouching|neutral|df+2'), 'standing move must not fit a crouching slot');
  assert.ok(isEligible(moves[1], 'standing|neutral|1'), 'input 1 move fits input 1 slot');
  assert.ok(!isEligible(moves[1], 'standing|neutral|2'), 'input 1 move must not fit input 2 slot');
  assert.equal(listEligibleMoves(moves, 'standing|neutral|1').length, 2, 'standing|neutral|1 should admit the input-less move + the 1 move');
  assert.equal(listEligibleMoves(moves, 'crouching|neutral|d+1').length, 1);
});

test('create + assign + validate: free template works, claimed template refused', () => {
  // t3-hwoarang is FREE (claimed map free list) — any fighter may base on it
  const use = canUseTemplate(byId.get('t3-hwoarang'), 'custom', claimed);
  assert.ok(use.allowed, use.reason);
  // t3-king is CLAIMED by Pantera — a custom fighter may not base on it
  const no = canUseTemplate(byId.get('t3-king'), 'custom', claimed);
  assert.ok(!no.allowed, 'claimed template must be refused for a custom fighter');
  assert.match(no.reason, /CLAIMED/);
  assert.ok(canUseTemplate(byId.get('t3-king'), 'pantera', claimed).allowed, 'the claimant may still use its own template');
  // frame-data-only and pending rows cannot be a base (no playable moves)
  assert.ok(!canBeBaseTemplate(byId.get('t7-frame-king')), 'frame-data-only must not be a base');
  assert.ok(!canBeBaseTemplate(byId.get('urban-reign-pending')), 'pending-ingest must not be a base');
  assert.throws(() => createCustomMoveset({ templateId: 't3-king', fighterId: 'custom', templates, claimed }), /CLAIMED/);

  const ms = createCustomMoveset({ templateId: 't3-hwoarang', fighterId: 'custom', name: 'Test Custom', templates, claimed });
  assert.equal(ms.base.bank, 't3');
  assert.equal(ms.base.character, 'hwoarang');
  const lib = new Map([
    ['t3:hwoarang:row:31', { id: 't3:hwoarang:row:31', position: 'standing', input: null, anim_ref: 't3:hwoarang:row:31' }],
    ['t3:king:row:35', { id: 't3:king:row:35', position: 'standing', input: null, anim_ref: 't3:king:row:35' }],
  ]);
  const assigned = assignMove(ms, 'standing|neutral|df+2', 't3:hwoarang:row:31', lib);
  assert.equal(getMove(assigned, 'standing|neutral|df+2'), 't3:hwoarang:row:31');
  assert.throws(() => assignMove(ms, 'crouching|neutral|df+2', 't3:hwoarang:row:31', lib), /cannot fill slot/);
  assert.throws(() => assignMove(ms, 'standing|neutral|1', 't3:nope:row:1', lib), /unknown library move/);
  const removed = removeMove(assigned, 'standing|neutral|df+2');
  assert.equal(getMove(removed, 'standing|neutral|df+2'), null);

  // a claimed move smuggled into the slots fails validation (assembler law)
  const bad = { ...assigned, slots: { 'standing|neutral|1': 't3:king:row:35' } };
  const vBad = validateMoveset(bad, { libraryById: lib, claimed });
  assert.ok(!vBad.ok, 'claimed move in slots must fail validation');
  assert.ok(vBad.errors.some((e) => /CLAIMED/.test(e)), JSON.stringify(vBad.errors));
  const vGood = validateMoveset(assigned, { libraryById: lib, claimed });
  assert.ok(vGood.ok, JSON.stringify(vGood.errors));
  assert.ok(vGood.warnings.some((w) => /no decoded input/.test(w)), 'input-less T3 assignment must warn, not silently pass');

  // serialize round-trip
  assert.equal(deserializeMoveset(serializeMoveset(assigned)).baseTemplate, 't3-hwoarang');
  assert.throws(() => deserializeMoveset('{"schema":"nope"}'), /wh\.custom-moveset/);
});

test('integration: custom moveset from t3-hwoarang assembles, source law green', async () => {
  const lib = await loadLibrary({ root: ROOT });
  const claimedMap = await loadClaimedMap({ root: ROOT });
  const hwMoves = lib.banks.t3.moves.filter((m) => m.id.startsWith('t3:hwoarang:'));
  assert.ok(hwMoves.length === 221, `expected 221 Hwoarang moves, got ${hwMoves.length}`);
  let ms = createCustomMoveset({ templateId: 't3-hwoarang', fighterId: 'custom', name: 'Test Custom', templates, claimed: claimedMap });
  ms = assignMove(ms, 'standing|neutral|df+2', hwMoves[0].id, lib.byId);
  const manifest = toManifest(ms);
  assert.equal(manifest.base.bank, 't3');
  assert.equal(manifest.base.character, 'hwoarang');
  assert.equal(manifest.moves[0].slot, 'standing|neutral|df+2');
  const kit = await assembleFighter(manifest, { root: ROOT });
  assert.ok(kit.report.source_law.passed, JSON.stringify(kit.report.source_law));
  assert.ok(kit.moves['standing|neutral|df+2'], 'the swapped-in move must be in the assembled kit');
  /* HONEST LIMIT, measured: T3 rows carry input null (0/4,648 have
     an input — the #615 fidelity engine owns that decode), so the
     assembler's base-kit loop (`if (m.input ...)`) adds nothing
     from a T3 base. A T3-based custom moveset today assembles to
     exactly its explicitly-assigned overlay moves. That is the
     #615 gap, asserted here so it cannot silently change. */
  assert.equal(kit.report.assembled, 1, 'T3 base kit contributes nothing until inputs are decoded — only the overlay move assembles');
});

test('integration: vf5-based custom moveset assembles its FULL base kit', async () => {
  const lib = await loadLibrary({ root: ROOT });
  const claimedMap = await loadClaimedMap({ root: ROOT });
  // vf5/doa/vf moves all carry decoded inputs (96/96, 146/146, 48/48),
  // so unlike T3 the base kit fills every input slot by itself.
  const ms = createCustomMoveset({ templateId: 'vf5-el-blaze-vf', fighterId: 'custom', name: 'Test VF5', templates, claimed: claimedMap });
  const kit = await assembleFighter(toManifest(ms), { root: ROOT });
  assert.ok(kit.report.source_law.passed, JSON.stringify(kit.report.source_law));
  assert.ok(kit.report.assembled >= 20, `vf5 base kit should assemble most of its 28 moves, got ${kit.report.assembled}`);
  assert.ok(kit.moves['1'], 'base kit move on input 1 must be present');
});

test('custom fighter carries its custom moveset instead of the jin fallback', () => {
  const save = {
    profile: { name: 'Test', alias: 'Tester' },
    body: { body_type: 'Medium 1', skin_tone: '#c98d5e' },
    moveset_custom: {
      schema: 'wh.custom-moveset.v1', fighterId: 'custom', name: 'Test Custom',
      baseTemplate: 't3-hwoarang', base: { bank: 't3', character: 'hwoarang' },
      slots: { 'standing|neutral|df+2': 't3:hwoarang:row:31' }, created: '2026-11-08',
    },
  };
  assert.deepEqual(customMovesetFor(save), save.moveset_custom);
  const roster = customFighterToRoster(save);
  assert.equal(roster.moveset, 'custom:t3-hwoarang');
  assert.equal(roster.customMoveset.baseTemplate, 't3-hwoarang');
  assert.equal(roster.movesetFallback, 'jin');
  const plain = { profile: { name: 'Plain', alias: '' }, body: { body_type: 'Medium 1' } };
  assert.equal(customMovesetFor(plain), null);
  assert.equal(customFighterToRoster(plain).moveset, 'jin', 'no custom moveset keeps the named jin fallback');
});
