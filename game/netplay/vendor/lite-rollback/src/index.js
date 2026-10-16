// @zakkster/lite-rollback
// Zero-GC binary ring buffer + GGPO-shaped rollback Session for browser-native
// deterministic netcode. Single-file ESM. No dependencies. No allocations after
// construction.
//
// (c) Zahary Shinikchiev. MIT licensed.
//
// Two surfaces:
//   createRollback({ capacity, fields })
//     Pure binary ring buffer. commit() snapshots, rollback() pops + restores,
//     peek() reads. No knowledge of frames, inputs, or simulation.
//   createSession({ capacity, fields, numPlayers, inputWords, simulate, predict? })
//     GGPO-shaped wrapper. step(), setInput(), feedRemoteInput(). Owns a Rollback.
//     Re-simulates on misprediction. Tracks frame number.
//
// Both factories own a single ArrayBuffer per instance. Every snapshot is a
// TypedArray .set() -- one memcpy per field, zero allocation, zero GC.

// ---------------------------------------------------------------------------
//  Bounds & validation
// ---------------------------------------------------------------------------

const CAPACITY_MIN = 1;
const CAPACITY_MAX = 1 << 20;            // 1 048 576 frames -- sanity bound
const MAX_PLAYERS = 32;                  // one Uint32 bitmask per slot
const INPUT_WORDS_MAX = 16;              // 16 x Uint32 = 512 bits per player/frame

const TYPED_ARRAYS = new Set([
  Float32Array, Float64Array,
  Int32Array, Uint32Array,
  Int16Array, Uint16Array,
  Int8Array, Uint8Array, Uint8ClampedArray,
]);

// Symbol-keyed internal handle. Used by stateChecksum() to access a Rollback's
// pre-built Uint8Array views of each field's live region without paying for a
// fresh view allocation per call. Symbol-keyed (not string-keyed) so it does
// NOT show up in Object.keys / for..in / JSON.stringify, and cannot be
// accidentally referenced by user code that thinks it's a public field.
const LIVE_BYTES = Symbol('lite-rollback:liveBytes');

// Symbol-keyed internal handle used by the module-level wire codec
// (packInputs / unpackInputs) to reach a Session's input ring and shape without
// a public accessor. Symbol-keyed for the same reason as LIVE_BYTES: invisible
// to Object.keys / for..in / JSON.stringify, not a field user code can trip over.
const CODEC = Symbol('lite-rollback:codec');

function isPosInt(x) {
  return Number.isInteger(x) && x > 0;
}

function validateFields(fields) {
  if (!fields || typeof fields !== 'object') {
    throw new TypeError('fields: object required');
  }
  const names = Object.keys(fields);
  if (names.length === 0) {
    throw new RangeError('fields: at least one field required');
  }
  for (const n of names) {
    const f = fields[n];
    if (!f || typeof f !== 'object') {
      throw new TypeError(`fields.${n}: must be an object`);
    }
    if (!TYPED_ARRAYS.has(f.type)) {
      throw new TypeError(`fields.${n}: type must be a typed-array constructor`);
    }
    if (!isPosInt(f.length)) {
      throw new RangeError(`fields.${n}: length must be positive integer`);
    }
  }
  return names;
}

// ---------------------------------------------------------------------------
//  Rollback (S1) -- binary ring buffer
// ---------------------------------------------------------------------------

/**
 * Create a binary-state ring buffer.
 *
 * Memory layout (per field):
 *   [ live | slot 0 | slot 1 | ... | slot (capacity - 1) ]
 *
 * All fields share one backing `ArrayBuffer`. Snapshots are `TypedArray.set()`
 * memcpys -- one per field, zero allocation.
 *
 * @param {object} opts
 * @param {number} opts.capacity
 *   Ring depth. 1 <= capacity <= 2^20. MUST be a power of two -- the hot path
 *   uses `& mask` instead of `% capacity` to avoid the idiv tax.
 * @param {Record<string, {type: Function, length: number}>} opts.fields
 *   Named fields. Each entry: typed-array constructor + element count.
 * @returns {object} Rollback instance.
 */
