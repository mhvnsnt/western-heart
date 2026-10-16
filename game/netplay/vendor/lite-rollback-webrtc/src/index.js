// @zakkster/lite-rollback-webrtc
//
// RTCDataChannel-backed Transport for @zakkster/lite-rollback.
// Browser-to-browser, no server in the data path. Includes a minimal
// manual-signalling helper (copy/paste SDP) for LAN play and a clear hook
// for replacing it with a real WebSocket signaling server in production.
//
// (c) Zahary Shinikchiev. MIT licensed.

import { assertTransport, packInputs, unpackInputs } from '@zakkster/lite-rollback';

// Re-export the single-input wire-protocol helpers from local; the encoding of
// an individual INPUT message is identical. connectPeer is DELIBERATELY NOT
// re-exported here: local's connectPeer sends exactly ONE input per frame, and
// on an unreliable RTCDataChannel (maxRetransmits:0) a dropped packet then
// strands that frame as a permanent misprediction -> desync. This package
// ships its OWN connectPeer below that packs the last-N inputs per packet, so a
// single drop self-heals from the next packet. See decisions/0001-redundant-codec.md.
export {
  MSG,
  packInput,
  unpackMessage,
  unpackMessageInto,
} from '@zakkster/lite-rollback-local';

// ---------------------------------------------------------------------------
//  Transport -- wraps an open RTCDataChannel
// ---------------------------------------------------------------------------

/**
 * Wrap an OPEN RTCDataChannel as a lite-rollback Transport.
 *
 * The channel SHOULD be configured as unreliable + unordered
 * (`{ ordered: false, maxRetransmits: 0 }`) for lowest latency, and ordering is
 * reconstructed by the frame number inside the payload.
 *
 * CORRECTION (v1.1.0): an earlier revision claimed "packet loss is fine, the
 * next frame's message delivers the latest state anyway." That is FALSE for
 * input-transfer rollback. Each frame's input is a distinct fact that is sent
 * exactly once; under `maxRetransmits: 0` a dropped packet strands THAT frame
 * as a permanent prediction the receiver never corrects -- a silent desync,
 * not a transient hiccup. The remedy is redundancy, not reliability: this
 * package's `connectPeer` (below) packs the last-N inputs into every packet via
 * the core `packInputs` codec, so a single drop self-heals from the next
 * packet without a retransmit round-trip. See decisions/0001-redundant-codec.md.
 *
 *   const pc = new RTCPeerConnection({ iceServers: [...] });
 *   const dc = pc.createDataChannel('rollback', {
 *     ordered: false,
 *     maxRetransmits: 0,
 *   });
 *   await new Promise(r => dc.onopen = r);
 *   const transport = wrapDataChannel(dc);
 *
 * ## Allocation honesty
 *
 * Send path: zero allocation. `dc.send(payload)` accepts an ArrayBufferView
 * directly and synchronously copies into the SCTP stack at the C++ boundary.
 *
 * Receive path: ONE `Uint8Array` view allocation per incoming message. The
 * WebRTC API delivers each message as a fresh `ArrayBuffer` owned by the
 * browser; we cannot pre-allocate or pool the underlying buffer. We wrap it
 * in a `Uint8Array` view (~24 bytes of header) before handing it to the
 * Transport handler. The buffer itself is browser-allocated and out of our
 * control. This is a fixed per-message cost independent of payload size.
 *
 * The downstream `connectPeer` decodes these bytes directly through the core
 * `unpackInputs` codec into the Session's pre-allocated input ring, so no
 * further per-message garbage is produced. At 60 Hz x 2 players, that's ~120
 * Uint8Array views per second per peer -- well within any GC budget.
 *
 * @param {RTCDataChannel} dc
 * @returns {{ send(payload: Uint8Array, peer?: string): void,
 *            onMessage(h: (payload: Uint8Array, peer?: string) => void): void,
 *            close(): void }}
 */
