// test-bridge.mjs -- node tests for the netcode bridge layer.
// Run: node --test game/netplay/bridge/test-bridge.mjs   (from repo root)
import test from 'node:test';
import assert from 'node:assert/strict';
import { encodeInput, decodeInput, inputWordToSimBits, NET } from './input-codec.js';
import { checksumFields, WhNetSim, runReferenceSelfTest } from './sim-adapter.js';
import { FIELDS, INPUT, initFighterState, fighterSimulate } from '../sim/fighter-sim.js';

test('input codec: directions + limbs round-trip', () => {
  const w = encodeInput({ axisX: -1, up: false, down: false, block: true, pressed: ['1', '4'] });
  assert.ok(w & NET.LEFT);
  assert.ok(w & NET.BLOCK);
  assert.ok(w & NET.LP);
  assert.ok(w & NET.RK);
  const d = decodeInput(w);
  assert.equal(d.left, true);
  assert.equal(d.right, false);
  assert.equal(d.lp, true);
  assert.equal(d.rk, true);
  assert.equal(d.block, true);
  assert.equal(d.surge, false);
});

test('input codec: Tekken chord specials ride as limb pairs', () => {
  const w = encodeInput({ axisX: 0, pressed: ['1+2'] });
  assert.ok(w & NET.LP, '1+2 sets LP');
  assert.ok(w & NET.RP, '1+2 sets RP');
  const w2 = encodeInput({ axisX: 0.9, pressed: ['grab', 'ss-up'] });
  assert.ok(w2 & NET.RIGHT);
  assert.ok(w2 & NET.GRAB);
  assert.ok(w2 & NET.SS_UP);
  const d2 = decodeInput(w2);
  assert.equal(d2.grab, true);
  assert.equal(d2.ssUp, true);
});

test('input codec: dead-zone on axisX', () => {
  const w = encodeInput({ axisX: 0.1, pressed: [] });
  assert.equal(w & (NET.LEFT | NET.RIGHT), 0);
});

test('input codec: WH word -> reference sim bits', () => {
  const w = encodeInput({ axisX: 1, up: true, pressed: ['1'] });
  const s = inputWordToSimBits(w);
  assert.ok(s & INPUT.RIGHT);
  assert.ok(s & INPUT.UP);
  assert.ok(s & INPUT.LP);
  const wb = encodeInput({ axisX: 0, block: true, pressed: [] });
  assert.ok(inputWordToSimBits(wb) & INPUT.BLOCK);
});

test('checksumFields: stable and sensitive', () => {
  const a = new Int32Array([1, 2, 3]);
  const b = new Int32Array([1, 2, 3]);
  const c = new Int32Array([1, 2, 4]);
  assert.equal(checksumFields([a]), checksumFields([b]));
  assert.notEqual(checksumFields([a]), checksumFields([c]));
  assert.equal(typeof checksumFields([a]), 'number');
});

test('WhNetSim: snapshot/restore round-trips state', () => {
  const fields = {};
  for (const [name, spec] of Object.entries(FIELDS)) fields[name] = new spec.type(spec.length);
  initFighterState(fields);
  const order = Object.keys(FIELDS);
  const sim = new WhNetSim({
    simulate: fighterSimulate,
    fieldArrays: () => order.map((k) => fields[k]),
  }).bindNamed(fields);
  const before = sim.checksum();
  sim.tick(new Uint32Array([INPUT.RIGHT, INPUT.LEFT]), 0);
  const after = sim.checksum();
  assert.notEqual(before, after, 'tick should change state');
  const snap = sim.snapshot();
  sim.tick(new Uint32Array([INPUT.LP, INPUT.HP]), 1);
  assert.notEqual(sim.checksum(), after);
  sim.restore(snap);
  assert.equal(sim.checksum(), after, 'restore should return to snapshot');
});

test('WhNetSim: adapter self-test on the reference sim (600 frames)', async () => {
  const report = await runReferenceSelfTest(600);
  assert.equal(report.ok, true, `determinism self-test failed: ${report.mismatches} mismatches`);
  assert.equal(report.frames, 600);
  console.log(`    reference sim self-test: ${report.frames} frames, final checksum 0x${report.finalChecksum.toString(16)}`);
});
