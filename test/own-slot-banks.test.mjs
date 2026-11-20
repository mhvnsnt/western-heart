// Own-slot banks (2026-11-07): a fighter's OWN character's bank laid over its bound bank slot by slot
// (fighter.js layerOwnSlots). Candidates are registered banks; none is active until its clips pass by eye
// (docs/proof/2026-11-07/bank-audit/README.md). Run: node --test test/own-slot-banks.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));

test('every own-slot candidate is a registered bank', () => {
  for (const [id, bank] of Object.entries(F.OWN_SLOT_CANDIDATES)) {
    assert.ok(T.T3_BANKS[bank], `${id}: ${bank} registered in T3_BANKS`);
    assert.equal(F.ownSlotBankFor(id, { candidates: true }), bank);
  }
});

test('active own-slot banks are candidates that were judged by eye; inactive fighters are untouched', () => {
  for (const [id, bank] of Object.entries(F.OWN_SLOT_BANKS)) {
    assert.equal(F.OWN_SLOT_CANDIDATES[id], bank, `${id}: an active own-slot bank must come from the candidate list`);
  }
  for (const id of Object.keys(F.OWN_SLOT_CANDIDATES)) {
    if (F.OWN_SLOT_BANKS[id]) continue;
    assert.equal(F.ownSlotBankFor(id), null, `${id} is not active`);
    const clips = { stance: 'bound-bank-stance' };
    assert.equal(F.layerOwnSlots(id, clips, null, null), clips, 'no-op for an inactive fighter');
    assert.equal(clips.stance, 'bound-bank-stance');
  }
});
