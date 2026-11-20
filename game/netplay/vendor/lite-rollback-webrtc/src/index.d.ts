// @zakkster/lite-rollback-webrtc v1.1.0 -- type definitions.
//
// (c) Zahary Shinikchiev. MIT licensed.

import type { Transport } from '@zakkster/lite-rollback';

// Re-exports of the single-input wire helpers from the local package.
// connectPeer is NOT re-exported -- this package defines its own redundant
// variant (see below).
export { assertTransport } from '@zakkster/lite-rollback';
export {
  MSG,
  packInput,
  unpackMessage,
  unpackMessageInto,
} from '@zakkster/lite-rollback-local';
export type {
  MsgType,
  UnpackedInputSingle,
  UnpackedInputMulti,
  UnpackedChecksum,
  UnpackedPing,
  UnpackedMessage,
} from '@zakkster/lite-rollback-local';

// ---------------------------------------------------------------------------
//  Redundant peer glue
// ---------------------------------------------------------------------------

/** A lite-rollback Session, structurally (the fields connectPeer touches). */
export interface Session {
  readonly numPlayers: number;
  readonly inputWords: number;
  readonly capacity: number;
  readonly inputDelay: number;
  frame(): number;
  setLocalPlayer(p: number): void;
  setLocalInput(input: number | Uint32Array): void;
  feedRemoteInput(player: number, frame: number, input: number | Uint32Array): boolean;
}

/** Options for the redundant `connectPeer`. */
export interface ConnectPeerOptions {
  session: Session;
  transport: Transport;
  /** Which player index this peer controls. Default 0. */
  localPlayer?: number;
  /** Frames of the local player's input packed into every packet, clamped to the
   *  Session's ring capacity. MUST exceed the Session's inputDelay (an explicit
   *  value <= inputDelay throws RangeError). Defaults to `inputDelay + 4`. */
  redundancy?: number;
}

/** The turnkey peer returned by `connectPeer`. */
export interface Peer {
  /** Record this frame's local input and broadcast the last-N local inputs. */
  tickLocal(input: number | Uint32Array): void;
  /** Apply any queued remote inputs. Returns the number of rollbacks. */
  drain(): number;
  /** Close the underlying transport. */
  close(): void;
  /** The transport's peer id, if any. */
  readonly peerId: string | undefined;
}

/**
 * Wire a Session and a Transport together for an UNRELIABLE channel, packing
 * the last `redundancy` frames of local input into every packet so a single
 * dropped packet self-heals. See decisions/0001-redundant-codec.md.
 */
export function connectPeer(opts: ConnectPeerOptions): Peer;

// ---------------------------------------------------------------------------
//  Transport
// ---------------------------------------------------------------------------

/**
 * Wrap an OPEN RTCDataChannel as a lite-rollback Transport.
 *
 * Throws if `dc` is not an object or if `dc.readyState !== 'open'`.
 *
 * Allocation profile:
 * - Send: zero allocation. dc.send() takes the Uint8Array directly.
 * - Receive: one Uint8Array view allocation per incoming message. The
 *   underlying ArrayBuffer is browser-owned and out of our control. This is
 *   a fixed per-message cost.
 */
export function wrapDataChannel(dc: RTCDataChannel): Transport;

// ---------------------------------------------------------------------------
//  Signalling helpers
// ---------------------------------------------------------------------------

/** Common options for host / joiner creation. */
export interface SignallingOptions {
  /** Defaults to `[{ urls: 'stun:stun.l.google.com:19302' }]`. */
  iceServers?: RTCIceServer[];
  /** Data channel name. Defaults to `'rollback'`. */
  channelName?: string;
  /** Defaults to `false` (recommended for rollback). */
  ordered?: boolean;
  /** Defaults to `0` (unreliable, recommended for rollback). */
  maxRetransmits?: number;
}

/** Host-side controller. Generates the offer, accepts the answer back. */
export interface HostController {
  createOffer(): Promise<RTCSessionDescription>;
  acceptAnswer(answer: RTCSessionDescriptionInit): Promise<void>;
  /** Resolves with the wrapped Transport once the data channel is open. */
  readonly onOpen: Promise<Transport>;
  /** Underlying RTCPeerConnection -- for advanced wiring. */
  readonly pc: RTCPeerConnection;
  /** Close the data channel and the peer connection. */
  close(): void;
}

/** Joiner-side controller. Receives the offer, hands back the answer. */
export interface JoinerController {
  acceptOffer(offer: RTCSessionDescriptionInit): Promise<RTCSessionDescription>;
  /** Resolves with the wrapped Transport once the data channel is open. */
  readonly onOpen: Promise<Transport>;
  /** Underlying RTCPeerConnection -- for advanced wiring. */
  readonly pc: RTCPeerConnection;
  /** Close the data channel and the peer connection. */
  close(): void;
}

export function createHost(opts?: SignallingOptions): HostController;
export function createJoiner(opts?: SignallingOptions): JoinerController;

export const VERSION: '1.1.0';