export function createRollback(opts) {
  if (!opts || typeof opts !== 'object') {
    throw new TypeError('createRollback(opts): options object required');
  }
  const { capacity, fields } = opts;
  if (!Number.isInteger(capacity) || capacity < CAPACITY_MIN || capacity > CAPACITY_MAX) {
    throw new RangeError(`capacity: must be integer in [${CAPACITY_MIN}, ${CAPACITY_MAX}], got ${capacity}`);
  }
  // Power-of-two enforcement. The hot path uses `& mask` instead of `% capacity`,
  // turning a 10-15 cycle idiv into a 1-cycle and. Costs the user a snap to the
  // next power of two when sizing the rollback window; in practice 32 frames at
  // 60 Hz is the natural pick for ~500 ms tolerance regardless.
  if ((capacity & (capacity - 1)) !== 0) {
    throw new RangeError(`capacity: must be a power of two for bitwise-mask hot path, got ${capacity}`);
  }
  const mask = capacity - 1;
  const fieldNames = validateFields(fields);

  // Resolve the layout: byte sizes, total, and per-field offsets.
  //
  // TypedArray-view construction requires `byteOffset % BYTES_PER_ELEMENT === 0`.
  // When fields mix alignments and a smaller-aligned field precedes a larger
  // one (Uint8 -> Uint32 is the canonical case), naive packing lands the next
  // field's view at a misaligned offset and `new Uint32Array(buf, off, n)`
  // throws. We pad each field's start offset up to the next multiple of its
  // own BPE. The wasted bytes are bounded by `(maxBPE - 1) * (numFields - 1)`
  // per `total` (single-digit bytes per field, negligible vs the live + ring
  // allocation).
  const layout = [];
  let total = 0;
  for (const name of fieldNames) {
    const f = fields[name];
    const bpe = f.type.BYTES_PER_ELEMENT;
    // Align `total` up to a multiple of bpe before reserving this field's block.
    const misalign = total % bpe;
    if (misalign !== 0) total += bpe - misalign;
    const bytes = f.length * bpe;
    layout.push({ name, type: f.type, length: f.length, bytes, offset: total });
    total += bytes * (capacity + 1);   // 1 live + capacity ring slots
  }

  // One contiguous allocation for the lifetime of the rollback.
  const backing = new ArrayBuffer(total);

  // Build live views + ring views. Each field has `capacity + 1` typed-array
  // views into the same backing buffer.
  //
  // We also cache a Uint8Array view of each field's live region -- `stateChecksum`
  // hashes these directly without allocating a fresh view per call.
  //
  // Within one field's block the cursor stays aligned because every slot's
  // byte size is `length * bpe` (always a multiple of bpe). Alignment only
  // matters at the BOUNDARY between fields -- handled by the precomputed
  // `ent.offset` above.
  const live = Object.create(null);
  const liveBytes = Object.create(null);
  const ring = new Array(capacity);
  // Per-slot Uint8Array views, parallel to `ring`. `checksumSlot(n)` hashes a
  // committed ring slot with zero allocation exactly the way `stateChecksum`
  // hashes live: over pre-built byte views, never a fresh view per call. A raw
  // `stateChecksum(peek(n))` would fall off that path -- peek() returns the slot
  // WITHOUT the LIVE_BYTES handle, so it would allocate one Uint8Array per field
  // per call. These views cost `capacity x numFields` construction-time objects
  // (no backing-store growth: they alias the one existing ArrayBuffer).
  const ringBytes = new Array(capacity);
  for (let s = 0; s < capacity; s++) {
    ring[s] = Object.create(null);
    ringBytes[s] = Object.create(null);
  }

  for (const ent of layout) {
    let cursor = ent.offset;
    live[ent.name] = new ent.type(backing, cursor, ent.length);
    liveBytes[ent.name] = new Uint8Array(backing, cursor, ent.bytes);
    cursor += ent.bytes;
    for (let s = 0; s < capacity; s++) {
      ring[s][ent.name] = new ent.type(backing, cursor, ent.length);
      ringBytes[s][ent.name] = new Uint8Array(backing, cursor, ent.bytes);
      cursor += ent.bytes;
    }
  }

  // State.
  //   head  -- slot index of the most recent commit, -1 if depth === 0.
  //   depth -- number of valid commits (0 <= depth <= capacity).
  let head = -1;
  let depth = 0;

  // -------------------------------------------------------------------------
  //  Hot path -- no allocations
  // -------------------------------------------------------------------------

  function commit() {
    head = (head + 1) & mask;
    const slot = ring[head];
    // Numeric for-loop over a stable Array shape. V8 keeps `layout[i]` and
    // `slot[name]` lookups monomorphic across the loop body.
    for (let i = 0, n = layout.length; i < n; i++) {
      const name = layout[i].name;
      slot[name].set(live[name]);
    }
    if (depth < capacity) depth++;
  }

  function rollback(n) {
    if (n === undefined) n = 1;
    if (!Number.isInteger(n) || n < 1) {
      throw new RangeError(`rollback(${n}): n must be positive integer`);
    }
    if (n > depth) {
      throw new RangeError(`rollback(${n}): only ${depth} commits available`);
    }
    // Discard the n most recent commits AND restore live to the state from
    // BEFORE them. Symmetric with `peek`: peek(n) returns ring[head - n];
    // rollback(n) copies that slot into live and rewinds head there. After
    // rollback, live === peek(0) -- live and history-tip agree.
    //
    // Net result of `rollback(n)` followed by re-committing n frames: the
    // surviving history before the rollback is INTACT. Earlier versions used
    // `restoreIdx = (head - n + 1) & mask` with `head = (head - n) & mask`,
    // leaving live and head out of sync by one slot -- the next commit
    // overwrote the slot that held the just-restored state, deleting it
    // from history and producing a permanent desync if a later mismatch
    // needed it. See test/desync.test.js for the regression.
    const restoreIdx = (head - n) & mask;
    const slot = ring[restoreIdx];
    for (let i = 0, count = layout.length; i < count; i++) {
      const name = layout[i].name;
      live[name].set(slot[name]);
    }
    head = restoreIdx;
    depth -= n;
  }

  function peek(n) {
    if (n === undefined) n = 0;
    if (!Number.isInteger(n) || n < 0) {
      throw new RangeError(`peek(${n}): n must be non-negative integer`);
    }
    if (n >= depth) {
      throw new RangeError(`peek(${n}): only ${depth} commits available`);
    }
    const idx = (head - n) & mask;
    return ring[idx];
  }

  // Zero-alloc checksum of a committed ring slot, addressed exactly like peek(n):
  // the n-th most recent commit. Hashes the slot's pre-built per-field Uint8Array
  // views in layout (declaration) order -- the SAME order and routine
  // `stateChecksum` uses over the live region -- so `checksumSlot(0)` right after
  // a commit equals `stateChecksum` of the live state that produced it. Used by
  // Session.checksumAt() to compare a specific committed frame across clients
  // without the per-field view allocation `stateChecksum(peek(...))` would incur.
  function checksumSlot(n, seed) {
    if (n === undefined) n = 0;
    if (!Number.isInteger(n) || n < 0) {
      throw new RangeError(`checksumSlot(${n}): n must be non-negative integer`);
    }
    if (n >= depth) {
      throw new RangeError(`checksumSlot(${n}): only ${depth} commits available`);
    }
    const slotBytes = ringBytes[(head - n) & mask];
    let h = (seed === undefined ? 0 : seed) >>> 0;
    for (let i = 0, count = layout.length; i < count; i++) {
      h = checksum(slotBytes[layout[i].name], h);
    }
    return h >>> 0;
  }

  function reset() {
    head = -1;
    depth = 0;
    // Note: we do not zero the backing buffer. Old data remains until
    // overwritten. This matches @zakkster/lite-batch-buffer's reset() and
    // is intentional -- zeroing on reset would defeat the point.
  }

  return Object.freeze({
    // Inspection
    capacity,
    arrayBuffer: backing,
    byteLength: total,
    fields: live,
    depth: () => depth,
    head: () => head,

    // Operations
    commit,
    rollback,
    peek,
    checksumSlot,
    reset,

    // Symbol-keyed handle to per-field Uint8Array views over the live region.
    // Used by stateChecksum() to hash without allocating new views per call.
    // Not part of the public API; not enumerable as a string key.
    [LIVE_BYTES]: liveBytes,
  });
}

// ---------------------------------------------------------------------------
//  Session (S2) -- input queue + simulate + fast-forward
// ---------------------------------------------------------------------------

/**
 * Create a rollback Session.
 *
 * Wraps a `createRollback` instance with:
 *   - an input ring (capacity x numPlayers x inputWords Uint32s)
 *   - a confirmation bitmask per slot
 *   - a frame counter
 *   - automatic fast-forward on misprediction
 *
 * @param {object} opts
 * @param {number} opts.capacity
 *   Ring depth (typical: 8-32 for fighters, 60 for tolerance).
 * @param {Record<string, {type: Function, length: number}>} opts.fields
 *   Field schema. See createRollback.
 * @param {number} opts.numPlayers
 *   1..32.
 * @param {number} [opts.inputWords=1]
 *   Uint32 words per player per frame (default 1 = 32 bits).
 * @param {number} [opts.inputDelay=0]
 *   Local input delay in frames (v1.2.0). 0..capacity-1.
 * @param {(fields: object, inputs: Uint32Array, frame: number) => void} opts.simulate
 *   Mutates fields in place. MUST be deterministic given (fields, inputs, frame).
 * @param {(player: number, frame: number, scratch: Uint32Array, outOff: number) => void} [opts.predict]
 *   Custom predictor. Writes inputWords words into scratch starting at outOff.
 *   Defaults to "repeat last confirmed input for the player".
 * @returns {object} Session instance.
 */