export function wrapDataChannel(dc) {
  if (!dc || typeof dc !== 'object') {
    throw new TypeError('wrapDataChannel: RTCDataChannel required');
  }
  if (dc.readyState !== 'open') {
    throw new Error(`wrapDataChannel: channel must be open, is ${dc.readyState}`);
  }
  // Receive raw ArrayBuffer messages (binaryType = 'arraybuffer' is the
  // default for newly-constructed channels, but be explicit).
  dc.binaryType = 'arraybuffer';

  let handler = null;
  dc.onmessage = (ev) => {
    if (!handler) return;
    const data = ev.data;
    if (data instanceof ArrayBuffer) {
      // The browser owns `data`; we own the view. See "Allocation honesty"
      // in the wrapDataChannel JSDoc above.
      handler(new Uint8Array(data));
    } else if (data instanceof Uint8Array) {
      // Some runtimes deliver Uint8Array directly when binaryType is
      // overridden upstream. Forward as-is, no view allocation.
      handler(data);
    }
    // Strings ignored -- we only speak binary.
  };

  const transport = {
    send(payload, _peer) {
      if (!(payload instanceof Uint8Array)) {
        throw new TypeError('send: payload must be Uint8Array');
      }
      if (dc.readyState !== 'open') return;       // graceful drop on close mid-tick
      // Modern RTCDataChannel.send accepts ArrayBufferView and synchronously
      // copies the bytes across the C++/JS boundary into the SCTP stack. No
      // JS-side .slice() is required -- the older Safari race where the
      // buffer had to be detached has been fixed for years. Pass the view
      // directly, zero JS-side allocation per send.
      dc.send(payload);
    },
    onMessage(h) {
      if (typeof h !== 'function') throw new TypeError('onMessage: function required');
      handler = h;
    },
    close() {
      handler = null;
      try { dc.close(); } catch (_) { /* already closing */ }
    },
  };
  assertTransport(transport);
  return transport;
}

// ---------------------------------------------------------------------------
//  Minimal signalling helper -- manual copy/paste, no server
// ---------------------------------------------------------------------------

/**
 * Helpers for the LAN / one-laptop scenario where the two peers can exchange
 * SDP offers by hand (paste into a textarea, hit send). For production, use
 * a real signalling channel -- WebSocket, Firebase, etc. -- and call
 * createOffer / createAnswer / setRemote yourself.
 *
 * The flow:
 *   Peer A (host)                 Peer B (joiner)
 *   -------------                 ---------------
 *   create(host)                  (waiting)
 *   send offer ---------------->  accept(offer)
 *   (waiting)                     send answer back
 *   <---------------- accept(answer)
 *   <both connected, dc open>
 *
 * @param {object} [opts]
 * @param {RTCIceServer[]} [opts.iceServers]
 * @param {string} [opts.channelName='rollback']
 * @param {boolean} [opts.ordered=false]
 * @param {number} [opts.maxRetransmits=0]
 * @returns {{
 *   createOffer(): Promise<RTCSessionDescription>,
 *   acceptAnswer(answer: RTCSessionDescriptionInit): Promise<void>,
 *   onOpen: Promise<object>,
 *   pc: RTCPeerConnection,
 *   close(): void,
 * }}
 */
export function createHost(opts) {
  return _create({ ...opts, isHost: true });
}

/**
 * Joiner-side mirror of `createHost`. The flow is symmetric -- joiner
 * receives the host's offer, calls `acceptOffer`, hands back the answer.
 *
 * @param {object} [opts] -- same shape as createHost
 * @returns {{
 *   acceptOffer(offer: RTCSessionDescriptionInit): Promise<RTCSessionDescription>,
 *   onOpen: Promise<object>,
 *   pc: RTCPeerConnection,
 *   close(): void,
 * }}
 */
export function createJoiner(opts) {
  return _create({ ...opts, isHost: false });
}

