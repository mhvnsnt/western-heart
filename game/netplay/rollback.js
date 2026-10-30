/* ============================================================
   WESTERN HEART — GGPO-style rollback netcode (JS algorithm port)
   Source design: GGPO (pond3r/ggpo, MIT) — prediction + rollback +
   resimulation. This is a JS implementation of GGPO's ALGORITHM
   (input prediction, confirmed-input tracking, snapshot / restore,
   rollback + resim on misprediction). It is NOT the GGPO C library
   and is NOT byte-compatible with GGPO C sessions: the WASM compile
   of the C library (Emscripten) is the later swap-in path, and this
   module's session interface (addInput / advance / snapshot hooks)
   is deliberately kept small so that swap does not touch game code.

   SCOPE (lane 8): this upgrades WH's netcode only. WH's online
   structure (game/js/online.js lobbies/tournaments, game/netplay/
   bridge, lobby, signaling, mirror.mjs) is NOT replaced and is NOT
   touched by this module. Combat simulation must stay deterministic:
   the sim object passed in owns state; this module only decides
   WHICH inputs each frame runs with and re-runs frames when a
   prediction turns out wrong. Physics state (game/js/physics.js,
   game/js/ragdoll.js) is never read here.

   Sim interface (caller-supplied, any deterministic sim):
     sim.save()    -> opaque snapshot (caller clones state)
     sim.load(snap)-> restore state from a snapshot
     sim.step(inputs) -> advance exactly one frame; inputs is an
       array indexed by player (0..numPlayers-1), each an input
       value the sim understands (numbers, bitmasks, objects).
   Input values must be comparable with === for prediction checks;
   object inputs should be interned / reused by the caller.

   Frames: frame numbers start at 0 and advance by 1 per advance().
   inputDelay: local inputs are delayed that many frames before they
   take effect (GGPO's input-delay behaviour); remote inputs that
   arrive after their frame was already simulated with a prediction
   trigger a rollback to that frame and a resim to the present.
   maxRollback: cap on resim length; exceeding it is reported in
   the advance() result (stats.rollbackOverflow) rather than
   silently dropping frames, so callers can surface it.
   ============================================================ */

export const GGPO_ALGORITHM = 'prediction + rollback + resim (JS port of GGPO design, MIT source)';
export const GGPO_C_SWAP_NOTE = 'WASM compile of pond3r/ggpo C library is the later byte-compatible swap-in; this module is the near-term JS path.';

export class RollbackSession {
  constructor({ numPlayers = 2, inputDelay = 2, maxRollback = 8, sim = null } = {}) {
    if (!sim || typeof sim.save !== 'function' || typeof sim.load !== 'function' || typeof sim.step !== 'function') {
      throw new Error('rollback: sim with save/load/step is required');
    }
    if (numPlayers < 1) throw new Error('rollback: numPlayers >= 1 required');
    this.numPlayers = numPlayers;
    this.inputDelay = inputDelay;
    this.maxRollback = maxRollback;
    this.sim = sim;
    this.frame = 0; // next frame to simulate
    // frame -> { inputs: [...], predicted: [bool,...], snapshot }
    this.history = new Map();
    // frame -> inputs already received (confirmed), per player
    this.confirmed = new Map();
    this.stats = { frames: 0, rollbacks: 0, resimmed: 0, mispredictions: 0, rollbackOverflow: 0 };
    this._lastInputs = new Array(numPlayers).fill(0);
  }

  // Record an input for a player at a frame. Local inputs are usually
  // added for (currentFrame + inputDelay); remote inputs arrive with
  // their original frame. Returns 'ok' | 'late' (frame already simulated).
  addInput(player, frame, input) {
    if (player < 0 || player >= this.numPlayers) throw new Error('rollback: bad player ' + player);
    if (!this.confirmed.has(frame)) this.confirmed.set(frame, new Array(this.numPlayers).fill(undefined));
    const slot = this.confirmed.get(frame);
    const wasPredicted = this.history.has(frame) && this.history.get(frame).predicted[player];
    slot[player] = input;
    if (frame < this.frame && wasPredicted && this.history.get(frame).inputs[player] !== input) {
      this.stats.mispredictions++;
      return 'late-mispredicted';
    }
    return frame < this.frame ? 'late' : 'ok';
  }

  // Advance one frame. If any already-simulated frame now has a
  // confirmed input that differs from its prediction, roll back to
  // the earliest such frame, restore its pre-frame snapshot, and
  // resimulate forward to the present, then simulate the new frame.
  advance() {
    let rolledBackTo = null;
    // Find earliest mispredicted simulated frame.
    for (let f = 0; f < this.frame; f++) {
      const rec = this.history.get(f);
      if (!rec) continue;
      const conf = this.confirmed.get(f);
      if (!conf) continue;
      for (let p = 0; p < this.numPlayers; p++) {
        if (rec.predicted[p] && conf[p] !== undefined && conf[p] !== rec.inputs[p]) {
          rolledBackTo = f;
          break;
        }
      }
      if (rolledBackTo !== null) break;
    }
    if (rolledBackTo !== null) {
      const span = this.frame - rolledBackTo;
      if (span > this.maxRollback) this.stats.rollbackOverflow++;
      this.sim.load(this.history.get(rolledBackTo).snapshot);
      this.stats.rollbacks++;
      for (let f = rolledBackTo; f < this.frame; f++) {
        const inputs = this._inputsFor(f);
        // Mark resimmed frames as no longer predicted where confirmed.
        const rec = this.history.get(f);
        rec.inputs = inputs;
        rec.predicted = this._predictedFlags(f, inputs);
        this.sim.step(inputs);
        this.stats.resimmed++;
      }
    }
    // Simulate the new frame with confirmed inputs where known,
    // otherwise the last known input for that player (prediction).
    const snapshot = this.sim.save();
    const inputs = this._inputsFor(this.frame);
    const predicted = this._predictedFlags(this.frame, inputs);
    this.history.set(this.frame, { inputs, predicted, snapshot });
    this.sim.step(inputs);
    for (let p = 0; p < this.numPlayers; p++) this._lastInputs[p] = inputs[p];
    this.frame++;
    this.stats.frames++;
    // Prune history older than maxRollback behind the current frame
    // (keeps memory bounded; snapshots are caller-owned clones).
    for (const f of [...this.history.keys()]) {
      if (f < this.frame - this.maxRollback - 2) { this.history.delete(f); this.confirmed.delete(f); }
    }
    return { frame: this.frame - 1, rolledBackTo, resimmed: rolledBackTo === null ? 0 : this.frame - 1 - rolledBackTo, stats: { ...this.stats } };
  }

  _inputsFor(frame) {
    const conf = this.confirmed.get(frame);
    const out = [];
    for (let p = 0; p < this.numPlayers; p++) {
      out.push(conf && conf[p] !== undefined ? conf[p] : this._lastInputs[p]);
    }
    return out;
  }

  _predictedFlags(frame, inputs) {
    const conf = this.confirmed.get(frame);
    return inputs.map((_, p) => !(conf && conf[p] !== undefined));
  }

  // Current frame number (next frame to simulate).
  get currentFrame() { return this.frame; }
}