export function createSession(opts) {
  if (!opts || typeof opts !== 'object') {
    throw new TypeError('createSession(opts): options object required');
  }
  const {
    capacity,
    fields,
    numPlayers,
    inputWords = 1,
    inputDelay = 0,
    simulate,
    predict,
    onDesync,
  } = opts;

  if (!isPosInt(numPlayers) || numPlayers > MAX_PLAYERS) {
    throw new RangeError(`numPlayers: must be positive integer <= ${MAX_PLAYERS}, got ${numPlayers}`);
  }
  if (!isPosInt(inputWords) || inputWords > INPUT_WORDS_MAX) {
    throw new RangeError(`inputWords: must be positive integer <= ${INPUT_WORDS_MAX}, got ${inputWords}`);
  }
  // Local input delay (v1.2.0): buffer the local player's input `inputDelay`
  // frames before it takes effect. Must be an integer in [0, capacity - 1] -- a
  // delayed write targets frame `frame + inputDelay`, which must stay inside the
  // one-revolution ring window; capacity or more would alias a live slot. Fail
  // closed on a non-integer or out-of-range value, matching the capacity /
  // numPlayers validation style. See decisions/0004-input-delay.md.
  if (!Number.isInteger(inputDelay) || inputDelay < 0 || inputDelay > capacity - 1) {
    throw new RangeError(`inputDelay: must be integer in [0, ${capacity - 1}], got ${inputDelay}`);
  }
  if (typeof simulate !== 'function') {
    throw new TypeError('simulate: function required');
  }
  if (predict !== undefined && typeof predict !== 'function') {
    throw new TypeError('predict: must be function if provided');
  }
  if (onDesync !== undefined && typeof onDesync !== 'function') {
    throw new TypeError('onDesync: must be function if provided');
  }

  // Owned rollback for state snapshots.
  const rb = createRollback({ capacity, fields });
  const mask = capacity - 1;   // rollback already validated power-of-two

  // Input ring: contiguous Uint32 storage.
  // Layout: inputRing[(slot * numPlayers + player) * inputWords + word]
  const inputRing = new Uint32Array(capacity * numPlayers * inputWords);

  // Per-slot confirmation bitmask. Bit p set => player p's input for this slot
  // is real, not predicted.
  const confirmedMask = new Uint32Array(capacity);

  // Last-confirmed input per player. Used by the default predictor.
  // Pre-allocated. No GC.
  const lastConfirmedInput = new Uint32Array(numPlayers * inputWords);

  // Frame number of the most recent input confirmation we've applied to
  // `lastConfirmedInput` per player. Used to ignore late/out-of-order remote
  // packets that would otherwise poison the predictor by overwriting newer
  // truth with older. Initial `-1` means "no confirmation yet"; any f >= 0
  // qualifies.
  const lastConfirmedFrame = new Int32Array(numPlayers);
  for (let p = 0; p < numPlayers; p++) lastConfirmedFrame[p] = -1;

  // Scratch input buffer passed to simulate() each frame. Pre-allocated.
  const inputScratch = new Uint32Array(numPlayers * inputWords);

  // Reused by unpackInputs() when inputWords > 1: a single per-player input is
  // copied here from the wire buffer before being handed to the feed callback,
  // so decoding a multi-word packet allocates nothing. inputWords === 1 uses the
  // numeric fast path and never touches this. Pre-allocated, never grown.
  const codecScratch = new Uint32Array(inputWords);

  // Observability counters (R-03, v1.1.0). A pre-allocated Uint32 block, never
  // reallocated -- every update is a typed-array store on an already-rare branch
  // (rollback or confirmed-mismatch), so the zero-alloc contract holds. Exposed
  // read-only via `session.stats` getters below. See decisions/0003-observability.md.
  const STAT_ROLLBACKS = 0;         // feedRemoteInput calls that rolled back
  const STAT_MAX_ROLLBACK_DEPTH = 1;// deepest single rollback (frames re-simulated)
  const STAT_MISPREDICTIONS = 2;    // predicted inputs later corrected
  const STAT_DESYNCS = 3;           // confirmed-input mismatches (true divergence)
  const STAT_FAST_FORWARD = 4;      // total frames re-simulated across all rollbacks
  const statsArr = new Uint32Array(5);

  // Frame counter. Monotonic; wraps to ring slots via bitwise mask.
  let frame = 0;
  let localPlayer = 0;

  // Genesis commit (R-02, v1.1.0). Snapshot the pre-frame-0 state -- state(-1) --
  // so a frame-0 misprediction can roll back to a real committed baseline instead
  // of landing in the out-of-window branch and baking the error in permanently.
  //
  // CRITICAL: it must capture the caller's ACTUAL pre-frame-0 live state, not
  // construction-time zeros. A user may seed initial conditions by writing
  // `session.fields` after construction and before the first step(); if genesis
  // snapshotted zeros, a later frame-0 rollback would silently restore zero over
  // that seed and desync against a peer that never rolled back. So genesis is
  // committed lazily, once, at the TOP of the first step() -- when live holds
  // whatever the caller has set -- guarded by `genesisDone`. reset() re-arms it.
  //
  // It is an HONEST ring commit, not a hidden side buffer: it occupies one ring
  // slot and raises depth() by one from the first step until it rolls off the back
  // after `capacity` further commits (mid-match, once evicted, depth() and the redo
  // window are exactly as before). We keep depth() a true mirror of the state ring
  // -- hiding genesis would decouple depth() from the raw `rollback`/`peek`
  // pass-throughs advanced users rely on. See decisions/0002-genesis.md.
  let genesisDone = false;
  function ensureGenesis() {
    if (!genesisDone) { rb.commit(); genesisDone = true; }
  }

  // -------------------------------------------------------------------------
  //  Helpers (all zero-alloc)
  // -------------------------------------------------------------------------

  function slotOf(f) {
    // Bitwise AND on a signed Int32 in JS handles negative `f` correctly
    // for a power-of-two mask.
    return f & mask;
  }

  function inputOffset(slot, player) {
    return (slot * numPlayers + player) * inputWords;
  }

  function lastConfirmedOffset(player) {
    return player * inputWords;
  }

  function writeInputAt(slot, player, input) {
    const off = inputOffset(slot, player);
    if (typeof input === 'number') {
      if (inputWords !== 1) {
        throw new TypeError(`input: numeric form requires inputWords === 1, got ${inputWords}`);
      }
      inputRing[off] = input >>> 0;
    } else {
      // input is a Uint32Array-like with at least inputWords entries.
      for (let w = 0; w < inputWords; w++) inputRing[off + w] = input[w] >>> 0;
    }
  }

  // Update `lastConfirmedInput[player]` to mirror the input written into
  // `inputRing[slot, player]`, but ONLY if `f` is at least as recent as
  // the most recent confirmation we've applied for this player. Late /
  // out-of-order remote packets (e.g. f=5 arriving after f=8 was already
  // confirmed) would otherwise overwrite newer truth with older, making
  // the predictor mis-predict every subsequent frame.
  function maybeAdvanceLastConfirmed(slot, player, f) {
    if (f < lastConfirmedFrame[player]) return;
    lastConfirmedFrame[player] = f;
    // Do NOT let a FUTURE (input-delayed) confirmation poison the predictor. The
    // default predictor repeats the last input the frame counter has actually
    // REACHED. A delayed local input for frame `frame + inputDelay` legitimately
    // advances the watermark above, but must not become the value predicted for
    // the not-yet-reached startup frames 0..inputDelay-1 -- those must stay
    // neutral, matching what a peer predicts for them, or the two clients desync
    // permanently at startup (the startup frames' local inputs are never
    // transmitted). With the default inputDelay 0 every write has f <= frame, so
    // this guard never fires and behaviour is byte-identical to earlier versions.
    // See decisions/0004-input-delay.md.
    if (f > frame) return;
    const src = inputOffset(slot, player);
    const dst = lastConfirmedOffset(player);
    for (let w = 0; w < inputWords; w++) lastConfirmedInput[dst + w] = inputRing[src + w];
  }

  // Default predictor: repeat the last confirmed input for the player.
  // Zero-alloc: writes directly into `inputScratch[outOff..outOff+inputWords]`.
  function defaultPredict(player, _f, scratch, outOff) {
    const srcOff = lastConfirmedOffset(player);
    for (let w = 0; w < inputWords; w++) scratch[outOff + w] = lastConfirmedInput[srcOff + w];
  }

  const doPredict = predict || defaultPredict;

  // Fill inputScratch with inputs for frame `f`: real where confirmed,
  // predicted otherwise.
  //
  // CRITICAL: when we predict, we also persist the predicted value into the
  // input ring at that slot. Then on feedRemoteInput, comparing incoming
  // against inputRing tells us "did my prediction match the truth?" -- and
  // we only rollback on actual mismatches.
  function fillInputs(f) {
    const slot = slotOf(f);
    // Read the confirmation mask for this slot ONCE. Use a clearly-named local
    // (`confMask`) so it doesn't shadow the outer power-of-two `mask`.
    const confMask = confirmedMask[slot];
    for (let p = 0; p < numPlayers; p++) {
      const outOff = p * inputWords;
      const inOff = inputOffset(slot, p);
      if (confMask & (1 << p)) {
        for (let w = 0; w < inputWords; w++) inputScratch[outOff + w] = inputRing[inOff + w];
      } else {
        doPredict(p, f, inputScratch, outOff);
        // Persist the prediction so feedRemoteInput can compare against it.
        for (let w = 0; w < inputWords; w++) inputRing[inOff + w] = inputScratch[outOff + w];
      }
    }
  }

  // -------------------------------------------------------------------------
  //  Public API
  // -------------------------------------------------------------------------

  /**
   * Set the local player's input, marking it confirmed (it can't be wrong -- it
   * is local). With `inputDelay` > 0 the input takes effect `inputDelay` frames
   * from now (target frame `frame + inputDelay`), giving the network that many
   * frames of lead time to deliver it before it is needed -- the single biggest
   * rollback-frequency reducer. With the default `inputDelay` 0 it targets the
   * current frame, unchanged from earlier versions.
   */
  function setLocalInput(input) {
    setInput(localPlayer, frame + inputDelay, input);
  }

  /**
   * Set a player's input for a specific frame, marking it confirmed.
   * Frame must be in the window [frame - capacity + 1, frame + inputDelay] -- the
   * upper bound admits the local input-delay writes (v1.2.0); with inputDelay 0
   * it is the historical [frame - capacity + 1, frame].
   * Mainly used to seed inputs before the first step() or in tests.
   */
  function setInput(player, f, input) {
    if (!Number.isInteger(player) || player < 0 || player >= numPlayers) {
      throw new RangeError(`setInput: player ${player} out of [0, ${numPlayers})`);
    }
    if (!Number.isInteger(f)) {
      throw new TypeError(`setInput: frame must be integer, got ${f}`);
    }
    if (f > frame + inputDelay || f < frame - capacity + 1) {
      throw new RangeError(`setInput: frame ${f} outside window [${frame - capacity + 1}, ${frame + inputDelay}]`);
    }
    const slot = slotOf(f);
    writeInputAt(slot, player, input);
    confirmedMask[slot] |= (1 << player);
    maybeAdvanceLastConfirmed(slot, player, f);
  }

  /**
   * Advance one frame.
   *   1. Fill inputs (real where confirmed, predicted otherwise).
   *   2. Call simulate(fields, inputs, frame).
   *   3. Commit the resulting state.
   *   4. Increment frame.
   *
   * Hot path: zero allocations.
   */
  function step() {
    // Commit the genesis baseline (state(-1)) on the very first step, capturing
    // the caller's actual pre-frame-0 live state. Fires once per match (guarded);
    // after that this is a single predicted-not-taken boolean test. R-02, v1.1.0.
    ensureGenesis();
    fillInputs(frame);
    simulate(rb.fields, inputScratch, frame);
    rb.commit();
    frame++;
    // Wrap-clear (v1.0.3, fixes the stale-confirmedMask desync; generalized for
    // input delay in v1.2.0). Clear the confirmed bits of the slot for the
    // FURTHEST-AHEAD writable frame, `frame + inputDelay` -- the frame that just
    // became reachable by this step's advance. That slot was last occupied by
    // frame `frame + inputDelay - capacity`, a full revolution ago; its bits are
    // stale. Clearing it here -- after frame++ and BEFORE the caller's next
    // setLocalInput (which writes exactly this frame + inputDelay) -- means
    // fillInputs() can never mistake a revolution-old input for confirmed truth,
    // and a live delayed input written for a nearer frame is never touched.
    //
    // With the default inputDelay 0 this is `confirmedMask[frame & mask] = 0`,
    // byte-identical to v1.0.3. With inputDelay > 0 the entering slot legitimately
    // holds the delayed input for the current frame (written `inputDelay` frames
    // ago), so clearing the entering slot would erase a live confirmation -- the
    // collision proven safe in decisions/0004-input-delay.md by clearing the
    // just-opened future slot instead. A future write (setLocalInput at counter
    // frame) lands AFTER this clear; no wrap-clear revisits the slot until a full
    // revolution later, so the delayed input survives to consumption. One store,
    // no branch, no allocation. Deliberately NOT done inside feedRemoteInput's
    // fast-forward loop: those slots hold genuine confirmations being replayed.
    // See decisions/0001-wrap-clear.md and decisions/0004-input-delay.md.
    confirmedMask[(frame + inputDelay) & mask] = 0;
  }

  /**
   * Accept a remote player's input for some frame `f`.
   * If `f` is in the past AND the actual input differs from what we predicted,
   * rolls back state to before `f` and fast-forwards back to the current frame.
   *
   * @returns {boolean} true if a rollback was performed.
   */
  function feedRemoteInput(player, f, input) {
    if (!Number.isInteger(player) || player < 0 || player >= numPlayers) {
      throw new RangeError(`feedRemoteInput: player ${player} out of [0, ${numPlayers})`);
    }
    if (!Number.isInteger(f)) {
      throw new TypeError(`feedRemoteInput: frame must be integer, got ${f}`);
    }
    if (f > frame) {
      throw new RangeError(`feedRemoteInput: frame ${f} is in the future (current ${frame})`);
    }
    if (f < frame && f < frame - rb.depth() + 1 + inputDelay) {
      // A PAST frame (`f < frame`) too old to safely redo -- too late to apply.
      // This region is fully INERT: it stores NOTHING (no writeInputAt, no
      // confirmedMask, no maybeAdvanceLastConfirmed) and returns false. Such a
      // packet's slot `f & mask` may alias a still-pending frame, and a stale
      // confirmed bit there would be read as truth by `fillInputs` later and
      // misroute THAT frame's own in-window correction into the desync branch
      // (silent R-01 through the aliased slot). Two aliasing cases:
      //   - the RESERVED BAND `[frame - depth + 1, frame - depth + inputDelay]`
      //     (v1.2.0): its slot is owned by a pending delayed FUTURE frame
      //     `f + capacity in [frame + 1, frame + inputDelay]` whose wrap-clear has
      //     already run; and
      //   - the UPPER EDGE `f = frame - capacity` (pre-existing since v1.1.0):
      //     `f + capacity === frame`, the CURRENT not-yet-stepped frame, whose
      //     slot must stay clean so `fillInputs(frame)` predicts, not reads stale.
      // Storing buys nothing for frame `f` regardless: it is out of the redo
      // window and will never be re-simulated, and the default predictor reads
      // `lastConfirmedInput`, not the raw ring slot. So inert is correct.
      //
      // CRUCIAL: this rejection is gated on `f < frame`. The CURRENT frame
      // (`f === frame`) is NOT a redo -- it is the frame being assembled, whose
      // slot is owned only by itself -- so it must fall through to the normal path
      // and be CONFIRMED, even before the first step when `depth === 0` puts the
      // floor above `frame` (the delay-0 unseeded-frame-0 mirror: a remote input
      // arriving for the current frame before it is stepped). Its slot cannot
      // alias any in-play frame (`frame +/- capacity` are never in the redo
      // window since depth <= capacity), so confirming it is safe.
      //
      // Redo window: `[frame - depth + 1 + inputDelay, frame - 1]`, i.e.
      // `capacity - 1 - inputDelay` frames at steady state; the `+ inputDelay`
      // uses `depth` (not `capacity`) so it stays correct through startup and
      // genesis eviction (a safe over-approximation, depth <= capacity). See
      // decisions/0004-input-delay.md.
      return false;
    }

    const slot = slotOf(f);
    const off = inputOffset(slot, player);
    const wasConfirmed = (confirmedMask[slot] & (1 << player)) !== 0;

    // Detect mismatch against current ring contents.
    let mismatch = false;
    if (typeof input === 'number') {
      if (inputWords !== 1) {
        throw new TypeError(`feedRemoteInput: numeric input requires inputWords === 1`);
      }
      if (inputRing[off] !== (input >>> 0)) mismatch = true;
      inputRing[off] = input >>> 0;
    } else {
      for (let w = 0; w < inputWords; w++) {
        const v = input[w] >>> 0;
        if (inputRing[off + w] !== v) mismatch = true;
        inputRing[off + w] = v;
      }
    }
    confirmedMask[slot] |= (1 << player);
    maybeAdvanceLastConfirmed(slot, player, f);

    // If the slot was previously predicted (or simulated with a wrong value)
    // AND we're now in the past relative to `frame`, we must re-simulate.
    if (mismatch && f < frame && wasConfirmed === false) {
      // We need live to equal state(f - 1) -- the state captured AFTER
      // frame (f - 1) finished, BEFORE frame f's simulate ran. After
      // step(N), `frame === N + 1` and the most recent commit is state(N).
      // The number of commits we need to discard (frames f, f+1, ...,
      // frame-1) is exactly `frame - f`. Under v1.0.2+ rollback semantics
      // (symmetric with peek), rollback(frame - f) restores live to
      // peek(frame - f) BEFORE the call, which is state(f - 1). Previous
      // versions used `frame - f + 1` against the old off-by-one rollback
      // and silently corrupted history on the redo path; see
      // test/desync.test.js for the regression.
      const framesBack = frame - f;
      // Observability (R-03): a misprediction was detected and is being corrected.
      // Typed-array stores on the already-taken rollback branch -- zero alloc.
      statsArr[STAT_MISPREDICTIONS]++;
      statsArr[STAT_ROLLBACKS]++;
      if (framesBack > statsArr[STAT_MAX_ROLLBACK_DEPTH]) statsArr[STAT_MAX_ROLLBACK_DEPTH] = framesBack;
      statsArr[STAT_FAST_FORWARD] += framesBack;
      rb.rollback(framesBack);
      const targetFrame = frame;
      frame = f;
      while (frame < targetFrame) {
        fillInputs(frame);
        simulate(rb.fields, inputScratch, frame);
        rb.commit();
        frame++;
      }
      return true;
    }

    // Mismatch in an ALREADY-CONFIRMED PAST input is a desync signal, not a
    // misprediction: two clients that both marked past frame `f` confirmed now hold
    // different truths for it. We do NOT auto-correct (the invariant), but we must
    // make the divergence observable (R-03): bump the counter and fire the optional
    // onDesync callback. The guard mirrors the misprediction branch exactly
    // (`f < frame && wasConfirmed` vs `f < frame && !wasConfirmed`), so the
    // remaining fall-through -- a current-frame (f === frame) re-confirmation, whose
    // frame has not been simulated or committed yet -- is benign and not counted.
    // The boolean return is unchanged for compatibility.
    if (mismatch && f < frame && wasConfirmed) {
      statsArr[STAT_DESYNCS]++;
      if (onDesync !== undefined) onDesync(f, player);
    }
    return false;
  }

  function reset() {
    rb.reset();
    // Session.reset goes further than Rollback.reset -- it zeroes live state
    // too. The pure rollback primitive doesn't (cheaper, matches lite-batch-
    // buffer convention); but at the Session layer "reset" semantically means
    // "start a new match", so a known-zero baseline is the useful contract.
    const live = rb.fields;
    for (const name in live) live[name].fill(0);
    inputRing.fill(0);
    confirmedMask.fill(0);
    lastConfirmedInput.fill(0);
    for (let p = 0; p < numPlayers; p++) lastConfirmedFrame[p] = -1;
    inputScratch.fill(0);
    statsArr.fill(0);
    frame = 0;
    // Re-arm genesis: it is (re)committed at the top of the next step(), so it
    // captures whatever initial state the caller sets before stepping the new
    // match. depth() is 0 immediately after reset (as on a fresh session) and
    // becomes 1 once the first step() commits genesis.
    genesisDone = false;
  }

  // The highest frame at which EVERY player's input is real (confirmed), not
  // predicted -- the GGPO "confirmed frame" watermark (v1.1.0). Defined as the
  // minimum over players of each player's most-recent confirmed frame, so it is
  // monotone non-decreasing (confirmations only advance) and never exceeds the
  // lowest per-player confirmed frame. -1 means no fully-confirmed frame yet.
  // This is the value S3's input-delay / frame-advantage / checksum-exchange
  // helpers key off. Zero alloc: a numPlayers-wide min into a local.
  function confirmedFrame() {
    let m = lastConfirmedFrame[0];
    for (let p = 1; p < numPlayers; p++) {
      if (lastConfirmedFrame[p] < m) m = lastConfirmedFrame[p];
    }
    return m;
  }

  // Local-vs-remote frame lead (v1.2.0): the raw delta between the local player's
  // most-recent confirmed frame and the confirmed-frame watermark (the slowest
  // player). Positive means the local client is running ahead of the remotes'
  // confirmed inputs -- the caller's loop can stall to let them catch up (GGPO
  // time-sync). Zero when everyone is level; can go negative if some other player
  // is further ahead than the local one. Pure read of the per-player watermark;
  // zero allocation. A never-confirmed player pins confirmedFrame() at -1. See
  // decisions/0004-input-delay.md.
  function frameAdvantage() {
    return lastConfirmedFrame[localPlayer] - confirmedFrame();
  }

  // Checksum-exchange helper (v1.2.0). The 32-bit hash of the COMMITTED state at
  // frame `f`, so two clients can compare the same committed frame -- typically
  // `confirmedFrame()`, the highest frame both have real inputs for -- rather than
  // whatever live frame each happens to be on. Reaches the committed slot through
  // the ring's zero-alloc `checksumSlot`, never `stateChecksum(peek(...))` (which
  // would allocate a view per field per call).
  //
  // Head math (genesis-aware, decision 0002): after N steps `frame === N` and the
  // most recent commit peek(0) is state(N - 1); peek(n) is state(N - 1 - n). To
  // reach state(f) we peek n = frame - 1 - f. Fail closed: a frame outside the
  // committed window [frame - depth, frame - 1] throws RangeError -- a checksum is
  // a full Uint32 with no free sentinel, and a null answer is not a zero one.
  function checksumAt(f, seed) {
    if (!Number.isInteger(f)) {
      throw new TypeError(`checksumAt: frame must be integer, got ${f}`);
    }
    const n = frame - 1 - f;
    const d = rb.depth();
    if (n < 0 || n >= d) {
      throw new RangeError(
        `checksumAt: frame ${f} outside committed window [${frame - d}, ${frame - 1}]`);
    }
    return rb.checksumSlot(n, seed);
  }

  // Read-only view over the observability counters (R-03). Stable frozen object;
  // the getters read the live typed array, so values are always current and no
  // allocation happens on read. Counters are cumulative until reset().
  const stats = Object.freeze({
    get rollbacks() { return statsArr[STAT_ROLLBACKS]; },
    get maxRollbackDepth() { return statsArr[STAT_MAX_ROLLBACK_DEPTH]; },
    get mispredictions() { return statsArr[STAT_MISPREDICTIONS]; },
    get desyncs() { return statsArr[STAT_DESYNCS]; },
    get fastForwardFrames() { return statsArr[STAT_FAST_FORWARD]; },
  });

  // Expose a minimal subset of the rollback's surface plus session-specific ops.
  // Note: `rollback`, `commit`, `peek` are pass-throughs to the underlying ring
  // and do NOT touch the frame counter -- they are for advanced users who want
  // raw access to the state ring. The frame-aware path is feedRemoteInput().
  return Object.freeze({
    // Inspection
    capacity,
    numPlayers,
    inputWords,
    inputDelay,
    fields: rb.fields,
    frame: () => frame,
    depth: rb.depth,
    confirmedFrame,
    frameAdvantage,
    checksumAt,
    stats,
    arrayBuffer: rb.arrayBuffer,

    get localPlayer() { return localPlayer; },
    setLocalPlayer(p) {
      if (!Number.isInteger(p) || p < 0 || p >= numPlayers) {
        throw new RangeError(`setLocalPlayer(${p}): out of [0, ${numPlayers})`);
      }
      localPlayer = p;
    },

    // Session operations
    setLocalInput,
    setInput,
    step,
    feedRemoteInput,

    // Pass-through to underlying rollback (advanced users)
    commit: rb.commit,
    rollback: rb.rollback,
    peek: rb.peek,
    reset,

    // Symbol-keyed forward to the underlying rollback's live-byte views.
    // Used by stateChecksum() on a Session just as on a Rollback.
    [LIVE_BYTES]: rb[LIVE_BYTES],

    // Symbol-keyed handle for the module-level wire codec. Gives packInputs /
    // unpackInputs direct, zero-alloc access to the input ring and shape without
    // a public accessor. Not enumerable; not part of the string-keyed API.
    [CODEC]: {
      inputRing,
      numPlayers,
      inputWords,
      capacity,
      mask,
      scratch: codecScratch,
    },
  });
}

