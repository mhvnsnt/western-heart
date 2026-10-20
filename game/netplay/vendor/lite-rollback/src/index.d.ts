// @zakkster/lite-rollback v1.2.1 -- type definitions.
//
// (c) Zahary Shinikchiev. MIT licensed.

/** Any typed-array constructor accepted as a field type. */
export type TypedArrayConstructor =
  | Float32ArrayConstructor
  | Float64ArrayConstructor
  | Int32ArrayConstructor
  | Uint32ArrayConstructor
  | Int16ArrayConstructor
  | Uint16ArrayConstructor
  | Int8ArrayConstructor
  | Uint8ArrayConstructor
  | Uint8ClampedArrayConstructor;

/** Any typed-array instance produced by the constructors above. */
export type TypedArray =
  | Float32Array
  | Float64Array
  | Int32Array
  | Uint32Array
  | Int16Array
  | Uint16Array
  | Int8Array
  | Uint8Array
  | Uint8ClampedArray;

/**
 * Spec for a single field of a Rollback / Session.
 *
 * The `type` parameter `T` carries the constructor through to `Fields<S>` so
 * `rb.fields.pos` types as `Float32Array` (the concrete view), not a union.
 */
export interface FieldSpec<T extends TypedArrayConstructor = TypedArrayConstructor> {
  /** Typed-array constructor (e.g. `Float32Array`, `Uint8Array`). */
  type: T;
  /** Element count. Positive integer. */
  length: number;
}

/** A map of named fields. Inferred from the literal passed to createRollback. */
export type FieldsSpec = Record<string, FieldSpec>;

/**
 * Resolve a `FieldsSpec` to the runtime live-view map.
 *
 * Each entry's type is the `InstanceType` of its constructor, so callers get
 * concrete `Float32Array` / `Uint8Array` / ... views, not a union over all.
 */
export type Fields<S extends FieldsSpec> = {
  [K in keyof S]: InstanceType<S[K]['type']>;
};

// ---------------------------------------------------------------------------
//  Rollback
// ---------------------------------------------------------------------------

export interface Rollback<F extends Record<string, TypedArray>> {
  /** Ring depth (power-of-two). */
  readonly capacity: number;
  /** The single backing allocation shared by all field views. */
  readonly arrayBuffer: ArrayBuffer;
  /** Total bytes (`Sum (capacity + 1) x length x bpe`). */
  readonly byteLength: number;
  /** Live views -- what your code mutates. */
  readonly fields: F;
  /** Commits available (0..capacity). */
  depth(): number;
  /** Slot index of the most recent commit, or -1 if depth() === 0. */
  head(): number;
  /** Snapshot live -> ring. Zero alloc. */
  commit(): void;
  /**
   * Discard the `n` most recent commits and restore live to the state from
   * BEFORE them -- symmetric with `peek(n)`. After the call, live === peek(0).
   *
   * Pre-v1.0.2 used an off-by-one that left live and head out of sync; a
   * commit after rollback() would overwrite the just-restored state, silently
   * dropping a frame from history. The fix changes user-visible behaviour for
   * direct rollback callers (see CHANGELOG).
   *
   * Throws RangeError if `n < 1` or `n > depth()`.
   */
  rollback(n?: number): void;
  /**
   * Stable, read-only view of the `n`-th most recent commit. Same field shape
   * as `fields`. Treat as read-only -- mutating it corrupts the ring history.
   */
  peek(n?: number): F;
  /**
   * Zero-alloc 32-bit checksum of the `n`-th most recent commit (same addressing
   * as `peek(n)`), hashed over pre-built per-field byte views in declaration
   * order -- the identical order and routine `stateChecksum` uses over the live
   * region, so `checksumSlot(0)` right after a `commit()` equals `stateChecksum`
   * of the live state that produced it. Throws RangeError if `n < 0` or
   * `n >= depth()`. v1.2.0.
   */
  checksumSlot(n?: number, seed?: number): number;
  /** Clear head and depth. Does NOT zero the backing buffer. */
  reset(): void;
}

