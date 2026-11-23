// Moveset template library + moveset editor (2026-11-08 lane; engine
// rebuilt 2026-11-20 per EDITOR-SPEC §3).
// Node, no browser. Run: node --test test/moveset-editor.test.mjs
// What it proves, from real files (nothing stubbed):
//  - game/data/moveset-templates/index.json is consistent with the
//    banks it points at (per-template move counts, library prefixes)
//  - the editor slot catalog is the resolver prefix list (A §3a/§3b):
//    plain resolver notations are the slot keys, the old
//    "position|situation|input" keys are migration-only, and the old
//    position words (corner/apron/mounted/...) are refused, not mapped
//  - per-slot swap works: eligible moves assign, ineligible and
//    unknown moves are refused, claimed-bank moves are refused by
//    the same source law the assembler enforces (at validate time)
//  - a custom moveset built on a fighter base (demonio default)
//    round-trips through the named-document store and compiles into
//    the live loadout via setLoadoutSlot + __base
//  - toManifest() is RETIRED for the editor path but kept exported:
//    the assembler integration tests still prove an editor-produced
//    document projects into a kit the assembler accepts
//  - Create Fighter carries the custom moveset instead of the jin
//    fallback when one is saved
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  RESOLVER_POSITIONS, SOUL_STATES, NO_RESOLVER_PATH, RETIRED_POSITION_WORDS,
  DEMONIO_FORMS, SLOT_INPUTS,
  prefixOf, positionOfNotation, validateNotation, slotKey, parseSlotKey,
  layerOfKey, isGrabMove,
  createCustomMoveset, isEligible, listEligibleMoves, assignMove, removeMove, getMove,
  toManifest, validateMoveset, serializeMoveset, deserializeMoveset,
  migrateDocSlots, compileToLoadout,
  saveNamedMoveset, loadNamedMoveset, listNamedMovesets, deleteNamedMoveset,
  getAppliedName, setAppliedName,
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