// ---------------------------------------------------------------------------
//  Checksum -- state-hash utility for desync detection
// ---------------------------------------------------------------------------

/**
 * Fast non-cryptographic 32-bit hash over a typed-array region.
 *
 * Variant of the FNV-1a / xor-rotate family -- good enough for detecting state
 * divergence between two clients running the same simulation. NOT suitable for
 * security or content-addressing.
 *
 * Zero allocation when passed a typed-array view. When passed a raw ArrayBuffer,
 * allocates ONE Uint8Array view per call -- pass a view instead for hot paths.
 * Stable across little-endian platforms (which is all the platforms anyone
 * runs a browser on in practice).
 *
 * @param {ArrayBuffer | ArrayBufferView} buf
 * @param {number} [seed=0]
 * @returns {number} Uint32 hash
 */
export function checksum(buf, seed) {
  if (seed === undefined) seed = 0;
  let bytes;
  // Fast path: caller already has a Uint8Array (this is what `stateChecksum`
  // hands us per cached LIVE_BYTES view). Skip the re-wrap, save one view
  // allocation per field per call. Other typed-array views (Float32Array,
  // Uint32Array, etc.) still need wrapping to expose their bytes.
  if (buf instanceof Uint8Array) {
    bytes = buf;
  } else if (buf instanceof ArrayBuffer) {
    bytes = new Uint8Array(buf);
  } else if (ArrayBuffer.isView(buf)) {
    bytes = new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  } else {
    throw new TypeError('checksum: ArrayBuffer or typed-array view required');
  }
  // xor-rotate-multiply: simple, fast, decent avalanche for state diffs.
  let h = (seed >>> 0) ^ 0x9e3779b9;
  const len = bytes.length;
  for (let i = 0; i < len; i++) {
    h ^= bytes[i];
    // 32-bit rotate-left by 5, multiply by 0x01000193 (FNV prime), clamp to u32.
    h = (((h << 5) | (h >>> 27)) >>> 0);
    h = Math.imul(h, 0x01000193);
  }
  // Final avalanche.
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b);
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35);
  h ^= h >>> 16;
  return h >>> 0;
}

