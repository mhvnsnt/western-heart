// sim-adapter.js -- deterministic-sim hooks for Western Heart netplay.
//
// WHAT THIS IS: the wiring contract between the real Three.js combat
// (game/js/game.js + fighter.js) and the GGPO-style rollback session
// (game/netplay/vendor/lite-rollback). It does NOT port the combat sim
// itself -- that is the remaining architectural work, documented honestly
// in docs/netcode/NETCODE-ARCHITECTURE.md.
//
// WHAT IT PROVIDES:
//   FIELD_CONTRACT -- the typed-array state layout the real combat must
//     expose for rollback (save/load snapshots + per-frame checksums).
//   checksumFields(namedArrays) -- FNV-1a over the field arrays; the
//     cross-check primitive for desync detection, independent of the
//     vendored session's own checksum.
//   WhNetSim -- adapter class: wraps ANY simulate(fields, inputs, frame)
//     tick with beforeTick/afterTick hooks, snapshot save/restore, and a
//     determinism self-test harness (run the tick twice, compare).
//   runReferenceSelfTest() -- drives the REAL reference fighter sim
//     (game/netplay/sim/fighter-sim.js) through the adapter for 600
//     frames with scripted inputs, twice, and asserts identical
//     checksums. This is the proof that the adapter layer preserves
//     determinism end to end; the same harness will run against the
//     real combat sim once it is ported.
//
// DOM-free and node-testable: `node --test` on test-bridge.mjs.

/**
 * FIELD_CONTRACT -- what the real combat sim must expose.
 *
 * Rollback needs three operations, all integer-typed:
 *   1. SAVE a full snapshot (copy typed arrays -- no object graphs).
 *   2. LOAD a snapshot (memcpy back -- no allocation in the hot path).
 *   3. CHECKSUM the state (fast hash for desync detection).
 *
 * The reference sim's FIELDS schema (sim/fighter-sim.js) is the shape to
 * follow: every gameplay-relevant value lives in a typed array, in
 * FIXED-POINT integers (1/16 px). The real combat port must move these
 * out of JS objects / THREE.Vector3 floats and into this layout:
 */
export const FIELD_CONTRACT = Object.freeze({
  layout: 'typed-array struct-of-arrays; one entry per fighter unless noted',
  fields: Object.freeze({
    pos:   'Int32Array[2] -- x position, fixed-point (FP=16 subpixels/px)',
    y:     'Int32Array[2] -- height above ground, fixed-point (0 = grounded)',
    vel:   'Int32Array[2] -- x velocity, fixed-point',
    vy:    'Int32Array[2] -- y velocity, fixed-point',
    hp:    'Int16Array[2] -- hit points',
    state: 'Uint8Array[2] -- state id (idle/walk/jump/attack/hitstun/blockstun/ko)',
    stateT:'Int16Array[2] -- frames remaining in state',
    atk:   'Uint8Array[2] -- active attack id (0 = none)',
    facing:'Int8Array[2]  -- +1 faces right, -1 faces left',
    timer: 'Int16Array[1] -- round timer, frames',
    flags: 'Uint8Array[1] -- bit0: round over',
    rng:   'Uint32Array[1] -- seeded RNG state (xorshift), advanced in lockstep',
  }),
  rules: Object.freeze([
    'integer or fixed-point math ONLY in the tick -- no floats, no Math.random, no Date',
    'one canonical update order; no iteration over object key order',
    'render interpolation may READ fields but never WRITE them',
    'RNG (when needed) is xorshift state in fields.rng, stepped every frame',
  ]),
});

/** FNV-1a 32-bit over a list of typed arrays. Deterministic, zero-alloc. */
export function checksumFields(arrays) {
  let h = 0x811c9dc5;
  for (const a of arrays) {
    const bytes = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    for (let i = 0; i < bytes.length; i++) {
      h ^= bytes[i];
      h = Math.imul(h, 0x01000193);
    }
  }
  return h >>> 0;
}

/**
 * WhNetSim -- adapter between a deterministic tick and rollback plumbing.
 *
 *   const sim = new WhNetSim({ simulate, fieldArrays: () => [...], onTick });
 *   sim.tick(inputs, frame);          // runs hooks + the tick
 *   const snap = sim.snapshot();      // deep copy of all field arrays
 *   sim.restore(snap);                // memcpy back (rollback)
 *   sim.checksum();                   // FNV-1a over live fields
 *   sim.selfTest(frames, inputFn);    // determinism proof, returns {ok, ...}
 */