test('slot catalog: resolver positions in order, plain notations, fixed inputs', () => {
  assert.deepEqual(RESOLVER_POSITIONS.map((p) => p.id),
    ['WR', 'CD', 'SOUL', 'BT', 'STANCE', 'FUFT', 'FUFA', 'FDFT', 'FDFA', 'R', 'H', 'RD', 'SSL', 'SSR', 'SS', 'FC', 'OTG', 'WALL', 'WS', 'AIR', 'STAND'],
    'resolver positions must be in _pressV2 order (A §3a/§3b); ground stances ride the generic stance slot, so they sit with STANCE (Lane C 2026-11-20)');
  for (const p of RESOLVER_POSITIONS) {
    if (p.prefix !== null) assert.ok(p.prefix === '' || p.prefix.endsWith('.'), `${p.id}: prefix ${p.prefix} must end with '.'`);
  }
  assert.ok(RESOLVER_POSITIONS.find((p) => p.id === 'RD').synthesized, 'Rage Drive is synthesized — no data keys');
  assert.deepEqual(SOUL_STATES, ['SPIRIT', 'KESSHOU', 'SOUL9', 'REIHOU', 'SEAL']);
  assert.equal(NO_RESOLVER_PATH.length, 7, 'seven no-resolver-path prefixes left (Lane C 2026-11-20 unquarantined FUFT/FUFA/FDFT/FDFA — knockdown-exit stance window)');
  for (const pre of ['GROUNDED', 'FDFL', 'FDFR', 'FUFL', 'CH', 'TACKLE', 'REV']) assert.ok(NO_RESOLVER_PATH.includes(pre), `${pre} must be quarantined`);
  for (const pre of ['FUFT', 'FUFA', 'FDFT', 'FDFA']) assert.ok(!NO_RESOLVER_PATH.includes(pre), `${pre} must NOT be quarantined (Lane C: stance-window path)`);
  for (const w of ['corner', 'apron', 'mounted', 'jumping', 'sidestep-left', 'sidestep-right']) {
    assert.ok(RETIRED_POSITION_WORDS.includes(w), `${w} must be listed as a retired word`);
  }
  assert.deepEqual(DEMONIO_FORMS, ['demonio', 'demonio-human', 'demonio-winged', 'demonio-bloodline-ember']);

  // the slot key IS the notation now; the old '|' form is migration-only
  assert.equal(slotKey('df+2'), 'df+2');
  assert.equal(slotKey('WS.1'), 'WS.1');
  // ground orientations are assignable now (Lane C): slot key builds, validates, buckets
  assert.equal(slotKey('FUFT.3'), 'FUFT.3');
  assert.equal(validateNotation('FUFT.3'), 'FUFT.3');
  assert.equal(validateNotation('FDFA.4'), 'FDFA.4');
  assert.equal(positionOfNotation('FUFT.3').id, 'FUFT');
  assert.equal(positionOfNotation('FUFA.db+1+3_2+4').id, 'FUFA');
  assert.equal(positionOfNotation('FDFT.db+1+3_2+4').id, 'FDFT');
  assert.equal(positionOfNotation('FDFA.3').id, 'FDFA');
  assert.throws(() => slotKey('standing|neutral|df+2'), /legacy/);
  assert.throws(() => slotKey('GROUNDED.1'), /no resolver path/);
  assert.throws(() => slotKey('corner.1'), /not a data prefix/);
  assert.throws(() => slotKey('BT.3,&#58;1+2'), /corrupt/);
  assert.deepEqual(parseSlotKey('df+2'), { position: 'STAND', situation: null, input: 'df+2', legacy: false });
  assert.deepEqual(parseSlotKey('standing|neutral|d+1'), { position: 'standing', situation: 'neutral', input: 'd+1', legacy: true });
  assert.equal(prefixOf('WS.1'), 'WS');
  assert.equal(prefixOf('1'), '');
  assert.equal(positionOfNotation('WS.1').id, 'WS');
  assert.equal(positionOfNotation('BT.2').id, 'BT');
  assert.equal(positionOfNotation('FC.d/f+1').id, 'FC');
  assert.equal(positionOfNotation('SPIRIT.1').id, 'SOUL');
  assert.equal(positionOfNotation('RD.1').id, 'RD');
  assert.equal(positionOfNotation('1').id, 'STAND');
  assert.deepEqual(positionOfNotation('GROUNDED.1'), { id: 'QUARANTINE', stance: null, quarantine: true });
  assert.deepEqual(positionOfNotation('FOX.1', ['FOX']), { id: 'STANCE', stance: 'FOX', quarantine: false });
  assert.equal(positionOfNotation('AB1.1').id, 'STAND', 'throw-chain stage tags bucket under Standing');
  assert.equal(layerOfKey('x~t7.y').layer, 'T7');
  assert.equal(layerOfKey('x~t3.y').layer, 'T3');
  assert.equal(layerOfKey('x__main').layer, 'MAIN');
  assert.equal(layerOfKey('x').layer, 'BASE');
  assert.ok(isGrabMove({ isGrab: true }));
  assert.ok(isGrabMove({ move_class: 'throw' }));
  assert.ok(!isGrabMove({ move_class: 'strike' }));
  assert.ok(!isGrabMove(null));

  // SLOT_INPUTS kept verbatim from the old engine (EDITOR-SPEC §2f)
  assert.equal(SLOT_INPUTS.length, 60, 'SLOT_INPUTS must stay the 60 measured inputs');
  assert.equal(new Set(SLOT_INPUTS).size, SLOT_INPUTS.length, 'duplicate slot input');
  for (const input of SLOT_INPUTS) {
    assert.match(input, /^[dfbuqhc\/0-9+,]+$/, `input ${input} is not Tekken notation`);
    assert.ok(/[1234]/.test(input), `input ${input} names no limb button`);
  }
});