/**
 * Compute a checksum across all fields of a Rollback's (or Session's) live state.
 *
 * Zero allocation per call: Rollbacks pre-build a `Uint8Array` view of each
 * field's live region at construction; this iterates those cached views.
 * Safe to call every frame as a desync canary.
 *
 * @param {object} rb - Rollback or Session instance.
 * @param {number} [seed=0]
 * @returns {number} Uint32 hash
 */
export function stateChecksum(rb, seed) {
  if (seed === undefined) seed = 0;
  let h = seed >>> 0;
  // Fast path: Rollback / Session expose pre-cached byte views via a Symbol key.
  const lb = rb[LIVE_BYTES];
  if (lb) {
    for (const name in lb) {
      h = checksum(lb[name], h);
    }
    return h >>> 0;
  }
  // Fallback for anything else with a `fields` map. Allocates a view per
  // field; reserved for objects that don't come from createRollback.
  const f = rb.fields;
  for (const name in f) {
    h = checksum(f[name], h);
  }
  return h >>> 0;
}

// ---------------------------------------------------------------------------
//  Wire codec -- zero-alloc input packing (v1.2.0)
// ---------------------------------------------------------------------------
//
// GGPO-shaped "last-N-inputs" redundancy: every packet carries the most recent
// `redundancy` frames of inputs, so a single dropped packet is recovered by the
// next one without a retransmit. The transport (sister packages) owns framing;
// core owns only the byte layout. See decisions/0005-wire-codec.md.
//
// Layout, little-endian throughout:
//   [ baseFrame : u32 ][ playerMask : u32 ]        <- 8-byte header
//   then `redundancy` frames, OLDEST first (baseFrame - redundancy + 1 .. baseFrame):
//     each frame: numPlayers players in ascending index order,
//       each player: inputWords x u32
// The body always includes every player's slot for a fixed frame stride;
// `playerMask` marks which players are meaningful (unpack feeds only those).
// numPlayers / inputWords are session config, known to both peers, so they are
// not on the wire; `redundancy` is recovered from the buffer length.