function _create(opts) {
  if (typeof RTCPeerConnection === 'undefined') {
    throw new Error('RTCPeerConnection is not available. This package is browser-only.');
  }
  const {
    iceServers = [{ urls: 'stun:stun.l.google.com:19302' }],
    channelName = 'rollback',
    ordered = false,
    maxRetransmits = 0,
    isHost,
  } = opts || {};

  const pc = new RTCPeerConnection({ iceServers });

  let dc = null;
  let onOpenResolve, onOpenReject;
  const onOpen = new Promise((res, rej) => {
    onOpenResolve = res;
    onOpenReject = rej;
  });

  if (isHost) {
    dc = pc.createDataChannel(channelName, { ordered, maxRetransmits });
    // A freshly-created channel is always 'connecting'; onopen will fire.
    dc.onopen = () => onOpenResolve(wrapDataChannel(dc));
    dc.onerror = (e) => onOpenReject(e);
  } else {
    pc.ondatachannel = (ev) => {
      dc = ev.channel;
      // RACE: by the time ondatachannel fires, the underlying SCTP stream
      // may already be open. In that case `onopen` will never fire and the
      // Promise hangs forever. Check synchronously and short-circuit.
      if (dc.readyState === 'open') {
        onOpenResolve(wrapDataChannel(dc));
      } else {
        dc.onopen = () => onOpenResolve(wrapDataChannel(dc));
      }
      dc.onerror = (e) => onOpenReject(e);
    };
  }

  // ICE gathering: bundle everything into the SDP so the user only needs to
  // paste one blob. (No trickle-ICE here -- that needs a signalling server.)
  async function gatheredSdp(setLocalFn) {
    await setLocalFn();
    // Wait for ICE gathering to complete or 3 s timeout. The timeout matters
    // because some networks never reach 'complete' (TURN unreachable, etc.);
    // we want a usable SDP either way.
    await new Promise((res) => {
      if (pc.iceGatheringState === 'complete') return res();
      const t = setTimeout(res, 3000);
      pc.onicegatheringstatechange = () => {
        if (pc.iceGatheringState === 'complete') {
          clearTimeout(t);
          res();
        }
      };
    });
    return pc.localDescription;
  }

  return {
    /** Host: create an SDP offer to paste to the joiner. */
    async createOffer() {
      if (!isHost) throw new Error('createOffer: host-only');
      return gatheredSdp(async () => {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
      });
    },
    /** Joiner: paste in the offer; returns the answer to paste back. */
    async acceptOffer(offer) {
      if (isHost) throw new Error('acceptOffer: joiner-only');
      await pc.setRemoteDescription(offer);
      return gatheredSdp(async () => {
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
      });
    },
    /** Host: paste in the answer from the joiner. */
    async acceptAnswer(answer) {
      if (!isHost) throw new Error('acceptAnswer: host-only');
      await pc.setRemoteDescription(answer);
    },
    /** Resolves with a Transport once the data channel is open. */
    onOpen,
    /** Underlying RTCPeerConnection -- for advanced wiring. */
    pc,
    /** Close everything. */
    close() {
      try { if (dc) dc.close(); } catch (_) {}
      try { pc.close(); } catch (_) {}
    },
  };
}

// ---------------------------------------------------------------------------
//  Peer -- redundant turnkey glue: Session + Transport <-> unreliable network
// ---------------------------------------------------------------------------