export interface CreateRollbackOptions<S extends FieldsSpec> {
  /** 1..2^20, must be a power of two. */
  capacity: number;
  /** At least one named field. */
  fields: S;
}

export function createRollback<S extends FieldsSpec>(
  opts: CreateRollbackOptions<S>,
): Rollback<Fields<S>>;

// ---------------------------------------------------------------------------
//  Session
// ---------------------------------------------------------------------------

/**
 * `simulate(fields, inputs, frame)` -- user-supplied tick function.
 * Must mutate `fields` in place. Must be deterministic given (fields, inputs, frame).
 */
export type SimulateFn<F extends Record<string, TypedArray>> = (
  fields: F,
  inputs: Uint32Array,
  frame: number,
) => void;

/**
 * `predict(player, frame, scratch, outOff)` -- user-supplied predictor.
 * Writes `inputWords` Uint32 words into `scratch` starting at `outOff`.
 * Default behaviour: repeat the last confirmed input for the player.
 */
export type PredictFn = (
  player: number,
  frame: number,
  scratch: Uint32Array,
  outOff: number,
) => void;

/**
 * `onDesync(frame, player)` -- fired when a remote input contradicts an input
 * the session had already marked confirmed for `frame` (a genuine two-client
 * divergence, not a misprediction). v1.1.0.
 */
export type OnDesyncFn = (frame: number, player: number) => void;

/**
 * Read-only observability counters (v1.1.0). Cumulative until `reset()`; every
 * value reflects the live internal state at read time. Backed by a pre-allocated
 * typed array -- reading allocates nothing.
 */
export interface SessionStats {
  /** feedRemoteInput calls that triggered a rollback + fast-forward. */
  readonly rollbacks: number;
  /** Deepest single rollback so far, in frames re-simulated. */
  readonly maxRollbackDepth: number;
  /** Predicted inputs later corrected by a real remote value. */
  readonly mispredictions: number;
  /** Confirmed-input mismatches: two clients disagreed on a frame both confirmed. */
  readonly desyncs: number;
  /** Total frames re-simulated across all rollbacks. */
  readonly fastForwardFrames: number;
}

export interface Session<F extends Record<string, TypedArray>> {
  readonly capacity: number;
  readonly numPlayers: number;
  readonly inputWords: number;
  /** Local input delay in frames (`setLocalInput` targets `frame() + inputDelay`). v1.2.0. */
  readonly inputDelay: number;
  /** Live state -- same surface as Rollback. */
  readonly fields: F;
  /** Backing buffer for the state ring (not the input ring). */
  readonly arrayBuffer: ArrayBuffer;
  /** Frames simulated so far. Next step() will simulate frame `frame()`. */
  frame(): number;
  /**
   * Commits available (same as the underlying Rollback). Since v1.1.0 this counts
   * the genesis snapshot (state(-1)), which is committed at the first step(): 0 on
   * a fresh or just-reset session, 2 after the first step (genesis + state(0)),
   * and (frames + 1) until the genesis baseline rolls off after `capacity`
   * further commits.
   */
  depth(): number;
  /**
   * The highest frame at which EVERY player's input is real (confirmed), not
   * predicted -- the GGPO confirmed-frame watermark. Monotone non-decreasing;
   * -1 until every player has at least one confirmation. v1.1.0.
   */
  confirmedFrame(): number;
  /**
   * Local-vs-remote frame lead (v1.2.0): the raw delta
   * `latest-confirmed-frame(localPlayer) - confirmedFrame()`. Positive means the
   * local client is running ahead of the slowest remote's confirmed inputs -- the
   * caller's loop can stall to let them catch up (GGPO time-sync). Pure read;
   * zero allocation.
   */
  frameAdvantage(): number;
  /**
   * 32-bit checksum of the COMMITTED state at frame `f` -- pin it to
   * `confirmedFrame()` so two clients compare the same committed frame rather than
   * whatever live frame each is on. Reaches the committed slot through the ring's
   * zero-alloc path (never `stateChecksum(peek(...))`, which would allocate a view
   * per field). Fail closed: a frame outside the committed window
   * `[frame() - depth(), frame() - 1]` throws RangeError. v1.2.0.
   */
  checksumAt(f: number, seed?: number): number;
  /** Read-only observability counters. v1.1.0. */
  readonly stats: SessionStats;