const CODEC_HEADER_BYTES = 8;          // [baseFrame u32 LE][playerMask u32 LE]
const CODEC_REDUNDANCY_DEFAULT = 4;

function writeU32LE(buf, off, v) {
  buf[off] = v & 0xff;
  buf[off + 1] = (v >>> 8) & 0xff;
  buf[off + 2] = (v >>> 16) & 0xff;
  buf[off + 3] = (v >>> 24) & 0xff;
}

function readU32LE(buf, off) {
  return (buf[off] | (buf[off + 1] << 8) | (buf[off + 2] << 16) | (buf[off + 3] << 24)) >>> 0;
}

/**
 * Pack the last `redundancy` frames of `session`'s inputs (ending at, inclusive,
 * `baseFrame`) into the caller-owned Uint8Array `dest`. Zero allocation.
 *
 * @param {object} session   A Session created by createSession.
 * @param {Uint8Array} dest  Caller-owned output buffer. Must be large enough.
 * @param {number} baseFrame Newest frame to include (typically session.frame()-1
 *                           or confirmedFrame()). Integer, must be >= 0.
 * @param {number} playerMask Bitmask of players whose inputs are meaningful.
 * @param {number} [redundancy=4] Frames to include; clamped to capacity and to
 *                           what exists at/below baseFrame.
 * @returns {number} Bytes written into `dest`.
 * @throws {TypeError|RangeError} On a bad argument, a negative baseFrame (nothing
 *   confirmed yet -- guard with `if (session.confirmedFrame() >= 0)`), or a dest
 *   that is too small (fail closed -- a short buffer is never silently truncated).
 */