/**
 * Wire a Session and a Transport together for an UNRELIABLE channel. Unlike
 * lite-rollback-local's connectPeer (one input per packet, correct only on a
 * lossless transport such as BroadcastChannel), this variant packs the last
 * `redundancy` frames of the LOCAL player's inputs into EVERY packet via the
 * core `packInputs` codec. A single dropped packet is then self-healing: the
 * next packet re-delivers the same frames, so the receiver corrects the missed
 * frame within `redundancy` ticks instead of being stranded on a permanent
 * prediction. This is the whole reason the webrtc package exists as more than a
 * transport wrapper -- see decisions/0001-redundant-codec.md.
 *
 * Call every render tick:
 *
 *   const peer = connectPeer({ session, transport, localPlayer: 0, redundancy: 4 });
 *   function frame() {
 *     peer.tickLocal(myButtons);   // sends the last-N local inputs, records this one
 *     peer.drain();                // applies any inputs received this frame
 *     session.step();
 *     render(session.fields);
 *     requestAnimationFrame(frame);
 *   }
 *
 * `tickLocal` and `drain` are zero-allocation in steady state: the send buffer
 * is sized once for the maximum packet and reused, and decode writes straight
 * into the Session's input ring. The receive queue holds references to the
 * transport-owned Uint8Array views (the one unavoidable per-message view is
 * allocated by `wrapDataChannel`, documented there), never a copy.
 *
 * Startup: the first `redundancy - 1` packets are naturally short (the codec
 * clamps `redundancy` to `baseFrame + 1`), so those cold-path packets send a
 * `subarray` view; steady-state packets are full-size and allocate nothing.
 * `packInputs` throws on a negative baseFrame, which cannot occur here because
 * the base is `session.frame() + session.inputDelay >= 0` from frame 0 -- the
 * very first tick already carries its own current-frame input. Fail closed:
 * a future frame decoded from a peer that is running ahead is skipped, never
 * fed (which would throw), and the redundancy re-delivers it once we catch up.
 *
 * inputDelay interaction (verified in test/webrtc.test.js and the torture
 * suite): the base frame is `frame() + inputDelay`, so a delayed local input is
 * transmitted `inputDelay` ticks BEFORE it is consumed -- redundancy and input
 * delay compound the delivery lead rather than fight. The hard constraint is
 * that `redundancy` must EXCEED `inputDelay` for the newest (furthest-ahead)
 * frames to reach the peer at all: an explicit `redundancy <= inputDelay` throws
 * at construction, and the default is `inputDelay + 4` so it is safe at any
 * inputDelay without the caller having to reason about it.
 *
 * Backpressure: the incoming queue holds up to 1024 packets; if it fills, the
 * OLDEST packet is dropped (LRU). At 60 Hz that is ~17 s of unread packets.
 *
 * @param {object} opts
 * @param {object} opts.session       -- a lite-rollback Session
 * @param {object} opts.transport     -- anything satisfying assertTransport
 * @param {number} [opts.localPlayer=0]
 * @param {number} [opts.redundancy] -- frames of local input per packet; clamped
 *   to the ring capacity. MUST exceed the Session's inputDelay (else the newest
 *   delayed frames can never be delivered -- a silent desync); an explicit value
 *   `<= inputDelay` throws RangeError. Defaults to `inputDelay + 4` (always clears
 *   the delay, plus 4 frames of loss tolerance), so the default is safe at any
 *   inputDelay -- 4 when inputDelay is 0, unchanged from 1.0.x behaviour there.
 * @returns {{
 *   tickLocal(input: number | Uint32Array): void,
 *   drain(): number,
 *   close(): void,
 *   readonly peerId: string | undefined,
 * }}
 */