test('eligibility: input gate + position-prefix gate, input-less moves fit by position only', () => {
  const moves = [
    { input: null }, // T3 row: no decoded input — position-only fit
    { input: '1' },
    { input: 'd+1' },
  ];
  assert.ok(isEligible(moves[0], 'df+2'), 'input-less move should fit any assignable notation');
  assert.ok(isEligible(moves[0], 'WS.1'), 'input-less move fits a prefixed notation too');
  assert.ok(isEligible(moves[1], '1'), 'input 1 move fits input 1 slot');
  assert.ok(!isEligible(moves[1], '2'), 'input 1 move must not fit input 2 slot');
  assert.ok(isEligible(moves[2], 'd+1'), 'input d+1 move fits d+1 slot');
  assert.ok(!isEligible(moves[2], '1'), 'input d+1 move must not fit input 1 slot');
  assert.equal(listEligibleMoves(moves, '1').length, 2, 'input 1 should admit the input-less move + the 1 move');
  assert.equal(listEligibleMoves(moves, 'd+1').length, 2, 'input d+1 should admit the input-less move + the d+1 move');
  // position-prefix gate on the move KEY: WS key cannot fill a BT slot
  assert.ok(!isEligible({ input: 'WS.1' }, 'BT.1', 'WS.1'), 'WS move key must not fill a BT slot');
  assert.ok(isEligible({ input: 'WS.1' }, 'WS.1', 'WS.1'), 'WS move key fills its own WS slot');
  assert.ok(!isEligible({ input: 'WS.1' }, 'WS.2', 'WS.1'), 'WS.1 input must not fill WS.2');
  // quarantined notations are never eligible
  assert.ok(!isEligible(moves[0], 'GROUNDED.1'), 'quarantined notation is never eligible');
  assert.ok(!isEligible(moves[1], '1', 'GROUNDED.1'), 'quarantined move key is never eligible');
  // ground-orientation move keys fill their own slot, not a sibling orientation (Lane C)
  assert.ok(isEligible({ input: 'FUFT.3' }, 'FUFT.3', 'FUFT.3'), 'FUFT move key fills its own FUFT slot');
  assert.ok(!isEligible({ input: 'FUFT.3' }, 'FDFA.3', 'FUFT.3'), 'FUFT move key must not fill an FDFA slot');
  assert.ok(isEligible({ input: 'FDFA.4' }, 'FDFA.4', 'FDFA.4'), 'FDFA move key fills its own FDFA slot');
});

test('create + assign + validate: named doc, source law at validate, store round-trip', () => {
  // the base kit is a FIGHTER ID now, not a library template object;
  // the custom fighter defaults to demonio (suite parity, B §3a)
  const ms = createCustomMoveset({ name: 'Test Custom', fighterId: 'custom', baseTemplate: 'demonio', base: { bank: 't3', character: 'hwoarang' } });
  assert.equal(ms.schema, 'wh.custom-moveset.v1');
  assert.equal(ms.baseTemplate, 'demonio');
  assert.equal(ms.base.bank, 't3');
  assert.equal(ms.base.character, 'hwoarang');
  assert.deepEqual(ms.slots, {});
  assert.throws(() => createCustomMoveset({}), /needs a name/);
  const def = createCustomMoveset({ name: 'Default Base' });
  assert.equal(def.fighterId, 'custom');
  assert.equal(def.baseTemplate, 'demonio', 'custom fighter without a base defaults to demonio');

  const lib = new Map([
    ['t3:hwoarang:row:31', { id: 't3:hwoarang:row:31', position: 'standing', input: null, anim_ref: 't3:hwoarang:row:31' }],
    ['t3:king:row:35', { id: 't3:king:row:35', position: 'standing', input: null, anim_ref: 't3:king:row:35' }],
  ]);
  const hw = lib.get('t3:hwoarang:row:31');
  const assigned = assignMove(ms, 'df+2', 't3:hwoarang:row:31', { move: hw });
  assert.equal(getMove(assigned, 'df+2'), 't3:hwoarang:row:31');
  // a move with a decoded input that does not match the slot is refused
  assert.throws(() => assignMove(ms, 'df+2', 't3:hwoarang:row:31', { move: { input: '1' } }), /cannot fill slot/);
  assert.throws(() => assignMove(ms, 'df+2', 'bad|key'), /bad move key/);
  assert.throws(() => assignMove(ms, 'GROUNDED.1', 't3:hwoarang:row:31'), /no resolver path/);
  const removed = removeMove(assigned, 'df+2');
  assert.equal(getMove(removed, 'df+2'), null);

  // a claimed move smuggled into the slots fails validation (assembler law)
  const bad = { ...assigned, slots: { '1': 't3:king:row:35' } };
  const vBad = validateMoveset(bad, { libraryById: lib, claimed });
  assert.ok(!vBad.ok, 'claimed move in slots must fail validation');
  assert.ok(vBad.errors.some((e) => /CLAIMED/.test(e)), JSON.stringify(vBad.errors));
  const vGood = validateMoveset(assigned, { libraryById: lib, claimed });
  assert.ok(vGood.ok, JSON.stringify(vGood.errors));
  assert.ok(vGood.warnings.some((w) => /no decoded input/.test(w)), 'input-less T3 assignment must warn, not silently pass');
  // an unknown library move fails validation instead of assigning
  const vUnknown = validateMoveset({ ...assigned, slots: { '1': 't3:nope:row:1' } }, { libraryById: lib, claimed });
  assert.ok(!vUnknown.ok);
  assert.ok(vUnknown.errors.some((e) => /unknown library move/.test(e)), JSON.stringify(vUnknown.errors));

  // serialize round-trip + legacy migration on read
  assert.equal(deserializeMoveset(serializeMoveset(assigned)).baseTemplate, 'demonio');
  assert.throws(() => deserializeMoveset('{"schema":"nope"}'), /wh\.custom-moveset/);
  const migrated = migrateDocSlots({ ...assigned, slots: { 'standing|neutral|df+2': 't3:hwoarang:row:31' } });
  assert.deepEqual(migrated.doc.slots, { 'df+2': 't3:hwoarang:row:31' });
  assert.deepEqual(migrated.migrated, ['standing|neutral|df+2']);

  // named-document store + compile into the live loadout
  saveNamedMoveset(assigned);
  const listed = listNamedMovesets().find((d) => d.name === 'Test Custom');
  assert.ok(listed, 'saved doc must be listed');
  assert.equal(listed.slots, 1);
  assert.equal(loadNamedMoveset('Test Custom').baseTemplate, 'demonio');
  setAppliedName('custom', 'Test Custom');
  assert.equal(getAppliedName('custom'), 'Test Custom');
  const seen = {};
  const fakeSet = (fid, n, v) => { seen[n] = v; return true; };
  const res = compileToLoadout(loadNamedMoveset('Test Custom'), { setLoadoutSlot: fakeSet, clearNotations: ['1'] });
  assert.equal(res.cleared, 1);
  assert.equal(res.applied, 1);
  assert.equal(res.base, 'demonio');
  assert.equal(seen['df+2'], 't3:hwoarang:row:31');
  assert.equal(seen['1'], null, 'APPLY clears stale loadout entries first');
  assert.equal(seen['__base'], 'demonio');
  assert.ok(deleteNamedMoveset('Test Custom'));
  assert.equal(loadNamedMoveset('Test Custom'), null);
  assert.equal(getAppliedName('custom'), null, 'deleting the applied doc clears the pointer');
});