export function packInputs(session, dest, baseFrame, playerMask, redundancy) {
  const h = session && session[CODEC];
  if (!h) throw new TypeError('packInputs: a Session is required');
  if (!(dest instanceof Uint8Array)) {
    throw new TypeError('packInputs: dest must be a Uint8Array');
  }
  if (!Number.isInteger(baseFrame)) {
    throw new TypeError(`packInputs: baseFrame must be integer, got ${baseFrame}`);
  }
  // Fail closed on a negative baseFrame. The advertised checksum-exchange usage is
  // `packInputs(s, dest, s.confirmedFrame(), mask)`, and confirmedFrame() is -1
  // until every player has confirmed a frame. Packing that would encode
  // -1 >>> 0 = 0xFFFFFFFF and the peer's unpackInputs would call feedRemoteInput
  // with a garbage 4-billion frame and throw. Reject at the door; the caller
  // guards with `if (s.confirmedFrame() >= 0) packInputs(...)`.
  if (baseFrame < 0) {
    throw new RangeError(`packInputs: baseFrame must be >= 0; nothing is confirmed yet (got ${baseFrame})`);
  }
  if (!Number.isInteger(playerMask) || playerMask < 0) {
    throw new RangeError(`packInputs: playerMask must be a non-negative integer bitmask, got ${playerMask}`);
  }
  if (redundancy === undefined) redundancy = CODEC_REDUNDANCY_DEFAULT;
  if (!isPosInt(redundancy)) {
    throw new RangeError(`packInputs: redundancy must be a positive integer, got ${redundancy}`);
  }
  const numPlayers = h.numPlayers;
  const inputWords = h.inputWords;
  const mask = h.mask;
  // Clamp: never read past one ring revolution, and never below frame 0 (baseFrame
  // is guaranteed >= 0 by the guard above).
  let R = redundancy;
  if (R > h.capacity) R = h.capacity;
  if (R > baseFrame + 1) R = baseFrame + 1;
  const need = CODEC_HEADER_BYTES + R * numPlayers * inputWords * 4;
  if (dest.length < need) {
    throw new RangeError(`packInputs: dest too small (need ${need} bytes, have ${dest.length})`);
  }
  writeU32LE(dest, 0, baseFrame >>> 0);
  writeU32LE(dest, 4, playerMask >>> 0);
  const inputRing = h.inputRing;
  const first = baseFrame - R + 1;
  let o = CODEC_HEADER_BYTES;
  for (let k = 0; k < R; k++) {
    const slot = (first + k) & mask;
    for (let p = 0; p < numPlayers; p++) {
      let src = (slot * numPlayers + p) * inputWords;
      for (let w = 0; w < inputWords; w++, o += 4) {
        writeU32LE(dest, o, inputRing[src + w]);
      }
    }
  }
  return need;
}