export function connectPeer(opts) {
  if (!opts || typeof opts !== 'object') {
    throw new TypeError('connectPeer(opts): options object required');
  }
  const { session, transport, localPlayer = 0, redundancy } = opts;
  if (!session || typeof session.setLocalInput !== 'function') {
    throw new TypeError('session: must be a lite-rollback Session');
  }
  assertTransport(transport);
  if (!Number.isInteger(localPlayer) || localPlayer < 0 || localPlayer >= session.numPlayers) {
    throw new RangeError(`localPlayer: out of [0, ${session.numPlayers})`);
  }

  const numPlayers = session.numPlayers;
  const inputWords = session.inputWords;
  const capacity = session.capacity;
  const inputDelay = session.inputDelay;
  session.setLocalPlayer(localPlayer);

  // Redundancy MUST exceed inputDelay, or the newest delayed frames can never be
  // delivered: tickLocal packs frames up to `frame() + inputDelay`, which are all
  // in the peer's future in lockstep, so the peer's future-guard skips them until
  // it catches up. Frame `N + inputDelay` is only carried while the sender is at
  // frames [N, N+redundancy-1]; if `redundancy <= inputDelay` the peer does not
  // reach it until AFTER those packets stopped, so it commits its prediction and
  // -- once the frame leaves the redo window -- can never correct it (a silent,
  // permanent desync). Fail closed on explicit misuse; when the caller does not
  // pass `redundancy`, derive a default that always clears the delay AND keeps 4
  // frames of loss tolerance.
  let redundancyEff;
  if (redundancy === undefined) {
    redundancyEff = inputDelay + 4;
  } else {
    if (!Number.isInteger(redundancy) || redundancy < 1) {
      throw new RangeError(`redundancy: must be a positive integer, got ${redundancy}`);
    }
    if (redundancy <= inputDelay) {
      throw new RangeError(
        `connectPeer: redundancy (${redundancy}) must exceed session inputDelay (${inputDelay}); ` +
        `the newest delayed frames can never be delivered otherwise`);
    }
    redundancyEff = redundancy;
  }

  // Clamp redundancy to capacity so a full-length packet is achievable in
  // steady state (and the zero-alloc full-buffer send path is the norm). The
  // codec would clamp per-call anyway; pinning it here fixes the packet size.
  const R = redundancyEff > capacity ? capacity : redundancyEff;

  // Only the local player's inputs are meaningful to the peer -- pack just that
  // bit so the receiver decodes exactly our own frames and ignores the codec's
  // (predicted) slots for every other player.
  const sendMask = 1 << localPlayer;

  // Send buffer, sized ONCE for the maximum packet: header + R frames x all
  // players x inputWords x 4 bytes. Reused every tick.
  const sendCap = 8 + R * numPlayers * inputWords * 4;
  const sendBuf = new Uint8Array(sendCap);

  // Receive queue: a power-of-two ring of references to the transport-owned
  // Uint8Array payloads. Storing a reference allocates nothing here; the view
  // itself is created by wrapDataChannel (one unavoidable per-message view).
  const queueCap = 1024;                 // power of two
  const queueMask = queueCap - 1;
  const queue = new Array(queueCap).fill(null);
  let queueHead = 0, queueTail = 0;

  // A valid packInputs packet is the 8-byte header plus a whole number of frames.
  // Reject any other length at ingress (fail closed): unpackInputs would throw a
  // RangeError mid-drain and kill the loop, so a malformed datagram must be
  // dropped here like any other garbage rather than enqueued.
  const frameBytes = numPlayers * inputWords * 4;

  transport.onMessage((payload, _peer) => {
    if (!(payload instanceof Uint8Array)) return;
    if (payload.length < 8 || (payload.length - 8) % frameBytes !== 0) return;
    // Drop oldest if full (a loud throw would be worse in production).
    if (queueTail - queueHead >= queueCap) queueHead = queueTail - queueCap + 1;
    queue[queueTail & queueMask] = payload;
    queueTail++;
  });

  // Drain state, closed over by the feed callback (allocated ONCE). `curFrame`
  // is refreshed per drain; a decoded frame from a peer running AHEAD of us is
  // skipped rather than fed -- feedRemoteInput throws on a future frame, and
  // redundancy re-delivers it once we have stepped far enough to accept it.
  let curFrame = 0;
  let rollbacks = 0;
  function feed(player, f, input) {
    if (f > curFrame) return;            // future frame: fail closed, wait for resend
    if (session.feedRemoteInput(player, f, input)) rollbacks++;
  }

  /**
   * Record the local player's input for the current frame AND broadcast the
   * last `redundancy` frames of local inputs.
   * @param {number | Uint32Array} input
   */
  function tickLocal(input) {
    session.setLocalInput(input);
    // base is frame() + inputDelay -- the furthest-ahead frame we hold a real
    // local input for. Always >= 0, so packInputs never trips its negative
    // guard, even on the very first tick.
    const base = session.frame() + inputDelay;
    const n = packInputs(session, sendBuf, base, sendMask, R);
    if (n === sendCap) {
      transport.send(sendBuf);           // steady state: zero allocation
    } else {
      transport.send(sendBuf.subarray(0, n)); // startup only (R clamped short)
    }
  }

  /**
   * Apply any queued inputs from the peer.
   * @returns {number} count of rollbacks triggered this call.
   */
  function drain() {
    rollbacks = 0;
    curFrame = session.frame();
    while (queueHead < queueTail) {
      const idx = queueHead & queueMask;
      const payload = queue[idx];
      queue[idx] = null;
      queueHead++;
      if (payload) unpackInputs(session, payload, feed);
    }
    return rollbacks;
  }

  function close() {
    transport.close();
  }

  return Object.freeze({
    tickLocal,
    drain,
    close,
    get peerId() {
      return transport.peerId;
    },
  });
}

export { assertTransport } from '@zakkster/lite-rollback';
export const VERSION = '1.1.0';