  /** Which player setLocalInput targets. Read directly; write via setLocalPlayer. */
  readonly localPlayer: number;
  setLocalPlayer(p: number): void;

  /** Confirm local player's input for the current frame. */
  setLocalInput(input: number | Uint32Array): void;
  /**
   * Confirm a specific player/frame.
   * Frame must be in `[frame() - capacity + 1, frame()]`.
   */
  setInput(player: number, frame: number, input: number | Uint32Array): void;
  /**
   * Fill inputs -> simulate -> commit -> frame++. Zero alloc.
   *
   * Since v1.0.3, step() also clears the confirmed-input mask of a slot last used
   * a full revolution ago (since v1.2.0 the just-opened `frame + inputDelay` slot,
   * which reduces to the entering slot when inputDelay is 0). This closes the
   * stale-confirmedMask desync that struck any session running past `capacity`
   * frames. Consequence: the effective late-input redo window is
   * `capacity - 1 - inputDelay` frames -- a remote input older than that lands in
   * the documented out-of-window branch of feedRemoteInput (updates the slot, no
   * rollback). See CHANGELOG 1.0.3 / 1.2.0.
   */
  step(): void;
  /**
   * Accept a remote input for some past frame.
   * Returns true iff a rollback + fast-forward happened.
   *
   * A mismatch against an input already CONFIRMED for that frame is a genuine
   * desync (not a misprediction): it does NOT roll back, returns false, bumps
   * `stats.desyncs`, and fires the `onDesync` callback if one was supplied.
   *
   * The oldest safely-redoable frame is `frame() - capacity + 1 + inputDelay`; a
   * PAST remote input older than that is inert -- it stores nothing (no slot
   * write, no confirm) and returns false, because its ring slot may alias a
   * still-pending frame and a stale confirmed bit there would poison that frame
   * (fixes a pre-existing v1.1.0 out-of-window R-01). The current frame
   * (`frame === frame()`) is still confirmed via the normal path. v1.2.0.
   */
  feedRemoteInput(player: number, frame: number, input: number | Uint32Array): boolean;

  /** Pass-through to underlying rollback (advanced users; does NOT touch frame counter). */
  commit(): void;
  rollback(n?: number): void;
  peek(n?: number): F;
  /**
   * Reset rollback, zero live state, clear input ring, stats, and watermark,
   * frame = 0. Re-arms the genesis commit (re-committed at the next first step),
   * so depth() is 0 immediately after and 2 after the first post-reset step.
   */
  reset(): void;
}

export interface CreateSessionOptions<S extends FieldsSpec> extends CreateRollbackOptions<S> {
  /** 1..32. */
  numPlayers: number;
  /** 1..16. Default 1. */
  inputWords?: number;
  /**
   * Local input delay in frames (v1.2.0). `setLocalInput` targets frame
   * `frame() + inputDelay`, buffering the local player's input this many frames
   * before it takes effect and giving the network that lead time to deliver it --
   * the single biggest rollback-frequency reducer. Integer in `[0, capacity - 1]`;
   * out of range throws RangeError. Default 0 (no delay, historical behaviour).
   * The first `inputDelay` frames use the neutral predicted input on every client.
   */
  inputDelay?: number;
  simulate: SimulateFn<Fields<S>>;
  /** Optional custom predictor. Defaults to "repeat last confirmed input". */
  predict?: PredictFn;
  /** Optional callback fired on a confirmed-input mismatch (a true desync). v1.1.0. */
  onDesync?: OnDesyncFn;
}

export function createSession<S extends FieldsSpec>(
  opts: CreateSessionOptions<S>,
): Session<Fields<S>>;

// ---------------------------------------------------------------------------
//  Checksum
// ---------------------------------------------------------------------------

