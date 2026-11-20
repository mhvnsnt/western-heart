// mirror.mjs -- the load-bearing determinism + rollback proof for the fighter sim.
//
//   node mirror.mjs   -> prints PASS lines, exit 0
//
// Two INDEPENDENT lite-rollback Sessions run the same fighter-sim for 3600
// frames (a full minute at 60 Hz). Each is fed the OTHER client's inputs through
// a deterministic, seeded, delayed channel -- the same wiring a real transport
// provides. Inputs are a scripted, frame-deterministic fight (walks, jumps,
// all four attacks, blocks) so the sim's combat paths all get exercised.
//
// Timing model (matches GGPO input-delay semantics):
//   - inputDelay d: at frame f the client samples its local input and it takes
//     effect at frame t = f + d (setLocalInput targets frame() + inputDelay).
//   - channelDelay c: a packet sampled at sender frame s is delivered when the
//     receiver's frame g satisfies g - s >= c.
//   - Scenario A (c == d): the remote input for frame t arrives exactly when the
//     receiver sits at frame t, before stepping it -> confirmed, zero rollbacks.
//   - Scenario B (c > d): the remote input for frame t arrives c - d frames
//     AFTER frame t was stepped on a prediction -> mispredict, rollback,
//     re-simulate. We assert rollbacks > 0 on BOTH clients so a regression that
//     silently stops rolling back is caught.
//
// In BOTH scenarios we compare checksumAt(confirmedFrame()) on both clients
// after every frame -- the GGPO confirmed-frame watermark, never the live
// frame, which legitimately differs while inputs are in flight. Equality there,
// frame after frame, is the guarantee. Pixels are not the pass condition;
// checksum equality is.

import { createSession } from './vendor/lite-rollback/src/index.js';
import { FIELDS, INPUT, fighterSimulate, initFighterState } from './sim/fighter-sim.js';

const FRAMES = 3600;
const CAPACITY = 128;
const SEED = 0x9e3779b9;

// Deterministic scripted fight: identical on every run, exercises walk, jump,
// all four attacks, and blocking for both players. Pure function of (player,
// targetFrame) so both clients sample the same value for the same frame.
function scriptedInput(player, frame) {
  let h = (((frame + 1) * 2654435761) ^ ((player + 1) * 0x85ebca77) ^ SEED) >>> 0;
  h ^= h >>> 15; h = (h * 0x2c1b3c6d) >>> 0;
  h ^= h >>> 12; h = (h * 0x2c1b3c6d) >>> 0;
  h ^= h >>> 15;
  const phase = (frame >>> 4) & 15; // 16-frame behavior windows
  const r = h & 0xff;
  let m = 0;
  // Player 0 advances, player 1 holds ground -- they meet mid-stage.
  if (player === 0 && phase < 6) m |= INPUT.RIGHT;
  if (player === 1 && phase < 6) m |= INPUT.LEFT;
  if (phase >= 6 && phase < 8) {
    if (r < 64) m |= INPUT.LP;
    else if (r < 128) m |= INPUT.HP;
    else if (r < 192) m |= INPUT.LK;
    else m |= INPUT.HK;
  }
  if (phase >= 8 && phase < 10 && r < 128) m |= INPUT.BLOCK;
  if (phase >= 10 && phase < 12 && r < 96) m |= INPUT.UP;
  if (phase >= 12 && r < 64) m |= INPUT.LK;
  return m >>> 0;
}

function makeClient(player, inputDelay) {
  const session = createSession({
    capacity: CAPACITY,
    fields: FIELDS,
    numPlayers: 2,
    inputWords: 1,
    inputDelay,
    simulate: fighterSimulate,
  });
  session.setLocalPlayer(player);
  initFighterState(session.fields);
  return session;
}

function runScenario(name, inputDelay, channelDelay, expectRollbacks) {
  const a = makeClient(0, inputDelay);
  const b = makeClient(1, inputDelay);
  // In-flight packets: { frame (target), input, sentAt (sender frame) }.
  const toA = []; // b's inputs heading to a (player 1's inputs)
  const toB = []; // a's inputs heading to b (player 0's inputs)

  for (let f = 0; f < FRAMES; f++) {
    // Sample local input NOW; with inputDelay it takes effect at frame t.
    const t = f + inputDelay;
    const ia = scriptedInput(0, t);
    const ib = scriptedInput(1, t);
    a.setLocalInput(ia); // confirms player 0, frame t, on A
    b.setLocalInput(ib); // confirms player 1, frame t, on B
    toB.push({ frame: t, input: ia, sentAt: f });
    toA.push({ frame: t, input: ib, sentAt: f });

    // Deliver packets whose channel delay has elapsed.
    for (let i = toA.length - 1; i >= 0; i--) {
      const p = toA[i];
      if (f - p.sentAt >= channelDelay) { a.feedRemoteInput(1, p.frame, p.input); toA.splice(i, 1); }
    }
    for (let i = toB.length - 1; i >= 0; i--) {
      const p = toB[i];
      if (f - p.sentAt >= channelDelay) { b.feedRemoteInput(0, p.frame, p.input); toB.splice(i, 1); }
    }

    a.step();
    b.step();

    // Compare at the confirmed watermark.
    const w = Math.min(a.confirmedFrame(), b.confirmedFrame());
    if (w >= 0) {
      const ha = a.checksumAt(w);
      const hb = b.checksumAt(w);
      if (ha !== hb) {
        console.error(`FAIL [${name}] desync at confirmed frame ${w}: a=${ha} b=${hb}`);
        process.exit(1);
      }
    }
    if (a.stats.desyncs > 0 || b.stats.desyncs > 0) {
      console.error(`FAIL [${name}] true desync counter fired at frame ${f}`);
      process.exit(1);
    }
  }

  const okRollbacks = expectRollbacks
    ? (a.stats.rollbacks > 0 && b.stats.rollbacks > 0)
    : (a.stats.rollbacks === 0 && b.stats.rollbacks === 0);
  if (!okRollbacks) {
    console.error(`FAIL [${name}] rollback expectation missed: a=${a.stats.rollbacks} b=${b.stats.rollbacks}`);
    process.exit(1);
  }
  console.log(`PASS [${name}] frames=${FRAMES} confirmed=${a.confirmedFrame()}/${b.confirmedFrame()} ` +
    `rollbacks=${a.stats.rollbacks}/${b.stats.rollbacks} ` +
    `maxDepth=${a.stats.maxRollbackDepth}/${b.stats.maxRollbackDepth} ` +
    `desyncs=${a.stats.desyncs}/${b.stats.desyncs}`);
}

runScenario('A lockstep-clean (delay 2 == channel 2)', 2, 2, false);
runScenario('B real-rollback (delay 2 < channel 6)', 2, 6, true);
console.log('ALL PASS');