test('integration: custom moveset from t3-hwoarang assembles, source law green', async () => {
  const lib = await loadLibrary({ root: ROOT });
  const claimedMap = await loadClaimedMap({ root: ROOT });
  const hwMoves = lib.banks.t3.moves.filter((m) => m.id.startsWith('t3:hwoarang:'));
  // 376 entries (183 distinct T3 rows — the same row appears under
  // several move keys/inputs); the old bank carried only 221.
  assert.ok(hwMoves.length === 376, `expected 376 Hwoarang moves, got ${hwMoves.length}`);
  let ms = createCustomMoveset({ name: 'Test Custom', fighterId: 'custom', baseTemplate: 'demonio', base: { bank: 't3', character: 'hwoarang' } });
  ms = assignMove(ms, 'df+2', hwMoves[0].id, lib.byId);
  const manifest = toManifest(ms);
  assert.equal(manifest.base.bank, 't3');
  assert.equal(manifest.base.character, 'hwoarang');
  assert.equal(manifest.moves[0].slot, 'df+2');
  const kit = await assembleFighter(manifest, { root: ROOT });
  assert.ok(kit.report.source_law.passed, JSON.stringify(kit.report.source_law));
  assert.ok(kit.moves['df+2'], 'the swapped-in move must be in the assembled kit');
  /* The #615 gap is CLOSED for the library fill (2026-11-20): the new
     index carries inputs decoded from the moveset files, so the T3
     base kit now assembles like the vf5 one does — 188 distinct
     inputs from 376 Hwoarang entries (183 distinct T3 rows). The
     overlay at df+2 is a 189th slot (df+2 is not a base input).
     Asserted here so it cannot silently change. */
  assert.equal(kit.report.assembled, 189, 'T3 base kit assembles 188 distinct inputs + the df+2 overlay = 189');
});

test('integration: vf5-based custom moveset assembles its FULL base kit', async () => {
  const lib = await loadLibrary({ root: ROOT });
  const claimedMap = await loadClaimedMap({ root: ROOT });
  // vf5/doa/vf moves all carry decoded inputs (96/96, 146/146, 48/48),
  // so unlike T3 the base kit fills every input slot by itself.
  const ms = createCustomMoveset({ name: 'Test VF5', fighterId: 'custom', baseTemplate: 'demonio', base: { bank: 'vf5', character: 'el-blaze' } });
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