/**
 * Fast non-cryptographic 32-bit hash. Zero alloc for typed-array views;
 * allocates one Uint8Array view per call for raw ArrayBuffer input.
 */
export function checksum(buf: ArrayBuffer | ArrayBufferView, seed?: number): number;

/** Hash across all fields of a Rollback / Session's live state. Zero alloc. */
export function stateChecksum(
  rb: { fields: Record<string, TypedArray> },
  seed?: number,
): number;

// ---------------------------------------------------------------------------
//  Wire codec (v1.2.0)
// ---------------------------------------------------------------------------

/**
 * `feed(player, frame, input)` -- applied by `unpackInputs` per masked player,
 * oldest frame first. For `inputWords === 1`, `input` is a number; for
 * `inputWords > 1` it is a REUSED per-session `Uint32Array` scratch -- read it
 * synchronously, do not retain it.
 */
export type CodecFeedFn = (
  player: number,
  frame: number,
  input: number | Uint32Array,
) => void;

/**
 * Pack the last `redundancy` frames of a Session's inputs (ending at, inclusive,
 * `baseFrame`) into the caller-owned `dest`. Zero allocation. Little-endian
 * layout: `[baseFrame u32][playerMask u32]` (8-byte header) then `redundancy`
 * frames oldest-first x numPlayers x inputWords LE u32.
 *
 * `redundancy` defaults to 4, clamped to `capacity` and to `baseFrame + 1`.
 * Returns bytes written. Fail closed: throws `RangeError` on a too-small `dest`
 * or a negative `baseFrame` (nothing confirmed yet -- guard with
 * `if (session.confirmedFrame() >= 0)`), `TypeError` on a bad argument.
 * v1.2.0.
 */
export function packInputs(
  session: { readonly numPlayers: number; readonly inputWords: number },
  dest: Uint8Array,
  baseFrame: number,
  playerMask: number,
  redundancy?: number,
): number;

/**
 * Decode a buffer produced by `packInputs` and apply each masked input via
 * `feed` (default `session.feedRemoteInput`, oldest frame first). Zero
 * allocation. Returns the decoded `baseFrame`. Fail closed: throws `RangeError`
 * on a below-header or misaligned buffer, `TypeError` on a bad argument. v1.2.0.
 */
export function unpackInputs(
  session: { readonly numPlayers: number; readonly inputWords: number },
  src: Uint8Array,
  feed?: CodecFeedFn,
): number;

// ---------------------------------------------------------------------------
//  PRNG
// ---------------------------------------------------------------------------

export interface PRNG {
  /** Re-seed. 0 is illegal for xorshift32; gets replaced with the default seed. */
  seed(x: number): void;
  /** Current state (Uint32). */
  state(): number;
  /** Restore state. 0 gets replaced with the default seed. */
  setState(x: number): void;
  /** Full 32-bit unsigned sample. */
  int32(): number;
  /** Uniform float in [0, 1). */
  float(): number;
  /** Integer in [lo, hi). */
  range(lo: number, hi: number): number;
}

export function createPRNG(seed?: number): PRNG;

/**
 * Pure-function xorshift32. Reads `state[index]`, writes the new state back,
 * returns the new value. Inlinable; no closure / no `this`.
 */
export function nextPRNG(state: Uint32Array, index: number): number;

// ---------------------------------------------------------------------------
//  Transport contract
// ---------------------------------------------------------------------------

export interface Transport {
  send(payload: Uint8Array, peer?: string): void;
  onMessage(handler: (payload: Uint8Array, peer?: string) => void): void;
  close(): void;
}

/**
 * Runtime contract check.
 * @returns true if t implements the Transport interface.
 * @throws TypeError otherwise.
 */
export function assertTransport(t: unknown): t is Transport;

// ---------------------------------------------------------------------------
//  Constants
// ---------------------------------------------------------------------------

export const VERSION: '1.2.1';

export const CONSTANTS: {
  readonly CAPACITY_MIN: number;
  readonly CAPACITY_MAX: number;
  readonly MAX_PLAYERS: number;
  readonly INPUT_WORDS_MAX: number;
};