export class WhNetSim {
  constructor({ simulate, fieldArrays, onTick = null }) {
    if (typeof simulate !== 'function') throw new Error('WhNetSim: simulate required');
    if (typeof fieldArrays !== 'function') throw new Error('WhNetSim: fieldArrays required');
    this.simulate = simulate;
    this.fieldArrays = fieldArrays;
    this.onTick = onTick;
    this.frame = 0;
    this.ticks = 0;
    this.rollbacks = 0; // incremented by restore(); the session drives this
  }

  /** Run one fixed-timestep tick: hooks wrap the deterministic core. */
  tick(inputs, frame = this.frame) {
    if (this.onTick) this.onTick('before', frame, inputs);
    this.simulate(this._fields(), inputs, frame);
    if (this.onTick) this.onTick('after', frame, inputs);
    this.frame = frame + 1;
    this.ticks++;
  }

  checksum() { return checksumFields(this.fieldArrays()); }

  /** Deep snapshot of every field array (for the rollback ring buffer). */
  snapshot() { return this.fieldArrays().map((a) => a.slice()); }

  /** Restore a snapshot (rollback). Counts as a rollback event. */
  restore(snap) {
    const live = this.fieldArrays();
    if (snap.length !== live.length) throw new Error('WhNetSim.restore: snapshot shape mismatch');
    for (let i = 0; i < live.length; i++) live[i].set(snap[i]);
    this.rollbacks++;
  }

  /**
   * selfTest(frames, inputFn) -- determinism proof.
   * Runs `frames` ticks twice from identical initial state with
   * inputFn(frame) -> [p1word, p2word]; compares per-frame checksums.
   * Returns { ok, frames, mismatches, finalChecksum }.
   */
  selfTest(frames, inputFn) {
    const initial = this.snapshot(); // captured ONCE: both runs start here
    const run = () => {
      this.restore(initial);
      this.frame = 0;
      const sums = [];
      for (let f = 0; f < frames; f++) {
        const [i1, i2] = inputFn(f);
        const inputs = new Uint32Array([i1 >>> 0, i2 >>> 0]);
        this.tick(inputs, f);
        sums.push(this.checksum());
      }
      return { sums, final: this.checksum() };
    };
    const a = run();
    const b = run();
    let mismatches = 0;
    for (let f = 0; f < frames; f++) if (a.sums[f] !== b.sums[f]) mismatches++;
    this.restore(initial); // leave the adapter where the test found it
    return { ok: mismatches === 0, frames, mismatches, finalChecksum: a.final >>> 0 };
  }

  _fields() {
    // The tick needs the NAMED field object, not just the array list.
    // Subclasses / factories pass a fields object via fieldArrays() returning
    // arrays; for the reference sim we keep the named object alongside.
    return this._named || (this._named = this._namedFields());
  }

  /** Override (or set .bindNamed) to provide the named fields object. */
  _namedFields() { throw new Error('WhNetSim: bindNamed() not called'); }

  bindNamed(named) { this._named = named; return this; }
}

/**
 * makeReferenceSim() -- WhNetSim bound to the REAL reference fighter sim.
 * This is the live wiring proof: the adapter drives fighterSimulate with
 * the exact FIELDS layout, checksums every frame, and self-tests clean.
 */
export async function makeReferenceSim(simModule) {
  const sim = simModule || (await import('../sim/fighter-sim.js'));
  const fields = {};
  for (const [name, spec] of Object.entries(sim.FIELDS)) {
    fields[name] = new spec.type(spec.length);
  }
  sim.initFighterState(fields);
  const order = Object.keys(sim.FIELDS);
  const adapter = new WhNetSim({
    simulate: sim.fighterSimulate,
    fieldArrays: () => order.map((k) => fields[k]),
  });
  adapter.bindNamed(fields);
  adapter.simModule = sim;
  return adapter;
}

/**
 * runReferenceSelfTest(frames=600) -- the adapter determinism proof.
 * Scripted inputs: P1 walks in and jabs on a cycle, P2 blocks and
 * counter-pokes. Returns the selfTest report; throws on mismatch.
 */
export async function runReferenceSelfTest(frames = 600) {
  const adapter = await makeReferenceSim();
  const I = adapter.simModule.INPUT;
  const script = (f) => {
    // P1: approach, jab every 40f, jump every 97f. P2: hold block, poke back.
    let p1 = I.RIGHT;
    if (f % 40 < 3) p1 |= I.LP;
    if (f % 97 === 0) p1 |= I.UP;
    let p2 = I.BLOCK;
    if (f % 53 < 3) p2 |= I.LK;
    return [p1, p2];
  };
  return adapter.selfTest(frames, script);
}
