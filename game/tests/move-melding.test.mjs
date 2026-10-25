/* move-melding.test.mjs — WH procedural grapple combinations (2026-10-23).
 *
 * Covers the pure logic in game/js/ai/move-melding.js (MeldEngine,
 * grip-continuity gate, hybrid generation) and its advisory integration
 * in game/js/ai/grapple-chains.js (THROW state -> 'chain-meld' intent).
 * All randomness is injected, so every test is deterministic.
 * No THREE, no DOM.
 *
 * Run: node --test game/tests/move-melding.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const mm = await import(join(here, '..', 'js', 'ai', 'move-melding.js'));
const gc = await import(join(here, '..', 'js', 'ai', 'grapple-chains.js'));

const ZERO = () => 0;       // every roll succeeds
const ONE = () => 0.99999;  // every roll fails

test('library loads: 10 moves, phases validated', () => {
  const eng = new mm.MeldEngine();
  assert.equal(eng.moves.size, 10);
  const h = eng.getMove('hurricanrana');
  assert.ok(h);
  assert.deepEqual(h.phases, undefined); // phases live on the engine, not the def
  assert.equal(h.grips.payload.attacker[0], 'leg-hook');
  assert.equal(eng.getMove('nope'), null);
});

test('defineMove validates shape', () => {
  assert.throws(() => mm.defineMove({ name: 'x' }), /missing 'id'/);
  assert.throws(() => mm.defineMove({
    id: 'bad', name: 'Bad', duration: 1, damage: 1,
    grips: {
      entry: { attacker: ['nope-grip'], victim: ['none'] },
      contact: { attacker: ['none'], victim: ['none'] },
      payload: { attacker: ['none'], victim: ['none'] },
      release: { attacker: ['none'], victim: ['none'] },
    },
  }), /unknown grip/);
});

test('findMelds: hurricanrana@payload offers piledriver + powerbomb (chains)', () => {
  const eng = new mm.MeldEngine();
  const cands = eng.findMelds('hurricanrana', 'payload');
  assert.equal(cands.length, 2);
  assert.equal(cands[0].to, 'piledriver');
  assert.equal(cands[0].kind, 'chain');
  assert.equal(cands[1].to, 'powerbomb');
  for (const c of cands) {
    assert.ok(isFinite(c.cost) && c.cost >= 0 && c.cost <= 1, `cost ${c.cost}`);
    assert.ok(c.hybrid && c.hybrid.id.includes('hurricanrana'));
  }
});

test('findMelds: empty when no window / unknown move / roles mismatch', () => {
  const eng = new mm.MeldEngine();
  assert.deepEqual(eng.findMelds('hurricanrana', 'entry'), []);
  assert.deepEqual(eng.findMelds('powerbomb', 'payload'), []); // no windows declared
  assert.deepEqual(eng.findMelds('nope', 'payload'), []);
  assert.deepEqual(eng.findMelds('hurricanrana', 'payload', { rolesOk: false }), []);
});

test('blendCost: victim teleport is rejected (Infinity)', () => {
  const eng = new mm.MeldEngine();
  eng.addMove({
    id: 'teleport-test', name: 'Teleport Test', duration: 1, damage: 1,
    grips: {
      // entry demands a victim state no hurricanrana payload can satisfy
      entry: { attacker: ['none'], victim: ['ground-back'] },
      contact: { attacker: ['none'], victim: ['ground-back'] },
      payload: { attacker: ['none'], victim: ['ground-back'] },
      release: { attacker: ['none'], victim: ['ground-back'] },
    },
  });
  const h = eng.getMove('hurricanrana');
  const t = eng.getMove('teleport-test');
  assert.equal(mm.blendCost(h, 'payload', t), Infinity);
  // ...while the canonical meld has a finite cost
  const p = eng.getMove('piledriver');
  const cost = mm.blendCost(h, 'payload', p);
  assert.ok(isFinite(cost) && cost < 1, `canonical cost ${cost}`);
});

test('meld: hybrid concatenates phases, blends damage, caches', () => {
  const eng = new mm.MeldEngine();
  const hy = eng.meld('hurricanrana', 'piledriver', { fromPhase: 'payload' });
  assert.equal(hy.name, 'Hurricane Piledriver');
  assert.deepEqual(hy.phases, ['entry', 'contact', 'payload', 'contact', 'payload', 'release']);
  assert.equal(hy.damage, Math.round(22 * 0.4 + 30));
  assert.deepEqual(hy.roles, { attacker: 'attacker', victim: 'victim' });
  assert.deepEqual(hy.endState, eng.getMove('piledriver').endState);
  assert.equal(eng.meld('hurricanrana', 'piledriver', { fromPhase: 'payload' }), hy, 'cached');
  assert.throws(() => eng.meld('hurricanrana', 'nope'), /unknown move/);
});

test('counter meld flips the roles', () => {
  const eng = new mm.MeldEngine();
  const counters = eng.findCounters('hurricanrana', 'contact');
  assert.equal(counters.length, 1);
  assert.equal(counters[0].to, 'ace-crusher');
  assert.equal(counters[0].counterBy, 'victim');
  assert.deepEqual(counters[0].hybrid.roles, { attacker: 'victim', victim: 'attacker' });
  assert.equal(counters[0].hybrid.counterOf, 'hurricanrana');
});

test('phaseAtProgress maps the throw timeline', () => {
  assert.equal(mm.phaseAtProgress(0), 'entry');
  assert.equal(mm.phaseAtProgress(0.24), 'entry');
  assert.equal(mm.phaseAtProgress(0.3), 'contact');
  assert.equal(mm.phaseAtProgress(0.6), 'payload');
  assert.equal(mm.phaseAtProgress(0.9), 'release');
});

test('grapple chain: no engine -> mid-throw intent stays null (backwards compat)', () => {
  const chain = new gc.GrappleChain(null, {});
  chain.fsm.changeTo(gc.GRAPPLE_STATES.THROW);
  const intent = chain.think({ myState: 'throwing', throwMove: 'hurricanrana', throwProgress: 0.6 }, ZERO);
  assert.equal(intent, null);
  assert.equal(chain.meld, null);
});

test('grapple chain: THROW + open window -> chain-meld intent with the hybrid', () => {
  const eng = new mm.MeldEngine();
  const chain = new gc.GrappleChain(null, { meldBias: 1 });
  chain.attachMeldEngine(eng);
  chain.fsm.changeTo(gc.GRAPPLE_STATES.THROW);
  // entry phase: hurricanrana declares no window here -> hold
  let intent = chain.think({ myState: 'throwing', throwMove: 'hurricanrana', throwProgress: 0.1 }, ZERO);
  assert.equal(intent, null);
  // payload phase: window opens -> meld fires exactly once
  intent = chain.think({ myState: 'throwing', throwMove: 'hurricanrana', throwProgress: 0.6 }, ZERO);
  assert.equal(intent, 'chain-meld');
  assert.ok(chain.meld);
  assert.equal(chain.meld.from, 'hurricanrana');
  assert.equal(chain.meld.to, 'piledriver');
  assert.equal(chain.meld.hybrid.name, 'Hurricane Piledriver');
  assert.equal(chain.meld.kind, 'chain');
  // same phase again: no double-fire (phase boundary already consumed)
  intent = chain.think({ myState: 'throwing', throwMove: 'hurricanrana', throwProgress: 0.65 }, ZERO);
  assert.equal(intent, null);
});

test('grapple chain: meldBias 0 never melds; unknown throwMove is safe', () => {
  const eng = new mm.MeldEngine();
  const chain = new gc.GrappleChain(null, { meldBias: 0 });
  chain.attachMeldEngine(eng);
  chain.fsm.changeTo(gc.GRAPPLE_STATES.THROW);
  const intent = chain.think({ myState: 'throwing', throwMove: 'hurricanrana', throwProgress: 0.6 }, ZERO);
  assert.equal(intent, null, 'roll(0) always fails');
  const intent2 = chain.think({ myState: 'throwing', throwMove: 'nope', throwProgress: 0.6 }, ZERO);
  assert.equal(intent2, null, 'unknown move -> no candidates -> hold');
});

test('GRAPPLE_INTENTS carries CHAIN_MELD', () => {
  assert.equal(gc.GRAPPLE_INTENTS.CHAIN_MELD, 'chain-meld');
});