/**
 * Decode a buffer produced by packInputs and apply each masked input via `feed`.
 * Zero allocation (a per-player multi-word input is copied into a pre-allocated
 * session scratch before the callback; the single-word path passes a number).
 *
 * @param {object} session   The receiving Session (supplies numPlayers/inputWords
 *                           shape and the default feed).
 * @param {Uint8Array} src   Buffer produced by packInputs (exactly bytesWritten).
 * @param {(player:number, frame:number, input:number|Uint32Array)=>void} [feed]
 *   Applied per masked (player, frame), oldest frame first. Defaults to
 *   session.feedRemoteInput. The Uint32Array handed for inputWords>1 is a reused
 *   scratch -- read it synchronously, do not retain it.
 * @returns {number} The baseFrame decoded from the header.
 * @throws {TypeError|RangeError} On a bad argument or a malformed buffer length.
 */
export function unpackInputs(session, src, feed) {
  const h = session && session[CODEC];
  if (!h) throw new TypeError('unpackInputs: a Session is required');
  if (!(src instanceof Uint8Array)) {
    throw new TypeError('unpackInputs: src must be a Uint8Array');
  }
  const numPlayers = h.numPlayers;
  const inputWords = h.inputWords;
  if (src.length < CODEC_HEADER_BYTES) {
    throw new RangeError(`unpackInputs: src too small (need >= ${CODEC_HEADER_BYTES} bytes, have ${src.length})`);
  }
  const frameBytes = numPlayers * inputWords * 4;
  const bodyBytes = src.length - CODEC_HEADER_BYTES;
  if (bodyBytes % frameBytes !== 0) {
    throw new RangeError(`unpackInputs: src body ${bodyBytes} is not a whole number of frames (${frameBytes} bytes each)`);
  }
  const R = bodyBytes / frameBytes;
  const baseFrame = readU32LE(src, 0);
  const playerMask = readU32LE(src, 4);
  const applyFn = feed === undefined ? session.feedRemoteInput : feed;
  if (typeof applyFn !== 'function') {
    throw new TypeError('unpackInputs: feed must be a function');
  }
  const scratch = h.scratch;
  const first = baseFrame - R + 1;
  let o = CODEC_HEADER_BYTES;
  for (let k = 0; k < R; k++) {
    const f = first + k;
    for (let p = 0; p < numPlayers; p++) {
      if ((playerMask & (1 << p)) === 0) { o += inputWords * 4; continue; }
      if (inputWords === 1) {
        applyFn(p, f, readU32LE(src, o));
        o += 4;
      } else {
        for (let w = 0; w < inputWords; w++, o += 4) scratch[w] = readU32LE(src, o);
        applyFn(p, f, scratch);
      }
    }
  }
  return baseFrame;
}

// ---------------------------------------------------------------------------
//  Deterministic primitives
// ---------------------------------------------------------------------------

/**
 * Create a deterministic xorshift32 PRNG whose entire state is a single Uint32.
 *
 * If you snapshot the state via a rollback field (declare a `Uint32Array` of
 * length 1 in your `fields` spec), it participates in rewind/restore for free.
 *
 *   const rng = createPRNG();
 *   rng.seed(0xCAFE);
 *   const r01 = rng.float();            // [0, 1)
 *   const rInt = rng.int32();           // full 32-bit
 *   const inRange = rng.range(0, 100);  // integer [0, 100)
 *
 *   // To make it snapshot-safe in a rollback:
 *   //   fields: { rng: { type: Uint32Array, length: 1 } }
 *   //   rb.fields.rng[0] = rng.state();    // before each commit (or just keep
 *   //   rng.setState(rb.fields.rng[0]);    // live state aliased to rb.fields.rng)
 *
 * Output quality: good enough for game simulation, not cryptographic.
 *
 * @param {number} [seed]
 */
export function createPRNG(seed) {
  let s = (seed >>> 0) || 0x12345678;
  function next() {
    // xorshift32 -- Marsaglia 2003.
    s ^= s << 13; s >>>= 0;
    s ^= s >>> 17;
    s ^= s << 5;  s >>>= 0;
    return s;
  }
  return Object.freeze({
    seed(x) { s = (x >>> 0) || 0x12345678; },
    state() { return s >>> 0; },
    setState(x) { s = x >>> 0; if (s === 0) s = 0x12345678; },
    int32() { return next(); },
    float() { return next() / 0x100000000; },
    range(lo, hi) { return lo + (next() % (hi - lo)); },
  });
}

/**
 * Pure-function xorshift32 for tight inner loops.
 *
 * The closure-based `createPRNG` is ergonomic for outer logic but each
 * `rng.int32()` call resolves an object property and invokes a closure --
 * overhead that adds up when you're sampling thousands of times per frame
 * during a rollback resimulation.
 *
 * `nextPRNG` takes the state buffer + index directly. Inlinable, monomorphic,
 * zero overhead per call. Pair it with a `Uint32Array(1)` field in your
 * rollback so the state participates in commit/rollback for free:
 *
 *   const FIELDS = { rng: { type: Uint32Array, length: 1 }, ... };
 *   // inside simulate(fields, inputs):
 *   const r = nextPRNG(fields.rng, 0);
 *   if (r < threshold) ...
 *
 * Returns the new Uint32 value AND writes it back into `state[index]`.
 *
 * @param {Uint32Array} state
 * @param {number} index
 * @returns {number} the new state value (also stored at state[index])
 */
export function nextPRNG(state, index) {
  let s = state[index];
  if (s === 0) s = 0x12345678;
  s ^= s << 13; s >>>= 0;
  s ^= s >>> 17;
  s ^= s << 5;  s >>>= 0;
  state[index] = s;
  return s;
}

// ---------------------------------------------------------------------------
//  Transport contract (interface only -- no implementation in core)
// ---------------------------------------------------------------------------

/**
 * The Transport interface. Sister packages -- @zakkster/lite-rollback-local,
 * @zakkster/lite-rollback-webrtc -- implement this. Core ships no transport.
 *
 * ```ts
 * interface Transport {
 *   send(payload: Uint8Array, peer?: string): void;
 *   onMessage(handler: (payload: Uint8Array, peer?: string) => void): void;
 *   close(): void;
 * }
 * ```
 *
 * This export is a runtime-checkable assertion. Use it to verify a transport
 * implementation in tests:
 *
 *   import { assertTransport } from '@zakkster/lite-rollback';
 *   assertTransport(myTransport);
 *
 * @param {any} t
 * @returns {true}
 * @throws {TypeError} if t is not a valid Transport.
 */
export function assertTransport(t) {
  if (!t || typeof t !== 'object') {
    throw new TypeError('Transport: object required');
  }
  for (const m of ['send', 'onMessage', 'close']) {
    if (typeof t[m] !== 'function') {
      throw new TypeError(`Transport: missing method '${m}'`);
    }
  }
  return true;
}

// ---------------------------------------------------------------------------
//  Version & sentinels
// ---------------------------------------------------------------------------

export const VERSION = '1.2.1';

/** Useful constants for sister packages and userland. */
export const CONSTANTS = Object.freeze({
  CAPACITY_MIN,
  CAPACITY_MAX,
  MAX_PLAYERS,
  INPUT_WORDS_MAX,
});
